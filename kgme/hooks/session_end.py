"""SessionEnd entry point: the session's `session:end` note (HANDOFF-0061 §1).

Purpose: `cockpit/render.py` closes a hook session (a run of `tool:*` pairs) when its newest
event is a `note` keyed `session:end`, and until this module nothing wrote one, so every
Claude Code session stayed open in the cockpit. `control/hooks/session_end_sync.sh` runs this
first, then starts `kgme sync`, so the note reaches the remote with the session's other events.
The note carries the reason Claude Code gives (`clear`, `logout`, `prompt_input_exit`,
`other`, or whatever a later build names), in its summary.
Inputs: the hook JSON on stdin (`session_id`, `reason`); `kgme.toml`; `--test-streams` for tests.
Outputs: always exit 0. The session is over; nothing is left to block.
Side effects: one ledger line; if it cannot be written, one line in `hook-errors.jsonl` under
the scratch directory, which `make check` refuses to ignore.
"""

import json
import sys

from kgme import events, ledger
from kgme.hooks import common

KEY = "session:end"
JOB = "session"


def read_input() -> dict:
    """The hook JSON from stdin; a SessionEnd input names no tool, so `common.read_payload`
    does not apply."""
    payload = json.loads(sys.stdin.read())
    if not isinstance(payload, dict):
        raise ValueError("hook payload is not an object")
    return payload


def end_note(session_id: str, reason: str, parent: str | None) -> dict:
    """Pure: the note `render.run_closed` reads as the session's end."""
    return events.make_event(
        source="claude-code",
        actor="claude-code.hook",
        kind="note",
        run_id=session_id,
        job=JOB,
        key=KEY,
        parent=parent,
        summary=events.clip(f"session ended: {reason or 'no reason given'}"),
    )


def main(argv: list[str]) -> int:
    """Read, write the note. Always 0."""
    places: common.Places | None = None
    try:
        payload = read_input()
        places, _ = common.read_places(argv)
        session_id = str(payload.get("session_id") or "no-session")
        reason = str(payload.get("reason") or "")
        parent = common.read_session_parent(session_id, places.streams)
        ledger.append(end_note(session_id, reason, parent), places.streams)
    except Exception as error:  # noqa: BLE001 - nothing to block; record and surface
        try:
            scratch = places.scratch if places else common.read_places(argv)[0].scratch
            scratch.mkdir(parents=True, exist_ok=True)
            line = json.dumps(
                {"ts": events.now_iso(), "error": f"session_end: {type(error).__name__}: {error}"}
            )
            with open(scratch / "hook-errors.jsonl", "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except Exception:  # noqa: BLE001
            print(f"session-end hook failed twice: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
