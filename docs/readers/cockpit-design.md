---
id: READER-COCKPIT-DESIGN
type: note
status: active
created: 2026-10-09T21:50:00-07:00
modified: 2026-10-22T02:15:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — the cockpit design canvas, and how to work on it together

*Written 2026-10-09 by Cowork for Michou, Claude Code, and the Codex reviewer (GPT-6 Astra). This is the context a cold reader needs before touching `docs/design/cockpit-v0/`. The design itself is HANDOFF-0036; the code that will be built from it is HANDOFF-0037.*

## What is in `docs/design/cockpit-v0/`
The original 12 core files were hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and 10 `.dc.html` artboards. CDH-0001 adds the reusable `chibi/` SVG sources, shared motion layer, standalone fixture and README. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.

| File | Board | What it shows |
|---|---|---|
| `Components.dc.html` | 1 | palette, type scale, frame states, row anatomy, chips, resource bar, strike boxes, keys, the noise furniture |
| `Empty.dc.html` | 2 | the timeline with zero events and the three ways events start |
| `Main.dc.html` | 3 | live: events arriving, the entry board |
| `Blocking.dc.html` | 4 | a `blocking` outcome and a halt: magenta frame, strike boxes full, detail pane open on the halt note |
| `Pending.dc.html` | 5 | an intent with no outcome yet: amber strip, open-intents panel, reconciliation explained |
| `Disconnected.dc.html` | 6 | server unreachable: grey static, snapshot, the modal with the facts |
| `Keys.dc.html` | 7 | the keyboard map, bound keys solid, Phase 2 keys dashed |
| `Phase2.dc.html` | 8 | `/btw` lane, model selector, approvals, dispatch, queued-message buffer, VS Code follow, all dashed and labelled Phase 2 |
| `Wall.dc.html` | 9 | the four-column layout for an external monitor, with the raw vendor stream |
| `Sprites.dc.html` | 10 | the cast: one sprite per `actor`, seven modes, two palettes, the rules |

CDH-0001 implemented the reusable cast; CDH-0002 found the native iframe failure. Michou separately adopted CDH-0003 for Codex to rebuild board 10 as self-contained native markup; Cowork verifies it under CDH-0004. The scoped implementation exception does not change the independent read-only reviewer role or grant final design approval.

## The one rule
**Signal in the centre, noise at the edges, and noise never carries information.** Everything outside the three columns (frame, tick rails, micro-labels, scanlines, vignette, sweep) and every sprite is decoration that mirrors a fact already shown in text. Therefore the `c` key and `prefers-reduced-motion` can remove or freeze all of it without loss. A finding that a decorative element carries a fact nowhere else on screen is `blocking`; a finding that a fact is shown only by colour is `blocking` (ADR-016 vocabulary, see below).

## Decided (by Michou, 2026-10-08, 09 and 22)
- Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` (focus, live, frame), magenta `#ff3d7f` (blocking and refused only), amber `#ffb02e` (pending, transient, advisory), green `#4de38a` (ok, approval). Sprite extras: hat `#8fb4c4` in phosphor; a sticker palette for two places only.
- Type: JetBrains Mono everywhere, dense, 22 px rows; 9 px only for repeated labels.
- The frame carries system state: cyan live, magenta flood on blocking or halt, amber strip while an intent awaits its outcome, grey static when disconnected.
- Keys: `j`/`k` move, `g`/`G` ends, `Enter` detail, `Esc` back, `u` parent, `Tab` pane, `f` follow, `/` filter line with `run:` `kind:` `job:`, `1`–`4` class toggles, `0` all, `r` run filter, `t` trace, `o` open intents, `x` clear, `c` calm, `p` payload, `w` wall, `?` keys. Reserved for Phase 2, dashed and unbound: `b` `/btw`, `m` model, `y`/`n` approve, `;` command, `Space` queue.
- ADR-016 strikes as three boxes filling per cycle, magenta on halt.
- Sprites under adopted CDH-0001: 1 original smooth, layered SVG per `actor` (not per model), with 6 semantic material roles and restrained cel shading. Use deliberate 24 px portraits in run headers and full 72 px characters in detail headers; the event rows remain 22 px. Each of the 7 modes uses at most 2 authored key poses with interpolated transforms and discrete expression swaps. Accent follows a class or state already written in adjacent text. Phosphor stays in the timeline; sticker stays in the detail header and illustrated Phase 2 model selector. Mapping in `kgme.toml [sprites]`, first rule wins, `default = "stranger"`. "Outrageous, but it retains all the darkness" remains the brief.
- Sprite motion: all dense run portraits and the 49-cell matrix stay static; only 1 selected visible detail may animate. Hidden, offscreen, calm and actual reduced-motion states remove animation work. Calm removes decoration without losing actor, lifecycle, class or event facts or changing row geometry. Modes are not failure classes; fixture controls cannot override reduced motion or bind application keys.
- Sprite evidence: the 24 × 24 source grid, 6 flat fills, 2 hard-swapped frames and 3 KB cap are retired for CDH-0001. The provisional target is 512 KiB raw for all 7 SVG assets plus shared animation code. Report bytes per actor and total, SVG element counts, simultaneous active animations, and 30-second target-Mac captures with 50 static portraits and 1 selected detail, with motion and calm baselines. Record environment, frame intervals, long tasks and interaction observations; label missing measurements unverified. A small file is not proof of runtime performance.
- Wishlist's empty sections stay empty for v0.
- **The design philosophy, for every component going forward (Michou, 2026-10-22):** "the maximalism here is that the sum of all parts is something almost absurdly extra but in a useful and creative and unexpected but welcome way. that doesnt mean clutter and more for less." Maximalism is never read literally, as a screen so full of clutter that the operator can't act. It came with his answer to the brief's first question: he likes the station and the whole vibe, and wants less clutter on screen as the UI is refined across all areas. How the agents apply it until he says otherwise:
  - every element earns its place: the operator uses it, or it delights without getting in the way, and it does not repeat another;
  - the "extra" lives in how the parts combine (character, light, motion, surprise), not in how many there are;
  - decoration and repeated hints are the first candidates to cut, and no fact is ever removed (the one rule).
  It refines 2026-10-08's "almost too much": the brief stays "outrageous, but it retains all the darkness".
- **The station joins board 9's wall (Michou, 2026-10-22):** when the cockpit is built, `w` cycles desk → wall → station.
- **No likeness (Michou, 2026-10-22):** "you" on the bridge stays the chalk silhouette.
- **The compact operating header (Michou, 2026-10-22, B1):** operating surfaces show state and alerts; system context (session, versions, latency, full quotas, origin, ledger file, provenance) lives once, under `?` on desk and wall and under `a` on the station; the corner micro-labels carry no fact.
- **The disconnect band (Michou, 2026-10-22, B2):** a disconnected cockpit shows a persistent band under the header, never a modal, and the last snapshot stays inspectable.
- **Superseded 2026-10-09, design session (CDH-0001):** the sprite direction moved from 24 × 24 pixel art to original vector characters, 240 × 280 source, six material roles, cel-shaded, static in the matrices and animated only in the selected detail; see `docs/design/cockpit-v0/chibi/README.md`. The actor mapping, the two-palette rule, the class-colour accent and the noise rule are unchanged. The design track's own handoffs are `CDH-NNNN` under `docs/handoff/cockpit-design/` (HANDOFF-0042 registers them).

## Open (Michou has not ruled)
- Acceptance of the canvas as a whole (HANDOFF-0036's acceptance test: identify the timeline, a run, a failure class and the keyboard focus within ten minutes using only the keyboard map).
- Sticker palette placement: the two allowed spots, or a `sticker` tweak that allows it anywhere.
- The `mood` tweak for micro-label copy (the "based" set on board 10).
- Every value in the top bar is a sample; the real cockpit reads them. The versions shown are placeholders.

## How to review it (Codex, GPT-6 Astra)
The `.dc.html` format requires the native canvas editor; preserve its support mechanism and templating. The standalone `chibi/preview.html` fixture and SVG assets can be rendered in a browser when tool access permits. Read PNG evidence from `logs/scratch/design-review/`. Review the **source** and distinguish supplied PNG evidence, independently observed browser behavior, measured target-Mac performance and native observations. A fixture screenshot does not establish native canvas behavior. Cowork must import and observe the delivered native board under CDH-0004; any unavailable native capability remains explicitly unverified.

What a design review is for, and the class each finding carries:
- a fact shown only by colour, or a decorative element that carries a fact shown nowhere else → `blocking`
- a key bound twice, a bound key missing from the map, a Phase 2 control without the dashed style and label → `blocking`
- a text/ground pair under 4.5:1 (3:1 at 24 px+), a filled chip with light text → `blocking`
- a `<div>` doing a button's job, an icon-only control without a label, focus shown by colour alone → `blocking`
- a label or chip outside ADR-016's vocabulary (`ok`, `blocking`, `transient`, `advisory`, plus status `refused`, `pending`) → `advisory`
- inconsistency between boards (a token, a key hint, a row layout that differs without reason) → `advisory`
- whether each actor's `<symbol>` in `Sprites.dc.html` matches its file under `chibi/` and whether every mode has adjacent text; use `tests/test_design_sprites.py` to check drift, and classify a lost fact as `blocking`
- an unexplained exceedance of the provisional 512 KiB total sprite-source target, or omitted source-size, SVG-complexity or runtime evidence → `advisory`; never enforce the retired 3 KB cap or treat a byte count as a performance result
- taste → `advisory`, stated as such; Michou's taste is the spec, the reviewer's is a suggestion
- whitespace, typos → `cosmetic`

What is not a finding: that the files exceed ADR-015's 300-line guide (artboards are drawings, exempt by HANDOFF-0036); that the `.dc.html` syntax (`<x-dc>`, `<sc-for>`, `{holes}`, `DCLogic`) is unfamiliar, it is the editor's format; that sample data is sample data.

The prompt that says all this to the reviewer is `control/review/design-prompt.md`. First pass, from the repository root, Michou's terminal:

```
codex exec -s read-only -m gpt-6-astra "$(cat control/review/design-prompt.md)" > logs/scratch/design-review-cycle-1.md
```

Then Claude Code, on Michou's word, turns the scratch file into `docs/audit/AUDIT-NNNN-design-review-cockpit-v0-cycle-N.md` with report frontmatter, and records the cycle as a ledger note on `design:HANDOFF-0036`.

## How to iterate (the loop, for a drawing)
Work in `~/Projects/Automate-design` on branch `design`, never on `main`. Codex reviews only until HANDOFF-0042, except for the explicitly adopted CDH-0001 and CDH-0003 implementation scopes. There are no binaries committed; captures live under `logs/scratch/design-review/` and identify their source hashes. CDH-0003 delivers local files and its report without committing or publishing; Cowork commits by pathspec at the next authorized checkpoint.

1. Astra's findings land in the audit file. Michou reads them and rules: take, reject, or defer each, in one message to Cowork.
2. Cowork edits the files under `docs/design/cockpit-v0/` (or Claude Code does, on a handoff), commits with `design: cockpit v0, cycle N (HANDOFF-0036)`, and republishes the canvas viewer from the committed files, so the page and the repository stay the same thing.
3. Michou can also edit on the canvas page by hand; when he does, Cowork reads the page back, commits those changes, and republishes nothing. The repository is still the truth; the edit just arrived through the viewer.
4. Acceptance closes the handoff: Michou records an `approval` event naming the committed tree (`kgme ledger note --kind approval …`, flags per `kgme ledger note --help`, summary `design: cockpit v0 approved at <short sha>`), and 0036 goes to `done`. 0037 builds from that sha and nothing else.

## For Michou's further requests to Astra
Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules," "inspect the standalone chibi fixture at 24/72 px." Bad questions: "make it look better" (taste is Michou's), "certify the native canvas without observing it," "approve it" (only Michou does).
