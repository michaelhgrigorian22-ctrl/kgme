---
id: AUDIT-0060
type: report
status: final
handoff: HANDOFF-0050
author: codex
source: inferred
sources: ["HANDOFF-0050", "staged diff sha256 c3772db7dee65a8466b05a4c281ad044b1598cd52c1cb1ea693cc7f537f4533b"]
tier: 2
created: 2026-10-16T14:59:36-07:00
period: 2026-10-16
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F2, F3, F10]
---

# Review of HANDOFF-0050, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `c3772db7dee65a8466b05a4c281ad044b1598cd52c1cb1ea693cc7f537f4533b`. Verdict **BLOCK**: blocking 3, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/capture_fs.py:94` | Complete files are now published through a non-replacing hard link. The regression test interrupts the temporary-file write and checks successful recovery. | Implemented and covered. |
| F2 | blocking | `kgme/capture_record.py:112`; `kgme/daily_io.py:127` | Daily now reconciles captures, but an interrupted held capture still disappears from the draft if its scratch payload was cleaned. Reconciliation records an error despite the complete words remaining in the durable summary; `read_held` excludes it, and daily creates the note without those words. The regression test retains the payload. | Recover validated held words independently of disposable scratch, or stop drafting until the capture is resolved. Test an unanswered held intent with its payload removed. |
| F3 | blocking | `kgme/capture_io.py:114`; `kgme/capture_record.py:134` | The missing-outcome retry is fixed, but a failure after writing still permits duplication. If `fsync` raises after the append or publication, the failure handler closes the intent with an error. Subsequent reconciliation ignores that closed intent, and `read_done` accepts only successful outcomes, so retry writes again. | Check prior attempted writes against their byte evidence before replaying, including attempts closed with errors. Test post-write failures for creation and append. |
| F4 | blocking, resolved | `kgme/capture_record.py:109` | Recovery reads hash-bound payload metadata instead of the redacted summary. The regression test covers a 45-character filename stem. | Implemented and covered. |
| F5 | blocking, resolved | `kgme/daily.py:157` | Unrelated capture successes no longer resolve failures merely because they share a job. The regression test verifies the refused reminder stays open. | Implemented and covered. |
| F6 | blocking, resolved | `kgme/brief_read.py:108` | The brief reads the preceding daily note when today’s note is absent. The integration test checks the evening’s captured words appear the following morning. | Implemented and covered. |
| F7 | blocking, resolved | `jobs/capture/run.py:22`; `jobs/daily/run.py:22` | Both job entry points and CLI commands accept `--dry-run`. The regression test checks unchanged vault bytes and preview output. | Implemented and covered. |
| F8 | blocking, resolved | `kgme/capture_record.py:68`; `tests/test_capture_review.py:194` | Payloads retain exact written bytes, and the reconstruction test covers both jobs and capture text exceeding the summary limit. ADR-019 explicitly permits these replay payloads to be disposable. | Implemented and covered within ADR-019’s retention policy. |
| F9 | cosmetic, resolved | `kgme/capture_io.py:1`; `kgme/daily_io.py:205`; `tests/test_capture.py:318` | The effects module was split, the failure helper was renamed and documented, and the structural test now carries its class marker. | Implemented. |
| F10 | blocking | `kgme/capture_fs.py:81`; `kgme/capture_record.py:124` | An interruption during an append leaves a partial line. Reconciliation treats its hash mismatch as “not written”; retry appends a complete line after the fragment. A split UTF-8 character can permanently invalidate the file. The interruption tests cover publication and completed appends, not partial appends. | Detect partial spans and recover only a verified missing suffix; stop when recovery is ambiguous. Test interruption during an append, including a split UTF-8 character, while preserving the original prefix. |
| F11 | cosmetic | `kgme/capture_io.py:222` | The nested `announce` helper writes a payload and ledger intent but lacks ADR-015’s effect prefix and a docstring. | Rename it `write_announcement` and document its inputs, output, and effects. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/capture_fs.py:94` | Complete files are now published through a non-replacing hard link. The regression test interrupts the temporary-file write and checks successful recovery. | Implemented and covered. |
| F2 | blocking | `kgme/capture_record.py:112`; `kgme/daily_io.py:127` | Daily now reconciles captures, but an interrupted held capture still disappears from the draft if its scratch payload was cleaned. Reconciliation records an error despite the complete words remaining in the durable summary; `read_held` excludes it, and daily creates the note without those words. The regression test retains the payload. | Recover validated held words independently of disposable scratch, or stop drafting until the capture is resolved. Test an unanswered held intent with its payload removed. |
| F3 | blocking | `kgme/capture_io.py:114`; `kgme/capture_record.py:134` | The missing-outcome retry is fixed, but a failure after writing still permits duplication. If `fsync` raises after the append or publication, the failure handler closes the intent with an error. Subsequent reconciliation ignores that closed intent, and `read_done` accepts only successful outcomes, so retry writes again. | Check prior attempted writes against their byte evidence before replaying, including attempts closed with errors. Test post-write failures for creation and append. |
| F4 | blocking, resolved | `kgme/capture_record.py:109` | Recovery reads hash-bound payload metadata instead of the redacted summary. The regression test covers a 45-character filename stem. | Implemented and covered. |
| F5 | blocking, resolved | `kgme/daily.py:157` | Unrelated capture successes no longer resolve failures merely because they share a job. The regression test verifies the refused reminder stays open. | Implemented and covered. |
| F6 | blocking, resolved | `kgme/brief_read.py:108` | The brief reads the preceding daily note when today’s note is absent. The integration test checks the evening’s captured words appear the following morning. | Implemented and covered. |
| F7 | blocking, resolved | `jobs/capture/run.py:22`; `jobs/daily/run.py:22` | Both job entry points and CLI commands accept `--dry-run`. The regression test checks unchanged vault bytes and preview output. | Implemented and covered. |
| F8 | blocking, resolved | `kgme/capture_record.py:68`; `tests/test_capture_review.py:194` | Payloads retain exact written bytes, and the reconstruction test covers both jobs and capture text exceeding the summary limit. ADR-019 explicitly permits these replay payloads to be disposable. | Implemented and covered within ADR-019’s retention policy. |
| F9 | cosmetic, resolved | `kgme/capture_io.py:1`; `kgme/daily_io.py:205`; `tests/test_capture.py:318` | The effects module was split, the failure helper was renamed and documented, and the structural test now carries its class marker. | Implemented. |
| F10 | blocking | `kgme/capture_fs.py:81`; `kgme/capture_record.py:124` | An interruption during an append leaves a partial line. Reconciliation treats its hash mismatch as “not written”; retry appends a complete line after the fragment. A split UTF-8 character can permanently invalidate the file. The interruption tests cover publication and completed appends, not partial appends. | Detect partial spans and recover only a verified missing suffix; stop when recovery is ambiguous. Test interruption during an append, including a split UTF-8 character, while preserving the original prefix. |
| F11 | cosmetic | `kgme/capture_io.py:222` | The nested `announce` helper writes a payload and ledger intent but lacks ADR-015’s effect prefix and a docstring. | Rename it `write_announcement` and document its inputs, output, and effects. |

## Verdict

BLOCK with 3 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`c3772db7dee65a84`**, verified again after inspection. No files were modified and no tests were run. The builder reports **315 passed, 10 deselected**; that result was not independently executed.

The ordinary acceptance items have tests: reminder creation and due resolution, ledger pairing, printed output, friction formatting, append-prefix preservation, cited daily sections, repeat-run inactivity, and next-morning visibility. The reminder visibility test uses Thursday-to-Friday dates; the report explicitly acknowledges that its Friday live capture would not appear the next morning.

No dependencies were added, and no added `TODO` or `shell=True` was found. The requested reader remains absent under the reported tooling restriction, which is not counted against this diff. The real HANDOFF-0035 seeding targets remain undemonstrated.
