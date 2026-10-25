---
id: CDH-0031
type: handoff
created: 2026-10-25T16:40:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0029, CDH-0030]
design_track: HANDOFF-0036
---

# CDH-0031: The precision pass (the first detailing run)

## Outcome and authority

Michou, 2026-10-25 16:33: detailing runs "to kind of smooth things out on the app will be useful asf going forward for ensuring that the UI is not only pretty but also works seamlessly." This is the first. A detailing run changes no fact, no feature and no layout intent; it tightens how the existing design is executed, and it leaves behind checks so the next build cannot undo it. From here a detailing run is a standing row type, written whenever the canvas has settled after a round of feature rows.

The reference feel Michou named is the one where the thing you touch answers at once and settles like something physical. That is mostly motion and response, and partly spacing. Nothing here contradicts the component sheet (board 1): JetBrains Mono everywhere, the type scale 22/14/12/11/9, the phosphor palette with its state meanings, 4.5:1 for every text pair, colour never alone. Gemini's advice of the same day was read; its grid and border points are taken, its second font and low-contrast labels are not.

This row is `ready` after CDH-0030. It is read against the eleven boards, the station page and the tray.

## Do

### A. The grid: an 8 px scale, measured

1. Every padding, gap and margin on the boards, the station's HUD, pane and chips, and the tray snaps to the 8 px scale (4 px allowed only inside a row's own anatomy: chip padding, the 3 px row inset, the 1 px rule). Where a value is off the scale today, move it to the nearest step; where moving it would change a documented size (the 22 px row, the 24 px target), the documented size wins and is listed.
2. **Shared baselines.** On every multi-column board the columns start on one top line and end on one bottom line at the board's design size; the wall's four columns and the desk's three. Panel heights balance by flex, not by padding.
3. **Borders.** Structural dividers and panel borders are 1 px at one muted value per surface, used everywhere on that surface (today's `#1e2a33` on the desk boards is the candidate). The frame, its glow, the corner brackets and the tick rails are the signature and stay as they are; they are noise under the one rule and already collapse under `c`.
4. **Type.** No arbitrary tracking or stretching: the five sizes of the scale and their documented line-heights only; `letter-spacing` only the two documented values (.14em labels, .1em chips). Numbers in the HUD and the clock use tabular figures everywhere so nothing shifts as they tick.

### B. Motion and response: one rulebook

5. **One easing, three durations.** Every transition on every surface uses one curve (a standard ease-out, the same cubic-bezier everywhere) and one of three durations: 120 ms for response (hover, focus ring, a chip highlight, a button press), 240 ms for state (a pane opening or closing, a filter applying, a row selecting), 480 ms for travel (the station's camera following a room, a crew member walking). Nothing else. Any existing transition or animation that is not one of these becomes one of these or goes.
6. **Response within a frame.** Hover and focus feedback begins on the next frame after the input (no delay, no debounce on feedback; debounce the work, never the acknowledgement).
7. **Settle, never snap or drift.** State changes animate from where the element is, not from a reset position; the station's camera easing finishes (no perpetual creep after a follow); the only perpetual motions are the documented ambient ones (the replay's crew, the sky, the cursor blink), each already stilled under reduced motion.
8. **Focus is never ambiguous.** One focus ring style on every surface (the cyan 2 px outline with its offset), visible on every focusable element including the station's chips and the boards' filter buttons, and it moves with the same 120 ms response.
9. **Reduced motion** keeps every state change visible (an instant cut), removes every travel and ambient animation, and is one media query, not scattered rules.

### C. Leave the checks behind

10. `tests/test_design_precision.py` (or the existing `tests/test_design_*.py` pattern): the 8 px scale over every padding/gap/margin in the design files, allowing the listed exceptions; the baseline check at design size through the CSS projection; one border value per surface; the easing and duration whitelist (every `transition` and `animation` in the design files uses the one curve and one of the three durations); tabular figures on the numeric classes. These run under `make check`, so a later row that strays fails the gate.
11. The rulebook itself goes into the reader, `docs/readers/cockpit-design.md`, as a short "Precision" section beside the noise rule, and board 1 gains a small "Motion" specimen: the curve, the three durations, the focus ring.

## Verify

- The new tests green, and `make check` green.
- The CSS fixture at design size, before and after, for every board: diff images, so that what changed is only spacing, borders, type metrics and motion.
- The station standalone: a recording or frame series of a follow (480 ms), a pane open (240 ms) and a chip focus (120 ms), with the measured durations; focus and calm as before.
- Contrast unchanged or better on every text pair (the sampling of CDH-0028).
- No fact removed, no feature changed (the source comparison of CDH-0026).

Report, close out and commit as for CDH-0023, then stop for Cowork's native pass, where the response rules are felt in the pane, not only measured.

## Acceptance

- Everything sits on the grid, columns share baselines, borders are one line, type is the scale.
- Everything that moves uses the one curve and one of three durations, answers within a frame, and settles.
- The checks exist and run, so the precision survives the next feature row.
