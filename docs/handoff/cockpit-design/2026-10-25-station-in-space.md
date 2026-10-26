---
id: CDH-0028
type: handoff
created: 2026-10-25T13:30:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: done
completed: 2026-10-25T15:14:10-07:00
report: docs/audit/cockpit-design/cdh-0028-implementation.md
adopted_by: michou
adopted: 2026-10-25T14:04:14-07:00
depends_on: [CDH-0027]
design_track: HANDOFF-0036
---

# CDH-0028: The station in space

## Outcome and authority

Michou, 2026-10-25 13:25: "keep the station basically the same but add planets around it make it look like its a terminal floating in space haha like a weird swag trippy version of space though." That is the instruction; this row writes its boundaries. The deck, the crew, the HUD, the pane, the chips, the bubbles and every key stay as they are after CDH-0027. What changes is what the station floats in.

This row becomes `ready` after Cowork's native pass of CDH-0027, because both touch `docs/design/cockpit-v0/station/index.html`.

## Do

1. **The sky.** Behind and around the deck, in the WebGL scene: planets, and a weird, swag, trippy space. Read that as the philosophy reads "extra": the surprise is in how the parts combine, not in how many there are. Some directions, Codex's to choose from and combine:
   - a few planets at different depths, one near and large, the others far; banded gas giants, a ringed one, a moon or two;
   - a nebula or aurora wash behind the stars, slow and drifting;
   - the existing star field kept, perhaps with a second, denser layer at depth for parallax when the deck pans;
   - colour from the cockpit's phosphor palette (cyan, magenta, amber, green, the dark ground) pushed further than the deck uses it: gradients, iridescence, a little chromatic fringe, bloom on the planets' limbs. Nothing pastel, nothing bright enough to compete with the HUD;
   - slow motion only: a planet's rotation measured in minutes, a nebula drift measured in tens of seconds.
2. **The one rule holds.** The sky is noise in the reader's sense: it carries no fact. No planet, ring or colour means anything about the ledger; nothing in the sky changes with runs, halts, quotas or rooms. The hull's state light and the rooms' lights keep their meanings and are not echoed in the sky.
3. **Calm and reduced motion.** `c` removes the sky with the deck as today (the wall is text). Under `prefers-reduced-motion` every sky motion stops; the planets stay, still.
4. **Legibility.** Every HUD, chip, bubble and pane text keeps at least 4.5:1 against whatever the sky puts behind it; the HUD backgrounds may be made more opaque where needed, and the sky is darker behind the HUD bands than in the centre. The deck's own lines stay the brightest thing on screen apart from the text.
5. **Performance.** No new dependency: the pinned three@0.182.0 and its addons, nothing fetched. Planets are low-poly spheres with shader or texture bands generated in code; no image files. On the target Mac the frame interval does not get worse than the CDH-0026 baseline by more than 2 ms at 1440 × 900; record the numbers. At 400 × 700 the sky may be simplified (fewer planets, no second star layer).
6. **The frame.** The grey disconnect frame and the hull halt colour are unchanged; the sky must not read as a state.

## Verify

- The station standalone at 400, 800 × 600 and 1440, deck and calm, reduced motion on and off: contrast of every text class against its actual background (sample the pixels behind each text box); no sky element over a chip, bubble or pane; calm shows no sky; reduced motion shows no sky motion over 10 s.
- Frame intervals over a 30 s replay at ×2, with and without the sky, at 1440 × 900 and 400 × 700.
- A source check that no sky parameter reads ledger state.
- `make check` green.

Report, close out and commit as for CDH-0023, then stop for Cowork's native pass: Michou will judge the look natively, so the native captures at 1440 and in the pane are the review.

## Acceptance

- It looks like a terminal floating in a weird, swag, trippy space, and the station is otherwise the same.
- No fact in the sky; calm and reduced motion unchanged in meaning.
- Every text still reads; the deck still leads.
- No new dependency and no frame-time regression beyond the budget.
