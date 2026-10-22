---
id: CDH-0014
type: handoff
created: 2026-10-15T22:55:00-07:00
from: michou
to: cowork
tier: 2
status: done
adopted_by: michou
adopted: 2026-10-15T22:43:00-07:00
completed: 2026-10-15T23:50:00-07:00
rulings: "relayed from the substantive session's review of ui-ux-pro-max (2026-10-15): rubric only, never the generator; runs under the 2026-10-14 00:41 rule (blocking findings taken by default)"
depends_on: [CDH-0012, CDH-0013]
design_track: HANDOFF-0036
---

# CDH-0014: The rubric's checks, measured natively — tray, boards and station

## Why

Michou found `nextlevelbuilder/ui-ux-pro-max-skill` (MIT). The substantive Cowork session reviewed it on 2026-10-15 and ruled: use it as a **review rubric only**, never its generator (its `--design-system` output proposes a landing-page pattern, a slate/green palette and Google-Fonts Orbitron; the cockpit's palette and type are decided, and AUDIT-CDH-0011 S6 removed remote fonts). Three text files are vendored at `tools/review/design-reference/ui-ux-pro-max/` pinned to `56ea9cf1` (commit `85691f9`, hashes in its `PROVENANCE.md`), and `tools/review/design-prompt.md` cites them. This handoff runs the six checks the substantive session named against the tray (board 11 and its hosts), the boards and the station, **measured natively** where the browser pane allows and standalone where it does not, saying which, and fixes what fails in the same cycle.

## Do

1. **Count changes as one status** (`contextual live badge updates`, ux-guidelines 118). The tray's summary (`tr-sum` on board 11 and in every host; `#traysum` in the station) is one `role="status"` region with `aria-atomic="true"` whose text is a meaningful sentence (`active runs: 2 working (1 quiet) · 1 transient`), polite by default, and nothing else in the tray is a live region; a change never moves focus. Measure: the accessibility tree (the pane's reader where it reaches the frame, Playwright's otherwise) shows one status node with that text before and after a count change; `document.activeElement` is unchanged across the change.
2. **Focus never obscured** (`focus-not-obscured`, row 100; sticky navigation, row 2). On boards 3, 4, 5, 9 the timeline and the tray's pane scroll under nothing: `scroll-padding-top` equal to the header's height on the scrolling container, or the header not sticky, stated on the board. In the station the pane and the wall sit below the measured HUD (the wall does since CDH-0012; the pane is at a fixed 118 px, which the HUD exceeds when it wraps at 1440 or under a halt): the pane's top follows the HUD's height as the wall's padding does. Measure: Tab to the last row of a scrolled pane and the first row of the timeline at 1440 × 900 and 400 × 800; the focused element's rect does not intersect the header's or the HUD's rect.
3. **A pause for the looping replay** (`auto-rotation-controls`, row 108). The station gets a visible pause/play control in the HUD and a key (`p`), named in the footer and board 7's station rows when they come; under reduced motion the replay starts paused, with the control saying so (Michou may veto the default). Measure: the clock stops and the rows stop changing while paused; the control's accessible name states the state.
4. **24 × 24 CSS px pointer targets** (`web-target-size`, row 104). Every real button in the tray and the station measures at least 24 × 24 CSS px or has the spacing exception documented: the tray's `Esc closes` button and the collapsed bar, the station's `Esc closes`, the room chips, the filter buttons on board 3, the pane rows (two lines, already taller). Measure: `getBoundingClientRect()` of every `button` in the mounted boards and in the station at 1440 and 400.
5. **WCAG 2.1.4 character-key shortcuts.** The cockpit binds single characters (`j k / Enter Esc u Tab f t o x c p w ? r a` and `1`–`7`); the drawing must say that they are active only while focus is on the cockpit's own surface and never inside a text field, and that `?` lists them, or that they can be turned off or remapped. Board 7 (Keys) gains that sentence; the station's handler ignores keys whose target is an input, a textarea or an editable element and its footer says so. Measure: the sentence on board 7 natively; in the station, a key pressed with focus in a (test-only) text field does nothing.
6. **The station against `stacks/threejs.csv` rows 1–9.** Row by row: 1 the pinned package (`three@0.182.0` through an import map; the rubric's "current" is 0.185.1, the pin is the rule, the version is Michou's call with HANDOFF-0044); 2 CapsuleGeometry (not applicable, no capsules); 3 and 4 OrbitControls from the addons or a custom drag fallback (the station pans and zooms with its own handlers: judge them against row 4's guidance); 5 ESM imports through the import map; 6 one renderer per page; 7 the pixel-ratio cap at 2; 8 an alpha canvas with a CSS background versus the scene's own background colour; 9 the camera's aspect on resize (orthographic: `left`/`right` from the aspect). Record each as met, not applicable, or changed.
7. Commit `design: rubric checks, CDH-0014`, republish the review copy and the station, write `docs/audit/cockpit-design/cdh-0014-implementation.md` with one row per check (rule id, row number, what was measured, what changed), mark this file done, and set the Codex queue row for the re-review to `ready`.

## Acceptance

Codex's re-review, by the rubric now cited in `design-prompt.md`, finds the six checks met by measurement or by a documented exception, with every finding still carrying one ADR-016 class.
