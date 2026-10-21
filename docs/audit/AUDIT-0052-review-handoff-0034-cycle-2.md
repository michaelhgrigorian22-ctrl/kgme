---
id: AUDIT-0052
type: report
status: final
handoff: HANDOFF-0034
author: codex
source: inferred
sources: ["HANDOFF-0034", "staged diff sha256 dce616f881034734c063ce59423e66bdb0503e7212a1b0e56f0715309f02c22c"]
tier: 2
created: 2026-10-14T00:59:16-07:00
period: 2026-10-14
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F6, F11]
---

# Review of HANDOFF-0034, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `dce616f881034734c063ce59423e66bdb0503e7212a1b0e56f0715309f02c22c`. Verdict **BLOCK**: blocking 3, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/brief_reconcile.py:65](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:65) | The 3 symlink cases are addressed, but recovery still reads destinations without `places.allowed("read", destination)`. If a pending intent’s destination becomes blocklisted, reconciliation reads it and can record `ok` before the ordinary run checks permission. | Check current policy before recovery reads. Add a pending-intent canary whose destination is now forbidden, asserting that no bytes are read. |
| F2 | blocking, resolved | [kgme/ledger.py:234](/Users/michaelgrigorian/Projects/Automate/kgme/ledger.py:234), [kgme/brief_reconcile.py:54](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:54) | Payload bytes are verified against the recorded digest, and destinations must match the intent key. Altered, malformed and misdirected payloads have regression coverage. | No further change is required for this finding. |
| F3 | blocking, resolved | [kgme/brief_io.py:106](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:106) | Successful dry runs skip reconciliation. The added orphan test requires exactly 1 new note and leaves the intent open. | No further change is required. |
| F4 | blocking, resolved | [kgme/brief_read.py:135](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:135) | Historical ledger entries now require an `ok` outcome. The later-date regression covers an intent that never wrote; regeneration coverage retains history after cleaning. | No further change is required. |
| F5 | blocking, resolved | [kgme/brief_io.py:43](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:43) | Replacement now follows complete writing, `fsync` and size verification. The regression injects writes of only 7 bytes and checks the persisted hash. | No further change is required. |
| F6 | blocking | [kgme/brief_read.py:177](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:177), [kgme/brief_io.py:130](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:130) | Identity parsing still escapes classification. An existing brief containing `# Brief` without frontmatter, or malformed YAML, raises `ValueError`; the caller catches only `clean_fs.Refused`. That run records no intent/outcome. The added test covers missing fields in parseable YAML only. | Convert frontmatter parsing failures into classified refusals. Test both absent frontmatter and malformed YAML, preserving the existing artefact. |
| F7 | blocking, resolved | [kgme/brief_io.py:99](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:99) | Canonical calendar-date validation precedes job effects. All 5 invalid-date cases require exit 2 and no ledger events. | No further change is required. |
| F8 | blocking, resolved | [kgme/brief_read.py:115](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:115) | Hashes now use original bytes, with strict UTF-8 decoding before rendering. CRLF and invalid UTF-8 have regression coverage. | No further change is required. |
| F9 | blocking, resolved | [kgme/brief.py:101](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:101) | Ordering uses UTC instants; grouping and display use the configured timezone. The regression covers mixed offsets and a midnight boundary. | No further change is required. |
| F10 | cosmetic, resolved | [kgme/brief_reconcile.py:43](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:43), [kgme/brief_io.py:70](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:70) | All 3 previously cited effect functions were removed or replaced with correctly prefixed functions. | No further change is required for those functions. |
| F11 | blocking | [kgme/brief_read.py:91](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:91) | Input discovery silently loses unreadable subtrees. Python 3.13’s `rglob` suppresses directory-scan errors, so 1 unreadable directory containing open tasks is omitted while other inputs allow a successful, incomplete brief. The unreadable-file test does not cover discovery failures. | Use enumeration that reports scan errors and routes them to a blocking refusal. Add an unreadable-directory regression requiring no artefact replacement. |
| F12 | cosmetic | [kgme/ledger.py:189](/Users/michaelgrigorian/Projects/Automate/kgme/ledger.py:189) | The new `ok_intents` function reads ledger files without ADR-015’s effect prefix. | Rename it `read_ok_intents` and update callers. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/brief_reconcile.py:65](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:65) | The 3 symlink cases are addressed, but recovery still reads destinations without `places.allowed("read", destination)`. If a pending intent’s destination becomes blocklisted, reconciliation reads it and can record `ok` before the ordinary run checks permission. | Check current policy before recovery reads. Add a pending-intent canary whose destination is now forbidden, asserting that no bytes are read. |
| F2 | blocking, resolved | [kgme/ledger.py:234](/Users/michaelgrigorian/Projects/Automate/kgme/ledger.py:234), [kgme/brief_reconcile.py:54](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:54) | Payload bytes are verified against the recorded digest, and destinations must match the intent key. Altered, malformed and misdirected payloads have regression coverage. | No further change is required for this finding. |
| F3 | blocking, resolved | [kgme/brief_io.py:106](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:106) | Successful dry runs skip reconciliation. The added orphan test requires exactly 1 new note and leaves the intent open. | No further change is required. |
| F4 | blocking, resolved | [kgme/brief_read.py:135](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:135) | Historical ledger entries now require an `ok` outcome. The later-date regression covers an intent that never wrote; regeneration coverage retains history after cleaning. | No further change is required. |
| F5 | blocking, resolved | [kgme/brief_io.py:43](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:43) | Replacement now follows complete writing, `fsync` and size verification. The regression injects writes of only 7 bytes and checks the persisted hash. | No further change is required. |
| F6 | blocking | [kgme/brief_read.py:177](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:177), [kgme/brief_io.py:130](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:130) | Identity parsing still escapes classification. An existing brief containing `# Brief` without frontmatter, or malformed YAML, raises `ValueError`; the caller catches only `clean_fs.Refused`. That run records no intent/outcome. The added test covers missing fields in parseable YAML only. | Convert frontmatter parsing failures into classified refusals. Test both absent frontmatter and malformed YAML, preserving the existing artefact. |
| F7 | blocking, resolved | [kgme/brief_io.py:99](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:99) | Canonical calendar-date validation precedes job effects. All 5 invalid-date cases require exit 2 and no ledger events. | No further change is required. |
| F8 | blocking, resolved | [kgme/brief_read.py:115](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:115) | Hashes now use original bytes, with strict UTF-8 decoding before rendering. CRLF and invalid UTF-8 have regression coverage. | No further change is required. |
| F9 | blocking, resolved | [kgme/brief.py:101](/Users/michaelgrigorian/Projects/Automate/kgme/brief.py:101) | Ordering uses UTC instants; grouping and display use the configured timezone. The regression covers mixed offsets and a midnight boundary. | No further change is required. |
| F10 | cosmetic, resolved | [kgme/brief_reconcile.py:43](/Users/michaelgrigorian/Projects/Automate/kgme/brief_reconcile.py:43), [kgme/brief_io.py:70](/Users/michaelgrigorian/Projects/Automate/kgme/brief_io.py:70) | All 3 previously cited effect functions were removed or replaced with correctly prefixed functions. | No further change is required for those functions. |
| F11 | blocking | [kgme/brief_read.py:91](/Users/michaelgrigorian/Projects/Automate/kgme/brief_read.py:91) | Input discovery silently loses unreadable subtrees. Python 3.13’s `rglob` suppresses directory-scan errors, so 1 unreadable directory containing open tasks is omitted while other inputs allow a successful, incomplete brief. The unreadable-file test does not cover discovery failures. | Use enumeration that reports scan errors and routes them to a blocking refusal. Add an unreadable-directory regression requiring no artefact replacement. |
| F12 | cosmetic | [kgme/ledger.py:189](/Users/michaelgrigorian/Projects/Automate/kgme/ledger.py:189) | The new `ok_intents` function reads ledger files without ADR-015’s effect prefix. | Rename it `read_ok_intents` and update callers. |

## Verdict

BLOCK: 3 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`dce616f881034734`**, verified against the patch and staged diff. No files were modified and no tests were run. The builder reports 242 passing tests and 20 pre-fix failures; those execution results were not independently reproduced.

All 5 acceptance scenarios have classified tests in [tests/test_brief.py](/Users/michaelgrigorian/Projects/Automate/tests/test_brief.py). Interruption coverage plants orphan states rather than issuing a live `SIGKILL`. The existing daily template supplies the third requested template.

Changed production modules remain below 300 lines and carry the required module documentation. The diff adds no dependencies, subprocess calls, `shell=True`, or code TODOs.
