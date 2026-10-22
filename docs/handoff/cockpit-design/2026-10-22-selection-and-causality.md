---
id: CDH-0026
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

# CDH-0026: Selection and causality, the sum of the parts

## Outcome and authority

AUDIT-CDH-0022's "the sum" paragraph names what the whole canvas does that no single board does: the tray answers who, the timeline what happened, the detail why, and the station makes responsibility spatial. This row spends the extravagance there: on the links between responsibility, event and evidence, replacing repeated captions.

Every item is from AUDIT-CDH-0022's table, scored below 1.5 and decided by Cowork. Each goes on the approval screen. This row becomes `ready` after Cowork's native pass of CDH-0023.

## Do

1. **One selected-event context strip on the desk boards (0.9).** On 3, 4 and 5, the selected run's portrait, lifecycle word, elapsed time and latest event form one strip. It replaces the competing run headers and repeated run-ID lines that say the same thing.
2. **One selected-run marker, tray ↔ timeline (0.6).** The same mark sits on the tray row and on the timeline's run group, replacing the duplicated selection captions.
3. **The wall's one selection (0.8, with F6 at 0.4).** On board 9:
   - the raw stream column follows the selected event, so it shows the reviewer event's payload, not the builder's session;
   - one shared selection marker runs across timeline, raw payload and detail;
   - the repeated selection metadata in the payload and detail headers goes.
4. **Causal connectors (0.8 each).** Each replaces an ordinary duplicated label:
   - board 3: a short parent-to-outcome trace for the selected event;
   - board 4: the three strike marks terminate at the escalation packet's link;
   - board 5: a visible open connector from the intent to where its outcome will land, replacing the empty outcome row and the separate waiting explanation.
5. **The station's bubbles: Cowork's decision, which differs from AUDIT-CDH-0022.** Keep the ambient bubbles: they are the crew's voice, and Michou kept the station's whole vibe. Instead:
   - at most one bubble per room, and never two overlapping (the newest wins; the seven-second lifetime is unchanged);
   - while a room is followed, add one dispatch line in the pane's head joining speaker, event and room (AUDIT-CDH-0022's 1.2 idea, as an addition, not a replacement).

   Scored 3 × 0.4 = 1.2, approval screen. Every event's text stays in the room chip, the pane and the wall.

## Verify

- A source check that no fact is lost: each removed caption's text exists in the strip, the marker's label, the connector's label or the pane.
- The CSS fixture at 1440, and 2560 for the wall.
- The station standalone at 1440 and 400: no two bubbles overlapping across a 60 s replay at speed 2, sampled each second; the dispatch line correct when following; focus and calm as before.
- `make check` green.

Report, close out and commit as for CDH-0023.

## Acceptance

- Each board says who, what and why once, with visible links between them.
- The wall's evidence belongs to its selection.
- The station keeps its voices without overlap.
