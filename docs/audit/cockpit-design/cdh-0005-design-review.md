---
id: AUDIT-CDH-0005
type: report
created: 2026-10-12T18:00:21-07:00
handoff: CDH-0005
period: "2026-10-12"
source: inferred
sources:
  - CDH-0005
  - CDH-0001
  - docs/handoff/cockpit-design/README.md
  - docs/readers/cockpit-design.md
  - tools/review/design-prompt.md
  - HANDOFF-0036
  - ADR-016
  - ADR-017
  - memory/notes/cockpit-wishlist.md
  - AUDIT-CDH-0001
  - AUDIT-CDH-0002
  - AUDIT-CDH-0003
  - AUDIT-CDH-0004
  - AUDIT-CDH-0006
  - docs/design/cockpit-v0/ at a27d2f21e5c362b6a3e29dea2ddced6cd7f6c7dd
  - tests/test_design_sprites.py at a27d2f21e5c362b6a3e29dea2ddced6cd7f6c7dd
  - logs/scratch/design-review/cdh-0004/
  - logs/scratch/design-review/cdh-0006/
author: codex
status: final
tier: 2
reviewed_sha: a27d2f2
---

## Findings

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | advisory | `docs/audit/cockpit-design/cdh-0004-cowork-verification.md`, Evidence table; `docs/audit/cockpit-design/cdh-0006-implementation.md:44` and `:48`; the 14 images listed below. | All 11 CDH-0004 image hashes and all 3 CDH-0006 image hashes differ from the recorded SHA-256 values. The CDH-0004 experiment HTML and the 17-file CDH-0006 source digest do match. The supplied CDH-0006 frame pair has 1,459 differing RGB pixels, versus the report's 675, with the same bounding rectangle. Thus the current images cannot be identified as the recorded originals, and the difference is not confined to file metadata. Their visible content is consistent with the described states, but their source attribution and the claimed 600 ms interval remain unverified. This is an evidence limitation, classified advisory under the reader's evidence rule; it does not establish a defect in the reviewed design. | Cowork should restore the recorded originals or append a provenance correction identifying the current image hashes, any transformation, and the source commit. If that chain cannot be established, recapture the relevant native states at the reviewed commit and record their hashes and measurement method. Preserve the existing final reports. |
| F2 | cosmetic | `docs/design/cockpit-v0/chibi/README.md:3`, `:7`, `:13`, `:33`, `:34`, `:39`. | CW9's integration paragraph and fixture footer are corrected, but 2 opening references still assign native verification to CDH-0002, while the later paragraph records CDH-0004/CDH-0006. The explanation and 3 mode-table entries also retain `no outcome` as the class wording after CW3 changed both rendered implementations to an absence marker. The rendered board and fixture have the corrected values. | In a later authorized wording edit, align the 2 verification references and the 3 absent-class entries with the current integration paragraph and rendered labels. Keep the geometry and runtime unchanged. |

## Verdict

PASS

## Notes

This is the CDH-0005 review of board 10 at `a27d2f21e5c362b6a3e29dea2ddced6cd7f6c7dd`: 0 blocking findings, 1 advisory and 1 cosmetic. The evidence limitation in F1 prevents this report from certifying the supplied captures as the original native exports. The source checks and visible supplied images reveal no blocking board-10 design defect. This PASS does not record Michou's acceptance of HANDOFF-0036 or authorize HANDOFF-0037.

**Review scope and identity.** The worktree was on `design`, with a clean initial status and HEAD `ff8969c4496a4d61c9563c4dedd13dbfebb7e3a0`. All 22 files under `docs/design/cockpit-v0/` were read or parsed and compared byte-for-byte with the named review commit before using worktree paths. The 9 other artboards were read as context and remain byte-identical to `7bf773f`; board 7's keyboard map is unchanged. This is the scoped native-cast review, not a fresh acceptance audit of all 10 boards. The reader, review prompt, HANDOFF-0036 proposal, ADR-016, ADR-017, wishlist, CDH-0001 constraints and 5 delivered reports, AUDIT-CDH-0001/0002/0003/0004/0006, supplied the review context. No browser interaction or native editor session was performed in this review; all 14 named raster captures were opened as image input.

**Prior findings.** CW1 is resolved in source: board 10 has 7 inline symbols and local `use` references, with 0 iframe/object/embed elements or sibling cast loads; the editor's `./support.js` mechanism remains. CW2 is resolved: board 10 and the fixture use the component sheet's muted `#6f8290` and rule `#1e2a33`. CW3 is resolved in both rendered implementations: idle, working and asleep use the absence marker in the class field. CW7 is resolved in source: the template contains 51 double-brace holes and 0 remaining single-brace identifier holes. The supplied after-fix capture shows the 16 buttons, resolved fact text and builder drawing; F1 qualifies its provenance. The hash-matched CDH-0004 experiment differs from the reviewed board only by CW8's 1 CSS rule and 2 scroll wrappers, with an identical logic block. CW8 is applied as `overflow-x:auto` with 980 px and 1,100 px minimum grid widths at `Sprites.dc.html:44`, `:820` and `:836`; its native narrow-width result remains unverified. CW9's native-integration paragraph and fixture footer are applied, with the small wording remainder in F2. CW4 and CW5 remain closed as drawn.

**Facts, controls and motion.** At `Sprites.dc.html:813` through its context examples and `renderVals()` at `:922`, actor, mode, lifecycle, class and event are explicit text outside the decorative SVGs. The 49-cell matrix repeats actor text by row and state text by column, with a complete screen-reader label per cell. The 7 palette pairs state their shared idle state. Calm hides the artwork with `visibility:hidden` while retaining its layout boxes and facts; the supplied calm image visibly retains the selected arbiter's facts. The drawing defines 68 decorative instances: 1 selected detail, 49 matrix specimens, 14 palette specimens, 2 run portraits and 2 context figures. Only the selected detail can receive the animation class. Its eligibility requires visibility, at least 50% intersection, no calm and no reduced-motion request; the independent media rule suppresses animation. The 7 modes reuse the canonical parts and shared keyframes, with at most 2 endpoint poses per animated part. These are source findings, not new native performance measurements.

The 16 fixture controls are named native buttons grouped by actor, mode and palette, with `aria-pressed`, an underline for selection and a 2 px focus outline. The scroll region has a label and keyboard focus. The source declares 24 px cropped run portraits, 72 px detail figures and exactly 22 px event rows. The preserved Phase 2 example is a labelled, dashed 48 px guard drawing; both `y` and `n` remain dashed, reserved and unbound. Board 10 and the fixture add 0 application keyboard handlers, so they introduce no new collision with board 7. Sticker remains limited to detail specimens; the matrix and run portraits use phosphor.

**Contrast.** I recalculated the 6 text-token ratios from the source sRGB values against both board-10 backgrounds. The lowest is muted text on the panel at 4.5926:1, above the 4.5:1 requirement for the board's small text. Decorative material fills are not text or the sole carrier of any reviewed fact. The selected-state underline and focus outline supply shape changes as well as colour.

| Text token | On ground `#0a0c10` | On panel `#11151c` |
| --- | ---: | ---: |
| `#cfe6ef` | 15.1151:1 | 14.1290:1 |
| `#6f8290` | 4.9131:1 | 4.5926:1 |
| `#39d0ff` | 10.8486:1 | 10.1408:1 |
| `#ff3d7f` | 5.8025:1 | 5.4239:1 |
| `#ffb02e` | 10.7193:1 | 10.0200:1 |
| `#4de38a` | 11.8084:1 | 11.0380:1 |

**Mechanical checks and supplied performance evidence.** `uv run --offline --no-sync pytest -q -p no:cacheprovider tests/test_design_sprites.py` passed all 14 checks in 0.01 s. The 7 body comparisons at `tests/test_design_sprites.py:24` preserve text, attributes, geometry and inline styles, normalizing only outer/inter-tag whitespace. The 7 material comparisons at `:39` separately compare canonical root sticker values. All 7 canonical SVGs parse, contain ordinary vector elements, and retain 6 semantic material roles, shaded variants and actor-specific pivots. The following byte and element counts were recalculated in this review, including each SVG root and metadata.

| Canonical asset | Raw bytes | SVG elements |
| --- | ---: | ---: |
| `arbiter.svg` | 8,166 | 76 |
| `builder.svg` | 8,775 | 98 |
| `guard.svg` | 8,053 | 88 |
| `michou.svg` | 8,730 | 95 |
| `reviewer.svg` | 7,988 | 86 |
| `scribe.svg` | 6,717 | 71 |
| `stranger.svg` | 6,353 | 68 |
| All 7 SVGs | 54,782 | 582 |
| `characters.css` + `characters.js` | 21,513 | Not applicable. |
| Target comparison total | 76,295 | Not applicable. |

The 76,295-byte total is 74.51 KiB, or 14.55% of the provisional 512 KiB target; the native board itself is 81,036 bytes. Neither number establishes runtime cost. AUDIT-CDH-0001 supplies the 2 approximately 30-second target-Mac captures: headless Chrome 155.0.8059.39, Apple M4 Pro, 12 logical CPUs, 24 GiB RAM, 1,440 × 1,100 CSS px, DPR 2, 50 static run portraits and 1 working builder detail. It reports motion/calm RAF means of 33.33/33.33 ms, p95 of 33.40/33.40 ms, 0/0 long tasks, input-to-next-frame p95 of 27.60/29.20 ms and scroll-to-next-frame p95 of 0.20/0.10 ms, with 56 input and 56 scroll samples in each capture. It reports 1/1 active working animation at motion start/end, 0/0 under calm, and a maximum of 3 effects on the single idle detail. These are prior Codex measurements of the standalone fixture, not measurements repeated here or native-editor certification. AUDIT-CDH-0003's 101 static raster comparisons and 49 selection checks are also supplied Codex observations of a browser projection. That report explicitly found that `getAnimations()` returned 0 despite moving pixels in SVG use trees, so this review makes no native active-effect count claim from that API.

**Image observations and provenance.** The 11 CDH-0004 images show the failed single-brace delivery, the brace experiment's matrix, palette/context views at 2 widths, selected builder and arbiter states, the 2 arbiter palette crops, asleep, the calm tweak and calm with retained facts. The 3 CDH-0006 images show the resolved default state and 2 working-builder crops. I decoded the 2 current 122 × 122 RGB PNGs without modifying them: 1,459 pixels differ inside `(27,58)` to `(61,115)`, with the latter corner exclusive, and 0 pixels differ outside it. That supports a localized image difference in the prop/arm area; capture timing and native origin remain Cowork-attributed, unverified because of F1. No cause for the 14 hash mismatches was established.

The current SHA-256 values below identify exactly the images inspected. Each differs from its corresponding value in AUDIT-CDH-0004 or AUDIT-CDH-0006. Filenames are relative to `logs/scratch/design-review/`.

| Capture | Current SHA-256 |
| --- | --- |
| `cdh-0004/native-as-delivered-board-10-unresolved-holes.jpg` | `bd2e9fc737048be08bf11400bfdd94d705b4534aca4d46f5d370c19bf35d64c8` |
| `cdh-0004/native-experiment-matrix-phosphor.jpg` | `0c2f7bde3fadf5dadaf9bf9cbedb7ab075b2a04d3912ca6e52d1ca467d9a2b8b` |
| `cdh-0004/native-experiment-pairs-and-contexts-fill-width.jpg` | `f9a8fc8fcf939a597b5d3f99fa62193b083aa97f5f86d7d7f228aa4544d62d69` |
| `cdh-0004/native-experiment-pairs-and-contexts-800px-collisions.jpg` | `f242140d680b7b9565cf2ab6669d7cb5231b1d67f5ed29134276f33a0341038a` |
| `cdh-0004/native-experiment-detail-controls-builder-sticker.jpg` | `494d47b638106bc8379c02cae1b3a02785e72e431d25aca1aed55b16108ccebd` |
| `cdh-0004/native-experiment-detail-arbiter-blocked-sticker.jpg` | `d853f2ff9de8fbb8170783968daa57515e412bf1f16cbd2ea3a3294464758b06` |
| `cdh-0004/native-experiment-zoom-arbiter-blocked-sticker-72px.png` | `ad79ee9c62e5e6773e81a8f87db1ee129444efbdd1388eac7f45784ca2b5f5a4` |
| `cdh-0004/native-experiment-zoom-arbiter-blocked-phosphor-72px.png` | `03ead5d2c683d5c4c812c999c4fa4716657c27540cdcf30876a984e42e75bdb0` |
| `cdh-0004/native-experiment-detail-arbiter-asleep-phosphor.png` | `cc1497938dd50b2b0027e47cff616084747d2e97e88a0bd69745051802d8a95a` |
| `cdh-0004/native-experiment-tweaks-panel-calm.jpg` | `24544e26d01ef034d041426f3eda63507663372f8111f26cd012fa2899e4ec0c` |
| `cdh-0004/native-experiment-calm-on-detail-hidden-facts-retained.jpg` | `ce034c1ed1a34270ac8de63f12b02117c80cd7b19414472e9170274be4570d5b` |
| `cdh-0006/native-board-10-after-fix-default-state.jpg` | `ef63b486cf819c790666dd3396ba2dc31e48bce605dcb4b245376fe13e61cbd2` |
| `cdh-0006/native-builder-working-72px-frame-a.png` | `2e9d9f93d30ce7878cb3cb6654eb8865153e671d48fcbbf5546796e40a58b8f5` |
| `cdh-0006/native-builder-working-72px-frame-b.png` | `7572be91d3ea89b3b714b2f28668f4b4fd89c5105ca1aa84470397556fc29fdb` |

The CDH-0004 experiment HTML does match its recorded SHA-256, `a5e612fbea9e8f652f361517f659d7cd3993e38c8b7029d9d0d0b58b7792538a`. The CDH-0006 17-path source-set digest also reproduces exactly: `eb8002d68811360f347c683fd02ae0e11906b023b33fed5b251a2d5ec592f43b`. Neither match authenticates the 14 raster files by association. Native reduced motion, the post-CW8 narrow-width matrix/pairs, all-mode native motion, native hidden/offscreen resumption, matrix-wide calm, and native performance remain unverified here. The approved reference artwork, older standalone screenshots and CDH-0003 browser projections were distinguished by their reports and were not treated as fresh native evidence.

**Reviewed source hashes.** These 22 SHA-256 values identify the complete design tree read at the reviewed commit. Paths are relative to `docs/design/cockpit-v0/`. Its aggregate digest is `4c9467b54045c95598fde0419b839219ed436b95822089e35b6c0a11aff8258e`, computed over sorted records of repository-relative path, NUL, file SHA-256 and LF. The drift-test SHA-256 is `2088cb369492922729773f36b1b45c72f07b20896f0d77a5f2c924ee6e8c3062`.

| Source file | SHA-256 |
| --- | --- |
| `canvas.json` | `650393ca46d84101dd9a4c3655aa727202cb9315176aeb7d69cea40b88c0de80` |
| `Main.dc.html` | `997ffaeb4dfbe7f66732505ed123a3c73e91cc80c0b018b86b5dcb54ce57dab6` |
| `Components.dc.html` | `fe89cbb9f225bc81f65ca664a600b3d816203d636889463073e845cb6adead4e` |
| `Empty.dc.html` | `5de581859ed272ac290af6041253c6496583b357e576e849cabc06ec5400fddd` |
| `Blocking.dc.html` | `3717e1fb378dc3f5a33ffb8d4ae902fc8cfdcbd0891d7f82233804b46bbd2965` |
| `Pending.dc.html` | `80c17188b620421463040cf3753525cfc7d77a48b1646ec6e814fadc5476fa3f` |
| `Disconnected.dc.html` | `cfab94cc2c997ea2d908cdd96e225733a4e028cc036c32a88104a1f373d67fdd` |
| `Keys.dc.html` | `ee5dc291d5022607667d6887bedad934b44816e164b7946e261a403e6b2c364e` |
| `Phase2.dc.html` | `5bd59761b2dbc37ad9bf1620e9cb5dec1300f6209c4f9791168f228039161539` |
| `Wall.dc.html` | `edc288fdf5d7ff354ebc309029d510dc301f6e23242c79fb8d229b9aeee86dfb` |
| `Sprites.dc.html` | `e54f58bfd3dd315d0e82830587008be202b761f6c7593b5e7d344f433683ca7a` |
| `chibi/README.md` | `58215297735ac7827b4f9fd6250adba22b314204be02d2a08c3190f60f06792d` |
| `chibi/arbiter.svg` | `8d7bb211574d347a5038dfb1b38aa7facc414369f24d7e640102059b16bdcdc1` |
| `chibi/builder.svg` | `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e` |
| `chibi/characters.css` | `7fcb692d48d26201744cf6795c899cdbaa9a93750bbb9d952407921bcd19a020` |
| `chibi/characters.js` | `900872eec1de4f457c120eeeedb068d4a2346ceeb9e803acfb20ac3dd0b4e26e` |
| `chibi/guard.svg` | `da6639d6cabae91e7fa622754a6fc27c9dc7c823e3657d34340a76729f6b31fa` |
| `chibi/michou.svg` | `46831a1e9d6ebf8991beb59b0281779ee6bc7869798fd2b168822b0f2bdfa9c7` |
| `chibi/preview.html` | `2681c521c3de5091b82f4cb1c829071d4f3be8e60c54fb0a6e1c1d19561aff23` |
| `chibi/reviewer.svg` | `f444d74e398ab00a5a52e9160c50bf433113ba9115e0fe65efbb51b13e9a062b` |
| `chibi/scribe.svg` | `cba7d68489569c0dc783086829752807af719b3473dd9d0286a00807d39fc026` |
| `chibi/stranger.svg` | `7fed1b5845d5934e37580d7070c35adfbabb9e84cc9b87a0e536ef602ab81516` |

**Taste, advisory only.** My first 3 preferences would be to give the actor/mode/palette control groups slightly more vertical separation so the 16 buttons scan more easily; shorten the repeated explanatory copy above the 49-cell matrix while retaining every fact field; and make the Voice/Rules reference area collapsible so the 72 px selected detail and specimens dominate the inspection view. These are optional presentation preferences, not acceptance conditions, and do not reopen CW4 or CW5.

The only delivery writes are this 1 report, CDH-0005's adoption/completion frontmatter and its single queue-row status. No design, ADR, config, accepted report, evidence image or `main` file was edited; no commit or push was performed. Cowork can commit the 3 delivery files on `design`. Michou's own look at the review copy remains part of HANDOFF-0036's acceptance process.
