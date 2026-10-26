---
id: AUDIT-0137
type: report
status: final
handoff: HANDOFF-0060
author: claude-code
source: inferred
sources: ["HANDOFF-0060", "tests/clocktools.py", "kgme/canary_run.py", "kgme/coherence.py", "kgme/vault.py", "kgme/cli_parser.py", "kgme/session_read.py", "kgme/merge_rules.py"]
tier: 2
created: 2026-10-26T02:42:16-07:00
period: 2026-10-26
---

# HANDOFF-0060: the weekly review's code items

Four items. The fixes are one commit, and each split is a commit of its own, made of moves only.

## 1. Midnight
- **The cause.** `tests/test_daily.py`, `tests/test_capture_replace.py` and `tests/test_capture_review.py` took `TODAY` from the wall clock at import. The code then took its own "now" later, and the ledger stamped events at the real time, so a run across midnight compared two different days.
- **`tests/clocktools.py` (new).** `freeze` pins every place `kgme` reads the wall clock to one instant: the event timestamp (`events`), the ULID time (`ulid`), `kgme capture`'s and `kgme daily`'s `now`, and the brief's clock. `FROZEN` is 2026-10-22 23:59:59 in the vault's zone. `git_dates` dates a test's commits from the same instant.
- **The three files.** Each takes `TODAY = FROZEN.date()` and freezes the clock for every test, through an autouse fixture. `test_daily`'s git test dates its commits from the frozen instant.
- **No production change.** `kgme capture` and `kgme daily` already take `now` with the wall clock as the default, and the frozen clock covers the rest.
- **Acceptance** (`logs/scratch/handoff-0060/red/`): a pytest plugin freezes the code's clock at 23:59:59 on another day than the files' import-time "today", which is the midnight case.
  - The files as committed fail 10 (`red-midnight.txt`). They are the same 10 that failed at midnight on 2026-10-26.
  - The new files pass 34 (`green-midnight.txt`), and the new files never read the wall clock at all.

## 2. The loop-mode canary cell
- **The cause.** A run whose turns ran out (`error_max_turns`) after its aimed call was recorded as transient before anything was classified.
- **`kgme/canary_run.py`.** Such a run is now measured, but only when the measurement decides: a refusal at a named layer, or the effect. Anything else stays transient, as before, with the reason "ran out of turns before a refusal or an effect was seen". `read_hook_refusals` reads the tool-call ids the guard refused in the worker's session from the test ledger: each refused outcome keys its call by the vendor's `tool_use_id`.
- **The cell.** Both `loop-write` probes in `tests/policy/test_agents_guard.py` now take the guard's refusal from the ledger. `claude_max_turns` stays 2.
- **Fast tier** (`tests/policy/test_canary.py`):
  - a silent run out of turns after a refused call passes, "refused by hook … then error_max_turns";
  - one that reached the effect fails;
  - one with no refusal stays transient.

  The earlier case of a transient terminal error now uses `error_during_execution`, since `error_max_turns` is no longer always transient.
- **Live:** the cell alone, with `claude_max_turns = 2` (`logs/scratch/handoff-0060/canary-loop.txt`), passes both probes. The outside probe now reads "refused by hook/settings", the hook taken from the ledger. In this run both streams ended `success` after 2 turns, so the out-of-turns path was not exercised live. The fast tier covers it. The whole matrix was not run, to keep the cost down.

## 3. Under the line, by moves alone
Every split was made by `logs/scratch/handoff-0060/split.py`, which moves top-level blocks byte for byte. It was then checked by `verify_moves.py`: every block of the file at HEAD appears exactly once in the new files, identical, and nothing is added but imports and docstrings. The checks also confirmed that no top-level comment was lost and that the same test ids are collected before and after.

| module at HEAD | lines | now | new beside it |
|---|---|---|---|
| `kgme/cli.py` | 443 | 308 | `kgme/cli_parser.py` (148): `CLASSES`, `build_parser` |
| `kgme/session.py` | 429 | 284 | `kgme/session_read.py` (193): the launch's reads |
| `kgme/merge.py` | 461 | **380** | `kgme/merge_rules.py` (145): constants, lanes, quiet point, events, lock path |
| `tests/test_lint.py` | 356 | 193 | `linttools.py`, `test_lint_tracks.py`, `test_lint_scope.py` |
| `tests/test_brief_review.py` | 406 | 215 | `briefreviewtools.py`, `test_brief_review_inputs.py`, `test_brief_review_gate.py` |
| `tests/test_cheap.py` | 499 | 157 | `cheaptools.py`, `test_cheap_live.py`, `test_cheap_review.py` |

- **Names callers know are re-exported**, with `noqa: F401`, where the tests or other modules reach them through the old module: `session.SKILL`, `session.uv_env`, `merge.DEFAULT_LANES`, `cli.build_parser` and the rest.
- **`kgme/merge.py` stays at 380 lines, over the line.** The tests patch `run_git`, `run_trial`, `read_sha`, `read_checkout` and `read_landed_state` on `kgme.merge`. Every function left in `merge.py` calls one of them, or calls `run_attempt`, `read_heads` and `write_reconciled`, which do. Moving a caller would make it see the unpatched name, which changes what a test exercises. That is a behaviour change, and §3 says such a split is not made. `run_merge` also stays, because moving it would need a circular import.
- **`session.py`'s docstring** gains the cheap route (AUDIT-0108) and the mods.
- **Two re-exports needed restoring by hand,** `SKILL`, `read_committed_claude_md` and `DEFAULT_LANES`, because `ruff --fix` drops an import nothing in the module uses. One function body changed in transit: `ruff` removed `run_guard_in`'s local `import sys`, shadowed by the copied module-level import. The module-level import was removed instead, and the verifier then reported zero changes.

## 4. The `completed:` coherence check
- **What it compares.** `kgme lint` compares a done handoff's `completed:` with the `created` of its latest PASS review audit (`coherence.check_completed`, `vault.read_passes`). A difference is one `advisory` line, whatever `[coherence] blocking_from` makes the other checks.
- **The PASS review, not the report, against the letter of §4.** §4 writes "its report's `created`", citing STATUS's housekeeping of 2026-10-21. STATUS line 65 records the rule as "`completed:` on a done handoff is its PASS audit's `created`", which is Michou's rule of 2026-10-21 and every close since. Against the report's `created`, 38 done handoffs differ, by up to a week, because the report is written before the reviews. Against the PASS review, 11 differ, and the check takes STATUS's rule.
- **The 11 today**, each one advisory line:
  - **kgme-brief-v1 (17 s), kgme-clean (11 s), validator (57 s), push-on-commit (70 s):** HANDOFF-0034, 0033, 0031 and 0040. They were closed in their own build commits between 2026-09-20 and 2026-10-15, a matter of seconds after their PASS. They are not the four STATUS names as set by hand on 2026-10-21: 0045, 0050, 0051 and 0054 match their PASS audits (AUDIT-0068, 0065, 0074, 0071) to the second. §4's parenthesis fits neither reading literally; under the report reading those four differ by 456 s to 4.4 days. (Corrected on the arbiter's ruling.)
  - **canary-tests, hook-pair, one-home, session-levels, cheap-lane, design-lands-continuously:** each has a PASS later than its `completed`, a review after close (an amendment or a follow-up).
  - **review-wrapper:** closed a day after its PASS.
  - These are history, not errors.
- **Tests.** `tests/test_coherence_completed.py`:
  - ten seconds off is one advisory line, even with the class set to blocking;
  - equal is no line, and the latest PASS of several is the one;
  - no PASS review, or an open handoff, is not this check's.

  The two whole-tree tests in `tests/test_coherence.py` now exclude this advisory rule from their "no finding" assertion and assert that it is advisory.

- **Skipped: 20 done handoffs have no PASS review audit,** because they predate the review loop or were closed without one: HANDOFF-0001 to 0005, 0013, 0014, 0015, 0017 to 0023, 0025, 0026, 0027, 0030 and 0041. The check finds nothing about them, by design.

## Review cycle 1 (AUDIT-0138, BLOCK on F1)
- **F1, disputed and sent to the arbiter. Ruling (recorded): advisory, on conditions this report now meets.**
  - The check compares `completed:` with the PASS review audit's `created`, per STATUS line 65, which §4 cites as its source. A PASS review audit is itself a report (`type: report`).
  - Read literally, the check flags 39 of the 41 done handoffs, including every one closed correctly under Michou's rule, and measures nothing.
  - The claim about the four hand-set handoffs is corrected above.
  - The 20 skipped handoffs are named above.
  - The reading stays on the approval screen.
- **F2 (advisory):** `kgme/merge_rules.py`'s docstring called everything but `read_refused` pure. `read_merge_lock` asks git where the lock lives, and the docstring now says so. The module still holds the two small readers beside the pure rules, kept whole for the move.
- **F3 (advisory):** `make check` at every split step. The commits are made splits first, one per module, then the fixes. Each split state was checked in a fresh clone, cumulatively in commit order (`logs/scratch/handoff-0060/steps.py`, `steps.txt`).

## Review cycle 2 (AUDIT-0139, BLOCK on F4), fixed
- **F4:** `read_passes` chose the latest PASS by comparing timestamps as text. On 2026-11-01, 01:00:05-08:00 is ten seconds after 01:59:55-07:00 but sorts first. The PASS audits are now compared as parsed, offset-aware instants, and a `created` that will not parse, or carries no offset, is left out. The regression is the reviewer's own case: red on the cycle-2 module (`logs/scratch/handoff-0060/red-c2.txt`), green after.
- **F1, F2 and F3** stay advisory as recorded.

## Review cycle 3 (AUDIT-0140): PASS
F1, F2 and F3 are advisory, as recorded.

## The commits
The six splits come first, one per module, each holding only its old and new files, in the order the clone checked them:
- `b5971e7` cli;
- `a89d028` session;
- `7480e96` merge;
- `e9903c5` test_lint;
- `ad5ca4b` test_brief_review;
- `b3e6820` test_cheap.

Then come the fixes, with this report and the close. Each split commit's `git show -M --stat` is in `logs/scratch/handoff-0060/split-commits.txt`.

`git diff -M` shows these as insertions and deletions, not renames, because git's rename detection matches whole files and one file split into several is not a rename. What proves them moves is `verify_moves.py`, which shows every block byte-identical, together with `make check` at every step.

## Acceptance
- `make check`: lint 0 blocking, 680 passed with every change in the tree.
- The midnight run, the canary cell, the splits, and the advisory line, each as above.

## Waiting for Michou
- **`logs/scratch/handoff-0060/readers.diff`:** `docs/readers/merging.md` and `docs/readers/sessions.md` add the new modules to `sources:`.
- **`sessions.md` collides with HANDOFF-0059's `human-paths.diff`,** which changes the same line. Apply 0059's first, then `sessions-after-0059.diff` instead of that hunk.
- **STATUS's weekly-review items** (lines 61 and 69) are Cowork's to strike.

## For the approval screen
- **`completed:` against the PASS review rather than the report,** the letter of §4. Stakes 2, edge 0.3, score 0.6.
- **`kgme/merge.py` at 380 lines.** Under ~300 would need the tests to patch `kgme.merge_<x>`, which changes those tests. Stakes 1, edge 0.3, score 0.3.
