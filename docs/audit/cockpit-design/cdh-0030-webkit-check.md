---
id: AUDIT-CDH-0030
type: report
created: 2026-10-25T23:43:28-07:00
author: codex
source: inferred
sources:
  - CDH-0030
  - Michou's review request and correction of the Safari observation in this session
  - docs/design/cockpit-v0/ at 0907f28
  - logs/scratch/design-review/cdh-0030/
tier: 2
status: final
handoff: CDH-0030
period: "2026-10-25"
reviewed_sha: 0907f283f66ae198abee14370bba1414c66e4503
---

## Findings

| ID | Class | File and location | Finding | Proposed fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | Main.dc.html:19–20 and the boards' decorative stacking layers | Rendered text falls below 4.5:1 after decoration composites over it. Main's clock label is 2.125478:1 in Safari and 2.119576:1 in Chromium. Safari's measured foreground/background at (40,32) CSS px are [60,74,84] / [7,14,20], after conversion to sRGB. Ordinary labels on the other operating boards show the same overlay mechanism. This predates the WebKit check and is shared by both engines. | Proposed CDH row: put words above vignette, frame glow and scanlines, retaining decoration behind them; repeat rendered-pixel checks. Score 3 × 0.2 = 0.6. |
| F2 | blocking | Keys.dc.html:30,37–38, reserved-key captions | The keyboard map's readable descriptions inherit #3a4650. The caption "approve · p2" is 1.935186:1 in Safari and 1.941916:1 in Chromium. These map descriptions explain reserved bindings; they are not disabled form controls. | Proposed CDH row: raise caption contrast while keeping the reserved keys dashed and inert. Score 2 × 0.2 = 0.4. |
| F3 | advisory | Safari's keyboard navigation environment | Ordinary Tab leaves focus on the document in this configuration. Native Option-Tab reaches all 7 room buttons at both widths, with 22 focused-room observations per width and 0 obscured or failed hit targets. | Document Safari's all-controls keyboard navigation option or use Option-Tab for this browser check. No application focus workaround is proposed. Score 1 × 0.2 = 0.2. |

F1 and F2 are grounded in the matched Safari/Chromium foreground and background captures and their exact text ranges: validated-pixels.json, review-summary.json, paint-board-Main-foreground.png / -background.png, paint-chrome-board-Main-foreground.png / -background.png, and the corresponding Keys pairs under logs/scratch/design-review/cdh-0030/. F3 is grounded in focus-probe.json and option-tab-1440.png / option-tab-400.png. Both proposed build rows are recorded in the README's scored list for Cowork to assign or fold into the next handoff. No repair is made in this review.

## Verdict

BLOCK: 2 blocking contrast findings, both reproduced in Safari and Chromium.

## Notes

The reviewed design is 0907f28, unchanged through the starting documentation commit 4c83064 and the later handoff update 68e1ae0. Safari Remote Automation was already enabled. Safari 26.6.2 and macOS 26.6.2 are recorded by WebDriver; Chromium Chrome/155.0.8059.85 supplies the comparison. The station is served from the existing pinned three@0.182.0 local package. No dependency is installed and no remote asset is fetched. The 11 boards use CDH-0027's static CSS projection, extended to the unchanged Keys and Wall boards. This checks WebKit paint and native HTML behavior, not the canvas editor's callbacks. Sources and hashes are in source-set.json and inputs.json.

The handoff gained Michou's inert-page observation while this review was running. He subsequently clarified that he had interacted with the automation windows while the tests opened and closed them and might have clicked a pending test page. The local station did not reproduce an inert interaction layer: all 7 digit keys follow the right rooms; a opens the pane, Esc closes it, c shows calm, p changes replay state and r returns to the requested start. Native WebDriver clicks open and close the pane through its actual buttons. Both widths produce 0 captured page, promise, console or shader errors. No failing source line can be named from this corrected observation. No artifact-host claim is made. Evidence: preflight.json, safari-manifest.json, interaction-timing.json and the station deck, following and pane captures.

The station renders at 1440 × 900 and 400 × 700, at device scale 2, with the deck lines, planets and SVG crew painted. All 9 visible SVG uses resolve to nonzero geometry at the paused sample. The 7 chip rectangles have 0 pair overlaps at both sizes. Option-Tab's 44 focused-room observations pass HUD/frame bounds, centre hit testing and the 2 px cyan outline. Calm hides the stage and retains 7 room records at both sizes. Evidence: safari-manifest.json, focus-probe.json and the associated screenshots.

Sixteen station pixel cases cover deck, pane, calm wall and calm pane at 2 sizes with full and reduced motion. The validated minimum is 4.554073:1 over 164,944 painted sample points. There are 88 unchanged background points outside the painted foreground swatches at clipped text edges; these are not counted as visible text. One first deck pair caught a departing crew tag between captures; the settled replacement has no changed text ranges or contrast failure. The initial phone pair also had a shifted capture, so it was not used as a product finding. Evidence: paint-manifest.json, paint-addendum-manifest.json, validated-pixels.json and the paint-station pairs.

Both sky-only reduced-motion pairs are pixel-identical across 10 seconds. The sky clock stays at 0 and every planet rotation is unchanged at both sizes; bloom is removed and calm hides the stage. The phone addendum triggers fresh native key input before each capture to ensure the final pixels are rendered. This is an explicit media fixture: native macOS Reduce Motion was off, the test copy substitutes the matchMedia result and activates the corresponding CSS branches, and no system preference was changed. Safari's live reaction to an OS preference toggle remains unverified. Evidence: safari-manifest.json, phone-reduced-final.json, station-1440-reduced-still-a.png / -b.png and phone-reduced-final-a.png / -b.png.

All 11 board projections render at their canvas.json sizes, including the 2560 × 1080 Wall. All 489 activity bars match their CSS percentage heights within 0.1 px; 48 chamfered panels exclude the sampled cut corner; :has() and :where() are supported and match page elements. All 6 details disclosures open through native Enter. All visible SVG uses resolve. The keyboard map and its reserved labels are rendered. Browser errors and warnings are 0. The local ui-monospace fallback paints on every board, confirmed by canvas glyph comparison; JetBrains Mono is unavailable to the fixture and is not fetched from Google Fonts. The remote-font path is therefore not certified. Evidence: safari-manifest.json, chrome-manifest.json, viewport-probe.json and the board captures; CDH-0027's earlier Chromium captures remain historical references.

Contrast uses paired rendered foreground swatches and masked backgrounds, so vignette and scanline effects on the words themselves are included. Safari's original Display P3 PNGs are retained and copies are converted through the system sRGB profile for sampling. Chromium uses its matching device-scale-2 captures. The first computed-colour-only analysis was diagnostic and is not the verdict's evidence. The swatch fixture reports 3 text-range changes across Main's causal link and a Tray note; those altered ranges are excluded from the findings. The cited clock and reserved-caption ranges remain unchanged in both engines. A disabled-button specimen on Components also uses low-contrast grey, but inactive controls are distinct from F2's readable keyboard-map descriptions and are not counted as a separate blocking finding.

Frame intervals below cover 30-second replays at ×2 with the same source and device scale 2. The desktop Safari run remains visible throughout. The phone window becomes occluded 7 times for about 6.039 seconds despite foreground activation; its inclusive timing is reported, not presented as an uninterrupted engine comparison. Earlier hidden-window timeouts and a later iframe attempt that lost its WebDriver window are retained without attributing a source defect. A clean uninterrupted phone timing remains unverified. No other browser benchmark runs concurrently. Evidence: timing-visible-1440.json, timing-visible-400.json, chrome-manifest.json, interaction-timing.json and timing-frame-400.log.

| Width px | Engine | Frames | Mean ms | Median ms | P95 ms | Maximum ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1440 | Safari | 1801 | 16.6652 | 17.000 | 18.000 | 20.000 |
| 1440 | Chromium | 1800 | 16.6660 | 16.700 | 16.800 | 16.800 |
| 400 | Safari | 1438 | 20.8637 | 17.000 | 18.000 | 1657.000 |
| 400 | Chromium | 1800 | 16.6659 | 16.700 | 16.700 | 16.800 |

The full offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 42.17 seconds. The personal memory index was absent and is not a design prerequisite. No memory, ledger, runtime, design-source or dependency file changed. Main advanced externally from ab0f748346a2ea48800525f03e67671d958e1654 to 6887717a6b529b7827540529b30c1fc1fb94798f; no merge or push was performed. CDH-0030 is closed as an audit with a BLOCK verdict. CDH-0031 remains proposed until Cowork reviews this report and disposes of the two contrast proposals. No native pass or canvas approval is claimed. Evidence: make-check.log, source-set.json and the closeout git comparison.

No taste changes are proposed: Michou's accepted direction remains the specification. The two repair scores and the Safari navigation score are above; the method choices are reversible evidence collection, not changes to the design.

Delivered document hashes exclude this report's own digest. The source set and all 288 PNG hashes, including diagnostic captures, are individually indexed in the evidence files.

| File | SHA-256 |
| --- | --- |
| docs/handoff/cockpit-design/2026-10-25-webkit-check.md | 80c2957f2a09fb320ff51f556b6d986e8212bbb514764e3528411667f67fde48 |
| docs/handoff/cockpit-design/README.md | 4ff3a04697d2df19bf48b8893bcafa384b3c3d7759bc99d4d35e01e78d1b4eea |
| logs/scratch/design-review/cdh-0030/preflight.py | 9e6e30f1bc717db2a86b92e0cc696fff76ed40c04d1852f9df331ed77a5f303a |
| logs/scratch/design-review/cdh-0030/preflight.json | 7d2d10ea8ec3cf36c82a28ed3b95625734dcdac7b5aadf5e6aa79bbe888973f7 |
| logs/scratch/design-review/cdh-0030/prepare.mjs | 04fe39872753dfb22d9b337b407159cf826fb9cd470c28195de236f9dd144b3e |
| logs/scratch/design-review/cdh-0030/inputs.json | 7fbd3c4e4909c09a851418162ec47421a06c5c47b4a810eb85ccfb3f28024673 |
| logs/scratch/design-review/cdh-0030/source-set.json | d96d32da425f6aa668ee665fb145ad0eeb9e5b905e56b570914f0c7b8da2e3d3 |
| logs/scratch/design-review/cdh-0030/webkit.py | c00f41863e315275ca18b97b228e93441e1b3fc4a956cdcac6bb40c31f76a161 |
| logs/scratch/design-review/cdh-0030/viewport-probe.json | 97ca2f495dfe63b5b2d92221d826c066ad33eac4aea6204317e380af0c474d4d |
| logs/scratch/design-review/cdh-0030/run.py | 72d350ea41d8d03c16cb8f16f283df92a90db6227d4d8e12345e72f21f7b434a |
| logs/scratch/design-review/cdh-0030/measure-original.js | 760403e1469a5f4440911ad19f8873c2a4fee3492d00a13cfd1e7c3dcdd8718b |
| logs/scratch/design-review/cdh-0030/measure.js | fc16ad5ee8673f843823db6864b2528c0378b9c6bbe3d0b6cdeb721e318a154f |
| logs/scratch/design-review/cdh-0030/safari-manifest.json | db16a928c511f67ff97b506e6a055ef4db46cb6c9ef1520b49cfe24118c2735e |
| logs/scratch/design-review/cdh-0030/focus-probe.py | 5fb5d37f216e78b39d4237962fcd4cd335612fb5f1b77ead64bd5620dcf8de39 |
| logs/scratch/design-review/cdh-0030/focus-probe.json | e0e55f381f97180ca15d686215753fab4dd94fc3380c55e257f4fbdd21e8e0e3 |
| logs/scratch/design-review/cdh-0030/interaction-timing.py | 131d421177a7cdd819a9e8a8917d723b6b3c0b2bcc89bc1c429e519cb706612f |
| logs/scratch/design-review/cdh-0030/interaction-timing.json | 60f04e54a0e8dfd89cd889c20d07f168e182198c5deacc6a78650546d7b3c737 |
| logs/scratch/design-review/cdh-0030/timing-visible.py | bda92cb2593444d5f79bc263c09e0f1c69565b4db5c2d37ffcbbfbcad9b54b33 |
| logs/scratch/design-review/cdh-0030/timing-visible-1440.json | 5bacb0479b9a4044a282d1ceb363ae62060b749150b13f703eb12952229aebff |
| logs/scratch/design-review/cdh-0030/timing-visible-400.json | 79a893823e3baa291f740fd5ead0da475e4a3b6a959d38fe4efd0a4cde6b30d7 |
| logs/scratch/design-review/cdh-0030/timing-frame.py | ecb3832b26f343a2a9bc9e26b788585e437acfe6d22ddb0e8d09c69f6072000f |
| logs/scratch/design-review/cdh-0030/timing-frame-400.log | e570e21c341039792d5255de0517c247b5e54002d2e2306c5f8c850167051877 |
| logs/scratch/design-review/cdh-0030/contrast.py | e6f1117a7ffcca05206a995d7116235f8faaafcf2771f800104de41f9ca2f8f4 |
| logs/scratch/design-review/cdh-0030/contrast-addendum.py | 12cfc5718f609d2176f8202930670e65573dd1221f03e5b62464de86cd6f6026 |
| logs/scratch/design-review/cdh-0030/paint-manifest.json | 9a752f7ccc53a8a3bf2cc7b6c1addfea58a55e4bde6122cdb778e8806505f4e8 |
| logs/scratch/design-review/cdh-0030/paint-addendum-manifest.json | 75065c249a8a1af3fb938c2d1232aabe83090672c218ba3203b589f2086aae0e |
| logs/scratch/design-review/cdh-0030/phone-reduced-final.json | c5fe0adf3ddc39f9091e05b99a1bf42a5914d115090c1724c9180787d956e78c |
| logs/scratch/design-review/cdh-0030/chrome.mjs | 351c8e214b18a174b5ae4fb4084979568b3041964017bf9ded690a34c04dc114 |
| logs/scratch/design-review/cdh-0030/chrome-manifest.json | 499b49c3a13ca0c8c4ba7b388fec941b117152d86060a9efa39722de3992f582 |
| logs/scratch/design-review/cdh-0030/png.mjs | 6c761d320eb98ca229b7dab08952979797fe18305ecbba1b182fb4fb63052763 |
| logs/scratch/design-review/cdh-0030/analyze-paint.mjs | 107e43307eb376e3e228c164dfc663822b3cbb11c75598c9d1a0a1183c4cf25f |
| logs/scratch/design-review/cdh-0030/validate-pixels.mjs | 5ad76dce2c117bf0e66e80c5eda99417655fdff082c791dcc11aa0c520323b1c |
| logs/scratch/design-review/cdh-0030/validated-pixels.json | 9fb3207814bf03dcbfa58eba04fbd0f2413598f6984205f1d4015a3b73f7629d |
| logs/scratch/design-review/cdh-0030/review-summary.json | 65b0b2228cc2d107ffc6b6e2de971ba2bce2fbd385f90201bac0d1a616c2ee6c |
| logs/scratch/design-review/cdh-0030/capture-hashes.json | 2a06066976df29234eb3e9c9b662114937507c9d562784a386f0b3ba382c2958 |
| logs/scratch/design-review/cdh-0030/make-check.log | f97a490b49e2ed6dee94dd37eb9d9b53c29f66c341d3468f5212e51cdaedb9c8 |
| logs/scratch/design-review/cdh-0030/closeout-lint.log | 701fd71e0da0f4920e74c8cda448479f051bd3341f67e18c834961d6bb22a44d |
