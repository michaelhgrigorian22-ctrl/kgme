"""`kgme merge`, its rules and records (moved out of `kgme/merge.py` by HANDOFF-0060 §3,
unchanged).

Purpose: the merge's constants; a checkout's state (`Checkout`); the track's lanes and the
paths a merge would change outside them (`read_lanes`, `lane_paths`); whether the main
checkout is at a quiet point (`is_quiet`); the merge job's ledger events and refusals
(`_event`, `read_refused`); and where the merge lock lives (`read_merge_lock`).
Inputs: the parsed `kgme.toml`, a checkout's state, paths, the ledger.
Outputs: constants, booleans, path lists, events.
Side effects: `read_refused` reads the ledger; `read_merge_lock` asks git where the lock lives
(`sync_git.read_lock_path`); the rest is pure.
"""

import fnmatch
from dataclasses import dataclass
from pathlib import Path

from kgme import events, ledger
from kgme.sync_git import read_lock_path

JOB = "merge"


TRUNK = "main"


CHECK = ("make", "check")


CHECK_TIMEOUT = 1800  # seconds; `make check` takes about a minute and a half


LOCK_POLL_WAIT = CHECK_TIMEOUT + 120  # seconds: a waiting trigger outlasts the holder's trial


ATTEMPTS = 3  # trials per run when the trunk moves during one


# HANDOFF-0055 §1, until `kgme.toml [tracks.design] lanes` holds them
DEFAULT_LANES = {
    "design": (
        "docs/design/",
        "docs/handoff/cockpit-design/",
        "docs/audit/cockpit-design/",
        "docs/readers/cockpit-design*.md",
        "tests/test_design_*.py",
    )
}


# git sets these for a hook (a commit hook gets GIT_INDEX_FILE): they would point the trial's
# git commands and its check at the committing checkout's index (found by the hook test)
HOOK_GIT_VARIABLES = (
    "GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX", "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)  # fmt: skip


TRIAL_REF = "refs/kgme/merge-trial"  # the trial's merge commit, fetched into the main repository


# a blocked landing's commit, kept apart from the disposable trial ref so no later trial, dry
# run, or design head replaces what the repair command names (review cycle 7 F19)
BLOCKED_REFS = "refs/kgme/merge-blocked/"


IN_PROGRESS = ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "REVERT_HEAD")


MOVED = "moved"


BLOCKED = "blocked"


@dataclass(frozen=True)
class Checkout:
    """What `is_quiet` reads of the main checkout."""

    branch: str
    head: str
    staged: bool
    index_lock: bool
    in_progress: tuple[str, ...]
    ref_lock: bool = False  # refs/heads/main.lock: git would fail the landing after the index


def read_lanes(settings: dict, track: str) -> tuple[str, ...]:
    """Pure: the track's lanes from `kgme.toml [tracks.<track>] lanes`, else the default."""
    configured = settings.get("tracks", {}).get(track, {}).get("lanes")
    return tuple(configured) if configured else DEFAULT_LANES.get(track, ())


def lane_paths(changed: list[str], lanes: tuple[str, ...]) -> list[str]:
    """Pure: the changed paths outside every lane, sorted. A lane ending in `/` holds its
    folder; any other lane is a glob matched against the whole path."""

    def inside(path: str) -> bool:
        return any(
            path.startswith(lane) if lane.endswith("/") else fnmatch.fnmatchcase(path, lane)
            for lane in lanes
        )

    return sorted(p for p in set(changed) if not inside(p))


def is_quiet(checkout: Checkout, tried: str) -> str:
    """Pure: why the main checkout is not at a quiet point for a merge, or "" when it is."""
    if checkout.branch != TRUNK:
        return f"the main checkout is on {checkout.branch}, not {TRUNK}"
    if checkout.head != tried:
        return f"{TRUNK} moved to {checkout.head[:12]} after the trial at {tried[:12]}"
    if checkout.ref_lock:
        return f"refs/heads/{TRUNK}.lock is held"
    if checkout.index_lock:
        return "index.lock is held"
    if checkout.in_progress:
        return f"{', '.join(checkout.in_progress)} in progress"
    if checkout.staged:
        return "the index differs from HEAD"
    return ""


def _event(kind: str, run_id: str, key: str, summary: str, **more) -> dict:
    return events.make_event(
        source="kgme",
        actor="kgme.merge",
        kind=kind,
        job=JOB,
        run_id=run_id,
        key=key,
        summary=events.clip(events.redact(summary)),
        **more,
    )


def read_refused(key: str, dirs: ledger.Dirs) -> bool:
    """Effect: whether the newest merge outcome for `key` is a refusal for the lanes."""
    closing = [e for e in ledger.read(dirs) if e["job"] == JOB and e["kind"] == "outcome"]
    mine = [e for e in closing if e["key"] == key]
    return bool(mine) and mine[-1]["status"] == "refused"


def read_merge_lock(main: Path) -> Path:
    """`kgme-merge.lock` inside the git directory, beside the sync lock."""
    return read_lock_path(main).with_name("kgme-merge.lock")
