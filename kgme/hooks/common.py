"""What both hook entry points share: reading the payload, the places to write, the key, the parent.

Purpose: keep the two hook scripts small and identical where they should be.
Inputs: stdin JSON from Claude Code; `kgme.toml`.
Outputs: dicts, strings, a `Places` naming the streams and the scratch directories.
Side effects: `read_payload` reads stdin. `read_places` reads `kgme.toml`. `read_session_parent`
reads the ledger. `read_script_text` reads one script file. Nothing here writes.
"""

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from kgme import config, ledger, paths

SUMMARY_BUDGET = 150
FILE_TOOLS = ("Read", "Edit", "Write", "NotebookEdit", "MultiEdit", "Glob", "Grep", "LS")


@dataclass(frozen=True)
class Places:
    """Where a hook writes: the two streams, the scratch directory, its payload subdirectory."""

    streams: ledger.Dirs
    scratch: Path
    payloads: Path


def read_payload() -> dict:
    """The hook JSON from stdin. A malformed payload is a ValueError; the caller blocks on it."""
    raw = sys.stdin.read()
    payload = json.loads(raw)
    if not isinstance(payload, dict) or "tool_name" not in payload:
        raise ValueError("hook payload is not an object with tool_name")
    return payload


def read_places(argv: list[str]) -> tuple[Places, dict]:
    """The real places, or the gitignored test places when called with `--test-streams`."""
    settings = config.read_config()
    if "--test-streams" in argv:
        # Errors go to the test scratch; payloads stay under logs/scratch/payloads/, the one
        # prefix ADR-019 §1 allows for payload_ref, in a subdirectory tests may delete.
        scratch = paths.scratch_test_dir(settings)
        payloads = paths.payloads_dir(settings) / "test"
        return Places(ledger.read_test_dirs(settings), scratch, payloads), settings
    places = Places(
        ledger.read_default_dirs(settings),
        paths.scratch_dir(settings),
        paths.payloads_dir(settings),
    )
    return places, settings


def call_key(payload: dict) -> str:
    """The key pairing pre and post: the vendor's tool_use_id, else a digest of the call."""
    tool_use_id = payload.get("tool_use_id")
    if isinstance(tool_use_id, str) and tool_use_id:
        return tool_use_id
    material = json.dumps(
        [payload.get("session_id"), payload.get("tool_name"), payload.get("tool_input")],
        sort_keys=True,
        default=str,
    )
    return "call:" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def read_session_parent(session_id: str, dirs: ledger.Dirs) -> str | None:
    """The first event of this session, so hook pairs nest under it (ADR-019 §3), else null."""
    first = ledger.read(dirs, run_id=session_id)
    return first[0]["id"] if first else None


def read_script_text(path: Path) -> str | None:
    """The text of a script a Bash line would run, for the guard to scan; None if unreadable,
    which the caller treats as uninspectable and refuses (review F2, cycle 2)."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def summarize_call(tool_name: str, tool_input: dict, candidates: int) -> str:
    """What the ledger line says about a call, without any text from the call itself.

    A file tool names its path in the summary, repo-relative where possible, within a budget.
    Every other tool, Bash included, is summarized by its name and the number of path-like
    fragments the guard examined: a Bash line can carry inline code or prose in a fragment that
    looks like a path, and ADR-019 §4 keeps such text out of the ledger. The raw call is in scratch.
    """
    if tool_name not in FILE_TOOLS:
        return f"{tool_name} {candidates} path-like fragments examined"
    root = paths.root()
    shown: list[str] = []
    for key in ("file_path", "path", "notebook_path", "directory"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            path = Path(value).expanduser()
            absolute = path if path.is_absolute() else root / path
            try:
                shown.append(str(absolute.resolve().relative_to(root)))
            except ValueError:
                shown.append(str(absolute))
    text = tool_name
    for index, item in enumerate(shown):
        candidate = f"{text} {item}"
        if len(candidate) > SUMMARY_BUDGET - 12:
            return f"{text} (+{len(shown) - index} more)"
        text = candidate
    return text


def withheld_call(tool_name: str, candidates: int) -> str:
    """The fallback when even the budgeted summary overflows the cap after redaction."""
    return f"{tool_name} {candidates} fragments (summary withheld: redaction overflow)"
