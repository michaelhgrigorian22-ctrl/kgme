---
id: AUDIT-CDH-0019-DISTANT-DREADNAUGHT
type: report
created: 2026-10-25T17:00:13-07:00
handoff: CDH-0019
period: "2026-10-25"
source: inferred
sources:
  - Michou's direct instruction and attached ship reference, 2026-10-25
  - CDH-0019
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/distant-dreadnaught/
author: codex
status: final
tier: 2
---

# Station: distant dreadnaught

Michou accepted the background, current planets and casino-inspired station, then replaced his extra-planets request with 1 Dreadnaught-inspired object below the station. That direct addition is complete under CDH-0019. Cowork's native pass and Michou's look remain pending. The starting design ref was d271003, whose station source equals c3e8618. Main advanced externally from 7f1c5ea93c3005859df2bbf296831ef60716946f to ee78653a84e4f4624c8a976c97717ab8be993b2a. No merge, push, publication or dependency installation occurred. CDH-0030 and CDH-0031 remain untouched.

## Delivery

The new object is a long tapered hull with a diamond cross-section, etched armour panels, 4 spined ridges, 48 instanced upper ribs, a recessed circular side eye and an inset green bow aperture. The reference guides its silhouette and surface detail. All geometry and shading are procedural Three.js; no model, bitmap, import or fetch is added. Its 9 renderable objects include 1 line batch and 1 instanced rib batch. It introduces no light that could change the existing station or sky.

The ship sits below the station at sky-local y=-11 and z=-24, with x=0.16 times the viewport half-width. It retains its 0.68 scale on phone widths through 720 px and full scale above that. At default zoom 1 it is below the viewport; at minimum zoom 0.6 its upper edge begins to emerge, and panning the lower sky reveals the full shape. It is static, carries no fact, reads no event, room, run or animation clock, and disappears with the stage in calm mode.

A source comparison removes only 3 additions: the new helper, its attachment to ambient space, and its placement in the existing resize path. Every remaining byte equals the approved source. All 8 planets, star layers, nebula, existing motion, station geometry, room anchors, controls, camera rules, DOM, CSS and state logic are preserved.

## Verification

At 1440 × 900, 800 × 600 and 400 × 700, isolated sky screenshots with the object on/off at home have identical decoded pixels. Native wheel input reaches an asserted 0.600 zoom, then pointer dragging reveals the new object. Removing only the object from the discovered view yields the following actual changed-pixel bounds, all inside the frame and HUD boundaries. The desktop and phone compositions were also inspected visually.

| Viewport | Object pixels | Horizontal bounds px | Vertical bounds px |
| --- | ---: | --- | --- |
| 1440 × 900 | 25330 | 641–949 | 522–650 |
| 800 × 600 | 11331 | 340–545 | 332–418 |
| 400 × 700 | 7174 | 141–303 | 313–380 |

All 3 discovered-sky pairs remain pixel-identical over 10 seconds under reduced motion. The 3 existing home-sky stillness checks also pass. Calm hides the stage in all 3 discovery cases and all 6 original normal/reduced cases. The 36 text/background cases cover deck, pane, calm wall, calm system pane, lower deck and lower pane at all 3 sizes with reduced motion on/off. Their minimum contrast is 4.592580:1 across 584,691 sampled pixels. Text fill is masked while backgrounds and borders remain, and periodic word updates are frozen during sampling.

The uninstrumented page retains 0 overlaps among all 7 room-chip rectangles at default zoom at each size. Thirty Tab presses produce 21 focused-room observations per size, covering all 7 targets. Every focus rectangle stays within its HUD/frame bounds and passes centre hit testing. Chip widths and room positions are byte-identical to c3e8618.

Offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 37.02 seconds. The browser manifests contain 0 page, console, HTTP or external-request errors. Chrome uses the existing pinned three@0.182.0 package over loopback, with outside traffic blocked. No personal memory or ledger was written. The absent personal memory index is not a design prerequisite.

## Frame budget

Six sequential 30-second replays at ×2 use Chromium's ANGLE Metal renderer on Apple M4 Pro. Every variant receives the same native zoom/pan sequence before measurement, so the delivered ship is visible during its timing. The cdh26 baseline is 8f49559; before is c3e8618, unchanged in d271003; with is this delivery. No other browser test or screenshot runs concurrently. The first phone setup stopped before timing because the taller CDH-0026 HUD intercepted its centre-screen wheel input. The fixture now locates unobstructed canvas between the measured HUD bounds and asserts zoom 0.600; the 3 valid desktop runs were retained and the 3 phone runs completed afterward. The first-attempt manifest preserves this setup failure. Production controls were not changed. Raw frame intervals and clock endpoints are retained.

| Viewport | Variant | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | cdh26 | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |
| 1440 × 900 | before | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |
| 1440 × 900 | with | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |
| 400 × 700 | cdh26 | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |
| 400 × 700 | before | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |
| 400 × 700 | with | 900 | 33.332000 | 33.300 | 33.400 | 33.500 |

1440 px versus cdh26: mean 0.000000 ms, P95 0.000000 ms. 1440 px versus before: mean 0.000000 ms, P95 0.000000 ms. 400 px versus cdh26: mean 0.000000 ms, P95 0.000000 ms. 400 px versus before: mean 0.000000 ms, P95 0.000000 ms. All 4 comparisons pass the 2 ms mean/P95 budget. These are local frame-interval observations; the native host remains Cowork's check.

## Decisions and closeout

The single distant interpretation of the explicit reference scores 3 × 0.2 = 0.6 and is on the approval screen. Static muted green apertures score 2 × 0.2 = 0.4, keeping the bright casino as the focal point. The lower-sky placement and 0.68 phone scale score 2 × 0.2 = 0.4, verified by actual pixel bounds. The user supplied the direction, so no further brief was needed.

The README records the acceptance of the casino station, this direct instruction and the pending native pass. No handoff is adopted or closed by this small direct addition; CDH-0019 stays open. The lesson file is unchanged. Stop for Cowork and Michou; no canvas approval is claimed.

## Delivered text SHA-256

The report excludes its own digest. The README digest describes this delivery.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | 44afe7ef78e51f226ed444361e27c87360e3967d6330710a811596004cbaf17d |
| docs/handoff/cockpit-design/README.md | f93ba9cfb51512139d8d18874f27b7e3a8917c95504f100517b13c923af92140 |

## Evidence SHA-256

The 67 PNGs, including the supplied reference, have individual digests in capture-hashes.json. All evidence remains in ignored scratch storage.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/distant-dreadnaught/before.html | b7c3f13205217ce9dba485d5bd3c65e2d7726acb9c19e1abc79f7854977468fa |
| logs/scratch/design-review/distant-dreadnaught/prepare.mjs | d7bd44008e1beff0ff73d9f5500243de8c39a6c8737a53b478358cac66d96c9b |
| logs/scratch/design-review/distant-dreadnaught/source-checks.json | 3936630a551b4eb14df03f2af6bd6ee3c87da108b35c9b652a890ecc8b740dc5 |
| logs/scratch/design-review/distant-dreadnaught/preview.mjs | bfca2b037e0bc5e2a21e80b4bf14b5a885b51b70c4279efa4bf4e3fe2fe85183 |
| logs/scratch/design-review/distant-dreadnaught/verify-visual.mjs | 99c271775ae065c181a754ff778efd6d0e5286cce592c60ab44b9e70f0c75ad3 |
| logs/scratch/design-review/distant-dreadnaught/verify.mjs | 2a02030d8cc82f19896a0c96dea195748581d9f57ff1fd4d68906e1c85acad11 |
| logs/scratch/design-review/distant-dreadnaught/performance-first-attempt.json | 507dea7d1f0ac0640126b30d5a4d975084575db1727ab7663b8d1d6a919435d6 |
| logs/scratch/design-review/distant-dreadnaught/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/distant-dreadnaught/discovery.mjs | cf464c7a214194e436192a31c81f2ab5d4632009c6b6fd3e1f2f6b8b26dc3c7f |
| logs/scratch/design-review/distant-dreadnaught/discovery-manifest.json | d283598b505a2a01f46705e4088dea06680c4a593461adea9cb3ec2437a230f4 |
| logs/scratch/design-review/distant-dreadnaught/focus.mjs | a8fd2ae62c2e570486563575f942da3892291f3f434bf46055ea60b3880991a5 |
| logs/scratch/design-review/distant-dreadnaught/focus-manifest.json | 0c70a8da1fba2be428065e1f472b8e41f0227e0dcb9dea858156137e90f27c7b |
| logs/scratch/design-review/distant-dreadnaught/visual-manifest.json | ddf7e7013fa31f8805167fc7a66dfb5c1b994b52f3913a37d653001f240622b8 |
| logs/scratch/design-review/distant-dreadnaught/performance-manifest.json | 22ecafe3e4163fe35d90f6b4b74c5629df5b420c2489b6da7056eb9fb7ec0574 |
| logs/scratch/design-review/distant-dreadnaught/budget-check.json | e9df88640124ca1f09eb8c1c7d19b51f4dab5e350b19aeb4bf958c77ed7e4550 |
| logs/scratch/design-review/distant-dreadnaught/station-cdh26-baseline.html | ed1b3b763fdac1d289cb2a59624b31aee6723adaba9ca4fc662eed8e5c9501ec |
| logs/scratch/design-review/distant-dreadnaught/capture-hashes.json | db7917bded7d77ba1d78cc18dcd1e247eff25961d18de6712c5284bb059e42a5 |
| logs/scratch/design-review/distant-dreadnaught/make-check.log | 75b3904a81d7158ea984199aa193b0a807aa9fa13257c5eabac129715fba2682 |
| logs/scratch/design-review/distant-dreadnaught/closeout.mjs | 0a940039232fa9235358322fa47c1f368cd01c5a7d572769212f194aa4492bce |
| logs/scratch/design-review/distant-dreadnaught/closeout-lint.log | 8554954e7f3077b75d6f8076b40e75d44fd26eaf29d283abe390b370bc137884 |
