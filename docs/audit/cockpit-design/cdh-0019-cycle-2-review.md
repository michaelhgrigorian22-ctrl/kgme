---
id: AUDIT-CDH-0019-CYCLE-2-REVIEW
type: report
created: 2026-10-22T01:55:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0019
  - CDH-0022
  - AUDIT-CDH-0022
  - AUDIT-CDH-0019-CYCLE-2
  - docs/design/cockpit-v0/ at ebcf02c
  - logs/scratch/design-review/cdh-0019-cycle-2-native/
tier: 2
status: final
handoff: CDH-0019
period: "2026-10-22"
reviewed_sha: ebcf02c
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 33 (9 boards republished from ebcf02c); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 10"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW28 | advisory | the eight host boards' `source-facts` line; `station/index.html` `[data-source-facts]` in the pane and the wall | F3's repair is correct against the one rule but repeats the four corner micro-labels word for word, under every operating board and twice in the station. Seen natively on board 3, the line wraps to two lines just above the footer while the same four strings stay at the corners. That is the repetition the 2026-10-22 philosophy cuts first. | Give these facts one home: B1's system context under `?` (desk and wall) and `a` (station). Strip the micro-labels to facts-free ornament, for example "KGME · KUANG GRADE MARK ELEVEN" and the board's name. Scored 2 × 0.3 = 0.6: decided, approval screen. It's built with B1, or on its own if B1 is declined. |
| CW29 | advisory | the activity grids (`cells()` and `.cell-value` on Main, Blocking, Pending, Disconnected and Wall) | F4's repair is correct against the colour rule, but each grid became a table of 96 digits (240 on the wall). Colour survives only at the cell edges, so the picture the grid exists for, where activity clusters and where it turned blocking, is mostly gone. At 1440 it reads as a block of numbers. | Use a non-colour encoding that keeps the picture: each sample becomes a column whose height is its count, with B and P as glyph marks on their columns. Put the exact value in each cell's accessible label and a one-line summary under the grid (peak, total, where the blocking falls). Scored 2 × 0.4 = 0.8: decided, approval screen, a coordinated build row. The F7 bucket contract (60 one-minute buckets) belongs in the same row. |
| CW30 | cosmetic | `Disconnected.dc.html:119` | The new line uses `#7a8d9b` while the rest of the board's muted text uses `#a3b0b8`. It sits outside the `.stale` filter and reads about 5.7:1, so it passes. It's only the one grey that differs from its neighbours. | Folded into CW28's rebuild, 1 × 0.1 = 0.1. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of Codex's cycle 2 (`ebcf02c`, AUDIT-CDH-0019-CYCLE-2), which repairs AUDIT-CDH-0022's five blocking findings. ADR-023: the reviewer is never the builder; Codex's checks are read as data and repeated here with different means. The philosophy proposals and B1/B2 were not built in this cycle, as CDH-0022 required.

**Delivered and republished.** Before republishing:
- the nine published board files of the review copy matched the pre-cycle source byte for byte (the hashes AUDIT-CDH-0022 records);
- the ten files staged from `ebcf02c` matched the hashes in AUDIT-CDH-0019-CYCLE-2.

The review copy now carries the nine changed boards; the service counts it as version 33. KGME Station version 10 matches `ebcf02c`'s page body, apart from the publish wrapper's newline.

| finding | Codex measured | Cowork measured | closed |
|---|---|---|---|
| F1, the component sheet's focused row | computed `#7a8d9b` on `#0e1a22`, 5.1371:1 | the source carries `#7a8d9b` on the three cells, the same token and pair AUDIT-CDH-0019-CYCLE-1-REVIEW confirmed painted on boards 3 and 9 | yes |
| F2, station room focus at phone widths | 98 observations at seven widths, all visible | Tab focus measured after three rendered frames: 14 of 14 observations inside the deck band and topmost at 320, 360, 400 and 720 (focus22b.json); visually the focused Workshop chip sits in the band with its cyan outline at 400. Measured after a fixed 250 ms instead, 2 at 320 and 4 at 400 were still at their untranslated positions, because the clamp runs in the render loop, so the room moves into view one frame after it takes focus. That's acceptable; recorded as a measurement lesson. 1440 is unchanged (all inside) | yes |
| F2's side effect, the label layer | not measured | the labels now sit outside `#stage` with every wrapper at `z-index:1`, which could have changed which label draws on top. At 1440 × 900 at the same replay moment, the three overlapping label pairs keep the same label on top in v9 and in cycle 2 (measure22.json). Natively, version 10 at an emulated 1024 paints chips, crew and bubble over the deck as before | yes |
| F3, facts in noise | 32 mirrored strings on eight hosts, outside the noise condition; the station's pane and wall | natively, board 3 at 1440 × 1100 and board 6 show the line above the footer. In the station, the `a` pane and the calm wall each carry one line holding all four micro-label strings, at 320, 400 and 1440 (measure22.json) | yes; CW28 for the repetition |
| F4, colour-only grid values | 624 styles unchanged; labels and B/P sentinels | natively the digits paint inside the cells and stay legible at the pane's own width (board 3, 643 CSS px); under board 6's filter they stay light on the ground | yes; CW29 for the picture |
| F5, `r` in two contexts | key face and legend | the source of board 7 carries "run · retry" and the two-context legend; board 6's modal keeps "r retry now" | yes |

**Pre-existing, not acted on.** At the pane's own width (643 px) the host boards' corner micro-labels collide with each other (board 3's top edge). The boards are desktop drawings, and CW28 removes the cause, so this is 1 × 0.2 = 0.2, recorded.

**The two items for Michou (AUDIT-CDH-0022's brief).** Cowork's read agrees with both of Codex's recommendations:
- **B1, a compact operating header with diagnostics under `?` and `a` (2.0).** It is the philosophy's clearest single move: at 400 px, 78 % of the station's screen is HUD. It also gives CW28 its one home.
- **B2, a persistent disconnect band (1.5).** The snapshot stays inspectable instead of sitting under a modal.

**Evidence** under `logs/scratch/design-review/cdh-0019-cycle-2-native/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `native-v33-board03-pane-643px.jpg` | `c18fec37c61d4837b8e3ffa84e982cdffef0d1b16e2dcdfd7632c4044ab07b9f` |
| `native-v33-board03-1440x1100.jpg` | `a0b666d8b99fc784d40a10d0ea2ed0b4924850b4299ac0c6f56b46e69efde351` |
| `native-v33-board06-1440x1100.jpg` | `710aa7d10a401b8d48b4fa628bc365faf87a08a1d5fdf64b8703687cf9fdc693` |
| `native-v33-board09-2560x1170.jpg` | `f63eacc39d8c032b242cd1fe30cdeb825ce30d72681597e0a92348bd3effa63a` |
| `native-station-v10-1024x768.jpg` | `fb0d59fed30aabdc0f8b0a47c9c87275fefdf99d1723c2c0736001d4bea477c0` |
| `standalone-cycle2-workshop-focus-400.png` | `cfb72825b44b1cf5f2e54ae9d7cb60cc2def2fed3a5b0152de1b6f9d64384dd2` |
| `standalone-cycle2-room-focus-400.png` | `545e0db6a51ae9851473c40a699ac7b3ea27f5bb3b75563c1c5e6d436d2cf015` |
| `standalone-cycle2-calm-1440.png` | `9be722bf61e555408e47bc51449c8c41fc110c07b3323973c31e145ab3e51570` |
| `standalone-stack-v9-1440.png`, `standalone-stack-cycle2-1440.png` | `5d30d0744ab9e5a9249979ead0b994468bc3f55c04068b67749b9d3b9f68a57e`, `e75460c89956e21227611fd3ae165b9a17e06dcdf98c6cb956428b8254935f34` |
| `measure22.json` (focus at a fixed delay, source facts, label stacking) | `294120881178c7bfd099a59be00e7d6e8073e498c180bd69201f841b00b1f2b5` |
| `focus22b.json` (focus after three rendered frames, four widths) | `db39448198139a25873f4910895a6f5ccf7a05b865c10591d6d5674a6bdb3fc0` |
| `measure22.py`, `focus22b.py`, `focus-probe.js` | `5dcd5b850cf5edb0ce151349213642a4e5861c5090b087a55c03943c5d7427ed`, `82627edbe72d04a4c431572cfe9e66d9d596c4185c964ea557971d8c2d44ce96`, `b11ffed3cd85a3d331a3501ff4eb410721bf776db5821e6c167fafedb16c3e9b` |

**Next.** No blocking finding is open, and no row is `ready`. The coordinated redesign waits for Michou's answers on B1 and B2. Cowork then writes its build rows, carrying CW28, CW29 and the scored AUDIT-CDH-0022 table. This report is not Michou's canvas approval.
