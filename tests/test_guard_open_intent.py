"""Tests for HANDOFF-0061 §2: every intent gets an outcome.

Purpose: the measured cause first. Claude Code reports a call that failed or was interrupted
through PostToolUseFailure, which nothing recorded, so no failed call had an outcome; the post
hook now closes its intent `error`, `advisory` (`transient` for the shapes ADR-016 names), never
`blocking`. Then the backstop, at PostToolBatch (review cycle 1 F1): a call of the batch whose
post record never came (suppressed here) is closed `error`, `transient`, "no post-tool record;
closed at the end of its batch", before the next call; a sibling that ran long and got its real
outcome keeps it, paired; an older open intent of the same session (history, review cycle 1
F2) and another session's are never reached.
Inputs: hook payloads; planted intents in the test streams.
Outputs: pytest assertions.
Side effects: lines in the test streams.
"""

from datetime import datetime, timedelta

import pytest
from hooktools import SETTINGS, payload, run_hook

from kgme import events, ledger
from kgme.hooks import open_intents


def session(prefix: str) -> str:
    return f"{prefix}-{events.new_ulid()}"


def outcomes_of(dirs: ledger.Dirs, sid: str, intent_id: str) -> list[dict]:
    return [
        e
        for e in ledger.read(dirs, run_id=sid)
        if e["kind"] == "outcome" and e.get("ref") == intent_id
    ]


def intent_of(dirs: ledger.Dirs, sid: str, call: dict) -> dict:
    return [
        e
        for e in ledger.read(dirs, run_id=sid)
        if e["kind"] == "intent" and e.get("key") == call["tool_use_id"]
    ][-1]


def batch(sid: str, *calls: dict) -> dict:
    return {
        "session_id": sid,
        "hook_event_name": "PostToolBatch",
        "tool_calls": [
            {
                "tool_name": c["tool_name"],
                "tool_input": c["tool_input"],
                "tool_use_id": c["tool_use_id"],
            }
            for c in calls
        ],
    }


def plant_intent(dirs: ledger.Dirs, sid: str, age_s: float, key: str) -> str:
    """An intent of this session written `age_s` seconds ago that nothing ever answered."""
    ts = (datetime.now().astimezone() - timedelta(seconds=age_s)).isoformat(timespec="milliseconds")
    return ledger.append(
        events.make_event(
            source="claude-code", actor="claude-code.hook", kind="intent", run_id=sid,
            job="tool:Bash", key=key, summary="Bash planted", ts=ts,
        ),
        dirs,
    )  # fmt: skip


@pytest.mark.blocking
@pytest.mark.parametrize(
    "error,interrupt,expected",
    [
        ("Exit code 1", False, ("error", "advisory")),
        ("", True, ("error", "advisory")),
        ("Command timed out after 2m", False, ("error", "transient")),
    ],
)
def test_a_failed_or_interrupted_call_closes_its_intent(
    error: str, interrupt: bool, expected
) -> None:
    dirs = ledger.read_test_dirs(SETTINGS)
    sid = session("fail")
    call = payload("Bash", sid, command="false")
    assert run_hook("kgme.hooks.pre_tool_guard", call).returncode == 0
    intent = intent_of(dirs, sid, call)
    failure = call | {
        "hook_event_name": "PostToolUseFailure",
        "error": error,
        "is_interrupt": interrupt,
    }
    assert run_hook("kgme.hooks.post_tool_ledger", failure).returncode == 0
    (closed,) = outcomes_of(dirs, sid, intent["id"])
    assert (closed["status"], closed["class"]) == expected and closed["summary"] == "Bash error"


@pytest.mark.blocking
def test_a_suppressed_post_leaves_no_open_intent_after_the_next_call() -> None:
    """The acceptance test, with an immediate next call (review cycle 1 F1: no age involved)."""
    dirs = ledger.read_test_dirs(SETTINGS)
    sid = session("suppressed")
    first = payload("Bash", sid, command="echo first")
    assert run_hook("kgme.hooks.pre_tool_guard", first).returncode == 0
    # its PostToolUse never runs; the batch of one ends
    assert run_hook("kgme.hooks.post_tool_ledger", batch(sid, first)).returncode == 0
    (closed,) = outcomes_of(dirs, sid, intent_of(dirs, sid, first)["id"])
    assert (closed["status"], closed["class"]) == ("error", "transient")
    assert closed["summary"] == "Bash no post-tool record; closed at the end of its batch"
    nxt = payload("Bash", sid, command="echo next")
    assert run_hook("kgme.hooks.pre_tool_guard", nxt).returncode == 0
    answered = {e.get("ref") for e in ledger.read(dirs, run_id=sid) if e["kind"] == "outcome"}
    still_open = [
        e
        for e in ledger.read(dirs, run_id=sid)
        if e["kind"] == "intent" and e["id"] not in answered
    ]
    assert [e["key"] for e in still_open] == [nxt["tool_use_id"]], "only the next call's own"


@pytest.mark.blocking
def test_a_long_sibling_keeps_its_real_outcome_paired() -> None:
    """Review cycle 1 F1: a parallel call that runs long gets its real post before the batch
    ends; the batch closes nothing of it and its outcome stays the one paired."""
    dirs = ledger.read_test_dirs(SETTINGS)
    sid = session("sibling")
    slow, quick = (
        payload("Bash", sid, command="sleep 30"),
        payload("Bash", sid, command="echo quick"),
    )
    for call in (slow, quick):
        assert run_hook("kgme.hooks.pre_tool_guard", call).returncode == 0
    for call in (quick, slow):  # the slow one's post comes last, whenever it comes
        post = call | {"hook_event_name": "PostToolUse", "tool_response": {"stdout": ""}}
        assert run_hook("kgme.hooks.post_tool_ledger", post).returncode == 0
    assert run_hook("kgme.hooks.post_tool_ledger", batch(sid, slow, quick)).returncode == 0
    for call in (slow, quick):
        outcomes = outcomes_of(dirs, sid, intent_of(dirs, sid, call)["id"])
        assert [(o["status"], o["summary"]) for o in outcomes] == [("ok", "Bash ok")]


@pytest.mark.blocking
def test_history_in_the_same_session_and_another_sessions_are_never_reached() -> None:
    """Review cycle 1 F2: only the batch's own calls are closed; an open intent from before it in
    the same session (the historical cohort, or a resumed session's past) stays open."""
    dirs = ledger.read_test_dirs(SETTINGS)
    sid, other = session("history"), session("other")
    old = plant_intent(dirs, sid, 3 * 86400, "toolu_history_old")
    recent = plant_intent(dirs, sid, 120, "toolu_history_recent")
    elsewhere = plant_intent(dirs, other, 60, "toolu_elsewhere")
    call = payload("Bash", sid, command="echo resumed")
    assert run_hook("kgme.hooks.pre_tool_guard", call).returncode == 0
    assert run_hook("kgme.hooks.post_tool_ledger", batch(sid, call)).returncode == 0
    assert outcomes_of(dirs, sid, old) == [] and outcomes_of(dirs, sid, recent) == []
    assert outcomes_of(dirs, other, elsewhere) == []
    assert len(outcomes_of(dirs, sid, intent_of(dirs, sid, call)["id"])) == 1, "the batch's own is"


@pytest.mark.blocking
def test_unanswered_is_pure_and_reads_only_the_batchs_hook_intents() -> None:
    def intent(key: str, **fields) -> dict:
        return {
            "id": events.new_ulid(),
            "kind": "intent",
            "actor": "claude-code.hook",
            "job": "tool:Bash",
            "key": key,
            **fields,
        }

    wanted, answered, outside, job_run = (
        intent("a"),
        intent("b"),
        intent("c"),
        intent("d", job="brief"),
    )
    reply = {"id": events.new_ulid(), "kind": "outcome", "ref": answered["id"]}
    found = open_intents.unanswered([wanted, answered, outside, job_run, reply], {"a", "b", "d"})
    assert [e["id"] for e in found] == [wanted["id"]]
