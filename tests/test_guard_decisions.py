"""The guard's decisions (HANDOFF-0028 acceptance, pure half): what is refused and why.

Purpose: the six synthetic payloads (exit codes 2, 2, 2, 2, 0, 2), every env-file name shape,
symlink resolution, fragment scanning of Bash lines and of the scripts they run, the
read-after-allow ordering, and the tilde word that must not crash the guard (AUDIT-0021).
Inputs: `guard.decide` with the real lists; subprocess runs of the guard for the payload test.
Outputs: pytest assertions.
Side effects: files under `tmp_path` and the gitignored test scratch and streams.
"""

import io
import json
import os
import sys
from pathlib import Path

import pytest
from hooktools import BLOCKLIST, ROOT, decide, payload, probe_script, run_hook

from kgme import config
from kgme.hooks import common, guard, pre_tool_guard


@pytest.fixture
def hook_probes(tmp_path: Path) -> dict[str, Path]:
    env_file = tmp_path / ".env"
    env_file.write_text("FAKE=1\n")
    tier1 = tmp_path / "tier1" / "positions.md"
    tier1.parent.mkdir()
    tier1.write_text("fake\n")
    return {"env": env_file, "tier1": tier1, "outside": tmp_path / "note.md"}


@pytest.mark.blocking
def test_six_synthetic_payloads_give_the_expected_exit_codes(hook_probes: dict[str, Path]) -> None:
    session = "hooktest-six"
    assert not decide("Read", {"file_path": str(hook_probes["env"])}).allowed
    assert not decide("Bash", {"command": "cat ~/.ssh/id_ed25519"}).allowed
    assert not decide(
        "Read",
        {"file_path": str(hook_probes["tier1"])},
        blocklist=BLOCKLIST + [hook_probes["tier1"].parent],
    ).allowed
    assert not decide("Read", {"file_path": str(hook_probes["outside"])}).allowed
    assert decide("Read", {"file_path": "kgme/paths.py"}).allowed
    exits = [
        run_hook(
            "kgme.hooks.pre_tool_guard", payload("Read", session, file_path=str(hook_probes["env"]))
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard", payload("Bash", session, command="cat ~/.ssh/id_ed25519")
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard",
            payload("Read", session, file_path=str(ROOT / "memory/private/x.md")),
        ),
        run_hook(
            "kgme.hooks.pre_tool_guard",
            payload("Read", session, file_path=str(hook_probes["outside"])),
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
def test_a_tilde_word_that_names_no_user_is_a_literal_not_a_crash() -> None:
    """`~330` in a table or `~nosuchuser/x` must not crash the guard: a crash fails closed and
    refuses the whole call (found 2026-09-17 when a report edit carried a `~330` cell)."""
    decision = decide("Bash", {"command": "echo '| ~330 |' and cat ~nosuchuser-kgme/notes.md"})
    assert decision.allowed, decision.reason
    assert any(p.name == "~330" for p in decision.paths)
    # the second call site of the fix (AUDIT-0021 F1): the script scan takes the same line
    same_line = {"command": "echo '| ~330 |' and cat ~nosuchuser-kgme/notes.md"}
    assert guard.script_candidates("Bash", same_line, ROOT) == ()
    assert guard.expand_home("~330") == Path("~330")
    assert guard.expand_home("~") == Path.home()
    still_fenced = decide("Bash", {"command": "cat ~/.ssh/id_ed25519"})
    assert not still_fenced.allowed, "a real home expansion still reaches the blocklist"


HUMAN = tuple(config.read_config()["hooks"]["human_paths"])
HUMAN_TARGETS = (
    "CLAUDE.md",
    "AGENTS.md",
    "docs/charter.md",
    "docs/STATUS.md",
    "docs/adr/ADR-001-x.md",
    "docs/plans/x.md",
    "docs/readers/x.md",
    "docs/handoff/2026-09-14-validator.md",
    "memory/notes/x.md",
    "memory/inbox/friction-log.md",
    "memory/daily/2026-09-23.md",
)
MACHINE_TARGETS = (
    "docs/audit/x.md",
    "docs/handoff/proposed/x.md",
    "kgme/x.py",
    "memory/agent/brief/x.md",
    "memory/templates/x.md",
)


@pytest.mark.blocking
def test_write_tools_are_refused_on_human_authored_paths_rule_4() -> None:
    """Guard rule 4 (HANDOFF-0032 follow-up, Michou 2026-09-23): Write and Edit may not name a
    human-authored path; the diff is shown, approved, and applied through Bash (ADR-004)."""
    edits = {"old_string": "a", "new_string": "b"}
    for path in HUMAN_TARGETS:
        for tool, extra in (("Write", {"content": "x"}), ("Edit", edits)):
            decision = decide(tool, {"file_path": path, **extra}, human_paths=HUMAN)
            assert not decision.allowed and "human-authored" in decision.reason, (tool, path)
    for path in MACHINE_TARGETS:
        assert decide("Write", {"file_path": path, "content": "x"}, human_paths=HUMAN).allowed
    assert decide("Read", {"file_path": "docs/adr/ADR-001-x.md"}, human_paths=HUMAN).allowed
    assert decide("Bash", {"command": "cat docs/charter.md"}, human_paths=HUMAN).allowed
    assert decide("Write", {"file_path": "docs/charter.md", "content": "x"}).allowed, "no list"
    assert guard.is_human_path(ROOT / "docs" / "audit" / "x.md", ROOT, HUMAN) is False
    assert guard.is_human_path(ROOT / "docs" / "charter.md", ROOT, HUMAN) is True
    assert guard.is_human_path(Path("/private/tmp/x.md"), ROOT, HUMAN) is False
