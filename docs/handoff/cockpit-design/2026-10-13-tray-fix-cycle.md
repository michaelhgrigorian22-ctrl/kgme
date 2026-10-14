---
id: CDH-0010
type: handoff
created: 2026-10-13T16:40:00-07:00
from: michou
to: cowork
tier: 2
status: done
adopted_by: michou
adopted: 2026-10-13T20:26:00-07:00
completed: 2026-10-13T20:40:00-07:00
rulings: "take all six (Michou, 2026-10-13 20:26)"
depends_on: [CDH-0008]
design_track: HANDOFF-0036
---

# CDH-0010: The tray, cycle 2 — AUDIT-CDH-0008's findings applied

## Why

AUDIT-CDH-0008 (Codex, 2026-10-13 15:54) returned `BLOCK: 3 blocking findings` on the active-runs tray at `5182d6a`: F1 the focused row's muted text on the focus tint is 4.43:1; F2 board 6's `stale` summary under the grey filter is 2.9:1; F3 the tray's actions are spans and divs, not buttons. Three advisories: F4 the transient-with-blocking-chip sample is not explained by the written rule; F5 `2 working · 1 transient · 1 quiet` reads like four runs; F6 calm with the tray mounted was not observed natively. The design loop (`docs/readers/cockpit-design.md`) has Michou rule take, reject or defer on each, then Cowork edits and commits a cycle. This handoff is that cycle, ready for his rulings.

## Do, finding by finding (Cowork's recommendation in brackets; Michou's ruling replaces it)

1. **F1 [take].** `.tr-focus .tr-run, .tr-focus .tr-l2 { color: #7a8d9b }` in `Tray.dc.html`: 5.1:1 on `#0e1a22`. The timeline's own focused rows share the pair and are out of this scope; note it in the report for a later cycle.
2. **F2 [take].** `.tr-stale .tr-sum { color: #cfe6ef }`: board 6's filter (`saturate(.12) brightness(.72)`) brings it to 7.7:1 on the ground; the muted word is dropped because the whole slot is already greyed by the page. The rest of board 6's header has the same pre-existing failure; note it.
3. **F3 [take].** The three row templates become `<button type="button" class="tr-row …">` with an `aria-label` carrying the row's facts; the collapsed bar becomes a `<button class="tr-open">` labelled "open the active runs pane"; `Esc closes` becomes a button; `:focus-visible` gets a 2 px cyan outline. Still a drawing: no handlers; the keys stay with HANDOFF-0037.
4. **F4 [take].** One sentence in both anatomy copies (board 11 and board 1's sheet): "an exhausted retry that names a time stays `transient`: the run is parked, not halted; the event's own chip keeps its class". The station's lifecycle code already does this.
5. **F5 [take].** The summary reads `2 working (1 quiet) · 1 transient`; the tray's `summarize()` and the station's agree.
6. **F6 [take].** Open board 3's Tweaks in the review copy, toggle `calm`, capture before and after with both tray instances mounted (portraits hidden, words kept, geometry unchanged); captures under `logs/scratch/design-review/cdh-0010/`.
7. Commit `design: tray cycle 2, AUDIT-CDH-0008 F1–F6 (CDH-0010)`, republish the review copy, write `docs/audit/cockpit-design/cdh-0010-implementation.md`, mark this file done, and set the Codex queue row for the re-review (`CDH-0011`, which also covers the station) to `ready` with the sha.

## Acceptance

Codex's re-review finds F1–F3 closed by measurement and source; the focused row, the stale slot and every action are readable and semantic; calm is observed natively with the tray mounted.
