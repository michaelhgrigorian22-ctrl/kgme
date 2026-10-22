---
id: AUDIT-CDH-0020
type: report
created: 2026-10-21T19:51:36-07:00
handoff: CDH-0020
period: "2026-10-21"
source: inferred
sources:
  - CDH-0020
  - AUDIT-CDH-0019-CYCLE-1-REVIEW
  - docs/design/cockpit-v0/station/index.html
  - logs/scratch/design-review/cdh-0020/
author: codex
status: final
tier: 2
---

# CDH-0020: the HUD summary stays inside narrow viewports

CW26 is implemented by one declaration, .tr-sum{white-space:normal}, inside the station's existing max-width:720px query. The base nowrap rule still applies at 721 px and above. Source base: ceb0a4b484765e485999e4b83151f0961c6aa63b. The delivered station file has SHA-256 0a93f8ebdcd91d0dbe869b10fea0360ba855afae192eb962dc055387bfad7a07; its prior hash was 35f87569802e1b16e8610dce451c15c9ee84364e33eb072c1870d1952e7952bc.

The handoff's existing judgement is 2 × 0.2 = 0.4: wrap, preserving text and type size. No new judgement or approval-screen item is introduced. No board mirrors the station's .hud.top markup or #traysum element: the boards mount the separate template-driven Tray component, with its own .tr-col/.tr-bar structure. That component and all other design files are unchanged. The handoff body is unchanged; only adoption and closeout frontmatter are recorded.

## Verification

The real station was rebuilt with sh logs/scratch/vendor/make-local.sh and served on 127.0.0.1. The helper copies the cast and rewrites the two import-map URLs; it does not copy the sample ledger, so this run also staged the unchanged repository sample as logs/scratch/vendor/station/sample-events.jsonl. The original page, local before/after pages, helper, sample and three.js entry files are hashed below. Three.js is the existing local version 0.182.0; no dependency was fetched.

Headless Chrome/155.0.8059.85 ran on the Mac with ANGLE/SwiftShader, device scale 1, 700 px viewport height below 721 px and 900 px otherwise. The harness used the requested query at=19:52:00&speed=1, waited for the expected summary, paused through the page's existing control, and entered calm with the c key. All nine captures show 19:52:00 before and after capture. The first sandbox launch could not bind 127.0.0.1 (EPERM); the approved local-only run succeeded. Background network features were disabled and external connections pointed at an unreachable proxy; all 24 distinct observed HTTP requests were to the loopback origin. No page exceptions, console errors or failed HTTP responses were observed.

| Viewport width, px | Before summary right edge, px | After right edge, px | After lines | After white-space | Calm columns | Horizontal overflow, px |
| --- | --- | --- | --- | --- | --- | --- |
| 320 | 362.156 | 304.000 | 2 | normal | 1 | 0 |
| 360 | 362.156 | 344.000 | 2 | normal | 1 | 0 |
| 400 | 362.156 | 362.156 | 1 | normal | 1 | 0 |
| 720 | 362.156 | 362.156 | 1 | normal | 1 | 0 |
| 721 | 463.172 | 463.172 | 1 | nowrap | 1 | 0 |
| 1440 | 463.172 | 463.172 | 1 | nowrap | 3 | 0 |

The summary rectangle and every text-line rectangle are inside the viewport after the change, in both deck and calm. The before run reproduces CW26 at 320 and 360: right edge 362.156 px, respectively 42.156 and 2.156 px outside. The required 320 / 360 / 400 / 1440 checks reproduce 1 / 1 / 1 / 3 calm columns, seven rooms and 0 px horizontal overflow. The extra 720 and 721 checks verify the media boundary. Grid tracks match the before run exactly at every width.

Every HUD fact string matches before/after at all six widths in both modes, including the full summary "2 working (1 quiet) · 1 transient". Node verifies that removing the one added declaration reproduces the entire original station source byte for byte, so no markup, sample fact or JavaScript changed. All seven actor symbols and a nonzero WebGL canvas loaded in every page. This browser run exercises the page's own load, snapshot, pause and calm functions; no independent rendering substitute was used. All nine PNGs were opened for visual inspection. Other existing deck overlap or clipping visible in the phone captures is outside this summary correction; the zero-overflow claim above is for the calm wall and the summary's measured text bounds.

Repository gate: make check exits 0; **360 passed, 10 deselected in 30.41 s**. Ruff check and format pass; kgme lint reports 198 notes, 0 blocking, 94 advisory and 6 cosmetic. Native artifact publication and Cowork's native review remain pending; these measurements are Codex's standalone browser checks, not an independent native verdict or a performance profile.

## Evidence

Captures are gitignored under logs/scratch/design-review/cdh-0020/. Hashes are taken directly from the Mac's PNG files.

| Capture | Viewport, px | SHA-256 |
| --- | --- | --- |
| `before-deck-320.png` | 320 × 700 | `2113a11e390a6ff22fa0f9c330e3af21e283568f5ad01727a42e7f50147e3955` |
| `after-deck-320.png` | 320 × 700 | `6ccaea502b5a0edaaadbd7ed3af9a5650f824cf5ffbbdfe84e3badcb7c29fcda` |
| `after-calm-320.png` | 320 × 700 | `805854a359f5189acd013d3b548295969f9ab3eb9f846c8e5a4480bdf98387e8` |
| `after-deck-360.png` | 360 × 700 | `a9a9af99685076d6e201834206d9570b7fbb1af58749554e98642a1a3e254c6a` |
| `after-calm-360.png` | 360 × 700 | `0f8a72fa99fd1a3f712492ed068c5566c0ce776d5d8f8076173dbcafc0bb04f7` |
| `after-deck-400.png` | 400 × 700 | `d4d4f3e14f8fae41ac1af4114b157b3097e7b554d073930d5e9a3087eb15b43a` |
| `after-calm-400.png` | 400 × 700 | `6749c7db1871ed62de982390ae9f718a5e0662e08e24ca0d227455895987f6d2` |
| `after-deck-1440.png` | 1440 × 900 | `00058e2e587205b7c0a4a24a5185a1c2410d1b1b23fd436efb1fa3213e8d0d27` |
| `after-calm-1440.png` | 1440 × 900 | `1aedfe4af36662f245b32adb97518c1f1173ca22cb8c9e9f237084f04074269e` |

| Check artifact under logs/scratch/design-review/cdh-0020/ | SHA-256 |
| --- | --- |
| `verify.mjs` | `9ff7d283d804a27fd2f64918310ab00b0771cb1f6e9785a94aa189bc650a545a` |
| `inputs.json` | `2f62cdbb5657309de51a3d337b45176662a54c589b72078ef8c2d9625a52f4c1` |
| `manifest.json` | `d8fdf6fdfd681113419f6acfc7f3335ea34ccdf7f4c2949619280d4c53157e6f` |

| Input or served file | SHA-256 |
| --- | --- |
| `logs/scratch/vendor/make-local.sh` | `0c8680b9b8f2a4afff4b2c45bab1fad062fa2b06c0475a952771496d4cc59913` |
| `logs/scratch/vendor/package/package.json` | `e234d004910abe90f3451486d7ca9feaf7b9f4247b24d5a00233ff6e14bb67a0` |
| `logs/scratch/vendor/package/build/three.module.js` | `d835eab0b3bca3fdfd51e2ce7d06911f4a089b08db73cc3cd70fe5e3005a623f` |
| `logs/scratch/vendor/package/build/three.core.js` | `283be43b2229e15f46dac84cd19354ede5f06cac7ffb185e765cfcfb2c1eec90` |
| `logs/scratch/vendor/station-before-cdh-0020.html` | `590840bad28bc68146f1244132d32d5679314de55e637b6ccf72ea2ccf76f83c` |
| `logs/scratch/vendor/station-local.html` | `69b96d8707fa7146631647b84271d20e525c584fc843ab8eff5bacaf3560e93c` |
| `docs/design/cockpit-v0/station/sample-events.jsonl` | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |

The repository gate log, make-check.log under the evidence directory, has SHA-256 f1c9c435228ba8f20665ad18343c890e41c72ea54fc03760c2d0c37edf4c2ec5.

## Closeout

| Delivery file | SHA-256 |
| --- | --- |
| `docs/design/cockpit-v0/station/index.html` | `0a93f8ebdcd91d0dbe869b10fea0360ba855afae192eb962dc055387bfad7a07` |
| `docs/handoff/cockpit-design/2026-10-21-hud-summary-wrap.md` | `2661d3732425f8bee807e0f7ad7b3737abfabfa38ceebe96e587b4ba07d74e82` |
| `docs/handoff/cockpit-design/README.md` | `8ace4dff8cbf5c949baae851cf3da5f73f6688114b0d5b5d1a362c25aa3ea5a9` |

The report, station source, README status and handoff frontmatter are the four delivery files. Their final hashes are recorded in delivery-manifest.json under the evidence directory; the report cannot embed its own hash. No capture, vendor file or browser profile is committed. The three previously asked taste questions remain unanswered and their tally unchanged.

Main was recorded as 0d8b4113831779489dc4cd4072b543d13983af06 at this start. It advanced externally while verification ran; the final SHA is reported at stop. Step 1 remains completed by 67bfebb: this run does not merge, check out, commit or push main. After this build's one pathspec commit, Codex stops for Cowork's native pass, as CDH-0020 requires.
