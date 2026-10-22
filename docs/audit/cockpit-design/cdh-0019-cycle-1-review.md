---
id: AUDIT-CDH-0019-CYCLE-1-REVIEW
type: report
created: 2026-10-21T16:20:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0019
  - AUDIT-CDH-0019-CYCLE-1
  - AUDIT-CDH-0018
  - AUDIT-CDH-0016
  - docs/design/cockpit-v0/ at 0618fa5
  - logs/scratch/design-review/cdh-0019-cycle-1-native/
tier: 2
status: final
handoff: CDH-0019
period: "2026-10-21"
reviewed_sha: 0618fa5
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 30; KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 7"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW26 | advisory | `station/index.html` (`.tr-sum`, `white-space:nowrap`; the `max-width:720px` block) | The HUD's active-runs summary (`2 working (1 quiet) · 1 transient`) runs past the viewport by 42 px at 320 and by 2 px at 360 (measured standalone with the real page; `#traysum` right edge 362 px); the HUD clips it, so the count is partly hidden below 362 px. Fine at 400, the phone width the track targeted (CDH-0015). Not a cycle-1 regression: the rule predates it; nobody measured below 400 before. | Let the summary wrap under the 720 px media query (`.tr-sum{white-space:normal}`), or shrink it there; verify `#traysum` inside the viewport at 320 and 360. Scored 2 × 0.2 = 0.4: decided, built in the next cycle (CDH-0020). |
| CW25 | cosmetic | `station/index.html` (bubbles) | At the pane's 800 × 600, the dock's bubble and the archive's chip meet (the back room's bubble hangs toward the front room's chip). The same mechanism as CW25 at 1440, at a width the station does not target. | Stays accepted (1 × 0.2), as cycle 1 recorded. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of Codex's first build cycle under CDH-0019 (`0618fa5`, AUDIT-CDH-0019-CYCLE-1): AUDIT-CDH-0018 F1 fixed (the duration cells of boards 3 and 9 take the `mut` class) and F2 built (the calm grid's minimum `min(400px,100%)`). ADR-023: the reviewer is never the builder; Codex's checks are read as data and repeated here with different means.

**Delivered by Codex** (shas on the Mac, from `0618fa5`): `docs/design/cockpit-v0/Main.dc.html` `9530b4bbebec1eac1cede407a672d55ebce6cc9370150bf50dd7ea1132228ddc`; `docs/design/cockpit-v0/Wall.dc.html` `6730cb1245c68d4629c80ff5eb8b00c5fa3aa92b0d220e790338067879391413`; `docs/design/cockpit-v0/station/index.html` `35f87569802e1b16e8610dce451c15c9ee84364e33eb072c1870d1952e7952bc`. Each differs from `2e14d66` by one line; the published copies of Main and Wall were byte-identical to `2e14d66` before republishing (no editor re-save drift), and the station page rebuilt from Cowork's template with the one CSS change reproduces the committed file byte for byte.

| finding | Codex measured | Cowork measured | closed |
|---|---|---|---|
| AUDIT-CDH-0018 F1 (CW17's duration cells) | computed style in headless Chrome 155: `#7a8d9b` on `#0e1a22`, 5.1371:1 (was 4.4317:1) | natively, review copy version 30, board 3 in the editor's preview: the focused row's `3 s` glyph cores read (106, 120, 125) against (93, 96, 101) on an unfocused `0.3 s`; lighter and bluer, as `#7a8d9b` against `#6f8290` is under the preview's 0.56 scale and the pane's JPEG. Board 9 renders with the change at 0.31 scale; its cell shares the identical `.focus .mut` cascade, so the computed ratio stands for both. | yes |
| AUDIT-CDH-0018 F2 (calm grid below 400) | an isolated CSS fixture without the station module, seven widths, no overflow | standalone, the real page with the vendored three@0.182.0 (`check19.mjs`): calm at 320 / 360 / 400 / 720 / 721 / 1440 / 2560 → 1 / 1 / 1 / 1 / 1 / 3 / 6 columns, tracks 288 / 328 / 368 / 688 / 649 / 447 / 403 px, horizontal overflow 0 px at every width, seven rooms laid out, no page errors | yes |
| the station paints after the republish | unverified standalone (no three.js) | natively, KGME Station version 7 in the pane at 800 × 600, about 40 s after load: deck, crew, chips, bubbles below the crew, HUD facts, `hull nominal` | yes |

**Codex's unverified item closed for good:** the worktree now holds three@0.182.0 under `logs/scratch/vendor/package/` (gitignored, from the npm registry), with `logs/scratch/vendor/make-local.sh`, which rewrites the committed station page into `station-local.html` with a local import map and copies the cast; served from that folder, headless Chrome renders the real station without network.

**Evidence** under `logs/scratch/design-review/cdh-0019-cycle-1-native/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `standalone-calm-wall-320.png` | `b735627c1a28452a133ed527ad0bc806228cb9592225fab35ead95f01fe572c3` |
| `standalone-calm-wall-320-fullpage.png` | `d5fe08d03a7ce640e71425a5e9b54ae27fc803a7a446f79f3eecdcedf3910321` |
| `standalone-calm-wall-360.png` | `a20bae2609abc18d5a56579844b314af6888c0b528d90621e73f305b6a9d748f` |
| `standalone-calm-wall-360-fullpage.png` | `6b35d5a3a4e5163dba5fd85ebbcfa668649398e6440e6532f1eb9aa3d34e8327` |
| `standalone-calm-wall-400.png` | `e74ae65c28d5fbb9e6bb05411b8349abc996612567f5f357c3e8e40a8ae449a9` |
| `standalone-calm-wall-400-fullpage.png` | `7e73fe30243d8efde518d6db18b4a28d3797f659e436ad0746e4a9820d84ac16` |
| `standalone-calm-wall-720.png` | `83c90048b0b039cb1e53090b8d7b35a1ab5e0e65e5adda15c88799b48fa40201` |
| `standalone-calm-wall-721.png` | `83d78e1bd5d165f8f156973ff3094a525befad6a6cf052cca2ce04728f54a8c3` |
| `standalone-calm-wall-1440.png` | `c168ef554312adab987a0e5b810598e377b2767c62115764a7b76a86fb4835ab` |
| `standalone-calm-wall-2560.png` | `94000c7f08b483ee41860102d6ed645103e9b43efcba4c16f7ee0b97928c968a` |
| `manifest.json` (served shas, the replay clock before and after each capture) | `a39ed2043ac1193773eeffc664a35e3b900bf09d4589727e8fb26d96af153a21` |
| `check19.mjs`, `check19b.mjs` | `ca46ffdb27a586f677e675e3bb276bf8f1ca2b9cba3cd6be4d0ea2f9fdaa7902`, `b6935fc880473a145d2f456021692296485c98d5c8beff1b88584a94d5bf3211` |
| `native-board3-preview-fill-800x600.jpg` | `0e844db69b8056b334599e7b7d673d27204067628274f553c2079057cc663eee` |
| `native-board3-focused-dt-crop.png`, `native-board3-unfocused-dt-crop.png` | `a6c0591a5c0257abb9d0af905a8dcf39779dc332f05e6557d68780d3c729cf1b`, `e93280b6e7768d5db579ad20fcb7ecd5cf03dddb51720235991739a2dab8934f` |
| `native-board9-preview-fit-800x600.jpg` | `754867fa6ddf5cb268822442eb5d74b2c89671aa8163df5c033f2dc3abe59bbc` |
| `native-station-v7-800x600.jpg` | `9d731fce132a5c6503a94b3127dd8c5134da29a44c9ee9ad1cf8ee55d1a33bb0` |

**Next:** CDH-0020 (CW26) is `ready` in the Codex queue. The design track has no open blocking finding at `0618fa5`. This report is not Michou's canvas approval.
