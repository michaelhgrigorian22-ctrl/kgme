"""`kgme sync`, git as subprocesses: one bounded command runner, the reads, the lock, the
commit, the push.

Purpose: every git effect of HANDOFF-0040 in one place, one named function each (ADR-015),
so `kgme/sync_io.py` holds only the events and the run. Nothing here can build a push that
overwrites the remote: `push` runs `git push` with no option but `--quiet`, and
`commit_ledger` passes the literal pathspec `logs/ledger`, never a setting.
Inputs: the checkout to act on (`repo`), argument lists, a bound in seconds.
Outputs: `CompletedProcess` results, strings, counts, a lock descriptor.
Side effects: `run_git` runs one git command in its own session and kills it with every
helper it started when it stalls; `read_*` run read-only git commands;
`write_lock` takes `kgme-sync.lock` inside the git directory; `commit_ledger` runs `git add`
and `git commit` on `logs/ledger` only, the commit carrying `KGME_SYNC_RUN` so the
post-commit hook exits; `push` runs `git push`. Git never prompts: `GIT_TERMINAL_PROMPT=0`
on every call.
"""

import fcntl
import os
import signal
import subprocess
import time
from pathlib import Path

from kgme import sync

LEDGER_REL = "logs/ledger"
OWNER_VARIABLE = "KGME_SYNC_RUN"
LOCK_NAME = "kgme-sync.lock"
GIT_TIMEOUT = 60
POLL_SECONDS = 0.2


def run_git(
    args: list[str],
    repo: Path,
    check: bool = True,
    timeout: int = GIT_TIMEOUT,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """One git command in `repo`, an argument list, prompts disabled, bounded by `timeout`
    seconds. The command runs in its own session so that when it stalls it and every helper
    it started (`git-remote-https`, a credential helper) are killed together, after which
    `TimeoutExpired` is raised."""
    process = subprocess.Popen(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", **(extra_env or {})},
        start_new_session=True,
    )
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        raise
    done = subprocess.CompletedProcess(process.args, process.returncode, out, err)
    if check and done.returncode != 0:
        raise subprocess.CalledProcessError(done.returncode, done.args, out, err)
    return done


def read_lock_path(repo: Path) -> Path:
    """`kgme-sync.lock` inside the git directory, which no `kgme clean` target reaches."""
    return repo / run_git(["rev-parse", "--git-path", LOCK_NAME], repo).stdout.strip()


def write_lock(lock_path: Path, wait_seconds: float) -> tuple[int | None, bool]:
    """Take the sync lock: at once, or by asking again every `POLL_SECONDS` for up to
    `wait_seconds` while another run holds it. Returns the descriptor (None when the wait ran
    out) and whether it had to wait. The kernel releases a lock when its holder exits,
    however it exits."""
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + wait_seconds
    waited = False
    while True:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return descriptor, waited
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(descriptor)
                return None, True
            waited = True
            time.sleep(POLL_SECONDS)


def read_ledger_diff(repo: Path) -> tuple[str, list[str]]:
    """What `logs/ledger/` holds that HEAD does not: the diff against HEAD, staged or not, and
    the text of every untracked file under it."""
    diff = run_git(["diff", "HEAD", "--no-color", "--unified=0", "--", LEDGER_REL], repo).stdout
    listed = run_git(["ls-files", "--others", "--exclude-standard", "--", LEDGER_REL], repo)
    texts = [(repo / name).read_text(encoding="utf-8") for name in listed.stdout.split()]
    return diff, texts


def read_counts(repo: Path) -> tuple[int, int] | None:
    """`(behind, ahead)` against the upstream, or None when the branch has no upstream."""
    done = run_git(["rev-list", "--left-right", "--count", "@{u}...HEAD"], repo, check=False)
    if done.returncode != 0:
        return None
    return sync.parse_counts(done.stdout)


def read_branch(repo: Path) -> str:
    """The current branch name."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()


def read_head(repo: Path) -> str:
    """HEAD's short sha."""
    return run_git(["rev-parse", "--short", "HEAD"], repo).stdout.strip()


def read_upstream(repo: Path) -> str:
    """The upstream's name (`origin/main`), or an empty string without one."""
    done = run_git(["rev-parse", "--abbrev-ref", "@{u}"], repo, check=False)
    return done.stdout.strip() if done.returncode == 0 else ""


def read_remote_head(repo: Path) -> str:
    """The upstream's short sha as this checkout last saw it, or an empty string."""
    done = run_git(["rev-parse", "--short", "@{u}"], repo, check=False)
    return done.stdout.strip() if done.returncode == 0 else ""


def commit_ledger(repo: Path, message: str, run_id: str) -> str:
    """Stage and commit the literal pathspec `logs/ledger` alone, so whatever else is staged
    stays staged and out of this commit. The commit carries `KGME_SYNC_RUN=<run_id>`, which
    the post-commit hook reads and exits on: this run pushes, not the hook. Returns the new
    HEAD's short sha."""
    owner = {OWNER_VARIABLE: run_id}
    run_git(["add", "--", LEDGER_REL], repo, extra_env=owner)
    run_git(["commit", "--quiet", "--message", message, "--", LEDGER_REL], repo, extra_env=owner)
    return read_head(repo)


def push(repo: Path, timeout: int) -> tuple[int, str]:
    """`git push` to the configured upstream, nothing else, bounded by `timeout` seconds.
    Returns the exit code and stderr; a stalled push is killed and reported as such."""
    try:
        done = run_git(["push", "--quiet"], repo, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -signal.SIGKILL, f"no answer from the remote in {timeout} s; killed"
    return done.returncode, done.stderr
