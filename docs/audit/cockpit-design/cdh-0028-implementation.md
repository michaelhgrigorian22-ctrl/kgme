---
id: AUDIT-CDH-0028
type: report
created: 2026-10-25T15:14:10-07:00
handoff: CDH-0028
period: "2026-10-25"
source: inferred
sources:
  - CDH-0028
  - CDH-0027
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/cdh-0028/
author: codex
status: final
tier: 2
---

# CDH-0028 implementation

Built from CDH-0027's separate commit 537b1e2. Michou explicitly authorized row 16 in this same run after row 15, overriding the intervening Cowork gate. No native pass of CDH-0027 or CDH-0028 is claimed. Main moved from the run's starting 0715e7e2deb9f242832d26a75e03ad02480533f9 through ed7faebeec886dd7bb7724e1dbda03c349f4bf67 to 3006a9b00d569c1f4a4d07110cd8a5f6931c7603; the builder did not modify or merge main and did not push.

## Delivery

The station now sits between a large cyan/magenta banded planet with a tilted ring, a smaller amber/cyan planet and a green/cyan moon, with a restrained procedural nebula behind the existing stars. The 3 spheres use 32 × 20 segments; the ring has 96 segments. At 400 px the far planet is omitted. No image, dependency or network source was added; the page retains pinned three@0.182.0.

The sky is one isolated component. Its inputs are viewport/camera geometry and its own accumulated real time. Planet rotation rates are 0.006, -0.004 and 0.003 radians per second, corresponding to approximately 17.45, 26.18 and 34.91 minutes per turn. The wash uses 75 / 95 / 110-second phase divisors. No run, event, room, quota, hull or replay value enters a sky parameter. Calm hides the stage and freezes the ambient clock; reduced motion freezes the clock while leaving the planets visible. The shader's outer bands are darker and every text surface is opaque.

The deck geometry, room lighting, camera setup, chip creation and all HUD/pane/wall/footer markup are byte-identical to CDH-0027. Grey disconnect styling and the hull halt logic are unchanged. Legibility required paint-layer adjustments: labels paint above decorative frame glow and below the HUD/pane; chips paint above crew artwork; crew tags use the primary text colour on ground. Projected labels clip 12 px inside the frame, and keyboard-focused chips use a 14 px horizontal inset so their focus outline stays inside that clip. Chip dimensions and anchors are unchanged. All 7 keyboard targets still pass at each required viewport.

The first pixel checks found actual text overpainting by crew artwork and by the frame at the viewport edge. Those were corrected rather than treating the sky's nominal CSS background as sufficient evidence. The fixture itself was also corrected: live word updates initially repainted text into its background capture, so the test copy pauses its render loop while collecting pixels and masks text fill without changing borders. Reduced-motion images mask other scene layers because expiring speech bubbles are not sky motion. The production page includes neither test mask nor inspector. Its only new read-only test affordance is sky=0, following the existing at/speed convention.

## Verification

The 24 cases cover 1440 × 900, 800 × 600 and 400 × 700; deck, followed-room pane, calm and calm system pane; reduced motion on and off. The background fixture samples visible pixels inside each text rectangle, after clipping and occlusion, with the actual background, borders and shaders intact. It covers 1,780 text boxes and 419,968 sampled pixels. Minimum contrast is 4.592580:1 overall and 4.913133:1 on the deck. The per-box colour, worst pixel and ratio are in the visual manifest; glyph-free background PNGs and normal captures are retained. The WebGL canvas paints below label, HUD, bubble and pane text; no sky mesh can paint over them.

At all 3 sizes, reduced motion leaves planet transforms and the sky's clock unchanged for 10 seconds. With non-sky layers masked only in the test copy, the decoded sky pixels are identical before and after. Full motion advances the independent clock. Calm hides the stage, performs no sky rendering and retains the ambient clock value in all 6 motion/width cases. It keeps the existing text wall. The source check confirms no sky parameter reads ledger state, unchanged imports/fetches, unchanged deck construction and unchanged state rendering. No dependency was installed.

A separate check uses the actual uninstrumented station: all 7 room-chip rectangles have 0 overlaps at each of the 3 viewports. Each viewport has 21 focused-room observations covering all 7 rooms; every focused target clears the HUD and frame clip and passes centre hit testing. The desktop deck, followed-room pane and phone deck captures were inspected. Native artifact paint, clicks and publication remain Cowork's pass.

## Frame intervals

All 6 runs use the Apple M4 Pro through Chromium's ANGLE Metal renderer, each for 30 seconds at replay ×2, starting around 19:41:20. CDH-0026 is loaded directly from commit 8f49559, with only its dependency URLs changed to the existing local package. The without-sky case is the new source with sky=0. Runs execute sequentially without screenshots or other browser verification during timing. Frame intervals are animation-frame deltas, not inferred shader times.

| Viewport | Variant | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | cdh26 | 1794 | 16.721683 | 16.700 | 16.700 | 116.600 |
| 1440 × 900 | without | 1800 | 16.665944 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | with | 1800 | 16.666056 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | cdh26 | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | without | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | with | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |

1440 px: the mean changes by -0.055628 ms versus CDH-0026 and 0.000111 ms versus sky disabled. 400 px: the mean changes by 0.000000 ms versus CDH-0026 and 0.000000 ms versus sky disabled. Both mean and P95 stay within the 2 ms budget. These are observed local replay measurements; the tiny differences are timing noise, not a claim of faster rendering. Full frame samples and actual replay-clock endpoints are in the performance manifest.

The offline make check passes ruff, format, lint with 0 blocking findings, and 360 tests with 10 deselected in 32.02 s. Visual and performance runs record 0 page, console, HTTP or external-request errors. The final document lint is recorded separately.

## Scores and handoff

The ambient direction is 3 × 0.4 = 1.2, on the README approval screen, within Michou's requested space treatment. The 3 low-poly spheres and single wash use the existing dependency; shader/material choice is 2 × 0.2 = 0.4. Opaque surfaces and label paint order are 2 × 0.2 = 0.4; the 12 px clip and 14 px focus inset are 2 × 0.2 = 0.4; narrow-screen simplification is 1 × 0.2 = 0.2. No decision requires a new brief. The lessons file records background-pixel masking and frame-glow ordering within its 40-line limit. No personal memory was written.

Both authorized rows are closed as builder deliveries with separate reports and commits. Stop here for Cowork's native pass, including the 1440 view and the opened pane, and Michou's judgement of the look. No canvas approval or publication is claimed.

## Delivered text SHA-256

The report excludes its own digest; the shared README digest describes this delivery.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | 0ddcbd9abe93dfbf7ad04c6433c634c4d5af2057b136332e0a1aedec3266eda9 |
| docs/handoff/cockpit-design/2026-10-25-station-in-space.md | 8d1ca67922c11aab15371765d486caf6cc343b3879bb75806a1313a9d71f9263 |
| docs/handoff/cockpit-design/README.md | 15995d41452e730f5250a10ab82b3e7eb9cd1f81d0cd6cebf0475e389431ca9d |
| docs/readers/cockpit-design-lessons.md | a1b3a568881663d1d0581b4cd24cdd579b3633533194100cbbb0ae5c2e75bb5d |

## Evidence SHA-256

All 45 PNGs have individual SHA-256 entries in capture-hashes.json, including the background samples and isolated reduced-motion sky captures.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/cdh-0028/prepare.mjs | 334d594b6b5b6bfe022c920102f0bbb7843e2fdb2a59b3740213c8100ab987f3 |
| logs/scratch/design-review/cdh-0028/source-checks.json | f2aa46b8cda84b38d1da1890b1b4e191eb177c493b0be075224c5d3631e8d0a5 |
| logs/scratch/design-review/cdh-0028/verify.mjs | 0dcea153b00655c6bce0694d394a840f4a6870433d9359548931e9599ddea50e |
| logs/scratch/design-review/cdh-0028/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/cdh-0028/visual-manifest.json | 999b2ca98ab8a29c3522f0c748982f07ffeb3d0547cdb666a49f1c2c779a1842 |
| logs/scratch/design-review/cdh-0028/focus.mjs | ea3fdcb7a1998a4d99e7c8558f5a9eb906e315d51d2e4e14243a97412a16aae6 |
| logs/scratch/design-review/cdh-0028/focus-manifest.json | a48785fd894d6fe79c095bfb05f516cc3c1446d625e82cf2d534f9563a5f7319 |
| logs/scratch/design-review/cdh-0028/performance-manifest.json | 411f1c77baca32489eab44cce6757a62d6030bbf6674a4b31c8ddc57819ee834 |
| logs/scratch/design-review/cdh-0028/station-cdh26-baseline.html | ed1b3b763fdac1d289cb2a59624b31aee6723adaba9ca4fc662eed8e5c9501ec |
| logs/scratch/design-review/cdh-0028/capture-hashes.json | b7e4424b3e5af10b0f6f9012ae1e2d386b3323f3f12c7afa82de807f4ed9827b |
| logs/scratch/design-review/cdh-0028/make-check.log | ca27aff95c9effe8111cb1fc9d3d575f51e0f025966c1446a633f52812d4cfff |
| logs/scratch/design-review/cdh-0028/closeout-lint.log | 6dde595a83a54d1e23d4d00aa56f85686ba0b6f01fa7b58598906131bca2c4a4 |
