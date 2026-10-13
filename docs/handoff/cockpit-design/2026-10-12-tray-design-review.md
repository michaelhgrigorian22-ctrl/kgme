---
id: CDH-0008
type: handoff
created: 2026-10-12T17:50:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: done
completed: 2026-10-13T15:54:51-07:00
adopted_by: michou
adopted: 2026-10-13T15:49:46-07:00
depends_on: [CDH-0007]
design_track: HANDOFF-0036
---

# CDH-0008: Read-only design review of the active-runs tray

## Outcome and authority

An independent, read-only review of the active-runs tray drawn under CDH-0007, at the commit CDH-0007's report names on branch `design`. Codex's reviewer role only. Adopted when Michou pastes `tools/review/codex-queue-prompt.md` into Codex and this row is the first `ready` one in the README's Codex queue; Cowork marks it `ready` when CDH-0007 is `done`.

## Do

1. From `~/Projects/Automate-design` on `design`, review boards 1, 3, 4, 5, 6, 7 and 9 under `docs/design/cockpit-v0/` at the named commit, by the rules and format of `tools/review/design-prompt.md`, with the captures under `logs/scratch/design-review/cdh-0007/` as image input.
2. Judge specifically: that no fact in the tray is shown only by portrait or colour (count, lifecycle word, `quiet`, `stale` and class chips all in text); that `a` is on board 7's map once and collides with no bound key; that the tray adds no animation and vanishes correctly under calm (text stays) and disconnection (`stale`); that the expanded pane's rows carry actor, run, lifecycle, elapsed and latest event in text; that nothing Phase 2 sits inside the tray; and consistency with the run headers of board 3 and the portraits of board 10.
3. Write `docs/audit/cockpit-design/cdh-0008-design-review.md`: `id: AUDIT-CDH-0008`, `handoff: CDH-0008`, `author: codex`, `source: inferred`, the reviewed sha, and the three sections.

## Closeout

Set this file `done` with `completed:` and the queue row `done`. Findings return to Michou; Cowork commits.
