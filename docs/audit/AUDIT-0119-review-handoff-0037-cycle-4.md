---
id: AUDIT-0119
type: report
status: final
handoff: HANDOFF-0037
author: codex
source: inferred
sources: ["HANDOFF-0037", "staged diff sha256 03ef5664f524bd8dad57a2e1052d5f2ffbc2a51befd826e2ad54dffa0983b094"]
tier: 2
created: 2026-10-25T22:53:50-07:00
period: 2026-10-25
review_cycle: 4
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F9]
---

# Review of HANDOFF-0037, cycle 4

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `03ef5664f524bd8dad57a2e1052d5f2ffbc2a51befd826e2ad54dffa0983b094`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:57 | The 50-event boundary now has a regression and stated browser evidence. The reader and README warning exist in the checkout, contrary to the report’s draft-only claims. Dock launch and 1 evening of use remain unverified. | Correct the report and keep HANDOFF-0037 open until the remaining evidence is recorded. |
| F2 | advisory, resolved | cockpit/render.py:11 | The approved revision comparison records 255 comparisons at 49 clocks, with 0 disagreements. | No further change is required. |
| F3 | blocking, resolved | cockpit/render.py:148 | Open runs refresh independently of returned rows. The regression covers both sides of the 3-minute quiet threshold and excludes a closed run. | No further change is required. |
| F4 | cosmetic, resolved | cockpit/server.py:134 | File reads delegate to documented `read_file`; the handler constructor also has a docstring. | No further change is required. |
| F5 | advisory, resolved | tests/station_equivalence.py:137 | The comparison reads the selected revision’s floor and fixtures and rejects 0 comparisons. | No further change is required. |
| F6 | cosmetic, resolved | tests/station_equivalence.py:130 | The prerequisite now checks exact equality with Node `v25.9.0`. | No further change is required. |
| F7 | blocking, resolved | cockpit/index.html:241 | A trace row hides only while its parent remains held. Parents outside the initial window or evicted from memory therefore no longer hide their orphaned rows. | No further functional change is required for this finding; see F13 for regression evidence. |
| F8 | blocking, resolved | cockpit/render.py:135 | Cursor polling now returns the oldest next batch. The regression covers an outcome followed by 55 events and verifies delivery without gaps. | No further change is required. |
| F9 | blocking | cockpit/index.html:401 | Run selection remains invisible when event detail is open. With 2 open runs and detail showing a closed run’s event, `a` activates the runs pane, but `drawRight` returns through the detail branch. `j` changes the hidden selection and `Enter` applies it. The in-memory reproduction recorded 0 runs-pane renders across those 3 keys. | Make activating the runs pane display it, including from event detail. Cover both the `a` key and runs button with a regression using 2 open runs and a selected closed-run event. |
| F10 | blocking, resolved | cockpit/index.html:409 | Detail now renders the supplied hash, preserves null, and distinguishes a missing field. The report records 1 non-null browser example and corrects its earlier claim. | No further change is required. |
| F11 | blocking, resolved | cockpit/index.html:465 | The amendment’s conditions are satisfied: `w` remains unbound, the map names HANDOFF-0058, and the report names the amendment and follow-up. HANDOFF-0058’s acceptance specifies the 3-surface binding. | No further change is required under HANDOFF-0037. |
| F12 | cosmetic | cockpit/index.html:207 | The page remains 541 lines, with mixed effects and logic and missing effect names/contracts. The stated deferral rationale is incomplete: naming and separating inline functions requires neither additional routes nor a build step. | Retain the weekly-review item; separate and document inline effects, and explicitly reconcile the size exception. |
| F13 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:81 | F7, F9 and F10 cite browser checks without the review loop’s required reproducible red commands and recorded pre-fix failures. F7 also lacks explicit eviction-regression evidence. | Supply repeatable regressions and pre-fix evidence, or explicitly record why a deterministic command is unavailable. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:57 | The 50-event boundary now has a regression and stated browser evidence. The reader and README warning exist in the checkout, contrary to the report’s draft-only claims. Dock launch and 1 evening of use remain unverified. | Correct the report and keep HANDOFF-0037 open until the remaining evidence is recorded. |
| F2 | advisory, resolved | cockpit/render.py:11 | The approved revision comparison records 255 comparisons at 49 clocks, with 0 disagreements. | No further change is required. |
| F3 | blocking, resolved | cockpit/render.py:148 | Open runs refresh independently of returned rows. The regression covers both sides of the 3-minute quiet threshold and excludes a closed run. | No further change is required. |
| F4 | cosmetic, resolved | cockpit/server.py:134 | File reads delegate to documented `read_file`; the handler constructor also has a docstring. | No further change is required. |
| F5 | advisory, resolved | tests/station_equivalence.py:137 | The comparison reads the selected revision’s floor and fixtures and rejects 0 comparisons. | No further change is required. |
| F6 | cosmetic, resolved | tests/station_equivalence.py:130 | The prerequisite now checks exact equality with Node `v25.9.0`. | No further change is required. |
| F7 | blocking, resolved | cockpit/index.html:241 | A trace row hides only while its parent remains held. Parents outside the initial window or evicted from memory therefore no longer hide their orphaned rows. | No further functional change is required for this finding; see F13 for regression evidence. |
| F8 | blocking, resolved | cockpit/render.py:135 | Cursor polling now returns the oldest next batch. The regression covers an outcome followed by 55 events and verifies delivery without gaps. | No further change is required. |
| F9 | blocking | cockpit/index.html:401 | Run selection remains invisible when event detail is open. With 2 open runs and detail showing a closed run’s event, `a` activates the runs pane, but `drawRight` returns through the detail branch. `j` changes the hidden selection and `Enter` applies it. The in-memory reproduction recorded 0 runs-pane renders across those 3 keys. | Make activating the runs pane display it, including from event detail. Cover both the `a` key and runs button with a regression using 2 open runs and a selected closed-run event. |
| F10 | blocking, resolved | cockpit/index.html:409 | Detail now renders the supplied hash, preserves null, and distinguishes a missing field. The report records 1 non-null browser example and corrects its earlier claim. | No further change is required. |
| F11 | advisory, resolved | cockpit/index.html:465 | The amendment’s conditions are satisfied: `w` remains unbound, the map names HANDOFF-0058, and the report names the amendment and follow-up. HANDOFF-0058’s acceptance specifies the 3-surface binding. | No further change is required under HANDOFF-0037. |
| F12 | cosmetic | cockpit/index.html:207 | The page remains 541 lines, with mixed effects and logic and missing effect names/contracts. The stated deferral rationale is incomplete: naming and separating inline functions requires neither additional routes nor a build step. | Retain the weekly-review item; separate and document inline effects, and explicitly reconcile the size exception. |
| F13 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:81 | F7, F9 and F10 cite browser checks without the review loop’s required reproducible red commands and recorded pre-fix failures. F7 also lacks explicit eviction-regression evidence. | Supply repeatable regressions and pre-fix evidence, or explicitly record why a deterministic command is unavailable. |

## Verdict

BLOCK with 1 blocking finding open.

## Notes

Reviewed SHA-256 prefix **`03ef5664f524bd8d`**. The 45-line patch changes 2 files; earlier dispositions were checked against surrounding implementation and recorded evidence.

No files were changed. No pytest or `make check` was run. The existing cycle-4 log reports **605 passed**, **42 deselected**, and **0 blocking lint findings**. F9 was reproduced using an in-memory Node probe with stubbed DOM helpers, not a live browser. Sandbox tooling limitations were not counted against the diff.
