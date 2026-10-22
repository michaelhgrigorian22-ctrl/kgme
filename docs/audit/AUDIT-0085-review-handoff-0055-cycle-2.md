---
id: AUDIT-0085
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 66aa2e1f13198aec08fb8e6bd6920ec0569263e89defe188a208e15f8556b783"]
tier: 2
created: 2026-10-21T22:35:09-07:00
period: 2026-10-21
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F5, F8, F11]
---

# Review of HANDOFF-0055, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `66aa2e1f13198aec08fb8e6bd6920ec0569263e89defe188a208e15f8556b783`. Verdict **BLOCK**: blocking 3, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:318` | The live merge now uses the tested SHA. The regression test advances `design` with a forbidden change and verifies it stays out. | Implemented. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with rename detection disabled preserve both endpoints and spaces. Both regression cases are covered. | Implemented. |
| F3 | blocking, resolved | `kgme/merge.py:331` | Successful merges now invoke `run_sync`. The bare-remote regression verifies publication without another commit. | Implemented. |
| F4 | blocking, resolved | `kgme/merge.py:245` | Waiting triggers receive the longer lock bound; attempts refresh heads under the lock and retry a moved `main`, up to 3 times. | Implemented, with contention and moved-main tests. |
| F5 | blocking | `kgme/merge.py:241` | Recovery remains incomplete. If the process dies after the merge succeeds but before its outcome is appended, `design` is already contained in `main`. Subsequent runs return here before `write_reconciled`, leaving the intent open indefinitely. The recovery test covers only an unmerged commit. | Reconcile under the lock before the no-work return. Add a restart test with an open intent whose design commit has already landed; verify exactly 1 closing outcome. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup compares the complete parsed name. The regression covers distinct approval names. | Implemented. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Selection now compares parsed instants and event IDs. Tests cover differing offsets and equal timestamps. | Implemented. |
| F8 | blocking | `docs/audit/2026-10-21-design-lands.md:37` | Production-path evidence reports **61 seconds**, exceeding the unchanged **60-second** acceptance bound. No accepted amendment is supplied. The report’s statement that the bound is “met” contradicts its measurement. | Demonstrate compliance or obtain an explicit acceptance amendment. Correct the report’s characterization. |
| F9 | cosmetic | `tests/test_approve.py:21`; `tests/test_approve.py:123`; `tests/test_merge.py:247` | The original renames landed, but helper contracts remain incomplete: `run_git` lacks a docstring, while the new effectful helpers `approval`, `trial_then_advance`, and `trial_while_main_moves` lack effect prefixes. | Add the missing contracts and appropriate `write_*` or `run_*` prefixes. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests now carry explicit class markers. | Implemented. |
| F11 | blocking | `kgme/merge.py:162`; `kgme/merge.py:295` | A check timeout becomes `green=False`, then an immediate `blocking` trial failure. It bypasses the new transient exception handler, contrary to ADR-016. Neither timeout path has a regression test. | Preserve timeout classification as `transient`. Test check and Git timeouts, including exactly 1 intent and 1 outcome. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:318` | The live merge now uses the tested SHA. The regression test advances `design` with a forbidden change and verifies it stays out. | Implemented. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with rename detection disabled preserve both endpoints and spaces. Both regression cases are covered. | Implemented. |
| F3 | blocking, resolved | `kgme/merge.py:331` | Successful merges now invoke `run_sync`. The bare-remote regression verifies publication without another commit. | Implemented. |
| F4 | blocking, resolved | `kgme/merge.py:245` | Waiting triggers receive the longer lock bound; attempts refresh heads under the lock and retry a moved `main`, up to 3 times. | Implemented, with contention and moved-main tests. |
| F5 | blocking | `kgme/merge.py:241` | Recovery remains incomplete. If the process dies after the merge succeeds but before its outcome is appended, `design` is already contained in `main`. Subsequent runs return here before `write_reconciled`, leaving the intent open indefinitely. The recovery test covers only an unmerged commit. | Reconcile under the lock before the no-work return. Add a restart test with an open intent whose design commit has already landed; verify exactly 1 closing outcome. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup compares the complete parsed name. The regression covers distinct approval names. | Implemented. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Selection now compares parsed instants and event IDs. Tests cover differing offsets and equal timestamps. | Implemented. |
| F8 | blocking | `docs/audit/2026-10-21-design-lands.md:37` | Production-path evidence reports **61 seconds**, exceeding the unchanged **60-second** acceptance bound. No accepted amendment is supplied. The report’s statement that the bound is “met” contradicts its measurement. | Demonstrate compliance or obtain an explicit acceptance amendment. Correct the report’s characterization. |
| F9 | cosmetic | `tests/test_approve.py:21`; `tests/test_approve.py:123`; `tests/test_merge.py:247` | The original renames landed, but helper contracts remain incomplete: `run_git` lacks a docstring, while the new effectful helpers `approval`, `trial_then_advance`, and `trial_while_main_moves` lack effect prefixes. | Add the missing contracts and appropriate `write_*` or `run_*` prefixes. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests now carry explicit class markers. | Implemented. |
| F11 | blocking | `kgme/merge.py:162`; `kgme/merge.py:295` | A check timeout becomes `green=False`, then an immediate `blocking` trial failure. It bypasses the new transient exception handler, contrary to ADR-016. Neither timeout path has a regression test. | Preserve timeout classification as `transient`. Test check and Git timeouts, including exactly 1 intent and 1 outcome. |

## Verdict

BLOCK: 3 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`66aa2e1f13198aec`**, matching `review.sha`. No files changed; no tests executed. The supplied gate log reports **448 passed, 34 deselected**.

All 6 acceptance scenarios have tests or stated evidence; F8 remains unsatisfied. Human-terminal approval is covered by a marker-free fixture, with no live human approval claimed. Hook, configuration, deny-rule, and reader drafts remain under `logs/scratch/handoff-0055/`.

Module contracts are present. File lengths are **332** for `merge.py`, **359** for its tests, and **388** for the already oversized CLI. No dependencies, `TODO`, or `shell=True` were introduced.

F5 and F8 remain blocking for a second cycle; the review-loop protocol calls for an arbiter ruling.
