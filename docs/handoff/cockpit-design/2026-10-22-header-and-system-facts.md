---
id: CDH-0023
type: handoff
created: 2026-10-22T02:10:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0023: The compact operating header and one home for system facts (B1, CW28, CW30, F8)

## Outcome and authority

The first build row of the coordinated redesign under the design philosophy of 2026-10-22, the first bullet of the reader's Decided list. Michou took B1 on 2026-10-22 at 01:59 ("agree on both"). It's built with CW28 and CW30 (AUDIT-CDH-0019-CYCLE-2-REVIEW, decided at 0.6 and 0.1) and AUDIT-CDH-0022 F8 (0.9), because all four touch the same strings and board 7.

**The rule this row establishes:** the operating surfaces show state and alerts; system context lives once, under `?` on desk and wall and under `a` on the station; the corner micro-labels carry no fact at all.

Adopted when the builder prompt takes this row as the first `ready` one.

## Do

1. **The header, on the operating boards.** These are 3 Live, 4 Blocking, 5 Pending, 6 Disconnected and 9 Wall; 2 Empty and 8 Phase 2 follow the same header.
   - **The header keeps:**
     - the clock;
     - the ledger state word with its counts (live, halted, unreachable, stale);
     - the active-runs tray slot;
     - each quota only as an alert: its bar appears at 80 % or more (amber) or at the cap (magenta), and below that nothing is shown for it.
   - **The header drops:** session, hook latency, harness versions and arbiter, the full quota bars and reset times. They move to step 3's system section.
   - **Board-specific state stays where it is the signal.** Board 4's halt and board 6's unreachable state are the alert itself. Board 6's disconnect presentation is CDH-0024's; here only give it the same header.
2. **The micro-labels, on every board that has them.**
   - Each corner micro-label becomes facts-free ornament. It may repeat text already on the same screen (for example the product name or "cockpit v0") or carry nothing; it may not hold a path, origin, version, ADR, hook, poll interval or key hint.
   - Delete the `source-facts` line from the eight hosts (CW28; CW30 goes with it).
   - Audit every remaining micro-label against the one rule.
3. **The system section, one copy per surface.**
   - **Desk and wall:** on board 7, `docs/design/cockpit-v0/Keys.dc.html`, the `?` overlay gains a "system" section with the sample values: session, harnesses and arbiter, hook latency, both quotas with resets, origin, ledger file, poll interval, the ADR, hook and guard provenance. Every operating board's footer keeps its `?` hint.
   - **Station:** in `docs/design/cockpit-v0/station/index.html` the `a` pane gains the same "system" section, holding the session and harnesses that leave its HUD, and the replay range and speed. It replaces the two `[data-source-facts]` mirrors.
4. **The key map knows its surface (F8).**
   - Board 7 shows which surface its keys belong to (desk, wall, station), with the station's own `p`, `r`, `1`–`7`, `a` and `c`.
   - It shows the three-way `w` cycle desk → wall → station (Michou, 2026-10-22).
   - Each binding's explanation goes beside its key family (AUDIT-CDH-0022, board 7, 0.6).
   - Keep the physical keyboard silhouette and the Phase 2 dashes.
5. **The station's HUD keeps:**
   - the clock;
   - the hull (`nominal` or `HALT · <key>`);
   - active runs;
   - the replay control;
   - following.

   Session and harnesses move to the `a` pane (step 3). Measure the HUD's share of a 400 × 700 viewport before and after; it was 78.1 % (AUDIT-CDH-0022).

## Verify

- **A source check:** every string removed from a header, a micro-label or a `source-facts` line appears exactly once in the system section of its surface, and no micro-label holds a fact.
- **The station, standalone:** with `sh logs/scratch/vendor/make-local.sh`, serve `logs/scratch/vendor/` on 127.0.0.1 and open `station-local.html?at=19:52:00&speed=1`. Check at 320, 400, 720, 721, 1440 and 2560, deck and calm:
  - the HUD's share of the viewport;
  - every Tab-focused room inside the deck band, measured after rendered frames (lessons file);
  - the `a` pane's system section complete;
  - calm unchanged;
  - no page errors.
- **The boards:** the CSS fixture method of cycle 2 for the headers' layout at 1440 (2560 for the wall), with a quota at 31 % (no bar) and at 91 % (amber bar). Native paint is Cowork's.
- `make check` green.

## Report and closeout

Write the implementation report for CDH-0023 under `docs/audit/cockpit-design/`. Close out:
- this file `done` with `completed:` and `report:`;
- the queue row `done`;
- a dated README status;
- one commit by pathspec.

Then take the next `ready` row (CDH-0025 is independent of this one). Cowork's native pass of this row comes before CDH-0024, CDH-0026 and CDH-0027 become `ready`.

## Acceptance

- The operating headers hold state and alerts only.
- Every system fact is reachable once, under `?` or `a`.
- No micro-label carries a fact.
- The station's phone HUD share drops measurably.
- Every earlier check still holds: contrast, 24 px targets, focus, calm, no fact removed.
