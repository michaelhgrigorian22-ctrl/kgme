"""Tests for the SessionEnd hook's `session:end` note (HANDOFF-0061 §1).

Purpose: the hook writes one `note` keyed `session:end` into the session's run, with Claude
Code's reason in its summary, and the cockpit's view then draws that run closed, where before
it was open; a malformed input never blocks and is recorded in the test scratch.
Inputs: hook payloads; the test streams.
Outputs: pytest assertions.
Side effects: lines in the test streams and the test scratch.
"""

import json
import time

import pytest
from hooktools import SETTINGS, TEST_SCRATCH, payload, run_hook

from cockpit import render
from kgme import events, ledger


def session(prefix: str) -> str:
    return f"{prefix}-{events.new_ulid()}"


@pytest.mark.blocking
def test_the_note_closes_the_session_on_the_next_view() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    sid = session("end")
    call = payload("Bash", sid, command="echo closed")
    assert run_hook("kgme.hooks.pre_tool_guard", call).returncode == 0
    assert (
        run_hook(
            "kgme.hooks.post_tool_ledger",
            call | {"hook_event_name": "PostToolUse", "tool_response": {"stdout": "closed"}},
        ).returncode
        == 0
    )
    mine = ledger.read(dirs, run_id=sid)
    before = render.build_view(mine, [], int(time.time() * 1000))
    assert before["runs"][sid]["closed"] is False, "a hook session is open until it ends"
    ended = run_hook(
        "kgme.hooks.session_end",
        {"session_id": sid, "hook_event_name": "SessionEnd", "reason": "prompt_input_exit"},
    )
    assert ended.returncode == 0 and ended.stderr == ""
    mine = ledger.read(dirs, run_id=sid)
    note = mine[-1]
    assert (note["kind"], note["key"], note["job"], note["actor"]) == (
        "note", "session:end", "session", "claude-code.hook",
    )  # fmt: skip
    assert note["summary"] == "session ended: prompt_input_exit"
    after = render.build_view(mine, [], int(time.time() * 1000))
    assert after["runs"][sid]["closed"] is True


@pytest.mark.blocking
def test_a_missing_reason_is_said_and_a_bad_input_never_blocks() -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    sid = session("noreason")
    assert run_hook("kgme.hooks.session_end", {"session_id": sid}).returncode == 0
    assert ledger.read(dirs, run_id=sid)[-1]["summary"] == "session ended: no reason given"
    log = TEST_SCRATCH / "hook-errors.jsonl"
    before = log.read_text().count("\n") if log.exists() else 0
    assert run_hook("kgme.hooks.session_end", "{not json").returncode == 0
    lines = log.read_text().splitlines()
    assert (
        len(lines) == before + 1
        and "session_end: JSONDecodeError" in json.loads(lines[-1])["error"]
    )
