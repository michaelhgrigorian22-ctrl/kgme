"""`kgme sync`, the pure half: what one sync run should do, decided from git's own answers.

Purpose: turn the new lines under `logs/ledger/` and the branch's position against its
upstream into a `SyncPlan` (HANDOFF-0040): whether to commit the ledger, with which message,
and whether to push. Nothing but the ledger is ever committed by this command, and nothing
is ever forced; `kgme/sync_io.py` carries the effects.
Inputs: the text of `git diff HEAD -- logs/ledger`, the text of untracked ledger files, the
`behind ahead` pair of `git rev-list --left-right --count @{u}...HEAD`.
Outputs: a `SyncPlan`. There is one mode: every run commits what changed and pushes what is
ahead (Michou, 2026-10-09, closing review cycle 5 of HANDOFF-0040).
Side effects: none.

The ledger is committed only when it holds events that are not this command's own: the push
events a sync writes are recorded after the ledger commit by construction, and if they alone
counted as a change, every run would commit the record of the previous one.
"""

import json
from dataclasses import dataclass

OWN_ACTOR = "kgme.sync"


@dataclass(frozen=True)
class SyncPlan:
    """One run's decisions. `commit` is false when nothing foreign is new."""

    commit: bool
    message: str
    push: bool
    behind: int
    ahead: int
    new_events: int


def added_lines(diff_text: str) -> list[str]:
    """The lines a unified diff adds, their `+` stripped; file headers (`+++`) excluded."""
    return [
        line[1:]
        for line in diff_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


def new_ledger_lines(diff_text: str, untracked_texts: list[str]) -> list[str]:
    """Every ledger line not yet in HEAD: added lines of tracked files plus whole untracked
    files (a new month's file is untracked until its first commit)."""
    lines = added_lines(diff_text)
    for text in untracked_texts:
        lines.extend(line for line in text.splitlines() if line.strip())
    return lines


def _event_of(line: str) -> dict | None:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    return event if isinstance(event, dict) else None


def is_own_event(line: str) -> bool:
    """True if `line` is an event this command wrote. A line that is not JSON is not ours."""
    event = _event_of(line)
    return event is not None and event.get("actor") == OWN_ACTOR


def last_timestamp(lines: list[str]) -> str:
    """The latest `ts` among the lines that parse, else `unknown`."""
    latest = ""
    for line in lines:
        event = _event_of(line)
        if event is not None and isinstance(event.get("ts"), str):
            latest = max(latest, event["ts"])
    return latest or "unknown"


def parse_counts(rev_list_output: str) -> tuple[int, int]:
    """`(behind, ahead)` from `git rev-list --left-right --count @{u}...HEAD`."""
    parts = rev_list_output.split()
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError(f"expected two counts from git rev-list, got {rev_list_output!r}")
    return int(parts[0]), int(parts[1])


def plan_sync(new_lines: list[str], counts: tuple[int, int]) -> SyncPlan:
    """Decide the run. `counts` is `(behind, ahead)`."""
    behind, ahead = counts
    foreign = [line for line in new_lines if not is_own_event(line)]
    commit = bool(foreign)
    message = f"ledger: {len(new_lines)} events through {last_timestamp(new_lines)}"
    return SyncPlan(
        commit=commit,
        message=message if commit else "",
        push=ahead > 0,
        behind=behind,
        ahead=ahead,
        new_events=len(new_lines),
    )
