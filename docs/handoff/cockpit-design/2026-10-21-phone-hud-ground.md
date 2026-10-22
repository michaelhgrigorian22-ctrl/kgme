---
id: CDH-0021
type: handoff
created: 2026-10-21T20:20:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0021: The phone HUD takes the ground (CW27)

## Outcome and authority

A build row under CDH-0019's mandate: AUDIT-CDH-0020-REVIEW CW27, scored 2 × 0.3 = 0.6 and decided (ADR-023); it also goes on the README's approval-screen list. Below 721 px the two HUDs cover most of the screen and have no ground in deck mode, so the deck's room chips, crew tags and bubbles show through the HUD's words (13 of 15 on-screen labels under a HUD box at 320, 15 of 18 at 400). The station's rule is that every fact reads as words; on a phone the words win. Adopted when the builder prompt takes this row as the first `ready` one.

## Do

1. In `docs/design/cockpit-v0/station/index.html`, inside the existing `@media (max-width:720px)` block, give both HUDs the ground, as calm already does: add `background:var(--ground)` to that block's `.hud` rule. Nothing changes at 721 and above, and nothing else in the file changes. No board mirrors the station's HUD (AUDIT-CDH-0020), so touch no board.
2. Verify standalone with the real page, as for CDH-0020: `sh logs/scratch/vendor/make-local.sh`, serve `logs/scratch/vendor/` on 127.0.0.1, open `station-local.html?at=19:52:00&speed=1` in headless Chrome at 320, 360, 400, 720, 721 and 1440, deck and calm, paused with the page's own control.
   - Both HUDs' computed `background-color` is `rgb(10, 12, 16)` at 320–720 and stays transparent at 721 and 1440 in deck mode.
   - Every HUD fact string, the summary's right edge (304 / 344 / 362.156 / 362.156 / 463.172 / 463.172 px) and the calm grid (1 / 1 / 1 / 1 / 1 / 3 columns, 0 px overflow, seven rooms) are unchanged from AUDIT-CDH-0020-REVIEW.
   - There are no page errors.
   - Before and after captures in deck mode at 320 and 400 show no deck label inside a HUD's box.
   - Captures and a manifest go in a cdh-0021 folder under the design-review scratch folder.
3. Report as the implementation report for CDH-0021 under `docs/audit/cockpit-design/`, with the delivered file's SHA-256 and the measurements; a dated status section in the README; this file `done` with `completed:` and `report:`; the queue row `done`; one commit by pathspec. Then stop for Cowork's native pass.

## Acceptance

The HUD's words never sit over a deck label below 721 px; 721 px and above are untouched; the facts, the summary and the calm grid are as AUDIT-CDH-0020-REVIEW measured them; `make check` green.
