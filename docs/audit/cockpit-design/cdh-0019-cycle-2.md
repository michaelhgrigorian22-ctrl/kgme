---
id: AUDIT-CDH-0019-CYCLE-2
type: report
created: 2026-10-22T01:28:58-07:00
handoff: CDH-0019
period: "2026-10-22"
source: inferred
sources:
  - CDH-0019
  - CDH-0022
  - AUDIT-CDH-0022
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0019-cycle-2/
author: codex
status: final
tier: 2
---

# CDH-0019 cycle 2: full UI review blocking repairs

This is the implementation following the read-only CDH-0022 review committed as c43b42d. Its source baseline is 3937854530c64065e4098b22183cdb234ce75883, unchanged by the review commit. All five blocking findings are taken and acted on. This report records builder verification, not a new independent PASS. Cowork's native pass remains pending. The philosophy proposals, including the two-item brief, are not implemented in this cycle.

## Changes and decisions

| Finding | Delivered repair | Decision score |
| --- | --- | --- |
| F1 | The component sheet's three focused muted cells use #7a8d9b. The computed browser colours are rgb(122,141,155) on rgb(14,26,34), **5.1371:1** versus 4.4317:1 before. The already repaired Main and Wall cells are unchanged. | The threshold is a check; reusing the established token is **1 × 0 = 0**. |
| F2 | The station's HTML labels are siblings of the WebGL stage. Ordinary labels stay below the HUD; the actual keyboard-focused room anchor rises above overlays and is translated inside the measured HUD gap. Only that anchor is adjusted; the camera, room geometry and default framing are unchanged. The focused element's identity is preserved. On phones the scrollable pane also fits between the measured HUDs, including after following changes the header height. | Clamp the existing control and constrain the existing pane, **2 × 0.2 = 0.4**. Both changes are isolated from the room/camera data. |
| F3 | All four micro-label strings are mirrored in normal flow on each of Main, Empty, Blocking, Pending, Disconnected, Keys, Phase2 and Wall, outside the noise condition. The station copies all four into its existing a pane and calm wall after replay metadata is populated. The a button's accessible name mentions source facts. These copies preserve provenance without adding another shortcut. | Keep the original strings and add a plain text mirror, **2 × 0.1 = 0.2**. This temporary correctness repair adds visible text; B1's coordinated hierarchy can later relocate it under the existing help surfaces. |
| F4 | Every activity cell has an 11 px text value and an accessible label. B and P explicitly denote blocking and pending, with adjacent legends. Text sits on the established opaque ground; the original coloured cell remains visible at its edges. All five arrays, sample orders, cell sizes and colour styles are unchanged. | Add non-colour values to existing cells, **2 × 0.2 = 0.4**. The ambiguous 96-bucket/60-minute contract remains advisory F7, not silently rewritten. |
| F5 | The r key face says run/retry; its full legend states retry while disconnected and run filtering otherwise. | Document the existing context, **1 × 0.1 = 0.1**. No new binding or handler. |

None of these implementation choices reaches the 0.5 approval-screen threshold. The README retains the separately scored philosophy proposals at 0.6–2.0, the two pending brief items, and the three previously taken answers. There is no disputed finding and no third patch on an existing finding. The pane adjustment followed an observed first-pass capture in this same cycle; its initial phone overlay is retained as pre-pane-fix-400.png for comparison.

## Verification

The Node source check executes the drawings' actual cells() functions with only DCLogic stubbed. It compares all **624** before/after styles in order, checks explicit labels and the B/P sentinels, verifies all **32** micro-label strings in the eight hosts' normal content, and confirms those mirrors have no sc-if ancestor. Both r contexts remain documented. This does not emulate native canvas behavior.

The isolated CSS fixture uses the real component stylesheet and focused row, plus the actual activity-cell output. Browser-computed colours confirm all three repaired cells. Every value is a single readable character within its unchanged cell width, on a dark text ground; the disconnected fixture retains the original saturation/brightness filter. The resulting image is labelled as isolated source/CSS specimens, not a native board render.

The final standalone run passes at **320, 360, 400, 720, 721, 1440 and 2560 px**. Eighteen actual Tab presses per width yield **98 room-focus observations**, all visible and inside the measured deck band. At every width, returning from calm restores visible room focus; native Enter follows the named room; the pane close button remains visible when focused. All calm facts retain the micro-label strings. All seven calm layouts have zero horizontal overflow, with 1 / 1 / 1 / 1 / 1 / 3 / 6 columns respectively. The final manifest has **0 page errors**.

| Width | Followed pane top / bottom, px | Current top-HUD bottom / bottom-HUD top, px | Room focus / close focus |
| --- | --- | --- | --- |
| 320 | 441.00 / 514.00 | 429.31 / 522.25 | 14 visible / visible |
| 360 | 399.00 / 530.00 | 386.88 / 538.19 | 14 visible / visible |
| 400 | 382.00 / 558.00 | 370.28 / 566.19 | 14 visible / visible |
| 720 | 184.00 / 574.00 | 171.58 / 582.13 | 14 visible / visible |
| 721 | 283.00 / 496.61 | 270.97 / 782.13 | 14 visible / visible |
| 1440 | 147.00 / 360.61 | 134.94 / 826.06 | 14 visible / visible |
| 2560 | 93.00 / 306.61 | 80.94 / 852.00 | 14 visible / visible |

The 17 final captures comprise deck/calm at seven widths, two additional 400 px focus views and the isolated CSS image. The final 400 px focus/pane, 320 px deck, 1440 px deck/calm, 2560 px deck and CSS specimens were visually inspected. Other widths have recorded geometry and hit-testing; a capture by itself is not native verification.

The local harness uses existing three@0.182.0 through the helper, loopback HTTP, disposable Chrome 155.0.8059.85 with ANGLE/SwiftShader and DPR 1. External requests are blocked and none were recorded. It loads at=19:52:00 and speed=1 and pauses before capturing, recording both capture clocks. The sample has 40 events; 37 have been applied at that time. No dependency was fetched and no native artifact was published.

Three intermediate harness failures were assertion/input problems: a hardcoded Workshop expectation although the first room is Bridge; an incomplete CDP Enter event that omitted its carriage-return text; and comparing the followed pane with the earlier, differently wrapped HUD height. The final check uses the selected room's name, a complete native Enter event, and current HUD rectangles. These did not require three source patches. Their result logs are retained; the final manifest is the authoritative completed run.

Final **make check exits 0**: frozen offline sync, Ruff lint and formatting pass; kgme lint: 205 notes, 0 blocking, 102 advisory, 6 cosmetic. Pytest reports **360 passed, 10 deselected in 32.90 s**. The sandbox initially denied uv cache access; the approved offline run passed. The 30 sprite checks are included. No out-of-boundary repair was needed. After finalization, report-frontmatter lint reports 26 notes, 0 blocking, 25 advisory and 1 cosmetic; the coherence suite passes all 19 tests in 2.15 s.

Native host-board heights after adding provenance text and legends, native font paint, clicks, focus and canvas publication remain unverified. Cowork should specifically check the 11 px cell values, all eight provenance mirrors, the phone pane's scrolling, and keyboard focus in the separately rendered station. At 320 px the space between the existing HUDs is still small; this cycle preserves access rather than implementing the unapproved header redesign. No new physical-display, GPU/energy or 30-second performance claim is made. The moved label layer and focus-only layout read need native observation; prior sprite timing evidence is not a station performance certificate.

## Delivery and evidence

The 12 payload files below plus this report are the 13 delivered files.

| File | SHA-256 |
| --- | --- |
| `docs/design/cockpit-v0/Components.dc.html` | `5415db68af5a32f85007c779d581cdd33a168e14eb28f1ee2593c9afb9a437d4` |
| `docs/design/cockpit-v0/Main.dc.html` | `60ce44c3852b59891c9536594d4301967b2a43d5d593291018b2ae39322a6ea9` |
| `docs/design/cockpit-v0/Empty.dc.html` | `f286d01d5c9ffa3504ac5aa027dd8865a169fa59aa3c94c41bdf705ab1bfc054` |
| `docs/design/cockpit-v0/Blocking.dc.html` | `85cb4603f2cac69021db3e131c378d3b3b7316069f1a956f5eef4aee02dc97ff` |
| `docs/design/cockpit-v0/Pending.dc.html` | `209350faf72c65976f65991d0b78877501bbf5f69ab809e9d220c6f25110e664` |
| `docs/design/cockpit-v0/Disconnected.dc.html` | `86125c4a2bef1f414f139399c9fa578f613b90b6df7786fb8c91bb1e2fa0ba18` |
| `docs/design/cockpit-v0/Keys.dc.html` | `76061637bb045b6216486fcee48e4f73c6a3883eb0b89f9c5feca31267c1931f` |
| `docs/design/cockpit-v0/Phase2.dc.html` | `07c5da807439a5d28b11f1de1819d23e58d6977359e75ab0fdbe04ca50ce35d4` |
| `docs/design/cockpit-v0/Wall.dc.html` | `784485935ded520e99ecb44df6c8961481bc20d8df6931936860bfa8c33d229b` |
| `docs/design/cockpit-v0/station/index.html` | `042586cc202c6cca6efb680be71b1daee49d5fe2e2af4fc5870d1a2bac301349` |
| `docs/handoff/cockpit-design/README.md` | `7cd6890322eab7bea229eda9c30b6282b2c936cdb0f366bd5a2fd827a65a8149` |
| `docs/readers/cockpit-design-lessons.md` | `a8c29b9eb9e1e2f31069992a361bb7d7b4fcc2ca256f95eab19e3c20b3246ade` |

All captures and checks remain gitignored under `logs/scratch/design-review/cdh-0019-cycle-2/`.

| Evidence | SHA-256 |
| --- | --- |
| after-calm-1440.png | `69978cc390ee2061e1acad5ecb1c8cbc73f03f4c792b7c0bf47e6b7d2760b683` |
| after-calm-2560.png | `390e7e13d97e8a6857f7b2eab0383dbecde5a9b1493394ab573af0897e17df63` |
| after-calm-320.png | `3b05082c0842450397c5e3f5ec1e832d81f63b1c6745c2274fb2faa3b4dd274b` |
| after-calm-360.png | `61faefeacb0eb7b6872dec930ef0cb65a2d7b27b8d73ea7ce8daecc0dd2dab6b` |
| after-calm-400.png | `6749c7db1871ed62de982390ae9f718a5e0662e08e24ca0d227455895987f6d2` |
| after-calm-720.png | `b588f3ed4a2e86f14a454b067b5fca1831b4d6e688e694e9a7ff606f2dae95f2` |
| after-calm-721.png | `a2682ecd51e7f58b1188b83cd0693a9925588842562748088cfe263173a83e80` |
| after-deck-1440.png | `54962020b25ae2d325949605a186836ecd8904deea6bfadbe0ac37c76adc8838` |
| after-deck-2560.png | `822c9f2946e4366f19fd455db9e6f10eeaea0cb57026d97b04af4eb6b110b295` |
| after-deck-320.png | `99108d05dfbb5a6e53a8c21c048b12d9767072b8c61cb38326e867a886347f76` |
| after-deck-360.png | `2554beac50cfdd58f203776159dd40c08293c5f6aa6237e5b0c92c68e56a9ab7` |
| after-deck-400.png | `45a13f24af53a202c71507b1381806c4c845756fd18c3763c44654e64713a75d` |
| after-deck-720.png | `9f2c005edb8093c76adee7aaecbe25dd638f58e5fec0fcee64867588ee1cc80c` |
| after-deck-721.png | `91c432afc1183d75ec1a845ac31213e13b735541810a66972b9d26e9a822ba70` |
| after-follow-focus-400.png | `5e575eda521b08e24e685e7219f447c5fcbf673812e969ba0d331bd32379f6d5` |
| after-room-focus-400.png | `b88013de4e30454e888428de43b39fb7f7173d7ea381538d7fa72f651c8602d2` |
| css-specimens.png | `110cb681b1aa00f49689eb33cc880872f1912dc05517e56dbbd0a4918d9e7e43` |
| pre-pane-fix-400.png | `ce4adc9692f553b8d11a28789a577c7d1b6b2b74990788d0cb4b727524cc86a3` |
| station-manifest.json | `efc5326a4f08c40ff7b9f69b252d2d11564f866a56eaa8e10a14683817988d37` |
| station-inputs.json | `f5f808af87977d3cc62bf4a1c9f4c1fd3c918b0dde713e349b1b877797a42718` |
| verify.mjs | `de073591da18aa4a031b6c8fbb1c5f603f0ee568536e065317c5eaf38d002b0f` |
| source-checks.json | `cf0192d7b626633a4188c5bc238bfaa5782df1a2bf2dc700466c92091535014d` |
| check-source.mjs | `d85f45aa48f489796f15a4540a1825d7033e2c96d180aff843c5abf4e1ed6581` |
| css-fixture.html | `ffbd8587da1f114ca1f85e23208e2056f9a76021f1fffb35f19ba7cdde0860bd` |
| make-check.log | `834ec8b4b87a4ecffc3ad98a60c13a22d8f86a0d6105b111b53f86080cd061af` |
| first-harness-result.json | `982cde6e641ff8567e0ba45e2ca7a787dba66c02e46a0d411a00e11fcd50c63e` |
| second-harness-result.json | `cd910a9f9539fab1c69ac483124ecfc50c584cbc7105614a8f280f134c31bd93` |
| third-harness-result.json | `2c8c81a81fc9bd1ec9ae04d0dfcb12c256a21de1059f3c406fac59e7ebc16321` |

The implementation report's own hash is in the ignored delivery manifest after finalization, since it cannot embed its own digest. The commit is titled "design: repair full UI review blockers (CDH-0019)". Only these files are staged by pathspec, with hooks enabled. No handoff body is changed. CDH-0019 remains open; CDH-0022 is already done; no ready queue row remains.

Main at run start was d9f632ee8fe4d5ad57733e2986e9ce70eba3498b. It advanced externally through 7966a19a1e53cc21c7696d2ff792e89f58270965 to e71f78a818174ae055ad601be2d2d2405ed58b1e during this work. No merge, main checkout or push was performed. The final stop compares the then-current ref with the original baseline.

Cowork's next action is the native review and republication. Michou's pending brief remains B1, compact operating headers with diagnostics retained under existing ?/a (**2.0**, recommended), and B2, a persistent disconnect band with an inspectable snapshot (**1.5**, recommended). The complete rationale and per-board plan remain in AUDIT-CDH-0022.
