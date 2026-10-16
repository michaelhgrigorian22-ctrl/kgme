---
id: HANDOFF-0040
type: handoff
created: 2026-10-08T19:30:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-09T22:34:30-07:00
report: docs/audit/2026-10-08-push-on-commit.md
depends_on: [HANDOFF-0025, HANDOFF-0026]
plan_ref: PLAN-PHASE-1 step 7b
---

# Handoff 0040 (proposed) — `kgme sync`: push on every commit, ledger committed at session end

## Why
The private remote exists so the repository's history is off the machine (Gate 1, AUDIT-0009). It is only that if commits reach it. Between 2026-09-23 and 2026-10-04 the local branch sat one, then two commits ahead of `origin/main`; on 2026-10-08 it is two ahead again. CLAUDE.md says "commit at the end of each handoff" and says nothing about pushing, so pushing has been a discipline nobody owned. Michou's words, 2026-10-08: the repo "needs to be updated automatically whenever something pushes; it's currently not accomplishing its purpose."

The ledger has the same gap one level down. ADR-012 makes `logs/ledger/` tracked, but it is only ever committed when a handoff closes, so between handoffs days of events exist on disk and in Backblaze and nowhere in git. `logs/ledger/2026-10.jsonl` is modified right now and belongs to no commit.

Both are fixed by one command with two triggers. Nothing here is scheduling (nothing fires on a clock); each trigger is an action someone already took.

## What
1. `kgme/sync.py` (pure): `plan_sync(status, mode) -> SyncPlan` from a parsed `git status --porcelain` and `git rev-list --left-right --count @{u}...HEAD`: whether `logs/ledger/` has changes to commit, whether there are commits to push, the commit message (`ledger: <n> events through <last ts>`), and nothing else. `kgme/sync_io.py` (effects, one named function each): `read_status`, `commit_ledger` (always the pathspec form, `git add logs/ledger && git commit -m <msg> -- logs/ledger`, so a handoff's staged work is never swept in), `push` (`git push`, never `--force`, never `-f`; the deny list already refuses both), `read_remote_head`.
2. `kgme sync` runs both halves: commit the ledger if it changed, then push if ahead. `kgme sync --push` pushes only. One `intent` before the push naming the branch and the commits to send; one `outcome` after, with the remote head's short sha in the summary. Offline or a refused remote is an `outcome` of class `transient`, exit 0, no retry: the next trigger will push. `kgme sync` never blocks the action that invoked it and never prompts.
3. Trigger one, every commit: `tools/git-hooks/post-commit`, a tracked shell file that sets `PATH` explicitly (`/opt/homebrew/bin` first, so `gh`'s credential helper resolves in the hook's bare environment, the lesson of 2026-09-11) and runs `uv run --frozen --project <repo> kgme sync --push`. Push-only inside the hook so a ledger commit cannot trigger itself. Enabled by `git config core.hooksPath tools/git-hooks`, which is local configuration, not tracked: `make setup` sets it and `make check` fails with the one-line fix when it is unset, so a fresh clone cannot silently forget it.
4. Trigger two, every session end: a `SessionEnd` hook in `.claude/settings.json` running `tools/hooks/session_end_sync.sh`, which runs `kgme sync` in full, so a Claude Code session's ledger events are committed and pushed when the session closes. Not `Stop` (every turn would be a commit). Same shape and failure path as the two hooks of 0028: never blocks, errors to `logs/scratch/hook-errors.jsonl`.
5. `CLAUDE.md` conventions, one line (human-authored, shown as a diff): "Every commit is pushed by the post-commit hook; the ledger is committed by `kgme sync`, never by hand."
6. `docs/readers/review-loop.md` is untouched; the review of this handoff runs under it.

## Outputs
`kgme/sync.py`, `kgme/sync_io.py`, `tools/git-hooks/post-commit`, `tools/hooks/session_end_sync.sh`, `Makefile` (`setup` target; `check` asserts `core.hooksPath`), `.claude/settings.json` (one `SessionEnd` entry), `CLAUDE.md` (one line, approved), `tests/test_sync.py`, `kgme sync` wired in `cli.py`.

## Acceptance test (under two minutes)
Against a bare repository in `tmp_path` as `origin`, never the network: a commit in a clone with the hook enabled appears on the bare repo without a second command; a staged unrelated file survives `kgme sync` still staged and absent from the ledger commit; with the remote URL pointed at a directory that does not exist, `kgme sync` exits 0 and the ledger holds one `transient` outcome; `kgme sync --push` with a dirty ledger pushes and commits nothing; two consecutive `kgme sync` runs produce one ledger commit, not two; `grep -c force` over `sync_io.py` is 0. Then, live, once: Michou commits in his own terminal and `git rev-list --count origin/main..HEAD` is 0 within the minute.

## Reviewer
Codex under `kgme review`. Codex checks that no path in `sync_io.py` can push with force or commit outside `logs/ledger/`.

## Reversibility
`git config --unset core.hooksPath`; remove the `SessionEnd` entry; `git revert`. The ledger commits already made stay, as they should.

## Who types what
Claude Code does all of it; `git config` and the hook files need no privilege. Michou types nothing except the live check in the acceptance test, from `kgh`.

## Needs from Michou
Adoption. Approval of the one-line CLAUDE.md diff. A word if he would rather the ledger were committed only at session end and by hand, never by the hook (the hook as proposed only pushes; the ledger commit is session-end and manual).

## Report
`docs/audit/2026-10-DD-push-on-commit.md`: the four tests, the live check with the remote sha, the two commits that were waiting on 2026-10-08 and when they landed. Set `status: done`, `completed:`. Commit `sync: push on commit, ledger committed at session end (HANDOFF-0040)`.
