---
id: AUDIT-CDH-0029-FOLLOWUP
type: report
created: 2026-10-25T16:08:23-07:00
handoff: CDH-0029
period: "2026-10-25"
source: inferred
sources:
  - CDH-0029
  - Michou's direct follow-up and attached image, 2026-10-25
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/cdh-0029-followup/
author: codex
status: final
tier: 2
---

# CDH-0029 direct follow-up

The 2 requested changes are built: a graphic space treatment drawn from Michou's image, and continuous background coverage when zooming out or dragging. He clarified that the trailing “also” did not add a third request. This is a direct follow-up to builder commit 86f145f under the existing design mandate. It does not adopt or execute CDH-0030, change the historical CDH-0029 handoff, or claim Cowork's native pass. Main advanced independently from ce86a885a0c608d927aa23acfa94b03c4a060ffd to 997a730eb950fb2e8ab844c467a90b3e937da21b; this builder did not merge, modify main or push.

## Delivery and root cause

The old wash was a finite world-space plane and the outer grid was 40 scene units wide. A long diagonal drag exposed the wash's straight vertical/horizontal boundary; minimum zoom exposed the grid perimeter. Increasing their dimensions would only move those edges farther away. The decorative outer grid is removed, while the station's hull and room outlines are unchanged. The nebula now draws an opaque full-viewport quad in clip space, before scene geometry, without depth writes or frustum culling. It cannot run out at the camera edge. Both star layers wrap in viewport space, keeping 0.12 / 0.45 pan coefficients and fixed point sizes. Planet positions remain in world space, so moving past a planet still feels spatial.

The reference supplies 4 concrete visual decisions: near-black negative space; saturated magenta, cobalt and violet; engraved planetary contours with amber/orange polar bands; and cut, grainy nebula structure. Planet lighting is quantized, surfaces combine irregular colour bands with dark etching, and rings use sharp stripes. The deck and text lead in luminance. There are still 8 planets on desktop and 3 on phone, with 5,200 far points plus 700 near points on desktop and only the far layer on phone. The sky retains its own frozen-under-reduced-motion clock, slow rotation and 111 gently twinkling points. No dependency, raster asset, import or fetch was added to the shipped page. The supplied reference is retained only in ignored local evidence.

The source comparison permits only the ambient component and removal of the decorative GridHelper line. Everything else is byte-identical to 86f145f, including CSS, markup, room and hull geometry, facts, chip dimensions, focus handling, controls and replay logic. The ambient component reads no ledger, event, room, quota or hull fact.

## Verification

The 32 coverage cases combine 4 sizes (1440 × 900, 800 × 600, 400 × 700 and 2560 × 600), 2 motion settings, and 4 camera states (home, minimum zoom, 6 long diagonal drags in one direction, then 12 in the opposite direction). Each non-home case asserts camera zoom 0.6. A fixture makes the scene clear colour red and renders only the real nebula: every screenshot has 0 uncovered red pixels. A second pass renders only the real stars against black and counts visible pixels in 12 viewport tiles; the least-populated tile still has 93 lit pixels. This tests actual pixel coverage after repeated pans, including an unusually wide aspect ratio. Before/after source previews preserve the visible defect and the repaired composition. The fixture initially used 1 large wheel delta, which the control handles as 1 step; it was corrected to 8 separate ticks, with the 0.6 assertion retained. A fixture-only visibility boolean was also corrected before the final coverage run.

All 24 text/background cases pass across the 3 required sizes, deck and pane, calm and calm system pane, reduced motion on and off: 1,780 visible text boxes, 419,946 sampled pixels, minimum 4.592580:1. Text fill is masked while backgrounds and borders remain, and periodic word updates are paused during each pixel sample. All 3 ten-second reduced-motion comparisons retain identical decoded sky pixels and transforms. The 6 calm cases hide the stage and freeze the sky clock. Full-motion time advances.

At default zoom, the uninstrumented station has 0 pair overlaps across all 7 chip rectangles at 1440 × 900, 800 × 600 and 400 × 700. Keyboard runs cover all 7 room targets at each size and verify visible bounds and centre hit testing. The 120 px pan moves a tracked far star 14.394672 px and a near star 53.980021 px, preserving the 3.75× ratio. The inspector projects the shader's wrapped coordinates. A separate stars-only comparison after camera easing settles records 148 changed pixels over 2.5 seconds and 4565 lit pixels, confirming visible twinkle.

The offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 32.58 seconds. Local browser fixtures use the existing pinned three@0.182.0, block external traffic and report 0 page, console, HTTP or external-request errors. No package was installed. Screenshots and inspectors remain under ignored scratch paths. Native host behaviour and Michou's judgement of the revised look remain pending.

## Frame budget

Six sequential 30-second replays at ×2 use Chromium's ANGLE Metal renderer on Apple M4 Pro. The baseline is CDH-0026 at 8f49559, with only dependency URLs redirected locally. The sky=0 comparison omits the new sky; the removed decorative grid stays removed. No other GPU test or capture runs during these measurements. Raw frame intervals and replay-clock endpoints are retained.

| Viewport | Variant | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | cdh26 | 1800 | 16.666056 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | without | 1800 | 16.665944 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | with | 1800 | 16.666000 | 16.700 | 16.800 | 16.800 |
| 400 × 700 | cdh26 | 1800 | 16.666000 | 16.700 | 16.800 | 16.800 |
| 400 × 700 | without | 1799 | 16.675320 | 16.700 | 16.800 | 33.400 |
| 400 × 700 | with | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |

1440 px change versus baseline: mean -0.000056 ms, P95 0.100000 ms. 400 px change versus baseline: mean 0.000000 ms, P95 -0.100000 ms. Both remain inside the 2 ms budget. These are local frame-interval observations, not a claim about every native host.

## Decisions and closeout

Reference-inspired graphic treatment: 3 × 0.3 = 0.9, implemented from Michou's explicit direction and listed for his native look. Removal of the finite decorative grid: 2 × 0.2 = 0.4, because its visible perimeter caused the reported defect and the reference calls for open space. Full-viewport wash and wrapped points: 2 × 0.1 = 0.2, a bounded implementation fix for unbounded camera movement. No additional brief is needed. The 40-line lessons file records viewport coverage and verification at actual minimum zoom. No personal memory or ledger was written; the missing personal MEMORY.md index remains nonessential to this design task.

The direct follow-up is complete as a builder delivery. Stop for Cowork's combined native pass and Michou's revised look. CDH-0030 remains untouched; no canvas approval is claimed.

## Delivered text SHA-256

The report excludes its own digest. The shared README digest describes this delivery.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | 3ada236ef5c6211c5cd273ae279d50abc9e4f43b7f65cd9fde3b6354db3bb31a |
| docs/handoff/cockpit-design/README.md | 2924652295fb55f69f63d9f14c5ee8261cce9dd3b5be3ea0f0564c5d7339551a |
| docs/readers/cockpit-design-lessons.md | b03b5150553714f54638d4a6a8c8e827f4ebf66444988ebdceac74984edf259c |

## Evidence SHA-256

The 85 PNGs, including the user-supplied reference, have individual digests in capture-hashes.json.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/cdh-0029-followup/before.html | 9121f26ca4e397aade67e6154ad8dceb811cf5c5da7058b93b369069a613e517 |
| logs/scratch/design-review/cdh-0029-followup/before.mjs | e1a11374480b916cf9843dcf0e0990e4d20139e9e7748863a9697533cafd1a99 |
| logs/scratch/design-review/cdh-0029-followup/prepare.mjs | 9d8edfb908778aa2b608705851b5eac5816bd554ff245cb3d1ea601ce03b5125 |
| logs/scratch/design-review/cdh-0029-followup/source-checks.json | 525b0a6eb43864ddd4191484b07530dc7389f6fe090ae836d4bd1cba3873be29 |
| logs/scratch/design-review/cdh-0029-followup/preview.mjs | 5bb622f9c50994bb247c72beb9592c149ef63eca478564499d9842f3cce1cf0d |
| logs/scratch/design-review/cdh-0029-followup/coverage.mjs | 1954fa45f51270088d4dc4696f409e3f1b6cfeffecb6ae03b19a2dbd6a0bd266 |
| logs/scratch/design-review/cdh-0029-followup/coverage-manifest.json | b7796067a7037211013970dfa05a7349f4df99f9dec4a1197ff6f0b6a60cecde |
| logs/scratch/design-review/cdh-0029-followup/verify.mjs | 97c913dfaba514a72f8a2d0cee369a19bd798101e2a16da5af964164ffe17132 |
| logs/scratch/design-review/cdh-0029-followup/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/cdh-0029-followup/visual-manifest.json | 0747d592704e91523ab03d61b53cb983a249138c8982bcbf649e44ff3cd77d78 |
| logs/scratch/design-review/cdh-0029-followup/focus.mjs | 032e9838e05f178a082efd7b056f150b1d5935e37a00f2394f6438295c210b2d |
| logs/scratch/design-review/cdh-0029-followup/focus-manifest.json | 354557e9bb42372caa0baf21943c6b0706ef689789d895b5fda21737d8ddd1fd |
| logs/scratch/design-review/cdh-0029-followup/depth.mjs | e05c18f3e24574221482d0f8331dd77e711cdb5a381b994f8f24c6415143926a |
| logs/scratch/design-review/cdh-0029-followup/depth-manifest.json | af4c741b45fcc681eb2a5ffb85085daec95b28021a09a8dc397e6ba022434678 |
| logs/scratch/design-review/cdh-0029-followup/performance-manifest.json | b92ceca639555c8ba47b3b82132d900eacc4f1a6bc9b3707de84da74f056eb7c |
| logs/scratch/design-review/cdh-0029-followup/station-cdh26-baseline.html | ed1b3b763fdac1d289cb2a59624b31aee6723adaba9ca4fc662eed8e5c9501ec |
| logs/scratch/design-review/cdh-0029-followup/capture-hashes.json | ba9db5da432b998a11a313e423dc90cd0134af288e7b3b6dd55e4130aa6f26f5 |
| logs/scratch/design-review/cdh-0029-followup/make-check.log | 111c8cefffe41178ed3850a034c11fc7ee9f99d7c47eaec7beb9412d62ec97d9 |
| logs/scratch/design-review/cdh-0029-followup/closeout-lint.log | 851ef4cfe0f1cc45d8c1aa7fb5134f835e6372275c4e501c1b36bac1cb6c76e8 |
