---
id: AUDIT-CDH-0027-0029-REVIEW
type: report
created: 2026-10-25T18:20:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0027
  - CDH-0028
  - CDH-0029
  - AUDIT-CDH-0027
  - AUDIT-CDH-0028
  - AUDIT-CDH-0029
  - docs/audit/cockpit-design/cdh-0029-followup-implementation.md
  - docs/audit/cockpit-design/station-casino-implementation.md
  - docs/audit/cockpit-design/distant-dreadnaught-implementation.md
  - docs/design/cockpit-v0/ at 0907f28
  - logs/scratch/design-review/cdh-0027-0031-native/
tier: 2
status: final
handoff: CDH-0029
period: "2026-10-25"
reviewed_sha: 0907f28
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 39 (9 boards republished from 537b1e2, unchanged since); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 17 (0907f28; versions 13 to 16 were 040a5ad, 86f145f, be4638f and c3e8618)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW36 | cosmetic | `station/index.html`, the solar crown and the Workshop chip | The orbital station's solar crown sits behind the Workshop chip at the default framing (1440 and the pane's 800 × 600). The chip is opaque and the text reads; it is only the busiest corner of the deck, where the newest voice also lands. | Record only; Michou judged the look natively and took it. If a later look wants it cleared, the crown's angle is one number. 1 × 0.2 = 0.2. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of everything since AUDIT-CDH-0024-0026-REVIEW: CDH-0027 (`537b1e2`), CDH-0028 (`040a5ad`), CDH-0029 (`86f145f`) and Michou's three direct iterations with Codex under CDH-0019 (`be4638f`, `c3e8618`, `0907f28`). Michou interrupted the first pass at version 13 to iterate, judged each version natively as it was published, and declared version 17 done at 17:03 ("its doneeee"). ADR-023: the reviewer is never the builder; Codex's six reports are read as data and their checks repeated by other means. CW34 and CW35 from the last review are closed below.

**Delivered and republished.** Each page was staged from its commit and matched its report's hash before publishing: the nine boards of CDH-0027 and the station pages of each iteration. The review copy's live boards matched `8f49559` before CDH-0027's publish (version 39). The station went out as versions 13, 14, 15, 16 and 17; version 12 matched `8f49559`'s body before the first.

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| CW34, the room chips' width | 222 px cap, interline gap 3 → 1 px, 0 overlaps at three widths | Standalone v17 at the same paused moment (19:45:00): max chip width 222 px (v12: 257), max height 57 (61); 0 chip-to-chip overlaps at 400 × 700, 800 × 600 and 1440 × 900, where v12 had 2 pairs at 800 × 600. Natively in the pane the seven chips sit clear of one another. | closed |
| CW35, the stale alert's rounding | `Math.round(value / 5)` | Natively on board 6: "Codex Plus · stale ▮ 18/20 segments · high"; the jitter animation is gone from the board's CSS. | closed |
| CW32, CW33 (board 1, board 8) | one noise statement; "? keys + system" | Natively board 1 states the noise rule once with a before/after specimen and says the micro-label "carries no fact"; board 8 explains one future interaction (dispatch, guard request, permission, arbiter ruling) and its footer ends with "? keys + system". | closed |
| CDH-0027's cuts | 41 source assertions; 18 fixtures with 0 overflow | Natively: board 2 opens on "nothing recorded yet" with its dormant cursor, zero counts and the three starts, the event shape behind `Enter`; board 10 pairs the selected 72 px figure with its 24 px portrait and its role's event; board 11 keeps the lifecycle essay and the opened pane; board 1 no longer imports the tray sheet. | yes |
| The sky carries no fact | source check | Read the ambient component at `0907f28`: its inputs are camera, viewport and its own clock; no run, room, event, quota or hull value reaches it; the dreadnaught is static. | yes |
| Calm and reduced motion | 6 cases each | Standalone v17: calm sets `#stage` to `display:none` and keeps 7 rooms, 1/1/3 columns, 0 overflow at the three sizes; under reduced motion the far-left sky band is pixel-identical across 4 s at all three sizes, and under full motion it changes; the planets stay visible. Natively, `c` shows the text wall with no sky. | yes |
| Text over the sky | 1,780 boxes sampled, min 4.59:1 | Every text surface is opaque by computed style (HUDs and chips on `#0a0c10`, bubbles and pane on `#11151c`, crew tags on ground), so the pairs the earlier reviews measured still apply; Codex's pixel sampling is the finer record. | yes |
| Focus, HUD share, errors | 21 observations per width | Tab after three rendered frames: 14 of 14 inside the deck band and on top at 400, 800 and 1440, all seven rooms; HUD share 55.34 / 40.69 / 17.21 %, unchanged; 0 page errors. | yes |
| Following, natively | — | Clicking the Review chamber chip in the pane follows it: the camera travels, the pane opens with the dispatch line ("arbiter.claude-opus-5-5 · 19:49:10 note → Review chamber: …") and the System section. | yes |
| Frame budget | 6 runs per build, mean 16.67 ms, within 2 ms of CDH-0026 | Not re-measured here (SwiftShader is not the Mac); Codex's Metal numbers are the record. | recorded |

**Michou's rulings this pass**, all on the README's Asked-and-answered line: the space direction (version 13, "looking fire"), more planets and stars (CDH-0029), the etched sky and continuous coverage, the orbital-casino hull, the dreadnaught; then "its doneeee" at version 17. Tally 7 of 7 plus the direct instructions.

**Evidence** is under `logs/scratch/design-review/cdh-0027-0031-native/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `native-station-v17-800x600.jpg` | `87d1f0e336af91ae782168f36d058184e3aff294dae380e232e78c65f2aebada` |
| `native-station-v17-following-pane.jpg` | `3d666ad1712268d3183bc767621468f37d16be0d008cf88cb4847c0e381e46d4` |
| `native-station-v17-calm.jpg` | `6daa07e333ed1efa993a3a64978c624d6ad465d9ecbb375583e8c1de73e4303b` |
| `native-v39-board01-1440x2000.jpg` | `faeb87a2ac0e1293e7f55d2e465b41d91b869a68655b2012e3f9e8c587a3ef72` |
| `native-v39-board02-1440x1000.jpg` | `323bad0f4da93f0e9a4ef6bacd80f982e291d67a1c2abee897910c7d8268b550` |
| `native-v39-board06-header-pane.png` | `3bbe87f1aaf0f8d8e47a4135e9de1665bce6e4ebdf7810a44c7f3c5118ccdc08` |
| `native-v39-board08-1440x1000.jpg` | `3247c04907cee7eac2eb78514f907ebdd39d867c3c722b0918ac5e35dbd26c81` |
| `native-v39-board10-1440x1600.jpg` | `a1028155eb2540639c7fa69acc384fbd24a5713a6172d0c95648d17b7ed27bb8` |
| `native-v39-board11-1440x1040.jpg` | `cfebe8723f340135b6dfcbfffc0f82493d589ab8ba6de35fbd0e179b8cd8d554` |
| `standalone-v17-deck-400.png`, `-800.png`, `-1440.png` | `6c44493e56fbf2b8143d7f8a898d05fb1eeea23239af2df24edcb9ccfa31daba`, `4af40bdf496ad550c95e8c70556281d6b06dbdd1d1e7d7e3090a6a81701ba084`, `a01c62e80948796036675dab27fa182002c323dc5afca8bfcece0234096f9d9b` |
| `standalone-v17-reduced-1440.png`, `standalone-v17-calm-1440.png` | `7e27cac22325fee7d4d1b579374b011adaf74c85d7741ca702eb2921f45f2fa7`, `69fc9a0d73de1020a408a88139913e137d04014fcbdd1b45e63017f83cf9d3a0` |
| `measure31.json` (chips v12 against v17, motion, surfaces, focus, calm, HUD share) | `a03ccd11beffb8d878adf69243e79206024a6641687f4079a7b1f82568d867b1` |
| `measure31.py`, `focus-probe.js` | `f8152819ad2b0816204634212441935d02c6f7cc197732645cbb74f8e6f86b9c`, `b11ffed3cd85a3d331a3501ff4eb410721bf776db5821e6c167fafedb16c3e9b` |

**Next.** The canvas at `0907f28` is reviewed and Michou has judged its look. Two rows stand between it and approval, both `ready` in order: CDH-0030 (the WebKit check, Michou's shell ruling; needs Safari's Allow Remote Automation) and CDH-0031 (the precision pass). The approval command is `kgme approve --what canvas --sha <the commit after those two>`; this report is not that approval.
