"""PostToolUse, PostToolUseFailure and PostToolBatch entry point: outcomes to the ledger.

Purpose: the second half of the ADR-013 §4 pair (HANDOFF-0028). Raw tool input and response go
to the payload directory, gitignored; the ledger line carries their hash. Claude Code reports a
call that failed or was interrupted through PostToolUseFailure, with `error` and `is_interrupt`
in place of `tool_response`; until HANDOFF-0061 nothing listened, so no failed call ever had an
outcome (2,509 `ok` and 0 `error` Bash outcomes in the ledger on 2026-10-26). Such a failure is
the model's to handle, not a halt: `error` with class `advisory`, or `transient` for the shapes
ADR-016 names, never `blocking`, so a failed `grep` does not draw its run as blocked.
PostToolBatch, which names no single tool, goes to `kgme.hooks.open_intents`: a call of the
batch that no post-tool record closed is closed there (HANDOFF-0061 §2, review cycle 1 F1).
Inputs: the hook JSON on stdin; `kgme.toml`; `--test-streams` for tests.
Outputs: always exit 0. The tool already ran; blocking now would change nothing.
Side effects: one payload file; one ledger or trace line. If either write fails, one line in
`hook-errors.jsonl` under the scratch directory, which `make check` refuses to ignore.
"""

import hashlib
import json
import sys
from pathlib import Path

from kgme import events, ledger
from kgme.hooks import common, open_intents

FAILURE = "PostToolUseFailure"
BATCH = "PostToolBatch"


def write_payload(payload: dict, places: common.Places, identifier: str) -> tuple[str, str]:
    """The raw call to scratch. Returns the path relative to the main checkout and its sha256."""
    places.payloads.mkdir(parents=True, exist_ok=True)
    body = json.dumps(
        {"tool_input": payload.get("tool_input"), "tool_response": payload.get("tool_response")},
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    target = places.payloads / f"{identifier}.json"
    target.write_bytes(body)
    return str(target.relative_to(places.root)), hashlib.sha256(body).hexdigest()


def read_response(payload: dict) -> object:
    """The call's response: `tool_response` for PostToolUse; for PostToolUseFailure, the error
    and whether it was an interrupt, in the shape `failure_status` reads (HANDOFF-0061 §2)."""
    if payload.get("hook_event_name") == FAILURE:
        return {
            "error": str(payload.get("error") or ""),
            "interrupted": bool(payload.get("is_interrupt")),
        }
    return payload.get("tool_response")


def failure_status(response: dict) -> tuple[str, str]:
    """`(status, class)` of a failed call: `error`, `transient` for the shapes ADR-016 names and
    `advisory` otherwise; the tool's own failure is the model's to handle, not a halt."""
    text = (
        "interrupted"
        if response.get("interrupted") and not response.get("error")
        else response.get("error", "")
    )
    return "error", "transient" if events.classify_failure(text) == "transient" else "advisory"


def response_status(tool_response: object) -> tuple[str, str | None]:
    """`(status, class)`: `error` with an ADR-016 class when the response says so, else `ok`."""
    if isinstance(tool_response, dict):
        error_text = ""
        if tool_response.get("is_error") or tool_response.get("error"):
            error_text = str(tool_response.get("error") or tool_response.get("content") or "")
        elif tool_response.get("interrupted"):
            error_text = "interrupted"
        if error_text or tool_response.get("is_error"):
            return "error", events.classify_failure(error_text)
    return "ok", None


def read_matching_intent(session_id: str, key: str, dirs: ledger.Dirs) -> dict | None:
    """The latest unclosed intent of this session with this key, else None."""
    session = ledger.read(dirs, run_id=session_id)
    closed = {e["ref"] for e in session if e["kind"] == "outcome" and e["ref"]}
    candidates = [
        e for e in session if e["kind"] == "intent" and e["key"] == key and e["id"] not in closed
    ]
    return candidates[-1] if candidates else None


def write_error(scratch: Path, error: Exception) -> None:
    """One JSON line in scratch; the only place a post-hook failure can go."""
    scratch.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"ts": events.now_iso(), "error": f"{type(error).__name__}: {error}"})
    with open(scratch / "hook-errors.jsonl", "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def main(argv: list[str]) -> int:
    """Read, store, pair, record. Always 0."""
    places: common.Places | None = None
    try:
        payload = json.loads(sys.stdin.read())
        if isinstance(payload, dict) and payload.get("hook_event_name") == BATCH:
            places, _ = common.read_places(argv)
            calls = payload.get("tool_calls") or []
            ids = {
                str(c["tool_use_id"]) for c in calls if isinstance(c, dict) and c.get("tool_use_id")
            }
            session = str(payload.get("session_id") or "no-session")
            open_intents.write_closed(session, ids, places.streams, places.scratch)
            return 0
        if not isinstance(payload, dict) or "tool_name" not in payload:
            raise ValueError("hook payload is not an object with tool_name")
        places, _ = common.read_places(argv)
        tool_name = str(payload["tool_name"])
        session_id = str(payload.get("session_id") or "no-session")
        key = common.call_key(payload)
        intent = read_matching_intent(session_id, key, places.streams)
        identifier = events.new_ulid()
        response = read_response(payload)
        payload_ref, digest = write_payload(
            payload | {"tool_response": response}, places, identifier
        )
        if payload.get("hook_event_name") == FAILURE:
            status, failure_class = failure_status(response)
        else:
            status, failure_class = response_status(response)
        parent = (
            intent["parent"] if intent else common.read_session_parent(session_id, places.streams)
        )
        ledger.append(
            events.make_event(
                id=identifier,
                source="claude-code",
                actor="claude-code.hook",
                kind="outcome",
                status=status,
                class_=failure_class,
                run_id=session_id,
                job=f"tool:{tool_name}",
                key=key,
                ref=intent["id"] if intent else None,
                parent=parent,
                summary=f"{tool_name} {status}" + ("" if intent else " (no intent found)"),
                payload_ref=payload_ref,
                payload_sha256=digest,
            ),
            places.streams,
        )
    except Exception as error:  # noqa: BLE001 - cannot block after the fact; record and surface
        try:
            scratch = places.scratch if places else common.read_places(argv)[0].scratch
            write_error(scratch, error)
        except Exception:  # noqa: BLE001
            print(f"post-tool hook failed twice: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
