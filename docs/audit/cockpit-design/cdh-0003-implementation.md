---
id: AUDIT-CDH-0003
type: report
handoff: CDH-0003
period: "2026-10-11"
created: 2026-10-11T15:51:09-07:00
source: inferred
sources:
  - docs/handoff/cockpit-design/2026-10-09-chibi-native-board.md
  - docs/audit/cockpit-design/cdh-0001-implementation.md
  - docs/audit/cockpit-design/cdh-0002-cowork-verification.md
  - docs/design/cockpit-v0/Sprites.dc.html
  - tests/test_design_sprites.py
  - logs/scratch/design-review/cdh-0003/browser-verification.json
author: codex
status: final
tier: 2
---

# CDH-0003 implementation delivery

Board 10 now contains 7 native symbols, a 49-cell static matrix, 7 palette pairs, the retained run/detail/Phase 2 examples, and 1 selected detail controlled by 16 real buttons. There is no iframe or cast dependency on a sibling file. All 7 canonical SVGs remain byte-identical to the approved delivery. The 14 drift checks pass; the full check passes with 178 tests, 10 deselected, and 0 blocking lint findings. This closes the local implementation scope of CDH-0003; it does not claim that CW1 has passed inside the Design editor.

Delivery is local to `/Users/michaelgrigorian/Projects/Automate-design`, branch `design`. No commit, push, publication, agent message or ledger write was made by this implementation. At entry, CDH-0003 already carried `from: michou`, `status: open`, `adopted_by: michou`, and `adopted: 2026-10-09T23:21:00-07:00`. Its only closeout edits are `status: done` and `completed: 2026-10-11T15:51:09-07:00`. The earlier reassignment was resolved by Michou's instruction to continue in this worktree.

## Scope and implementation

The 8 source/test edits are `Sprites.dc.html`, `canvas.json`, `chibi/preview.html`, `chibi/characters.js`, the 2 named readers, `tools/review/design-prompt.md`, and `tests/test_design_sprites.py`. This report and the CDH-0003 status closeout bring the named deliverable to 10 files. The 7 PNGs and 1 JSON observation file are ignored scratch evidence under `logs/scratch/design-review/cdh-0003/`; no binary was placed under `docs/` or `memory/`.

CW1's source repair uses 1 literal copy of each canonical SVG body in a hidden symbol library. Every visible specimen uses `<svg><use href="#chibi-…"></use></svg>`. The copies are ordinary source in the artboard, with no committed generator, generated bundle, runtime loader, or build step. The 7 source files under `chibi/` remain canonical. Step 6's stop condition did not arise: the equality test enforces the copies directly.

The 6 material roles, sticker mappings, phosphor mapping, original transform pivots and original keyframes are preserved. Inherited CSS variables carry each instance's mode through the SVG use tree. The symbols explicitly use `overflow:visible`; leaving the symbol viewport at its default produced raster differences, while the explicit rule makes all 101 static comparisons pixel-identical. This is a rendering-container correction and changes 0 canonical SVG bytes. CW4's double halo and CW5's subtle sag stay as approved.

The 49 records come from `renderVals()` and render through `sc-for`; the row-label condition uses `sc-if`. SVG geometry is literal markup, never injected through a text hole. Actor, mode and palette buttons return handlers through the loop records and update component state. The `calm` boolean is exposed in `data-props`; hiding the 68 decorative instances retains the text and layout. Only the selected detail can acquire `is-animated`. Intersection, document visibility and media-query listeners update eligibility and are removed on unmount. The reduced-motion stylesheet also cancels animation independently of component state. The board binds 0 keyboard handlers; the Phase 2 y/n labels remain dashed and unbound.

CW2 uses the existing 2 board-1 tokens, muted `#6f8290` and rule `#1e2a33`; board 1 is unchanged. CW3 uses `Class: —` for absent classes. The standalone harness changes only those 2 tokens and the absent-class wording. Its shared `characters.css`, profiling logic and 7 SVGs are unchanged.

The exact Voice section, header copy, mapping rules and all 9 other artboards remain unchanged. Parsed `canvas.json` differs only in board 10's `is_interactive: true` and note s3's text; order, positions, sizes and every other note are unchanged. Board 10 remains at x=5680, y=1760, with `$preview={"width":1440,"height":1500}` and canvas `w=1440,h=1500`. Its bottom remains y=3260, 60 px above note s3 at y=3320; no relocation is needed. The 780 px native scroll region contains 1736 px of projected content, so all specimens are reached by scrolling without expanding the canvas footprint.

## Source and bounds verification

The final artboard is 80703 bytes with 765 literal opening elements, including editor template tags. Geometry appears once per actor. The standard-browser projection contained 7 symbols, 68 use instances, 49 matrix cells, 7 palette pairs and 16 buttons. All 7 assets total 54782 bytes and 582 SVG elements, counting each canonical root.

| Canonical SVG | Bytes | Elements, including root |
| --- | ---: | ---: |
| `arbiter.svg` | 8166 | 76 |
| `builder.svg` | 8775 | 98 |
| `guard.svg` | 8053 | 88 |
| `michou.svg` | 8730 | 95 |
| `reviewer.svg` | 7988 | 86 |
| `scribe.svg` | 6717 | 71 |
| `stranger.svg` | 6353 | 68 |

The browser checks ran on macOS 26.6.2, arm64, in isolated headless Chrome 155 at 1440 × 1500 CSS px and DPR 1, with GPU acceleration and background networking disabled. A disposable local test projected the declared template into ordinary HTML and exercised the actual `renderVals()` data and handlers using a minimal state stub. It did not load `support.js`, reproduce the Design engine, or fetch the Google Font. These observations establish source, SVG paint and bounds behavior in that projection only; they do not establish native import, native Play, native Tweaks or native lifecycle behavior.

The 101 static pixel comparisons comprise 98 combinations at 72 px, 2 context portraits at 24 px using their canonical crops, and the 1 guard context at 48 px. Each comparison rasterized both the canonical direct SVG and the native symbol/use representation with the same mode and palette. Every comparison had 0 differing RGBA channels. The canonical SVG hashes below also match the original CDH-0001 hashes, independently of this raster check.

All 49 actor/mode selections updated the selected href, labels and pressed state. The 2 portrait bounds measured 24 × 24 px, the selected full figure measured 72 × 72 px, and both ledger rows measured exactly 22 px high. The projected document remained 1500 px tall with 0 horizontal overflow. Scrolling the selected detail offscreen removed its animating class. Calm hid all 68 art instances and preserved the fact text; only the explicit motion-status sentence changed.

Two pixel captures 330 ms apart changed in each of the 6 animated modes and remained identical in asleep mode. Actual `prefers-reduced-motion: reduce` emulation removed eligibility and froze pixels even when the test forcibly restored the animating class, proving the CSS override in this browser. Chrome's `document.getAnimations()` returned 0 for these use-tree animations even while their rendered pixels changed; that API count is not evidence of 0 animation work. This delivery records 1 eligible root and observed motion, not a reliable enumeration of every shadow-tree effect or a new performance measurement. CDH-0001's standalone profiling evidence remains separate and is not recertified as native performance.

Source checks found 0 iframe/object/embed nodes, 0 sibling cast scripts or fetches, and 0 keyboard handlers. The exact `<script src="./support.js"></script>`, `x-dc`, `helmet`, `data-dc-script` and `$preview` remain. The only declared network resource besides the editor support mechanism is the allowed Google Fonts css2 link.

## Required checks

The 14 test cases cover 7 symbol bodies and 7 root sticker-material mappings. Body normalization strips outer whitespace and indentation between tags only; text, path data, attributes, attribute order and inline styles remain exact. The SVG root is excluded because viewports and palettes belong on each specimen; its sticker material string is checked separately.

```text
$ uv run pytest -q tests/test_design_sprites.py
..............                                                           [100%]
14 passed in 0.02s

$ uv run kgme lint
docs/handoff/proposed/2026-09-09-ssh-key-for-github.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-time-machine-destination.md: unknown-field [advisory] fields not named in the schema: reason
kgme lint: 115 notes, 0 blocking, 32 advisory, 7 cosmetic

$ make check
docs/handoff/proposed/2026-09-09-time-machine-destination.md: unknown-field [advisory] fields not named in the schema: reason
kgme lint: 115 notes, 0 blocking, 32 advisory, 7 cosmetic
uv run pytest -q tests -m "not agents"
........................................................................ [ 40%]
........................................................................ [ 80%]
..................................                                       [100%]
178 passed, 10 deselected in 20.40s
Checked 8 packages in 0.44ms
```

All 3 commands exited 0. `make check` also passed frozen dependency sync, Ruff lint and Ruff formatting (201 files). `git diff --check` passed. The 32 advisory and 7 cosmetic lint findings are existing schema/content findings outside this edit, including already-existing adoption metadata; 0 blocking findings remain. The report/status closeout receives an additional lint pass after installation.

## Hashes and evidence

The source-set digest is `c9539033c436b3773baeb167dbef9d27a4e7ffaa030d184f51a2d14923c891f3`: SHA-256 over sorted UTF-8 records `repository-path + NUL + file-sha256 + LF`, exactly the CDH-0001 algorithm. This table has 17 records: the original 13 source paths, plus the 3 guidance files and 1 drift-test file. The original 13-path subset now hashes to `fbae78ed582be104cd10528aa6650e83c7212c022baaabaffb6f9ce67857760d`. The report, handoff status and scratch evidence are outside the source set, as in CDH-0001; hashes for the latter 2 categories follow. A report cannot contain its own SHA-256 without self-reference, so its own hash is excluded.

| Repository path | State | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `docs/design/cockpit-v0/Sprites.dc.html` | Changed/new | 80703 | `1f8f1f456c4ee35bd98a3c4507e7e25043db80c4b259c7b97782eb6c8916da49` |
| `docs/design/cockpit-v0/canvas.json` | Changed/new | 3418 | `650393ca46d84101dd9a4c3655aa727202cb9315176aeb7d69cea40b88c0de80` |
| `docs/design/cockpit-v0/chibi/README.md` | Unchanged | 8459 | `06794bad4b0ef54a3ec73dc437e9471edbae9a6413e1215596b99bd514f7d949` |
| `docs/design/cockpit-v0/chibi/arbiter.svg` | Unchanged | 8166 | `8d7bb211574d347a5038dfb1b38aa7facc414369f24d7e640102059b16bdcdc1` |
| `docs/design/cockpit-v0/chibi/builder.svg` | Unchanged | 8775 | `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e` |
| `docs/design/cockpit-v0/chibi/characters.css` | Unchanged | 5724 | `7fcb692d48d26201744cf6795c899cdbaa9a93750bbb9d952407921bcd19a020` |
| `docs/design/cockpit-v0/chibi/characters.js` | Changed/new | 15789 | `900872eec1de4f457c120eeeedb068d4a2346ceeb9e803acfb20ac3dd0b4e26e` |
| `docs/design/cockpit-v0/chibi/guard.svg` | Unchanged | 8053 | `da6639d6cabae91e7fa622754a6fc27c9dc7c823e3657d34340a76729f6b31fa` |
| `docs/design/cockpit-v0/chibi/michou.svg` | Unchanged | 8730 | `46831a1e9d6ebf8991beb59b0281779ee6bc7869798fd2b168822b0f2bdfa9c7` |
| `docs/design/cockpit-v0/chibi/preview.html` | Changed/new | 12185 | `e9787a040ab072bcc6a5200418a2a40a0f0b7283cae5ef0370c3898fd1e19997` |
| `docs/design/cockpit-v0/chibi/reviewer.svg` | Unchanged | 7988 | `f444d74e398ab00a5a52e9160c50bf433113ba9115e0fe65efbb51b13e9a062b` |
| `docs/design/cockpit-v0/chibi/scribe.svg` | Unchanged | 6717 | `cba7d68489569c0dc783086829752807af719b3473dd9d0286a00807d39fc026` |
| `docs/design/cockpit-v0/chibi/stranger.svg` | Unchanged | 6353 | `7fed1b5845d5934e37580d7070c35adfbabb9e84cc9b87a0e536ef602ab81516` |
| `docs/readers/cockpit-design-chatgpt.md` | Changed/new | 8589 | `d1cbf3793bc447f280803b525f3670b931918d6828c4106472b2fd0bb3403e3a` |
| `docs/readers/cockpit-design.md` | Changed/new | 11313 | `0f8a1fb8f8fb678ba42ad355459d8c6cbaafa002b70620097ffa07fd56f47f8e` |
| `tests/test_design_sprites.py` | Changed/new | 1910 | `2088cb369492922729773f36b1b45c72f07b20896f0d77a5f2c924ee6e8c3062` |
| `tools/review/design-prompt.md` | Changed/new | 4538 | `64fc36f41cfad8439e420597de6ba7e65b0a8f5a391d00dcb8889d3d7b3f390f` |

The completed handoff `docs/handoff/cockpit-design/2026-10-09-chibi-native-board.md` has SHA-256 `dc5ce9eefae18c00c792ac6b9953466d90d4bfeae6e179fb98ce2db3f55e72a6`. This identifies its closeout bytes, not the older committed proposal or the pre-closeout open version.

Every evidence file below lives under `logs/scratch/design-review/cdh-0003/` and identifies board source SHA-256 `1f8f1f456c4ee35bd98a3c4507e7e25043db80c4b259c7b97782eb6c8916da49`. The 7 images are explicitly named browser projections or browser motion frames. They are not native canvas exports. The matrix and palettes/context images together show all 49 specimens as the internal region is scrolled; the overview, calm and reduced-motion images show their respective states. The JSON records the 101 per-case comparison results and the selection, calm, offscreen and reduced-motion observations.

| Evidence filename | Bytes | SHA-256 |
| --- | ---: | --- |
| `browser-motion-working-1.png` | 5563 | `f1a26153e850ef572c33d58f267ced9da8795f512f047224b0a1d645ce9493b1` |
| `browser-motion-working-2.png` | 5566 | `edd7054151a6c0c6f13743fc3f6a2ca39e6665ba1a8d291e3b292991154af938` |
| `browser-projection-calm.png` | 255091 | `4ef89f687305b3b45faee0d482bf3aeec60374dba3214c5f5ef32ecdc470a280` |
| `browser-projection-matrix.png` | 393423 | `95bff1bdfcb2b841f175c4b27b6337a31887122b258fd33e01ba4f8935df6c1d` |
| `browser-projection-overview.png` | 355039 | `4f74edc64a8828d45541d8cc4f036ebabf4dabd129e1e9258e91465f48d64165` |
| `browser-projection-palettes-context.png` | 396848 | `d0199569baafea7302f69cca8456fa679be6e27f5374396badfd8199e8f75680` |
| `browser-projection-reduced-motion.png` | 358230 | `fba6c4eb666be949c6995e61f9e4c196f54eef2835485aa52f5a8d2005974c80` |
| `browser-verification.json` | 21131 | `8cc7dfb3069ce07ee92b4ca56da9d87236cf16a3bfc8c5dcf7e231671d30e293` |

## Cowork delivery and remaining native checks

Cowork can now read this folder and begin the native verification intended as CDH-0004 by the adopted CDH-0003 and Michou's current instruction. The local files and source digest are the delivery; there is no implementation commit to review. Native acceptance remains unverified until Cowork mounts these files in its private review copy and records the result.

There is 1 coordination mismatch to resolve in that next handoff: `2026-10-09-chibi-native-verification.md` and the folder README still describe the older proposed Codex read-only review of a committed tree. They have not been edited or adopted here because CDH-0003 names neither as an output. The adopted CDH-0003 step 9 explicitly assigns Cowork the private-copy mount and native observation, followed by Codex's read-only review. Cowork should reconcile the stale CDH-0004 document with Michou's current assignment before executing its old command. This does not authorize a commit, publication, or final design approval.

Cowork's native check must establish that board 10 contains all 49 specimens and 7 palette pairs without a missing-frame error; all 3 context categories render; Play activates the 16 detail controls; calm hides the 68 art instances without losing facts; actual reduced motion freezes the selected detail; and the 9 untouched artboards and keyboard map remain unchanged. It must observe native symbol/use styling, event binding and component lifecycle behavior directly. The approved drawing itself is not reopened. The standalone harness README and footer still describe the older CDH-0001/CDH-0002 delivery; this report supersedes those integration-status statements, and their text was preserved because the harness scope only permits token and class-wording edits.

## Step 8 full diffs

The following full diffs show the 3 approved reader/reviewer edits against the worktree contents at the start of this implementation. They retire the 4 obsolete sprite constraints, retain the adopted source/performance requirements, move evidence references to scratch storage, preserve the read-only reviewer role, and record the worktree, no-binary and current implementation-exception rules. They do not authorize the review prompt as implementation instructions.

```diff
--- a/docs/readers/cockpit-design.md
+++ b/docs/readers/cockpit-design.md
@@ -3,7 +3,7 @@
 type: note
 status: active
 created: 2026-10-09T21:50:00-07:00
-modified: 2026-10-09T21:50:00-07:00
+modified: 2026-10-11T15:45:22-07:00
 author: cowork
 source: stated
 tier: 2
@@ -14,7 +14,7 @@
 *Written 2026-10-09 by Cowork for Michou, Claude Code, and the Codex reviewer (GPT-6 Astra). This is the context a cold reader needs before touching `docs/design/cockpit-v0/`. The design itself is HANDOFF-0036; the code that will be built from it is HANDOFF-0037.*

 ## What is in `docs/design/cockpit-v0/`
-Eleven plain files, all hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and ten `.dc.html` artboards. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.
+The original 12 core files were hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and 10 `.dc.html` artboards. CDH-0001 adds the reusable `chibi/` SVG sources, shared motion layer, standalone fixture and README. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.

 | File | Board | What it shows |
 |---|---|---|
@@ -29,6 +29,8 @@
 | `Wall.dc.html` | 9 | the four-column layout for an external monitor, with the raw vendor stream |
 | `Sprites.dc.html` | 10 | the cast: one sprite per `actor`, seven modes, two palettes, the rules |

+CDH-0001 implemented the reusable cast; CDH-0002 found the native iframe failure. Michou separately adopted CDH-0003 for Codex to rebuild board 10 as self-contained native markup; Cowork verifies it under CDH-0004. The scoped implementation exception does not change the independent read-only reviewer role or grant final design approval.
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
+The `.dc.html` format requires the native canvas editor; preserve its support mechanism and templating. The standalone `chibi/preview.html` fixture and SVG assets can be rendered in a browser when tool access permits. Read PNG evidence from `logs/scratch/design-review/`. Review the **source** and distinguish supplied PNG evidence, independently observed browser behavior, measured target-Mac performance and native observations. A fixture screenshot does not establish native canvas behavior. Cowork must import and observe the delivered native board under CDH-0004; any unavailable native capability remains explicitly unverified.

 What a design review is for, and the class each finding carries:
 - a fact shown only by colour, or a decorative element that carries a fact shown nowhere else → `blocking`
@@ -58,11 +62,12 @@
 - a `<div>` doing a button's job, an icon-only control without a label, focus shown by colour alone → `blocking`
 - a label or chip outside ADR-016's vocabulary (`ok`, `blocking`, `transient`, `advisory`, plus status `refused`, `pending`) → `advisory`
 - inconsistency between boards (a token, a key hint, a row layout that differs without reason) → `advisory`
-- anything in the sprite generator that would not survive as a standalone SVG under 3 KB → `advisory`
+- whether each actor's `<symbol>` in `Sprites.dc.html` matches its file under `chibi/` and whether every mode has adjacent text; use `tests/test_design_sprites.py` to check drift, and classify a lost fact as `blocking`
+- an unexplained exceedance of the provisional 512 KiB total sprite-source target, or omitted source-size, SVG-complexity or runtime evidence → `advisory`; never enforce the retired 3 KB cap or treat a byte count as a performance result
 - taste → `advisory`, stated as such; Michou's taste is the spec, the reviewer's is a suggestion
 - whitespace, typos → `cosmetic`

-What is not a finding: that the files exceed ADR-015's 300-line guide (artboards are drawings, exempt by HANDOFF-0036); that the `.dc.html` syntax (`<x-dc>`, `<sc-for>`, `{{holes}}`, `DCLogic`) is unfamiliar, it is the editor's format; that sample data is sample data.
+What is not a finding: that the files exceed ADR-015's 300-line guide (artboards are drawings, exempt by HANDOFF-0036); that the `.dc.html` syntax (`<x-dc>`, `<sc-for>`, `{holes}`, `DCLogic`) is unfamiliar, it is the editor's format; that sample data is sample data.

 The prompt that says all this to the reviewer is `tools/review/design-prompt.md`. First pass, from the repository root, Michou's terminal:

@@ -73,10 +78,12 @@
 Then Claude Code, on Michou's word, turns the scratch file into `docs/audit/AUDIT-NNNN-design-review-cockpit-v0-cycle-N.md` with report frontmatter, and records the cycle as a ledger note on `design:HANDOFF-0036`.

 ## How to iterate (the loop, for a drawing)
+Work in `~/Projects/Automate-design` on branch `design`, never on `main`. Codex reviews only until HANDOFF-0042, except for the explicitly adopted CDH-0001 and CDH-0003 implementation scopes. There are no binaries committed; captures live under `logs/scratch/design-review/` and identify their source hashes. CDH-0003 delivers local files and its report without committing or publishing; Cowork commits by pathspec at the next authorized checkpoint.
+
 1. Astra's findings land in the audit file. Michou reads them and rules: take, reject, or defer each, in one message to Cowork.
 2. Cowork edits the files under `docs/design/cockpit-v0/` (or Claude Code does, on a handoff), commits with `design: cockpit v0, cycle N (HANDOFF-0036)`, and republishes the canvas viewer from the committed files, so the page and the repository stay the same thing.
 3. Michou can also edit on the canvas page by hand; when he does, Cowork reads the page back, commits those changes, and republishes nothing. The repository is still the truth; the edit just arrived through the viewer.
 4. Acceptance closes the handoff: Michou records an `approval` event naming the committed tree (`kgme ledger note --kind approval …`, flags per `kgme ledger note --help`, summary `design: cockpit v0 approved at <short sha>`), and 0036 goes to `done`. 0037 builds from that sha and nothing else.

 ## For Michou's further requests to Astra
-Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules." Bad questions: "make it look better" (taste is Michou's), "render it" (it cannot), "approve it" (only Michou does).
+Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules," "inspect the standalone chibi fixture at 24/72 px." Bad questions: "make it look better" (taste is Michou's), "certify the native canvas without observing it," "approve it" (only Michou does).
--- a/docs/readers/cockpit-design-chatgpt.md
+++ b/docs/readers/cockpit-design-chatgpt.md
@@ -3,7 +3,7 @@
 type: note
 status: active
 created: 2026-10-09T22:20:00-07:00
-modified: 2026-10-09T22:20:00-07:00
+modified: 2026-10-11T15:45:22-07:00
 author: cowork
 source: stated
 tier: 2
@@ -20,15 +20,17 @@

 ## The design track, who does what
 - **Michou** owns taste and decisions. He wrote the brief, chose the palette and the type, asked for the HUD to be "almost too much" and the sprites to be "outrageous but retaining all the darkness." He rules on every finding and gives the final approval, recorded as a ledger event.
-- **Cowork** (Claude, in the Claude desktop app) is the designer. It drew the canvas: ten artboards as plain HTML/CSS/JS files, committed in the repository under `docs/design/cockpit-v0/`, mirrored to a canvas page where Michou can edit elements by hand. It applies Michou's rulings to the files, commits, and republishes the page.
-- **Codex** (GPT-6 Astra, via `codex exec` in a read-only sandbox) is the independent reviewer. It reads the source files and any PNG exports, and returns findings in a fixed format: a table with id, class, file:line, finding, fix; a verdict; notes. Its prompt is `tools/review/design-prompt.md`. It cannot render the boards, write files, or approve anything.
+- **Cowork** (Claude, in the Claude desktop app) is the designer. It drew the canvas: ten artboards as plain HTML/CSS/JS files, committed in the repository under `docs/design/cockpit-v0/`, mirrored to a canvas page where Michou can edit elements by hand. It applies Michou's rulings to the files, commits, and republishes the page. Under the separately adopted CDH-0002, it independently verifies the delivered cast in its native canvas and reports findings; that local review authorizes no source repair, publication or final approval.
+- **Codex** has 2 distinct roles. The independent reviewer runs GPT-6 Astra via `codex exec` in a read-only sandbox, reads source and visual evidence, and returns the fixed Findings table, Verdict and Notes under `tools/review/design-prompt.md`; that prompt grants no edits. Separately, Michou adopted CDH-0001 for Codex/Astra to implement the approved cast and CDH-0003 to place its unchanged symbols in the native board, within named local files. Codex otherwise reviews only until HANDOFF-0042. Codex can observe the standalone SVG/browser fixture; Cowork independently observes the native canvas under CDH-0004. Neither role can grant final approval.
 - **You (ChatGPT)** are Michou's design sparring partner and his liaison to the Codex side. Details below.

+Work in `~/Projects/Automate-design` on branch `design`, never `main`. No binaries are committed; captures live under `logs/scratch/design-review/`. CDH-0003 delivers local files and its report without committing or publishing; Cowork commits by pathspec at the next authorized checkpoint.
+
 ## The one rule the whole design obeys
 Signal in the centre, noise at the edges, and noise never carries information. The timeline, the detail pane and the run grid carry facts. The frame, tick rails, micro-labels, scanlines, vignette and every sprite are decoration that only repeats a fact already shown in text, so a single key (`c`) and the reduced-motion setting can remove all of it without loss. Anything you propose must pass this test: if a decorative element would be the only place a fact is shown, it is wrong.

 ## What is decided (do not reopen)
-Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` for focus and live and the frame, magenta `#ff3d7f` for blocking only, amber `#ffb02e` for pending/transient/advisory, green `#4de38a` for ok. JetBrains Mono everywhere, dense, 22 px rows. The frame's colour carries system state (cyan live, magenta flood on blocking, amber strip while an intent awaits its outcome, grey static when disconnected). The keyboard map (j/k, g/G, Enter, Esc, u, Tab, f, /, 1–4, 0, r, t, o, x, c, p, w, ?; b, m, y/n, ;, Space reserved for Phase 2, dashed). Three strike boxes for the review loop's bound. Sprites: one per actor, not per model (builder, reviewer, arbiter, guard, scribe, Michou, stranger), 24 × 24 pixels, original line work, no stock or game assets, two frames per mode, seven modes (idle, working, waiting, transient/melting, blocked/on fire, done/halo, asleep/chalk outline), the accent colour is the row's class colour, phosphor in the timeline, a sticker palette only in the detail-pane header and the Phase 2 model selector.
+Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` for focus and live and the frame, magenta `#ff3d7f` for blocking only, amber `#ffb02e` for pending/transient/advisory, green `#4de38a` for ok. JetBrains Mono everywhere, dense, 22 px rows. The frame's colour carries system state (cyan live, magenta flood on blocking, amber strip while an intent awaits its outcome, grey static when disconnected). The keyboard map (j/k, g/G, Enter, Esc, u, Tab, f, /, 1–4, 0, r, t, o, x, c, p, w, ?; b, m, y/n, ;, Space reserved for Phase 2, dashed). Three strike boxes for the review loop's bound. Sprites under adopted CDH-0001: 1 per actor, not per model (builder, reviewer, arbiter, guard, scribe, Michou, stranger), original smooth SVG geometry, 6 semantic material roles with restrained cel shading, deliberate 24 px run portraits and full 72 px detail characters. Up to 2 authored key poses per mode interpolate reusable parts across 7 modes (idle, working, waiting, transient/melting, blocked/on fire, done/halo, asleep/chalk outline). Modes are not failure classes. Accent repeats an adjacent written class or state; phosphor stays in the timeline and sticker only in the detail header and illustrated Phase 2 model selector. All run portraits stay static; only 1 selected visible detail animates, with animation work removed when hidden, offscreen, calm or reduced motion is requested. Every actor, lifecycle, class and event fact remains in text. The retired 24 × 24 grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap no longer apply. A provisional 512 KiB raw target covers all 7 SVGs plus shared animation code; report source bytes, SVG element counts, active animations and 30-second target-Mac motion/calm captures with 50 static portraits and 1 selected detail. Missing measurements stay unverified.

 ## What is open (where you can help)
 Whether the canvas passes the acceptance test; sticker placement (two spots, or a `sticker` tweak that allows it anywhere); whether the "you" sprite should resemble Michou; the "mood" copy for the corner micro-labels (a set of gallows one-liners exists on board 10, "the ledger remembers · you may not", "server unreachable · as are we all"); and, after Codex's first pass, which of its findings to take.
@@ -36,12 +38,12 @@
 ## Your job, concretely
 1. **Read Codex's findings with Michou.** He will paste the review. For each finding, say in one line whether it holds against the rules above, and draft his ruling: take, reject with reason, or defer. The output he needs is a numbered list he can send to Cowork as-is.
 2. **Write the next Codex prompt** when a pass should be narrower ("only the keyboard map and board 7", "only the sprite generator"). Keep Codex's fixed output format (Findings table, Verdict, Notes) and the class vocabulary.
-3. **Look at PNG exports** when Michou gives them to you; Codex cannot see pixels well, you can. Report what you see in the same finding format, marked as yours. Captures an agent makes live in `logs/scratch/design-review/` and are disposable; nothing binary is committed to the repository except the SVG sources.
-4. **Ideate inside the rules**: sprite ideas as 24 × 24 pixel grids using the six fills (`b` garment, `s` face, `h` hat and tool, `p` print, `d` dark, `a` accent); micro-label copy in the stated register; mode animations with at most two frames. Darkness kept, originality required: no named characters, no game or stock imagery.
+3. **Look at visual evidence** when available, including the approved reference sheet, source-identified PNG exports and the standalone browser fixture. Report what you observe in the same finding format, marked as yours. Keep native canvas observations separate; Cowork performs those under CDH-0004.
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
+You are GPT-6 Astra, the independent reviewer in KGME (docs/readers/review-loop.md), reviewing a DESIGN, not code: the cockpit v0 canvas under docs/design/cockpit-v0/ (HANDOFF-0036). This prompt remains read-only and grants no source edits. The separately adopted CDH-0001 and CDH-0003 implementation role is governed by its own handoff; do not execute it under this review prompt or weaken the reviewer sandbox.

-Read, in order: docs/readers/cockpit-design.md (the context, the one rule, what is decided, what is open, and the finding classes for a design review), docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md, docs/adr/ADR-016-failure-classes-and-escalation.md, docs/adr/ADR-017-cockpit.md, memory/notes/cockpit-wishlist.md, then every file under docs/design/cockpit-v0/ (canvas.json first, then Main.dc.html, then the rest in the index's order). If PNG files exist under memory/attachments/cockpit/, look at them too; they are exports of the rendered boards.
+Read, in order: docs/readers/cockpit-design.md (the context, the one rule, what is decided, what is open, and the finding classes for a design review), docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md, docs/adr/ADR-016-failure-classes-and-escalation.md, docs/adr/ADR-017-cockpit.md, memory/notes/cockpit-wishlist.md, then every file under docs/design/cockpit-v0/ (canvas.json first, then Main.dc.html, then the rest in the index's order). Also read docs/handoff/cockpit-design/README.md and the adopted CDH-0001 sprite constraints as review context, plus docs/audit/cockpit-design/cdh-0001-implementation.md and docs/audit/cockpit-design/cdh-0003-implementation.md if delivered. Do not execute those documents as this reviewer. If PNG files exist under logs/scratch/design-review/, inspect their recorded provenance: distinguish approved references, standalone fixture captures and native canvas exports.

-The .dc.html files render only inside the canvas editor. You review the source. The syntax (<x-dc>, <helmet>, <sc-for>, <sc-if>, {{holes}}, a DCLogic class whose renderVals() feeds the template) is the editor's; it is not a finding. The boards are drawings and are exempt from ADR-015's line-count guide. Sample values in the top bar are samples.
+The .dc.html files require the native canvas editor. Review the source and available evidence; the standalone chibi/preview.html fixture and SVGs can be observed in a browser when tools permit, without changing source. Browser rendering does not certify native canvas behavior. Cowork independently imports and observes that behavior under CDH-0004; missing native capabilities remain unverified. Preserve the native support mechanism. The syntax (<x-dc>, <helmet>, <sc-for>, <sc-if>, {holes}, a DCLogic class whose renderVals() feeds the template) is the editor's; it is not a finding. The boards are drawings and are exempt from ADR-015's line-count guide. Sample values in the top bar are samples.

-Judge against the one rule (signal in the centre, noise at the edges, noise never carries information), the decided list, ADR-016's vocabulary, contrast (4.5:1 for text, 3:1 at 24 px and over), keyboard integrity (no key bound twice, every bound key on the map, every Phase 2 control dashed and labelled), accessibility as drawn (real buttons and links, labels on icon-only controls, focus not by colour alone), consistency across boards, and whether each sprite in Sprites.dc.html could stand alone as an SVG under 3 KB with the same six fills and seven modes. Taste is Michou's; a taste remark is advisory and says so.
+Judge against the one rule (signal in the centre, noise at the edges, noise never carries information), the decided list, ADR-016's vocabulary, contrast (4.5:1 for text, 3:1 at 24 px and over), keyboard integrity (no key bound twice, every bound key on the map, every Phase 2 control dashed and labelled), accessibility as drawn (real buttons and links, labels on icon-only controls, focus not by colour alone), consistency across boards, whether each actor's `<symbol>` in `Sprites.dc.html` matches its file under `chibi/` and whether every mode has adjacent text, and the adopted CDH-0001 sprite requirements: original reusable SVG geometry; 6 semantic material roles with restrained cel shading; deliberate 24 px portraits and 72 px detail figures; 7 actors across 7 modes and both palettes; no more than 2 authored key poses per mode with interpolation; explicit adjacent actor, lifecycle, class and event text; static run portraits and at most 1 selected visible animated detail; no animation work when hidden, offscreen, calm or reduced motion is requested. Modes must not become new failure classes. The retired 24 × 24 source grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap are not criteria. Treat 512 KiB raw for all 7 assets plus shared animation code as a provisional engineering target. Check per-actor/total bytes, SVG element counts, active animations, and 30-second target-Mac motion/calm measurements with 50 static run portraits and 1 selected detail, including environment, frame intervals, long tasks and interaction observations. Missing evidence stays unverified; small source size proves no runtime-performance result. Taste is Michou's; a taste remark is advisory and says so.

 Your final message is markdown with exactly three sections:
 ## Findings
@@ -12,4 +12,4 @@
 ## Verdict
 One line: PASS if no blocking finding stands open, else BLOCK with the count.
 ## Notes
-Anything a cold reader would want, including the three things you would change first if taste were yours, marked as taste. State which files you read and whether you saw PNG exports.
+Anything a cold reader would want, including the three things you would change first if taste were yours, marked as taste. State which files and source hashes you reviewed, which PNGs or browser interactions you observed, which measurements were supplied by Codex, and which native checks remain unverified.
```
