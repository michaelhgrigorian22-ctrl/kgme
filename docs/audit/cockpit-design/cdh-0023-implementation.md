---
id: AUDIT-CDH-0023
type: report
created: 2026-10-22T09:36:45-07:00
handoff: CDH-0023
period: "2026-10-22"
source: inferred
sources:
  - CDH-0023
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0023/
author: codex
status: final
tier: 2
---

# CDH-0023 implementation

The compact headers and consolidated system context are built from e7594d60caf46a3c5a13c881110bfd20b1e94bc2. This is builder verification, with Cowork's native pass pending. Michou explicitly authorized rows 11 and 12 in this session. The starting main ref is e91c98d5a9af85cf21e49179bfaa9e670e26ae5e; step 1 remains complete in 67bfebb and no merge is attempted.

## Delivered behavior

The seven operating headers retain clock, ledger state/counts and the active-runs slot. The four high-quota samples retain an amber alert; the lower readings are absent. Reset times, sessions, harnesses and latency are in board 7's System section. The disconnected sample preserves its original 19/20 lit segments as a stale reading rather than inventing a precise usage percentage. Board 4's halt and board 6's disconnect presentation are preserved. The two Phase 2 previews move immediately below the header so their content remains available.

All 32 micro-labels on the eight board hosts and the station's four labels contain only product-name or dot ornament. All eight source-facts strips and both station mirrors are removed. The source inventory verifies each removed header/micro string appears once in that surface's selected system sample; original quota segment counts are retained. Board 7 selects Desk, Wall or Station, with per-state desk samples, a physical keyboard and Phase 2 dashes. Station bindings are explicit; the three-way w cycle and ? entry are labelled as integrated-cockpit behavior because the standalone station does not implement navigation between boards.

The station keeps only clock, hull, runs, replay control and following in the top HUD. Its one System section in the a pane owns the moved ledger counters/session/harnesses and replay metadata. It is accessible in deck and calm. The pane opens with visible close-button focus and restores focus to its trigger; its calm background is opaque. Replay-only fields absent from the source, such as quota resets and hook latency, explicitly say they are not supplied or measured. No reading is invented.

## Measurements and checks

| Viewport | Before HUD share | After HUD share | After Tab room observations | Calm columns |
| --- | --- | --- | --- | --- |
| 320 × 700 | 89.2076% | 62.4732% | 22 | 1 |
| 400 × 700 | 78.0759% | 55.3415% | 22 | 1 |
| 720 × 700 | 47.4129% | 35.6964% | 22 | 1 |
| 721 × 900 | 43.2049% | 28.0903% | 22 | 1 |
| 1440 × 900 | 23.2083% | 17.2083% | 22 | 3 |
| 2560 × 900 | 14.3264% | 14.3264% | 22 | 6 |

Every width exposes all seven distinct rooms through Tab; their focused rectangles and hit-tested centers remain inside the deck band after two rendered frames. The 400 px reduction is 22.7344 percentage points. At 2560 both HUDs already fit their rows, so their combined height is unchanged. Calm's seven room records, column counts and zero horizontal overflow match the baseline at every width. The a pane is complete in both modes and scrolls between the phone HUDs. The final 400 px recheck includes the opaque calm pane. No page/console/HTTP errors or nonlocal requests were recorded. Chrome's own SwiftShader diagnostics are not page errors and are retained in the scratch log.

Node source checks verify tray data on all seven hosts, every migrated fact, all key selector callbacks, and quota cases 31% (none), 91% (amber) and 50% against a 50% cap (magenta). Fourteen isolated CSS projections exercise all headers at 1440 px, or 2560 for Wall, in low/high states. All fit their viewport and contain the active-runs summary. Three key-map projections retain 44 physical keys, selectors at least 24 px tall and no horizontal overflow. Captures were visually inspected for the desk map, live header, phone deck and system pane. The projection omits native canvas behavior and remote fonts; it does not establish native clicks or focus.

The final offline make check passes ruff, format, lint (0 blocking, 109 advisory, 6 cosmetic), and 360 tests, 10 deselected. The sandbox initially denied the uv cache and loopback listener; the approved offline/local commands completed. Early harness checks were corrected to use stable room names and allow unchanged HUD height at 2560; neither was a product defect. UTF-8 metadata was added to the scratch CSS projections before final captures.

## Decisions and limits

B1 is Michou's taken 2.0 ruling. CW28 (0.6), CW30 (0.1), F8 (0.9) and the adjacent key-family explanations (0.6) are implemented in this row and remain on the approval screen where applicable. New reversible choices: board 7 state selectors with a scrollable system region, 2 × 0.2 = 0.4; preserve absent readings explicitly, 1 × 0.1 = 0.1; move Phase 2 previews below the operating header, 2 × 0.1 = 0.2; opaque calm pane and trigger focus restoration, 2 × 0.1 = 0.2. No new brief is needed. Native board rendering, canvas interactions and artifact publication remain Cowork's, and canvas approval remains Michou's.

## Delivered text SHA-256

The report is excluded from its own digest. Closeout-file hashes are as delivered in this commit; later rows may update the shared README.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/Main.dc.html | f0113447ada99cbd02461ec43f4bfbbfb54d42eff9f661b5d33a3767e0db6e6e |
| docs/design/cockpit-v0/Empty.dc.html | 71d0e8d947c1833a89d5bf72d25a4601045f74513ac83d75509acb3943737e47 |
| docs/design/cockpit-v0/Blocking.dc.html | dbf8fbb7321e79a3fb497b0e45aa2d2ce71ef6bee15a6910f7d0f3173815be00 |
| docs/design/cockpit-v0/Pending.dc.html | cd5cbeb2215300de8c99ff6f5c5a2b71ac75e17bf128a8c80447f7c574777ae6 |
| docs/design/cockpit-v0/Disconnected.dc.html | 76ca2caeb982911b95b23161221e4076e15af411036b57aa598083bd0aa580ab |
| docs/design/cockpit-v0/Phase2.dc.html | 739bd50136911afaf8cac7e55214e17c79e522ce4eda6b850d13ac8ed07d4dc6 |
| docs/design/cockpit-v0/Wall.dc.html | b15ce8177c869657dffd124c1a75bd621627e3209a472065bbfe40c200ba9c4f |
| docs/design/cockpit-v0/Keys.dc.html | 6b02741696a749e54b2c87ecc0e0e70320c68ac4aaa390985cc01d86ff58972c |
| docs/design/cockpit-v0/station/index.html | 40926edc76c26e80b3bfa00f4bf592ed15acc31ed36c4881fa27e6694582faac |
| docs/handoff/cockpit-design/2026-10-22-header-and-system-facts.md | 673ce9cc8a5c376d2564354597c22f3adb63268f56aa4e21515525431f1255aa |
| docs/handoff/cockpit-design/README.md | 560ee8baa143ffa186aa637f94fa6de58cd728387f902dca3990a37839d5aa0a |

## Evidence SHA-256

Captures and harnesses remain gitignored. Paths below are relative to logs/scratch/design-review/cdh-0023/.

| Evidence | SHA-256 |
| --- | --- |
| after-calm-1440.png | 540ca0fa9ce9a4e09ed48636b1b2f6078c4611174ef0a16fee36dea88b8f0648 |
| after-calm-2560.png | 3d5d8955b932b07a40ba5d0e44800fe636a4ce5e49ce4b797147da5560d432fe |
| after-calm-320.png | 6eeb4feb6b8804a049be70df51c287ac1cbf95381a5ed1e7ec700cbffaa1bf80 |
| after-calm-400.png | c2f3ae370dce815f0eb86fb89783127ffcd0c1d78fc5f1257d8bf81b93222f31 |
| after-calm-720.png | 455fb97b9239590c7e6c080e0cc2c958328ea704981c0512441ce87e859d41d7 |
| after-calm-721.png | 6631713eb6d2ca95fdf02fcf9f8ce5f950b626770f1c3e2550c66dba1db51c3b |
| after-deck-1440.png | 129d75e9490e6bcf6007807bb27ec054cba3093a87e2aebfcf3dd2893ed94cbd |
| after-deck-2560.png | 3d16828d3f072dd882c46a1bac9b2f34b8372f465791a97045fd78a8ff817d27 |
| after-deck-320.png | 92f31d13f8f711dec44dd6d6294e448f1746ee5b7aa998c1ed85136d3760859e |
| after-deck-400.png | ccc416ebf27e3c44c00734676fa2e9a9eaabfc574e424b8ff6ae1fa768b260db |
| after-deck-720.png | 432766efc29986965d2cf92b4324326c8fcc5d810ff3b21193db7b39c25f157d |
| after-deck-721.png | 3a1c9f165f2f698a37ee9cca058a1b5027d6d23b52a9d3a70ae7501a466722a5 |
| after-system-calm-400.png | ccc76efffa1cd7ae5598c5cd66d441d91b30e8b755829f72f23d22caa31ef86d |
| after-system-deck-400.png | f2ff9afca9c7829e8f6217542f24f51f1e0a473f1002adc357f11b88d0173130 |
| before-calm-400.png | 6749c7db1871ed62de982390ae9f718a5e0662e08e24ca0d227455895987f6d2 |
| before-deck-400.png | d96a974f45ce616e16abb5c83049c7271eb6a34a83f717359ee5865abc9a5fe3 |
| header-Blocking.png | 402c655268c0744d3bec2093db24075024eb755dd2eeaefc1e897bc99285db42 |
| header-Disconnected.png | ff1b57b3ce5022d4c5215f6558978fb63c7d876166486af57bff6524855f14c8 |
| header-Empty.png | a8bcacdcf5c9248942c7c96f4d064d5f582f8ddb5d7aa8b9daccacd3eba57b7c |
| header-Main.png | 892960de490cd8f992ed12c1c44d284b0692b51c3c5ae8b3a6022ab50edb20ba |
| header-Pending.png | 88c7cdd1dc32fd67c92c4f345a2af4bc7a4295c50004c387ac2bb0276ac3863e |
| header-Phase2.png | 72160fa789ca102d613b924b33d36e4ecb0f80ccc903529f6d99167294a8ebb5 |
| header-Wall.png | 88659171c52e9c976dc50643d7aaaa740eb003696e5567fead5de807efd78e75 |
| keys-desk.png | 81245a59728895fdf85dd7b05486cf5975ba59da45dad50d00eb66e8e9925693 |
| keys-station.png | 2752c63be5afed2456cf24d2da9454c6eff384a6aa86d6b295410290c4d3780c |
| keys-wall.png | 9fd68e0b45b5e36ef2038f99268e771f69b57fa7cc9df9ec2c3ba1ea1372461f |
| migration-inputs.json | 6419d9be4b7c85cf36d431f329db3502c59b0a88c4499cbcfad8f3af3c09b12c |
| source-checks.json | eed253a2afce9198061b0e9baf4ea30466b92738a93999ea81141abcc8120bc3 |
| station-manifest.json | 9f188838e8bf07b15de15279918010616b1f1f3912d8ba6f74cde3cf516b2ba7 |
| check-source.mjs | 9e4501b7868f0933c6abaf6eaf828f9c42c9db12065d1ad47a84f70f16df765b |
| verify.mjs | d7ba943dffb522af4c0dbb7f8b4139ecf4182c96e88966bfaaa3d8d2708ba5f8 |
| make-check.log | 126e90054b4df55a6edc9736d132c6104caf5eee83a4af8b3fa7b75491546172 |
