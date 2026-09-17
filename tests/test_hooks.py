"""Tests for the hook pair (HANDOFF-0028 acceptance): the guard's decisions and the recorded pair.

Purpose: the six synthetic payloads (exit codes 2, 2, 2, 2, 0, 2), fragment scanning of Bash
lines and scripts, the read-after-allow ordering, routing of the pair to trace or ledger, the
intent-plus-refusal pair, the payload file and its hash, error outcomes with a class, the
fail-closed wrappers, and the post-hook that never blocks.
Inputs: subprocess runs of the two entry points with `--test-streams`, against temp fixtures;
the wrappers with a fake `uv` on PATH; one in-process run with the script reader replaced.
Outputs: pytest assertions.
Side effects: files under `tmp_path` and the gitignored test streams and test scratch.
"""

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kgme import config, ledger, paths
from kgme.hooks import common, guard, pre_tool_guard

ROOT = paths.root()
SETTINGS = config.read_config()
BLOCKLIST = [paths.resolve(p) for p in SETTINGS["hooks"]["blocklist"] if not p.startswith("**/")]
PATTERNS = [p[3:] for p in SETTINGS["hooks"]["blocklist"] if p.startswith("**/")]
TEST_SCRATCH = paths.scratch_test_dir(SETTINGS)


def run_hook(module: str, payload: object) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", module, "--test-streams"],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )


def payload(tool: str, session: str, **tool_input: object) -> dict:
    digest = hashlib.sha256(json.dumps([tool, tool_input], sort_keys=True).encode()).hexdigest()
    return {
        "session_id": session,
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_{digest[:12]}",
        "cwd": str(ROOT),
        "hook_event_name": "PreToolUse",
    }


def decide(tool: str, tool_input: dict, **overrides: object) -> guard.Decision:
    kwargs: dict = dict(
        cwd=ROOT, repo_root=ROOT, blocklist=BLOCKLIST, name_patterns=PATTERNS, allow_outside=[]
    )
    kwargs.update(overrides)
    return guard.decide(tool, tool_input, **kwargs)


def probe_script(name: str, text: str) -> Path:
    target = TEST_SCRATCH / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    return target


@pytest.fixture
def planted(tmp_path: Path) -> dict[str, Path]:
    env_file = tmp_path / ".env"
    env_file.write_text("FAKE=1\n")
    tier1 = tmp_path / "tier1" / "positions.md"
    tier1.parent.mkdir()
    tier1.write_text("fake\n")
    return {"env": env_file, "tier1": tier1, "outside": tmp_path / "note.md"}


@pytest.mark.blocking
def test_six_synthetic_payloads_give_the_expected_exit_codes(planted: dict[str, Path]) -> None:
    session = "hooktest-six"
    assert not decide("Read", {"file_path": str(planted["env"])}).allowed
    assert not decide("Bash", {"command": "cat ~/.ssh/id_ed25519"}).allowed
    assert not decide(
        "Read",
        {"file_path": str(planted["tier1"])},
        blocklist=BLOCKLIST + [planted["tier1"].parent],
    ).allowed
    assert not decide("Read", {"file_path": str(planted["outside"])}).allowed
    assert decide("Read", {"file_path": "kgme/paths.py"}).allowed
    exits = [
        run_hook(
            "kgme.hooks.pre_tool_guard", payload("Read", session, file_path=str(planted["env"]))
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard", payload("Bash", session, command="cat ~/.ssh/id_ed25519")
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard",
            payload("Read", session, file_path=str(ROOT / "memory/private/x.md")),
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard", payload("Read", session, file_path=str(planted["outside"]))
        ),
        run_hook("kgme.hooks.pre_tool_guard", payload("Read", session, file_path="kgme/paths.py")),
        run_hook("kgme.hooks.pre_tool_guard", "{not json"),
    ]
    assert [r.returncode for r in exits] == [2, 2, 2, 2, 0, 2], [r.stderr for r in exits]


@pytest.mark.blocking
def test_dotenv_name_shapes_are_all_refused(tmp_path: Path) -> None:
    for name in (".env", ".env.local", "planted.env", "prod.env.bak"):
        (tmp_path / name).write_text("x")
        assert not decide(
            "Read", {"file_path": str(tmp_path / name)}, allow_outside=[tmp_path]
        ).allowed
    assert decide(
        "Read", {"file_path": str(tmp_path / "environment.md")}, allow_outside=[tmp_path]
    ).allowed


@pytest.mark.blocking
def test_symlink_to_a_secret_is_caught_by_resolution(tmp_path: Path) -> None:
    secret = tmp_path / ".env"
    secret.write_text("x")
    link = tmp_path / "harmless.txt"
    link.symlink_to(secret)
    decision = decide("Read", {"file_path": str(link)}, allow_outside=[tmp_path])
    assert not decision.allowed and ".env" in decision.reason


@pytest.mark.blocking
@pytest.mark.parametrize(
    "command",
    [
        "cat planted.env",
        "cat .env;",
        "cat --file=.env",
        "python -c \"print(open('.env').read())\"",
        "uv run python - <<'PY'\nprint(open('.env').read())\nPY",
        "cat $HOME/.ssh/id_ed25519",
        "cat ~/Library/Keychains/login.keychain-db",
        "cat 2>.env",
    ],
)
def test_bash_fragments_reach_forbidden_names_wherever_they_sit(command: str) -> None:
    decision = decide("Bash", {"command": command})
    assert not decision.allowed and "blocklisted" in decision.reason, command


@pytest.mark.blocking
def test_bash_is_fenced_by_the_blocklist_only_for_ordinary_lines() -> None:
    for command in ("ls /usr/bin", "git status", "uv run kgme --help", "echo hi 2>/dev/null"):
        assert decide("Bash", {"command": command}).allowed, command


@pytest.mark.blocking
def test_script_candidates_follow_runners_within_a_segment() -> None:
    cases = {
        "uv run python -X dev job.py": ["job.py"],
        "./deploy.sh && cp a.py b.py": ["deploy.sh"],
        "sh tools/x.sh; grep secret tests/test_y.py": ["x.sh"],
        "cp a.py b.py": [],
        "grep x tests/test_y.py": [],
        "git add kgme/events.py": [],
        "source env.sh | tee out.log": ["env.sh"],
        "true && ./job.sh": ["job.sh"],
        "make check || ./fallback.sh; ls": ["fallback.sh"],
        "echo start\n./nightly.sh\n": ["nightly.sh"],
    }
    for command, expected in cases.items():
        found = [p.name for p in guard.script_candidates("Bash", {"command": command}, ROOT)]
        assert found == expected, command


@pytest.mark.blocking
def test_direct_script_after_a_separator_is_inspected() -> None:
    session = f"hooktest-separator-{os.getpid()}"
    probe = probe_script("after_and.sh", "cat .env\n")
    result = run_hook(
        "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"true && {probe}")
    )
    assert result.returncode == 2 and "blocklisted" in result.stderr
    probe.write_text("echo fine\n")
    result = run_hook(
        "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"true && {probe}")
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.blocking
def test_scripts_a_bash_line_runs_are_inspected_or_refused(tmp_path: Path) -> None:
    session = f"hooktest-script-{os.getpid()}"
    probe = probe_script("probe_script.py", "print(open('.env').read())\n")
    for command in (f"uv run python {probe}", f"uv run python -X dev {probe}"):
        result = run_hook("kgme.hooks.pre_tool_guard", payload("Bash", session, command=command))
        assert result.returncode == 2 and "blocklisted" in result.stderr, command
    copied = probe_script("probe_copy.py", "")
    result = run_hook(
        "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"cp {probe} {copied}")
    )
    assert result.returncode == 0, result.stderr
    probe.write_text("print('harmless')\n")
    result = run_hook(
        "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"uv run python {probe}")
    )
    assert result.returncode == 0, result.stderr
    outside = tmp_path / "opaque.sh"
    outside.write_text("cat .env\n")
    result = run_hook(
        "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"sh {outside}")
    )
    assert result.returncode == 2 and "cannot inspect" in result.stderr
    unreadable = probe_script("unreadable.sh", "echo x\n")
    unreadable.chmod(0)
    try:
        result = run_hook(
            "kgme.hooks.pre_tool_guard", payload("Bash", session, command=f"sh {unreadable}")
        )
        assert result.returncode == 2 and "cannot inspect" in result.stderr
    finally:
        unreadable.chmod(0o644)


@pytest.mark.blocking
def test_a_forbidden_script_path_is_refused_before_it_is_ever_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[Path] = []

    def recording_reader(path: Path) -> str:
        opened.append(path)
        return ""

    monkeypatch.setattr(common, "read_script_text", recording_reader)
    forbidden = ROOT / "memory" / "private" / "job.py"
    real_is_file = Path.is_file

    def exists_for_the_probe(self: Path) -> bool:
        return True if self == forbidden else real_is_file(self)

    # The forbidden script must look present, or the existence check alone would skip the
    # reader and the test would pass even if the read moved ahead of the decision (review F11).
    monkeypatch.setattr(Path, "is_file", exists_for_the_probe)
    command = f"uv run python {forbidden}"
    # Precondition: the line itself is refused on its fragments, before any script is opened.
    assert not decide("Bash", {"command": command}).allowed
    call = payload("Bash", f"hooktest-order-{os.getpid()}", command=command)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(call)))
    assert pre_tool_guard.main(["--test-streams"]) == 2
    assert opened == []


@pytest.mark.blocking
def test_read_pair_lands_in_trace_and_edit_pair_in_ledger_with_matching_ref_and_hash() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    session = f"hooktest-pair-{os.getpid()}"
    read_call = payload("Read", session, file_path="kgme/paths.py")
    assert run_hook("kgme.hooks.pre_tool_guard", read_call).returncode == 0
    read_call["tool_response"] = {"content": "not stored in the ledger"}
    assert run_hook("kgme.hooks.post_tool_ledger", read_call).returncode == 0
    edit_call = payload("Edit", session, file_path="kgme/cli.py", old_string="a", new_string="b")
    assert run_hook("kgme.hooks.pre_tool_guard", edit_call).returncode == 0
    edit_call["tool_response"] = {"ok": True}
    assert run_hook("kgme.hooks.post_tool_ledger", edit_call).returncode == 0

    trace = ledger.read(dirs, run_id=session, stream="trace")
    in_ledger = ledger.read(dirs, run_id=session, stream="ledger")
    assert [e["kind"] for e in trace] == ["intent", "outcome"]
    assert trace[1]["ref"] == trace[0]["id"] and trace[0]["job"] == "tool:Read"
    assert [e["kind"] for e in in_ledger] == ["intent", "outcome"]
    assert in_ledger[1]["ref"] == in_ledger[0]["id"] and in_ledger[0]["job"] == "tool:Edit"
    assert in_ledger[1]["parent"] == trace[0]["id"]
    payload_path = ROOT / in_ledger[1]["payload_ref"]
    assert payload_path.exists() and "payloads/test/" in in_ledger[1]["payload_ref"]
    assert hashlib.sha256(payload_path.read_bytes()).hexdigest() == in_ledger[1]["payload_sha256"]
    assert "not stored" not in " ".join(e["summary"] for e in trace + in_ledger)


@pytest.mark.blocking
def test_bash_summary_carries_a_count_never_command_text() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    session = f"hooktest-bashsummary-{os.getpid()}"
    command = "uv run python -c 'print(\"customer/RAW_SENTINEL\")'"
    result = run_hook("kgme.hooks.pre_tool_guard", payload("Bash", session, command=command))
    assert result.returncode == 0
    found = ledger.read(dirs, run_id=session)
    assert len(found) == 1 and "RAW_SENTINEL" not in found[0]["summary"]
    assert found[0]["summary"].startswith("Bash ") and "fragments examined" in found[0]["summary"]
    assert common.summarize_call("Bash", {"command": command}, 5) == (
        "Bash 5 path-like fragments examined"
    )


@pytest.mark.blocking
def test_refused_call_is_an_intent_plus_a_refused_outcome_in_the_ledger() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    session = f"hooktest-refused-{os.getpid()}"
    result = run_hook(
        "kgme.hooks.pre_tool_guard",
        payload("Read", session, file_path=str(ROOT / "memory/private/x.md")),
    )
    assert result.returncode == 2 and "refused" in result.stderr
    found = ledger.read(dirs, run_id=session, stream="ledger")
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["status"] == "refused" and found[1]["class"] == "blocking"
    assert found[1]["ref"] == found[0]["id"]
    assert ledger.read(dirs, run_id=session, stream="trace") == []


@pytest.mark.blocking
def test_refusal_with_a_very_long_path_is_recorded_clipped_not_failed(tmp_path: Path) -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    session = f"hooktest-longrefusal-{os.getpid()}"
    deep = tmp_path.joinpath(*[f"segment{i:02d}" for i in range(30)]) / ".env"
    result = run_hook("kgme.hooks.pre_tool_guard", payload("Read", session, file_path=str(deep)))
    assert result.returncode == 2 and "blocklisted" in result.stderr
    found = ledger.read(dirs, run_id=session, stream="ledger")
    assert found[-1]["status"] == "refused"
    assert len(found[-1]["summary"]) <= 200 and found[-1]["summary"].endswith("…")


@pytest.mark.blocking
def test_error_response_closes_the_intent_with_a_classed_error_outcome() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    session = f"hooktest-error-{os.getpid()}"
    call = payload("Edit", session, file_path="kgme/cli.py", old_string="x", new_string="y")
    assert run_hook("kgme.hooks.pre_tool_guard", call).returncode == 0
    call["tool_response"] = {"is_error": True, "content": "rate limit exceeded"}
    assert run_hook("kgme.hooks.post_tool_ledger", call).returncode == 0
    found = ledger.read(dirs, run_id=session, stream="ledger")
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["status"] == "error" and found[1]["class"] == "transient"
    assert found[1]["ref"] == found[0]["id"]
    assert not [e for e in ledger.open_intents("tool:Edit", dirs) if e["run_id"] == session]


@pytest.mark.blocking
def test_long_bash_lines_are_not_blocked_and_many_secrets_still_are() -> None:
    session = f"hooktest-long-{os.getpid()}"
    command = " ".join(f"cat dir{i}/file{i}.py" for i in range(60))
    result = run_hook("kgme.hooks.pre_tool_guard", payload("Bash", session, command=command))
    assert result.returncode == 0
    secrets = " ".join(f"cat ~/.ssh/x{i}" for i in range(12))
    refused = run_hook("kgme.hooks.pre_tool_guard", payload("Bash", session, command=secrets))
    assert refused.returncode == 2 and "blocklisted" in refused.stderr


def _fake_uv(tmp_path: Path, exit_code: int) -> dict:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    fake = bin_dir / "uv"
    fake.write_text(f"#!/bin/sh\necho 'import failure simulated' >&2\nexit {exit_code}\n")
    fake.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    return env


@pytest.mark.blocking
@pytest.mark.parametrize("exit_code", [1, 3, 127])
def test_pre_wrapper_maps_every_startup_failure_to_a_block(tmp_path: Path, exit_code: int) -> None:
    result = subprocess.run(
        ["sh", str(ROOT / "tools/hooks/pre_tool_guard.sh")],
        input="{}",
        capture_output=True,
        text=True,
        env=_fake_uv(tmp_path, exit_code),
        timeout=60,
    )
    assert result.returncode == 2 and "failing closed" in result.stderr


@pytest.mark.blocking
@pytest.mark.parametrize("exit_code", [1, 3, 127])
def test_post_wrapper_never_blocks_and_records_a_startup_failure(
    tmp_path: Path, exit_code: int
) -> None:
    result = subprocess.run(
        ["sh", str(ROOT / "tools/hooks/post_tool_ledger.sh")],
        input="{}",
        capture_output=True,
        text=True,
        env=_fake_uv(tmp_path, exit_code),
        timeout=60,
    )
    assert result.returncode == 0
    errors = tmp_path / "logs" / "scratch" / "hook-errors.jsonl"
    assert errors.exists() and f"exited {exit_code}" in errors.read_text()


@pytest.mark.blocking
def test_post_hook_never_blocks_and_records_its_own_failure_in_test_scratch() -> None:
    errors = TEST_SCRATCH / "hook-errors.jsonl"
    before = errors.read_text() if errors.exists() else ""
    live = paths.scratch_dir(SETTINGS) / "hook-errors.jsonl"
    live_before = live.read_bytes() if live.exists() else None
    result = run_hook("kgme.hooks.post_tool_ledger", "{not json")
    assert result.returncode == 0
    after = errors.read_text()
    assert after.startswith(before) and after.count("\n") == before.count("\n") + 1
    assert "JSONDecodeError" in after.splitlines()[-1]
    live_after = live.read_bytes() if live.exists() else None
    assert live_after == live_before


@pytest.mark.blocking
def test_a_tilde_word_that_names_no_user_is_a_literal_not_a_crash() -> None:
    """`~330` in a table or `~nosuchuser/x` must not crash the guard: a crash fails closed and
    refuses the whole call (found 2026-09-17 when a report edit carried a `~330` cell)."""
    decision = decide("Bash", {"command": "echo '| ~330 |' and cat ~nosuchuser-kgme/notes.md"})
    assert decision.allowed, decision.reason
    assert any(p.name == "~330" for p in decision.paths)
    assert guard.expand_home("~330") == Path("~330")
    assert guard.expand_home("~") == Path.home()
    still_fenced = decide("Bash", {"command": "cat ~/.ssh/id_ed25519"})
    assert not still_fenced.allowed, "a real home expansion still reaches the blocklist"
