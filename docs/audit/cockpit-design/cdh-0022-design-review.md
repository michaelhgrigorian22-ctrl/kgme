---
id: AUDIT-CDH-0022
type: report
created: 2026-10-22T00:48:26-07:00
handoff: CDH-0022
period: "2026-10-22"
source: inferred
sources:
  - CDH-0022
  - ADR-016
  - ADR-017
  - docs/readers/cockpit-design.md
  - control/review/design-prompt.md
  - control/review/design-reference/ui-ux-pro-max/
  - docs/design/cockpit-v0/ at 3937854530c64065e4098b22183cdb234ce75883
  - logs/scratch/design-review/cdh-0022/
  - AUDIT-CDH-0001
  - AUDIT-CDH-0003
author: codex
status: final
tier: 2
reviewed_sha: 3937854530c64065e4098b22183cdb234ce75883
---

## Findings

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | Components.dc.html:99, focused row | Three muted cells still use #6f8290 on #0e1a22, measured from the declared sRGB pair at **4.4317:1**. The time, job and duration miss 4.5:1. Main and Wall's repaired durations do not repair this specimen. | Use the already established focused token #7a8d9b on these three cells, **5.1371:1**. This is the first repair of this specimen, not a third attempt on Main or Wall. |
| F2 | blocking | station/index.html:389–394 and :111, room buttons under the phone HUD | At 400 × 700, real Tab navigation reaches **6 of 7 room buttons entirely behind the opaque top HUD**; some also extend outside the viewport. Workshop's button spans y164.27–208.25 while the HUD ends at y412.72. A focus outline exists but cannot be seen. The ground added for CW27 correctly protects HUD text; the next focus target must also be protected. Rubric: focus-not-obscured, row 100. | Keep the opaque HUD and make the focused room control fully visible in the available deck band. Measure all seven targets after Tab, including following a room and returning from calm. Do not restore transparency or change the approved camera default. |
| F3 | blocking | Main.dc.html:61–63; Empty:49–51; Blocking:61; Pending:61–63; Wall:63; station/index.html:109, :725 | Decorative micro-labels carry unique facts. Examples are the selected ledger month's path and origin on the host boards, and the station's replay date, range and speed. The host noise conditional and the station's calm CSS remove those facts. The station also hides its micro-labels below 721 px. This violates the one rule independently of whether the sample values are real telemetry. | Put those facts in normal content, preserved in calm and on phones. Audit the other micro-label hosts for the same issue. Keep decorative copies only where they mirror retained text. Do not solve this by deleting the facts. |
| F4 | blocking | Main.dc.html:105–107, :193–197; Blocking:83; Pending:83; Disconnected:78; Wall:86 | Five activity grids expose **96 / 96 / 96 / 96 / 240 cells** with a style field alone. Per-cell values are encoded only by colour. In Blocking and Pending the final cell's state also changes only by colour; totals elsewhere do not reproduce the individual values. | Add a readable non-colour encoding of the supplied values, with explicit blocking/pending markers and a legend. Preserve the supplied arrays; 7 and 9 are state sentinels here, not seven or nine events. Keep the empty board's explicit no-events explanation. |
| F5 | blocking | Disconnected.dc.html:113, :118; Keys.dc.html:81, :140 | The disconnected board advertises **r = retry**, while the map advertises only **r = run filter**. The context override is absent from the map. This is a missing documented binding, not a demand to implement keyboard handlers in static drawings. | State that r retries while disconnected and cycles the run filter otherwise, in the key face and map explanation. Preserve the existing text-field exclusion. |
| F6 | advisory | Wall.dc.html:132–143, raw payload column | The column says it is the focused event's raw payload, but shows the builder's full session transcript while the focused timeline/detail event is a reviewer event. The content relationship is contradictory even in a sample. | In a coordinated build, label this as the builder session stream with its run identity, or make the stream follow the selected reviewer event. Recommend the latter, **2 × 0.2 = 0.4**, because selection should explain what the adjacent evidence belongs to. |
| F7 | advisory | Main.dc.html:103, :194; Blocking/Pending/Disconnected activity grids | The desk grids draw 96 samples under a 60-minute label and describe events per minute. A minute-per-cell reading is inconsistent; the source supplies no bucket duration. | Define the time-bucket contract before implementation and label it. Recommend 60 one-minute buckets for the desk and 240 for the four-hour wall, **2 × 0.2 = 0.4**. Do not silently truncate these review fixtures in a correctness patch. |
| F8 | advisory | Keys.dc.html:81–86, :150; station/index.html:671–680 | Station p/r/digits mean pause/restart/rooms, while desk p/r/digits mean payload/run/classes. Separate pages currently scope these safely. The answered w cycle joining desk, wall and station is not yet described by the map. | The coordinated integration needs a visible current-surface key map, including the accepted three-way w cycle. Recommend context-specific legends under the existing ? key, **3 × 0.3 = 0.9**; do not treat separate-page handlers as a present duplicate-binding failure. |

## Verdict

BLOCK: 5 blocking findings at the reviewed SHA.

## Notes

The decision this review feeds is Cowork's next coordinated design handoffs, read by Michou and Cowork. The strongest case for the current density is that the canvas is also a specification: boards 1, 7, 10 and 11 need side-by-side comparisons. Their reference density is useful. On the operating boards, however, the same clock context, run identity, state, keyboard hint and explanatory sentence often appear in several competing places. The philosophy calls for more useful relationships between parts, not merely fewer painted objects.

**The sum.** The ledger becomes a place inhabited by recognisable workers: the tray answers who, the timeline answers what happened, the detail answers why, and the station makes responsibility spatial. A skeleton judge and a cherub guard are welcome because their roles remain readable in words and the operator can still inspect the underlying event. No single board provides that combination. Keep that relationship and the seven distinct silhouettes. Give each fact one primary home, with deliberate short mirrors for navigation; expend the visual extravagance on the transitions between responsibility, event and evidence.

**Scored recommendations.** Scores below are stakes × edge. A retained settled decision has score **1 × 0 = 0** and is not reopened. A cell marked “none, 0” proposes no change. These are specifications for future coordinated build rows, not authority to perform a redesign in the blocking fix loop. “Move” always preserves a reachable fact under an already drawn key.

| Board | Keep | Cut | Merge | Move behind a key | Add |
| --- | --- | --- | --- | --- | --- |
| 1 Components | Keep the comparative palette, state frames, row anatomy and tray specimen; **1 × 0 = 0**. | Remove repeated manifesto prose after retaining one complete statement; **1 × 0.2 = 0.2**. | Put the noise specimen and its calm explanation beside one another as a before/after comparison; **2 × 0.2 = 0.4**. | None; this is the reference sheet, **0**. | Show one selected event with its frame, glyph, text and tray role aligned as one cross-component specimen, replacing separate duplicated examples; **2 × 0.3 = 0.6**. |
| 2 Empty | Keep the three concrete ways events arrive and the read-only boundary; **1 × 0 = 0**. | Remove the empty detail's repeated invitation and the visual weight of four vacant auxiliary panels; **2 × 0.2 = 0.4**. | Make one “nothing recorded yet” area hold the zero counts and the three next steps; **2 × 0.2 = 0.4**. | Put the complete event-shape field list under the already advertised Enter detail; **2 × 0.2 = 0.4**. | Replace the blank matrix with a single dormant first-event cursor aligned to the future timeline, retaining all zero/no-reading facts; **2 × 0.3 = 0.6**. |
| 3 Live | Keep the dense chronological ledger, causal parent link, portraits and active-run tray; **1 × 0 = 0**. | Remove repeated global key hints from local panels once ? remains complete; **2 × 0.3 = 0.6**. | Make the selected run's portrait, lifecycle, elapsed time and latest event one context strip instead of competing headers; **3 × 0.3 = 0.9**. | Move routine versions, provenance, latency distribution and quota reset details into ? system context, preserving visible alerts; **4 × 0.5 = 2.0**, brief B1. | A short parent-to-outcome trace that replaces a repeated run-ID line would make the drawing more expressive and more explanatory; **2 × 0.4 = 0.8**. |
| 4 Blocking | Keep the magenta frame, explicit HALT, three-strike history and escalation packet; **1 × 0 = 0**. | Cut the repeated HALT prose in subordinate captions, keeping one actionable sentence plus the state label; **2 × 0.3 = 0.6**. | Join strike history and the root-cause evidence into one causal escalation strip; **3 × 0.3 = 0.9**. | Keep full hashes and payload fields behind p and parent evidence behind u; **2 × 0.3 = 0.6**. | Let the three strike marks terminate at the packet's existing link, replacing an ordinary duplicated packet label; **2 × 0.4 = 0.8**. |
| 5 Pending | Keep the distinction between attempted work and a missing outcome; **1 × 0 = 0**. | Reduce four repetitions of the 1m34 elapsed value to one timer and short mirrors only where navigation needs them; **2 × 0.2 = 0.4**. | Present intent, waiting timer and future outcome position as one pair; **3 × 0.3 = 0.9**. | Move the write-ahead explanation into Enter detail, keeping “waiting for outcome” visible; **2 × 0.3 = 0.6**. | A visible open connector from intent to outcome can replace both the empty outcome row and a separate waiting explanation; **2 × 0.4 = 0.8**. |
| 6 Disconnected | Keep the last-seen timestamp, stale tray, retry cadence, origin/error and file-backed durability explanation; **1 × 0 = 0**. | Remove decorative jitter while calm is active; **1 × 0.2 = 0.2**. | Replace the blocking visual treatment of the modal and dimmed workspace with one persistent disconnect band; **3 × 0.5 = 1.5**, brief B2. | Move the long recovery explanation into ? while the band retains retry and last-seen; **2 × 0.3 = 0.6**, contingent on B2. | Give the existing snapshot one clear “as of” boundary, replacing repeated stale captions; **2 × 0.4 = 0.8**. |
| 7 Keys | Keep the physical keyboard silhouette, context guard and visibly reserved Phase 2 keys; **1 × 0 = 0**. | Remove repeated explanatory introductions, not bindings; **1 × 0.2 = 0.2**. | Group each binding's full explanation beside its key family, retaining a complete readable reference; **2 × 0.3 = 0.6**. | Keep this as the ? destination; no second help destination, **0**. | Add a visible desk/wall/station context label and reuse the same map for the active surface, replacing contradictory generic legends; **3 × 0.3 = 0.9**, F8. |
| 8 Phase 2 | Keep dashed, labelled previews and the separation between read-only v0 and future commands; **1 × 0 = 0**. | Remove duplicate “not yet bound” prose after keeping explicit labels on every control; **1 × 0.2 = 0.2**. | Arrange approval, model and command specimens around one explained future interaction instead of several simultaneous workspaces; **3 × 0.3 = 0.9**. | Put the longer future-flow explanation in the drawn ? help; **2 × 0.3 = 0.6**. | Use the guard and arbiter's two distinct roles to explain request versus ruling in that one example, replacing duplicate status furniture; **2 × 0.4 = 0.8**. No activation is proposed. |
| 9 Wall | Keep the four-column evidence workspace and its place beside the station; **1 × 0 = 0**. | Remove repeated selection metadata in payload and detail headers; **2 × 0.3 = 0.6**. | Join the selected event and raw evidence under one selection identity, correcting F6; **2 × 0.2 = 0.4**. | Apply B1 to routine header diagnostics; **4 × 0.5 = 2.0**. Keep the raw stream visible, since that earns this layout. | A shared selection marker across timeline, raw payload and detail can replace three ordinary repeated labels; **2 × 0.4 = 0.8**. |
| 10 Sprites / cast | Keep all 49 actor/mode cells, both palettes, seven silhouettes, controlled selected animation and context examples; **1 × 0 = 0**. | Cut duplicated prose between the board and Components after preserving each mapping and constraint once; **1 × 0.2 = 0.2**. | Bring the selected figure and its actual 24 px portrait into one comparison; **2 × 0.2 = 0.4**. | None; comparison is the reference board's job, **0**. | Make the selected role's one existing event example align directly with its portrait/detail pair, replacing a redundant anatomy caption; **2 × 0.3 = 0.6**. No new character or likeness. |
| 11 Tray / host instances | Keep stacked static portraits, explicit lifecycle counts, quiet inside working and stale timestamp; **1 × 0 = 0**. | Cut the repeated lifecycle essay from host panels after retaining it on this reference board; **1 × 0.2 = 0.2**. | Let the opened a pane carry full lifecycle and latest-event explanations instead of repeating them in the compact header; **2 × 0.3 = 0.6**. | Move full run IDs and elapsed/event detail into the existing a/Enter path, keeping compact counts visible; **2 × 0.3 = 0.6**. | A shared selected-run marker between tray and timeline replaces duplicated selection captions; **2 × 0.3 = 0.6**. |
| Station, deck and calm | Keep the room topology, seven roles, c text view, accepted camera, wide calm grid and chalk silhouette; **1 × 0 = 0**. | Remove concurrent ambient speech bubbles after preserving every event in room/pane text; **3 × 0.4 = 1.2**. | Let the followed room own one event bubble and its existing pane. Keep the settled seven-second lifetime; **3 × 0.4 = 1.2**. | Put routine header diagnostics under the surface's existing a pane, retaining a clear diagnostics section and visible alerts; **4 × 0.5 = 2.0**, B1. | One followed-room “dispatch” joining speaker, event and destination can replace overlapping bubbles plus repeated crew/event captions; **3 × 0.4 = 1.2**. |

**Three changes first, if taste were mine:** B1's compact operating header (**2.0**); the station's single followed-room dispatch (**1.2**); the common selected-event context strip (**0.9**). The current header wrap and wide-grid decisions were previously accepted. These are new recommendations under the new philosophy, not declarations that those accepted tradeoffs were mistakes. No recommendation reopens the station's direction, joining the wall, or Michou's likeness; all three answers remain taken.

**Evidence and limits.** All 26 tracked design files matched the named commit byte for byte before review. The commit's author is Michael Grigorian, with Claude coauthorship. Earlier Codex patches are part of this mixed-history source; the 11 native board images and subsequent native passes are Cowork evidence, not a claim of independent vendor verification by Codex of its own earlier builds. The source read includes all 11 drawings, index, seven SVGs, standalone fixture and station. Canonical geometry comparisons pass all **30** existing sprite tests. The seven assets total **54,782 bytes and 582 elements**; shared CSS plus JS total **21,513 bytes**, making **76,295 bytes**, below the provisional 524,288-byte target. Per-actor counts are builder 98, reviewer 86, arbiter 76, guard 88, scribe 71, Michou 95 and stranger 68. The 40 sample events validate with the repository's event validator and describe six runs.

The vendored rubric was used locally as a checklist, including focus, target size, motion controls and live-status context. Three.js uses a consistent pinned 0.182.0 module graph, one renderer and a capped pixel ratio. Its orthographic resize updates frustum bounds; a rubric written around perspective camera.aspect is not a reason to replace that camera. No library upgrade, remote source or style generator was used.

Cowork supplied 11 native board JPEGs plus the canvas overview from review copy version 30. Their 800 px widths are downscales of the stated design viewports, not 800 px layout tests. They establish composition; exact contrast comes from source, not JPEG sampling. Every supplied image was inspected. The fresh six station PNGs are Codex standalone Chrome 155.0.8059.85 captures on the Mac with ANGLE/SwiftShader, DPR 1 and only loopback resources. Local three@0.182.0 was already present. The helper changes import paths, not source behavior. Each capture was loaded with at=19:52:00 and speed=1, then paused using the page's control; capture clocks are recorded before and after in the station manifest.

| Viewport | Top / bottom HUD, px | Calm columns / horizontal overflow | Observation |
| --- | --- | --- | --- |
| 400 × 700 | 412.72 / 133.81 | 1 / 0 px | The HUDs occupy 546.53 px, leaving 153.47 px of deck. Six room controls become entirely hidden when focused. Calm scrolls, but only its introduction initially fits between the HUDs. |
| 1440 × 900 | 134.94 / 73.94 | 3 / 0 px | All seven room controls have visible centres. Several crew bubbles compete in the same area, supporting the 1.2 taste recommendation, not another blocking overlap claim. |
| 2560 × 900 | 80.94 / 48.00 | 6 / 0 px | All seven room controls have visible centres. The accepted calm grid leaves one room on its second row. That is not reopened merely because blank space remains. |

The station has zero recorded page errors and no external resource requests. Its manifest's PASS refers only to the harness's layout/load assertions; it does not override this design BLOCK. Real Tab events and hit-testing establish F2. No new 30-second performance capture was taken: the supplied CDH-0001 report records 30,001.8 / 30,002.8 ms motion/calm runs, 50 static portraits plus one detail, 33.4 ms p95 RAF intervals in both, zero long tasks, and 56 input/scroll samples per run on the M4 Pro. That historical fixture evidence does not certify station GPU cost, energy, native canvas performance or present physical-display smoothness. CDH-0003's 101 canonical/use raster comparisons and native follow-up reports remain historical evidence. Native import, focus, clicks, font paint and canvas approval for any new fixes still belong to Cowork and Michou respectively.

The reviewed source hashes identify the original bytes, before any fix cycle.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/design/cockpit-v0/Blocking.dc.html` | 18117 | `ec2c61c00c4bcc085a78f77e0c1628807c42acd5ec844dae673890cac06f7b6e` |
| `docs/design/cockpit-v0/Components.dc.html` | 17409 | `a0d8fa4d0f3124938812e22bbe03961ad5467df82357c838fcdf0f373e4b52d7` |
| `docs/design/cockpit-v0/Disconnected.dc.html` | 13633 | `4e13f38b0113f91be1b316820193d6d45b79220e4e2b975a6e0480e0f8f03592` |
| `docs/design/cockpit-v0/Empty.dc.html` | 12239 | `5de581859ed272ac290af6041253c6496583b357e576e849cabc06ec5400fddd` |
| `docs/design/cockpit-v0/Keys.dc.html` | 13093 | `6ab106dcc65cfb2ddc27648942d69b3b2f8688e4d52eec3279ff38a32fd2e4f5` |
| `docs/design/cockpit-v0/Main.dc.html` | 18575 | `9530b4bbebec1eac1cede407a672d55ebce6cc9370150bf50dd7ea1132228ddc` |
| `docs/design/cockpit-v0/Pending.dc.html` | 16586 | `15cb75b53c47267ff85689e0646a1cff068581f82c8cfd2dab5176e523e414da` |
| `docs/design/cockpit-v0/Phase2.dc.html` | 13493 | `5bd59761b2dbc37ad9bf1620e9cb5dec1300f6209c4f9791168f228039161539` |
| `docs/design/cockpit-v0/Sprites.dc.html` | 81036 | `e54f58bfd3dd315d0e82830587008be202b761f6c7593b5e7d344f433683ca7a` |
| `docs/design/cockpit-v0/Tray.dc.html` | 83887 | `72e5d11cd22bdc9af65711d06dfee3493bf6623f2b6c87a707d2e3e0d87bfd34` |
| `docs/design/cockpit-v0/Wall.dc.html` | 23801 | `6730cb1245c68d4629c80ff5eb8b00c5fa3aa92b0d220e790338067879391413` |
| `docs/design/cockpit-v0/canvas.json` | 4011 | `a082ca20ffbb0397227613bdb483df80c869c1893bf0f6501ae9ffa266bf897f` |
| `docs/design/cockpit-v0/chibi/README.md` | 8285 | `c4059a5ee64560bdcc10e96786882cc92c5ebfbbfc7640efd70c938a99b054e2` |
| `docs/design/cockpit-v0/chibi/arbiter.svg` | 8166 | `8d7bb211574d347a5038dfb1b38aa7facc414369f24d7e640102059b16bdcdc1` |
| `docs/design/cockpit-v0/chibi/builder.svg` | 8775 | `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e` |
| `docs/design/cockpit-v0/chibi/characters.css` | 5724 | `7fcb692d48d26201744cf6795c899cdbaa9a93750bbb9d952407921bcd19a020` |
| `docs/design/cockpit-v0/chibi/characters.js` | 15789 | `900872eec1de4f457c120eeeedb068d4a2346ceeb9e803acfb20ac3dd0b4e26e` |
| `docs/design/cockpit-v0/chibi/guard.svg` | 8053 | `da6639d6cabae91e7fa622754a6fc27c9dc7c823e3657d34340a76729f6b31fa` |
| `docs/design/cockpit-v0/chibi/michou.svg` | 8730 | `46831a1e9d6ebf8991beb59b0281779ee6bc7869798fd2b168822b0f2bdfa9c7` |
| `docs/design/cockpit-v0/chibi/preview.html` | 12220 | `2681c521c3de5091b82f4cb1c829071d4f3be8e60c54fb0a6e1c1d19561aff23` |
| `docs/design/cockpit-v0/chibi/reviewer.svg` | 7988 | `f444d74e398ab00a5a52e9160c50bf433113ba9115e0fe65efbb51b13e9a062b` |
| `docs/design/cockpit-v0/chibi/scribe.svg` | 6717 | `cba7d68489569c0dc783086829752807af719b3473dd9d0286a00807d39fc026` |
| `docs/design/cockpit-v0/chibi/stranger.svg` | 6353 | `7fed1b5845d5934e37580d7070c35adfbabb9e84cc9b87a0e536ef602ab81516` |
| `docs/design/cockpit-v0/station/README.md` | 6300 | `6663ead8cba8947d804230c66e6d60369af91843a7a4b55c179373f65b85dfd3` |
| `docs/design/cockpit-v0/station/index.html` | 61233 | `45dbb6db88964982430870d00a3ed00246e7a3d151b5ae1e841f466f828dd129` |
| `docs/design/cockpit-v0/station/sample-events.jsonl` | 20110 | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |

All evidence below remains gitignored under `logs/scratch/design-review/cdh-0022/`. The supplied manifest is unchanged.

| Evidence | SHA-256 |
| --- | --- |
| board-01-components-1440x2400.jpg | `55c1f0e2f5781e06de05c066223d51fb37a7651d1560d16ccbde79d7364b8e85` |
| board-02-empty-1440x990.jpg | `ec93a6ad7c9eb69f78faf8e1fa57be5e5872bb2a2f5a888b9ca3e107996a9207` |
| board-03-live-1440x990.jpg | `7c1ded8737b80a1363d499e0500f3d2dba0363f9e3bacdbadbcf8ca41f0b3aae` |
| board-04-blocking-1440x990.jpg | `580adc5784cbc7a553bc39ffc53335da313fe9647ab6b367e71a29580c08a364` |
| board-05-pending-1440x990.jpg | `4b0a751b78e9adc734b6b0d40740e026855baccbb131feabfa2679da4048856e` |
| board-06-disconnected-1440x990.jpg | `6cda5be5ce96b795be98c66ae9586220c7b779a74b89fc3b7205e0dbeca84e81` |
| board-07-keys-1440x990.jpg | `7d27d905fb9bd4ce103275e755675d903d32641a45165116ce1709e3b6ed6083` |
| board-08-phase2-1440x990.jpg | `7b0a4e20402f17ca8e7b6189e5d56e69fcd56c5830e62c55f259ef9c543a847f` |
| board-09-wall-2560x1170.jpg | `e333c46ce2b74bd27b05637d123d5a7ff167171a9be6c30d3eb5f94dce157902` |
| board-10-sprites-1440x1590.jpg | `bd641dea0488d97861de998310602c347e1ec9735fd4deb5e15d926e32f987b9` |
| board-11-tray-1440x1030.jpg | `57afe07d2bc69c7b55cf1ad10b04f86a5ef376b94978154af4ad0a89209c3d3f` |
| canvas-overview-643px-pane.jpg | `935c528ba773876bf1387ca3c2ec2980e9bad230704a791c52d13dc544832d56` |
| manifest.json | `f00332c0292f94a62061e808802e318adbdf9262e81b75bc013548caf7c01a0a` |
| review-deck-400.png | `bc2c47fb68871b9271313cbced2f507b90db3095762251f59a639b22b0270b09` |
| review-calm-400.png | `4e321757c2a7ce234c2d3c2499b212344a35d16c78d1f18a3a3335417b73d62e` |
| review-deck-1440.png | `48062ff56658ecb8b6c0c99597034be38a4c37a6eb91cc4e3c711930f4e70c9f` |
| review-calm-1440.png | `98e54625751927518676fd3e5202402fec042ef78636bbba71862b55c662bb64` |
| review-deck-2560.png | `5636cbfa0b0e58b3f4adb483216ef5f4bcee79c2626ac7e77bca8e0bb2206697` |
| review-calm-2560.png | `0aa42e87f79d112edd6a0637ba7f3f4e5b203b2a2f2be50b721ce404a88c68f5` |
| station-manifest.json | `8f6c8ecb738c58ee02cc214a4c3fc55f75b3c31db3b94cfad50abeb2910838ce` |
| station-review.mjs | `9514906fd60753a954c7f5e2b6db6942462c3a9c6b106d8f74d41c4f058d0d38` |
| review-inputs.json | `cc4cd435e821f7850bc0bc6538026c63b7bbb2a4cc8ca2d0bd19f5f666016f8b` |
| source-audit.json | `1359d62d34f34ccca2d3dc9e749560a7fcfe870e1cd1da76d1739472901b2e17` |

**Batched brief for Michou.** These are the only new recommendations at or above 1.5; Cowork should turn the response into coordinated build rows. They do not hold the five blocking repairs open.

1. **B1, operating-header hierarchy, 4 × 0.5 = 2.0.** Recommend a compact default header with clock, live/stale/halt, active-run summary and actionable quota alerts. Preserve versions, provenance, full quota/reset details and latency diagnostics under ? on desk/wall and the existing a pane on the station. The 400 px measurement shows why this matters: 78.1% of the viewport is currently HUD. Approving the hierarchy authorizes a coordinated design; it does not pre-approve the final canvas.
2. **B2, disconnected presentation, 3 × 0.5 = 1.5.** Recommend replacing the central modal and globally obscured snapshot with a persistent disconnect band retaining last-seen, origin/error, retry and durability text. Keep the retained ledger inspectable. This changes the prominence of a failure state, so the tradeoff belongs to Michou.
