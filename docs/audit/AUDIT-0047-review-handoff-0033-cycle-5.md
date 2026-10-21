---
id: AUDIT-0047
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 5e819ab9da0ae3a2faced52255c1ae6b92b382195c01f685a300bcb4b5c2d7cc"]
tier: 2
created: 2026-10-14T00:01:54-07:00
period: 2026-10-14
review_cycle: 5
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8, F14, F15, F16]
---

# Review of HANDOFF-0033, cycle 5

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `5e819ab9da0ae3a2faced52255c1ae6b92b382195c01f685a300bcb4b5c2d7cc`. Verdict **BLOCK**: blocking 4, transient 0, cosmetic 2, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:89` | The holding name and overwriting restoration are gone. Replacement tests cover refusal before the final check. | No further holding/restoration fix is required under the supplied residual-risk assumption. |
| F2 | blocking, resolved | `kgme/clean_fs.py:13` | Size and modification-time changes are refused. The hash is explicitly defined as the pre-intent hash; the remaining writer race is documented. | Resolution relies on the supplied threat-model disposition, not exclusion of writers. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both caught deletion failures stop the run; regression tests preserve later files. | No further fix is required. |
| F4 | blocking, resolved | `kgme/clean_read.py:41` | Listing and metadata errors become refusals. Unreadable-root and child tests remain. | No further fix is required. |
| F5 | blocking, resolved | `kgme/clean_io.py:237` | Refused plans receive blocking outcomes in both modes. | No further fix is required. |
| F6 | blocking, resolved | `kgme/clean_io.py:82` | Fitting measures both raw and redacted lengths, with no subsequent clipping. The exact long-basename regression remains. | No further fix is required. |
| F7 | cosmetic | `kgme/clean_reconcile.py:110` | The cited filesystem helpers are gone, but `_write_outcome` still performs ledger writes without the required literal effect prefix. | Rename it with `write_*` and update its callers. |
| F8 | blocking | `kgme/clean_fs.py:131` | Payload creation has lost its directory-descriptor protection. Replacing `payloads` with a link to `docs` after the second ancestry check redirects `os.open` into `docs`; `O_NOFOLLOW` protects only the final component. The existing test plants the link before checking. This write-path risk is additional to the stated check-to-unlink risk. | Bind creation to the checked directory, or obtain an explicit ruling covering this additional boundary weakening. Test an ancestor swap after the final ancestry check. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. The CLI regression verifies this restriction. | No further fix is required for public invocation. |
| F10 | blocking, resolved | `kgme/clean_fs.py:101` | Whole writes, fsync, and persisted-size checks remain, with short-write and failed-write regressions. | No further fix is required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner supports `--dry-run` and delegates to the shared implementation. | No further fix is required. |
| F12 | blocking, resolved | `kgme/clean_fs.py:51` | Hashing failures occur before the intent and deletion. There is no held entry to strand. | No further restoration fix is required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:97` | Restoration is removed. Non-absence stat errors no longer become successful deletion outcomes. | No further restoration fix is required. |
| F14 | blocking | `kgme/clean_reconcile.py:73` | Recovery trusts mutable scratch JSON without checking `payload_sha256`; the fixtures even supply 64 zeroes. Changing a payload before restart can therefore produce permanent `ok` outcomes with invented paths, sizes, or hashes. The read also follows an existing payload symlink before policy checks. | Guard the payload read and verify its recorded hash and structure before interpreting it. Record a blocking recovery failure on invalid evidence. Add altered-payload and linked-payload tests. |
| F15 | blocking | `kgme/clean_reconcile.py:64` | An open intent need not belong to a dead process. Run A can pause after its intent; run B, even a dry run, closes A while its files remain; A then deletes a file and dies before its outcome. Subsequent reconciliation skips A permanently because B already closed it. | Exclude overlapping runs across reconciliation and execution, or establish that the previous run ended. Test this 2-run interleaving. |
| F16 | blocking | `kgme/clean_fs.py:55` | Listing treats a FIFO as a file. A FIFO under `logs/scratch` with no writer makes `--yes` block indefinitely in `os.open`, before any intent or refusal is recorded. No special-file test covers this case. | Refuse unsupported file kinds and ensure opening for verification cannot block on a FIFO. Add a FIFO refusal regression. |
| F17 | advisory | `docs/audit/2026-10-08-loop-0.md:25` | The staged report still describes descriptor chains, holding, and restoration, and marks removed tests as passing. Its working-tree corrections are outside the reviewed patch. | Bring the staged report into agreement with the rebuild and current evidence. |
| F18 | cosmetic | `kgme/clean_io.py:110` | Public `write_stop` has no parameter annotations, contrary to ADR-015. | Annotate its 6 parameters. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:89` | The holding name and overwriting restoration are gone. Replacement tests cover refusal before the final check. | No further holding/restoration fix is required under the supplied residual-risk assumption. |
| F2 | blocking, resolved | `kgme/clean_fs.py:13` | Size and modification-time changes are refused. The hash is explicitly defined as the pre-intent hash; the remaining writer race is documented. | Resolution relies on the supplied threat-model disposition, not exclusion of writers. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both caught deletion failures stop the run; regression tests preserve later files. | No further fix is required. |
| F4 | blocking, resolved | `kgme/clean_read.py:41` | Listing and metadata errors become refusals. Unreadable-root and child tests remain. | No further fix is required. |
| F5 | blocking, resolved | `kgme/clean_io.py:237` | Refused plans receive blocking outcomes in both modes. | No further fix is required. |
| F6 | blocking, resolved | `kgme/clean_io.py:82` | Fitting measures both raw and redacted lengths, with no subsequent clipping. The exact long-basename regression remains. | No further fix is required. |
| F7 | cosmetic | `kgme/clean_reconcile.py:110` | The cited filesystem helpers are gone, but `_write_outcome` still performs ledger writes without the required literal effect prefix. | Rename it with `write_*` and update its callers. |
| F8 | blocking | `kgme/clean_fs.py:131` | Payload creation has lost its directory-descriptor protection. Replacing `payloads` with a link to `docs` after the second ancestry check redirects `os.open` into `docs`; `O_NOFOLLOW` protects only the final component. The existing test plants the link before checking. This write-path risk is additional to the stated check-to-unlink risk. | Bind creation to the checked directory, or obtain an explicit ruling covering this additional boundary weakening. Test an ancestor swap after the final ancestry check. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. The CLI regression verifies this restriction. | No further fix is required for public invocation. |
| F10 | blocking, resolved | `kgme/clean_fs.py:101` | Whole writes, fsync, and persisted-size checks remain, with short-write and failed-write regressions. | No further fix is required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner supports `--dry-run` and delegates to the shared implementation. | No further fix is required. |
| F12 | blocking, resolved | `kgme/clean_fs.py:51` | Hashing failures occur before the intent and deletion. There is no held entry to strand. | No further restoration fix is required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:97` | Restoration is removed. Non-absence stat errors no longer become successful deletion outcomes. | No further restoration fix is required. |
| F14 | blocking | `kgme/clean_reconcile.py:73` | Recovery trusts mutable scratch JSON without checking `payload_sha256`; the fixtures even supply 64 zeroes. Changing a payload before restart can therefore produce permanent `ok` outcomes with invented paths, sizes, or hashes. The read also follows an existing payload symlink before policy checks. | Guard the payload read and verify its recorded hash and structure before interpreting it. Record a blocking recovery failure on invalid evidence. Add altered-payload and linked-payload tests. |
| F15 | blocking | `kgme/clean_reconcile.py:64` | An open intent need not belong to a dead process. Run A can pause after its intent; run B, even a dry run, closes A while its files remain; A then deletes a file and dies before its outcome. Subsequent reconciliation skips A permanently because B already closed it. | Exclude overlapping runs across reconciliation and execution, or establish that the previous run ended. Test this 2-run interleaving. |
| F16 | blocking | `kgme/clean_fs.py:55` | Listing treats a FIFO as a file. A FIFO under `logs/scratch` with no writer makes `--yes` block indefinitely in `os.open`, before any intent or refusal is recorded. No special-file test covers this case. | Refuse unsupported file kinds and ensure opening for verification cannot block on a FIFO. Add a FIFO refusal regression. |
| F17 | advisory | `docs/audit/2026-10-08-loop-0.md:25` | The staged report still describes descriptor chains, holding, and restoration, and marks removed tests as passing. Its working-tree corrections are outside the reviewed patch. | Bring the staged report into agreement with the rebuild and current evidence. |
| F18 | cosmetic | `kgme/clean_io.py:110` | Public `write_stop` has no parameter annotations, contrary to ADR-015. | Annotate its 6 parameters. |

## Verdict

BLOCK with 4 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `5e819ab9da0ae3a2`, verified again after inspection.

All 5 handoff acceptance items have tests in `tests/test_clean.py` at lines 26, 42, 63, and 91. Duplicate-run and interruption tests also remain. I did not run pytest or `make check`; **214 passed and 0 blocking lint findings** are builder-reported evidence.

The 5 new implementation modules are 124–292 lines, have the required module docstrings, and separate planning from filesystem effects. The patch introduces no dependency, subprocess call, `shell=True`, or TODO.

F1/F2 resolution accepts the supplied deletion-race scope. It does not establish race freedom or confinement during an ancestor swap. F8 concerns the separately weakened payload-write boundary. Tooling limits were not counted against the diff.
