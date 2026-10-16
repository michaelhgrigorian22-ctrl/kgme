---
id: AUDIT-0051
type: report
status: final
handoff: HANDOFF-0034
author: codex
source: inferred
sources: ["HANDOFF-0034", "staged diff sha256 8e282a65604fab715ec03837dca6ef20de62209fe8a5403af8d1d8cc90274677"]
tier: 2
created: 2026-10-14T00:46:06-07:00
period: 2026-10-14
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7, F8, F9]
---

# Review of HANDOFF-0034, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `8e282a65604fab715ec03837dca6ef20de62209fe8a5403af8d1d8cc90274677`. Verdict **BLOCK**: blocking 9, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/brief_read.py:139](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:139), [kgme/brief_io.py:28](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:28) | Auxiliary I/O bypasses policy checks. Identity loading follows an existing brief symlink before checking permission; reconciliation reads payloads and destinations unchecked; payload creation follows scratch-directory symlinks. Pre-existing links can therefore cause forbidden reads or writes outside scratch, without any concurrent directory swap. | Check containment and existing symlinks before every auxiliary read/write. Add canaries covering the output, recovery payload, and scratch ancestors. |
| F2 | blocking | [kgme/brief_io.py:68](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:68) | Recovery trusts payload JSON without verifying `payload_sha256`. Changing its destination or expected hash can produce a false successful reconciliation. The test explicitly supplies 64 zeroes as the payload hash and expects success. | Verify payload bytes against the recorded digest before using them; validate destination against the intent key. Test altered and malformed payloads, requiring a classified refusal. |
| F3 | blocking | [kgme/brief_io.py:137](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:137) | Reconciliation runs before the dry-run branch. With 1 orphan, a successful dry run appends an outcome plus its note and changes recovery state, violating the exactly-one-note acceptance requirement. The current test starts with an empty ledger. | Keep dry-run reconciliation observational. Test a pending orphan and require exactly 1 new note with the orphan unchanged. |
| F4 | blocking | [kgme/brief_read.py:125](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:125) | Every write intent advances the previous-brief cutoff, including failed attempts. If October 7 dies before writing and October 8 runs next, October 7 becomes the cutoff despite never producing a brief; earlier friction entries disappear. | Derive historical brief dates from successful or successfully reconciled writes, while retaining history after cleaning. Test recovery on a later date after an unwritten intent. |
| F5 | blocking | [kgme/brief_io.py:41](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:41) | `os.write`’s byte count is ignored. A short write replaces the destination with truncated content, then records `status: ok` and the intended full-content hash. | Require all bytes to be written before replacement. Inject a short write and verify either complete persistence or a classified failure that preserves the previous artefact. |
| F6 | blocking | [kgme/brief_io.py:143](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:143), [kgme/brief_io.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:197) | Read, identity-parse and write exceptions escape without classified failure outcomes. A failed input read can leave no event; a failed replacement leaves an orphan. Explicit output-validation and permission refusals also emit only notes. This breaks ADR-015’s failure-recording contract for normal runs. | Route normal-run failures through a consistent classified intent/outcome path. Test input-read, malformed-identity and replacement failures. |
| F7 | blocking | [kgme/brief_io.py:140](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:140) | `--date` is never validated before becoming paths, headings and ledger keys. On a seeded vault, `2026-02-30` passes output validation and produces an impossible-date brief; path-shaped arguments are also accepted. | Require a real, canonical `YYYY-MM-DD` before effects. Test impossible dates, arbitrary text, absolute paths and traversal. |
| F8 | blocking | [kgme/brief_read.py:104](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:104) | Input hashes describe decoded, normalized text rather than file bytes. CRLF becomes LF, and invalid UTF-8 is replaced, so the reported SHA-256 can disagree with the named input file and conceal decoding damage. | Hash original bytes, then decode strictly for validation/rendering. Cover CRLF input and invalid UTF-8. |
| F9 | blocking | [kgme/brief.py:78](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:78), [kgme/brief.py:146](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:146) | Due instants are compared as strings and their offsets disappear in rendering. On the same date, `17:00+02:00` precedes `09:00-07:00` by 1 hour, but this sort reverses them. Raw date-prefix grouping also misclassifies reminders across local midnight. | Sort aware instants chronologically and use an explicit brief timezone for day grouping and display. Add mixed-offset and midnight-boundary cases. |
| F10 | cosmetic | [kgme/brief_io.py:61](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:61) | The 3 effectful functions `_intended`, `reconcile_open_intents` and `_refuse` lack ADR-015’s effect prefixes, although their module separation is appropriate. | Rename them consistently with `read_*`, `run_*` and `write_*`. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/brief_read.py:139](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:139), [kgme/brief_io.py:28](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:28) | Auxiliary I/O bypasses policy checks. Identity loading follows an existing brief symlink before checking permission; reconciliation reads payloads and destinations unchecked; payload creation follows scratch-directory symlinks. Pre-existing links can therefore cause forbidden reads or writes outside scratch, without any concurrent directory swap. | Check containment and existing symlinks before every auxiliary read/write. Add canaries covering the output, recovery payload, and scratch ancestors. |
| F2 | blocking | [kgme/brief_io.py:68](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:68) | Recovery trusts payload JSON without verifying `payload_sha256`. Changing its destination or expected hash can produce a false successful reconciliation. The test explicitly supplies 64 zeroes as the payload hash and expects success. | Verify payload bytes against the recorded digest before using them; validate destination against the intent key. Test altered and malformed payloads, requiring a classified refusal. |
| F3 | blocking | [kgme/brief_io.py:137](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:137) | Reconciliation runs before the dry-run branch. With 1 orphan, a successful dry run appends an outcome plus its note and changes recovery state, violating the exactly-one-note acceptance requirement. The current test starts with an empty ledger. | Keep dry-run reconciliation observational. Test a pending orphan and require exactly 1 new note with the orphan unchanged. |
| F4 | blocking | [kgme/brief_read.py:125](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:125) | Every write intent advances the previous-brief cutoff, including failed attempts. If October 7 dies before writing and October 8 runs next, October 7 becomes the cutoff despite never producing a brief; earlier friction entries disappear. | Derive historical brief dates from successful or successfully reconciled writes, while retaining history after cleaning. Test recovery on a later date after an unwritten intent. |
| F5 | blocking | [kgme/brief_io.py:41](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:41) | `os.write`’s byte count is ignored. A short write replaces the destination with truncated content, then records `status: ok` and the intended full-content hash. | Require all bytes to be written before replacement. Inject a short write and verify either complete persistence or a classified failure that preserves the previous artefact. |
| F6 | blocking | [kgme/brief_io.py:143](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:143), [kgme/brief_io.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:197) | Read, identity-parse and write exceptions escape without classified failure outcomes. A failed input read can leave no event; a failed replacement leaves an orphan. Explicit output-validation and permission refusals also emit only notes. This breaks ADR-015’s failure-recording contract for normal runs. | Route normal-run failures through a consistent classified intent/outcome path. Test input-read, malformed-identity and replacement failures. |
| F7 | blocking | [kgme/brief_io.py:140](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:140) | `--date` is never validated before becoming paths, headings and ledger keys. On a seeded vault, `2026-02-30` passes output validation and produces an impossible-date brief; path-shaped arguments are also accepted. | Require a real, canonical `YYYY-MM-DD` before effects. Test impossible dates, arbitrary text, absolute paths and traversal. |
| F8 | blocking | [kgme/brief_read.py:104](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:104) | Input hashes describe decoded, normalized text rather than file bytes. CRLF becomes LF, and invalid UTF-8 is replaced, so the reported SHA-256 can disagree with the named input file and conceal decoding damage. | Hash original bytes, then decode strictly for validation/rendering. Cover CRLF input and invalid UTF-8. |
| F9 | blocking | [kgme/brief.py:78](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:78), [kgme/brief.py:146](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:146) | Due instants are compared as strings and their offsets disappear in rendering. On the same date, `17:00+02:00` precedes `09:00-07:00` by 1 hour, but this sort reverses them. Raw date-prefix grouping also misclassifies reminders across local midnight. | Sort aware instants chronologically and use an explicit brief timezone for day grouping and display. Add mixed-offset and midnight-boundary cases. |
| F10 | cosmetic | [kgme/brief_io.py:61](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:61) | The 3 effectful functions `_intended`, `reconcile_open_intents` and `_refuse` lack ADR-015’s effect prefixes, although their module separation is appropriate. | Rename them consistently with `read_*`, `run_*` and `write_*`. |

## Verdict

BLOCK with 9 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`8e282a65604fab71`**, matching `review.sha`.

All 5 acceptance items have classed tests. The interruption test plants orphan states rather than performing SIGKILL; the dry-run test covers only an empty ledger. Reported test timings and live runs were read as builder evidence, not independently reproduced.

New modules remain below 300 lines and carry the required module documentation. No dependency additions, TODOs, `shell=True`, or subprocess calls appear in the patch.

No pytest or job execution was performed, and no files were changed. Sandbox cache warnings are tooling limitations, not findings against the diff.
