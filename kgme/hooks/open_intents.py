"""PostToolBatch, the backstop: a call of the batch that no post-tool record closed is closed now.

Purpose: HANDOFF-0061 §2. Claude Code fires PostToolBatch once after every call of a batch
has resolved, before the next model request, with the batch's `tool_use_id`s; a single call
is a batch of one. The per-call post hooks have finished by then (measured in a clone on
2026-10-26: the slower call's outcome was written 44 ms before the batch arrived), so an
intent of this session whose key is one of the batch's ids and which still has no outcome got
no post-tool record at all. It gets `error`, class `transient` (an outcome must carry a status,
and its result is unknown, never `ok`): "no post-tool record; closed at the end of its batch".
Only the batch's own calls are ever closed: no age is guessed, no sibling still running is
touched, and no intent from before the session's batch, history included, is reached (review
cycle 1 F1, F2). This is stronger than the next call's PreToolUse (§2's letter): the batch
ends before the next call can start.
Inputs: the session id, the batch's tool-use ids, the streams, the scratch directory.
Outputs: the number of intents closed.
Side effects: one outcome line per closed intent; a failure is one line in
`hook-errors.jsonl` under scratch, never an exception.
"""

import json
from pathlib import Path

from kgme import events, ledger

NO_POST = "no post-tool record; closed at the end of its batch"


def unanswered(session: list[dict], ids: set[str]) -> list[dict]:
    """Pure: the hook's tool intents in `session` whose key is one of `ids` and that have no
    outcome."""
    closed = {e.get("ref") for e in session if e["kind"] == "outcome" and e.get("ref")}
    return [
        e
        for e in session
        if e["kind"] == "intent"
        and e["id"] not in closed
        and e.get("actor") == "claude-code.hook"
        and str(e.get("job") or "").startswith("tool:")
        and e.get("key") in ids
    ]


def write_closed(session_id: str, ids: set[str], dirs: ledger.Dirs, scratch: Path) -> int:
    """Effect: close this batch's unanswered intents; never raises."""
    try:
        if not ids:
            return 0
        count = 0
        for intent in unanswered(ledger.read(dirs, run_id=session_id), ids):
            tool = str(intent["job"]).removeprefix("tool:")
            ledger.append(
                events.make_event(
                    source="claude-code",
                    actor="claude-code.hook",
                    kind="outcome",
                    status="error",
                    class_="transient",
                    run_id=session_id,
                    job=intent["job"],
                    key=intent.get("key"),
                    ref=intent["id"],
                    parent=intent.get("parent"),
                    summary=f"{tool} {NO_POST}",
                ),
                dirs,
            )
            count += 1
        return count
    except Exception as error:  # noqa: BLE001 - recorded, never raised
        try:
            scratch.mkdir(parents=True, exist_ok=True)
            line = json.dumps(
                {"ts": events.now_iso(), "error": f"open_intents: {type(error).__name__}: {error}"}
            )
            with open(scratch / "hook-errors.jsonl", "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except Exception:  # noqa: BLE001 - nothing left to report to
            pass
        return 0
