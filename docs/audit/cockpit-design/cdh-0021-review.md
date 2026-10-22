---
id: AUDIT-CDH-0021-REVIEW
type: report
created: 2026-10-21T23:50:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0021
  - AUDIT-CDH-0021
  - AUDIT-CDH-0020-REVIEW
  - docs/design/cockpit-v0/station/index.html at bab44b5
  - logs/scratch/design-review/cdh-0021-native/
tier: 2
status: final
handoff: CDH-0021
period: "2026-10-21"
reviewed_sha: bab44b5
review_canvas: "private artifacts: KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 9; KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 30, unchanged (no board changed)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| — | — | — | No new finding. CW27 is closed (below). | — |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of Codex's CDH-0021 build (`bab44b5`, AUDIT-CDH-0021): CW27, the deck's labels showing through the HUD's words below 721 px. ADR-023: the reviewer is never the builder; Codex's checks are read as data and repeated here with different means.

**Delivered by Codex.** `docs/design/cockpit-v0/station/index.html` `45dbb6db88964982430870d00a3ed00246e7a3d151b5ae1e841f466f828dd129` (on the Mac, from `bab44b5`). It differs from `037da10` by one declaration, `background:var(--ground)` on the `.hud` rule inside the 720 px query. No board changed, so the review copy stays at version 30. KGME Station version 9 matches `bab44b5`'s page body byte for byte, apart from the publish wrapper's trailing newline.

| check | Codex measured | Cowork measured | closed |
|---|---|---|---|
| the HUDs' ground | computed `rgb(10, 12, 16)` on both HUDs at 320–720, transparent at 721 and 1440 in deck mode | the same computed values, in Playwright Chromium in the Cowork VM with three@0.182.0 packed from npm. A pixel check that does not rely on computed styles: with every HUD descendant hidden (the boxes and their backgrounds stay), every pixel inside both HUD boxes is the ground, 0 of 143,040 / 56,960 off at 320, 0 of 154,440 / 58,320 at 360, 0 of 165,200 / 53,600 at 400 and 0 of 154,080 / 84,960 at 720 (top / bottom). Before the change only 9.1 % / 0.2 % of those pixels were ground at 320, 9.4 % / 1.1 % at 400 and 26.6 % / 4.3 % at 720. At 721 and 1440 the counts are unchanged; the difference at 721 is 2 pixels of 195,391, from the cast's animation | yes |
| nothing else moved | rectangles, facts, summary and calm grid unchanged at six widths | every measured state paused at 37 events. Both HUDs' text, both HUD rectangles, the summary's rectangle and line count (304 / 344 / 362.156 / 362.156 / 463.172 / 463.172 px; 2 / 2 / 1 / 1 / 1 / 1 lines) and the calm grid (1 / 1 / 1 / 1 / 1 / 3 columns, 0 px overflow, seven rooms) are identical before and after, deck and calm, at all six widths; only the clock's second differs at 720 and 1440. Seven actor symbols and a sized WebGL canvas everywhere; no page errors (the one 404 is the browser's favicon request) | yes |
| the look | four captures inspected | standalone at 320, 360 and 400, the HUD's words sit on the ground and the deck shows only in the band between the two HUDs (76 px at 320, 153 px at 400). Natively, KGME Station version 9: at an emulated 320 × 700 the HUDs paint on the ground; at the pane's own size the frame measured 643 CSS px wide, so the phone layout applies there as decided; at an emulated 1024 × 768 the desktop look is unchanged (transparent HUD, the top labels shown) | yes |

**For the approval screen.** On a phone the station is now its words with a strip of deck between them. The wall (`c`) remains the phone's full view of the facts. That is the decided trade at 2 × 0.3 = 0.6 (CW27), already listed.

**Native pass.** The built-in browser pane was hidden. After each load the frame painted only on the third capture, about 40 s in. The frame takes no keys, so calm was checked standalone only.

**Evidence** under `logs/scratch/design-review/cdh-0021-native/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `standalone-before-deck-320.png` | `8d2d4f50c8af86694ffa8d3895cc645e03a728dee038723d4892052945eb5dcf` |
| `standalone-after-deck-320.png` | `242bf47b8b28d3fee14eda3dc7baf3e23f0c87e05e346ee944dbff2327dea266` |
| `standalone-before-deck-320-hud-text-hidden.png` | `8cfdf4ca6c9329a2ffaddd4aa75df4afed78382508b3129488781ec9322ddd29` |
| `standalone-after-deck-320-hud-text-hidden.png` | `60cd12ef30bf4704a7af6ff6609ae2a2896a5d0fe66eb50023b0cc89382d05bf` |
| `standalone-after-deck-360.png` | `748a0e956fce686ce60b2df9149f01137e4aa4a4d1fbe7d2a41d91412a175421` |
| `standalone-before-deck-400.png` | `faa5bcf98e82baa1fdfa56be20149de47a5e2fc0f97a8c816710c51f100ee419` |
| `standalone-after-deck-400.png` | `315051ac65199d8f3199710c2f7703fa0db0bfd567eade576436062c1a946435` |
| `standalone-after-deck-721.png` | `e7dd70ca6c2a649ca62ebd257f479b1490b2c9b78485f0394e7b3da09331c0df` |
| `native-v9-320x700.jpg` | `9a9665a9c8e95ba3e562463e7c9795b2f8447e60950c744a6dc7231a6ae1e071` |
| `native-v9-pane-643x823.jpg` | `5c622a3e8a18fca64705d724bb4fac1a209f75cf4254920cce8e619c2cca7492` |
| `native-v9-1024x768-scaled.jpg` | `5aa96f2a2bc75a0f529bc426433e20e28362f41223de621291fcc0591b68981c` |
| `measure21.json` (every width, deck and calm, before and after, with the pixel counts and the replay clock around each capture) | `06b3d66b0be997975beef918133754b19faf871f8206f6200b7946147ad3c363` |
| `manifest.json` (served shas, browser, the pixel method, the native captures) | `d7d52df83f08c3644c652896c3fc66ea2b99c451ba6109cbe2f4cc5a657c7fee` |
| `measure21.py` | `8c6f0af1ac499a62944c9e34b4ebe00886bb7fbff68aaee70793de6712ad1e75` |

**Next:** no row is `ready`; CDH-0019 stays open. The design track has no open finding of any class at `bab44b5` that a cycle would act on. What remains is Michou's: the three questions of the 2026-10-16 brief and the canvas approval. This report is not that approval.
