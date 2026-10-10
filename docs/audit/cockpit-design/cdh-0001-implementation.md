---
id: AUDIT-CDH-0001
type: report
created: 2026-10-09T22:43:59-07:00
author: codex
source: inferred
sources:
  - CDH-0001
  - docs/handoff/cockpit-design/README.md
  - docs/readers/cockpit-design.md
  - docs/readers/cockpit-design-chatgpt.md
  - tools/review/design-prompt.md
  - docs/design/cockpit-v0/chibi/
  - memory/attachments/cockpit/chibi-reference/approved-cast.png
  - memory/attachments/cockpit/chibi-reference/style-reference.png
  - memory/attachments/cockpit/chibi-review/cdh-0001/
tier: 2
status: final
handoff: CDH-0001
period: "2026-10-09"
---

# CDH-0001 implementation delivery

The 7 original SVG characters, 7 modes and board 10 integration are delivered locally. All 98 actor/mode/palette combinations passed the standalone behavior checks. The 2 required 30-second captures completed on the target Mac in headless Chrome. Native canvas import/playback and final visual acceptance remain unverified: Cowork must perform CDH-0002, and Michou retains approval of the design. This report does not close HANDOFF-0036 or start HANDOFF-0037.

## Delivered result and visual interpretation

Each of the 7 characters uses original authored geometry with a 240 × 280 source viewBox, 6 semantic material roles and restrained cel shading. The 24 px version deliberately crops the head; the 72 px version displays the whole character. The source preserves oversized heads, readable expressions, compact bodies and the specified identifying props. The painted concept's scratches, dense chains and fabric texture are simplified into contours, shading planes and sparse motifs for the 72 px display. This is an illustrated vector interpretation of the approved sheet, not a claim of pixel-identical painterly reproduction. Michou's figure is a stylized avatar, not a verified likeness.

The builder was rendered first at 24, 72 and 240 × 280 CSS px in both palettes before completing the other 6 actors. Visual inspection caught and corrected 2 stray boot strokes and the arbiter staff overlapping an eye socket. The final overview and both 49-cell matrices were inspected at delivery. These browser images are source-identified evidence, not native canvas exports or visual approval.

The 49-cell phosphor matrix and all 50 run portraits stay static. Only 1 selected detail root may animate. Actor-specific prop motion, waiting glances, transient sagging, class-colored fire, completion halos and authored chalk outlines reuse the same body/head/prop groups. The asleep detail is intentionally static; its 24 px portrait uses a muted closed-eye head crop. Every sample carries actor, mode, lifecycle, class and event text separately. The phrase `no outcome` indicates an absent failure class, not a new class.

The 2 approved palette placements remain intact: phosphor in timeline/run headers, sticker in detail specimens and the illustrated Phase 2 selector. The fixture's palette control affects the selected detail only. Fire is magenta for the written blocking class, completion halo is green for ok, and inactive chalk is muted. Fixed ochre fabric and the guard's material halo carry no status meaning.

## Changed paths and scope

The 11 new files under `docs/design/cockpit-v0/chibi/` are the 7 named SVGs, `characters.css`, `characters.js`, `preview.html` and `README.md`. The 2 existing design files changed are `Sprites.dc.html` and `canvas.json`. This report and the review PNGs are the remaining named outputs. The handoff closeout changes only its status and adds its completion timestamp.

Board 10 retains its 1440 × 1500 dimensions, position, native `./support.js` reference, `x-dc` / `helmet` / `DCLogic` format, original header micro-label and exact Voice section. It embeds the same standalone fixture via a relative iframe, with an internal scroll surface so all 49 specimens, palette pairs and original context examples fit without moving the board. The frame height is 780 px. The original outer 36 px padding and 22 px gap are retained. Only note s3's sprite-specific text changes in `canvas.json`; all board dimensions, positions, ordering and other notes remain byte-equivalent in parsed values. All 9 other artboards match their pre-session SHA-256 values.

The original context facts, including the 212-event run, 9-passed Bash row, transient reviewer sample, cycle-3 halt and dashed inactive Phase 2 approval example, are retained inside the fixture. The keyboard map, 3 strike boxes, frame rules, configuration and application runtime are outside this change. No dependency was installed. No commit, push, public publication, external message or approval event was performed. Unrelated concurrent edits were observed in sync/schema/audit/ledger files and left untouched by CDH-0001; a whole-repository unchanged claim would be inaccurate.

## Verification actually performed

| Check | Observed result |
| --- | --- |
| SVG syntax and source | All 7 files pass XML parsing and `xmllint --noout`; the final script passes `node --check`. SVGs contain no raster image dependency or painted rectangular background. |
| Complete state coverage | All 98 selections, 7 actors × 7 modes × 2 palettes, have matching text, palette variables, current effects and actor-specific animation names. |
| Actual dimensions | The 50 timeline portraits measure 24 × 24 CSS px, the selected detail measures 72 × 72, and all 50 event rows measure exactly 22 px high. |
| Simultaneous animation | The maximum is 3 CSS animation instances on 1 character in idle (body and 2 eye expressions). Working has 1 instance; asleep has 0. All 50 portraits have 0 animations. |
| Mode replacement | Changing working to done cancels the previous jackhammer animation; only the halo animation remains. No previous mode effect stays enabled across the 98 selections. |
| Geometry preservation | All 50 event-row rectangles match across 2 moving-frame samples, calm mode and actual removal of every SVG. |
| Text preservation | All 101 selected-detail/header/event text entries are identical before calm, during calm and after removing all 118 SVG roots. |
| Calm | All 118 SVG decorations become hidden without losing facts; active animation count is 0. |
| Reduced motion | Chromium's actual emulated `prefers-reduced-motion: reduce` media query yields 0 animations, including after the preview control selects blocked mode. CSS independently prohibits animations. |
| Offscreen | Scrolling the selected detail outside the viewport yields 0 animations; scrolling it back restores the eligible working animation. |
| Hidden | A real CDP page lifecycle transition produces `document.hidden === true` and 0 animations. No visibility property was stubbed. |
| Local artwork | The fixture requests 10 same-origin resources, its HTML, CSS, JS and 7 SVGs, with 0 external requests. The unchanged native board still declares its original Google Fonts links. |
| Errors and scope | The final behavior capture has 0 browser errors. The exact original Voice section is retained, and the targeted diff passes whitespace checks. |
| Outer board bounds | A standard-browser extraction of the existing board markup measures 1500 px document height at 1440 × 1500. This check omits the native support renderer and remote fonts; it is a bounds proxy only. |

The native design interface was not opened by Codex. Relative iframe loading, native script/support behavior, native playback, native reduced motion and native font/layout acceptance are CDH-0002 checks. If the editor rejects the iframe or relative local source, Cowork must name that capability and report the acceptance gap. No replacement `support.js` was fabricated.

The standalone source retains JetBrains Mono first in its font stack without installing or downloading a font. The measured platform font result was {"fonts":[{"familyName":"Menlo","postScriptName":"Menlo-Bold","isCustomFont":false,"glyphCount":11},{"familyName":"Menlo","postScriptName":"Menlo-Regular","isCustomFont":false,"glyphCount":184}]}. Thus browser font evidence does not certify native JetBrains rendering. Returning the lifecycle-frozen headless target to active did not restore its visible state; original-target visibility resumption is unverified in this harness. Subsequent screenshots and timing captures used fresh visible targets. An earlier hidden-target timing attempt was discarded.

## Source size and rendered complexity

| Asset | Raw bytes | SVG elements including root/metadata |
| --- | ---: | ---: |
| arbiter.svg | 8166 | 76 |
| builder.svg | 8775 | 98 |
| guard.svg | 8053 | 88 |
| michou.svg | 8730 | 95 |
| reviewer.svg | 7988 | 86 |
| scribe.svg | 6717 | 71 |
| stranger.svg | 6353 | 68 |
| All 7 SVG assets | 54782 | 582 |
| characters.css + characters.js | 21534 | n/a |
| Provisional target total | 76316 | n/a |

The measured total is 74.53 KiB against the 512 KiB provisional target, or 14.56% of that target. The comparison includes the entire fixture JavaScript, including diagnostic/profile helpers, and shared CSS. The separate HTML/README/board/reference/evidence files are not counted as character assets or shared animation code. No compressed-size figure is presented as a runtime measurement.

The profile scene's DOM complexity was {"totalSvgRoots":118,"totalSvgElements":9502,"visibleSvgRoots":51,"visibleSvgElements":4117}. The count called visible in the instrument means a nonzero layout box with visible CSS, including portraits clipped by the list's scroll viewport; it is not a claim that all 50 are simultaneously painted onscreen. Title, description and default style metadata are omitted from decorative inline clones, avoiding duplicate IDs and repeated default CSS while retaining the canonical SVG metadata. Normal operation uses no requestAnimationFrame loop, per-frame layout reads, WebGL, blur animation or animation dependency; RAF runs only inside an explicitly requested measurement capture.

## Target-Mac timing evidence

The 2 captures used Chrome/155.0.8059.39, headless, on an Apple M4 Pro with 12 logical CPUs and 24 GiB RAM. The viewport was 1440 × 1100 CSS px at DPR 2. Each scene had 50 static phosphor run portraits and 1 selected 72 px sticker builder in working mode. Calm is the same scene with decorations hidden and 0 CSS animations. Captures ran sequentially with a focused input probe, CDP key down/up events and wheel scrolling at approximately 500 ms intervals. Full capture summaries below preserve the measured values.

| Metric | Motion | Calm baseline |
| --- | ---: | ---: |
| Capture duration, ms | 30001.80 | 30002.80 |
| RAF intervals, count | 899.00 | 899.00 |
| RAF interval mean, ms | 33.33 | 33.33 |
| RAF interval p50, ms | 33.30 | 33.30 |
| RAF interval p95, ms | 33.40 | 33.40 |
| RAF interval p99, ms | 33.40 | 33.40 |
| RAF interval maximum, ms | 33.50 | 33.50 |
| RAF intervals above 50 ms, count | 0.00 | 0.00 |
| Long tasks, count | 0.00 | 0.00 |
| Long task total, ms | 0.00 | 0.00 |
| Input event samples, count | 56.00 | 56.00 |
| Input event to next frame p95, ms | 27.60 | 29.20 |
| Scroll event samples, count | 56.00 | 56.00 |
| Scroll event to next frame p95, ms | 0.20 | 0.10 |
| Active CSS animations at start/end | 1/1 | 0/0 |

RAF mean differs from calm by 0.00 ms and p95 differs by 0.00 ms in these 2 captures. This is a descriptive comparison, not a statistical claim. Long-task support was available in both captures. The keyboard probe and scrolling produced the sample counts shown above; latency starts when JavaScript handles the event and ends on its next RAF callback, excluding physical input and OS/browser dispatch time.

Headless Chrome reported no macOS display-link connection. These are observed headless RAF intervals, not physical-display FPS, GPU timing or whole-cockpit performance. CPU utilization, energy, physical keyboard latency and visible-display smoothness remain unverified. The 75 KiB-scale source size is not evidence for any of those unmeasured properties. The hardware model and RAM are machine metadata, not utilization measurements.

<details>
<summary>Exact capture summaries and interaction observations</summary>

```json
[
  {
    "capture": "CDH-0001 standalone fixture",
    "timestamp": "2026-10-10T05:41:34.059Z",
    "requestedMs": 30000,
    "elapsedMs": 30001.80000001192,
    "reason": "completed",
    "initial": {
      "actor": "builder",
      "mode": "working",
      "palette": "sticker",
      "calm": false,
      "profile": true,
      "inView": true,
      "hidden": false,
      "reducedMotion": false,
      "animatedRoots": 1,
      "activeAnimations": 1,
      "animationNames": [
        "chibi-hammer"
      ],
      "matrixCells": 49,
      "staticRunPortraits": 50,
      "activePortraitAnimations": 0,
      "devicePixelRatio": 2,
      "viewport": {
        "width": 1440,
        "height": 1100
      },
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"
    },
    "final": {
      "actor": "builder",
      "mode": "working",
      "palette": "sticker",
      "calm": false,
      "profile": true,
      "inView": true,
      "hidden": false,
      "reducedMotion": false,
      "animatedRoots": 1,
      "activeAnimations": 1,
      "animationNames": [
        "chibi-hammer"
      ],
      "matrixCells": 49,
      "staticRunPortraits": 50,
      "activePortraitAnimations": 0,
      "devicePixelRatio": 2,
      "viewport": {
        "width": 1440,
        "height": 1100
      },
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"
    },
    "frameIntervalMs": {
      "count": 899,
      "mean": 33.33203559510568,
      "p50": 33.30000000000018,
      "p95": 33.400000000001455,
      "p99": 33.400000000001455,
      "max": 33.5,
      "over50ms": 0
    },
    "longTasksSupported": true,
    "longTasks": {
      "count": 0,
      "totalMs": 0,
      "maxMs": 0
    },
    "inputEventToNextFrameMs": {
      "count": 56,
      "mean": 24.533928572067193,
      "p50": 24.100000008940697,
      "p95": 27.599999994039536,
      "p99": 28.30000001192093,
      "max": 28.5,
      "over50ms": 0
    },
    "scrollEventToNextFrameMs": {
      "count": 56,
      "mean": 0.08214285650423594,
      "p50": 0.09999999403953552,
      "p95": 0.20000000298023224,
      "p99": 0.20000000298023224,
      "max": 0.20000000298023224,
      "over50ms": 0
    },
    "limits": "Frame intervals are observed RAF cadence, not GPU render time. Input/scroll latency begins at event handling, not hardware input. No interaction samples means unverified. This fixture does not certify future cockpit performance.",
    "browser": {
      "protocolVersion": "1.3",
      "product": "Chrome/155.0.8059.39",
      "revision": "@3ff7ac5a9224be9156d7f8703a06e22890aafd34",
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36",
      "jsVersion": "15.5.35.20"
    },
    "harness": {
      "start": "2026-10-10T05:41:04.001Z",
      "elapsedWallMs": 30934,
      "interactions": {
        "count": 58,
        "first": {
          "time": 885.6000000089407,
          "textLength": 1,
          "scrollTop": 0,
          "animations": 1
        },
        "last": {
          "time": 31284.29999999702,
          "textLength": 58,
          "scrollTop": 540,
          "animations": 1
        },
        "minScroll": 0,
        "maxScroll": 1800,
        "animationCounts": [
          1
        ]
      },
      "method": "Native CDP keyboard a down/up and wheel delta +/-180 on #run-list every500ms; text field focused; headless target-Mac Chrome. Event-to-next-frame latency is not physical-input end-to-end latency."
    }
  },
  {
    "capture": "CDH-0001 standalone fixture",
    "timestamp": "2026-10-10T05:43:04.693Z",
    "requestedMs": 30000,
    "elapsedMs": 30002.80000001192,
    "reason": "completed",
    "initial": {
      "actor": "builder",
      "mode": "working",
      "palette": "sticker",
      "calm": true,
      "profile": true,
      "inView": true,
      "hidden": false,
      "reducedMotion": false,
      "animatedRoots": 0,
      "activeAnimations": 0,
      "animationNames": [],
      "matrixCells": 49,
      "staticRunPortraits": 50,
      "activePortraitAnimations": 0,
      "devicePixelRatio": 2,
      "viewport": {
        "width": 1440,
        "height": 1100
      },
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"
    },
    "final": {
      "actor": "builder",
      "mode": "working",
      "palette": "sticker",
      "calm": true,
      "profile": true,
      "inView": true,
      "hidden": false,
      "reducedMotion": false,
      "animatedRoots": 0,
      "activeAnimations": 0,
      "animationNames": [],
      "matrixCells": 49,
      "staticRunPortraits": 50,
      "activePortraitAnimations": 0,
      "devicePixelRatio": 2,
      "viewport": {
        "width": 1440,
        "height": 1100
      },
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36"
    },
    "frameIntervalMs": {
      "count": 899,
      "mean": 33.33203559510567,
      "p50": 33.30000000000018,
      "p95": 33.400000000001455,
      "p99": 33.400000000001455,
      "max": 33.5,
      "over50ms": 0
    },
    "longTasksSupported": true,
    "longTasks": {
      "count": 0,
      "totalMs": 0,
      "maxMs": 0
    },
    "inputEventToNextFrameMs": {
      "count": 56,
      "mean": 27.52142857148179,
      "p50": 27.700000002980232,
      "p95": 29.200000002980232,
      "p99": 29.400000005960464,
      "max": 29.799999997019768,
      "over50ms": 0
    },
    "scrollEventToNextFrameMs": {
      "count": 56,
      "mean": 0.033928572333284786,
      "p50": 0,
      "p95": 0.10000000894069672,
      "p99": 0.20000000298023224,
      "max": 0.20000000298023224,
      "over50ms": 0
    },
    "limits": "Frame intervals are observed RAF cadence, not GPU render time. Input/scroll latency begins at event handling, not hardware input. No interaction samples means unverified. This fixture does not certify future cockpit performance.",
    "browser": {
      "protocolVersion": "1.3",
      "product": "Chrome/155.0.8059.39",
      "revision": "@3ff7ac5a9224be9156d7f8703a06e22890aafd34",
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/155.0.0.0 Safari/537.36",
      "jsVersion": "15.5.35.20"
    },
    "harness": {
      "start": "2026-10-10T05:42:34.627Z",
      "elapsedWallMs": 30936,
      "interactions": {
        "count": 58,
        "first": {
          "time": 893.7999999970198,
          "textLength": 1,
          "scrollTop": 0,
          "animations": 0
        },
        "last": {
          "time": 31291.29999999702,
          "textLength": 58,
          "scrollTop": 540,
          "animations": 0
        },
        "minScroll": 0,
        "maxScroll": 1800,
        "animationCounts": [
          0
        ]
      },
      "method": "Native CDP keyboard a down/up and wheel delta +/-180 on #run-list every500ms; text field focused; headless target-Mac Chrome. Event-to-next-frame latency is not physical-input end-to-end latency."
    }
  }
]
```

</details>

## Cowork import and verification

1. Read `docs/handoff/cockpit-design/README.md`, the completed CDH-0001 and this report, then execute the already adopted CDH-0002 when Michou gives its start signal. Confirm the 13 source hashes below before attributing an observation to this delivery.
2. Open the existing native KGME design interface or a separate private review copy. Record its canvas/copy identity. Import or mount the complete `docs/design/cockpit-v0/` tree using that interface's supported mechanism, preserving the relative structure. The changed import roots are `canvas.json`, `Sprites.dc.html` and the entire 11-file `chibi/` directory. Other boards should remain the current repository versions. Do not replace existing human canvas edits; use the separate review copy if necessary.
3. Retain the editor's existing `./support.js` mechanism. Board 10 uses `chibi/preview.html?embed=1` as its relative iframe entry point, which loads the 7 sibling SVGs and shared CSS/JS. Observe whether the native editor actually resolves and runs it. An unavailable iframe/import capability is a verification gap, not permission to synthesize a renderer.
4. Inspect board 10's 49 static combinations, both palette comparisons and original 24/72 px contexts. Use the clearly labeled fixture actor/mode/detail-palette controls for the 7 × 7 motion checks, then calm and the environment's actual reduced-motion setting. Check all source props for clipping and pivots at actual size. The dashed Phase 2 drawing remains inactive.
5. Compare against the 2 reference PNGs under `memory/attachments/cockpit/chibi-reference/`, whose hashes are below. They are supporting references only; neither is imported as runtime texture or an animation atlas. Keep source, Codex-measured evidence and native observations distinct in the CDH-0002 report.
6. Write only the CDH-0002 report/evidence named in that handoff and return findings to Michou. This delivery does not dispatch Cowork, publish a viewer, approve the design or authorize implementation repairs by the verifier.

For the independent browser fixture, run this from the repository root using the existing uv environment and open the printed loopback address. No package installation is required:

```sh
uv run --no-sync python -m http.server 8765 --bind 127.0.0.1 --directory docs/design/cockpit-v0
# Open http://127.0.0.1:8765/chibi/preview.html
# The 50-run profile scene is http://127.0.0.1:8765/chibi/preview.html?profile=1
```

Opening `preview.html` directly as a file may block its local fetches. The native editor uses its own import/mount mechanism, not this HTTP command. No native API name or undocumented import gesture is assumed here.

## Delivered source identity

The aggregate source-set digest is `5c09201f57e5f5e9e4c6324a53bee85e69e0c8b5d40f07651668bef24013df3e`. It is SHA-256 over the sorted strings `repository-path + NUL + file-sha256 + LF` for the 13 rows below. This report and the handoff status are excluded to avoid self-reference; screenshots identify their rendered source separately.

| Repository path | Bytes | SHA-256 |
| --- | ---: | --- |
| docs/design/cockpit-v0/chibi/README.md | 8459 | `06794bad4b0ef54a3ec73dc437e9471edbae9a6413e1215596b99bd514f7d949` |
| docs/design/cockpit-v0/chibi/arbiter.svg | 8166 | `8d7bb211574d347a5038dfb1b38aa7facc414369f24d7e640102059b16bdcdc1` |
| docs/design/cockpit-v0/chibi/builder.svg | 8775 | `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e` |
| docs/design/cockpit-v0/chibi/characters.css | 5724 | `7fcb692d48d26201744cf6795c899cdbaa9a93750bbb9d952407921bcd19a020` |
| docs/design/cockpit-v0/chibi/characters.js | 15810 | `b6ab15002f5054c2175180dc70f2b515636a8883cc5597630dd549215eea3538` |
| docs/design/cockpit-v0/chibi/guard.svg | 8053 | `da6639d6cabae91e7fa622754a6fc27c9dc7c823e3657d34340a76729f6b31fa` |
| docs/design/cockpit-v0/chibi/michou.svg | 8730 | `46831a1e9d6ebf8991beb59b0281779ee6bc7869798fd2b168822b0f2bdfa9c7` |
| docs/design/cockpit-v0/chibi/preview.html | 12191 | `6efe71c8a4b00e4f60266363afde4263c3a1160ecc96e74c9d7f07753d67ba74` |
| docs/design/cockpit-v0/chibi/reviewer.svg | 7988 | `f444d74e398ab00a5a52e9160c50bf433113ba9115e0fe65efbb51b13e9a062b` |
| docs/design/cockpit-v0/chibi/scribe.svg | 6717 | `cba7d68489569c0dc783086829752807af719b3473dd9d0286a00807d39fc026` |
| docs/design/cockpit-v0/chibi/stranger.svg | 6353 | `7fed1b5845d5934e37580d7070c35adfbabb9e84cc9b87a0e536ef602ab81516` |
| docs/design/cockpit-v0/Sprites.dc.html | 7290 | `14356c6883128b83750ae69443ccebd966d7160149816eb8f4b3ff9af0042273` |
| docs/design/cockpit-v0/canvas.json | 3303 | `e88438d18684f81934d1c383f5ec0f0dd3e603de758409645acb9d2d25260492` |

| Supporting reference | SHA-256 verified in this session |
| --- | --- |
| memory/attachments/cockpit/chibi-reference/approved-cast.png | `a314d8f83653a4cb1354e15a1aa3d443ec3d239135760c9fbf712f34218426a1` |
| memory/attachments/cockpit/chibi-reference/style-reference.png | `519e0449af83b41775192190dec15caf5257e93d762a4c5cd9c3c52ea84598b8` |

## Review screenshot identity

All PNG paths below are relative to `memory/attachments/cockpit/chibi-review/cdh-0001/`. They are browser evidence, not native exports. The full 7-actor source and shared CSS/JS/HTML hashes match the delivered table. The builder checkpoint uses only the builder source and its recorded shared material mapping; the cast overview is a purpose-built read-only arrangement of the same SVG sources, not another canonical fixture. All captures are DPR 2. The sticker matrix is an evidence-only override of the static matrix's palette to inspect all 49 detail specimens; the shipped timeline remains phosphor.

| Evidence file | Actor / mode / palette | Rendered CSS size | Viewport / capture | PNG SHA-256 |
| --- | --- | --- | --- | --- |
| builder-idle-24-72-240x280-sticker-phosphor-checkpoint.png | builder / idle / sticker and phosphor | 24 × 24, 72 × 72, 240 × 280 | 1040 × 610 | `82092f60db22b0dd0039d84ed8206db49e44170a7fe96e524fa821d0ad1d198d` |
| builder-working-24-72-calm-profile.png | builder detail + 50 run portraits / working detail / sticker detail and phosphor portraits / calm hidden | 24 × 24 and 72 × 72 | 1440 × 1100 | `87bdcfb03e7f9bdb60bc8bdaf0e76f9904d57c3148394347cfc588018c1aab3f` |
| builder-working-24-72-phosphor-sticker-profile.png | builder detail + 50 run portraits / working detail / sticker detail and phosphor portraits | 24 × 24 and 72 × 72 | 1440 × 1100 | `bebfa1c70df321dcf2e6330b24fdad0d4ea7d58066eaf34e3b1fdf113b7564b7` |
| builder-working-24-72-reduced-motion-profile.png | builder detail + 50 run portraits / working detail / sticker detail and phosphor portraits / reduced motion | 24 × 24 and 72 × 72 | 1440 × 1100 | `949eb49a5e7e7a4bf6f8b7a1ced8764cdb5e9f63c26e6febd7eb68a8bc0954e9` |
| cast-all-modes-72-phosphor.png | all 7 / all 7 modes / phosphor | 72 × 72 | 1440 × 1100; crop 1346.00 × 768.00 | `329a4567d2689fd544a9e9ab2949f36f196b08368bc15d2ae704392b9a6236eb` |
| cast-all-modes-72-sticker.png | all 7 / all 7 modes / sticker detail specimens | 72 × 72 | 1440 × 1100; crop 1346.00 × 768.00 | `580087199f754e235fc589a22af350a23f976dac7574be35689dad86bbddcd3e` |
| cast-idle-24-72-240x280-sticker-overview.png | all 7 / idle / sticker detail specimens | 24 × 24, 72 × 72, 240 × 280 | 1960 × 620 | `35999e32580292454ab5eb72922536b3a7540af80b71ce39b92c3646e082eb63` |
| cast-idle-72-phosphor-sticker.png | all 7 / idle / phosphor and sticker | 72 × 72 | 1440 × 1100; crop 1346.00 × 156.50 | `6865fc420a2a631ddbd14913da2b2c7fb19b7c35f871f0e3e0452d650c8a07e4` |

The 7 asset hashes used by the overview are identical to the delivered table; the checkpoint builder hash is `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e`. The behavioral screenshots use the 10 source hashes (7 SVGs, CSS, JS and HTML) recorded in the table. A screenshot alone establishes no animation behavior; the instrumented observations above establish the reported browser behavior.

## Proposed reader and reviewer updates, not applied

The 3 following patches reconcile stale sprite constraints and clarify the 2 Codex roles. They preserve the read-only reviewer sandbox, keyboard/approval boundaries and unresolved taste decisions. Their presence in this report is a proposal only; the 3 underlying files were not edited.

<details>
<summary>Exact proposed diffs for the 2 readers and review prompt</summary>

```diff
--- a/docs/readers/cockpit-design.md
+++ b/docs/readers/cockpit-design.md
@@ -14,7 +14,7 @@
 *Written 2026-10-09 by Cowork for Michou, Claude Code, and the Codex reviewer (GPT-6 Astra). This is the context a cold reader needs before touching `docs/design/cockpit-v0/`. The design itself is HANDOFF-0036; the code that will be built from it is HANDOFF-0037.*
 
 ## What is in `docs/design/cockpit-v0/`
-Eleven plain files, all hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and ten `.dc.html` artboards. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.
+The original 11 core files were hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and 10 `.dc.html` artboards. CDH-0001 adds the reusable `chibi/` SVG sources, shared motion layer, standalone fixture and README. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.
 
 | File | Board | What it shows |
 |---|---|---|
@@ -29,6 +29,8 @@
 | `Wall.dc.html` | 9 | the four-column layout for an external monitor, with the raw vendor stream |
 | `Sprites.dc.html` | 10 | the cast: one sprite per `actor`, seven modes, two palettes, the rules |
 
+CDH-0001 is a separately adopted implementation assignment for Codex on GPT-6 Astra; CDH-0002 is Cowork's independent native-canvas verification. The adoption and scoped plan are recorded in `docs/handoff/cockpit-design/README.md`. The independent reviewer role and read-only command below remain unchanged. Neither implementation nor verification grants final design approval.
+
 ## The one rule
 **Signal in the centre, noise at the edges, and noise never carries information.** Everything outside the three columns (frame, tick rails, micro-labels, scanlines, vignette, sweep) and every sprite is decoration that mirrors a fact already shown in text. Therefore the `c` key and `prefers-reduced-motion` can remove or freeze all of it without loss. A finding that a decorative element carries a fact nowhere else on screen is `blocking`; a finding that a fact is shown only by colour is `blocking` (ADR-016 vocabulary, see below).
 
@@ -38,7 +40,9 @@
 - The frame carries system state: cyan live, magenta flood on blocking or halt, amber strip while an intent awaits its outcome, grey static when disconnected.
 - Keys: `j`/`k` move, `g`/`G` ends, `Enter` detail, `Esc` back, `u` parent, `Tab` pane, `f` follow, `/` filter line with `run:` `kind:` `job:`, `1`–`4` class toggles, `0` all, `r` run filter, `t` trace, `o` open intents, `x` clear, `c` calm, `p` payload, `w` wall, `?` keys. Reserved for Phase 2, dashed and unbound: `b` `/btw`, `m` model, `y`/`n` approve, `;` command, `Space` queue.
 - ADR-016 strikes as three boxes filling per cycle, magenta on halt.
-- Sprites: one per `actor` (not per model), 24 × 24, original line work, two frames per mode at most, the accent colour is the row's class colour, phosphor in the timeline, sticker palette only in the detail pane header and the Phase 2 model selector. Mapping in `kgme.toml [sprites]`, first rule wins, `default = "stranger"`. "Outrageous, but it retains all the darkness" is the brief for them.
+- Sprites under adopted CDH-0001: 1 original smooth, layered SVG per `actor` (not per model), with 6 semantic material roles and restrained cel shading. Use deliberate 24 px portraits in run headers and full 72 px characters in detail headers; the event rows remain 22 px. Each of the 7 modes uses at most 2 authored key poses with interpolated transforms and discrete expression swaps. Accent follows a class or state already written in adjacent text. Phosphor stays in the timeline; sticker stays in the detail header and illustrated Phase 2 model selector. Mapping in `kgme.toml [sprites]`, first rule wins, `default = "stranger"`. "Outrageous, but it retains all the darkness" remains the brief.
+- Sprite motion: all dense run portraits and the 49-cell matrix stay static; only 1 selected visible detail may animate. Hidden, offscreen, calm and actual reduced-motion states remove animation work. Calm removes decoration without losing actor, lifecycle, class or event facts or changing row geometry. Modes are not failure classes; fixture controls cannot override reduced motion or bind application keys.
+- Sprite evidence: the 24 × 24 source grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap are retired for CDH-0001. The provisional target is 512 KiB raw for all 7 SVG assets plus shared animation code. Report bytes per actor and total, SVG element counts, simultaneous active animations, and 30-second target-Mac captures with 50 static portraits and 1 selected detail, with motion and calm baselines. Record environment, frame intervals, long tasks and interaction observations; label missing measurements unverified. A small file is not proof of runtime performance.
 - Wishlist's empty sections stay empty for v0.
 
 ## Open (Michou has not ruled)
@@ -49,7 +53,7 @@
 - Every value in the top bar is a sample; the real cockpit reads them. The versions shown are placeholders.
 
 ## How to review it (Codex, GPT-6 Astra)
-The `.dc.html` format renders only inside the canvas editor; nobody outside it sees pixels. Review the **source**. If PNG exports exist under `memory/attachments/cockpit/` (Michou exports them from the canvas page), take them as image input alongside the source; they are the only way to see the result.
+The `.dc.html` format requires the native canvas editor; preserve its support mechanism and templating. The standalone `chibi/preview.html` fixture and SVG assets can be rendered in a browser when tool access permits. Review the **source** and distinguish supplied PNG evidence, independently observed browser behavior, measured target-Mac performance and native observations. A fixture screenshot does not establish native canvas behavior. Cowork must import and observe the delivered native board under CDH-0002; any unavailable native capability remains explicitly unverified.
 
 What a design review is for, and the class each finding carries:
 - a fact shown only by colour, or a decorative element that carries a fact shown nowhere else → `blocking`
@@ -58,7 +62,7 @@
 - a `<div>` doing a button's job, an icon-only control without a label, focus shown by colour alone → `blocking`
 - a label or chip outside ADR-016's vocabulary (`ok`, `blocking`, `transient`, `advisory`, plus status `refused`, `pending`) → `advisory`
 - inconsistency between boards (a token, a key hint, a row layout that differs without reason) → `advisory`
-- anything in the sprite generator that would not survive as a standalone SVG under 3 KB → `advisory`
+- an unexplained exceedance of the provisional 512 KiB total sprite-source target, or omitted source-size, SVG-complexity or runtime evidence → `advisory`; never enforce the retired 3 KB cap or treat a byte count as a performance result
 - taste → `advisory`, stated as such; Michou's taste is the spec, the reviewer's is a suggestion
 - whitespace, typos → `cosmetic`
 
@@ -79,4 +83,4 @@
 4. Acceptance closes the handoff: Michou records an `approval` event naming the committed tree (`kgme ledger note --kind approval …`, flags per `kgme ledger note --help`, summary `design: cockpit v0 approved at <short sha>`), and 0036 goes to `done`. 0037 builds from that sha and nothing else.
 
 ## For Michou's further requests to Astra
-Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules." Bad questions: "make it look better" (taste is Michou's), "render it" (it cannot), "approve it" (only Michou does).
+Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules," "inspect the standalone chibi fixture at 24/72 px." Bad questions: "make it look better" (taste is Michou's), "certify the native canvas without observing it," "approve it" (only Michou does).
--- a/docs/readers/cockpit-design-chatgpt.md
+++ b/docs/readers/cockpit-design-chatgpt.md
@@ -20,15 +20,15 @@
 
 ## The design track, who does what
 - **Michou** owns taste and decisions. He wrote the brief, chose the palette and the type, asked for the HUD to be "almost too much" and the sprites to be "outrageous but retaining all the darkness." He rules on every finding and gives the final approval, recorded as a ledger event.
-- **Cowork** (Claude, in the Claude desktop app) is the designer. It drew the canvas: ten artboards as plain HTML/CSS/JS files, committed in the repository under `docs/design/cockpit-v0/`, mirrored to a canvas page where Michou can edit elements by hand. It applies Michou's rulings to the files, commits, and republishes the page.
-- **Codex** (GPT-6 Astra, via `codex exec` in a read-only sandbox) is the independent reviewer. It reads the source files and any PNG exports, and returns findings in a fixed format: a table with id, class, file:line, finding, fix; a verdict; notes. Its prompt is `tools/review/design-prompt.md`. It cannot render the boards, write files, or approve anything.
+- **Cowork** (Claude, in the Claude desktop app) is the designer. It drew the canvas: ten artboards as plain HTML/CSS/JS files, committed in the repository under `docs/design/cockpit-v0/`, mirrored to a canvas page where Michou can edit elements by hand. It applies Michou's rulings to the files, commits, and republishes the page. Under the separately adopted CDH-0002, it independently verifies the delivered cast in its native canvas and reports findings; that local review authorizes no source repair, publication or final approval.
+- **Codex** has 2 distinct roles. The independent reviewer runs GPT-6 Astra via `codex exec` in a read-only sandbox, reads source and visual evidence, and returns the fixed Findings table, Verdict and Notes under `tools/review/design-prompt.md`; that prompt grants no edits. Separately, Michou adopted CDH-0001 for Codex/Astra to implement the approved illustrated cast within named local files. Codex can observe the standalone SVG/browser fixture; Cowork independently observes the native canvas under CDH-0002. Neither role can grant final approval.
 - **You (ChatGPT)** are Michou's design sparring partner and his liaison to the Codex side. Details below.
 
 ## The one rule the whole design obeys
 Signal in the centre, noise at the edges, and noise never carries information. The timeline, the detail pane and the run grid carry facts. The frame, tick rails, micro-labels, scanlines, vignette and every sprite are decoration that only repeats a fact already shown in text, so a single key (`c`) and the reduced-motion setting can remove all of it without loss. Anything you propose must pass this test: if a decorative element would be the only place a fact is shown, it is wrong.
 
 ## What is decided (do not reopen)
-Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` for focus and live and the frame, magenta `#ff3d7f` for blocking only, amber `#ffb02e` for pending/transient/advisory, green `#4de38a` for ok. JetBrains Mono everywhere, dense, 22 px rows. The frame's colour carries system state (cyan live, magenta flood on blocking, amber strip while an intent awaits its outcome, grey static when disconnected). The keyboard map (j/k, g/G, Enter, Esc, u, Tab, f, /, 1–4, 0, r, t, o, x, c, p, w, ?; b, m, y/n, ;, Space reserved for Phase 2, dashed). Three strike boxes for the review loop's bound. Sprites: one per actor, not per model (builder, reviewer, arbiter, guard, scribe, Michou, stranger), 24 × 24 pixels, original line work, no stock or game assets, two frames per mode, seven modes (idle, working, waiting, transient/melting, blocked/on fire, done/halo, asleep/chalk outline), the accent colour is the row's class colour, phosphor in the timeline, a sticker palette only in the detail-pane header and the Phase 2 model selector.
+Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` for focus and live and the frame, magenta `#ff3d7f` for blocking only, amber `#ffb02e` for pending/transient/advisory, green `#4de38a` for ok. JetBrains Mono everywhere, dense, 22 px rows. The frame's colour carries system state (cyan live, magenta flood on blocking, amber strip while an intent awaits its outcome, grey static when disconnected). The keyboard map (j/k, g/G, Enter, Esc, u, Tab, f, /, 1–4, 0, r, t, o, x, c, p, w, ?; b, m, y/n, ;, Space reserved for Phase 2, dashed). Three strike boxes for the review loop's bound. Sprites under adopted CDH-0001: 1 per actor, not per model (builder, reviewer, arbiter, guard, scribe, Michou, stranger), original smooth SVG geometry, 6 semantic material roles with restrained cel shading, deliberate 24 px run portraits and full 72 px detail characters. Up to 2 authored key poses per mode interpolate reusable parts across 7 modes (idle, working, waiting, transient/melting, blocked/on fire, done/halo, asleep/chalk outline). Modes are not failure classes. Accent repeats an adjacent written class or state; phosphor stays in the timeline and sticker only in the detail header and illustrated Phase 2 model selector. All run portraits stay static; only 1 selected visible detail animates, with animation work removed when hidden, offscreen, calm or reduced motion is requested. Every actor, lifecycle, class and event fact remains in text. The retired 24 × 24 grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap no longer apply. A provisional 512 KiB raw target covers all 7 SVGs plus shared animation code; report source bytes, SVG element counts, active animations and 30-second target-Mac motion/calm captures with 50 static portraits and 1 selected detail. Missing measurements stay unverified.
 
 ## What is open (where you can help)
 Whether the canvas passes the acceptance test; sticker placement (two spots, or a `sticker` tweak that allows it anywhere); whether the "you" sprite should resemble Michou; the "mood" copy for the corner micro-labels (a set of gallows one-liners exists on board 10, "the ledger remembers · you may not", "server unreachable · as are we all"); and, after Codex's first pass, which of its findings to take.
@@ -36,12 +36,12 @@
 ## Your job, concretely
 1. **Read Codex's findings with Michou.** He will paste the review. For each finding, say in one line whether it holds against the rules above, and draft his ruling: take, reject with reason, or defer. The output he needs is a numbered list he can send to Cowork as-is.
 2. **Write the next Codex prompt** when a pass should be narrower ("only the keyboard map and board 7", "only the sprite generator"). Keep Codex's fixed output format (Findings table, Verdict, Notes) and the class vocabulary.
-3. **Look at PNG exports** when Michou gives them to you; Codex cannot see pixels well, you can. Report what you see in the same finding format, marked as yours.
-4. **Ideate inside the rules**: sprite ideas as 24 × 24 pixel grids using the six fills (`b` garment, `s` face, `h` hat and tool, `p` print, `d` dark, `a` accent); micro-label copy in the stated register; mode animations with at most two frames. Darkness kept, originality required: no named characters, no game or stock imagery.
+3. **Look at visual evidence** when available, including the approved reference sheet, source-identified PNG exports and the standalone browser fixture. Report what you observe in the same finding format, marked as yours. Keep native canvas observations separate; Cowork performs those under CDH-0002.
+4. **Ideate inside the rules**: original smooth sprite geometry using 6 material roles (garment, face, hat/tool, print, dark and accent) with restrained cel shading, readable at 24/72 px; micro-label copy in the stated register; motion using at most 2 authored key poses per mode. Use the approved cast as the visual target and the supplied style image as rendering guidance only. Darkness and originality remain required; do not copy the reference character, game or stock imagery.
 5. **Flag collisions**: a proposal that would make noise carry information, a colour used for a second meaning, a key already bound, a Phase 2 control drawn solid.
 
 ## Output format that slots into the loop
-Rulings: `F3 — take. F5 — reject: taste, Michou keeps the cheetah print. F7 — defer to 0037.` Design proposals: a short title, the board it changes, the exact change, why it passes the rule. Sprite proposals: the grid, the fills, the modes affected. Nothing longer than it needs to be; Cowork edits files, it does not need prose.
+Rulings: `F3 — take. F5 — reject: taste, Michou keeps the cheetah print. F7 — defer to 0037.` Design proposals: a short title, the board it changes, the exact change, why it passes the rule. Sprite proposals: the geometry, material roles, poses, modes affected and actual 24/72 px treatment. Nothing longer than it needs to be; Cowork edits files, it does not need prose.
 
 ## What you do not do
-You do not have the files unless Michou uploads them; ask for the specific board rather than guessing. You do not approve; only Michou does. You do not rewrite the decided list. You do not produce images for use in the cockpit; sprites are drawn as pixel grids in the source. You never suggest another company's UI or a game's assets as a shortcut; the grammar is borrowed, the assets are not.
+If the files are unavailable, ask for the specific board rather than guessing. You do not approve; only Michou does. You do not rewrite the decided list. Visual studies and the approved concept sheet are design references; the delivered runtime artwork remains original editable SVG, not a raster sheet used as an animation atlas. You never suggest another company's UI or a game's assets as a shortcut; the grammar is borrowed, the assets are not.
--- a/tools/review/design-prompt.md
+++ b/tools/review/design-prompt.md
@@ -1,10 +1,10 @@
-You are GPT-6 Astra, the independent reviewer in KGME (docs/readers/review-loop.md), reviewing a DESIGN, not code: the cockpit v0 canvas under docs/design/cockpit-v0/ (HANDOFF-0036).
+You are GPT-6 Astra, the independent reviewer in KGME (docs/readers/review-loop.md), reviewing a DESIGN, not code: the cockpit v0 canvas under docs/design/cockpit-v0/ (HANDOFF-0036). This prompt remains read-only and grants no source edits. The separately adopted CDH-0001 implementation role is governed by its own handoff; do not execute it under this review prompt or weaken the reviewer sandbox.
 
-Read, in order: docs/readers/cockpit-design.md (the context, the one rule, what is decided, what is open, and the finding classes for a design review), docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md, docs/adr/ADR-016-failure-classes-and-escalation.md, docs/adr/ADR-017-cockpit.md, memory/notes/cockpit-wishlist.md, then every file under docs/design/cockpit-v0/ (canvas.json first, then Main.dc.html, then the rest in the index's order). If PNG files exist under memory/attachments/cockpit/, look at them too; they are exports of the rendered boards.
+Read, in order: docs/readers/cockpit-design.md (the context, the one rule, what is decided, what is open, and the finding classes for a design review), docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md, docs/adr/ADR-016-failure-classes-and-escalation.md, docs/adr/ADR-017-cockpit.md, memory/notes/cockpit-wishlist.md, then every file under docs/design/cockpit-v0/ (canvas.json first, then Main.dc.html, then the rest in the index's order). Also read docs/handoff/cockpit-design/README.md and the adopted CDH-0001 sprite constraints as review context, plus docs/audit/cockpit-design/cdh-0001-implementation.md if delivered. Do not execute those documents as this reviewer. If PNG files exist under memory/attachments/cockpit/, inspect their recorded provenance: distinguish approved references, standalone fixture captures and native canvas exports.
 
-The .dc.html files render only inside the canvas editor. You review the source. The syntax (<x-dc>, <helmet>, <sc-for>, <sc-if>, {{holes}}, a DCLogic class whose renderVals() feeds the template) is the editor's; it is not a finding. The boards are drawings and are exempt from ADR-015's line-count guide. Sample values in the top bar are samples.
+The .dc.html files require the native canvas editor. Review the source and available evidence; the standalone chibi/preview.html fixture and SVGs can be observed in a browser when tools permit, without changing source. Browser rendering does not certify native canvas behavior. Cowork independently imports and observes that behavior under CDH-0002; missing native capabilities remain unverified. Preserve the native support mechanism. The syntax (<x-dc>, <helmet>, <sc-for>, <sc-if>, {{holes}}, a DCLogic class whose renderVals() feeds the template) is the editor's; it is not a finding. The boards are drawings and are exempt from ADR-015's line-count guide. Sample values in the top bar are samples.
 
-Judge against the one rule (signal in the centre, noise at the edges, noise never carries information), the decided list, ADR-016's vocabulary, contrast (4.5:1 for text, 3:1 at 24 px and over), keyboard integrity (no key bound twice, every bound key on the map, every Phase 2 control dashed and labelled), accessibility as drawn (real buttons and links, labels on icon-only controls, focus not by colour alone), consistency across boards, and whether each sprite in Sprites.dc.html could stand alone as an SVG under 3 KB with the same six fills and seven modes. Taste is Michou's; a taste remark is advisory and says so.
+Judge against the one rule (signal in the centre, noise at the edges, noise never carries information), the decided list, ADR-016's vocabulary, contrast (4.5:1 for text, 3:1 at 24 px and over), keyboard integrity (no key bound twice, every bound key on the map, every Phase 2 control dashed and labelled), accessibility as drawn (real buttons and links, labels on icon-only controls, focus not by colour alone), consistency across boards, and the adopted CDH-0001 sprite requirements: original reusable SVG geometry; 6 semantic material roles with restrained cel shading; deliberate 24 px portraits and 72 px detail figures; 7 actors across 7 modes and both palettes; no more than 2 authored key poses per mode with interpolation; explicit adjacent actor, lifecycle, class and event text; static run portraits and at most 1 selected visible animated detail; no animation work when hidden, offscreen, calm or reduced motion is requested. Modes must not become new failure classes. The retired 24 × 24 source grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap are not criteria. Treat 512 KiB raw for all 7 assets plus shared animation code as a provisional engineering target. Check per-actor/total bytes, SVG element counts, active animations, and 30-second target-Mac motion/calm measurements with 50 static run portraits and 1 selected detail, including environment, frame intervals, long tasks and interaction observations. Missing evidence stays unverified; small source size proves no runtime-performance result. Taste is Michou's; a taste remark is advisory and says so.
 
 Your final message is markdown with exactly three sections:
 ## Findings
@@ -12,4 +12,4 @@
 ## Verdict
 One line: PASS if no blocking finding stands open, else BLOCK with the count.
 ## Notes
-Anything a cold reader would want, including the three things you would change first if taste were yours, marked as taste. State which files you read and whether you saw PNG exports.
+Anything a cold reader would want, including the three things you would change first if taste were yours, marked as taste. State which files and source hashes you reviewed, which PNGs or browser interactions you observed, which measurements were supplied by Codex, and which native checks remain unverified.
```

</details>

## Applied scoped diff for existing design files

The 11 added source files are listed and hashed above. The complete patch below shows the 2 existing design-file edits against their pre-session content, including removal of the old pixel generator. No other board or note placement changed.

<details>
<summary>Exact board 10 and canvas-note diff</summary>

```diff
--- a/docs/design/cockpit-v0/Sprites.dc.html
+++ b/docs/design/cockpit-v0/Sprites.dc.html
@@ -25,106 +25,26 @@
 .kbd{display:inline-block;min-width:16px;padding:0 5px;border:1px solid #39d0ff;color:#39d0ff;font-size:10px;line-height:16px;text-align:center;border-radius:2px}
 .grp{display:flex;gap:10px;align-items:center;padding:4px 10px;border-bottom:1px solid #1e2a33;color:#39d0ff;font-size:11px}
 .row{display:grid;grid-template-columns:70px 16px 112px minmax(0,1fr) 92px 56px;gap:10px;align-items:center;padding:3px 10px;border-bottom:1px solid #141b22;min-height:22px}
-svg{display:block}
-.fb{opacity:0}
-.m-idle .fb{animation:blink 4s steps(1,end) infinite}.m-idle .fa{animation:blinka 4s steps(1,end) infinite}
-@keyframes blink{0%,90%{opacity:0}91%,99%{opacity:1}100%{opacity:0}}
-@keyframes blinka{0%,90%{opacity:1}91%,99%{opacity:0}100%{opacity:1}}
-.m-working .fb{animation:tick .5s steps(1,end) infinite}.m-working .fa{animation:ticka .5s steps(1,end) infinite}
-@keyframes tick{0%,49%{opacity:0}50%,100%{opacity:1}}
-@keyframes ticka{0%,49%{opacity:1}50%,100%{opacity:0}}
-.m-waiting .fb{animation:tick 1.4s steps(1,end) infinite}.m-waiting .fa{animation:ticka 1.4s steps(1,end) infinite}
-.m-transient .fb{animation:tick 1s steps(1,end) infinite}.m-transient .fa{animation:ticka 1s steps(1,end) infinite}
-.m-blocked .fb{animation:tick .35s steps(1,end) infinite}.m-blocked .fa{animation:ticka .35s steps(1,end) infinite}
-.m-done .fb{animation:tick 1.2s steps(1,end) infinite}.m-done .fa{animation:ticka 1.2s steps(1,end) infinite}
-.m-asleep .fb{animation:tick 2.4s steps(1,end) infinite}.m-asleep .fa{animation:ticka 2.4s steps(1,end) infinite}
-@media (prefers-reduced-motion:reduce){.fa,.fb{animation:none}.fb{opacity:0}.fa{opacity:1}}
-.tile{display:flex;flex-direction:column;align-items:center;gap:6px}
-.stk{background:#efe7ff;border-radius:10px;padding:6px}
-.voice{display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:6px 18px;font-size:11px}
+.voice{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 18px;font-size:11px}
 .voice span{color:#6f8290;letter-spacing:.08em;text-transform:uppercase;font-size:10px}
+.fixture-frame{box-sizing:border-box;display:block;width:100%;height:780px;border:1px solid #1e2a33;background:#0a0c10}
 </style>
 </helmet>
-<div style="min-height:100vh;padding:36px;display:flex;flex-direction:column;gap:22px;background:#0a0c10">
+<div style="min-height:100vh;box-sizing:border-box;padding:36px;display:flex;flex-direction:column;gap:22px;background:#0a0c10">
   <div style="display:flex;flex-wrap:wrap;gap:18px;align-items:baseline;justify-content:space-between">
     <div>
       <div class="lbl">KGME cockpit · whimsy that obeys the rule · v2, louder</div>
       <h1 style="margin:2px 0 0;font-size:22px;font-weight:700;letter-spacing:.04em">Sprites — the cast and its modes</h1>
     </div>
-    <div style="max-width:760px;font-size:11px;color:#6f8290">One sprite per <code style="color:#cfe6ef">actor</code>, 24 × 24 pixels, original line work, two palettes from one drawing. A sprite's mode repeats the class chip on its row and nothing else, so it is noise by the rule: <span class="kbd">c</span> hides the whole cast, reduced motion freezes it to one pose. Each is one SVG under <code style="color:#cfe6ef">cockpit/sprites/</code>; a new harness is a file and a line in <code style="color:#cfe6ef">kgme.toml [sprites]</code>, and until then it is the stranger.</div>
+    <div style="max-width:760px;font-size:11px;color:#6f8290">One original illustrated character per <code style="color:#cfe6ef">actor</code>, 7 modes, 2 material palettes from the same drawing. A 24 px cropped portrait belongs in run headers; a 72 px full character belongs in detail headers. Modes repeat lifecycle facts in adjacent text; they are not failure classes. Calm removes decoration; reduced motion freezes it. The stranger remains the fallback.</div>
   </div>
-
-  <section class="pnl brk" style="padding:16px">
-    <h2 class="h">The cast × the modes · phosphor palette</h2>
-    <div style="display:grid;grid-template-columns:170px repeat(7, minmax(0, 1fr));gap:12px 8px;align-items:center">
-      <span class="lbl">actor → sprite</span>
-      <span class="lbl" style="text-align:center">idle</span>
-      <span class="lbl" style="text-align:center">working</span>
-      <span class="lbl" style="text-align:center;color:#ffb02e">waiting on you</span>
-      <span class="lbl" style="text-align:center;color:#ffb02e">transient · melting</span>
-      <span class="lbl" style="text-align:center;color:#ff3d7f">blocked · on fire</span>
-      <span class="lbl" style="text-align:center;color:#4de38a">done · halo</span>
-      <span class="lbl" style="text-align:center">asleep · chalk</span>
-      <sc-for list="{{cast}}" as="c" hint-placeholder-count="7">
-        <div style="display:flex;flex-direction:column;gap:2px"><span style="font-size:12px">{{c.name}}</span><span class="lbl">{{c.actor}}</span><span style="font-size:10px;color:#6f8290">{{c.bio}}</span></div>
-        <sc-for list="{{c.modes}}" as="sp" hint-placeholder-count="7">
-          <div class="tile">
-            <svg class="{{sp.cls}}" viewBox="0 0 24 24" width="72" height="72" shape-rendering="crispEdges" aria-label="{{sp.label}}">
-              <g class="fa"><path fill="{{sp.cb}}" d="{{sp.a_b}}"></path><path fill="{{sp.cs}}" d="{{sp.a_s}}"></path><path fill="{{sp.ch}}" d="{{sp.a_h}}"></path><path fill="{{sp.cp}}" d="{{sp.a_p}}"></path><path fill="{{sp.cd}}" d="{{sp.a_d}}"></path><path fill="{{sp.ca}}" d="{{sp.a_a}}"></path></g>
-              <g class="fb"><path fill="{{sp.cb}}" d="{{sp.b_b}}"></path><path fill="{{sp.cs}}" d="{{sp.b_s}}"></path><path fill="{{sp.ch}}" d="{{sp.b_h}}"></path><path fill="{{sp.cp}}" d="{{sp.b_p}}"></path><path fill="{{sp.cd}}" d="{{sp.b_d}}"></path><path fill="{{sp.ca}}" d="{{sp.b_a}}"></path></g>
-            </svg>
-          </div>
-        </sc-for>
-      </sc-for>
-    </div>
-    <div class="lbl" style="margin-top:12px">Two frames per mode. Working shakes at 0.5 s (the jackhammer, the quill, the beam). Blocked flickers at 0.35 s because fire does. Asleep is the chalk outline of the same drawing, rotated, breathing a z every 2.4 s. The accent colour is the row's class colour; it is also the colour of the fire.</div>
+  <section class="pnl brk" style="padding:14px">
+    <h2 class="h">Reusable cast · 49 static specimens · one selected preview</h2>
+    <div style="font-size:11px;color:#6f8290;margin-bottom:10px">The scrollable design fixture below uses the 7 sibling SVG sources and shared animation layer. It includes both palettes, original context examples, and actual 24/72 px sizes. Its controls are fixture controls only. <a href="./chibi/preview.html" target="_blank" rel="noopener">Open the standalone fixture</a>. Native import, iframe support and playback await CDH-0002 observation.</div>
+    <iframe class="fixture-frame" src="{{fixtureSource}}" title="CDH-0001 chibi cast design fixture: all 49 combinations, palettes and context" loading="eager"></iframe>
   </section>
-
-  <div style="display:grid;grid-template-columns:minmax(0, 1.2fr) minmax(0, 1fr);gap:18px">
+  <div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px">
     <section class="pnl brk" style="padding:16px">
-      <h2 class="h">Same drawings · sticker palette · cheetah print is a colour, not a pattern file</h2>
-      <div style="display:grid;grid-template-columns:repeat(7, minmax(0, 1fr));gap:10px">
-        <sc-for list="{{stickers}}" as="sp" hint-placeholder-count="7">
-          <div class="tile">
-            <div class="stk">
-              <svg class="{{sp.cls}}" viewBox="0 0 24 24" width="64" height="64" shape-rendering="crispEdges" aria-label="{{sp.label}}">
-                <g class="fa"><path fill="{{sp.cb}}" d="{{sp.a_b}}"></path><path fill="{{sp.cs}}" d="{{sp.a_s}}"></path><path fill="{{sp.ch}}" d="{{sp.a_h}}"></path><path fill="{{sp.cp}}" d="{{sp.a_p}}"></path><path fill="{{sp.cd}}" d="{{sp.a_d}}"></path><path fill="{{sp.ca}}" d="{{sp.a_a}}"></path></g>
-                <g class="fb"><path fill="{{sp.cb}}" d="{{sp.b_b}}"></path><path fill="{{sp.cs}}" d="{{sp.b_s}}"></path><path fill="{{sp.ch}}" d="{{sp.b_h}}"></path><path fill="{{sp.cp}}" d="{{sp.b_p}}"></path><path fill="{{sp.cd}}" d="{{sp.b_d}}"></path><path fill="{{sp.ca}}" d="{{sp.b_a}}"></path></g>
-              </svg>
-            </div>
-            <span class="lbl">{{sp.label}}</span>
-          </div>
-        </sc-for>
-      </div>
-      <div style="font-size:11px;color:#6f8290;margin-top:12px">Stickers are allowed in two places: the detail pane header (one sprite, 72 px) and the Phase 2 model selector. In the timeline, phosphor. A <code style="color:#cfe6ef">sticker</code> tweak flips that for an evening when the situation calls for cheetah print.</div>
-    </section>
-
-    <section class="pnl brk" style="padding:16px;display:flex;flex-direction:column;gap:12px">
-      <h2 class="h">Where they stand</h2>
-      <div style="border:1px solid #1e2a33">
-        <div class="grp"><svg class="m-working" viewBox="0 0 24 24" width="24" height="24" shape-rendering="crispEdges" aria-label="builder, working"><g class="fa"><path fill="#cfe6ef" d="{{ctx.builder.a_b}}"></path><path fill="#6f8290" d="{{ctx.builder.a_s}}"></path><path fill="#8fb4c4" d="{{ctx.builder.a_h}}"></path><path fill="#0a0c10" d="{{ctx.builder.a_p}}"></path><path fill="#0a0c10" d="{{ctx.builder.a_d}}"></path><path fill="#39d0ff" d="{{ctx.builder.a_a}}"></path></g><g class="fb"><path fill="#cfe6ef" d="{{ctx.builder.b_b}}"></path><path fill="#6f8290" d="{{ctx.builder.b_s}}"></path><path fill="#8fb4c4" d="{{ctx.builder.b_h}}"></path><path fill="#0a0c10" d="{{ctx.builder.b_p}}"></path><path fill="#0a0c10" d="{{ctx.builder.b_d}}"></path><path fill="#39d0ff" d="{{ctx.builder.b_a}}"></path></g></svg><span>▣ run c70d687b…8447</span><span style="color:#6f8290">claude-code · HANDOFF-0040 · 212 events</span></div>
-        <div class="row"><span style="color:#6f8290">19:41:48</span><span>◀</span><span style="color:#6f8290">tool:Bash</span><span>Bash ok · 9 passed</span><span><span class="chip c-ok">ok</span></span><span style="text-align:right;color:#6f8290">15 s</span></div>
-        <div class="grp"><svg class="m-transient" viewBox="0 0 24 24" width="24" height="24" shape-rendering="crispEdges" aria-label="reviewer, transient"><g class="fa"><path fill="#cfe6ef" d="{{ctx.reviewer.a_b}}"></path><path fill="#6f8290" d="{{ctx.reviewer.a_s}}"></path><path fill="#8fb4c4" d="{{ctx.reviewer.a_h}}"></path><path fill="#0a0c10" d="{{ctx.reviewer.a_p}}"></path><path fill="#0a0c10" d="{{ctx.reviewer.a_d}}"></path><path fill="#ffb02e" d="{{ctx.reviewer.a_a}}"></path></g><g class="fb"><path fill="#cfe6ef" d="{{ctx.reviewer.b_b}}"></path><path fill="#6f8290" d="{{ctx.reviewer.b_s}}"></path><path fill="#8fb4c4" d="{{ctx.reviewer.b_h}}"></path><path fill="#0a0c10" d="{{ctx.reviewer.b_p}}"></path><path fill="#0a0c10" d="{{ctx.reviewer.b_d}}"></path><path fill="#ffb02e" d="{{ctx.reviewer.b_a}}"></path></g></svg><span>▣ run 01M4F8NR…04F</span><span style="color:#6f8290">kgme.review · cycle 1 · usage limit · melting</span></div>
-        <div class="row" style="border-bottom:0"><span style="color:#6f8290">19:43:03</span><span>◀</span><span style="color:#6f8290">review:0040</span><span>cycle 1 attempt 1: reviewer exited 1 with no text</span><span><span class="chip c-trans">transient</span></span><span style="text-align:right;color:#6f8290">3 s</span></div>
-      </div>
-      <div class="lbl">run header · 24 px · mode = the run's latest class</div>
-
-      <div style="display:flex;gap:12px;align-items:center;border:1px solid #1e2a33;padding:10px">
-        <div class="stk"><svg class="m-blocked" viewBox="0 0 24 24" width="72" height="72" shape-rendering="crispEdges" aria-label="arbiter, blocked"><g class="fa"><path fill="#5b5bd6" d="{{ctx.arbiter.a_b}}"></path><path fill="#f2f2f2" d="{{ctx.arbiter.a_s}}"></path><path fill="#2b2d6b" d="{{ctx.arbiter.a_h}}"></path><path fill="#2a2340" d="{{ctx.arbiter.a_p}}"></path><path fill="#2a2340" d="{{ctx.arbiter.a_d}}"></path><path fill="#ff3d7f" d="{{ctx.arbiter.a_a}}"></path></g><g class="fb"><path fill="#5b5bd6" d="{{ctx.arbiter.b_b}}"></path><path fill="#f2f2f2" d="{{ctx.arbiter.b_s}}"></path><path fill="#2b2d6b" d="{{ctx.arbiter.b_h}}"></path><path fill="#2a2340" d="{{ctx.arbiter.b_p}}"></path><path fill="#2a2340" d="{{ctx.arbiter.b_d}}"></path><path fill="#ff3d7f" d="{{ctx.arbiter.b_a}}"></path></g></svg></div>
-        <div style="display:flex;flex-direction:column;gap:2px"><span class="lbl" style="color:#ff3d7f">detail · note · halt</span><span style="font-size:12px">review:HANDOFF-0032 HALT after cycle 3</span><span style="font-size:11px;color:#6f8290">arbiter claude-opus-5-5 · the skull sits down and burns until the override lands</span></div>
-      </div>
-      <div class="lbl">detail pane header · 72 px · sticker palette allowed here</div>
-
-      <div style="display:flex;gap:12px;align-items:center;border:1px dashed #3a4650;padding:10px;color:#6f8290">
-        <svg class="m-waiting" viewBox="0 0 24 24" width="48" height="48" shape-rendering="crispEdges" aria-label="guard, waiting"><g class="fa"><path fill="#cfe6ef" d="{{ctx.guard.a_b}}"></path><path fill="#6f8290" d="{{ctx.guard.a_s}}"></path><path fill="#8fb4c4" d="{{ctx.guard.a_h}}"></path><path fill="#0a0c10" d="{{ctx.guard.a_p}}"></path><path fill="#0a0c10" d="{{ctx.guard.a_d}}"></path><path fill="#ffb02e" d="{{ctx.guard.a_a}}"></path></g><g class="fb"><path fill="#cfe6ef" d="{{ctx.guard.b_b}}"></path><path fill="#6f8290" d="{{ctx.guard.b_s}}"></path><path fill="#8fb4c4" d="{{ctx.guard.b_h}}"></path><path fill="#0a0c10" d="{{ctx.guard.b_p}}"></path><path fill="#0a0c10" d="{{ctx.guard.b_d}}"></path><path fill="#ffb02e" d="{{ctx.guard.b_a}}"></path></g></svg>
-        <div style="display:flex;flex-direction:column;gap:2px"><span class="lbl">phase 2 · approval pending</span><span style="font-size:12px;color:#cfe6ef">Bash git push origin main</span><span style="font-size:11px">the cherub with the riot shield holds the door until <span class="kbd">y</span> or <span class="kbd">n</span></span></div>
-      </div>
-      <div class="lbl">approval card · 48 px · the guard is the hook pair, not a model</div>
-    </section>
-  </div>
-
-  <div style="display:grid;grid-template-columns:minmax(0, 1fr) minmax(0, 1fr);gap:18px">
-    <section class="pnl brk" style="padding:16px">
       <h2 class="h">Voice · the micro-labels, mood: based</h2>
       <div style="font-size:11px;color:#6f8290;margin-bottom:10px">The corner labels carry no information, so they can say anything. A <code style="color:#cfe6ef">mood</code> tweak swaps the cold set for this one. Same facts, worse attitude.</div>
       <div class="voice">
@@ -153,8 +73,8 @@
 "kgme.*"        = "scribe"
 "michou"        = "michou"
 default         = "stranger"</pre><span style="color:#6f8290">Matched on <code>actor</code>, first rule wins. A Kimi harness is the stranger until you give it a face.</span></div>
-        <div><span class="lbl">what a sprite may do</span><p style="margin:6px 0 0;color:#cfe6ef">Blink, shake a tool, hold up a glyph, melt, burn, sit down, lie in chalk. Two frames, one accent colour: the row's class. It may never show a fact the row does not show in text, so the cast can vanish under <span class="kbd">c</span> and nothing is lost. Under <code>prefers-reduced-motion</code> every sprite is frame A, still: on fire, but still.</p></div>
-        <div><span class="lbl">what a sprite is</span><p style="margin:6px 0 0;color:#cfe6ef">One file, <code>cockpit/sprites/builder.svg</code>, under 3 KB, 24 × 24, six fills (<code>b</code> garment, <code>s</code> face, <code>h</code> hat and tool, <code>p</code> print, <code>d</code> dark, <code>a</code> accent), seven groups for the modes. Original line work; no stock, no game, no named character. Reviewed like code.</p></div>
+        <div><span class="lbl">what a sprite may do</span><p style="margin:6px 0 0;color:#cfe6ef">Blink, work its own tool, glance, sag, burn, wear a halo or lie in chalk. Up to 2 authored key poses use interpolated transforms. Only the selected visible detail animates. Calm removes artwork without losing actor, lifecycle, class or event text. Hidden, offscreen and reduced-motion previews do no animation work.</p></div>
+        <div><span class="lbl">what a sprite is</span><p style="margin:6px 0 0;color:#cfe6ef">One editable SVG under <code>chibi/</code>, with 6 material roles and restrained cel shading. Smooth source geometry replaces the retired 24 × 24 grid and 3 KB cap. Phosphor stays in the timeline; sticker is confined to detail headers and the illustrated Phase 2 selector. The 22 px event rows, keyboard map and 3 strike boxes stay unchanged.</p></div>
       </div>
     </section>
   </div>
@@ -162,204 +82,8 @@
 </x-dc>
 <script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1440,"height":1500}}'>
 class Component extends DCLogic {
-  grid() { return Array.from({ length: 24 }, () => Array(24).fill('.')); }
-  put(g, rows, y0, x0) {
-    rows.forEach((r, j) => { for (let i = 0; i < r.length; i++) { const ch = r[i]; const y = y0 + j, x = x0 + i; if (ch !== '.' && y >= 0 && y < 24 && x >= 0 && x < 24) g[y][x] = ch; } });
-  }
-  paths(g) {
-    const out = { b: [], s: [], h: [], p: [], d: [], a: [] };
-    for (let y = 0; y < 24; y++) for (let x = 0; x < 24; x++) { const ch = g[y][x]; if (out[ch]) out[ch].push('M' + x + ' ' + y + 'h1v1h-1z'); }
-    const j = (k) => out[k].join('');
-    return { b: j('b'), s: j('s'), h: j('h'), p: j('p'), d: j('d'), a: j('a') };
-  }
-  body() {
-    return [
-      '........................','........................','........................','........................','........................',
-      '........bbbbbbbb........','.......bssssssssb.......','.......bssssssssb.......','.......bssssssssb.......','.......bssssssssb.......',
-      '.......bssssssssb.......','.......bssssssssb.......','........bbbbbbbb........','......bbbbbbbbbbbb......','.....bbbbbbbbbbbbbb.....',
-      '....bb.bbbbbbbbbb.bb....','....bb.bbbbbbbbbb.bb....','.......bbbbbbbbbb.......','.......bbbbbbbbbb.......','.......bbbbbbbbbb.......',
-      '.......bbb....bbb.......','.......bbb....bbb.......','.......bbb....bbb.......','......bbbb....bbbb......'
-    ];
-  }
-  characters() {
-    const cheetah = [[14,7],[14,11],[15,9],[15,14],[16,12],[17,8],[17,15],[18,11],[19,9],[19,14]];
-    return {
-      builder: { name: 'the builder', actor: 'claude-code.*', bio: 'jackhammer · cheetah overalls · hat on fire · cigarette',
-        layers: [
-          { y: 2, rows: ['........hhhhhhhh........','.......hhhhhhhhhh.......','......hhhhhhhhhhhh......','.....hhhhhhhhhhhhhh.....'] },
-          { y: 10, x: 16, rows: ['hhha'] }
-        ],
-        flames: [[0,10],[0,14],[1,9],[1,10],[1,13],[1,14],[1,15]],
-        print: cheetah,
-        tool: { y: 11, x: 18, rows: ['..dd..','..dd..','.hhhh.','..hh..','..hh..','..hh..','..hh..','..hh..','..hh..','..hh..','.hhhh.','.hhhh.'] },
-        smoke: [[7,20],[5,21],[3,22]] },
-      reviewer: { name: 'the reviewer', actor: 'kgme.review', bio: 'monocle · too many teeth · spiked collar · the loupe',
-        layers: [
-          { y: 2, rows: ['........hhhhhhhhh.......','.......hhhhhhhhhhh......','....hhhhhhhhhhhhhhhhh...'] },
-          { y: 6, x: 12, rows: ['hhhh','h..h','h..h','hhhh'] },
-          { y: 13, rows: ['.......d.d.d.d.d........'] }
-        ],
-        teeth: true,
-        tool: { y: 12, x: 17, rows: ['.hhhh.','h....h','h.aa.h','h.aa.h','.hhhh.','.h....','h.....'] } },
-      arbiter: { name: 'the arbiter', actor: 'arbiter.*', bio: 'skull · wizard hat · star staff · robe of stars',
-        layers: [
-          { y: 0, rows: ['............a...........','...........hh...........','..........hhhh..........','.........hhhhhh.........','........hhhhhhhh........','......hhhhhhhhhhhh......'] },
-          { y: 3, x: 19, rows: ['.a.','aaa','.a.'] },
-          { y: 6, x: 20, rows: ['h','h','h','h','h','h','h','h','h','h','h','h','h','h','h','h','h'] }
-        ],
-        skull: true,
-        stars: [[14,9],[16,13],[18,8],[19,15]] },
-      guard: { name: 'the guard', actor: 'kgme.guard', bio: 'riot helmet · halo · wings · shield says no',
-        layers: [
-          { y: 0, rows: ['.........aaaaaa.........','........a......a........'] },
-          { y: 2, rows: ['........hhhhhhhh........','.......hhhhhhhhhh.......','.......hhhhhhhhhh.......','.......hhhhhhhhhh.......'] },
-          { y: 8, rows: ['........dddddddd........'] },
-          { y: 13, x: 0, rows: ['.hhhhh','hhhhhh','hdhhdh','hhddhh','hdhhdh','hhhhhh','.hhhh.','..hh..'] },
-          { y: 14, x: 18, rows: ['hhhhhh'] }
-        ],
-        wings: true },
-      scribe: { name: 'the scribe', actor: 'kgme.*', bio: 'reaper · hood · the ledger is the book of the dead · quill',
-        layers: [
-          { y: 1, rows: ['.........hhhhhh.........','.......hhhhhhhhhh.......','......hhhhhhhhhhhh......','.....hhhhhhhhhhhhhh.....','.....hh..........hh.....','.....hh..........hh.....','.....hh..........hh.....','.....hh..........hh.....','.....hh..........hh.....'] },
-          { y: 0, x: 19, rows: ['...a','..hh','.hh.','hh..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..','.h..'] },
-          { y: 15, x: 1, rows: ['hhhhh','haaah','hhhhh','haaah','hhhhh'] }
-        ],
-        voidFace: true },
-      michou: { name: 'you', actor: 'michou', bio: 'bucket hat · shades · chain · flip phone · cheetah hoodie',
-        layers: [
-          { y: 1, rows: ['.........hhhhhhh........','........hhhhhhhhh.......','........hhhhhhhhh.......','........hhhhhhhhh.......','.....hhhhhhhhhhhhhhh....'] },
-          { y: 8, rows: ['........dddddddd........'] },
-          { y: 13, rows: ['........a.a.a.a.a.......'] },
-          { y: 6, x: 17, rows: ['hh','hh','hh','hh','.h'] }
-        ],
-        print: cheetah },
-      stranger: { name: 'the stranger', actor: 'default', bio: 'tv static for a face · antenna · no file yet',
-        layers: [
-          { y: 1, rows: ['.........h....h.........','..........h..h..........','...........hh...........','...........hh...........'] },
-          { y: 15, rows: ['..........dddd..........'] }
-        ],
-        staticFace: true }
-    };
-  }
-  modes() {
-    const Q = ['.aaa.','....a','..aa.','.....','..a..'];
-    const BANG = ['..a..','..a..','..a..','.....','..a..'];
-    const Z = ['.aaa.','...a.','..a..','.a...','.aaa.'];
-    const SPARK = ['..a..','.aaa.','aaaaa','.aaa.','..a..'];
-    const SWEAT = ['..a..','.aaa.','.aaa.','..a..'];
-    return [
-      { key: 'idle',      label: 'idle',             accent: '#39d0ff', cls: 'm-idle',      A: { eyes: 'open',  mouth: 'smile' }, B: { eyes: 'shut', mouth: 'smile', smokeB: true } },
-      { key: 'working',   label: 'working',          accent: '#39d0ff', cls: 'm-working',   A: { eyes: 'tall',  mouth: 'flat', toolDy: 0 }, B: { eyes: 'tall', mouth: 'flat', toolDy: -1, sparks: true, smokeB: true } },
-      { key: 'waiting',   label: 'waiting on you',   accent: '#ffb02e', cls: 'm-waiting',   A: { eyes: 'open',  mouth: 'oh', overlay: Q, ox: 18, oy: 0, tap: false }, B: { eyes: 'open', mouth: 'oh', overlay: Q, ox: 18, oy: 1, tap: true } },
-      { key: 'transient', label: 'transient',        accent: '#ffb02e', cls: 'm-transient', A: { eyes: 'open',  mouth: 'wavy', overlay: SWEAT, ox: 2, oy: 5, melt: 1 }, B: { eyes: 'open', mouth: 'wavy', overlay: SWEAT, ox: 2, oy: 6, melt: 2 } },
-      { key: 'blocked',   label: 'blocked · on fire', accent: '#ff3d7f', cls: 'm-blocked',   A: { eyes: 'cross', mouth: 'wavy', overlay: BANG, ox: 18, oy: 0, sit: true, fire: 0 }, B: { eyes: 'cross', mouth: 'wavy', overlay: BANG, ox: 18, oy: 0, sit: true, fire: 1 } },
-      { key: 'done',      label: 'done',             accent: '#4de38a', cls: 'm-done',      A: { eyes: 'shades', mouth: 'grin', halo: true, overlay: SPARK, ox: 18, oy: 0 }, B: { eyes: 'shades', mouth: 'grin', halo: true } },
-      { key: 'asleep',    label: 'asleep',           accent: '#6f8290', cls: 'm-asleep',    A: { eyes: 'shut',  mouth: 'oh', chalk: true, overlay: Z, ox: 18, oy: 0 }, B: { eyes: 'shut', mouth: 'oh', chalk: true, overlay: Z, ox: 18, oy: 1 } }
-    ];
-  }
-  face(g, ch, f) {
-    if (ch.staticFace) {
-      for (let y = 6; y <= 11; y++) for (let x = 8; x <= 15; x++) g[y][x] = ((x + y + (f.smokeB || f.sparks || f.tap ? 1 : 0)) % 2) ? 'd' : 's';
-      return;
-    }
-    if (ch.voidFace) {
-      for (let y = 6; y <= 11; y++) for (let x = 8; x <= 15; x++) g[y][x] = 'd';
-      if (f.eyes !== 'shut') { g[8][9] = 'a'; g[8][10] = 'a'; g[8][13] = 'a'; g[8][14] = 'a'; }
-      if (f.eyes === 'cross') { g[7][9] = 'a'; g[7][14] = 'a'; g[9][9] = 'a'; g[9][14] = 'a'; }
-      return;
-    }
-    if (ch.skull) {
-      g[7][9] = 'd'; g[7][10] = 'd'; g[8][9] = 'd'; g[8][10] = 'd'; g[7][13] = 'd'; g[7][14] = 'd'; g[8][13] = 'd'; g[8][14] = 'd';
-      g[9][11] = 'd'; g[9][12] = 'd';
-      for (let x = 8; x <= 15; x++) g[11][x] = (x % 2) ? 'd' : 's';
-      if (f.eyes === 'cross') { g[7][9] = 'a'; g[8][10] = 'a'; g[7][14] = 'a'; g[8][13] = 'a'; }
-      if (f.eyes === 'shades') for (let x = 8; x <= 15; x++) { g[7][x] = 'd'; g[8][x] = 'd'; }
-      return;
-    }
-    const E = f.eyes;
-    if (E === 'open' || E === 'tall') { g[8][9] = 'd'; g[8][10] = 'd'; g[8][13] = 'd'; g[8][14] = 'd'; }
-    if (E === 'tall') { g[9][9] = 'd'; g[9][10] = 'd'; g[9][13] = 'd'; g[9][14] = 'd'; g[7][9] = 'd'; g[7][14] = 'd'; }
-    if (E === 'shut') { g[9][9] = 'd'; g[9][10] = 'd'; g[9][13] = 'd'; g[9][14] = 'd'; }
-    if (E === 'cross') { g[7][9] = 'd'; g[7][10] = 'd'; g[9][9] = 'd'; g[9][10] = 'd'; g[8][9] = 'd'; g[7][13] = 'd'; g[7][14] = 'd'; g[9][13] = 'd'; g[9][14] = 'd'; g[8][14] = 'd'; }
-    if (E === 'shades') for (let x = 8; x <= 15; x++) { g[8][x] = 'd'; g[9][x] = 'd'; }
-    if (ch.teeth) { for (let x = 8; x <= 15; x++) g[10][x] = (x % 2) ? 'd' : 's'; g[11][9] = 'd'; g[11][14] = 'd'; return; }
-    const M = f.mouth;
-    if (M === 'smile') { g[10][10] = 'd'; g[10][13] = 'd'; g[11][11] = 'd'; g[11][12] = 'd'; }
-    if (M === 'flat') { g[10][10] = 'd'; g[10][11] = 'd'; g[10][12] = 'd'; g[10][13] = 'd'; }
-    if (M === 'oh') { g[10][11] = 'd'; g[10][12] = 'd'; g[11][11] = 'd'; g[11][12] = 'd'; }
-    if (M === 'wavy') { g[10][9] = 'd'; g[11][10] = 'd'; g[10][11] = 'd'; g[11][12] = 'd'; g[10][13] = 'd'; }
-    if (M === 'grin') { for (let x = 9; x <= 14; x++) g[10][x] = 'd'; g[11][10] = 'd'; g[11][13] = 'd'; }
-  }
-  frame(ch, f) {
-    const g = this.grid();
-    const body = this.body().slice();
-    if (f.sit) { body[20] = '....bbbbbbbbbbbbbbbb....'; body[21] = '....bbb..........bbb....'; body[22] = '....bbb..........bbb....'; body[23] = '...bbbb..........bbbb...'; }
-    if (f.tap) { body[22] = '.......bbb.....bbb......'; body[23] = '......bbbb....bbbbb.....'; }
-    this.put(g, body, 0, 0);
-    if (ch.print) ch.print.forEach(([y, x]) => { if (g[y][x] === 'b') g[y][x] = 'p'; g[y][x + 1] = g[y][x + 1] === 'b' ? 'p' : g[y][x + 1]; });
-    if (ch.stars) ch.stars.forEach(([y, x]) => { g[y][x] = 'a'; });
-    if (ch.wings) {
-      const w = f.sparks || f.tap || f.smokeB ? 1 : 0;
-      this.put(g, ['bb..','bbb.','bbbb','.bbb','..bb'], 12 + w, 0); this.put(g, ['..bb','.bbb','bbbb','bbb.','bb..'], 12 + w, 20);
-    }
-    this.face(g, ch, f);
-    (ch.layers || []).forEach((L) => this.put(g, L.rows, L.y, L.x || 0));
-    if (ch.tool) this.put(g, ch.tool.rows, ch.tool.y + (f.toolDy || 0), ch.tool.x);
-    if (ch.flames && !f.fire && f.fire !== 0) ch.flames.forEach(([y, x]) => { g[y + (f.smokeB ? 1 : 0)][x] = 'a'; });
-    if (ch.flames && f.fire === undefined) ch.flames.forEach(([y, x]) => { g[y][x] = 'a'; });
-    if (ch.smoke && f.smokeB) ch.smoke.forEach(([y, x]) => { g[y][x] = 'a'; });
-    if (f.sparks && ch.tool) { g[23][ch.tool.x] = 'a'; g[22][ch.tool.x + 5] = 'a'; g[21][ch.tool.x - 1] = 'a'; }
-    if (f.sparks && !ch.tool) { g[12][2] = 'a'; g[12][21] = 'a'; }
-    if (f.melt) { this.put(g, ['bb..bb','bbb.bb','.bb.b.'].slice(0, f.melt + 1), 21 + (3 - f.melt), 8); this.put(g, ['aa.a'], 23, 7); }
-    if (f.fire !== undefined) {
-      const F = f.fire ? ['......a....a....a.......','.....aa...aaa..aa.......','....aaa.aaaaa.aaa.......','....aaaaaaaaaaaaa.......','.....aaaaaaaaaaa........','......aaaaaaaaa.........']
-                       : ['........a.....a.........','.......aaa...aa.........','......aaaa..aaaa........','.....aaaaaaaaaaaa.......','......aaaaaaaaaa........','.......aaaaaaaa.........'];
-      this.put(g, F, 0, 0);
-    }
-    if (f.halo) this.put(g, ['.........aaaaaa.........','........a......a........'], 0, 0);
-    if (f.overlay) this.put(g, f.overlay, f.oy, f.ox);
-    if (f.chalk) return this.chalk(g);
-    return this.paths(g);
-  }
-  chalk(g) {
-    const r = this.grid();
-    for (let y = 0; y < 24; y++) for (let x = 0; x < 24; x++) { const ch = g[y][x]; if (ch === '.') continue; const ny = 23 - x, nx = y; r[ny][nx] = ch === 'a' && (y < 5 && x > 16) ? 'a' : 'b'; }
-    const o = this.grid();
-    for (let y = 0; y < 24; y++) for (let x = 0; x < 24; x++) {
-      if (r[y][x] === '.') continue;
-      const n = [[y - 1, x], [y + 1, x], [y, x - 1], [y, x + 1]].some(([yy, xx]) => yy < 0 || yy > 23 || xx < 0 || xx > 23 || r[yy][xx] === '.');
-      if (r[y][x] === 'a') o[y][x] = 'a'; else if (n) o[y][x] = 'a';
-    }
-    for (let x = 0; x < 24; x++) if (o[23][x] === '.') o[23][x] = 'd';
-    return this.paths(o);
-  }
-  sprite(ch, mode, pal) {
-    const A = this.frame(ch, mode.A), B = this.frame(ch, mode.B);
-    return { cls: mode.cls, label: ch.name + ', ' + mode.label, cb: pal.b, cs: pal.s, ch: pal.h, cp: pal.p, cd: pal.d, ca: mode.accent,
-      a_b: A.b, a_s: A.s, a_h: A.h, a_p: A.p, a_d: A.d, a_a: A.a, b_b: B.b, b_s: B.s, b_h: B.h, b_p: B.p, b_d: B.d, b_a: B.a };
-  }
   renderVals() {
-    const chars = this.characters(), modes = this.modes();
-    const phosphor = { b: '#cfe6ef', s: '#6f8290', h: '#8fb4c4', p: '#0a0c10', d: '#0a0c10' };
-    const stickerPal = {
-      builder: { b: '#e8a33d', s: '#ffd9c2', h: '#ffd23f', p: '#3b2412', d: '#2a2340' },
-      reviewer: { b: '#2bb3a3', s: '#ffd9c2', h: '#8b5e3c', p: '#2a2340', d: '#2a2340' },
-      arbiter: { b: '#5b5bd6', s: '#f2f2f2', h: '#2b2d6b', p: '#2a2340', d: '#2a2340' },
-      guard: { b: '#ff7ab8', s: '#ffd9c2', h: '#c9d1d9', p: '#2a2340', d: '#2a2340' },
-      scribe: { b: '#1b1b24', s: '#0a0a0f', h: '#c9d1d9', p: '#2a2340', d: '#0a0a0f' },
-      michou: { b: '#e8a33d', s: '#ffd9c2', h: '#3b82f6', p: '#3b2412', d: '#2a2340' },
-      stranger: { b: '#9aa3ad', s: '#d9dee3', h: '#9aa3ad', p: '#2a2340', d: '#2a2340' }
-    };
-    const order = ['builder', 'reviewer', 'arbiter', 'guard', 'scribe', 'michou', 'stranger'];
-    const cast = order.map((k) => ({ name: chars[k].name, actor: chars[k].actor, bio: chars[k].bio, modes: modes.map((m) => this.sprite(chars[k], m, phosphor)) }));
-    const stickers = order.map((k, i) => { const sp = this.sprite(chars[k], modes[i % 2], stickerPal[k]); sp.label = chars[k].name; return sp; });
-    const ctx = {
-      builder: this.sprite(chars.builder, modes[1], phosphor),
-      reviewer: this.sprite(chars.reviewer, modes[3], phosphor),
-      arbiter: this.sprite(chars.arbiter, modes[4], stickerPal.arbiter),
-      guard: this.sprite(chars.guard, modes[2], phosphor)
-    };
-    return { cast, stickers, ctx };
+    return { fixtureSource: './chibi/preview.html?embed=1' };
   }
 }
 </script>
--- a/docs/design/cockpit-v0/canvas.json
+++ b/docs/design/cockpit-v0/canvas.json
@@ -33,7 +33,7 @@
     "t2": {"x": 0, "y": 1460, "text": "Keyboard map · Phase 2 controls, greyed · wall layout · sprites", "kind": "title1", "maxW": 7120},
     "s1": {"x": 1520, "y": 960, "w": 520, "text": "Rule of the whole design: signal in the centre, noise at the edges. Everything outside the three columns (frame, tick rails, micro-labels, scanlines, vignette) carries no information and collapses under the c key or prefers-reduced-motion. Every row shown here is a real event shape from logs/ledger; paths are repo-relative.", "fill": "teal"},
     "s2": {"x": 4560, "y": 960, "w": 520, "text": "The frame carries system state: cyan while the ledger is live, magenta flood on a blocking outcome or halt, grey static when the server is unreachable. The three strike boxes are ADR-016's bound: they fill as one root cause survives cycles and go magenta on halt.", "fill": "pink"},
-    "s3": {"x": 5680, "y": 3320, "w": 520, "text": "Sprites are noise that mirrors one bit of signal: the mode repeats the row's class chip and nothing else, so c hides the whole cast and reduced motion freezes it. Phosphor palette in the timeline; the sticker palette only in the detail header and the Phase 2 model selector. Original line work, no stock or game assets.", "fill": "purple"}
+    "s3": {"x": 5680, "y": 3320, "w": 520, "text": "CDH-0001: 7 illustrated actors, 7 modes and 6 shaded material roles. Modes mirror adjacent actor, lifecycle, class and event text; they are not failure classes. Static 24 px phosphor portraits sit in run headers, outside 22 px ledger rows. Sticker remains confined to 72 px detail headers and the illustrated Phase 2 model selector. Only 1 selected visible detail animates; calm, hidden, offscreen and reduced-motion states remove animation work. Board 10 embeds the shared local fixture; native import and playback await CDH-0002.", "fill": "purple"}
   },
   "designSystems": []
 }
```

</details>

CDH-0001 is ready for local closeout. CDH-0002 remains open for Michou’s start signal; only that independent native review can resolve the native acceptance gaps.
