"""PostToolUse entry point: payload to scratch, outcome to the ledger (HANDOFF-0028).

Purpose: the second half of the ADR-013 §4 pair. Raw tool input and response go to the
payload directory, gitignored; the ledger line carries their hash.
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
from kgme.hooks import common


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
        payload = common.read_payload()
        places, _ = common.read_places(argv)
        tool_name = str(payload["tool_name"])
        session_id = str(payload.get("session_id") or "no-session")
        key = common.call_key(payload)
        intent = read_matching_intent(session_id, key, places.streams)
        identifier = events.new_ulid()
        payload_ref, digest = write_payload(payload, places, identifier)
        status, failure_class = response_status(payload.get("tool_response"))
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
