---
id: CDH-0011
type: handoff
created: 2026-10-13T16:42:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: done
completed: 2026-10-14T00:28:17-07:00
adopted_by: michou
adopted: 2026-10-14T00:19:27-07:00
depends_on: [CDH-0009, CDH-0010]
design_track: HANDOFF-0036
---

# CDH-0011: Read-only design review of the station and the tray's second cycle

## Outcome and authority

An independent, read-only review of two things on branch `design`: the station (CDH-0009, `docs/design/cockpit-v0/station/`, at `373de74` or the sha CDH-0010's report names if later) and the tray's second cycle (CDH-0010, boards 1, 3, 4, 5, 6, 9 and 11, at the sha its report names). Codex's reviewer role only. Adopted when Michou pastes `tools/review/codex-queue-prompt.md` into Codex and this row is the first `ready` one in the README's Codex queue; Cowork marks it `ready` when CDH-0010 is `done`.

## Do

1. From `~/Projects/Automate-design` on `design`, review by the rules and format of `tools/review/design-prompt.md`, with the captures under `logs/scratch/design-review/cdh-0009/` and `cdh-0010/` as image input. The station is a hand-built page, not an artboard: judge `station/index.html` and `station/sample-events.jsonl` as source, and its README as its statement of intent. Open the page in headless Chromium from the repository files if your sandbox allows (serve `docs/design/cockpit-v0/` over HTTP; the page loads `three@0.182.0` from jsDelivr, so it needs network); if not, say so and judge from source and captures.
2. Judge specifically, for the station: that every fact the scene shows is also a word or a number in a chip, a bubble or the HUD (lifecycle words, counts, quiet, the refusal, the halt), and that light adds no fact of its own; that the sample ledger lines are valid ADR-019 event v1 shapes with every field, monotonic ids and no raw bodies; that the lifecycle rules in the README match the code and board 11's text after CDH-0010; that calm drops to a page where nothing is lost; that reduced motion removes the bloom, the walks and the fades; that the page is read-only (no handler dispatches, approves or chooses a model) and loads nothing remote but the one pinned script and the repository's files; that the cast is read from the canonical SVGs unchanged; that the reel references were used for the interaction pattern only. Contrast as before: text 4.5:1 on its ground, including the HUD over the deck, chips over the scene and bubbles.
3. For the tray's second cycle: that F1, F2 and F3 of AUDIT-CDH-0008 are closed by measurement and source, F4 and F5 by wording, and F6 by the native calm captures; and that nothing else moved.
4. Write `docs/audit/cockpit-design/cdh-0011-design-review.md`: `id: AUDIT-CDH-0011`, `handoff: CDH-0011`, `author: codex`, `source: inferred`, the reviewed shas, and the three sections, with the station's and the tray's findings in one table, prefixed `S` and `T`.

## Closeout

Set this file `done` with `completed:` and the queue row `done`. Findings return to Michou; Cowork commits.
