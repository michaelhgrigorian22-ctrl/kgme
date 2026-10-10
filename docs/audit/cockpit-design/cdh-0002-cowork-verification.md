---
id: AUDIT-CDH-0002
type: report
created: 2026-10-09T22:56:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0002
  - CDH-0001
  - docs/handoff/cockpit-design/README.md
  - docs/audit/cockpit-design/cdh-0001-implementation.md
  - docs/readers/cockpit-design.md
  - docs/design/cockpit-v0/ (source-set digest 5c09201f57e5f5e9e4c6324a53bee85e69e0c8b5d40f07651668bef24013df3e)
  - memory/attachments/cockpit/chibi-reference/approved-cast.png
  - memory/attachments/cockpit/chibi-reference/style-reference.png
  - memory/attachments/cockpit/chibi-review/cdh-0002/
tier: 2
status: final
handoff: CDH-0002
period: "2026-10-09"
review_canvas: "private review copy, Design type, https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh (version 1791611311-c140); the accepted viewer RgRWz6iKEgR8SJJ6m1mUwY was not touched"
reviewed_source_digest: 5c09201f57e5f5e9e4c6324a53bee85e69e0c8b5d40f07651668bef24013df3e
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW1 | blocking | docs/design/cockpit-v0/Sprites.dc.html:44 (and :86, :43) | **Nothing of the cast renders on board 10 in the native canvas.** The board's fixture `<iframe src="./chibi/preview.html?embed=1">` renders the text `not found` (evidence `native-board-10-fixture-frame-not-found.jpg`). The editor renders each artboard as a self-contained document; a relative path from a board does not reach a sibling file, and the frame origin does not serve `project/chibi/*` at a plain path either (probe: `<frame-origin>/project/chibi/preview.html` → `not found`). The editor's own format rules exclude `<iframe>`, `<object>` and `<embed>` from artboards. So the 49 specimens, both palette comparisons, the 24 px run-header and 72 px detail-header contexts, the Phase 2 card and every fixture control are absent natively; board 10 shows only its header, an empty 780 px frame, the Voice panel and the Rules panel. The "Open the standalone fixture" link (line 43) resolves the same way and opens nothing. CDH-0002 checks 1–5 therefore cannot be evidenced in the native canvas: that is the acceptance gap. | Bring the cast into board 10 as markup the editor renders itself, which is what its format provides for: inline `<svg>` geometry inside `<x-dc>` (one `<symbol>` per actor part, `<use>` for the 49 cells, so the drawing is not copied 49 times), the mode and palette as CSS classes with the keyframes in `<helmet><style>`, text labels as literal markup, and the fixture's actor/mode/palette/calm controls as `data-props` tweaks or `<sc-if>` state rather than `<select>`s driven by script. Alternatively one `Chibi.dc.html` child component (props actor, mode, palette) mounted by `<dc-import>` inside `<sc-for>`; note every `.dc.html` under `project/` also appears as an artboard, so list it and place it. Keep `chibi/preview.html` as the browser profiling harness, but the board must not depend on it. The seven SVGs and `characters.css` stay the source of the geometry and motion. |
| CW2 | advisory | docs/design/cockpit-v0/chibi/preview.html:9 | Token drift between the fixture and the boards: `--muted:#93a6b3` and `--rule:#293946` versus the component sheet's `#6f8290` and `#1e2a33`. Both pass contrast on `#0a0c10` (`#6f8290` ≈ 4.9:1, `#93a6b3` ≈ 7.7:1), so this is consistency, not accessibility. | Either use the sheet's tokens in whatever replaces the fixture inside board 10 (CW1), or, if the lighter muted is wanted for 9–10 px captions, add it to board 1's palette as a named small-text token so the two agree. |
| CW3 | advisory | docs/design/cockpit-v0/chibi/characters.js:14, :15, :20 | `Class: no outcome` is rendered in the matrix headers and the selected-detail facts as the value of the class slot for idle, working and asleep. ADR-016's vocabulary is `ok`, `blocking`, `transient`, `advisory` (plus status `refused`, `pending`); "no outcome" is a phrase, not a class, and sits where a class is read. | Render the absence as `Class: —` or `Class: none yet`, and keep "no outcome" for prose. |
| CW4 | advisory (taste) | board 10, guard / done / both palettes (evidence `contact-sheet-49-sticker-72px-standalone.png`, row guard, column done) | The guard wears a material halo already; in `done` the green status halo is drawn above it, so two halos stack. Readable, but the one actor whose costume includes a halo is the one where the status halo is least distinct. | Michou's call. Options: suppress the status halo for the guard and let the shield's X glow green instead, or lift the status halo clear of the material one. |
| CW5 | advisory (taste) | board 10, column transient, all actors (same evidence) | The `transient` "melting" reads as a slight lean and sag at 72 px; identity is preserved, as the brief asks, but the melt is subtle enough that without the adjacent `transient` text it would be missed. The text is there, so this is not a signal finding. | Michou's call: a stronger droop (hat brim, shoulders, prop tip) within the two-key-pose rule, or leave as is. |
| CW6 | cosmetic | docs/design/cockpit-v0/chibi/README.md:1 | No frontmatter; `kgme lint` reported it `blocking` at delivery time. Resolved outside this handoff: schema v1.4 exempts `README.md` by name and HANDOFF-0041 (done 2026-10-09T22:36:40-07:00) made the validator agree. | None. |

Not findings, recorded so they are not re-raised: the retired 24 × 24 grid, six flat fills, two hard frames and 3 KB cap (superseded for the sprite design by CDH-0001); the nine other artboards (byte-identical to commit `40aa62b`, so board 7's map, board 8's dashed Phase 2 controls and all mood copy are unchanged); no keyboard listener anywhere in the delivered source, and the fixture's own text says so; the sticker palette confined to detail specimens and the Phase 2 selector in the delivered fixture, with the unapproved global sticker tweak not enabled; `canvas.json` changed in note `s3` only, parsed values of every board entry identical; the `.dc.html` templating, `./support.js` line, `<x-dc>`/`<helmet>`/`DCLogic` and the exact Voice section retained (the board's text panels do render natively, evidence `native-board-10-voice-and-rules.jpg`).

### Verdict

BLOCK: 1 blocking finding

### Notes

**What I opened and did natively.** Signed-in browser pane on the Mac (the Claude desktop app's built-in browser, Chromium-based), pane width 800 CSS px at DPR 2, motion settings default. I created a separate private Design-type canvas as the review copy (identity in frontmatter) and published the delivered tree to it verbatim under `project/`: `canvas.json`, all ten `.dc.html` boards, and the eleven files of `chibi/`. The accepted viewer was neither read for publishing nor republished. In the review copy I observed the canvas overview (all ten boards render; evidence `native-review-copy-overview-10-boards.jpg`), opened board 10 full-window, scrolled it end to end, and clicked its fixture link. I did not play any mode, toggle calm, or emulate reduced motion natively, because there was nothing on the board to play: CW1. One diagnostic probe of the frame origin's path for `project/chibi/preview.html` returned `not found`; no other site, login or setting was touched. The pane was set back to its default size.

**What was read-only source review.** `Sprites.dc.html`, `canvas.json` (diff against `40aa62b`), `chibi/preview.html`, `characters.css`, `characters.js`, `chibi/README.md`, Codex's implementation report, and the Design type's own format instructions (which forbid iframes and script-built UI in an artboard).

**What was supplied by Codex and is Codex-measured, not mine.** The 30-second captures (headless Chrome 155 on the target Mac, M4 Pro, 1440 × 1100 at DPR 2: RAF p95 33.4 ms motion and calm alike, zero long tasks, input-to-frame p95 27.6 / 29.2 ms), the 98-combination behaviour checks, the 74.5 KiB source total against the 512 KiB provisional target, and the eight PNGs under `chibi-review/cdh-0001/` whose hashes I verified. None of that is native evidence and none of it is overturned by CW1; it describes the standalone fixture, which works.

**What I observed in a standalone browser, which is not native verification.** To separate "the mounting failed" from "the artwork or motion failed", I served the delivered `chibi/` folder unchanged over loopback inside my own sandbox and drove the fixture in headless Chromium 141 (Linux, 1440 × 1000 at DPR 2) through its documented `window.chibiFixture` API; log in `run-log.json`, every file suffixed `-standalone`. Observed: ten same-origin requests and no external request; builder/working animates (frames 500 ms apart differ) with one active animation (`chibi-hammer`); working → done leaves only `chibi-halo`; calm gives zero animations with the selected-detail facts text byte-identical before and after; Chromium's real `prefers-reduced-motion: reduce` gives zero animations and identical frames even after the preview control selects arbiter/blocked; visible ledger rows measure 22 px, run-header portraits 24 × 24, the detail 72 × 72; no page errors. All 49 combinations in both palettes are on the two contact sheets. Against the approved sheet, at 72 px: each of the seven identities survives with its specified props (hardhat, cigarette, cheetah overalls and jackhammer; monocle, grin, hat and loupe; skull, star hat and star staff; riot helmet, wings, halo and X shield; hood, bone hands, ledger and quill; bucket hat, sunglasses, chain, cheetah hoodie and flip phone; CRT head, antennae, static face, grey coat). The spiked collar on the reviewer and the fine chain on Michou are simplified to a few marks, which the brief allows. The 24 px portraits are deliberate head crops and read as the right actor beside a 22 px row. Blocked fire is a small magenta flame at the feet, no full-figure strobe; done is a green halo; asleep is a chalk outline with zz. Fixed ochre cloth, the guard's halo and the reviewer's teal carry no status meaning in either palette. The sticker palette is the painted colour set; phosphor is the slate/cyan monochrome; both keep magenta and green only for the class-driven accents. This is an appearance and behaviour read of the same source files; a target-Mac browser may render fonts and anti-aliasing differently, and nothing here certifies the native canvas.

**Reviewed hashes.** Source-set digest `5c09201f57e5f5e9e4c6324a53bee85e69e0c8b5d40f07651668bef24013df3e`, all thirteen rows of Codex's table matching the files on disk at review time; both reference PNGs matching the README; all eight `cdh-0001` evidence PNGs matching the report. Evidence written by this review, under `memory/attachments/cockpit/chibi-review/cdh-0002/`:

| File | What | SHA-256 |
|---|---|---|
| native-review-copy-overview-10-boards.jpg | native canvas, all ten boards | `b96e34fedfa8698baecc20df03d3c2001eeb48d0680065da9f836c226fb4b228` |
| native-board-10-fixture-frame-not-found.jpg | native, board 10 full-window, top | `4b12b5877ee69515362908607e810866db45b8fb74afd12888667f08063ae221` |
| native-board-10-voice-and-rules.jpg | native, board 10, lower panels | `42a10c7e8cad51f844cb6f1434a61b754f1564916bc7bc49041d2350b0aed834` |
| contact-sheet-49-sticker-72px-standalone.png | 7 × 7, sticker, 72 CSS px at DPR 2 | `00c2c3dd83dbf1be90a648e290f343630cc049beebeeb16b38d57e354f22c1f2` |
| contact-sheet-49-phosphor-72px-standalone.png | 7 × 7, phosphor, 72 CSS px at DPR 2 | `14c6fe9fbebd253323fca9b23cb5b242e76e60072aec2788ed9a28d92bfb6a85` |
| contexts-stacked-standalone.png | run headers at 24 px beside 22 px rows; detail header at 72 px; dashed Phase 2 card | `9a281145e43ac591b49e6a25cd9120b5abca554937c27638fc799c2aff776120` |
| run-header-portraits-zoom-3x-standalone.png | the two 24 px portraits, 3 × nearest-neighbour | `280c1a01ec0684d83cc7bfc4be75cb2b71f477d1bfbf338b8756ba7fa8e835ca` |
| fixture-overview-full-page-standalone.png | fixture as delivered, full page | `8b969a67bbb31df46a30fd60557baab6fa724fb11ea704bc03e9eda1a86f8c9a` |
| fixture-calm-full-page-standalone.png | same, calm on | `36a902ad14eea4ed0c18f2a271c46472e0d77953ac2d691a58bab4628b8db8e9` |
| builder-working-72-frame-a-standalone.png / -b | two frames 500 ms apart | `3e3f7793f526324fe7b1db82676a1cc99d8aed034815afeb96ff4e1fa7f1eaed` / `6b7cbf42ad3272bba41f127a8e98b8157f173d2dda45ac2f5154e63fb9d473ee` |
| arbiter-blocked-72-reduced-motion-standalone.png | reduced motion emulated, blocked selected | `38da0b734c5b49fb395068161072b85856be825220e1546798ae84471f19bf07` |
| matrix-49-static-phosphor-72px-standalone.png | the fixture's static matrix with its text headers | `5ab871d2accae739a51253d80f7c6c8136e740e27668fe86ff865a7468c1c88b` |
| palette-pairs-phosphor-vs-sticker-72px-standalone.png | the fixture's palette pairs | `5e2bd69c92f91e45c9666f099c61ae9b3ce6992af25e59835066ffb2c72757b1` |
| run-log.json | the standalone run's diagnostics | `2e171621938a67d97700218b47bbffe0633e0dc7f915498fb04c0802035b8750` |

**Unverified.** Everything CDH-0002 asks to be observed natively in motion: native playback of the 49 modes, native calm, native reduced motion, native font rendering of the cast, matte halos on both surfaces in the canvas, seams and pivots under the canvas's own zoom. All blocked by CW1, not by a missing capability of the canvas or the browser pane: the canvas renders every other board and the text panels of board 10 natively. Target-Mac CPU, memory, frame timing and background work: Codex-measured only.

**Proposed rulings (recommendations for Michou, not decisions).**
- CW1: take. A separately authorized Codex revision (CDH-0003, or CDH-0001 reopened as a revision) that rebuilds board 10 from the same seven SVGs and `characters.css` as native artboard markup, keeping the fixture as the profiling harness. Then CDH-0002 reruns against the new source digest.
- CW2: take, in the same revision.
- CW3: take, in the same revision.
- CW4: Michou's taste; rule either way before the revision so it is done once.
- CW5: Michou's taste; same.
- CW6: no action; closed by HANDOFF-0041.
- Also awaiting a ruling, outside this review's findings: Codex's proposed diffs to `docs/readers/cockpit-design.md`, `docs/readers/cockpit-design-chatgpt.md` and `tools/review/design-prompt.md` (section "Proposed reader and reviewer updates, not applied" of its report), which retire the pixel constraints in the readers. Cowork can apply them on his word.

This verification is of the CDH-0001 delivery only. It is not Michou's design approval; HANDOFF-0036 stays open to his final word.
