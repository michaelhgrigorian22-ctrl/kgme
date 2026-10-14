---
id: CDH-0012
type: handoff
created: 2026-10-14T00:50:00-07:00
from: michou
to: cowork
tier: 2
status: done
adopted_by: michou
adopted: 2026-10-14T00:41:00-07:00
completed: 2026-10-14T01:45:00-07:00
rulings: "commit and keep working (Michou, 2026-10-14 00:41): blocking findings are taken by default; S7's threshold is Cowork's default pick until Michou says otherwise"
depends_on: [CDH-0011]
design_track: HANDOFF-0036
---

# CDH-0012: The station, cycle 2 — AUDIT-CDH-0011 applied, and the tray's T1

## Why

AUDIT-CDH-0011 (Codex, 2026-10-14 00:23) returned `BLOCK: 6 blocking findings` on the station at `373de74` and closed the tray's F1–F6 at `4f3e06c` with one advisory, T1. Michou's standing ruling of 00:41 ("it should honestly just commit and keep working in these situations") replaces the per-finding take/reject/defer round for blocking findings: Cowork applies them as the next cycle at once and Michou vetoes after the fact; only taste and deferrals wait for him. This handoff is that cycle.

## Do, finding by finding

1. **S1 [take].** One textual snapshot feeds the chips, the pane and the wall: system and replay context (clock, ledger line, session, harnesses, following), an explicit hull field (`nominal` or `HALT · <note>`), each room's state line, each run's row, and the fixtures' last events (the bridge's last human note, the airlock's last refusal, the review chamber's last ruling), kept as text after their bubbles fade. Calm no longer covers the HUD: the wall sits under it. Verify calm at the refusal, the human note and a synthetic halt, including after a newer event.
2. **S2 [take].** `waiting` is the newest op being an intent with no outcome, whichever its `parent`; a blocking note halts a run only until it moves again (a later intent or outcome), which is what board 11 already says ("has not moved since"). Keep the exhausted-retry exception and the recorded class. Verify the four root intents and a blocking-note-then-resume sequence by source evaluation.
3. **S3 [take].** `aria-hidden` moves from `#stage` to the WebGL canvas and the crew artwork (portraits, tags, bubbles, whose facts live in the rows); the seven room buttons stay exposed with their state in their accessible name.
4. **S4 [take].** Pane and wall rows are keyed by run (and room) and updated in place; nothing focused is removed on a refresh. The painted `.focus` is the drawing's default on the first row only while no row has real focus; a really focused row shows the same treatment.
5. **S5 [take].** Every muted descendant of a focused station row reads `#7a8d9b` (5.14:1): the run id, the second line, the quiet suffix, the `—` chip.
6. **S6 [take].** The three Google Fonts tags go; the font stack falls back to the system monospace. The page loads the pinned three.js package and the repository's files, nothing else; the README says so and the network list is checked.
7. **S7 [take, Cowork's default].** One quiet threshold in both anatomy copies, the station README and the code: the run's median gap between intents, never under three minutes; with fewer than two intents, three minutes. (First written here as three times the median; changed during the cycle because that contradicts board 3's own drawn sample, see AUDIT-CDH-0012.) Michou may change it.
8. **S8 [take].** The reduced-motion preference is observed live (bloom pass added or removed, walks and camera snap); calm skips the walks and the camera as well as the two renders.
9. **S9 [take].** Fresh standalone captures from the committed source with the served sha, wrapper and viewport recorded; the two earlier captures are labelled historical and their differences explained.
10. **T1 [take].** The tray's button reset drops to zero specificity (`:where`), the focused-row colour override moves after the base rule and covers the quiet suffix and the muted chip; the focus tint survives hover. Remeasure the focused pairs.
11. Commit `design: station cycle 2 and tray T1 (CDH-0012)`, republish both review artifacts, write `docs/audit/cockpit-design/cdh-0012-implementation.md`, mark this file done, and set the Codex queue row for the re-review (`CDH-0013`) to `ready` with the sha.

## Acceptance

Codex's re-review finds S1–S6 and T1 closed by source and measurement, S7 by one written threshold in three places, S8 by source, S9 by labelled evidence; calm shows every fact the deck shows.
