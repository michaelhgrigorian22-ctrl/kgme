---
id: CDH-0022
type: handoff
created: 2026-10-22T00:40:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0022: Read-only review of the full UI against the design philosophy

## Outcome and authority

Michou asked for this review on 2026-10-22 at 00:03: "maybe a codex review of the full UI at this point could be in order while we wait for claude code on substantive." It's an independent, read-only review of the whole cockpit canvas on branch `design`:
- the 11 boards, including the tray (board 11) mounted on the host boards;
- the cast;
- the station.

The design source is at `3937854`. The boards are unchanged since `0618fa5`, and the station since `bab44b5`.

It judges by `control/review/design-prompt.md` and its rubric, as every review does, and above all by the design philosophy Michou set at 00:03 for every component going forward. That philosophy now heads the reader's Decided list (`docs/readers/cockpit-design.md`):

> "the maximalism here is that the sum of all parts is something almost absurdly extra but in a useful and creative and unexpected but welcome way. that doesnt mean clutter and more for less."

Maximalism is never read literally, as a screen so cluttered the operator can't act.

This row is Codex's reviewer role only. The review row is adopted when the builder prompt starts Codex and this row is the first `ready` one.

## Do

1. **Read first,** from `~/Projects/KGME/design` on `design`:
   - `docs/readers/cockpit-design-lessons.md`;
   - `docs/readers/cockpit-design.md`, especially the philosophy, the one rule and the Decided list;
   - `control/review/design-prompt.md`;
   - the README's "Open list, scored", so you don't re-raise what's already decided.
2. **Review sources and images.**
   - Read the source under `docs/design/cockpit-v0/`: every `.dc.html` board, `chibi/` and `station/`.
   - Use as image input the 11 board captures and the canvas overview under `logs/scratch/design-review/cdh-0022/`. Cowork took them natively from review copy version 30, at each board's design size. They are downscaled to 800 px wide, so read exact text in the source; its `manifest.json` names each file.
   - Render the station yourself, deck and calm, at 1440, 2560 and 400. Use `sh logs/scratch/vendor/make-local.sh`, serve `logs/scratch/vendor/` on 127.0.0.1, and open `station-local.html?at=19:52:00&speed=1`.
3. **Judge three things.**
   - **The philosophy, board by board and across the whole canvas:**
     - Name each element that doesn't earn its place: one the operator doesn't use, that doesn't delight, or that repeats another. Repeated key hints, micro-labels, panels and ornament are the usual suspects.
     - Name the places where the sum already is absurdly extra in a useful way, so they're kept.
     - Name where one change would make a board more extra while making it less cluttered: an unexpected, welcome touch that replaces two ordinary ones.
     - No fact may be removed (the one rule). Moving a fact behind a key the board already has is allowed.
   - **The usual rules:** the one rule, the Decided list, ADR-016's vocabulary, contrast, keyboard, and the rubric.
   - **Coherence across boards:** the same thing drawn the same way everywhere (headers, footers, key hints, the tray, chips, the frame), and nothing contradicting the station's rules.
4. **Score every judgement call** under ADR-023 (stakes × edge).
   - Below 1.5: recommend it, and say what you'd build.
   - At or above 1.5: put it in one batched brief for Michou at the end of the report, with a recommendation each.
5. **Write the report** under `docs/audit/cockpit-design/` as the design review for CDH-0022, with the design prompt's three sections. Add two things to the Notes:
   - a per-board table: board, keep, cut, merge, move behind a key, add, each with its score;
   - a short "the sum" paragraph on what the whole canvas does that no single board does.

## Closeout and what happens next

- Close out as for every review row: this file `done` with `completed:` and `report:`; the queue row `done`; the report, this file and the README committed by pathspec.
- If the review finds `blocking` findings, the fix loop applies them as usual.
- The philosophy's cuts and additions are a coordinated redesign, not fixes. Don't build them in the fix loop. Cowork turns them into build rows once Michou has seen the items at or above 1.5. Findings go to Michou only where ADR-023 says they must.
