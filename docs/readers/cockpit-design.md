---
id: READER-COCKPIT-DESIGN
type: note
status: active
created: 2026-10-09T21:50:00-07:00
modified: 2026-10-09T22:55:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — the cockpit design canvas, and how to work on it together

*Written 2026-10-09 by Cowork for Michou, Claude Code, and the Codex reviewer (GPT-6 Astra). This is the context a cold reader needs before touching `docs/design/cockpit-v0/`. The design itself is HANDOFF-0036; the code that will be built from it is HANDOFF-0037.*

## What is in `docs/design/cockpit-v0/`
Eleven plain files, all hand-written by Cowork from Michou's brief and the wishlist (`memory/notes/cockpit-wishlist.md`): `canvas.json`, the index, and ten `.dc.html` artboards. They are the **source** of the design. The page at claude.ai (the "KGME Cockpit v0" canvas) is only a viewer and editor over the same files; when the two differ, the repository wins, and Cowork republishes the viewer from here. These are not generated bundles (ADR-017 forbids committing those); they are the drawing.

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

## The one rule
**Signal in the centre, noise at the edges, and noise never carries information.** Everything outside the three columns (frame, tick rails, micro-labels, scanlines, vignette, sweep) and every sprite is decoration that mirrors a fact already shown in text. Therefore the `c` key and `prefers-reduced-motion` can remove or freeze all of it without loss. A finding that a decorative element carries a fact nowhere else on screen is `blocking`; a finding that a fact is shown only by colour is `blocking` (ADR-016 vocabulary, see below).

## Decided (by Michou, 2026-10-08 and 09)
- Palette, phosphor + neon: ground `#0a0c10`, surface `#11151c`, rule `#1e2a33`, text `#cfe6ef`, muted `#6f8290`, cyan `#39d0ff` (focus, live, frame), magenta `#ff3d7f` (blocking and refused only), amber `#ffb02e` (pending, transient, advisory), green `#4de38a` (ok, approval). Sprite extras: hat `#8fb4c4` in phosphor; a sticker palette for two places only.
- Type: JetBrains Mono everywhere, dense, 22 px rows; 9 px only for repeated labels.
- The frame carries system state: cyan live, magenta flood on blocking or halt, amber strip while an intent awaits its outcome, grey static when disconnected.
- Keys: `j`/`k` move, `g`/`G` ends, `Enter` detail, `Esc` back, `u` parent, `Tab` pane, `f` follow, `/` filter line with `run:` `kind:` `job:`, `1`–`4` class toggles, `0` all, `r` run filter, `t` trace, `o` open intents, `x` clear, `c` calm, `p` payload, `w` wall, `?` keys. Reserved for Phase 2, dashed and unbound: `b` `/btw`, `m` model, `y`/`n` approve, `;` command, `Space` queue.
- ADR-016 strikes as three boxes filling per cycle, magenta on halt.
- Sprites, as first decided: one per `actor` (not per model), 24 × 24, original line work, two frames per mode at most, the accent colour is the row's class colour, phosphor in the timeline, sticker palette only in the detail pane header and the Phase 2 model selector. Mapping in `kgme.toml [sprites]`, first rule wins, `default = "stranger"`. "Outrageous, but it retains all the darkness" is the brief for them.
- Wishlist's empty sections stay empty for v0.
- **Superseded 2026-10-09, design session (CDH-0001):** the sprite direction moved from 24 × 24 pixel art to original vector characters, 240 × 280 source, six material roles, cel-shaded, static in the matrices and animated only in the selected detail; see `docs/design/cockpit-v0/chibi/README.md`. The actor mapping, the two-palette rule, the class-colour accent and the noise rule are unchanged. The design track's own handoffs are `CDH-NNNN` under `docs/handoff/cockpit-design/` (HANDOFF-0042 registers them).

## Open (Michou has not ruled)
- Acceptance of the canvas as a whole (HANDOFF-0036's acceptance test: identify the timeline, a run, a failure class and the keyboard focus within ten minutes using only the keyboard map).
- Sticker palette placement: the two allowed spots, or a `sticker` tweak that allows it anywhere.
- Whether "you" should look like you.
- The `mood` tweak for micro-label copy (the "based" set on board 10).
- Every value in the top bar is a sample; the real cockpit reads them. The versions shown are placeholders.

## How to review it (Codex, GPT-6 Astra)
The `.dc.html` format renders only inside the canvas editor; nobody outside it sees pixels. Review the **source**. If PNG exports exist under `docs/design/cockpit-v0/review/` (small ones Michou exports from the canvas page) or `logs/scratch/design-review/` (captures an agent made; disposable, never committed), take them as image input alongside the source; they are the only way to see the result. `memory/attachments/` is the vault's and is never an agent's output directory (ADR-004).

What a design review is for, and the class each finding carries:
- a fact shown only by colour, or a decorative element that carries a fact shown nowhere else → `blocking`
- a key bound twice, a bound key missing from the map, a Phase 2 control without the dashed style and label → `blocking`
- a text/ground pair under 4.5:1 (3:1 at 24 px+), a filled chip with light text → `blocking`
- a `<div>` doing a button's job, an icon-only control without a label, focus shown by colour alone → `blocking`
- a label or chip outside ADR-016's vocabulary (`ok`, `blocking`, `transient`, `advisory`, plus status `refused`, `pending`) → `advisory`
- inconsistency between boards (a token, a key hint, a row layout that differs without reason) → `advisory`
- anything in the sprite generator that would not survive as a standalone SVG under 3 KB → `advisory`
- taste → `advisory`, stated as such; Michou's taste is the spec, the reviewer's is a suggestion
- whitespace, typos → `cosmetic`

What is not a finding: that the files exceed ADR-015's 300-line guide (artboards are drawings, exempt by HANDOFF-0036); that the `.dc.html` syntax (`<x-dc>`, `<sc-for>`, `{{holes}}`, `DCLogic`) is unfamiliar, it is the editor's format; that sample data is sample data.

The prompt that says all this to the reviewer is `tools/review/design-prompt.md`. First pass, from the repository root, Michou's terminal:

```
codex exec -s read-only -m gpt-6-astra "$(cat tools/review/design-prompt.md)" > logs/scratch/design-review-cycle-1.md
```

Then Claude Code, on Michou's word, turns the scratch file into `docs/audit/AUDIT-NNNN-design-review-cockpit-v0-cycle-N.md` with report frontmatter, and records the cycle as a ledger note on `design:HANDOFF-0036`.

## How to iterate (the loop, for a drawing)
1. Astra's findings land in the audit file. Michou reads them and rules: take, reject, or defer each, in one message to Cowork.
2. Cowork edits the files under `docs/design/cockpit-v0/` (or Claude Code does, on a handoff), commits with `design: cockpit v0, cycle N (HANDOFF-0036)`, and republishes the canvas viewer from the committed files, so the page and the repository stay the same thing.
3. Michou can also edit on the canvas page by hand; when he does, Cowork reads the page back, commits those changes, and republishes nothing. The repository is still the truth; the edit just arrived through the viewer.
4. Acceptance closes the handoff: Michou records an `approval` event naming the committed tree (`kgme ledger note --kind approval …`, flags per `kgme ledger note --help`, summary `design: cockpit v0 approved at <short sha>`), and 0036 goes to `done`. 0037 builds from that sha and nothing else.

## For Michou's further requests to Astra
Point it at this reader first, then the folder, then ask the question. Good questions for it: "which of these boards would not survive reduced motion," "where does the keyboard map contradict the boards," "what would a screen reader say on board 4," "rewrite the voice panel in the same register but shorter," "propose a sprite for a Kimi harness within the rules." Bad questions: "make it look better" (taste is Michou's), "render it" (it cannot), "approve it" (only Michou does).
