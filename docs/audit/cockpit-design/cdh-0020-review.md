---
id: AUDIT-CDH-0020-REVIEW
type: report
created: 2026-10-21T20:20:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0020
  - AUDIT-CDH-0020
  - AUDIT-CDH-0019-CYCLE-1-REVIEW
  - docs/design/cockpit-v0/station/index.html at 037da10
  - logs/scratch/design-review/cdh-0020-native/
tier: 2
status: final
handoff: CDH-0020
period: "2026-10-21"
reviewed_sha: 037da10
review_canvas: "private artifacts: KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 8; KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 30, unchanged (no board changed)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW27 | advisory | `station/index.html` (`.hud`, no ground in deck mode; the `max-width:720px` block) | Below 721 px the two HUDs wrap to most of the screen (top 447 / 429 / 413 px and bottom 178 / 162 / 134 px of 700 at 320 / 360 / 400, leaving a deck band of 76 / 109 / 153 px), and they have no ground in deck mode, so the deck's labels show through their words: 13 of 15 on-screen room chips, crew tags and shown bubbles sit under a HUD box at 320, 14 of 16 at 360, 15 of 18 at 400 (3 of 19 at 720, 2 of 19 at 721, none at 1440). Seen natively at 320 and 360: a room chip and a crew tag over the harnesses line and the summary. Pre-existing: the counts are the same before CDH-0020; not a regression of this build. | Under the phone media query the two HUDs take the ground, as calm already does (`.hud{background:var(--ground)}`); at 721 and above nothing changes. Scored 2 × 0.3 = 0.6: decided, built as CDH-0021 (Codex), listed for the approval screen. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of Codex's CDH-0020 build (`037da10`, AUDIT-CDH-0020): CW26, the station HUD's active-runs summary past the viewport below 362 px. ADR-023: the reviewer is never the builder; Codex's checks are read as data and repeated here with different means.

**Delivered by Codex.** `docs/design/cockpit-v0/station/index.html` `0a93f8ebdcd91d0dbe869b10fea0360ba855afae192eb962dc055387bfad7a07` (on the Mac, from `037da10`). It differs from `ceb0a4b` by one declaration, `.tr-sum{white-space:normal}`, inside the existing 720 px query. No board mirrors the station's HUD (the boards mount `Tray.dc.html`, whose summary sits in fixed-width artboards), so the review copy stays at version 30. Published KGME Station version 7 matched `ceb0a4b`'s page body byte for byte before the republish (no drift); version 8 matches `037da10`'s body byte for byte, apart from the one trailing newline the publish wrapper adds.

| check | Codex measured | Cowork measured | closed |
|---|---|---|---|
| CW26 at 320 and 360 | `#traysum` right edge 304 / 344 px, two lines, headless Chrome 155 on the Mac with the worktree's three.js copy | standalone, Playwright Chromium in the Cowork VM with three@0.182.0 packed fresh from the npm registry (its `three.module.js`, `three.core.js` and `package.json` hash the same as the worktree's copy, and the rebuilt local page hashes the same as Codex's): right edge 304.000 / 344.000 px, two lines, `white-space:normal`; before the change 362.156 px at both, one line. Natively, KGME Station version 8 in the pane at an emulated 320 × 700: the summary `3 working (1 quiet) · 1 transient` breaks after `· 1` and ends inside the frame | yes |
| single line at 400 and above | 362.156 / 362.156 / 463.172 / 463.172 px at 400 / 720 / 721 / 1440 | the same four edges; one line at each; `normal` up to 720, `nowrap` at 721 and 1440. Natively at the pane's own 800 × 600, one line | yes |
| the calm grid | 1 / 1 / 1 / 3 columns, 0 px overflow | 1 / 1 / 1 / 1 / 1 / 3 columns at 320 / 360 / 400 / 720 / 721 / 1440, tracks 288 / 328 / 368 / 688 / 649 / 446.656–446.672 px, 0 px overflow, seven rooms, the same as AUDIT-CDH-0019-CYCLE-1-REVIEW | yes |
| the page itself | no page errors, 24 loopback requests | no page errors; one console 404, the browser's own favicon request; 22 page requests, all to the loopback origin; seven actor symbols and a sized WebGL canvas at every width; every HUD fact string identical before and after from 320 to 720, where both runs paused at 37 events (at 721 and 1440 the before runs paused later; see the notes) | yes |

**Two measurement notes.** (1) The only text box past the viewport at 320 after the change ends at 348.3 px: the visually hidden status region (`.vh`, clipped to 1 px), not painted and not scrollable (page scroll width 320); it is not a finding. (2) In the before runs at 721 and 1440 the replay reached 38 and 39 events between the summary wait and the pause (SwiftShader). At 721 that changed the summary to `1 working (1 quiet) · 1 waiting · 1 transient`, with its right edge at 564.313 px; the after run at 721 and Codex's before run at 721 both read 463.172 px. At 1440 only the event count differs. Both are a different moment of the replay, not a layout difference.

**Native pass.** The built-in browser pane was hidden; the artifact frame painted on the second capture after each load (the first was blank) and confirmed the wrap at 320, the deck and HUD at 360, and the single line at 800. The replay runs at ×20 in the artifact, so the moments differ per capture; the pixels are JPEGs and a PNG crop as the pane gives them. The frame takes no keys, so calm was checked standalone only.

**Evidence** under `logs/scratch/design-review/cdh-0020-native/` (hashes taken on the Mac after delivery; delivery re-encodes images, pixels compared identical on one PNG and one JPEG; text files byte-identical):

| File | SHA-256 |
|---|---|
| `standalone-before-deck-320.png` | `4daff739745945166edfc42615c9fec2e50ed155f2d2fdba354fa8e9db853b66` |
| `standalone-after-deck-320.png` | `cb1caee3dd33a2829cda2f83b50b63220ef2bb954bbd001fd1c03548baf17119` |
| `standalone-after-calm-320.png` | `07e72c37efd1b22596739ffd30af438ae981c23c37808b5aae020a29bbda8a2c` |
| `standalone-after-deck-360.png` | `45a5d7821f247809e80de94cf7dba6d2ae7e13364ee4421042457737ae84ab4d` |
| `standalone-after-calm-360.png` | `a03d5154cd50b3b83dd4ff4dd666246d8dd4c1fb3d5292e4d9d7086444f97561` |
| `standalone-after-deck-400.png` | `20bc74fa13fe8b33fb2cfe4c7c7882911d19a0d23a2dbdcac1da312163bfc413` |
| `standalone-after-deck-1440.png` | `5cc41aee1c0502ecd433433ef524e6b610f89de335936cf36239992c4ce66348` |
| `native-v8-320x700-in-800x600.jpg` | `86e4a7c2769fb0154eb9528de88a6207a676e11ad3e718e4ab04b33b0ddd107e` |
| `native-v8-320x700-hud-crop.png` | `24cd84c110d8e72241253673f2cc0f39058a38a4b669be10fc7ef4eee230a440` |
| `native-v8-360x700.jpg` | `2118e8f83c22da9b4df680144cdcd5b0b8751bd11a5939db28c3e414d60524d7` |
| `native-v8-800x600-desktop.jpg` | `c80d971015cd88dac9d94b1ecce32663ddb5adc312d34c5f3b940068ba92eabc` |
| `measure20.json` (every width, deck and calm, before and after; the replay clock before and after each capture) | `aa8152318f1af74e02d473731e269482ff496c00063562d363fdd6eae34b65c3` |
| `manifest.json` (served shas, browser, the native captures) | `34f3d527fbda1e3b10435872b8c8757af6a678ea842dec8335d5e9b3fa13543b` |
| `measure20.py`, `probe320.py` | `8de3263c443cf5849096ebc9b1613a17163c4c6c84a2125be94732e940b3efa4`, `7cf5943d2969161e526cc210b3d82119e646e6446a85f4b879914e2eeeef2e64` |

**Next:** CDH-0021 (CW27) is `ready` in the Codex queue. The design track has no open blocking finding at `037da10`. This report is not Michou's canvas approval.
