---
id: CDH-0005
type: handoff
created: 2026-10-09T23:06:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0006]
design_track: HANDOFF-0036
---

# CDH-0005: Read-only design review of the native board 10

## Outcome and authority

An independent, read-only review of board 10 as rebuilt under CDH-0003 and corrected under CDH-0006 (commit `a27d2f2` on branch `design`, verified natively by Cowork under CDH-0004 and CDH-0006). Codex's reviewer role only (Michou, 2026-10-09 23:13). Adopted when Michou pastes `tools/review/codex-queue-prompt.md` into Codex and this row is the first `ready` one in the README's Codex queue (revised 2026-10-12T17:50:00-07:00).

## Do

1. From `~/Projects/Automate-design` on `design`, review `docs/design/cockpit-v0/Sprites.dc.html`, `canvas.json` and `chibi/` at `a27d2f2`, by the rules and format of `tools/review/design-prompt.md`, with these captures as image input: `logs/scratch/design-review/cdh-0004/` (native, including the brace experiment) and `logs/scratch/design-review/cdh-0006/` (native, after the fix).
2. Judge against AUDIT-CDH-0002 (CW1–CW3 must be resolved) and AUDIT-CDH-0004 (CW7 must be resolved; CW8, CW9 taken), the one rule, the keyboard map (board 7 unchanged), Phase 2 dashing, contrast, and whether each actor's `<symbol>` equals its file under `chibi/` (`tests/test_design_sprites.py` is the mechanical form; cite it). CW4 and CW5 are closed as drawn and are not findings. Taste is advisory and says so.
3. Write `docs/audit/cockpit-design/cdh-0005-design-review.md`: `id: AUDIT-CDH-0005`, `handoff: CDH-0005`, `author: codex`, `source: inferred`, `reviewed_sha: a27d2f2`, and the three sections (Findings with `F` ids, Verdict `PASS` or `BLOCK: N`, Notes).

## Closeout

Set this file `done` with `completed:` and the queue row `done`. Findings return to Michou; Cowork commits the report on `design`. A `PASS` plus Michou's own look at the review copy is what HANDOFF-0036's acceptance test runs against.
