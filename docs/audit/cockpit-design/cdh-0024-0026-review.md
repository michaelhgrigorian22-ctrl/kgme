---
id: AUDIT-CDH-0024-0026-REVIEW
type: report
created: 2026-10-25T13:25:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0024
  - CDH-0026
  - AUDIT-CDH-0024
  - AUDIT-CDH-0026
  - docs/design/cockpit-v0/ at 8f49559
  - logs/scratch/design-review/cdh-0024-0026-native/
tier: 2
status: final
handoff: CDH-0026
period: "2026-10-25"
reviewed_sha: 8f49559
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 38 (7 boards republished from 8f49559); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 12"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW34 | advisory | `station/index.html`, the room chips' `.last-event` line (`renderWords`) | Each room chip now carries its latest event as a third line, so the widest chips grew from 222 px to 257 px. At 1440 × 900 and 400 × 700 no two chips touch, which is what CDH-0026 asked to verify. At 800 × 600, a split laptop screen or the pane's own size, two pairs overlap where version 11 had none: Workshop covers Dock, Review chamber covers Archive (chips26.json; seen natively in the pane). The facts are not lost: every chip's accessible name, the pane's dispatch line and the calm wall hold the text. | The chip keeps version 11's width budget: the latest-event line is clipped with an ellipsis at the chip's former maximum (about 220 px), the full text staying in the accessible name, the pane and the wall. Scored 2 × 0.3 = 0.6: decided, approval screen. Carried into CDH-0027 as a station item, since it is the last build row. |
| CW35 | cosmetic | `Disconnected.dc.html:131` | The stale alert derives its segment count as `value / 100 * 20`, which is 18 at the recorded 90 % but a fraction at any value not divisible by 5. | `Math.round`. Folded into CDH-0027's board 6 prose item. 1 × 0.1 = 0.1. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of CDH-0024 (`d96ade8`) and CDH-0026 (`8f49559`). ADR-023: the reviewer is never the builder; Codex's reports (AUDIT-CDH-0024, AUDIT-CDH-0026) are read as data and their checks repeated by other means. CW34 is advisory, not blocking: the handoff's own verification widths hold, the text survives in three places, and the fix is one CSS budget.

**Delivered and republished.** Before republishing:
- the seven live board files of the review copy matched `2744415` byte for byte, the version the last review published; service versions 35 to 37 in between were editor saves that left the board files unchanged;
- KGME Station version 11 matched `2744415`'s page body, apart from the publish wrapper's newline;
- the eight files staged from `8f49559` (Main, Blocking, Pending, Disconnected, Keys, Wall, Tray, the station page) matched the hashes in Codex's two reports.

The review copy now carries the seven changed boards as service version 38; KGME Station version 12 is `8f49559`'s body.

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| Board 6, the band (CDH-0024) | 1368 × 70 px under the header; snapshot panels start at y = 189 | Natively at 1440 × 1000: one band under the compact header, no modal, no dimming. It holds the origin and error, last event and age, retry cadence and attempt, the durability sentence, `r`, `c` and `? when disconnected`. One "Snapshot as of 19:52:14 −07:00" line; the timeline header no longer says "frozen at", the detail no longer says "Nothing here is live". The grey static frame stays. | yes |
| CW31, the stale alert's value | 18/20 rendered, 90 % fill, numeric comparison | Natively "Codex Plus · stale ▮ 18/20 segments · high", the fill at 90 %. The source derives the text from `value = 90`. | yes; CW35 for rounding |
| Board 6, focus | Tray, band, timeline, detail with outlines | In the pane, after a click in the frame: Tab reaches the timeline then the detail, Shift+Tab back to the band, each with a visible outline. | yes |
| The moved recovery text | Under board 7's "When disconnected" | The source of board 7 holds `kgme cockpit`, the Dock-icon sentence, the launchd note, the ledger file (its previously absent System field now filled) and "the grey frame means no signal". | yes |
| Boards 3, 4, 5: the strip and the marker (CDH-0026) | One strip per board at 51.9 px; labelled ◆ on tray and timeline | Natively at 1440 × 1000 each board opens with one selected-run strip (portrait, actor, run, lifecycle, elapsed, latest event) and the ◆ sits on the tray row and the timeline's run group. Board 3's selection is now the reviewer's, as the selected event is. | yes |
| The causal connectors | Three, each explicit | Board 3's detail traces "19:43:00 cycle 1 intent ↓ 19:43:03 attempt 1 outcome ⇒ exit 1 · no text · transient · 3 s". Board 4's three strike marks end in "HALT → AUDIT-0029" beside the escalation packet. Board 5's open connector reads "intent → ◀ outcome lands here · ref=… · pending · none yet · elapsed 1 m 34 s", replacing the empty outcome row. | yes |
| Board 9, one selection | Band across the three evidence columns | Natively at 2560 × 1180 (overview scale, 0.31) the ◆ band spans the timeline, payload and detail columns; the payload column shows the reviewer's attempt and names its excerpt as drawn, full bytes not supplied. | yes, at overview scale; Codex's fixture is the pixel-level record |
| The station's bubbles | 122 observations, 0 overlaps, ≤ 1 voice per room | Standalone v12, a 60 s replay at ×2 from 19:41:20, sampled each second with my own rectangle test (measure26.json): 400 × 700, 34 of 59 samples with speech, at most 2 visible, 0 overlaps, 0 duplicated rooms, 17 samples with a bubble hidden by the layout rule; 1440 × 900, 40 of 58 with speech, at most 2 visible, 0 overlaps, 0 duplicates. | yes |
| The dispatch line | Correct at both widths | Following room 3 at 400 and 1440: "kgme.review · 19:43:03 outcome → Review chamber: cycle 1 attempt 1: reviewer exited 1 with no text", the pane between the HUDs at 400. The room chip's accessible name carries the same voice. | yes |
| Focus, calm, HUD share | 22 focused-room observations per width; calm 7 rooms | Tab after three rendered frames: 14 of 14 inside the deck band and on top at 400 and 1440, all seven rooms. Calm 1 and 3 columns, 7 rooms, 0 overflow. HUD share unchanged from version 11 (55.34 % at 400, 17.21 % at 1440). 0 page errors. | yes |
| Room chips | not measured | See CW34: 0 chip overlaps at 1440 and 400 on both versions; 2 at 800 × 600 on version 12, 0 on version 11. | CW34 |

**Reversible choices Codex recorded, accepted as recorded.** Board 6 drops the `.stale` filter and keeps the grey frame and the stale word (0.2); the band, timeline and detail are focusable regions (0.2); the ledger path fills its System field (0.1); the tray's context view is reused for the strips (0.4); the ◆ marker (0.2); the strike connector beside the packet (0.4); the drawn payload excerpt labelled as such (0.4); clipped bubbles hidden with their words kept (0.2). None reaches 0.5; recorded here.

**One observation, not a finding.** A refusal belongs to the builder's run but is spoken by the guard, so the Workshop chip and the Airlock chip both carry "kgme.guard: refused: …" as their latest voice. That is the data: one event, one speaker, two rooms it concerns.

**Evidence** is under `logs/scratch/design-review/cdh-0024-0026-native/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `native-v38-board06-1440x1000.jpg` | `6f0841175605be0cb16f250fb986f7c037a1639e97bd4b9806b265e95ad54e92` |
| `native-v38-board06-focus-band-pane.jpg` | `ff4b7eabe3a136d81970410c0486464b4fe25b556fc450ed54c3dca2a16d8d70` |
| `native-v38-board06-focus-timeline-pane.jpg` | `4b8ed594c3f9e2564744eed6231099e0e4dd09cc8390eeaf1dbae2d294516ff9` |
| `native-v38-board06-focus-detail-pane.jpg` | `378e75aedf8cbd9aeffacfe185f42f1337ba535b39d3d6cca3ec6780e517d322` |
| `native-v38-board03-1440x1000.jpg` | `5dcf757ae7302c88e92d963664d02e649ee329b4d900b9d2d04d62fe0c358ed5` |
| `native-v38-board04-1440x1000.jpg` | `d54d0424817d8ad4bb2db39f04f221cb49bf2c5dba1d9f483fbe654faab6a000` |
| `native-v38-board05-1440x1000.jpg` | `234c183950ceba7f1094a7dddd208b26e789ff9720b2aaac10a87b210439e08f` |
| `native-v38-board09-2560x1180.jpg` (overview scale) | `58fe9bed0d9c60dff3ac8f8f95678ffe28d1a82bfee4be8edbfb184a715be1f7` |
| `native-station-v12-800x600.jpg` | `3483208f2a0b5f98465b38e298ae4744df15c657500c61fa4065f8a34b5e4624` |
| `standalone-v12-bubbles-400.png`, `standalone-v12-bubbles-1440.png` | `4ed59a1127d137e465e0fb47a05738c0bd9f532881b48c2746496b36157e1b6e`, `6dad0d585b29cf663f41e8b51f2eb20af9361da39fbf551f28d05fbe448f0bf5` |
| `standalone-v12-dispatch-400.png`, `standalone-v12-dispatch-1440.png` | `ff3629338d34f097e31181a3a8375e38b2090ebcb82a62eb969a8ed20fb65ff7`, `4d8465feaad6cc73bdbd362024656c0d71c3290d8967caa7933e4621151551de` |
| `standalone-v12-calm-1440.png` | `f34a398e4f95b3c852bde1f943863fab7c93032f791c880c609fdd0231a9f7ae` |
| `standalone-v12-chips-800.png` | `cd9d56a39811382bda1a6999c9b45d8b27ba3114e4ef729ed6d71c374a5a85e0` |
| `measure26.json` (bubbles, dispatch, focus, calm, HUD share) | `c89af56d8e624455c08a3e34ee317de017914a1a852f87157aaa66ffa0253d88` |
| `chips26.json` (chip overlaps, v11 against v12, three widths) | `6ce8b4534daa6c30dd5a0d14c56f7d6f45304d8c9bda3cf8234f36212becabfc` |
| `measure26.py`, `chips26.py`, `focus-probe.js` | `6f50bd12b2d6f9ef36a7423d6a420df936b20b5d5160d4de9ce79350c3e88c11`, `cf95afe47cb16b6a2f57e6ce924afe82efa9e838f9f6fef19cb9991ded6c1e30`, `b11ffed3cd85a3d331a3501ff4eb410721bf776db5821e6c167fafedb16c3e9b` |

**Next.** CDH-0027 is `ready` as queue row 15, carrying CW32, CW33, CW34 and CW35. It is the last row of the coordinated redesign; after its native pass the canvas goes to Michou for `kgme approve --what canvas --sha <commit>`. This report is not that approval.
