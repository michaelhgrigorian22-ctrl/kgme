---
id: AUDIT-CDH-0019-STATION-CASINO
type: report
created: 2026-10-25T16:33:28-07:00
handoff: CDH-0019
period: "2026-10-25"
source: inferred
sources:
  - Michou's direct station instruction and attached image, 2026-10-25
  - CDH-0019
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/station-casino/
author: codex
status: final
tier: 2
---

# Station: orbital casino reference

Michou accepted the space background at be4638f and asked for the terminal ship to take its silhouette, mechanical detail and presence from his attached orbital casino image. The direct build is complete under CDH-0019. Cowork's native pass and Michou's look remain pending. The starting main ref was 997a730eb950fb2e8ab844c467a90b3e937da21b; the closeout ref is 997a730eb950fb2e8ab844c467a90b3e937da21b. No main merge, push, dependency installation or native publication occurred. CDH-0030 and the finished CDH-0029 handoff are untouched.

## Delivery

The hull is now an open orbital rotunda: a rounded working island, an annular promenade connected by 8 bridges, 3 stacked habitat rings, radial supports and a stepped underside. The rings carry 3-row window bands, silver bearing rims, copper supports, 36 moving service saddles per tier and inset running lights. A ribbed copper lower spindle has 4 docking collars and a beacon; an upper tower carries 8 solar panels with 12 fine ribs each. Three docking bays and 56 small promenade lights add physical detail. This is procedural Three.js geometry and material work, with no imported model or bitmap asset.

The 3 rings rotate at +0.006, -0.004 and +0.008 radians per second, approximately 17.5, 26.2 and 13.1 minutes per revolution. Their own clock freezes under reduced motion and calm. Rotation happens inside fixed elliptical bearings, so the silhouette does not wobble. Static mechanical details are combined by material, and moving saddles and lamps use instanced meshes. The 3 structural trim loops share the existing lineCyan material, so the original hull state still governs them. Other windows and metal accents are decorative.

All 7 room coordinates, crew seats, labels, chip dimensions, event rules, pane behaviour, shortcuts, pan/zoom controls and existing crew motion remain byte-identical. The default target moves down by 0.3 scene units to frame the taller hull. At 1440 × 900, the measured non-instanced shell vertices span y=87.713–818.459 px, inside HUD boundaries 80.938–826.063 px; the actual screenshot was inspected for the ring saddles too. Smaller viewports retain the established pan/follow framing, and their 7 focus targets remain reachable. Default, minimum-zoom and panned previews were inspected. The final zoom capture asserts 0.600 after 8 wheel ticks aimed at unoccluded sky.

The entire accepted background component is byte-identical to be4638f: its palettes, planets, nebula, continuous coverage, star field and parallax remain intact. The source comparison permits only the hull construction, the home-framing line and the shell tick call. All CSS and DOM remain unchanged, as do imports and fetches. The shell animation reads no event, run, room or replay value.

## Verification

All 24 text/background cases pass at 1440 × 900, 800 × 600 and 400 × 700, across deck, pane, calm wall and calm system pane, with reduced motion on/off. There are 1,772 visible text boxes and 419,463 sampled pixels, with minimum contrast 4.592580:1. Text fill is masked while backgrounds and borders remain, and periodic word updates are paused during sampling. All 3 sky-only reduced-motion captures remain pixel-identical over 10 seconds. The 6 calm cases hide the stage and freeze the sky.

A separate 6-case shell test uses actual rendered geometry with fixed ambient/directional lighting. All 3 reduced-motion pairs retain identical decoded RGB buffers and rotor transforms over 10 seconds. All 3 full-motion cases change pixels over 2.5 seconds and all 3 rotors advance in their expected signed direction. Calm hides the stage and freezes rotor transforms. The fixture excludes room-state point lights from this isolated motion measurement: the existing refusal flash expires on a real-time timer, so pausing replay alone does not hold illumination constant. No production state-light rule was changed.

The reused 43-line synthetic halt fixture is loaded through its own fetch path, with the loaded sample count asserted. At 19:53:10 and after bookkeeping at 19:53:40, the HUD says HALT and all 3 shared trim loops read ff3d7f. After approval at 19:54:40, the HUD says nominal and all 3 loops read 39d0ff. The fixture stays in ignored scratch paths. The test fixture's initial single-string replacement changed provenance text but not the fetch; replacement and sample-count verification were corrected before these final state checks.

The uninstrumented page has 0 overlaps among all 7 room-chip rectangles at default zoom at each required size. Keyboard checks supply 21 focused-room observations per size, covering all 7 targets; every focus rectangle stays inside its HUD/frame boundaries and passes centre hit testing. The source check confirms no room-position or chip-width change.

The offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 30.21 seconds. The local browser checks use the existing pinned three@0.182.0 and block external traffic; final manifests contain 0 page, console, HTTP or external-request errors. No dependency was installed. The personal memory index was absent and is not a design prerequisite; no personal memory or ledger was written.

## Frame budget

Six sequential 30-second replays at ×2 use Chromium's ANGLE Metal renderer on Apple M4 Pro. The original baseline is CDH-0026 at 8f49559; the before variant is the accepted-background build be4638f; with is this delivery. Baseline URLs alone are redirected to the existing local package. No other browser test or screenshot runs during the timings. Raw frame intervals and clock endpoints are retained.

| Viewport | Variant | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | cdh26 | 1800 | 16.665944 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | before | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | with | 1800 | 16.666056 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | cdh26 | 1800 | 16.666000 | 16.700 | 16.800 | 16.800 |
| 400 × 700 | before | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | with | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |

1440 px versus cdh26: mean 0.000111 ms, P95 0.000000 ms. 1440 px versus before: mean 0.000056 ms, P95 0.000000 ms. 400 px versus cdh26: mean 0.000000 ms, P95 -0.100000 ms. 400 px versus before: mean 0.000000 ms, P95 0.000000 ms. Every comparison meets the 2 ms mean/P95 budget. These are local frame-interval observations; the native host remains Cowork's check.

## Decisions and closeout

Orbital-ring interpretation of the explicit reference: 4 × 0.3 = 1.2, built and listed for the native look. Open cutaway around fixed operational rooms: 3 × 0.2 = 0.6, preserving usability while changing the hull. Slow counter-rotation and a separate decoration clock: 2 × 0.2 = 0.4. The 0.3-unit framing adjustment: 2 × 0.2 = 0.4, checked against actual HUD bounds. No further brief is needed inside the given direction. The lessons file remains at 40 lines and records isolating decoration from changing event lights during pixel-stillness checks.

The README records Michou's acceptance of the background and this new builder delivery. Stop for Cowork's native pass and Michou's look; no canvas approval is claimed.

## Delivered text SHA-256

The report excludes its own digest. The README digest describes this delivery.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | b7c3f13205217ce9dba485d5bd3c65e2d7726acb9c19e1abc79f7854977468fa |
| docs/handoff/cockpit-design/README.md | 385356669d95213e1edd867e6c5de9dd830aa466d1acca2df8ac8b34b6176add |
| docs/readers/cockpit-design-lessons.md | eadf152bbc9654be49fc730f0f21ff0a1f854426b52231fd849a4656f57673a3 |

## Evidence SHA-256

The 58 PNGs, including the supplied reference, have individual digests in capture-hashes.json.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/station-casino/before.html | 3ada236ef5c6211c5cd273ae279d50abc9e4f43b7f65cd9fde3b6354db3bb31a |
| logs/scratch/design-review/station-casino/prepare.mjs | 4919572358a6219d925b82d29e0ef839fc759c452a3cb154f2bfc7b59eff19f7 |
| logs/scratch/design-review/station-casino/source-checks.json | 49538e10fda21307338c469023a02358f076a82bf23770452bf4ed0ccd2eed15 |
| logs/scratch/design-review/station-casino/preview.mjs | 307eccfa910800f400735c9806a9af5cfe0fb8c27742fa792db0bb0052581811 |
| logs/scratch/design-review/station-casino/verify.mjs | cc1661a6ef911b4389b1008d391802ea27249ae34ade8921f1431e47a0ff4728 |
| logs/scratch/design-review/station-casino/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/station-casino/visual-manifest.json | a8b77d0d0f01a42e2c051c194c4150cf10c745388d212bd5096cfae9d9a9b080 |
| logs/scratch/design-review/station-casino/ship.mjs | f99d88abfc84178723c2ae549c6723f764b06dec005d24ab396a20c00676145c |
| logs/scratch/design-review/station-casino/ship-manifest.json | b380bc0b2668c5f77f4ee22344943a0d1a8acfdf098ea4648d4fef8a37db3170 |
| logs/scratch/design-review/station-casino/sample-events-halt-synthetic.jsonl | db20ca89ab973d8c43c9bc43ed256c60187ca66f9440f427ea8f3abfaa500558 |
| logs/scratch/design-review/station-casino/focus.mjs | 4db23dcb0479982381d1bc72edf927fdc4ee015eeb341f2053bcdde30646a0ba |
| logs/scratch/design-review/station-casino/focus-manifest.json | 7bf6d32cc1cc7a70f1b782ec169d5990093637847a53833f8e878a6a6ed6b765 |
| logs/scratch/design-review/station-casino/performance-manifest.json | fa0f3865cf9738e329452ab95605d1298512550f17a97b75df9a922b6e17e603 |
| logs/scratch/design-review/station-casino/station-cdh26-baseline.html | ed1b3b763fdac1d289cb2a59624b31aee6723adaba9ca4fc662eed8e5c9501ec |
| logs/scratch/design-review/station-casino/capture-hashes.json | 3775aa0d504afa6fe063334b43d947a62d06e234e8de936ebfd998a8b0d5bc81 |
| logs/scratch/design-review/station-casino/make-check.log | a474a70f2871abbc165716dbd5e50f876301ce83ace5880c2434937b7cd15d8c |
| logs/scratch/design-review/station-casino/closeout-lint.log | 9559e88447f3d3bbf41589df715fab91c97e99b589d1141e58fd9773146e73b3 |
