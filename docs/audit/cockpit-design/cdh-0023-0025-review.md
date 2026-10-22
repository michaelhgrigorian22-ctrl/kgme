---
id: AUDIT-CDH-0023-0025-REVIEW
type: report
created: 2026-10-22T13:45:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0023
  - CDH-0025
  - AUDIT-CDH-0023
  - AUDIT-CDH-0025
  - docs/design/cockpit-v0/ at 2744415
  - logs/scratch/design-review/cdh-0023-0025-native/
tier: 2
status: final
handoff: CDH-0023
period: "2026-10-22"
reviewed_sha: 2744415
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 34 (9 boards republished from 2744415); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 11"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW31 | advisory | `Disconnected.dc.html:133–136` (`quotaAlerts`, default `value = 95`) | Board 6's header alert reads "Codex Plus · stale 19/20 segments · high", with a 95 % fill. The record says 18 of 20. The meter this alert replaced had 18 lit segments at `e7594d6`, and board 7's Disconnected system section says "18/20 lit segments". So a fact moved and changed value on the way. Codex's source check tests that each moved string is present, not that its value is the same. Seen natively at 1440 and at the pane's width. | The stale alert reads 18/20 with a 90 % fill, the text derived from the value so the two can't drift. Scored 2 × 0.2 = 0.4: decided, since the record decides. It's carried into CDH-0024, which rebuilds the top of board 6. |
| CW32 | cosmetic | `Components.dc.html:175` | Board 1's noise specimen still describes the micro-label as one that "repeats facts shown elsewhere". Since B1, the rule is that a micro-label carries no fact. | Folded into CDH-0027's one statement of the noise rule (board 1). 1 × 0.2 = 0.2. |
| CW33 | cosmetic | `Phase2.dc.html`, footer | Board 8's session line and its four micro-label sentences moved, once each, into board 7's Phase 2 system state, as the rule asks. But unlike boards 2–6, board 8's footer doesn't name `?`. It never had the hint, and now its facts live there. | Board 8's footer gains "? keys + system", in CDH-0027's board 8 item. 1 × 0.3 = 0.3. |

### Verdict

PASS

### Notes

**Scope.** This is Cowork's native and standalone review of CDH-0023 (`d67613c`, with the System-field addendum `1a43e0d`) and CDH-0025 (`2744415`); Michou's count ruling is in `ac6351b`. ADR-023: the reviewer is never the builder. Codex's checks (AUDIT-CDH-0023, AUDIT-CDH-0025) are read as data and repeated here by other means. CW31 is not blocking: the alert's presence, threshold and rule are right, and the value fix rides on the next row, which rebuilds the same board.

**Delivered and republished.** Before republishing:
- the review copy's live board files matched version 33, so there was no drift;
- the ten files staged from `2744415` (nine boards and the station page) matched the hashes in AUDIT-CDH-0023 and AUDIT-CDH-0025.

The service counts the review copy, with the nine changed boards, as version 34. KGME Station version 11 matches `2744415`'s page body, apart from the publish wrapper's newline.

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| The station HUD's share | 400 × 700: 78.0759 → 55.3415 % | Standalone v11 against v10, at the same paused replay moment: 400 × 700, 78.08 → 55.34 %; 320 × 700, 89.21 → 62.47 %; 1440 × 900, 23.21 → 17.21 %. The top HUD holds the clock, hull, active runs, replay and following. | yes |
| Station focus | Seven rooms at six widths, after two frames | Tab, measured after three rendered frames: 14 of 14 observations inside the deck band and on top at 320, 400 and 1440, all seven rooms. | yes |
| The station's `a` pane | Complete in both modes | At 400 and 1440 it holds ledger, session, harnesses, surface, replay range and speed, provenance, source, origin and navigation. Hook latency and both quotas say outright that the replay doesn't supply them, which follows Michou's ruling that unavailable counts stay explicit. | yes |
| Micro-labels | Facts-free on every board | The station's are `KGME`, `· · ·`, `◦ ◦ ◦` and `· · ·` at three widths. Natively, boards 1–9 show only the product name and dots. A source grep finds board 8's four sentences and session line once each, in board 7's Phase 2 state. | yes; CW32 for board 1's description |
| Calm | Seven rooms; columns unchanged | 1, 1 and 3 columns at 320, 400 and 1440; 7 rooms, 0 overflow, 0 page errors. | yes |
| The operating headers (boards 2–6, 8 and 9) | Fourteen CSS projections | Natively at design size: the clock, the ledger word with its counts and the tray slot. Codex Plus at 91 % shows its amber alert on 3, 5 and 9. Nothing shows below 80 %: board 4 is at 38 % and board 2 has no reading. Board 6 carries its stale alert. | yes; CW31 for board 6's value |
| Board 7's map and system section | Selector callbacks in source | Natively, clicking desk, wall and station switches the title, the key faces and the system section. `SYSTEM · WALL` holds the wall's own facts; the station map says its system facts live once in `a`. Clicking Disconnected shows the stale record. In the pane, a click inside the frame and then Tab put the cyan focus ring on "Live"; Shift+Tab moved it to "station", and Enter selected it. | yes |
| Activity columns (CDH-0025) | 480 buckets; nine specimen columns | Each board's `cells()` was evaluated from the published copy. Boards 3, 4, 5 and 6 have 60 buckets each (18:53–19:52, 08:50–09:49, 18:54–19:53 and 18:53–19:52), and the wall has 240 (15:53–19:52). Every column is labelled with its time and count. The B on board 4's 09:49 and the P on board 5's 19:53 both read "count unavailable" and are left out of the peak and total. The `+` caps sit at 19:52 (boards 3 and 9) and 17:19 (board 9). The summaries are as published, for example board 4's "peak 4/min (known) · 68 known events · blocking 09:49 · 1 bucket count unavailable". No digit cell and no "sample order" caption remain. Natively, the columns paint at 1440 with the axis "60 minutes · 1 min/bucket" ("4 hours" on the wall), and they go grey under board 6's stale state. | yes |
| Board 1's column specimen | Panel dimensions unchanged | Natively at 1440 × 2000: "Activity columns · events per minute", with its legend (height 0–5, `+` for 5 or more, B, P, `?` for unknown, exact values in the labels). | yes |

**Not acted on, by design.** Board 6's central modal still covers the snapshot; that is B2, now `ready` as CDH-0024. Board 2's blank activity matrix is CDH-0027's dormant cursor.

**A lessons correction.** The lessons file said the artifact frame takes clicks but not keys from the pane. Today, after a click inside it, the frame took Tab, Shift+Tab and Enter on board 7. The line is corrected. A capture can also trail the last action by one step, so wait before judging one.

**Evidence** is under `logs/scratch/design-review/cdh-0023-0025-native/`. Hashes were taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `native-v34-board01-1440x2000.jpg` | `467c2bd2e6636c56fa121b17dd4925f8005655be32953ee582d9c4591d66ad9b` |
| `native-v34-board02-1440x1000.jpg` | `4c83e9712cc595e508b4e78677599355cdeaf5fc9b7e50cddc510c94c0f20e67` |
| `native-v34-board03-1440x1000.jpg` | `316b9315bd77821f0d3cff28718674670074bad61e5fac4e0888504eaf6d1c66` |
| `native-v34-board04-1440x1000.jpg` | `51ce819de0af15543a4fba610426979cdd5e2059cd669e433b3962bcad03f5e8` |
| `native-v34-board05-1440x1000.jpg` | `19fdc53858a3f8ecf1be1b47181524205822ea675c82e6f9a035e0c8fc52941d` |
| `native-v34-board06-1440x1000.jpg` | `78f5fce173cb9c3117af168075269cf564e4e5410c12311e97f40876296abdb2` |
| `native-v34-board06-header-pane.jpg` | `e8e3416102ca0d6fd577d3f88e0f7e53ab33fced2ee6da95d31ec369bc7bf354` |
| `native-v34-board07-desk-1440x1000.jpg` | `ca860f7c40dac7bf0fa1605a01bb10233c2f6fb7e2c054fef3412482e5e97889` |
| `native-v34-board07-station-clicked-pane.jpg` | `c314b37c8a807fb0b72879c7544c1e70962688f303b3d684c54e1b294b148b7b` |
| `native-v34-board07-station-a-pane-line-pane.jpg` | `2b2fd26a299f15f35f07bbeb9cbe34d88f385c6b1265a9d298825dde75b05f4b` |
| `native-v34-board07-wall-clicked-pane.jpg` | `597614debba4e38c44838f368280af02d426325a8834f071c46ffaab590483e0` |
| `native-v34-board07-system-disconnected-clicked-pane.jpg` | `bdfe0c6eb3523f9878939fbdc37855aaf47a722dfbe3c99040151adfd1a07248` |
| `native-v34-board07-focus-live-pane.jpg` | `919893b711687d4df0c28226494beaea754558878ce8ed6565faebf07e7f0573` |
| `native-v34-board07-keys-shift-tab-enter-station-pane.jpg` | `848068499dcdd3483662f1d8489d691fc4012e7df4afb89d764f9ac07918690f` |
| `native-v34-board08-1440x1000.jpg` | `ad109a95cb3bc1c2a5b69e550ad907f99e0b3cd7eeff7a5e9fbb907aadb2be39` |
| `native-v34-board09-2560x1180.jpg` (overview scale) | `7365ec7580018fe7994648a39eb6ee26d0a1cb9c6c32706ad73073e46c56161d` |
| `standalone-v11-deck-400.png` | `2e7449e5f15f765b06f97860d99b37324775ed4243d23f41296e71957411bc67` |
| `standalone-v11-a-pane-400.png` | `0e61f4494295717b35ed95593b9fcaf4cbea72974828aa0d17f2afacf6df87a4` |
| `standalone-v11-a-pane-1440.png` | `e35099bce56dbd17b2a50d1c8ac2fcaeb68f45be32858eeac2f6907a42f9b9e4` |
| `standalone-v11-calm-1440.png` | `8008eccb0f06fa8894946a5b0be8ac501c0c5c1915f091c8a8fce47ae71a63bf` |
| `measure23.json` (HUD share, focus, `a` pane, micro-labels, calm; v10 against v11) | `b2cb0ea5f2607dd596dc5b7274b19a1219b099d041acdec64ff4dc01deeabb69` |
| `cols25.txt` (every board's buckets, marks, labels, summaries and quota alert) | `6449ea93d6b5569bc0c2869bb3720b1446cb826aa9ba5731baa934d30b9ee314` |
| `measure23.py`, `focus-probe.js`, `cols25.js` | `65ba44496a59541a9fdc447967cd691c409e5c31a741cbcd6cd6faedf1efc7ff`, `b11ffed3cd85a3d331a3501ff4eb410721bf776db5821e6c167fafedb16c3e9b`, `d06fe28c0c25f6b326ffb738e412c70ef790f8343a6044d11dfb7306378c4f00` |

**Next.**
- CDH-0024 is `ready` as queue row 13, now carrying CW31.
- CDH-0026 is `ready` as queue row 14.
- CDH-0027, which now carries CW32 and CW33, becomes `ready` after Cowork's native pass of CDH-0026.

This report is not Michou's canvas approval.
