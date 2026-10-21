---
id: AUDIT-0064
type: report
status: final
handoff: HANDOFF-0050
author: codex
source: inferred
sources: ["HANDOFF-0050", "staged diff sha256 963cd8812994f29c9dd62bca93ab90ada5bc1ca9bb38dc28fc074cc71b224baf"]
tier: 2
created: 2026-10-21T00:22:39-07:00
period: 2026-10-21
review_cycle: 6
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F13, F15]
---

# Review of HANDOFF-0050, cycle 6

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `963cd8812994f29c9dd62bca93ab90ada5bc1ca9bb38dc28fc074cc71b224baf`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 2, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/capture_fs.py:149` | New files are published complete without replacing existing destinations. The interruption regression remains. | Implemented and covered. |
| F2 | blocking, resolved | `kgme/capture_recover.py:38`; `kgme/daily_io.py:125` | Held words survive payload removal through the durable summary. Available payloads remain authoritative. | Implemented and covered. |
| F3 | blocking, resolved | `kgme/capture_recover.py:111`; `kgme/capture_recover.py:146` | Post-write failures and retries inspect byte evidence, including attempts closed in error. | Implemented and covered. |
| F4 | blocking, resolved | `kgme/capture_record.py:97` | Recovery uses hash-bound metadata instead of redacted destination summaries. | Implemented and covered. |
| F5 | blocking, resolved | `kgme/daily.py:157` | Unrelated capture successes do not resolve failures. | Implemented and covered. |
| F6 | blocking, resolved | `kgme/brief_read.py:108` | The morning brief reads the preceding evening’s draft when today’s note is absent. | Implemented and covered. |
| F7 | blocking, resolved | `jobs/capture/run.py:22`; `jobs/daily/run.py:22` | Both entry points accept `--dry-run`; coverage checks preview output and unchanged vault bytes. | Implemented and covered. |
| F8 | blocking, resolved | `kgme/capture_record.py:68`; `tests/test_capture_review.py:197` | Payloads preserve exact written bytes for both jobs, including words exceeding the summary limit. | Implemented within ADR-019’s disposable-payload policy. |
| F9 | cosmetic, resolved | `kgme/capture_io.py:1`; `kgme/daily_io.py:215`; `tests/test_capture.py:331` | The effects split, documented failure helper, and test classification remain. | Implemented. |
| F10 | blocking, resolved | `kgme/capture_fs.py:125`; `tests/test_capture_review.py:315` | Whole-file publication removes the partial-append mechanism. Both destination kinds retain interruption-before-publication regressions. | Implemented per the ruling. |
| F11 | cosmetic, resolved | `kgme/capture_io.py:245` | `write_announcement` names and documents its payload and ledger effects. | Implemented. |
| F12 | blocking, resolved | `kgme/capture_recover.py:91` | Recovery reads destination evidence and writes ledger outcomes only. | Resolved by removing the vault-write mechanism. |
| F13 | blocking | `kgme/capture_fs.py:129`; `kgme/capture_fs.py:143`; `docs/audit/2026-10-16-capture-and-daily.md:66` | The new tests preserve saves completed before the exchange, but the race remains after the displaced-byte check. A writer can open the original before the exchange, then write and close after that check. Cleanup unlinks the edited inode and capture records success. Ordinary scheduling between open, write, and close suffices. The report acknowledges this loss window; its approval-screen score is not an explicit boundary ruling. | Obtain the boundary ruling required by the previous finding, or protect against intervening writers. Add a regression that writes through the original descriptor after the displaced-byte check and requires preservation. |
| F14 | cosmetic, resolved | `jobs/capture/manifest.toml:11` | The manifest now describes `write_new`, `write_replaced`, and exchange rollback instead of `O_APPEND`. | Implemented. |
| F15 | blocking | `kgme/capture_fs.py:128`; `kgme/capture_fs.py:140`; `kgme/capture_recover.py:123` | Exception cleanup can delete an already completed edit independently of F13’s remaining race. After an editor saves and closes, the first exchange moves that edit to `temp`. If the displaced-file read raises, rollback fails, or execution is interrupted before validation, `keep` remains false and `finally` deletes the edited file. On an `OSError` path, settlement sees the intended destination hash and can return success despite the loss. | Preserve the displaced file whenever exchange or rollback state is uncertain, identify it in the failure record, and prevent successful settlement from concealing that uncertainty. Test failures after the first exchange and during rollback, with an edit completed beforehand. |
| F16 | cosmetic | `kgme/capture_fs.py:55` | `swap_names` changes filesystem state without ADR-015’s required effect prefix. | Rename it with a `write_*` or `run_*` prefix and update callers and tests. |
| F17 | cosmetic | `tests/test_capture_review.py:364` | The review test module has grown to 414 lines, beyond ADR-015’s approximately 300-line convention. | Split the regression groups along their existing responsibilities. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/capture_fs.py:149` | New files are published complete without replacing existing destinations. The interruption regression remains. | Implemented and covered. |
| F2 | blocking, resolved | `kgme/capture_recover.py:38`; `kgme/daily_io.py:125` | Held words survive payload removal through the durable summary. Available payloads remain authoritative. | Implemented and covered. |
| F3 | blocking, resolved | `kgme/capture_recover.py:111`; `kgme/capture_recover.py:146` | Post-write failures and retries inspect byte evidence, including attempts closed in error. | Implemented and covered. |
| F4 | blocking, resolved | `kgme/capture_record.py:97` | Recovery uses hash-bound metadata instead of redacted destination summaries. | Implemented and covered. |
| F5 | blocking, resolved | `kgme/daily.py:157` | Unrelated capture successes do not resolve failures. | Implemented and covered. |
| F6 | blocking, resolved | `kgme/brief_read.py:108` | The morning brief reads the preceding evening’s draft when today’s note is absent. | Implemented and covered. |
| F7 | blocking, resolved | `jobs/capture/run.py:22`; `jobs/daily/run.py:22` | Both entry points accept `--dry-run`; coverage checks preview output and unchanged vault bytes. | Implemented and covered. |
| F8 | blocking, resolved | `kgme/capture_record.py:68`; `tests/test_capture_review.py:197` | Payloads preserve exact written bytes for both jobs, including words exceeding the summary limit. | Implemented within ADR-019’s disposable-payload policy. |
| F9 | cosmetic, resolved | `kgme/capture_io.py:1`; `kgme/daily_io.py:215`; `tests/test_capture.py:331` | The effects split, documented failure helper, and test classification remain. | Implemented. |
| F10 | blocking, resolved | `kgme/capture_fs.py:125`; `tests/test_capture_review.py:315` | Whole-file publication removes the partial-append mechanism. Both destination kinds retain interruption-before-publication regressions. | Implemented per the ruling. |
| F11 | cosmetic, resolved | `kgme/capture_io.py:245` | `write_announcement` names and documents its payload and ledger effects. | Implemented. |
| F12 | blocking, resolved | `kgme/capture_recover.py:91` | Recovery reads destination evidence and writes ledger outcomes only. | Resolved by removing the vault-write mechanism. |
| F13 | blocking | `kgme/capture_fs.py:129`; `kgme/capture_fs.py:143`; `docs/audit/2026-10-16-capture-and-daily.md:66` | The new tests preserve saves completed before the exchange, but the race remains after the displaced-byte check. A writer can open the original before the exchange, then write and close after that check. Cleanup unlinks the edited inode and capture records success. Ordinary scheduling between open, write, and close suffices. The report acknowledges this loss window; its approval-screen score is not an explicit boundary ruling. | Obtain the boundary ruling required by the previous finding, or protect against intervening writers. Add a regression that writes through the original descriptor after the displaced-byte check and requires preservation. |
| F14 | cosmetic, resolved | `jobs/capture/manifest.toml:11` | The manifest now describes `write_new`, `write_replaced`, and exchange rollback instead of `O_APPEND`. | Implemented. |
| F15 | blocking | `kgme/capture_fs.py:128`; `kgme/capture_fs.py:140`; `kgme/capture_recover.py:123` | Exception cleanup can delete an already completed edit independently of F13’s remaining race. After an editor saves and closes, the first exchange moves that edit to `temp`. If the displaced-file read raises, rollback fails, or execution is interrupted before validation, `keep` remains false and `finally` deletes the edited file. On an `OSError` path, settlement sees the intended destination hash and can return success despite the loss. | Preserve the displaced file whenever exchange or rollback state is uncertain, identify it in the failure record, and prevent successful settlement from concealing that uncertainty. Test failures after the first exchange and during rollback, with an edit completed beforehand. |
| F16 | cosmetic | `kgme/capture_fs.py:55` | `swap_names` changes filesystem state without ADR-015’s required effect prefix. | Rename it with a `write_*` or `run_*` prefix and update callers and tests. |
| F17 | cosmetic | `tests/test_capture_review.py:364` | The review test module has grown to 414 lines, beyond ADR-015’s approximately 300-line convention. | Split the regression groups along their existing responsibilities. |

## Verdict

BLOCK with 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`963cd8812994f29c`**, verified before and after inspection. No files were changed and no tests were run. The builder reports **325 passed, 10 deselected**, clean ruff, and **0 blocking** lint findings; these results were not independently executed.

Every ordinary acceptance item has test coverage: reminder creation, due resolution, ledger pairing, and printed output at `tests/test_capture.py:34`; friction formatting and prefix preservation at `:82`; daily prefix preservation at `:108`; cited daily sections and repeat-run inactivity at `tests/test_daily.py:50`; next-morning reminder and friction visibility at `tests/test_capture.py:317`. The last uses Thursday-to-Friday dates. The report explicitly acknowledges that its Friday live example would not show the reminder the following morning.

F13’s disposition supplies the required red command and symptom. Its new regressions address the original pre-publication save, but neither covers the remaining post-check write. F13 has now stood blocking for **2 consecutive cycles**, requiring an arbiter ruling under ADR-023 and the review-loop reader.

No dependencies were added. Added executable code contains no `TODO` or `shell=True`; subprocess arguments are lists. New production modules remain below 300 lines and carry purpose, input, output, and side-effect docstrings.

The requested reader remains absent under the reported tooling restriction, which is not counted against the diff. HANDOFF-0035’s **5 reminders, 5 tasks, 7 daily notes, and 10 friction entries** remain undemonstrated.
