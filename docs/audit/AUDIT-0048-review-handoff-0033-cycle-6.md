---
id: AUDIT-0048
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 c8a4afc2327cd8fe3dfc1addd47bd87f660accd798bc753473d6bcefb9d942a9"]
tier: 2
created: 2026-10-14T00:11:58-07:00
period: 2026-10-14
review_cycle: 6
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8, F14]
---

# Review of HANDOFF-0033, cycle 6

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `c8a4afc2327cd8fe3dfc1addd47bd87f660accd798bc753473d6bcefb9d942a9`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:98` | Holding and overwriting restoration remain removed. Final-check regressions remain. | No further fix under the supplied residual-risk assumption. |
| F2 | blocking, resolved | `kgme/clean_fs.py:45` | Size and modification-time changes are refused; the hash remains explicitly pre-intent. | Resolution retains the supplied writer-race assumption. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both deletion-failure branches stop the run and preserve later paths. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:43` | Listing and child-metadata failures become refusals, with regressions retained. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:257` | Refused plans receive blocking outcomes in both modes. | No further fix required. |
| F6 | blocking, resolved | `kgme/clean_io.py:55` | Summary fitting checks raw and redacted lengths; the exact long-basename regression remains. | No further fix required. |
| F7 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | The ledger-writing helper is now named `write_recovery_outcome`. | No further naming fix required. |
| F8 | blocking | `kgme/clean_fs.py:161` | Descriptor-relative file creation fixes the reported final-open race, but directory creation still precedes binding. Swap `logs/scratch` for a link to `docs` after line 159: `mkdir(parents=True)` creates `docs/payloads` before the later check refuses the run. Both new regressions inject their swaps after this mkdir. This remains a write outside the disposable boundary. | Bind directory creation too, or require an existing checked directory. Test a scratch-ancestor swap immediately before mkdir and assert that `docs` remains unchanged. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. | No further public-invocation fix required. |
| F10 | blocking, resolved | `kgme/clean_fs.py:110` | Whole writes, fsync, size checks, and short-write/failure regressions remain. | No further fix required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner supports `--dry-run` and delegates to the shared implementation. | No further fix required. |
| F12 | blocking, resolved | `kgme/clean_io.py:170` | Hashing failures precede the intent and deletion; no held entry can be stranded. | No further restoration fix required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:161` | Restoration remains removed; non-absence stat failures do not become successful deletions. | No further restoration fix required. |
| F14 | blocking | `kgme/clean_reconcile.py:119` | Hash verification fixes altered JSON, but the payload read remains redirectable. Swap its parent for a symlink after the ancestry check at line 116: pathname-based `os.open` follows that ancestor, and line 126 reads the redirected file. `O_NOFOLLOW` protects only the final component. Hash rejection happens after the unauthorized read; a genuine payload copied there passes. The new link test plants its link before checking. | Open the payload relative to a checked, bound directory before reading bytes. Add an ancestor-swap regression after the final ancestry check and verify blocking recovery without reading the redirected file. |
| F15 | blocking, resolved | `kgme/clean_io.py:193` | The exclusive lock spans reconciliation, planning, and deletion. The contention regression covers both modes and subsequent reconciliation. | No further overlap fix required. |
| F16 | blocking, resolved | `kgme/clean_fs.py:61` | Special entries are refused during planning; hashing uses nonblocking open and rejects nonregular files. Both FIFO regressions are present. | No further FIFO fix required. |
| F17 | advisory, resolved | `docs/audit/2026-10-08-loop-0.md:25` | The staged report describes the rebuild and cycle-5 dispositions; removed mechanisms are identified as historical. | No further fix to the cited report mismatch required. |
| F18 | cosmetic, resolved | `kgme/clean_io.py:108` | All 6 `write_stop` parameters are annotated. | No further fix to this function required. |
| F19 | cosmetic | `kgme/clean_reconcile.py:174` | Newly public `write_recovery_outcome` has 7 unannotated parameters; `write_outcome` also leaves `cls` unannotated. ADR-015 requires public-function type hints. | Annotate these parameters, including `cls: str \| None`. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:98` | Holding and overwriting restoration remain removed. Final-check regressions remain. | No further fix under the supplied residual-risk assumption. |
| F2 | blocking, resolved | `kgme/clean_fs.py:45` | Size and modification-time changes are refused; the hash remains explicitly pre-intent. | Resolution retains the supplied writer-race assumption. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both deletion-failure branches stop the run and preserve later paths. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:43` | Listing and child-metadata failures become refusals, with regressions retained. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:257` | Refused plans receive blocking outcomes in both modes. | No further fix required. |
| F6 | blocking, resolved | `kgme/clean_io.py:55` | Summary fitting checks raw and redacted lengths; the exact long-basename regression remains. | No further fix required. |
| F7 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | The ledger-writing helper is now named `write_recovery_outcome`. | No further naming fix required. |
| F8 | blocking | `kgme/clean_fs.py:161` | Descriptor-relative file creation fixes the reported final-open race, but directory creation still precedes binding. Swap `logs/scratch` for a link to `docs` after line 159: `mkdir(parents=True)` creates `docs/payloads` before the later check refuses the run. Both new regressions inject their swaps after this mkdir. This remains a write outside the disposable boundary. | Bind directory creation too, or require an existing checked directory. Test a scratch-ancestor swap immediately before mkdir and assert that `docs` remains unchanged. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. | No further public-invocation fix required. |
| F10 | blocking, resolved | `kgme/clean_fs.py:110` | Whole writes, fsync, size checks, and short-write/failure regressions remain. | No further fix required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner supports `--dry-run` and delegates to the shared implementation. | No further fix required. |
| F12 | blocking, resolved | `kgme/clean_io.py:170` | Hashing failures precede the intent and deletion; no held entry can be stranded. | No further restoration fix required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:161` | Restoration remains removed; non-absence stat failures do not become successful deletions. | No further restoration fix required. |
| F14 | blocking | `kgme/clean_reconcile.py:119` | Hash verification fixes altered JSON, but the payload read remains redirectable. Swap its parent for a symlink after the ancestry check at line 116: pathname-based `os.open` follows that ancestor, and line 126 reads the redirected file. `O_NOFOLLOW` protects only the final component. Hash rejection happens after the unauthorized read; a genuine payload copied there passes. The new link test plants its link before checking. | Open the payload relative to a checked, bound directory before reading bytes. Add an ancestor-swap regression after the final ancestry check and verify blocking recovery without reading the redirected file. |
| F15 | blocking, resolved | `kgme/clean_io.py:193` | The exclusive lock spans reconciliation, planning, and deletion. The contention regression covers both modes and subsequent reconciliation. | No further overlap fix required. |
| F16 | blocking, resolved | `kgme/clean_fs.py:61` | Special entries are refused during planning; hashing uses nonblocking open and rejects nonregular files. Both FIFO regressions are present. | No further FIFO fix required. |
| F17 | advisory, resolved | `docs/audit/2026-10-08-loop-0.md:25` | The staged report describes the rebuild and cycle-5 dispositions; removed mechanisms are identified as historical. | No further fix to the cited report mismatch required. |
| F18 | cosmetic, resolved | `kgme/clean_io.py:108` | All 6 `write_stop` parameters are annotated. | No further fix to this function required. |
| F19 | cosmetic | `kgme/clean_reconcile.py:174` | Newly public `write_recovery_outcome` has 7 unannotated parameters; `write_outcome` also leaves `cls` unannotated. ADR-015 requires public-function type hints. | Annotate these parameters, including `cls: str \| None`. |

## Verdict

BLOCK with 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `c8a4afc2327cd8fe`, verified against the patch and `review.sha`.

All 5 functional handoff acceptance items have corresponding tests. Duplicate-run, interrupted-run, and forbidden-access tests are present; the report states why reconstruction is inapplicable to a deleter. Timing evidence is stated. The builder reports 221 passing tests and 0 blocking lint findings; I did not rerun tests or modify files.

No dependencies, subprocess calls, `shell=True`, or TODOs are introduced. The 312-line `clean_io.py` is reasonably within the “about 300” guideline.

F8 and F14 concern payload boundaries outside the accepted check-to-unlink residual risk. Both remain open across cycles 5 and 6, so the review-loop rule requires the next disposition to remove the affected mechanism or obtain Michou’s threat-model ruling.
