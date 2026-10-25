---
id: AUDIT-CDH-0029
type: report
created: 2026-10-25T15:44:01-07:00
handoff: CDH-0029
period: "2026-10-25"
source: inferred
sources:
  - CDH-0029
  - CDH-0028
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/cdh-0029/
author: codex
status: final
tier: 2
---

# CDH-0029 implementation

Row 17 is built under Michou's instruction to turn up KGME Station v13, then stop for Cowork and his native look. The session started at df9e777; the unrelated shell ruling / proposed CDH-0030 arrived in 0aadc74 before source edits, and is preserved. No WebKit work was taken. Main moved from the starting 3006a9b00d569c1f4a4d07110cd8a5f6931c7603 to 19b60d15f661d6a2b50011c6c8f267189c3f6d50; this builder did not modify or merge main and did not push. Cowork's native pass of CDH-0027 and CDH-0028 folds into this row's pass. None is claimed here.

## Delivery

The desktop sky has 8 bodies: the existing large ringed giant, an amber gas giant, a cratered green moon, an ice world, a cratered rock, a small second ringed planet and a close pair of smaller moons. Radii range from 0.22 to 3.15 scene units and local depths from -1 to -33 relative to the sky group. Each has its own slow signed rotation rate, 0.0024–0.006 radians per second in magnitude, approximately 17–44 minutes per revolution. The second ring reuses the first ring's geometry and material. The existing wash remains restrained; it is placed behind the populated sky.

| Width | Visible planets | Far star layer | Near star layer |
| --- | ---: | --- | --- |
| 1440 px | 8 | 5,200 points, 1 px | 700 points, mostly 1.5 px, a few 2.2 px |
| 800 px | 8 | 5,200 points, 1 px | 700 points, mostly 1.5 px, a few 2.2 px |
| 400 px | 3: ringed giant, moon, smaller far giant | 5,200 points, 1 px | Hidden |

Each star layer uses exactly 1 Points object and 1 shader material, with deterministic clustered positions plus a sparse background. The far layer is mostly faint and the near layer has a small cyan/magenta/amber subset. The 47 far and 64 near twinkling points comprise 111 of 5,900 points, 1.88%. Their sine opacity ramps have periods of 8–16 seconds and remain between 70% and 100% of each point's base opacity; no flash or on/off blink. Both layers share the sky's real-time uniform, which freezes under reduced motion and calm.

The star layers are at local depths -70 / -40, with pan coefficients 0.12 / 0.45. The station's orthographic camera requires explicit compensation: distance alone would not create parallax. A 120 px input drag produces 14.394672 px far-star movement and 53.980021 px near-star movement, a 3.75× ratio. After camera easing settles, the stars-only image changes at 38 pixels over 2.5 seconds, while 1115 pixels exceed intensity 30 in at least 1 RGB channel. This checks visible twinkle rather than only the presence of a time uniform.

Only the ambient component, the replaced 900-point star field, and the ambient tick's camera argument changed. The source comparison removes precisely those regions and finds the rest byte-identical to 040a5ad: all CSS and markup, deck, crew, room lights, facts, chip dimensions, focus rules, keys, frame colours and pane remain unchanged. Opaque text surfaces keep the sky out of text backgrounds and above-sky paint order remains intact. The default composition places the new bodies in the margins around the deck; projected sky is occluded by the unchanged opaque chip, bubble, HUD and pane surfaces. No sky parameter reads a ledger, run, room, quota or hull value. No import, dependency, fetch, image file or external asset was added.

## Verification

The 24 surface/motion cases cover 1440 × 900, 800 × 600 and 400 × 700; deck, followed-room pane, calm wall and calm system pane; reduced motion on and off. There are 1,780 text boxes and 419,968 sampled visible background pixels, with minimum contrast 4.592580:1. During background sampling, the test copy pauses periodic rendering and masks text fill, preserving backgrounds and borders. Each box records its computed text colour, actual worst background pixel and ratio. Desktop deck and pane, phone deck and the isolated star capture were inspected. The shader points stay below the deck lines and text in visual prominence.

At each of the 3 widths, all sky parameters and decoded sky pixels are identical over 10 seconds under reduced motion, with non-sky layers masked only in the fixture. The planets remain visible. Full motion advances the ambient clock. All 6 calm cases hide the stage and retain the sky clock and transforms without rendering the sky. A separate run against the uninstrumented station compares all 7 chip rectangles, including offscreen rectangles: 0 pair overlaps at each width. Each viewport supplies 21 focused-room observations covering all 7 rooms; every target stays inside its HUD/frame bounds and passes centre hit testing.

The source check passes, as do the visual, parallax/twinkle and focus checks. The offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 33.27 seconds. No dependency was installed. The browser runs use local three@0.182.0, block external traffic, and report no page, console, HTTP or external-request errors. Test inspectors and image masks exist only in ignored local fixture copies. Native publication, native interactions and Michou's look remain pending.

## Frame intervals

Six sequential 30-second replays at ×2 run through Chromium's ANGLE Metal renderer on the Apple M4 Pro. CDH-0026 is commit 8f49559 with only dependency URLs redirected to the existing local package. The without-sky comparison uses the final source's sky=0 affordance. No screenshots or parallel browser tests run during timing. The manifest retains every animation-frame delta and the actual replay-clock endpoints.

| Viewport | Variant | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 × 900 | cdh26 | 1800 | 16.665944 | 16.700 | 16.700 | 16.800 |
| 1440 × 900 | without | 1800 | 16.665944 | 16.700 | 16.800 | 16.800 |
| 1440 × 900 | with | 1800 | 16.665944 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | cdh26 | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |
| 400 × 700 | without | 1800 | 16.665944 | 16.700 | 16.800 | 16.800 |
| 400 × 700 | with | 1800 | 16.666000 | 16.700 | 16.700 | 16.800 |

1440 px changes versus CDH-0026: mean 0.000000 ms, P95 0.000000 ms. 400 px changes versus CDH-0026: mean 0.000000 ms, P95 0.000000 ms. Both measures stay within the 2 ms budget. These observations do not imply a universal frame rate; the native host remains Cowork's check.

## Scores and closeout

Eight planets rather than six, with the existing giant retained: 3 × 0.3 = 0.9. Clustered stars, two explicit pan coefficients and restrained twinkle: 3 × 0.3 = 0.9. Both are on the README approval screen for Michou's look. Procedural surface types: 2 × 0.2 = 0.4. Deterministic point placement: 1 × 0.1 = 0.1. The 400 px reduction follows the handoff: 1 × 0.2 = 0.2. No new brief is required. The 40-line lessons file records orthographic parallax and settling camera easing before a twinkle measurement. The absent personal MEMORY.md index is not a design prerequisite; no personal memory was written.

CDH-0029 is closed as a builder delivery. Stop here for Cowork's combined native pass and Michou's look. CDH-0030 and canvas approval are not performed by this report.

## Delivered text SHA-256

The report excludes its own digest; the shared README hash describes this delivery.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/station/index.html | 9121f26ca4e397aade67e6154ad8dceb811cf5c5da7058b93b369069a613e517 |
| docs/handoff/cockpit-design/2026-10-25-more-planets-and-stars.md | f94371b53806885c76a84ae9f0f19897e6c7ed1936e770488c86f82797cef439 |
| docs/handoff/cockpit-design/README.md | 8de29c2403989c893c8f20378bcd508e811c5923c75199ced7de2e49e96e00fa |
| docs/readers/cockpit-design-lessons.md | 2ccf69537dbdd8667a6283ca84e633460394f67729b82624ccabdf78fd877ee0 |

## Evidence SHA-256

The 46 final PNGs have individual SHA-256 entries in capture-hashes.json, including background samples, reduced-motion sky captures and the isolated star field.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/cdh-0029/prepare.mjs | f0e4c17b0149ac2adc47cbd7514470398a42895d4bbbd5adc45a2d27f28279ad |
| logs/scratch/design-review/cdh-0029/source-checks.json | dd8a5c12470ffe5a3931d494275d3a0f653ff47fbf41191cb4f726e2bd18cc93 |
| logs/scratch/design-review/cdh-0029/verify.mjs | 5041adf4cbd11ec1bb3d8152c04c72dfdde36ea0f6f7a57d51dc324e47622dd0 |
| logs/scratch/design-review/cdh-0029/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/cdh-0029/visual-manifest.json | 429386e4fa70427bac73e760d9084bab5b03eba40fb723afb408c4c93f1e3b9c |
| logs/scratch/design-review/cdh-0029/focus.mjs | 1adaf00c79e9657e03ac1db21f80ba8488ae66bcc9a78640edf07b140038bc58 |
| logs/scratch/design-review/cdh-0029/focus-manifest.json | 834a599b12a7d9ceb810a0708edd82b5ee02297cafea12f011e441857c6de9cf |
| logs/scratch/design-review/cdh-0029/depth.mjs | b9b37c79df9185d6d3442c1c70338a8f9b0a17cfa7d75d1365352a285852e0a9 |
| logs/scratch/design-review/cdh-0029/depth-manifest.json | 0a27fb1354aeed9aee63090983a560fd44862afbb35af1c4a714b3542a00e260 |
| logs/scratch/design-review/cdh-0029/performance-manifest.json | 00bc0bc580058e9479ef9a005f09350112bb58b3434d3a50d28fc36ab4bf3d50 |
| logs/scratch/design-review/cdh-0029/station-cdh26-baseline.html | ed1b3b763fdac1d289cb2a59624b31aee6723adaba9ca4fc662eed8e5c9501ec |
| logs/scratch/design-review/cdh-0029/capture-hashes.json | 49ed093fc33cac8780a22c0467e5110059ad0d8495b4e25f6ebab4f84bc6f307 |
| logs/scratch/design-review/cdh-0029/make-check.log | 830adeffa27ddec332c757eeacda58f30997ea88ed1beb684006230cc8a59ae6 |
| logs/scratch/design-review/cdh-0029/closeout-lint.log | 5711526939f91761d1b64c073248dfcd6fe5f4c012afe266af8cb07d2c4667b1 |
