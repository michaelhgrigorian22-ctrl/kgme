---
id: CDH-0024
type: handoff
created: 2026-10-22T02:10:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0023]
design_track: HANDOFF-0036
---

# CDH-0024: The persistent disconnect band (B2)

## Outcome and authority

Michou took B2 on 2026-10-22 at 01:59. Board 6, `docs/design/cockpit-v0/Disconnected.dc.html`, replaces its central modal and globally dimmed workspace with a persistent disconnect band. The band sits under the compact header from CDH-0023, and the snapshot below it stays inspectable.

It's built with board 6's two dependent items from AUDIT-CDH-0022:
- one clear "as of" boundary on the snapshot, replacing the repeated stale captions (2 × 0.4 = 0.8);
- the long recovery explanation moved into `?` (2 × 0.3 = 0.6).

This row becomes `ready` after Cowork's native pass of CDH-0023.

## Do

1. **The band.** One band, full width, under the header, in the disconnected frame's grey with a glyph and the words.
   - It keeps:
     - last event and its age;
     - origin and error (`127.0.0.1:8642 · connection refused`);
     - retry cadence and attempt;
     - the durability sentence ("nothing is lost: the ledger is a file");
     - `r` retry now and `c` calm.
   - No modal, and no dimming of the whole workspace.
2. **The snapshot.**
   - The timeline, tray and detail stay readable and focusable, in their stale state.
   - One "as of 19:52:14" boundary line marks where the live record stopped; remove the other stale captions that repeat it.
   - Muted text under any remaining filter keeps the board's `#a3b0b8` rule (CW18).
3. **Into `?`.** "To start: kgme cockpit from the repository", the Dock-icon sentence and the launchd note move into the system section from CDH-0023, under a "when disconnected" heading.
4. **The frame stays grey static.** The noise rule is unchanged.

## Verify

- The CSS fixture at 1440: the band's facts, the snapshot's contrast under the stale state, focus order (band, then timeline), and no element hidden behind the band.
- A source check that every fact the modal held is in the band or under `?`.
- `make check` green.

Report, close out and commit as for CDH-0023.

## Acceptance

- No modal.
- The band carries every fact the modal held, or names `?` for the long explanation.
- The snapshot is inspectable, with one "as of" boundary.
- Contrast and focus pass.
