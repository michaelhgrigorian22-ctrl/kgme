---
id: CDH-0033
type: handoff
created: 2026-10-28T20:20:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0033: The station, over the edge

## Outcome and authority

Michou, 2026-10-28 20:12: the station should look like a rendered place, not a diagram, and the logic should live inside the world. His word is the ruling on the two taste calls below (4 × 0.5 = 2.0, asked and answered in the same breath). The canvas at `9c360af` is the approval candidate and stays so; this row lands after it as new commits and is reviewed natively by Cowork like every other.

**Two rulings this row carries.** (1) Frame budget: the standing "within 2 ms of CDH-0026" is replaced for the station by *60 fps at 1440 × 900 on the M4 Pro: ≤ 16.7 ms mean, ≤ 20 ms P95 over a 30 s replay at ×2*, the 400 px profile simplified as today and never worse than today's numbers, reduced motion stilling every animation. (2) Direction: the orbital-casino hull, the etched sky, the dreadnaught and the cast are kept as accepted; this row deepens how they are rendered and inhabited, it does not redraw them. A change that reads as a different station is out of scope.

**What does not change.** The one rule (the sky and the shell carry no fact; every fact is in words); AUDIT-CDH-0011 S1 (the HTML HUD, chips, pane and wall are the source of truth, light and scene mirror them, never replace them); calm removes the stage entirely; reduced motion stills everything; 4.5:1 on every text element as painted (the composited sweep); the chips' width and height budgets (CW34, CW40: 0 overlaps at 400 × 700, 800 × 600, 1440 × 900); one focus ring, one easing, three durations (CDH-0031); no dependency beyond the pinned `three@0.182.0` and its own `examples/jsm` addons; no network; Chrome-neutral (WebGL2, nothing WebGPU-only); the page stays a plain file served over HTTP with no build step.

## Do

### A. Render: the place has light, depth and material

1. **Shadows.** One directional key light casting soft shadow maps onto the deck, the rings and the crew; the room point lights stay as the state lights they are (their intensity still mirrors the words). Shadow resolution scales with the profile.
2. **Materials.** The hull, rings, spindle, deck and furniture get proper PBR surfaces: roughness and metalness maps generated procedurally in shaders (no texture files), subtle wear on edges, an environment reflection from a small procedural cubemap of the sky so the copper and glass pick up the nebula. The deck floor gets a faint planar reflection of the rooms' state lights (a reflector pass or a screen-space fake, whichever stays in budget).
3. **Atmosphere.** Volumetric light from each lit room (a cheap cone mesh with additive falloff, driven by the same state light), a thin fog toward the hull's edge, and the bloom retuned so only emissive seams, state lights and the HUD-free seams bloom. Nothing of this carries a fact; all of it goes under calm and reduced motion.
4. **Camera.** The follow keeps its 480 ms travel; add a slow idle drift (sub-pixel per second) when nothing is followed, stilled under reduced motion, and a depth-of-field pass only while following (the followed room sharp, the rest soft), within budget or omitted.

### B. Inhabit: the crew and the rooms behave

5. **The crew walks the station.** Runs enter through the dock gate along a path around the promenade to their seat, not in a straight line; seated poses at desks; the builder hammers at its bench, the reviewer leans over its lectern, the guard paces the airlock, Michou on the bridge turns toward whichever room is followed. Each pose is the existing chibi symbol with its documented modes; no new artwork, only placement, facing and the existing animations.
6. **The rooms show their state in the scene** without adding a fact: the workshop's bench lights up while working, the review chamber's lectern glows amber while transient, the airlock's door flashes on a refusal (it already does), the archive's vault opens on a `kgme sync` outcome, the engine room stays dark and dashed. Every one of these mirrors a word already on a chip.

### C. The logic window: the pane inside the world

7. **A diegetic screen** on the bridge (and a small one in each room) renders that room's live rows — the same rows the pane shows — as an in-world display: a CSS3DRenderer panel placed in the scene, so it is real DOM text (selectable, accessible, measured by the same contrast sweep), tilted in perspective with a faint scanline and glow. The HTML pane stays the accessible source of truth and keeps every keyboard path; the screen is a second view of the same snapshot, never a different one.
8. Following a room brings its screen to the camera; `a` still opens the pane; `Esc` behaves as today. On the phone profile the screens are hidden and the pane alone serves.

### D. Leave the checks behind

9. `tests/test_design_station.py` (or the precision pattern): the frame-budget test from Codex's existing 30 s replay harness, asserting the new budget at 1440 and the unchanged numbers at 400; the chip overlap count (already there); the 16 contrast cases including the in-world screens; calm removes the stage and every new mesh; reduced motion stills every new animation; 0 new network requests; 0 page errors.

## Verify

- The frame runs at 1440 × 900 and 400 × 700, 30 s at ×2, in Chromium on Metal; mean and P95 against the new budget; the 400 numbers no worse than `9c360af`.
- The composited contrast sweep over the station's 16 cases plus the in-world screens; 0 elements below 4.5.
- Chips 0 overlaps at the three sizes; the focus pass (54 stops) unchanged; Enter, Esc, a, c, p, r as before; the pane's content equals the screen's content for the followed room (a text comparison).
- Calm: the stage hidden, 7 rooms, columns as before, 0 overflow. Reduced motion: two captures 4 s apart pixel-identical across the whole stage.
- Safari through `safaridriver`: renders, no shader errors, the 16 contrast cases, keys and clicks (CDH-0030's method).
- Before/after captures at 1440 and 400 for Cowork's native pass and Michou's look.

Report, close out and commit as for CDH-0023; this row's verify needs a served page, so it runs attended (server: yes). Then stop for Cowork's native pass; Michou judges the look.

## Outputs

- `docs/design/cockpit-v0/station/index.html` (the only design source this row touches).
- `tests/test_design_station.py`: the standing checks of D.9, under `make check`.
- `docs/audit/cockpit-design/cdh-0033-implementation.md`: the implementation report, with every delivered file's SHA-256, the frame numbers, every check and every score.

## Acceptance

- The station reads as a lit, material place with a crew that moves through it, under the accepted hull and sky; the logic is visible inside the world and identical to the pane's.
- The new frame budget holds at 1440; the phone profile is no worse.
- Every rule above holds and the tests keep it.
