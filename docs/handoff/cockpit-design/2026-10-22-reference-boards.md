---
id: CDH-0027
type: handoff
created: 2026-10-22T02:10:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0023, CDH-0026]
design_track: HANDOFF-0036
---

# CDH-0027: The reference boards and the remaining cuts

## Outcome and authority

This is the last row of the coordinated redesign: the remaining items of AUDIT-CDH-0022's table, all scored below 1.5 and decided by Cowork, each on the approval screen. The reference boards (1, 7, 10, 11) keep their side-by-side density, which is their job. What goes is prose that repeats across boards. No fact is removed: each cut text survives once, in its home.

Cowork's native pass of CDH-0026 is done (AUDIT-CDH-0024-0026-REVIEW, PASS), so this row is `ready`. It also carries that review's CW34 and CW35.

## Do

1. **Board 1, Components.**
   - One complete statement of the noise rule, not several (0.2). Its micro-label specimen says a micro-label carries no fact, replacing "repeats facts shown elsewhere" (CW32, AUDIT-CDH-0023-0025-REVIEW, 0.2).
   - The noise specimen beside its calm explanation as one before/after (0.4).
   - One cross-component specimen: a selected event with its frame, glyph, text and tray role aligned, replacing separate duplicated examples (0.6).
2. **Board 2, Empty.**
   - One "nothing recorded yet" area holding the zero counts and the three ways events start (0.4).
   - The four vacant auxiliary panels lose their visual weight (0.4).
   - The full event-shape field list goes under the advertised `Enter` detail (0.4).
   - A single dormant first-event cursor aligned to the future timeline replaces the blank matrix, keeping every zero/no-reading fact (0.6).
3. **Boards 4, 5 and 6: repeated prose.**
   - One actionable HALT sentence plus the state label (0.6).
   - The 1m34 waiting time once, with short mirrors only where navigation needs them (0.4).
   - The write-ahead explanation under `Enter` detail (0.6).
   - Decorative jitter removed while calm (0.2).
   - Board 6's stale alert rounds its segment count (`Math.round(value / 5)`), so no value shows a fraction (CW35, AUDIT-CDH-0024-0026-REVIEW, 0.1).
4. **Board 8, Phase 2.**
   - Arrange approval, model and command around one explained future interaction (0.9).
   - Use the guard and the arbiter to show request versus ruling in it (0.8).
   - Duplicate "not yet bound" prose goes; every control keeps its explicit label (0.2).
   - The footer gains "? keys + system" like boards 2–6, since board 8's system facts now live in board 7's Phase 2 state (CW33, 0.3).
   - Nothing activates.
5. **Board 10, Sprites.**
   - Prose duplicated with board 1 goes, each mapping and constraint kept once (0.2).
   - The selected figure and its actual 24 px portrait in one comparison (0.4).
   - The selected role's existing event example aligned with its portrait and detail pair (0.6).
   - No new character and no likeness.
6. **The station's room chips (CW34, AUDIT-CDH-0024-0026-REVIEW, 2 × 0.3 = 0.6).** The latest-event line CDH-0026 added made the widest chips grow from 222 px to 257 px, and at 800 × 600 two pairs overlap (Workshop over Dock, Review chamber over Archive) where version 11 had none. Keep the chip inside its former width budget: clip the latest-event line with an ellipsis at about 220 px, the full text staying in the chip's accessible name, the pane's dispatch line and the calm wall. Verify chip-to-chip overlaps at 400, 800 × 600 and 1440 (`logs/scratch/design-review/cdh-0024-0026-native/chips26.py` is the measurement): none at any width.
7. **Board 11 and the host trays.**
   - The lifecycle essay stays on board 11 only (0.2).
   - The opened `a` pane carries the full lifecycle and latest-event explanations instead of the compact header (0.6).
   - Full run IDs and elapsed/event detail go behind `a` and `Enter`, compact counts staying visible (0.6).

## Verify

- A source check that every cut string survives once in its stated home.
- The CSS fixture at 1440 (board 1 at 1900 tall, board 10 at 1500).
- `make check` green.

Report, close out and commit as for CDH-0023.

## Acceptance

- Each fact has one home.
- The reference boards still compare side by side.
- The operating boards read faster.
- Contrast, targets, focus and calm hold.
