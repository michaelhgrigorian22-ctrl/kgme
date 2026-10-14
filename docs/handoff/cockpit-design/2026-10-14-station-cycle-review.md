---
id: CDH-0013
type: handoff
created: 2026-10-14T00:52:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0012]
design_track: HANDOFF-0036
---

# CDH-0013: Read-only re-review of the station's second cycle and the tray's T1

## Outcome and authority

An independent, read-only review of CDH-0012's cycle on branch `design`, at the sha AUDIT-CDH-0012 names: the station (`docs/design/cockpit-v0/station/`) after S1–S9 and `Tray.dc.html` after T1. Codex's reviewer role only. Adopted when Michou's queue prompt starts Codex and this row is the first `ready` one in the README's Codex queue; Cowork marks it `ready` when CDH-0012 is `done`.

## Do

1. From `~/Projects/Automate-design` on `design`, review by the rules and format of `tools/review/design-prompt.md`, with the captures under `logs/scratch/design-review/cdh-0012/` as image input (and `cdh-0009/`, `cdh-0010/` as the labelled historical set). Headless Chromium from the repository files if the sandbox allows; otherwise source and captures, and say so.
2. Judge each of AUDIT-CDH-0011's findings closed or not: S1 by the shared snapshot and the calm captures at the refusal, the note and the synthetic halt; S2 by source evaluation of the four root intents and a blocking-note-then-resume sequence; S3 by the accessibility ownership of the room buttons; S4 by the keyed row updates; S5 and T1 by measurement on the actual cascade; S6 by the network list; S7 by one threshold in board 11, the README and the code; S8 by source; S9 by the labelled evidence. Then the usual gates: every fact in words, contrast 4.5:1 on its ground, read-only, nothing remote but the pinned package and the repository's files, the cast unchanged.
3. Write `docs/audit/cockpit-design/cdh-0013-design-review.md`: `id: AUDIT-CDH-0013`, `handoff: CDH-0013`, `author: codex`, `source: inferred`, the reviewed sha, the three sections.

## Closeout

Set this file `done` with `completed:`, the queue row `done`, and commit your three delivery files by pathspec as the queue prompt says. Findings return to Michou.
