---
id: AUDIT-0096
type: report
status: final
handoff: HANDOFF-0056
author: codex
source: inferred
sources: ["HANDOFF-0056", "staged diff sha256 a13d2453b38cf8377299e1d7a6601fc1943c7ea27bbdc300c27eb31fa24c63cf"]
tier: 2
created: 2026-10-22T02:02:52-07:00
period: 2026-10-22
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6]
---

# Review of HANDOFF-0056, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `a13d2453b38cf8377299e1d7a6601fc1943c7ea27bbdc300c27eb31fa24c63cf`. Verdict **BLOCK**: blocking 6, transient 0, cosmetic 0, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/atlas_read.py:190 | Tier 1 exclusion happens after `read_sources` has read the files, including the synthetic `kgme/secret/notes.py` fixture. Additionally, `read_excluded` excludes neither a base equal to a Tier 1 root nor a base inside one. | Validate the base before traversal and filter forbidden paths before reading content. Test that excluded files are never opened and that bases inside Tier 1 are refused. |
| F2 | blocking | kgme/atlas_read.py:203 | The title echoes unfiltered arguments. `--around memory/example.md` therefore names a forbidden path even when every node is filtered, violating What §1. | Build the title from validated, permitted paths. Test the entire rendered text for excluded paths, including its header. |
| F3 | blocking | kgme/atlas_slice.py:95 | Atlas adds module-to-test backlinks at `atlas.py:179`. This code interprets those backlinks as imports: `tests/test_ledger_concurrency.py` is reported as “imported by” `kgme/ledger.py`, and a test seed ranks its dependencies as importers. | Preserve actual import direction separately from atlas backlinks. Add a graph-builder regression covering a test seed and its imported module. |
| F4 | blocking | kgme/atlas_read.py:192 | The reused graph does not connect ADRs to file paths they name. For example, ADR-023:44 names `kgme/review.py`, but that relationship cannot reach its slice. Handoffs similarly contribute only their Outputs references. This misses document neighbours promised by What §1. | Derive document-to-file references from the permitted sources, preserving their relationship type. Test an ADR reference and a handoff reference outside Outputs. |
| F5 | blocking | kgme/atlas_slice.py:160 | The header and closing line are emitted even when they exceed the budget. A budget of 1 necessarily overflows; budget 0 silently becomes the configured default at `atlas_read.py:202`. | Validate budgets, distinguish zero from an omitted value, and account for the complete rendered header and footer. Reject budgets too small for required metadata. |
| F6 | blocking | kgme/cli.py:356 | Slice dispatch ignores `args.dry_run`. Consequently, `atlas --around kgme/ledger.py --dry-run --out existing.txt` reaches `write_text` and overwrites the file despite the flag’s “write nothing” contract. | Honour dry-run in slice dispatch or reject this combination before writing. Add a regression asserting unchanged destination bytes. |
| F7 | advisory | kgme/atlas_slice.py:83 | Named-file seeds precede folder-derived seeds, contrary to What §1’s single path ordering within each rank. The report acknowledges this deliberate deviation, but the tests do not establish its intended ordering. | Reconcile the ordering contract and add an explicit mixed file/folder seed test. |
| F8 | advisory | kgme/session.py:119 | ADR-015’s approximate 300-line target is exceeded: `session.py` reaches 360 lines, `cli.py` 409, and `test_session.py` 356. The new public `read_slice` also lacks a return annotation. | Add the return annotation and isolate the new carry responsibility when addressing module size, keeping restructuring scoped. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/atlas_read.py:190 | Tier 1 exclusion happens after `read_sources` has read the files, including the synthetic `kgme/secret/notes.py` fixture. Additionally, `read_excluded` excludes neither a base equal to a Tier 1 root nor a base inside one. | Validate the base before traversal and filter forbidden paths before reading content. Test that excluded files are never opened and that bases inside Tier 1 are refused. |
| F2 | blocking | kgme/atlas_read.py:203 | The title echoes unfiltered arguments. `--around memory/example.md` therefore names a forbidden path even when every node is filtered, violating What §1. | Build the title from validated, permitted paths. Test the entire rendered text for excluded paths, including its header. |
| F3 | blocking | kgme/atlas_slice.py:95 | Atlas adds module-to-test backlinks at `atlas.py:179`. This code interprets those backlinks as imports: `tests/test_ledger_concurrency.py` is reported as “imported by” `kgme/ledger.py`, and a test seed ranks its dependencies as importers. | Preserve actual import direction separately from atlas backlinks. Add a graph-builder regression covering a test seed and its imported module. |
| F4 | blocking | kgme/atlas_read.py:192 | The reused graph does not connect ADRs to file paths they name. For example, ADR-023:44 names `kgme/review.py`, but that relationship cannot reach its slice. Handoffs similarly contribute only their Outputs references. This misses document neighbours promised by What §1. | Derive document-to-file references from the permitted sources, preserving their relationship type. Test an ADR reference and a handoff reference outside Outputs. |
| F5 | blocking | kgme/atlas_slice.py:160 | The header and closing line are emitted even when they exceed the budget. A budget of 1 necessarily overflows; budget 0 silently becomes the configured default at `atlas_read.py:202`. | Validate budgets, distinguish zero from an omitted value, and account for the complete rendered header and footer. Reject budgets too small for required metadata. |
| F6 | blocking | kgme/cli.py:356 | Slice dispatch ignores `args.dry_run`. Consequently, `atlas --around kgme/ledger.py --dry-run --out existing.txt` reaches `write_text` and overwrites the file despite the flag’s “write nothing” contract. | Honour dry-run in slice dispatch or reject this combination before writing. Add a regression asserting unchanged destination bytes. |
| F7 | advisory | kgme/atlas_slice.py:83 | Named-file seeds precede folder-derived seeds, contrary to What §1’s single path ordering within each rank. The report acknowledges this deliberate deviation, but the tests do not establish its intended ordering. | Reconcile the ordering contract and add an explicit mixed file/folder seed test. |
| F8 | advisory | kgme/session.py:119 | ADR-015’s approximate 300-line target is exceeded: `session.py` reaches 360 lines, `cli.py` 409, and `test_session.py` 356. The new public `read_slice` also lacks a return annotation. | Add the return annotation and isolate the new carry responsibility when addressing module size, keeping restructuring scoped. |

## Verdict

BLOCK with 6 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`a13d2453b38cf837`**, verified before and after inspection. No files were modified and no tests were executed.

The supplied check log reports **506 passed, 34 deselected**. The first 6 acceptance bullets have automated coverage, with the gaps above; the seventh, live skill discovery in `work`, remains explicitly pending human installation. The dry-run test omits the skill, while a separate launch test checks all 3 carried parts.

The baseline’s first-review counts, **7 and 8**, match AUDIT-0076 and AUDIT-0084. Its orientation measurements use handoff-specific windows within 1 long session, a limitation to preserve when making the weekly comparison.
