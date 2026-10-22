---
id: CDH-0018
type: handoff
created: 2026-10-16T00:08:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: done
completed: 2026-10-21T01:32:35-07:00
report: docs/audit/cockpit-design/cdh-0018-design-review.md
adopted_by: michou
adopted: 2026-10-21T01:26:15-07:00
depends_on: [CDH-0017]
design_track: HANDOFF-0036
---

# CDH-0018: Read-only review of the open list's cycle

## Outcome and authority

An independent, read-only review on branch `design` of CDH-0017 at the sha its report names: the three checks (CW17, CW18, CW22), the four decided builds (bubbles beside the crew, the hull's key, the deck's framing, the calm grid) and the recorded scores. Codex's reviewer role only; under the rubric cited in `control/review/design-prompt.md` and ADR-023 (`git show main:CLAUDE.md`, "How decisions are made"). Adopted when the builder prompt starts Codex and this row is the first `ready` one.

## Do

1. From `~/Projects/KGME/design` on `design`, read `docs/readers/cockpit-design-lessons.md` first, then review by `control/review/design-prompt.md` with the captures under `logs/scratch/design-review/cdh-0017/` as image input.
2. Judge CW17 and CW18 by the contrast arithmetic on the actual cascade (boards 3, 4, 5, 9 focused rows; board 6 under its filter, its own text and the mounted tray's), CW22 by the buttons' boxes, the four builds by source and captures, and the README's "Open list, scored" for a recorded score on every open item and a recommendation on each item left for Michou.
3. Then the usual gates. Write `docs/audit/cockpit-design/cdh-0018-design-review.md` with the three sections.

## Closeout

Set this file `done` with `completed:`, the queue row `done`, and commit your three delivery files by pathspec. Findings return to Michou only where ADR-023 says they must; the rest are the next cycle's.
