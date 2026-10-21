---
id: AUDIT-0040
type: report
status: final
handoff: HANDOFF-0040
author: codex
source: inferred
sources: ["HANDOFF-0040", "staged diff sha256 a576c1bbe73317ce4a0f6e3e801b8c4620d16e552ebd0e584f61e5571bc2cee7"]
tier: 2
created: 2026-10-09T22:22:59-07:00
period: 2026-10-09
review_cycle: 5
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8]
---

# Review of HANDOFF-0040, cycle 5

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `a576c1bbe73317ce4a0f6e3e801b8c4620d16e552ebd0e584f61e5571bc2cee7`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/sync_git.py:178 | The ledger commit suppresses its nested hook, preserving 1 push owner. Coverage remains at `tests/test_sync_guards.py:41`. | No further fix is required. |
| F2 | blocking, resolved | kgme/sync_git.py:59 | A stalled push receives process-group termination and 1 transient outcome, with exit 0. Coverage remains at `tests/test_sync_guards.py:59`. | No further fix is required for the reported stalled-push case. |
| F3 | blocking, resolved | kgme/sync_io.py:160 | Validation precedes locking, and both commit commands retain the 1 literal `logs/ledger` pathspec. Coverage remains at `tests/test_sync_guards.py:87`. | No further fix is required. |
| F4 | blocking, resolved | kgme/sync_io.py:194 | Reconciliation remains under 1 exclusive lock, preventing a contender from closing the active owner's intent. | No further fix is required for the original duplicate-outcome defect. |
| F5 | blocking, resolved | kgme/sync_io.py:112 | Behind-upstream refusal remains `transient`; `tests/test_sync.py:136` checks classification and an unchanged remote. | No further fix is required. |
| F6 | blocking, resolved | docs/audit/2026-10-08-push-on-commit.md:72 | The 1 human-terminal check remains explicitly deferred under the accepted disposition. | Record Michou's terminal commit, remote SHA, and ahead count of 0 within 1 minute when completed. |
| F7 | cosmetic, resolved | kgme/sync_git.py:37 | The 3 previously cited helpers retain the names `run_git`, `run_push`, and `write_reconciled_outcomes`. | No further fix is required. |
| F8 | blocking | [kgme/sync_io.py:142](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:142), [kgme/sync_io.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:197) | The 5-round cap is removed, but both gate callers proceed when `write_lock` returns `None`. Consider 1 owner paused after its empty scan at line 198 while holding both locks: a full waiter exhausts its lock and gate waits, publishes without the gate, fails its lock retry, and exits. The owner resumes, releases the lock at line 200, and exits without another scan. This leaves 1 pending full request, uncommitted foreign events, and 0 workers. The test at `tests/test_sync_pending.py:121` releases the gate before its timeout and misses this ordering. | Require successful gate acquisition before either critical section, preserving an active owner or automatic successor on timeout. Add a deterministic regression for this ordering without a third invocation or repeated failed push. Also exercise more than 5 successive service rounds; 7 requests present at startup test only 1 batch. |
| F9 | cosmetic | [kgme/sync_io.py:135](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:135) | The 1 new helper `_leave_request` acquires locks and writes files without an ADR-015 effect prefix. | Rename it to `write_pending_handoff` or another appropriate `write_*` / `run_*` name. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/sync_git.py:178 | The ledger commit suppresses its nested hook, preserving 1 push owner. Coverage remains at `tests/test_sync_guards.py:41`. | No further fix is required. |
| F2 | blocking, resolved | kgme/sync_git.py:59 | A stalled push receives process-group termination and 1 transient outcome, with exit 0. Coverage remains at `tests/test_sync_guards.py:59`. | No further fix is required for the reported stalled-push case. |
| F3 | blocking, resolved | kgme/sync_io.py:160 | Validation precedes locking, and both commit commands retain the 1 literal `logs/ledger` pathspec. Coverage remains at `tests/test_sync_guards.py:87`. | No further fix is required. |
| F4 | blocking, resolved | kgme/sync_io.py:194 | Reconciliation remains under 1 exclusive lock, preventing a contender from closing the active owner's intent. | No further fix is required for the original duplicate-outcome defect. |
| F5 | blocking, resolved | kgme/sync_io.py:112 | Behind-upstream refusal remains `transient`; `tests/test_sync.py:136` checks classification and an unchanged remote. | No further fix is required. |
| F6 | blocking, resolved | docs/audit/2026-10-08-push-on-commit.md:72 | The 1 human-terminal check remains explicitly deferred under the accepted disposition. | Record Michou's terminal commit, remote SHA, and ahead count of 0 within 1 minute when completed. |
| F7 | cosmetic, resolved | kgme/sync_git.py:37 | The 3 previously cited helpers retain the names `run_git`, `run_push`, and `write_reconciled_outcomes`. | No further fix is required. |
| F8 | blocking | [kgme/sync_io.py:142](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:142), [kgme/sync_io.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:197) | The 5-round cap is removed, but both gate callers proceed when `write_lock` returns `None`. Consider 1 owner paused after its empty scan at line 198 while holding both locks: a full waiter exhausts its lock and gate waits, publishes without the gate, fails its lock retry, and exits. The owner resumes, releases the lock at line 200, and exits without another scan. This leaves 1 pending full request, uncommitted foreign events, and 0 workers. The test at `tests/test_sync_pending.py:121` releases the gate before its timeout and misses this ordering. | Require successful gate acquisition before either critical section, preserving an active owner or automatic successor on timeout. Add a deterministic regression for this ordering without a third invocation or repeated failed push. Also exercise more than 5 successive service rounds; 7 requests present at startup test only 1 batch. |
| F9 | cosmetic | [kgme/sync_io.py:135](/Users/michaelgrigorian/Projects/Automate/kgme/sync_io.py:135) | The 1 new helper `_leave_request` acquires locks and writes files without an ADR-015 effect prefix. | Rename it to `write_pending_handoff` or another appropriate `write_*` / `run_*` name. |

## Verdict

BLOCK: 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`a576c1bbe73317ce`**, verified before and after inspection. This was a static review; no tests ran and no files were changed.

All 6 automated acceptance items have tests; the 1 terminal check retains its accepted deferral. The 3 new production modules contain 101, 189, and 246 lines, with the required module docstrings. The patch adds 0 dependencies and contains no `TODO` or `shell=True`; subprocess calls use argument lists.

The historical 191-test pass and current 188-pass/3-fail state are builder-reported. The 4 reported HANDOFF-0036 lint findings are outside this patch and are not findings against HANDOFF-0040. F8 remains the existing trigger-service defect, not a new root cause.
