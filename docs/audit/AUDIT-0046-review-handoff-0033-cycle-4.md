---
id: AUDIT-0046
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 8972dc8fd065d952829b494a784615a4962d1d8b5128a33719e1ea7b48991d9f"]
tier: 2
created: 2026-10-13T12:27:53-07:00
period: 2026-10-13
review_cycle: 4
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F6, F9, F12, F13]
---

# Review of HANDOFF-0033, cycle 4

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `8972dc8fd065d952829b494a784615a4962d1d8b5128a33719e1ea7b48991d9f`. Verdict **BLOCK**: blocking 6, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_fs.py:179` | The holding name remains enumerable and replaceable in the same parent directory. A swap after verification still makes `unlink` or `rmdir` remove an unchecked replacement. The new tests swap before the holding rename. Restoration also uses `lstat` followed by overwriting `rename`, so concurrent recreation can lose an unplanned entry. | Protect held entries through deletion and restore without overwriting. Test replacement after hashing, immediately before removal, and during restoration. |
| F2 | blocking | `kgme/clean_fs.py:173` | The planned digest is now checked, but an already-open writable descriptor can change the inode after the final hash and before unlink. Deletion and interruption recovery then report metadata for different bytes. The new rewrite test changes content before deletion starts. | Enforce exclusion of writers through deletion. Test writing through an existing descriptor after the final hash, followed by interruption before the outcome. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both caught failure paths stop deletion. The regression checks that later files remain untouched. | No further fix is required for this finding. |
| F4 | blocking, resolved | `kgme/clean_read.py:40` | Listing and metadata errors become refusals. Tests cover unreadable children and roots. | No further fix is required. |
| F5 | blocking, resolved | `kgme/clean_io.py:237` | Refused plans receive blocking outcomes in both modes. The symlink regression checks both. | No further fix is required. |
| F6 | blocking | `kgme/clean_io.py:80` | `_event` clips raw text after `fit_text` fits its redacted length. For a changed-file refusal with filename `"words " * 24 + "key=x " + "z" * 40`, fitting produces 207 raw characters and 200 redacted characters; the subsequent clip produces 214 redacted characters. Ledger append rejects the refusal, leaving the intent unclosed. | Fit both raw and redacted limits after the final transformation, without subsequent raw clipping. Add this long-basename refusal regression. |
| F7 | cosmetic | `kgme/clean_fs.py:132` | The four cited helpers were renamed, but `_hold`, `_release`, and `_write_whole` perform disk effects without the required prefixes. ADR-015 provides no exemption for private helpers. | Rename them with `run_*` or `write_*` prefixes. |
| F8 | blocking, resolved | `kgme/clean_fs.py:244` | Payload creation retains checked directory descriptors and exclusive, no-follow creation. The linked-directory regression remains present. | No further fix is required for this path-guard finding. |
| F9 | blocking | `kgme/clean_io.py:208` | Nested bases are refused, but any disjoint directory containing even an empty `.git` still passes. Public `--base` therefore rebases deletion permissions outside `KGME_HOME`; the directory’s `memory/agent` is treated as disposable without authorization. | Restrict public invocation to the authorized repository root. Keep temporary-root injection internal to tests and test refusal of disjoint alternate bases. |
| F10 | blocking, resolved | `kgme/clean_fs.py:226` | The writer handles short writes, fsyncs, and checks persisted size. Tests cover seven-byte writes and failure on the second write before deletion. | No further fix is required for the short-write finding. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner exists, supports `--dry-run`, and delegates to the same implementation. | No further fix is required. |
| F12 | blocking | `kgme/clean_fs.py:171` | An `OSError` during the held file’s `fstat` or hash closes its descriptor without restoring its name. `run_deletions` then closes the intent as stopped, so startup reconciliation never restores this stranded entry. | Restore on every post-hold failure, or retain explicit pending recovery until restoration succeeds. Test a hash-read error after holding. |
| F13 | blocking | `kgme/clean_reconcile.py:120` | Restoration errors become `False`, which the caller interprets as deletion. With a held file’s parent readable but non-writable, restoration fails, yet reconciliation writes an `ok` deletion outcome and closes the intent while the file still exists under its holding name. | Distinguish absence from failed restoration. Record the failure and retain pending recovery; test restoration under a non-writable parent. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_fs.py:179` | The holding name remains enumerable and replaceable in the same parent directory. A swap after verification still makes `unlink` or `rmdir` remove an unchecked replacement. The new tests swap before the holding rename. Restoration also uses `lstat` followed by overwriting `rename`, so concurrent recreation can lose an unplanned entry. | Protect held entries through deletion and restore without overwriting. Test replacement after hashing, immediately before removal, and during restoration. |
| F2 | blocking | `kgme/clean_fs.py:173` | The planned digest is now checked, but an already-open writable descriptor can change the inode after the final hash and before unlink. Deletion and interruption recovery then report metadata for different bytes. The new rewrite test changes content before deletion starts. | Enforce exclusion of writers through deletion. Test writing through an existing descriptor after the final hash, followed by interruption before the outcome. |
| F3 | blocking, resolved | `kgme/clean_io.py:144` | Both caught failure paths stop deletion. The regression checks that later files remain untouched. | No further fix is required for this finding. |
| F4 | blocking, resolved | `kgme/clean_read.py:40` | Listing and metadata errors become refusals. Tests cover unreadable children and roots. | No further fix is required. |
| F5 | blocking, resolved | `kgme/clean_io.py:237` | Refused plans receive blocking outcomes in both modes. The symlink regression checks both. | No further fix is required. |
| F6 | blocking | `kgme/clean_io.py:80` | `_event` clips raw text after `fit_text` fits its redacted length. For a changed-file refusal with filename `"words " * 24 + "key=x " + "z" * 40`, fitting produces 207 raw characters and 200 redacted characters; the subsequent clip produces 214 redacted characters. Ledger append rejects the refusal, leaving the intent unclosed. | Fit both raw and redacted limits after the final transformation, without subsequent raw clipping. Add this long-basename refusal regression. |
| F7 | cosmetic | `kgme/clean_fs.py:132` | The four cited helpers were renamed, but `_hold`, `_release`, and `_write_whole` perform disk effects without the required prefixes. ADR-015 provides no exemption for private helpers. | Rename them with `run_*` or `write_*` prefixes. |
| F8 | blocking, resolved | `kgme/clean_fs.py:244` | Payload creation retains checked directory descriptors and exclusive, no-follow creation. The linked-directory regression remains present. | No further fix is required for this path-guard finding. |
| F9 | blocking | `kgme/clean_io.py:208` | Nested bases are refused, but any disjoint directory containing even an empty `.git` still passes. Public `--base` therefore rebases deletion permissions outside `KGME_HOME`; the directory’s `memory/agent` is treated as disposable without authorization. | Restrict public invocation to the authorized repository root. Keep temporary-root injection internal to tests and test refusal of disjoint alternate bases. |
| F10 | blocking, resolved | `kgme/clean_fs.py:226` | The writer handles short writes, fsyncs, and checks persisted size. Tests cover seven-byte writes and failure on the second write before deletion. | No further fix is required for the short-write finding. |
| F11 | advisory, resolved | `jobs/clean/run.py:21` | The thin runner exists, supports `--dry-run`, and delegates to the same implementation. | No further fix is required. |
| F12 | blocking | `kgme/clean_fs.py:171` | An `OSError` during the held file’s `fstat` or hash closes its descriptor without restoring its name. `run_deletions` then closes the intent as stopped, so startup reconciliation never restores this stranded entry. | Restore on every post-hold failure, or retain explicit pending recovery until restoration succeeds. Test a hash-read error after holding. |
| F13 | blocking | `kgme/clean_reconcile.py:120` | Restoration errors become `False`, which the caller interprets as deletion. With a held file’s parent readable but non-writable, restoration fails, yet reconciliation writes an `ok` deletion outcome and closes the intent while the file still exists under its holding name. | Distinguish absence from failed restoration. Record the failure and retain pending recovery; test restoration under a non-writable parent. |

## Verdict

BLOCK with 6 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`8972dc8fd065d952`**, verified before and after inspection. This was a static, read-only review; no tests were run. Tooling warnings were excluded from findings.

All 5 handoff acceptance behaviors have tests in `tests/test_clean.py`: seeded dry run, deletion with outcomes, symlink refusal, unknown-target rejection, and rejection of `ledger`. The audit supplies timing evidence. The builder reports 37 clean tests and 213 full-suite tests passing; those results were not independently reproduced. Reconstruction evidence belongs to the separately reported HANDOFF-0034 work.

New Python files remain below 300 lines and carry purpose, inputs, outputs, and side-effect headers. The patch introduces no dependency, subprocess, `shell=True`, or `TODO`. F7 identifies the remaining effect-naming issue.

## Escalation

```
ESCALATION HANDOFF-0033: review loop halted after 4 cycles.
What failed: 4 root causes survived a fix cycle: F1, F2, F6, F9. Class: blocking.
Evidence:
  F1 `kgme/clean_fs.py:179`: The holding name remains enumerable and replaceable in the same parent directory. A swap after verification still makes `unlink` or `rmdir` remove an unchecked replacement. The new tests swap before the holding rename. Restoration also uses `lstat` followed by overwriting `rename`, so concurrent recreation can lose an unplanned entry.
  F2 `kgme/clean_fs.py:173`: The planned digest is now checked, but an already-open writable descriptor can change the inode after the final hash and before unlink. Deletion and interruption recovery then report metadata for different bytes. The new rewrite test changes content before deletion starts.
  F6 `kgme/clean_io.py:80`: `_event` clips raw text after `fit_text` fits its redacted length. For a changed-file refusal with filename `"words " * 24 + "key=x " + "z" * 40`, fitting produces 207 raw characters and 200 redacted characters; the subsequent clip produces 214 redacted characters. Ledger append rejects the refusal, leaving the intent unclosed.
  F9 `kgme/clean_io.py:208`: Nested bases are refused, but any disjoint directory containing even an empty `.git` still passes. Public `--base` therefore rebases deletion permissions outside `KGME_HOME`; the directory’s `memory/agent` is treated as disposable without authorization.
  F12 `kgme/clean_fs.py:171`: An `OSError` during the held file’s `fstat` or hash closes its descriptor without restoring its name. `run_deletions` then closes the intent as stopped, so startup reconciliation never restores this stranded entry.
  F13 `kgme/clean_reconcile.py:120`: Restoration errors become `False`, which the caller interprets as deletion. With a held file’s parent readable but non-writable, restoration fails, yet reconciliation writes an `ok` deletion outcome and closes the intent while the file still exists under its holding name.
Options: override (kgme review override --handoff HANDOFF-0033 --reason ...), reject (revert the working tree), retry (fix, then override, then kgme review again); a disputed class goes to the arbiter claude-opus-5-5 once, recorded with kgme review rule.
Recommended default: override and continue when the remaining findings are understood; reject when they are not.
If you do nothing: nothing is committed.
```
