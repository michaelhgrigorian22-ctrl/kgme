---
id: CDH-0016
type: handoff
created: 2026-10-15T23:08:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0014, CDH-0015]
design_track: HANDOFF-0036
---

# CDH-0016: Read-only review of the station's third cycle and the rubric checks

## Outcome and authority

An independent, read-only review on branch `design` of CDH-0015 (AUDIT-CDH-0013's F1–F6 applied) and CDH-0014 (the six rubric checks), at the sha their reports name. Codex's reviewer role only. This is the first review under the rubric cited in `tools/review/design-prompt.md`: findings may name a rule id and a row, and still carry one ADR-016 class. Adopted when the queue prompt starts Codex and this row is the first `ready` one; Cowork marks it `ready` when both handoffs are `done`.

## Do

1. From `~/Projects/Automate-design` on `design`, review by `tools/review/design-prompt.md` with the captures under `logs/scratch/design-review/cdh-0014/` and `cdh-0015/` as image input (earlier folders are labelled historical). Headless Chromium from the repository files if the sandbox allows; otherwise source, evaluation and captures, and say so.
2. For CDH-0015: F1 by evaluation of the shared halt rule (halt then ordinary note; halt then approval; the exhausted retry), F2 by the resize path and the standalone `c`-resize-`c` captures, F3 by one wording in three places, F4 by the hashes on disk against AUDIT-CDH-0012's corrected table, F5 by `validate_event` over the 42 synthetic records, F6 by the accessibility tree.
3. For CDH-0014, each check against its rule: `contextual-live-badge-updates` (ux-guidelines 118): one status region, atomic, meaningful text, focus unmoved; `focus-not-obscured` (100) and sticky navigation (2): focused rects clear of the header and the HUD at 1440 and 400; `auto-rotation-controls` (108): the pause control, its name, its reduced-motion default; `web-target-size` (104): every button 24 × 24 CSS px or a documented exception; WCAG 2.1.4: board 7's sentence and the station's editable-target guard; `stacks/threejs.csv` rows 1–9: each met, not applicable or changed, as the report records.
4. Then the usual gates: every fact in words, contrast, read-only, nothing remote but the pinned package and the repository's files, the cast unchanged.
5. Write `docs/audit/cockpit-design/cdh-0016-design-review.md`: `id: AUDIT-CDH-0016`, `handoff: CDH-0016`, `author: codex`, `source: inferred`, the reviewed sha, the three sections.

## Closeout

Set this file `done` with `completed:`, the queue row `done`, and commit your three delivery files by pathspec as the queue prompt says. Findings return to Michou.
