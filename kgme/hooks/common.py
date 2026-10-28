"""What both hook entry points share: reading the payload, the places to write, the key, the parent.

Purpose: keep the two hook scripts small and identical where they should be.
Inputs: stdin JSON from Claude Code; `kgme.toml`.
Outputs: dicts, strings, a `Places` naming the streams and the scratch directories.
Side effects: `read_payload` reads stdin. `read_places` reads `kgme.toml`. `read_session_parent`
reads the ledger, and the environment for the loop's parent. `read_script_text` reads one
script file. `read_guard_root` checks that one folder exists. Nothing here writes.
"""

import hashlib
import json
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from kgme import cheap, config, events, ledger, paths

SUMMARY_BUDGET = 150
# HANDOFF-0032: the one ambient switch, and only for a canary run id (adopted exception to
# ADR-015's explicit configuration; recorded in AUDIT-0026). A stray value routes nothing.
CANARY_STREAMS = re.compile(r"^canary:[0-7][0-9A-HJKMNP-TV-Z]{25}$")
# HANDOFF-0063: the second ambient switch, and only for the loop's parent. `kgme loop` sets it
# in the builder's environment to its run's first intent id, which the session's own tools
# cannot change; a value without an event id's shape is ignored, never trusted.
LOOP_PARENT_ENV = "KGME_LOOP_PARENT"
FILE_TOOLS = ("Read", "Edit", "Write", "NotebookEdit", "MultiEdit", "Glob", "Grep", "LS")


@dataclass(frozen=True)
class Places:
    """Where a hook writes: the two streams, the scratch directory, its payload subdirectory,
    and the main checkout payload refs are relative to. The streams, the scratch (where the
    loop's Outputs list is, review cycle 2 F9), and the payloads are the main checkout's from
    any worktree (HANDOFF-0047 §3; Michou, 2026-10-21: payloads follow the ledger, since
    worktrees are disposable)."""

    streams: ledger.Dirs
    scratch: Path
    payloads: Path
    root: Path


def read_payload() -> dict:
    """The hook JSON from stdin. A malformed payload is a ValueError; the caller blocks on it."""
    raw = sys.stdin.read()
    payload = json.loads(raw)
    if not isinstance(payload, dict) or "tool_name" not in payload:
        raise ValueError("hook payload is not an object with tool_name")
    return payload


def read_places(argv: list[str]) -> tuple[Places, dict]:
    """The real places, or the gitignored test places when called with `--test-streams`, or
    when `KGME_TEST_STREAMS` carries a canary run id (`canary:<ULID>`): a `claude -p` run the
    canary matrix launches (HANDOFF-0032) inherits it, so its hook pairs land in the test
    streams and never in git. Any other value is ignored."""
    settings = config.read_config()
    flagged = CANARY_STREAMS.match(os.environ.get("KGME_TEST_STREAMS", ""))
    main = ledger.read_main_checkout()
    if "--test-streams" in argv or flagged:
        # Errors go to the test scratch; payloads stay under logs/scratch/payloads/, the one
        # prefix ADR-019 §1 allows for payload_ref, in a subdirectory tests may delete.
        scratch = paths.scratch_test_dir(settings, main)
        payloads = paths.payloads_dir(settings, main) / "test"
        return Places(ledger.read_test_dirs(settings), scratch, payloads, main), settings
    places = Places(
        ledger.read_default_dirs(settings),
        paths.scratch_dir(settings, main),
        paths.payloads_dir(settings, main),
        main,
    )
    return places, settings


def read_guard_root(settings: dict, env: Mapping[str, str] = os.environ) -> Path:
    """The repository the guard judges paths against: this checkout, or the cheap lane's
    export when its launcher names one in `KGME_GUARD_ROOT` (HANDOFF-0053). The hooks then
    run this checkout's code, so the session cannot edit them and the ledger stays this
    checkout's, while its edits are judged inside the export. Honoured only for an existing
    folder strictly under `kgme.toml [paths] work_dir` and outside this checkout; any other
    value is a ValueError, and the guard blocks on it. Set on the guard's command line by the
    launcher, so the session's own tools cannot change it."""
    named = env.get(cheap.GUARD_ROOT_ENV, "")
    here = paths.root()
    if not named:
        return here
    root = Path(named).expanduser().resolve()
    work = cheap.read_work_dir(settings, here).resolve()
    inside = root != work and root.is_relative_to(work) and root.is_dir()
    if not inside or root.is_relative_to(here) or here.is_relative_to(root):
        raise ValueError(
            f"{cheap.GUARD_ROOT_ENV} names {root}, not a folder under {work} outside {here}"
        )
    return root


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


def read_session_parent(
    session_id: str, dirs: ledger.Dirs, env: Mapping[str, str] = os.environ
) -> str | None:
    """The first event of this session, so hook pairs nest under it (ADR-019 §3); before the
    session has one, the loop's first intent that `KGME_LOOP_PARENT` names when it has the
    exact shape of an event id (HANDOFF-0063), so the session's first event sits under the
    loop's intent and every later pair under that event, as today; else null. A value of any
    other shape, a trailing newline included, is ignored, never trusted (review cycle 1 F1)."""
    first = ledger.read(dirs, run_id=session_id)
    if first:
        return first[0]["id"]
    named = env.get(LOOP_PARENT_ENV, "")
    return named if events.ULID_PATTERN.fullmatch(named) else None


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
