---
id: AUDIT-0037
type: report
status: final
handoff: HANDOFF-0040
author: codex
source: inferred
sources: ["HANDOFF-0040", "staged diff sha256 31fc1564ccabb7b5954536c640471e509c73f56aa52891866ab2d67c186a6f05"]
tier: 2
created: 2026-10-09T10:50:06-07:00
period: 2026-10-09
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8]
---

# Review of HANDOFF-0040, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `31fc1564ccabb7b5954536c640471e509c73f56aa52891866ab2d67c186a6f05`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/sync_io.py:139 | The ledger commit suppresses its nested hook. `tests/test_sync_guards.py:37` covers the enabled hook, dirty ledger, nonexistent remote, and exactly 1 intent/outcome pair. | No further fix is required. |
| F2 | blocking, resolved | kgme/sync_io.py:39 | A stalled push receives bounded execution and process-group termination, followed by 1 transient outcome and exit 0. The regression is at `tests/test_sync_guards.py:55`. | No further fix is required for the reported stalled-push case. |
| F3 | blocking, resolved | kgme/sync_io.py:236 | The configurable path is validated before locking, and both commit commands use the fixed `logs/ledger` pathspec. The broader-path rejection test is at `tests/test_sync_guards.py:83`. | No further fix is required. |
| F4 | blocking, resolved | kgme/sync_io.py:245 | The exclusive lock serializes reconciliation, preventing a competing sync from closing the active owner's intent. The contention test verifies 0 events from the contender. | The original duplicate-outcome defect is closed; F8 addresses a separate consequence of discarding contenders. |
| F5 | blocking, resolved | kgme/sync_io.py:217 | A behind-upstream refusal now records class `transient`. `tests/test_sync.py:136` asserts that classification and an unchanged remote. | No further fix is required. |
| F6 | blocking, resolved | docs/audit/2026-10-08-push-on-commit.md:66 | The report explicitly documents 1 deferred human-terminal check, satisfying cycle 1's permitted deferral disposition. It does not establish live acceptance for this version. | Complete the deferred check with Michou's terminal commit, remote SHA, and ahead count of 0 within 1 minute. |
| F7 | cosmetic, resolved | kgme/sync_io.py:39 | The 3 cited effect functions are now named `run_git`, `run_push`, and `write_reconciled_outcomes`. | No further fix is required. |
| F8 | blocking | kgme/sync_io.py:246 | Lock contention discards the incoming trigger and its mode. If 1 push-only run holds the lock when a full session-end sync arrives, the latter exits before committing its dirty ledger, and the owner never performs that work. A commit arriving after an active push captured its revision can similarly remain unpushed. The contention test conceals the missing handoff by manually invoking sync again at `tests/test_sync_guards.py:118`. | Preserve pending triggers and their required mode, then service them after ownership transfers without retrying the same failed attempt. Test overlapping push/full runs and overlapping commits without requiring a third manual invocation. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/sync_io.py:139 | The ledger commit suppresses its nested hook. `tests/test_sync_guards.py:37` covers the enabled hook, dirty ledger, nonexistent remote, and exactly 1 intent/outcome pair. | No further fix is required. |
| F2 | blocking, resolved | kgme/sync_io.py:39 | A stalled push receives bounded execution and process-group termination, followed by 1 transient outcome and exit 0. The regression is at `tests/test_sync_guards.py:55`. | No further fix is required for the reported stalled-push case. |
| F3 | blocking, resolved | kgme/sync_io.py:236 | The configurable path is validated before locking, and both commit commands use the fixed `logs/ledger` pathspec. The broader-path rejection test is at `tests/test_sync_guards.py:83`. | No further fix is required. |
| F4 | blocking, resolved | kgme/sync_io.py:245 | The exclusive lock serializes reconciliation, preventing a competing sync from closing the active owner's intent. The contention test verifies 0 events from the contender. | The original duplicate-outcome defect is closed; F8 addresses a separate consequence of discarding contenders. |
| F5 | blocking, resolved | kgme/sync_io.py:217 | A behind-upstream refusal now records class `transient`. `tests/test_sync.py:136` asserts that classification and an unchanged remote. | No further fix is required. |
| F6 | blocking, resolved | docs/audit/2026-10-08-push-on-commit.md:66 | The report explicitly documents 1 deferred human-terminal check, satisfying cycle 1's permitted deferral disposition. It does not establish live acceptance for this version. | Complete the deferred check with Michou's terminal commit, remote SHA, and ahead count of 0 within 1 minute. |
| F7 | cosmetic, resolved | kgme/sync_io.py:39 | The 3 cited effect functions are now named `run_git`, `run_push`, and `write_reconciled_outcomes`. | No further fix is required. |
| F8 | blocking | kgme/sync_io.py:246 | Lock contention discards the incoming trigger and its mode. If 1 push-only run holds the lock when a full session-end sync arrives, the latter exits before committing its dirty ledger, and the owner never performs that work. A commit arriving after an active push captured its revision can similarly remain unpushed. The contention test conceals the missing handoff by manually invoking sync again at `tests/test_sync_guards.py:118`. | Preserve pending triggers and their required mode, then service them after ownership transfers without retrying the same failed attempt. Test overlapping push/full runs and overlapping commits without requiring a third manual invocation. |

## Verdict

BLOCK with 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix: `31fc1564ccabb7b5`.

All 6 automated acceptance items have corresponding tests; the 1 human-terminal item remains explicitly deferred. The reported **184 passed** is builder-supplied evidence. I did not execute tests or modify files.

The changed Python files are at most 282 lines, have module-level purpose/input/output/side-effect documentation, and introduce 0 dependencies. Subprocess calls use argument lists; no `TODO` or `shell=True` was introduced. The hash command emitted sandbox cache warnings, which are tooling limitations, not findings against the diff.
