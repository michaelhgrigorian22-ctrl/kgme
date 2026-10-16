"""The hook pair as recorded (HANDOFF-0028 acceptance, effects half).

Purpose: routing of the pair to trace or ledger with matching `ref` and payload hash, the
intent-plus-refusal pair, summaries that carry counts and never command text, clipped refusal
reasons, error outcomes with a class, the fail-closed pre wrapper, the post wrapper and post
hook that never block and record their own failures.
Inputs: subprocess runs of the two entry points with `--test-streams`; the wrappers with a fake
`uv` on PATH.
Outputs: pytest assertions.
Side effects: the gitignored test streams and test scratch; files under `tmp_path`.
"""

import hashlib
import os
import subprocess
from pathlib import Path

import pytest
from hooktools import (
    ROOT,
    SETTINGS,
    TEST_SCRATCH,
    payload,
    run_hook,
)

from kgme import ledger, paths
from kgme.hooks import common


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
        ["sh", str(ROOT / "control/hooks/pre_tool_guard.sh")],
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
        ["sh", str(ROOT / "control/hooks/post_tool_ledger.sh")],
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
