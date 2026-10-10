"""`kgme sync`, the effects half: the ledger events and the run.

Purpose: `run_sync`, which orders the git effects of `kgme/sync_git.py` per HANDOFF-0040 as
Michou simplified it on 2026-10-09 (closing review cycle 5): one mode, one lock, nothing
kept between runs. Every run takes the lock, waiting for a holder up to the git bound,
reconciles, plans, commits `logs/ledger/` by pathspec if a foreign event is new, pushes if
ahead, and records one `intent` and one `outcome` per push. It never blocks the action that
invoked it: the hooks start it in the background, every git call is bounded, every path
returns 0 once git answered, and a failed push is a `transient` outcome the next trigger
retries. One run owns one push: the ledger commit it makes carries `KGME_SYNC_RUN`, which the
post-commit hook exits on. A run whose wait for the lock runs out writes one `transient` note
and exits: every run does the whole job, so the holder did this run's work or the next
trigger will. A run that waited does not push a head the holder has just attempted: that
would retry the holder's failed attempt, and the next trigger is the retry.
Inputs: the checkout to sync (`repo`), the parsed `kgme.toml`.
Outputs: an exit code: 0 done or nothing to do, 2 the ledger setting is not `logs/ledger`;
lines on stdout or stderr.
Side effects: `read_attempted` reads the ledger; `write_reconciled_outcomes`, `run_push`,
and `run_sync` append ledger events to the checkout's own streams; the git and lock effects
are those of `kgme.sync_git`.
"""

import os
import subprocess
import sys
from pathlib import Path

from kgme import events, ledger, paths, sync, sync_git
from kgme.sync_git import GIT_TIMEOUT, LEDGER_REL

JOB = "sync"
TAIL_CHARS = 100


def read_dirs(settings: dict, repo: Path) -> ledger.Dirs:
    """The two streams of the checkout at `repo`: a test clone's own, never this one's."""
    return ledger.Dirs(
        ledger=paths.ledger_dir(settings, repo),
        trace=paths.trace_dir(settings, repo),
        read_only_tools=tuple(settings["hooks"]["read_only_tools"]),
    )


def read_attempted(dirs: ledger.Dirs, head: str, since: str) -> bool:
    """Whether a push outcome for `head` was recorded at or after `since`: the run that held
    the lock attempted exactly this push, and this run does not repeat it."""
    key = f"sync:push:{head}"
    return any(
        e["kind"] == "outcome" and e["job"] == JOB and e["key"] == key and e["ts"] >= since
        for e in ledger.read(dirs, stream="ledger")
    )


def _tail(text: str) -> str:
    """The last non-empty line of `text`, clipped, for a summary."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return (lines[-1] if lines else "no output")[:TAIL_CHARS]


def _event(kind: str, run_id: str, summary: str, **more) -> dict:
    return events.make_event(
        source="kgme",
        actor=sync.OWN_ACTOR,
        kind=kind,
        job=JOB,
        run_id=run_id,
        summary=events.clip(summary),
        **more,
    )


def _outcome(run_id: str, key: str, intent_id: str, summary: str, status: str, cls: str | None):
    return _event(
        "outcome",
        run_id,
        summary,
        status=status,
        class_=cls,
        key=key,
        ref=intent_id,
        parent=intent_id,
    )


def write_reconciled_outcomes(repo: Path, dirs: ledger.Dirs, run_id: str) -> int:
    """Close every push intent no outcome answered (ADR-013 §4) as `transient`. Under the
    lock, such an intent belongs to a run that died, never to one still pushing; the push
    state is unknown and the next trigger pushes again. Returns how many."""
    remote_head = sync_git.read_remote_head(repo) or "unknown"
    opened = ledger.open_intents(JOB, dirs)
    for intent in opened:
        summary = (
            f"reconciled on start: push intent {intent['id']} had no outcome; "
            f"remote head now {remote_head}"
        )
        ledger.append(
            _outcome(run_id, intent["key"], intent["id"], summary, "error", "transient"), dirs
        )
    return len(opened)


def run_push(repo: Path, plan: sync.SyncPlan, dirs: ledger.Dirs, run_id: str, timeout: int) -> int:
    """One `intent`, one push, one `outcome`. A branch behind its upstream is refused and the
    remote left as it is; that, an unreachable remote, and a stalled one are `transient`."""
    branch, head = sync_git.read_branch(repo), sync_git.read_head(repo)
    upstream = sync_git.read_upstream(repo)
    key = f"sync:push:{head}"
    summary = f"push {branch} {head} to {upstream}: {plan.ahead} ahead, {plan.behind} behind"
    intent_id = ledger.append(_event("intent", run_id, summary, key=key), dirs)
    if plan.behind:
        summary = f"refused: {branch} is {plan.behind} behind {upstream}; pull first"
        ledger.append(_outcome(run_id, key, intent_id, summary, "refused", "transient"), dirs)
        print(f"kgme sync: {summary}", file=sys.stderr)
        return 0
    code, stderr = sync_git.push(repo, timeout)
    if code == 0:
        remote = sync_git.read_remote_head(repo)
        summary = f"pushed {branch} {head} to {upstream}; remote head {remote}"
        ledger.append(_outcome(run_id, key, intent_id, summary, "ok", None), dirs)
        print(f"kgme sync: {summary}")
        return 0
    summary = f"push failed, exit {code}: {_tail(stderr)}; the next trigger retries"
    ledger.append(_outcome(run_id, key, intent_id, summary, "error", "transient"), dirs)
    print(f"kgme sync: {summary}", file=sys.stderr)
    return 0


def run_sync(repo: Path, settings: dict) -> int:
    """The run: refuse a ledger setting other than `logs/ledger` before any effect; take the
    lock, waiting for a holder up to the git bound, or write one `transient` note and exit 0;
    then reconcile, plan, commit the ledger if it changed, push if ahead. Returns 0 once git
    answered."""
    configured = settings["paths"]["ledger_dir"]
    if configured != LEDGER_REL:
        print(
            f"kgme sync: refused: kgme.toml names {configured!r} as the ledger; "
            f"this command commits {LEDGER_REL!r} and nothing else",
            file=sys.stderr,
        )
        return 2
    timeout = int(settings.get("sync", {}).get("git_timeout_seconds", GIT_TIMEOUT))
    dirs = read_dirs(settings, repo)
    run_id = events.new_ulid()
    started = events.now_iso()
    lock, waited = sync_git.write_lock(sync_git.read_lock_path(repo), timeout)
    if lock is None:
        summary = (
            f"another run held the lock for {timeout} s; nothing done, "
            "the holder or the next trigger does the same work"
        )
        ledger.append(_event("note", run_id, summary, class_="transient", key="sync:lock"), dirs)
        print(f"kgme sync: {summary}", file=sys.stderr)
        return 0
    if waited:
        print("kgme sync: waited for the run that held the lock")
    try:
        return _run_locked(repo, dirs, run_id, timeout, started if waited else None)
    finally:
        os.close(lock)


def _run_locked(
    repo: Path, dirs: ledger.Dirs, run_id: str, timeout: int, waited_since: str | None
) -> int:
    reconciled = write_reconciled_outcomes(repo, dirs, run_id)
    if reconciled:
        print(f"kgme sync: reconciled {reconciled} open push intent(s)")
    diff, untracked = sync_git.read_ledger_diff(repo)
    counts = sync_git.read_counts(repo)
    plan = sync.plan_sync(sync.new_ledger_lines(diff, untracked), counts or (0, 0))
    if plan.commit:
        try:
            head = sync_git.commit_ledger(repo, plan.message, run_id)
        except subprocess.CalledProcessError as error:
            summary = f"ledger commit failed: {_tail(error.stderr)}"
            ledger.append(
                _event("note", run_id, summary, class_="transient", key="sync:commit"), dirs
            )
            print(f"kgme sync: {summary}", file=sys.stderr)
            return 0
        print(f"kgme sync: committed {head} ({plan.message})")
        counts = sync_git.read_counts(repo)
        plan = sync.plan_sync([], counts or (0, 0))
    if counts is None:
        print("kgme sync: this branch has no upstream; nothing pushed")
        return 0
    if not plan.push:
        print("kgme sync: nothing to push")
        return 0
    head = sync_git.read_head(repo)
    if waited_since and read_attempted(dirs, head, waited_since):
        print(f"kgme sync: the run that held the lock attempted the push of {head}; not again")
        return 0
    return run_push(repo, plan, dirs, run_id, timeout)
