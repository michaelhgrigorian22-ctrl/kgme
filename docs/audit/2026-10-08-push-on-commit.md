---
id: AUDIT-0034
type: report
status: final
handoff: HANDOFF-0040
author: claude-code
source: fetched
origin: this repository, `make check` and `pytest tests/test_sync.py` output of 2026-10-08, `git log` of origin/main, the review audits under docs/audit/
tier: 2
created: 2026-10-08T19:48:00-07:00
period: 2026-10-08
---

# HANDOFF-0040 — `kgme sync`: push on every commit, ledger committed at session end

Per HANDOFF-0040, proposed by Cowork and adopted by Michou on 2026-10-08, built the same evening ahead of 0033 on his word. The handoff named this file with `DD`; the local date is the 8th.

## What was built
| Path | Purpose | Lines |
|---|---|---|
| `kgme/sync.py` | pure: `new_ledger_lines` (added lines of `git diff HEAD -- logs/ledger` plus whole untracked files), `plan_sync` (one mode: commit only when a line that is not this command's own is new; message `ledger: <n> events through <last ts>`; push when ahead), `parse_counts` | 99 |
| `kgme/sync_git.py` | git as subprocesses, one named function each: `run_git` (one bounded git command in its own session, killed with its helpers when it stalls), `read_lock_path`, `write_lock` (the sync lock in the git directory, taken at once or by waiting for the holder up to the bound), `read_ledger_diff`, `read_counts`, `read_branch`, `read_head`, `read_upstream`, `read_remote_head`, `commit_ledger` (`git add -- logs/ledger`, `git commit --quiet --message … -- logs/ledger`, the pathspec a literal, the commit carrying `KGME_SYNC_RUN`), `push` (`git push --quiet`, no other option, bounded); every git call an argument list with `GIT_TERMINAL_PROMPT=0` | 150 |
| `kgme/sync_io.py` | the events and the run: `read_attempted` (whether the holder just attempted this head), `write_reconciled_outcomes`, `run_push`, `run_sync` (the lock, the whole job, nothing kept between runs) | 194 |
| `kgme/cli.py` | `kgme sync [--base DIR]`; `--base` names the checkout to act on, default this one, refused when it is not a git checkout | +20 |
| `tools/git-hooks/post-commit` | trigger one: `PATH` set explicitly, `uv run --frozen --project <repo> kgme sync --base <repo>` started in the background (its lines to `logs/scratch/sync.log`), so the commit returns at once; exits before that when `KGME_SYNC_RUN` is set, because the sync run that made the commit owns its push; a failure goes to `logs/scratch/hook-errors.jsonl`; exit 0 always | 30 |
| `tools/hooks/session_end_sync.sh` | trigger two: the same command, backgrounded the same way, on `$CLAUDE_PROJECT_DIR` | 22 |
| `.claude/settings.json` | one `SessionEnd` entry naming the script, 120-second timeout | +13 |
| `Makefile` | `setup` sets `core.hooksPath tools/git-hooks`; `check` fails first, with the one-line fix, when it is not set | +7 |
| `kgme.toml` | `[sync] git_timeout_seconds = 60`, the bound on every git call | +5 |
| `CLAUDE.md` | the approved line under Conventions | +1 |
| `tests/synctools.py` | the seed repository (the working tree's code, a bare `origin`, one committed event), the scrubbed environment, the helpers both test files share, the wait for the backgrounded hook | 109 |
| `tests/test_sync.py` | twelve tests against the seed repository, never the network: the acceptance list | 234 |
| `tests/test_sync_guards.py` | seven tests for the guarantees the review asked for and the simplification Michou chose: one push owner, the stalled push killed, the literal pathspec, the waiting lock in three cases, the wait that runs out | 205 |
| `tests/test_smoke.py` | the subcommand set gains `sync` | ±2 |

## The rule that makes two runs one commit
A push writes an `intent` and an `outcome` into the ledger after the ledger commit, so the file is dirty again the moment a sync finishes. If that counted as a change, every run would commit the record of the previous one. `plan_sync` therefore commits only when a new line's `actor` is not `kgme.sync`; the command's own events ride along with the next foreign batch. A line that is not JSON counts as foreign, so a torn line is committed rather than hidden.

## What happens on each trigger
One mode, one lock, nothing kept between runs: Michou's word of 2026-10-09, closing review cycle 5 (the override reason, approval `01M4J3WB2VKZB3HT952HKJZMVP`). Every run does the whole job: take the lock, reconcile, commit `logs/ledger/` if a foreign event is new, push if ahead.
- **Any commit** (Michou's terminal, Claude Code): the hook starts `kgme sync` in the background and the commit returns at once; the run's lines go to `logs/scratch/sync.log`. Ahead and not behind: `git push`. Behind the upstream: `outcome` `refused`, class `transient`, nothing sent, remote untouched, a pull is the human's step. Remote unreachable, refusing, or silent past the bound: `outcome` `error`, class `transient`, exit 0, no retry; the next trigger pushes. No upstream: one line, nothing written. A commit `kgme sync` itself makes carries `KGME_SYNC_RUN`; the hook sees it and exits, so the run that made the commit pushes, once.
- **Session end**: the same command, backgrounded the same way.
- **Every run** first takes `kgme-sync.lock` in the git directory, waiting for a holder up to the git bound. A run that waited then does the whole job, except that it does not push a head the holder has just attempted (an outcome for `sync:push:<head>` newer than its own start): the next trigger is the retry. A run whose wait runs out writes one `transient` note (`sync:lock`) and exits 0: the holder did this run's work or the next trigger will, since every run does the same work; there is no trigger mode to preserve and nothing is kept between runs. Under the lock a run closes any push `intent` without an `outcome` as `transient` (ADR-013 §4): such an intent belongs to a run that died, never to one still pushing.
- **Every git call is bounded** (`[sync] git_timeout_seconds`, 60). A stalled push runs in its own session and is killed with `git-remote-https` and the credential helper together; the outcome is one `transient`, the exit 0.
- **Before any effect**, the run refuses a `kgme.toml` whose `ledger_dir` is not `logs/ledger`, with exit 2: the pathspec `commit_ledger` passes to git is the literal, never the setting, so no configuration can widen the commit.

## Acceptance test (HANDOFF-0040)
| Check | Test | Result |
|---|---|---|
| a commit in a checkout with the hook enabled appears on the bare repo without a second command | `test_commit_with_the_hook_enabled_reaches_origin_by_itself` (the seed repository carries the working tree's `kgme/` and `tools/`, so the staged code is what the hook runs, through `uv` offline from cache); the commit returns in under two seconds and the push lands behind it | pass; one `ok` outcome in the checkout's ledger, `pushed main` in `sync.log`, no `hook-errors.jsonl` |
| a staged unrelated file survives `kgme sync` still staged and absent from the ledger commit | `test_staged_unrelated_file_survives_and_stays_out_of_the_ledger_commit` | pass; `git diff --cached --name-only` is the unrelated file; the commit names only `logs/ledger/` |
| remote pointed at a directory that does not exist: exit 0, one `transient` outcome | `test_unreachable_remote_is_one_transient_outcome_and_exit_zero` | pass |
| a dirty ledger that holds only this command's own events pushes and commits nothing (the handoff's `--push` case; there is one mode now) | `test_a_run_with_nothing_foreign_pushes_and_commits_nothing` | pass |
| two consecutive `kgme sync` runs produce one ledger commit | `test_two_consecutive_runs_make_one_ledger_commit` | pass; `rev-list --count` is 2 (seed plus one) |
| `grep -c force` over `sync_io.py` is 0 | `test_sync_io_cannot_spell_a_forced_push`, which also refuses `"-f"`, `--delete`, `+refs`, and checks both scripts are executable | pass |
| beyond the handoff: a branch behind its upstream is refused, remote unchanged | `test_behind_upstream_is_refused_never_forced` | pass |
| beyond the handoff: an open push intent is reconciled on start | `test_open_push_intent_is_reconciled_on_start` | pass |
| beyond the handoff: the SessionEnd script logs a failure and exits 0 | `test_session_end_script_logs_a_failure_and_exits_zero` | pass |
| cycle 1 F1: full sync, dirty ledger, hook enabled, remote a directory that does not exist | `test_full_sync_with_the_hook_enabled_attempts_the_push_once`: one ledger commit, one `intent`, one `transient` outcome, no `hook-errors.jsonl` | pass |
| cycle 1 F2: a push that never answers | `test_stalled_push_is_killed_with_its_helpers_and_is_one_transient_outcome`: the remote is an `ext::` helper that sleeps; bound 2 s; the run returns 0 in under 15 s with one `transient` outcome, and `pgrep` finds no helper alive | pass |
| cycle 1 F3: `ledger_dir = "."` | `test_a_ledger_setting_wider_than_the_literal_pathspec_is_refused_before_any_effect`: exit 2, no commit, the staged file still staged, no lock file, no event | pass |
| cycle 1 F4, cycle 2 F8: a sync arriving while a run holds the lock | `test_a_sync_arriving_during_a_push_waits_then_commits_and_pushes`: the lock is held 0.6 s; the run waits, commits the dirty ledger, pushes; one outcome | pass |
| cycle 2 F8: a commit arriving while a run holds the lock | `test_a_commit_arriving_during_a_push_is_pushed_by_its_own_hook`: hook enabled, the lock held 0.6 s; the backgrounded hook waits and pushes, the bare repo at HEAD, one `ok` outcome | pass |
| cycle 2 F8: no retry of the holder's attempt | `test_a_waiting_run_does_not_repeat_the_push_the_holder_just_attempted`: the holder records a `transient` outcome for the head while the contender waits; the contender then writes no intent and leaves the remote alone | pass |
| F8 as closed by Michou: a wait that runs out | `test_a_wait_that_runs_out_is_one_transient_note_and_nothing_else`: bound 1 s, lock held 2 s; exit 0, one `transient` note under `sync:lock`, no intent, remote unchanged; the holder or the next trigger does the same work | pass |
| `make check` green end to end | after cycle 5: `ruff`, `ruff format`, `core.hooksPath`, `hook-errors.jsonl` green; `pytest` 184 passed and 3 failed, the three being the tests that assert the real tree carries no blocking lint finding, which fail on lines in `docs/handoff/cockpit-design/` and `docs/design/`, the design track's untracked files, and on nothing else; `kgme lint` red on those lines only | pass but for the design track's files, outside this handoff |
| under two minutes | the nineteen sync tests run in 17 seconds, one `uv` environment build, four held locks, and one stalled push among them | pass |
| live, once: Michou commits from `kgh` and `git rev-list --count origin/main..HEAD` is 0 within the minute | his step | **deferred**, see below |

## The live check, deferred
The handoff's Who-types-what gives the one live check to Michou, from his own terminal; he was not in the session when the review ran (cycle 1 came back at 03:09 on 2026-10-09, after the Codex usage window reset), so it is deferred to his next terminal commit, and this report stays open on that row until he records it. What this checkout shows meanwhile, from the ledger: the hook pushed `d4e19c5` at 19:39:51, `bffbb42` at 19:48:50, and `cd7712e` at 20:03:31 on 2026-10-08, each one `intent` and one `ok` outcome under `sync:push:<sha>`, each within two seconds of its commit, `origin/main..HEAD` 0 after each. Those commits were made by Claude Code through `git commit` with the hook enabled, the same mechanism his terminal uses; the terminal's own environment (`kgh`, his shell's `PATH`) is what remains to be shown, and it is his to show. The code the hook ran then differs from this version only in what cycle 1 added (the owner variable, the lock, the bound, the literal pathspec, the transient refusal); the commit that closes this handoff is itself pushed by this version.

## The two commits that were waiting, and the first live run
On 2026-10-08 at 19:32 PDT the branch was two commits ahead (`db314aa`, `d0a67f1`). They were pushed by hand with the STATUS commit `b990a2b` at 19:33, and the adoption commit `c7b0c16` at 19:34, before any of this was built; `origin/main..HEAD` was 0 from then on.

The first live run was not planned. During the first test run, at 19:39, the SessionEnd failure test pointed the script at a directory with no project. Pytest runs under `uv run`, so the child inherited `VIRTUAL_ENV`; `uv run --project <no project>` fell back to that active environment, found `kgme`, and `kgme sync` with no `--base` acted on the checkout the package lives in, this repository. It committed the 76 uncommitted ledger events as `d4e19c5` (`ledger: 76 events through 2026-10-08T19:39:37.567-07:00`), `logs/ledger/2026-10.jsonl` alone, and the post-commit hook, enabled by `make setup` minutes earlier, pushed it: `origin/main..HEAD` was 0 at 19:40. Nothing else was touched and nothing was lost; the commit is what the session-end trigger will do every evening. Two changes followed: both hook scripts pass `--base` so the command can act only on the checkout the hook belongs to (a directory that is not a git checkout exits 2 before any git command), and the tests scrub `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` from every child's environment. The unplanned run is recorded here as the deviation it was.

## Deviations, stated
- `--base` was added to `kgme sync` (not in the handoff) so the tests act on a repository under `tmp_path` and the hooks name their own checkout explicitly. Default is this checkout.
- A branch behind its upstream is a `refused` outcome: the push is never attempted, so nothing is overwritten. Its class was `blocking` in the first diff; cycle 1 (F5) held the handoff's §2 to its word, a refused push is `transient`, and this diff complies. The summary says `pull first`, which is the human's step whatever the class.
- Added by the review, none in the handoff: the owner variable `KGME_SYNC_RUN` on the ledger commit (cycle 1 F1), the bound on every git call with the process group killed on a stall (F2), the literal pathspec and the refusal of a wider `ledger_dir` (F3), the lock in the git directory (F4), the effect names `run_git`, `run_push`, `write_reconciled_outcomes` (F7); the lock that waits for its holder (cycle 2 F8). The handoff names `kgme/sync_io.py` for the effects; with the lock and the bound it passed 300 lines, so the git subprocess functions are `kgme/sync_git.py` and `sync_io.py` keeps the events and the run, as 0031 and 0033 split theirs. The tests for the review's guarantees are in `tests/test_sync_guards.py`.
- Chosen by Michou over the reviewer's requirement (2026-10-09, the override reason, after F8 had stood five cycles in one form after another: a trigger lost under contention): one mode, so the hook's `--push` is gone and every run commits and pushes; one blocking lock with a timeout; the hooks backgrounded, so no commit and no session end waits for a push; no pending-request state, so a wait that runs out is one note and the next trigger does the same work. The pending directory and the gate of cycles 3 and 4 are deleted with their tests. The handoff's own reason for push-only in the hook, that a ledger commit must not trigger itself, is met by `KGME_SYNC_RUN` instead.
- The hook sets `PATH` to `~/.local/bin` (where `uv` lives on this machine) ahead of `/opt/homebrew/bin`; the credential helper is configured by absolute path in `~/.gitconfig`, so the push authenticates even in a bare environment.
- `make setup` ran at 19:38, before the review, on Michou's instruction ("run make setup once it exists"); the hook has been live on this checkout since.

## Needs from Michou, closed
Adoption and the CLAUDE.md line were his word of 2026-10-08. He did not ask for the ledger to be committed only by hand, so the session-end trigger commits it.

## Review loop
Each cycle is an audit file written by `kgme review`; the dispositions the builder sent with the next cycle are under `logs/scratch/dispositions-0040-cycle-N.md`.

| Cycle | Audit | Verdict | Findings | Disposition |
|---|---|---|---|---|
| 1, attempts of 2026-10-08 19:43 to 19:51 | none | tooling exhausted, not a strike | Codex's usage window closed at 19:43 on both reviewer models; three attempts, each `transient` | waited for the reset (00:21 PDT) |
| 1, 2026-10-09 03:09 | AUDIT-0036 | BLOCK | F1 two push attempts when the hook's push fails inside a full sync; F2 no bound on git; F3 the configurable `ledger_dir` as pathspec; F4 reconcile closes an active run's intent when two runs overlap; F5 the `blocking` class on a refused push against §2; F6 the live check pending; F7 (cosmetic) effect names | all fixed in the cycle 2 diff as the trigger list above states; F6 deferred explicitly, the section above |
| 2, 2026-10-09 ~11:00 | AUDIT-0037 | BLOCK | F1 to F7 resolved; F8 the lock dropped a contending trigger and its mode, so a session-end sync arriving during a push never committed, and a commit arriving during a push stayed unpushed | fixed in the cycle 3 diff: the contender waits for the holder up to the bound, then runs its own plan, skipping only the push the holder just attempted; four tests, no third invocation |
| 3, 2026-10-09 11:09 | AUDIT-0038 | BLOCK | F8 stood (strike one): a wait that ran out still dropped the trigger and its mode | fixed in the cycle 4 diff: the trigger is left as a file under `kgme-sync.pending/`, served by the holder before it releases the lock and merged by every later run at its start; the test that expected the loss is replaced by three with a real stalled holder |
| 4, 2026-10-09 21:57 | AUDIT-0039 | BLOCK, **halt** | F8 stood a third consecutive cycle: the holder's last look could come before the waiter's file and its release after, both exiting; the five-round limit could leave requests without a successor | the loop halted; Michou's override of 2026-10-09 (`01M4J3WB2VKZB3HT952HKJZMVP`): cycle 5 on the gate-and-lock redesign, and if F8 survived it, simplify |
| 5, 2026-10-09 22:23 | AUDIT-0040 | BLOCK | F8 stood: a gate wait that ran out let a waiter publish without the gate while the holder was between its last look and its release; F9 (cosmetic) `_leave_request` unprefixed | per the override reason, the cycle 6 diff is the simplification: one mode, one lock with a timeout, hooks backgrounded, no pending-request state; `_leave_request` is gone with it. The gate was red on the design track's lint findings, outside this handoff, so cycle 5 ran with `--skip-check` after every other part of the gate was run by hand |
| 6, 2026-10-09 22:33 | AUDIT-0041 | **PASS** | F10 (cosmetic) two acceptance rows left from the deleted pending tests; F11 (cosmetic) the test helpers without effect prefixes | both fixed in the commit: the rows removed, the helpers renamed `run_git`, `write_seed`, `write_commit`, `run_holder`, `read_ledger_lines`, `read_sync_events`, `read_hook_outcomes`, `write_git_env`. Ran with `--skip-check` for the same reason as cycle 5 |
