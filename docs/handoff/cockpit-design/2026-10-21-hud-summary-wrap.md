---
id: CDH-0020
type: handoff
created: 2026-10-21T16:25:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0020: The HUD's active-runs summary below 362 px (CW26)

## Outcome and authority

A build row under CDH-0019's mandate: AUDIT-CDH-0019-CYCLE-1-REVIEW CW26, scored 2 × 0.2 = 0.4 and decided (ADR-023). Adopted when the builder prompt takes this row as the first `ready` one.

## Do

1. In `docs/design/cockpit-v0/station/index.html`, under the existing `@media (max-width:720px)` block, let `.tr-sum` wrap (`white-space:normal`) or shrink it, so `#traysum` stays inside the viewport at 320 and 360; keep the single line at 721 and above. If the station's HUD markup is mirrored on a board, follow it there too; otherwise touch nothing else.
2. Verify standalone with the real page: `sh logs/scratch/vendor/make-local.sh`, serve `logs/scratch/vendor/` on 127.0.0.1, open `station-local.html?at=19:52:00&speed=1` in headless Chrome at 320, 360, 400 and 1440: `#traysum`'s right edge ≤ the viewport width at each, the calm grid unchanged (1 / 1 / 1 / 3 columns, 0 px overflow), no page errors. Captures and a manifest under `logs/scratch/design-review/cdh-0020/`.
3. Report `docs/audit/cockpit-design/cdh-0020-implementation.md` with the delivered file's SHA-256 and the measurements; a dated status section in the README; this file `done` with `completed:` and `report:`; the queue row `done`; one commit by pathspec. Then stop for Cowork's native pass.

## Acceptance

`#traysum` inside the viewport at 320, 360 and 400 with the HUD's facts unchanged; the calm grid results of AUDIT-CDH-0019-CYCLE-1-REVIEW reproduced; `make check` green.
