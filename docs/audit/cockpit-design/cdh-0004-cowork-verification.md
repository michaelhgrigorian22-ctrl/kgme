---
id: AUDIT-CDH-0004
type: report
created: 2026-10-12T15:32:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0004
  - CDH-0003
  - docs/audit/cockpit-design/cdh-0003-implementation.md
  - docs/audit/cockpit-design/cdh-0002-cowork-verification.md
  - docs/design/cockpit-v0/ at 0bb87d5 (source-set digest c9539033c436b3773baeb167dbef9d27a4e7ffaa030d184f51a2d14923c891f3)
  - logs/scratch/design-review/cdh-0004/
tier: 2
status: final
handoff: CDH-0004
period: "2026-10-12"
review_canvas: "private review copy, Design type, https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh (delivery at version 1791762876-2c76; experiment at version 1791842738-0c7a); the accepted viewer RgRWz6iKEgR8SJJ6m1mUwY was not touched"
reviewed_source_digest: c9539033c436b3773baeb167dbef9d27a4e7ffaa030d184f51a2d14923c891f3
reviewed_sha: 0bb87d5
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW7 | blocking | docs/design/cockpit-v0/Sprites.dc.html:800, :804, :808, :811–:814, :821–:827 (51 holes in all, inside `<x-dc>`) | **Every template hole is written with single braces — `{selected.name}`, `list="{cells}"`, `onClick="{choice.pick}"`, `href="#{selected.symbol}"` — while the editor's hole syntax, and every other board on the canvas, is `{{…}}`.** The file contains 51 single-brace holes and zero `{{`. Natively the runtime therefore resolves nothing: in Play the board shows the literal text `{selected.name}`, `{selected.mapping}`, `{motionStatus}`, `{selected.bio}`, the actor/mode/palette rows are empty, the detail mount is empty, and the matrix shows only its "Actor / mapping" header with no cells (evidence `native-as-delivered-board-10-unresolved-holes.jpg`). Codex's projection test used its own template substitution, which accepted single braces, so it never saw this; nothing in its report claims native rendering. The symbols, CSS and logic block are not at fault: with the holes rewritten to `{{…}}` in the review copy only (below), the board renders completely. | Inside `<x-dc>…</x-dc>` of `Sprites.dc.html`, rewrite each hole `{name}` / `{a.b}` to `{{name}}` / `{{a.b}}` — the substitution `(?<![$\{])\{([A-Za-z][A-Za-z0-9_.]*)\}(?!\})` → `{{\1}}` makes exactly 51 replacements and leaves CSS braces and the logic block's `${…}` template literals untouched (the logic block is byte-identical before and after). The result is on disk as `logs/scratch/design-review/cdh-0004/experiment-Sprites.dc.html` (SHA-256 `a5e612fbea9e8f652f361517f659d7cd3993e38c8b7029d9d0d0b58b7792538a`) and can be copied over the delivered file verbatim; the drift test is unaffected because the `<symbol>` bodies contain no holes. |
| CW8 | advisory | docs/design/cockpit-v0/Sprites.dc.html:38, :43 | At viewport widths under the board's 1440 px the matrix headers and the palette-pair captions collide ("Mode: working" over "Lifecycle:", "PhosphorSticker" run together) because `.sprite-matrix` and `.palette-grid` are `minmax(0,1fr)` grids with no horizontal scroll box (evidence `native-experiment-pairs-and-contexts-800px-collisions.jpg` at 800 px versus `…-fill-width.jpg` at the board's width, where the layout is correct). The editor's own rule for a PAGE is that wide tables scroll in a box at narrow widths; the standalone fixture already does this with `.matrix-scroll{overflow-x:auto}`. | Wrap the matrix and the pair grid in an `overflow-x:auto` box with a `min-width` on the grid (the fixture's `.matrix-scroll` / `min-width:970px` pattern), so narrow viewports scroll instead of overlapping. Not a defect at the intended width. |
| CW9 | cosmetic | docs/design/cockpit-v0/chibi/README.md:3, :55–:57; chibi/preview.html footer | The harness README and the fixture footer still describe the CDH-0001 iframe integration and "await CDH-0002"; Codex preserved them because its scope allowed only token and wording edits there. Stale after CDH-0003. | Two sentences in each, in the same revision as CW7. |

Not findings, recorded so they are not re-raised: CW1 (the iframe) is resolved in source — no `<iframe>`, `<object>`, `<embed>`, sibling `<script src>` or `fetch` for the cast; CW2 and CW3 applied (board-1 tokens; `Class: —`, observed natively in the facts text); CW4 and CW5 closed as drawn; boards 1–9 byte-identical to `7bf773f`; `is_interactive: true` took effect natively (board 10 carries a PLAY button on the canvas); the Tweaks tab shows exactly one lever, "Sprites › calm"; no keyboard handler; the Phase 2 card's `y`/`n` stay dashed; the drift test `tests/test_design_sprites.py` passes (14) from an out-of-repo environment; `kgme lint` 0 blocking.

### Verdict

BLOCK: 1 blocking finding

### Notes

**What I opened and did natively.** Signed-in browser pane on the Mac (the Claude desktop app's built-in browser), pane width 800 CSS px, default motion settings. I published the four changed files of `0bb87d5` (`Sprites.dc.html`, `canvas.json`, `chibi/characters.js`, `chibi/preview.html`) to the existing private review copy over Michou's Friday-night state (which was the editor's own reformatting of `canvas.json` plus a dropped contact-sheet image on board 10, not design intent); the accepted viewer was not touched. Opened board 10 through PLAY › Play full screen and observed the as-delivered state (CW7). Then, as a labelled experiment in the review copy only, published the brace-corrected board and observed: the 7 × 7 phosphor matrix with every mode header carrying Lifecycle / Class / Event text, magenta fire on `blocked`, green halo on `done`, chalk outline on `asleep`; the seven phosphor/sticker pairs with captions; the two run headers with 24 px portraits above 22 px rows and the arbiter detail header; the selected-detail panel with its 16 real buttons; state changes through those buttons (builder → arbiter, waiting → blocked → asleep, sticker → phosphor), each reflected in the facts text and the 72 px drawing; zoom at 72 px on sticker and phosphor arbiter in `blocked` with no clipping of hat, staff or fire; the Tweaks tab's `calm` toggle turning the artwork off with every fact line retained and the status reading "Calm: artwork hidden; all facts retained." The viewport-size emulation of the pane clips rather than scales, so the 1440 px view was taken from the editor's own Fill mode.

**What I could not observe natively, and why.** (1) Motion: the board's frame reported `document.hidden` as true from this pane throughout (its status read "Document hidden: animation removed"), which is the visibility gate working as designed, not a defect; wheel scrolling inside the frame also timed out for the same reason. Native playback is therefore unverified by me; the mechanism (one `is-animated` class on the selected detail, keyframes in `<helmet><style>`) is identical to the standalone fixture whose motion I observed under CDH-0002 and Codex measured under CDH-0003. Michou will see it on his own screen. (2) Reduced motion: the macOS setting cannot be toggled from here; the CSS media block is the same as the fixture's, verified in CDH-0002. (3) The matrix under calm: the inner scroll region could only be moved with keys and not reliably; the detail under calm was observed and the same rule hides all specimens. (4) Target-Mac performance: Codex-measured only (CDH-0001 captures); the CDH-0003 report makes no new performance claim.

**Experiment identity.** Board as delivered: SHA-256 `1f8f1f456c4ee35bd98a3c4507e7e25043db80c4b259c7b97782eb6c8916da49`. Board with holes rewritten: `a5e612fbea9e8f652f361517f659d7cd3993e38c8b7029d9d0d0b58b7792538a`, differing from the delivered file only in the 51 hole substitutions inside `<x-dc>`. The experiment is a verification aid, not a delivery: the repository still holds the delivered file, and the review copy currently shows the experiment with `calm` left on in its Tweaks.

**Evidence** under `logs/scratch/design-review/cdh-0004/` (all native, browser-pane captures unless named `experiment-`):

| File | What | SHA-256 |
|---|---|---|
| native-as-delivered-board-10-unresolved-holes.jpg | CW7: Play view of the delivered board | `18a42c28d1a988edec227f15931c27348978397e6763604156c35d4dec355d25` |
| native-experiment-matrix-phosphor.jpg | braces fixed: matrix, mode headers, first rows | `0fa21317bb6224b54a4cfbb9e0b1c55f7d4860e6a8a8a6f5506e58b9c9c1d38b` |
| native-experiment-pairs-and-contexts-fill-width.jpg | pairs and run-header context at the board's width | `1d2be4ef6daaf609312fee4b35681f5f3226303b81892d2dc289ed7cc1db71c7` |
| native-experiment-pairs-and-contexts-800px-collisions.jpg | CW8 at 800 px | `46571ce3bc21c292b373499c52bd15c8fb81704a13f50fa5075874737a3dac24` |
| native-experiment-detail-controls-builder-sticker.jpg | 16 buttons, builder, sticker | `0482a9408040cb61b5462cb5b1d867610ae86c37806ecccaf25c5b8de05a9997` |
| native-experiment-detail-arbiter-blocked-sticker.jpg | after two button presses | `4071622cc82fc1427e5286679a58e7673d41ad18a5da3c7ee402acd1b6ea8392` |
| native-experiment-zoom-arbiter-blocked-sticker-72px.png | 72 px, sticker | `81b1ad89076e27d324f14f9ca9a5acb7d1a021c2789e3c2ad71f6791eb206143` |
| native-experiment-zoom-arbiter-blocked-phosphor-72px.png | 72 px, phosphor | `ffda6965074820d83b19361f7f5561c3e86d317756dd3637fb9123e298f54b31` |
| native-experiment-detail-arbiter-asleep-phosphor.png | chalk outline, `Class: —` | `f912d3ea127155ec42b7b6dfe6291c7d145163af0820ca8fd78f588e4c75f2e6` |
| native-experiment-tweaks-panel-calm.jpg | the one tweak | `02adbe4fde9fa006e75299ed1b1eb2891b324700def01abe6712d7b981ef3368` |
| native-experiment-calm-on-detail-hidden-facts-retained.jpg | calm on | `b47ebd974d9d2b2b39a743d209f5d56d25af8ecfe84d5b30bb45be5c317d6f3c` |
| experiment-Sprites.dc.html | the brace-corrected board (text) | `a5e612fbea9e8f652f361517f659d7cd3993e38c8b7029d9d0d0b58b7792538a` |

**Proposed rulings (recommendations for Michou, not decisions).**
- CW7: take. Codex is review-only, the fix is mechanical and already validated natively, so Cowork applies it under CDH-0006 (drafted, `proposed`), commits on `design`, republishes the review copy and re-checks natively in the same pass; CDH-0005 (Codex's read-only review) then runs on that commit.
- CW8: take, in CDH-0006, unless Michou prefers the board to be judged at 1440 only.
- CW9: take, in CDH-0006.

This verification is of the CDH-0003 delivery only. It is not Michou's design approval; HANDOFF-0036 stays open to his final word.
