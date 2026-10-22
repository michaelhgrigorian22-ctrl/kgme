"""`kgme merge design`: the design track lands on `main` as soon as it is green (HANDOFF-0055).

Purpose: merge a track's branch into `main` without Michou, when the merge stays inside the
track's lanes and passes `make check`. The pure half (`lane_paths`, `is_quiet`) decides; the
effects half (`run_merge`) reads git, runs the trial, and merges. Every run resolves the main
checkout as the ledger does (`ledger.read_main_checkout`), so the post-commit hook may start
it from the design worktree. A run with nothing to merge writes nothing. Otherwise: a trial
in a temporary local clone at `main` (`git merge --no-ff <track>`, then the track's
check, `make check` by default), removed however it ends; a refusal naming every path the
merge would change outside the lanes, which Michou merges by hand after a green trial; and,
only at a quiet point in the main checkout (nothing staged, no `index.lock`, no merge,
rebase, or cherry-pick in progress, on `main` at the commit the trial tried), the same merge
there, message `merge: <track> <sha> (kgme merge)`. Not quiet is `transient`: the next
trigger retries. One intent and one outcome per run.
Inputs: the checkout (any worktree of the repository), the parsed `kgme.toml`, the track,
whether this is a dry run.
Outputs: an exit code: 0 merged, nothing to do, or a `transient` wait; 1 refused or red;
2 not configured. Lines on stdout or stderr.
Side effects: git reads; a temporary clone outside the repository, removed; on success
one merge commit in the main checkout, which `run_merge` then pushes through `kgme sync` (a
`git merge` fires no post-commit hook); ledger events in the main checkout's streams. A dry
run runs the trial and writes no event and no merge.
"""

import fnmatch
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from kgme import events, ledger
from kgme.sync_git import read_lock_path, run_git, write_lock

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


def read_sha(main: Path, ref: str) -> str:
    """Effect: the full commit sha `ref` names in `main`, or "" when there is none."""
    done = run_git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], main, check=False)
    return done.stdout.strip()


def read_checkout(main: Path) -> Checkout:
    """Effect: the main checkout's branch, HEAD, index, and git operation state."""
    git_dir = Path(run_git(["rev-parse", "--absolute-git-dir"], main).stdout.strip())
    staged = run_git(["diff", "--cached", "--quiet"], main, check=False).returncode != 0
    return Checkout(
        branch=run_git(["rev-parse", "--abbrev-ref", "HEAD"], main).stdout.strip(),
        head=read_sha(main, "HEAD"),
        staged=staged,
        index_lock=(git_dir / "index.lock").exists(),
        ref_lock=(git_dir / "refs" / "heads" / f"{TRUNK}.lock").exists(),
        in_progress=tuple(n for n in IN_PROGRESS if (git_dir / n).exists()),
    )


def run_trial(
    main: Path, track_sha: str, trunk_sha: str, check: tuple[str, ...], message: str = ""
) -> tuple[bool, list[str], str]:
    """Effect: the merge and the check in a temporary local clone detached at `trunk_sha`,
    removed however it ends. A clone, not a worktree: a worktree's hooks and ledger resolve to
    the main checkout (HANDOFF-0047), so tests that need their own checkout fail there and the
    trial's events would land in the main checkout's streams (found on the first dry run,
    2026-10-21). Returns (green, the paths the merge changes, a line on the result). The trial's
    merge runs no hook; the check runs with `core.hooksPath` set as `make setup` sets it."""
    where = Path(tempfile.mkdtemp(prefix="kgme-merge-")) / "trial"
    try:
        run_git(["clone", "--quiet", "--shared", "--no-checkout", str(main), str(where)], main)
        run_git(["checkout", "--quiet", "--detach", trunk_sha], where)
        # the commit that lands is this one, made here with the main checkout's identity and
        # the final message, then fetched into the main repository (review cycle 4 F13)
        name = run_git(["config", "user.name"], main, check=False).stdout.strip() or "kgme"
        email = run_git(["config", "user.email"], main, check=False).stdout.strip()
        merged = run_git(
            ["-c", "core.hooksPath=/dev/null", "-c", f"user.name={name}", "-c",
             f"user.email={email or 'kgme@localhost'}", "merge", "--no-ff",
             "-m", message or f"merge: {track_sha[:12]} (kgme merge trial)", track_sha],
            where,
            check=False,
        )  # fmt: skip
        if merged.returncode != 0:
            conflicted = run_git(
                ["diff", "-z", "--name-only", "--diff-filter=U"], where, check=False
            )
            paths = [p for p in conflicted.stdout.split("\0") if p]
            return False, paths, f"the merge does not apply: conflicts in {', '.join(paths)}"
        # NUL-delimited and with renames off, so a rename out of a human path names its source
        # and a path with spaces stays whole (review cycle 1 F2)
        listed = run_git(["diff", "-z", "--no-renames", "--name-only", "HEAD^1", "HEAD"], where)
        changed = [p for p in listed.stdout.split("\0") if p]
        run_git(["fetch", "--quiet", "--no-tags", str(where), f"HEAD:{TRIAL_REF}"], main)
        run_git(["config", "core.hooksPath", "control/git-hooks"], where)
        # the hook's `uv run` exports its own environment; the trial uses the clone's
        env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        ran = subprocess.run(
            list(check), cwd=where, capture_output=True, text=True, timeout=CHECK_TIMEOUT,
            env=env,
        )  # fmt: skip
        if ran.returncode != 0:
            log = main / "logs" / "scratch" / "merge" / f"trial-{trunk_sha[:12]}.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(ran.stdout + ran.stderr, encoding="utf-8")
            failed = [
                ln
                for ln in ran.stdout.splitlines()
                if ln.startswith(("FAILED", "ERROR")) or "[blocking]" in ln
            ]
            first = (failed or (ran.stdout + ran.stderr).strip().splitlines()[-1:] or [""])[0]
            return (
                False,
                changed,
                f"{' '.join(check)} exited {ran.returncode}: {first[:140]}; "
                f"{len(failed)} failing line(s); full output {log.relative_to(main)}",
            )
        return True, changed, f"{' '.join(check)} green on the trial merge"
    finally:
        shutil.rmtree(where.parent, ignore_errors=True)


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


def write_cleared_blocks(main: Path) -> list[str]:
    """Effect: the kept refs of blocked landings, after deleting each whose design commit (its
    second parent) is on `main`, by Michou's repair or by a later landing; those that remain."""
    listed = run_git(["for-each-ref", "--format=%(refname)", BLOCKED_REFS], main).stdout.split()
    remaining = []
    for ref in listed:
        landed = run_git(["merge-base", "--is-ancestor", f"{ref}^2", TRUNK], main, check=False)
        if landed.returncode == 0:
            run_git(["update-ref", "-d", ref], main, check=False)
        else:
            remaining.append(ref)
    return remaining


def read_refused(key: str, dirs: ledger.Dirs) -> bool:
    """Effect: whether the newest merge outcome for `key` is a refusal for the lanes."""
    closing = [e for e in ledger.read(dirs) if e["job"] == JOB and e["kind"] == "outcome"]
    mine = [e for e in closing if e["key"] == key]
    return bool(mine) and mine[-1]["status"] == "refused"


MOVED = "moved"
BLOCKED = "blocked"


def read_landed_state(main: Path) -> tuple[str, str, bool]:
    """Effect: the branch HEAD names ("" when detached), `main`'s commit, and whether the
    index differs from HEAD."""
    named = run_git(["symbolic-ref", "-q", "HEAD"], main, check=False).stdout.strip()
    staged = run_git(["diff-index", "--cached", "--quiet", "HEAD"], main, check=False)
    return named.removeprefix("refs/heads/"), read_sha(main, TRUNK), staged.returncode != 0


def write_landing(main: Path, merged: str, trunk_sha: str, kept_ref: str) -> tuple[str, str, str]:
    """Effect: land the trial's merge commit `merged`, whose first parent is the tested
    `trunk_sha`, by `git merge --ff-only` in the main checkout, as any merge is made.
    Before git is invoked: the quiet point and the branch are read again (a move or a wait
    there touches nothing), and `merged` is kept at `kept_ref`. Once git is invoked, only a
    verified landing (on `main`, `main` is `merged`, the index matches HEAD) counts; any
    other end, a git error, or a check that cannot run is `BLOCKED`, with `kept_ref` left in
    place (Cowork's ruling on F16, cycle 8: nothing after that point is transient). A
    verified landing deletes `kept_ref`. Returns (the landed commit, "", "") or ("", why,
    state): `MOVED` or "" (a wait) before git, `BLOCKED` after it."""
    parent = run_git(["rev-parse", f"{merged}^1"], main, check=False).stdout.strip()
    if parent != trunk_sha:
        return "", "the trial's commit is not a merge of this main", ""
    checkout = read_checkout(main)
    if checkout.branch == TRUNK and checkout.head != trunk_sha:
        return "", f"{TRUNK} moved", MOVED
    waiting = is_quiet(checkout, trunk_sha)
    if waiting:
        return "", waiting, ""
    run_git(["update-ref", kept_ref, merged], main)  # recovery state first
    try:  # every effect from here on, diagnostics included, is inside the boundary (cycle 9)
        done = run_git(["merge", "--ff-only", "--quiet", merged], main, check=False)
        branch, now, staged = read_landed_state(main)
        if branch == TRUNK and now == merged and not staged:
            run_git(["update-ref", "-d", kept_ref], main, check=False)
            return merged, "", ""
        moved_other = branch != TRUNK and read_sha(main, branch or "HEAD") == merged
        tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
        state = (
            f"HEAD is on {branch or 'a detached HEAD'}"
            + (f", which the fast-forward moved to {merged[:12]}" if moved_other else "")
            + f"; {TRUNK} is at {now[:12]}"
            + ("; the index differs from HEAD (the trial's tree is staged)" if staged else "")
            + (f"; git exited {done.returncode}: {tail[0][:100]}" if done.returncode else "")
        )
    except (OSError, subprocess.SubprocessError) as error:
        return "", f"git failed or could not be checked: {type(error).__name__}: {error}", BLOCKED
    return "", state, BLOCKED


def read_merge_lock(main: Path) -> Path:
    """`kgme-merge.lock` inside the git directory, beside the sync lock."""
    return read_lock_path(main).with_name("kgme-merge.lock")


def read_heads(main: Path, track: str) -> tuple[str, str, int]:
    """Effect: the track's and the trunk's commits and how many the trunk lacks; ("", "", 0)
    when either branch is missing."""
    track_sha, trunk_sha = read_sha(main, track), read_sha(main, TRUNK)
    if not track_sha or not trunk_sha:
        return "", "", 0
    ahead = int(run_git(["rev-list", "--count", f"{TRUNK}..{track_sha}"], main).stdout)
    return track_sha, trunk_sha, ahead


def write_reconciled(main: Path, dirs: ledger.Dirs) -> int:
    """Effect: close every merge intent no outcome answered. Under the lock such an intent
    belongs to a run that died (review cycle 1 F5): `ok` when its commit is on `main` (it died
    after the merge, cycle 2 F5), else `transient`, and this run tries again. Returns how many."""
    opened = ledger.open_intents(JOB, dirs)
    for intent in opened:
        sha = (intent["key"] or "").rsplit(":", 1)[-1]
        landed = (
            bool(sha)
            and run_git(["merge-base", "--is-ancestor", sha, TRUNK], main, check=False).returncode
            == 0
        )
        line = f"reconciled on start: merge intent {intent['id']} had no outcome; " + (
            f"{sha[:12]} is on main" if landed else "trying again"
        )
        ledger.append(
            _event(
                "outcome", events.new_ulid(), intent["key"], line,
                status="ok" if landed else "error", class_=None if landed else "transient",
                ref=intent["id"], parent=intent["id"],
            ),
            dirs,
        )  # fmt: skip
    return len(opened)


def run_merge(base: Path, settings: dict, track: str = "design", dry_run: bool = False) -> int:
    """`kgme merge <track> [--dry-run]`: nothing to do, or under the merge lock one attempt per
    trunk head, each a trial then a refusal, a wait, or the merge and its push; an attempt
    that finds the trunk moved during its trial is tried again, up to `ATTEMPTS`."""
    for name in HOOK_GIT_VARIABLES:
        os.environ.pop(name, None)
    main = ledger.read_main_checkout(base)
    lanes = read_lanes(settings, track)
    if not lanes:
        print(f"kgme merge: {track} has no lanes in kgme.toml [tracks.{track}]", file=sys.stderr)
        return 2
    # a run that died after its merge left an intent open with nothing left to merge, so the
    # no-work return waits for the reconciling (review cycle 2 F5)
    if not read_heads(main, track)[2] and not ledger.open_intents(
        JOB, ledger.read_base_dirs(settings, main)
    ):
        print(f"kgme merge: {TRUNK} holds every {track} commit; nothing to do")
        return 0
    # a second trigger waits out the holder's trial rather than vanishing (review cycle 1 F4)
    descriptor, _ = write_lock(read_merge_lock(main), LOCK_POLL_WAIT)
    if descriptor is None:
        print(f"kgme merge: the lock was held past {LOCK_POLL_WAIT}s; the next trigger retries")
        return 0
    try:
        dirs = ledger.read_base_dirs(settings, main)
        if not dry_run:
            write_reconciled(main, dirs)
        for _ in range(ATTEMPTS):
            heads = read_heads(main, track)  # under the lock, never before it (F4)
            if not heads[2]:
                print(f"kgme merge: {TRUNK} holds every {track} commit; nothing to do")
                return 0
            code, again = run_attempt(main, settings, track, lanes, heads, dry_run, dirs)
            if not again:
                return code
        return 0
    finally:
        os.close(descriptor)


def run_attempt(
    main: Path,
    settings: dict,
    track: str,
    lanes: tuple[str, ...],
    heads: tuple[str, str, int],
    dry_run: bool,
    dirs: ledger.Dirs,
) -> tuple[int, bool]:
    """Effect: one intent, one trial, one outcome, and on success the merge of the tested
    commit and its push. Returns (exit code, whether to try again against a moved trunk)."""
    track_sha, trunk_sha, ahead = heads
    run_id, key = events.new_ulid(), f"merge:{track}:{track_sha}"
    kept = [] if dry_run else write_cleared_blocks(main)
    if kept and is_quiet(read_checkout(main), trunk_sha):
        # a landing left blocked and not repaired: refuse every head, writing nothing, until
        # the checkout is quiet again (the arbiters' ruling on F16 and F18, Fable's latch;
        # across heads, cycle 7 F19)
        print(
            f"kgme merge: {track} {track_sha[:12]}: refused; a blocked landing is kept at "
            f"{kept[0]} and the checkout is not quiet; see the newest merge outcome",
            file=sys.stderr,
        )
        return 1, False
    if not dry_run and read_refused(key, dirs):
        # it waits for Michou's hand; a new trial would only write the same refusal again
        # (Cowork's advisory on cycle 3); a dry run still runs it
        print(f"kgme merge: {track} {track_sha[:12]} was already refused for its lanes; waiting")
        return 0, False
    what = f"merge {track} {track_sha[:12]} ({ahead} commits) into {TRUNK} {trunk_sha[:12]}"
    intent = None if dry_run else ledger.append(_event("intent", run_id, key, what), dirs)

    def write_outcome(status: str, cls: str | None, line: str) -> None:
        print(f"kgme merge: {line}", file=sys.stdout if status == "ok" else sys.stderr)
        if intent:
            closing = _event(
                "outcome", run_id, key, line, status=status, class_=cls, ref=intent, parent=intent
            )
            ledger.append(closing, dirs)

    try:
        check = tuple(settings.get("tracks", {}).get(track, {}).get("check", CHECK))
        message = f"merge: {track} {track_sha[:12]} (kgme merge)"
        green, changed, result = run_trial(main, track_sha, trunk_sha, check, message)
        outside = lane_paths(changed, lanes)
        if not green:
            write_outcome("error", "blocking", f"{what}: trial red: {result}; {TRUNK} untouched")
            return 1, False
        if outside:
            write_outcome(
                "refused",
                "advisory",
                f"{what}: trial green, but it changes {len(outside)} path(s) outside the lanes: "
                f"{', '.join(outside)}; Michou merges it by hand (git merge --no-ff {track})",
            )
            return 1, False
        if dry_run:
            print(f"kgme merge: dry run; {what}: {result}; {len(changed)} paths, all in the lanes")
            return 0, False
        checkout = read_checkout(main)
        if checkout.branch == TRUNK and checkout.head != trunk_sha:
            write_outcome("error", "transient", f"{what}: {TRUNK} moved during the trial; again")
            return 0, True
        waiting = is_quiet(checkout, trunk_sha)
        if waiting:
            write_outcome("error", "transient", f"{what}: trial green; waiting: {waiting}")
            return 0, False
        # the trial's own merge commit lands, and only on the main it was tried on (cycle 4 F13)
        kept_ref = f"{BLOCKED_REFS}{track_sha[:12]}"
        landed, why, state = write_landing(main, read_sha(main, TRIAL_REF), trunk_sha, kept_ref)
        if state == MOVED:
            write_outcome("error", "transient", f"{what}: {TRUNK} moved before the landing; again")
            return 0, True
        if state == BLOCKED:
            # the essentials first: the ledger clips a summary
            write_outcome(
                "error",
                "blocking",
                f"landing of {track} {track_sha[:12]} blocked, kept at {kept_ref}, nothing "
                f"reset: {why}; repair by hand: clear a stale refs/heads/{TRUNK}.lock, git "
                f"switch {TRUNK}, git merge --ff-only {kept_ref}",
            )
            return 1, False
        if why:
            write_outcome("error", "transient", f"{what}: trial green; not landed: {why}")
            return 0, False
        write_outcome("ok", None, f"{what}: merged as {landed[:12]}; {result}")
    except (OSError, subprocess.SubprocessError, ValueError) as error:  # cycle 1 F5
        write_outcome("error", "transient", f"{what}: failed: {type(error).__name__}: {error}")
        return 1, False
    finally:
        run_git(["update-ref", "-d", TRIAL_REF], main, check=False)
    # a `git merge` fires no post-commit hook, so the run pushes it itself (cycle 1 F3)
    from kgme import sync_io

    sync_io.run_sync(main, settings)
    return 0, False
