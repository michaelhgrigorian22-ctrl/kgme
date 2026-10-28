---
id: AUDIT-CDH-0019-CHIP-BUDGET
type: report
created: 2026-10-27T22:56:00-07:00
author: codex
source: inferred
sources: [CDH-0019, AUDIT-CDH-0031-REVIEW, AUDIT-CDH-0031]
tier: 2
status: final
handoff: CDH-0019
period: "2026-10-27"
reviewed_sha: 002db55
---

# CW40: restore the room-chip budget

CW40 is repaired in 1 CDH-0019 cycle from `002db55`: chip overlaps measure **0 / 0 / 0** at 400 × 700, 800 × 600 and 1440 × 900 using the review's `19:45:00` replay snapshot and unchanged default camera. This is builder verification; Cowork's native pass remains pending. No queue row is taken and no canvas approval is recorded.

The station changes exactly 2 declarations in `.chip-room`: `gap:4px` becomes `gap:1px`, and `padding:8px` becomes `padding:4px`. The 5 expanded chips measure 56.921875 px high, and the 2 compact chips measure 39.984375 px, against 70.921875 / 50.984375 px before. A scratch assertion verifies every other source byte is identical to `002db55`. The 4 px inset already belongs to the precision test's compact-row allowance; the additional 1 px chip-only gap exception is explicitly listed there. The 8 px rules elsewhere and the 11 px chip text stay intact.

Keeping 8 px horizontal padding after reducing the vertical inset left 1 Workshop/Engine overlap at 800 × 600, 2.489777 px wide: the 11 px last-event text widened Workshop relative to the older implementation. A symmetric 4 px inset clears that remaining pair without changing text, the event-width cap, anchors or the camera. This implementation choice scores 2 × 0.1 = 0.2; no new judgement requires Michou's answer. The failed check itself is unscored.

| Viewport, CSS px | Before, overlapping pairs | After, normal motion | After, reduced-motion fixture |
| --- | ---: | ---: | ---: |
| 400 × 700 | 2 | 0 | 0 |
| 800 × 600 | 4 | 0 | 0 |
| 1440 × 900 | 0 | 0 | 0 |

The real Three.js page and the source-only gate independently reproduce the review's 2 / 4 / 0 counts before the repair. The real page counts all 21 unordered pairs among 7 chip rectangles at 2 settled samples per case. The new parametrized test reads the station's room definitions, camera, anchor expressions, CSS and fixture ledger, computes the orthographic wrapper projection, and lets installed Chrome measure the actual chip CSS. It asserts 7 distinct, visible, positive-size chips and a count of exactly 0 at each of the 3 sizes. Missing projection contracts fail the fixture. It uses 0 server, vendor or network dependencies and runs under `make check`. The working tree already contained an unfinished projection adapter at session entry; it is preserved and completed with these 3 assertions.

## Contrast and focus

All **16 station contrast cases** pass in installed Chromium 156 using the existing composited glyph-core method: 1440 / 400 px, normal / reduced motion, deck / pane / calm / calm-pane. There are 1,372 measured text observations, 0 failures, 0 owned-but-unmeasured text nodes and a minimum of **4.59258018:1** in every case. The collector includes pointer-transparent bubbles. Hidden or wholly occluded nodes remain enumerated as unpainted in each inventory. The replay is paused at `19:52:00`; the capture fixture freezes scene updates, and the original text nodes and clipping ownership are retained.

The first swatch sweep recorded 1 low Archive last-event reading in each phone deck mode, at the fractional clipped ellipsis edge. The complete 16-case glyph sweep resolves both readings with the standing opaque-core method rather than changing any source colour or accepting the swatch result. Both sweep manifests remain in scratch evidence.

Safari 26.6.2 independently passes all 16 contrast cases: 1,374 measured observations, 0 failures, 0 cases without measurable glyph cores, 0 changed original text ranges and a 4.52990630:1 minimum. The existing glyph collector retains clipping ownership and includes bubbles; native Display P3 captures are converted to sRGB with the existing `sips` procedure. The first attempt, with an extra application-activation step, timed out before replay initialization. A bounded diagnostic using only the WebDriver window initialized 37 events within 2 seconds; removing that extra harness activation produced the complete 16-case capture. There is no design-source workaround. Cowork's native artifact pass remains unclaimed.

In Chromium, real Tab presses at all 3 sizes in both motion modes reach 54 stops: all 7 rooms plus pause and tray in each of 6 variants. Every measured stop has the 2 px solid cyan ring, offset −2 px. All 42 room stops are inside the viewport, clear of both HUDs and hit-testable. Enter follows a focused room and shows its pane in all 6 variants; Escape returns to the deck with the focused chip visible. There are 0 page, console, HTTP or external-request errors across the Chromium geometry/focus and final contrast runs. Screenshots at 800 px default and 400 px deck were inspected. No interaction source changes were required.

## Gate and delivery

The targeted precision suite passes 85 tests, including the 3 new overlap cases. `make check` passes 489 tests with 10 agent-tier tests deselected, 0 blocking lint, 138 advisory and 6 cosmetic findings; Ruff check and format pass. The gate runs offline with the existing locked environment and the absolute worktree uv cache. Its full output is `logs/scratch/design-review/cdh-0019-chip-budget/make-check.log`.

Only 4 delivery files belong to this cycle: the station, `tests/test_design_precision.py`, this report and the handoff README status. Existing ledger and inbox modifications are excluded. CDH-0019 stays open. `main` advanced externally from the starting `d20b172f8aef69cf6bd38483b937201d148086c6` to `89d755e08122a4fc42cb9a9aa00165bbd5a83f00` during verification; that advance was reported immediately. No merge, push or publication is performed by this cycle. Stop after the pathspec commit for Cowork's native pass; that commit is the approval candidate only if the native check passes.

## Evidence

All evidence is under `logs/scratch/design-review/cdh-0019-chip-budget/`. `summary.json` records the scope assertion, counts and score; `sha256.json` hashes the sources, harnesses, logs and captures. `inputs.json` records the fresh before/after fixtures and the already-installed pinned Three.js dependency. The reduced-motion variant is an explicitly labelled media fixture, not an OS preference claim.

| File | SHA-256 |
| --- | --- |
| `docs/design/cockpit-v0/station/index.html` | `d66f537a1d5090e0442f02266041d1b918539a14ec37aa913d666d0343fc1e6c` |
| `tests/test_design_precision.py` | `14f88eddd50dfc2a578a3e485044b50d23dac32c5656551494e2fb0f5b252702` |
| `geometry-focus.json` | `48fbf1968f6e141ce4c5471c484fe412dcbefdf5782135def7d83058ca6b424d` |
| `station/glyph-after/manifest.json` | `4dbd7ea38764a164801c89933f7ca9d9017b26b223d7c4af9c327f8ab9234aa9` |
| `safari/glyph-station-after-manifest.json` | `2c6bf4d104b350aaf7378dfc45684f3aa186417da2a938a1e98cf7e76b35e63e` |
| `safari/glyph-station-after-analysis.json` | `a4639fc775f80d6e0d400721a1aa341ea47dda96c7ae8cb60d27067d78979a65` |

Reproduction uses `node logs/scratch/design-review/cdh-0019-chip-budget/prepare.mjs`, then `verify.mjs` and `station/glyph-contrast.mjs after` in that folder. Safari uses `safari-prepare.mjs`, `uv run .../safari-capture.py` and `node .../safari-analyze.mjs station-after`. The loopback servers serve only existing local assets; no dependency was installed. `regression-before.log` records 2 failed / 1 passed overlap cases before the source fix, and `precision-after.log` records 85 passes after it.
