---
id: AUDIT-0049
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 52586e5e11681fa221339d36305b4fbf3c1ac44a713eb3c3dc590efdc9025d3a"]
tier: 2
created: 2026-10-14T00:25:45-07:00
period: 2026-10-14
review_cycle: 7
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F20]
---

# Review of HANDOFF-0033, cycle 7

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `52586e5e11681fa221339d36305b4fbf3c1ac44a713eb3c3dc590efdc9025d3a`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:98` | Holding and restoration remain removed; final-check regressions remain. | No further fix under the accepted residual risk. |
| F2 | blocking, resolved | `kgme/clean_fs.py:45` | Size and modification-time changes are refused; hashes remain explicitly pre-intent. | No further fix under the accepted writer-race assumption. |
| F3 | blocking, resolved | `kgme/clean_io.py:150` | Both deletion-failure branches stop the run and preserve later paths. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:43` | Listing and child-metadata failures become refusals; regressions remain. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:263` | Refused plans receive blocking outcomes in both modes. | No further fix required. |
| F6 | blocking, resolved | `kgme/clean_io.py:55` | Summary fitting checks raw and redacted lengths; the exact long-basename regression remains. | No further fix required. |
| F7 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | The ledger-writing helper remains named `write_recovery_outcome`. | No further naming fix required. |
| F8 | advisory | `kgme/clean_fs.py:161` | Directory creation remains pathname-based. Michou’s recorded ruling accepts the directory-swap risk; existing checks remain. | No further code change required under the ruling. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. | No further public-invocation fix required. |
| F10 | blocking, resolved | `kgme/clean_fs.py:110` | Whole writes, fsync, size checks, and short-write/failure regressions remain. | No further fix required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The runner supports `--dry-run` and delegates to the shared implementation. | No further fix required. |
| F12 | blocking, resolved | `kgme/clean_io.py:176` | Hashing failures precede intent and deletion; no held entry can be stranded. | No further restoration fix required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:161` | Restoration remains removed; non-absence stat failures do not become successful deletions. | No further restoration fix required. |
| F14 | advisory | `kgme/clean_reconcile.py:119` | The payload read remains pathname-based. Michou’s recorded ruling accepts the ancestor-swap risk; hash verification remains. | No further code change required under the ruling. |
| F15 | blocking, resolved | `kgme/clean_io.py:215` | The exclusive lock spans reconciliation, planning, and deletion; contention coverage remains. | No further overlap fix required. |
| F16 | blocking, resolved | `kgme/clean_fs.py:56` | Special entries are refused during planning; hashing opens without blocking and rejects nonregular files. | No further FIFO fix required. |
| F17 | advisory, resolved | `docs/audit/2026-10-08-loop-0.md:25` | The report describes the rebuild and identifies removed mechanisms as historical. | No further fix to the previously cited mismatch required. |
| F18 | cosmetic, resolved | `kgme/clean_io.py:114` | All 6 `write_stop` parameters remain annotated. | No further fix required. |
| F19 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | Both outcome writers are fully annotated, including `cls: str \| None`; the recovery writer has a docstring. | No further fix required. |
| F20 | blocking | `kgme/clean_read.py:110` | Overlapping cache matches duplicate candidates. With 1 file at `pkg/__pycache__/nested/__pycache__/x.pyc`, both matching directories recursively collect it. The dry run counts 2 files; `--yes` deletes the first occurrence, then refuses the duplicate as gone and stops before removing directories. No concurrent mutation is needed. | Deduplicate candidates by path before planning. Add a nested-cache regression asserting unique plan paths, exit 0, and one deletion outcome per path. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/clean_fs.py:98` | Holding and restoration remain removed; final-check regressions remain. | No further fix under the accepted residual risk. |
| F2 | blocking, resolved | `kgme/clean_fs.py:45` | Size and modification-time changes are refused; hashes remain explicitly pre-intent. | No further fix under the accepted writer-race assumption. |
| F3 | blocking, resolved | `kgme/clean_io.py:150` | Both deletion-failure branches stop the run and preserve later paths. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:43` | Listing and child-metadata failures become refusals; regressions remain. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:263` | Refused plans receive blocking outcomes in both modes. | No further fix required. |
| F6 | blocking, resolved | `kgme/clean_io.py:55` | Summary fitting checks raw and redacted lengths; the exact long-basename regression remains. | No further fix required. |
| F7 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | The ledger-writing helper remains named `write_recovery_outcome`. | No further naming fix required. |
| F8 | advisory | `kgme/clean_fs.py:161` | Directory creation remains pathname-based. Michou’s recorded ruling accepts the directory-swap risk; existing checks remain. | No further code change required under the ruling. |
| F9 | blocking, resolved | `kgme/cli.py:205` | Both public entry points use the repository root and expose no alternate-base argument. | No further public-invocation fix required. |
| F10 | blocking, resolved | `kgme/clean_fs.py:110` | Whole writes, fsync, size checks, and short-write/failure regressions remain. | No further fix required. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The runner supports `--dry-run` and delegates to the shared implementation. | No further fix required. |
| F12 | blocking, resolved | `kgme/clean_io.py:176` | Hashing failures precede intent and deletion; no held entry can be stranded. | No further restoration fix required. |
| F13 | blocking, resolved | `kgme/clean_reconcile.py:161` | Restoration remains removed; non-absence stat failures do not become successful deletions. | No further restoration fix required. |
| F14 | advisory | `kgme/clean_reconcile.py:119` | The payload read remains pathname-based. Michou’s recorded ruling accepts the ancestor-swap risk; hash verification remains. | No further code change required under the ruling. |
| F15 | blocking, resolved | `kgme/clean_io.py:215` | The exclusive lock spans reconciliation, planning, and deletion; contention coverage remains. | No further overlap fix required. |
| F16 | blocking, resolved | `kgme/clean_fs.py:56` | Special entries are refused during planning; hashing opens without blocking and rejects nonregular files. | No further FIFO fix required. |
| F17 | advisory, resolved | `docs/audit/2026-10-08-loop-0.md:25` | The report describes the rebuild and identifies removed mechanisms as historical. | No further fix to the previously cited mismatch required. |
| F18 | cosmetic, resolved | `kgme/clean_io.py:114` | All 6 `write_stop` parameters remain annotated. | No further fix required. |
| F19 | cosmetic, resolved | `kgme/clean_reconcile.py:174` | Both outcome writers are fully annotated, including `cls: str \| None`; the recovery writer has a docstring. | No further fix required. |
| F20 | blocking | `kgme/clean_read.py:110` | Overlapping cache matches duplicate candidates. With 1 file at `pkg/__pycache__/nested/__pycache__/x.pyc`, both matching directories recursively collect it. The dry run counts 2 files; `--yes` deletes the first occurrence, then refuses the duplicate as gone and stops before removing directories. No concurrent mutation is needed. | Deduplicate candidates by path before planning. Add a nested-cache regression asserting unique plan paths, exit 0, and one deletion outcome per path. |

## Verdict

BLOCK (1 open blocking finding: F20).

## Notes

Reviewed sha256 prefix **`52586e5e11681fa2`**, verified before and after review. No files were changed and no tests were run. F20 follows directly from the staged collection, planning, and deletion paths.

All 5 handoff acceptance behaviors have staged tests in `tests/test_clean.py`; the report supplies historical timing evidence. The builder reports **221 passed and 0 blocking lint findings**, which I did not independently execute. Existing cache coverage does not exercise overlapping matches.

The 2 advisory rulings are recorded at `logs/ledger/2026-10.jsonl:846` and `:847`. The staged report’s cycle-6 row still describes the ruling as pending. Hash verification establishes payload content integrity, not its read location: a byte-identical redirected copy can pass, within the accepted threat-model exclusion.

The production modules separate planning from named effects and carry purpose/input/output/side-effect docstrings. `clean_io.py` is 318 lines, slightly above ADR-015’s approximate 300-line guideline. The patch introduces no dependencies, TODOs, or subprocess calls.
