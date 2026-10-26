---
id: CDH-0032
type: handoff
created: 2026-10-26T00:45:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: open
adopted_by: michou
adopted: 2026-10-26T00:50:00-07:00
depends_on: [CDH-0030]
design_track: HANDOFF-0036
---

# CDH-0032: Words above the noise (the contrast repair)

## Outcome and authority

AUDIT-CDH-0030 (Codex, the WebKit check at `0907f28`) found two blocking contrast defects shared by Safari and Chromium; AUDIT-CDH-0030-REVIEW (Cowork) confirmed both and widened the first: the boards' decorative overlays composite above the words, and the muted text token has no headroom even where no overlay touches it. Under ADR-023 a failed check is repaired, not asked about; the two judgement calls inside the repair are scored below the asking line and recorded on the README's open list. This row is `ready` now and goes before CDH-0031, which reads against the result.

The one rule stands: the vignette, the frame glow, the scanlines and the tick rails are noise that carries no fact, and they stay. They move under the text, not out of the design.

## The findings, in numbers (AUDIT-CDH-0030-REVIEW)

- Rendered, not computed: the muted token `#6f8290` on the panel tint `#11151c` is 4.59:1 by the CSS pair and paints at 4.47 to 4.55:1 in every renderer measured (Metal, SwiftShader; Safari and Chromium agree). With the overlays hidden, 82 elements in that token still fail on the eleven boards. Sprites and Tray carry no overlays and still show the token at the edge.
- The overlays (`.vig` at z 2, `.frame` at z 3, `.scan` at z 4 in each desk board's head; the wall's equivalents) sit above the text and take the edges and corners to 1.6 to 3.9:1: Main's `clock` label 2.1 to 2.2:1, the `◦ ◦ ◦` micro-label at the bottom-left 1.55 to 1.63:1 on five boards, the key legends along the bottom 2.5 to 4.4:1. As painted, 238 of 1,524 measured text elements fail.
- Board 7's twelve reserved-key captions (`.f2 small`, `.f2 b` at `#3a4650`) paint at 1.9:1. They are descriptions, not disabled controls.

## Do

### A. The words above the overlays (3 × 0.2 = 0.6, decided)

1. On every desk board and the wall, the decorative overlays composite **below** every text-bearing layer: `.vig`, `.scan`, `.frame`, `.tx`, `.ty` and any board-local equivalent (the glow, the corner brackets). Keep them above the ground (`body`, `.hud`'s own background) so the look is unchanged on empty surface; put the panels, the header, the tray, the legends and the micro-labels above them. One ordering per surface, written once in the shared head of each board (and in `Tray.dc.html`'s `<helmet>` for the mounted tray), not patched per element.
2. The vignette keeps dimming the ground toward the corners and the HUD bands keep it behind them; no word is dimmed by it anywhere. The scanlines still cross the panels' surfaces behind the words.
3. Nothing else moves: no padding, no size, no fact, no feature. CDH-0031 owns spacing and motion.

### B. Headroom in the token (2 × 0.3 = 0.6, decided)

4. The muted text token `#6f8290` becomes `#7a8d9b` wherever it colours words: `.lbl`, `.mut`, `.micro`, the `.tr-*` muted classes, `.chip.c-none`, the key legends and every inline `color:#6f8290` on text. `#7a8d9b` is already the focused-row token (CDH-0017), 5.1 to 5.4:1 on the panel tints before overlays. Where `#6f8290` colours a border, a rule or a glyph that is not text (the `◦` ornaments count as text), it may stay.
5. Board 1's component sheet records the change: the muted token's value and that every text token is measured as painted, after overlays, not as a CSS pair.
6. Any other text token that the sweep shows below 4.8:1 by its CSS pair on its own surface is raised the same way and listed; `#6f8290` is the one known today.

### C. Board 7's captions (F2, 2 × 0.2 = 0.4, decided)

7. `.f2 small` and `.f2 b` take the muted token; the reserved key's frame stays dashed in `#3a4650` and the key stays inert (no `.on`, no cursor change). The legend and the "reserved" wording are unchanged.

### D. Leave the check behind

8. `tests/test_design_contrast.py` under `make check`, static, no browser: (a) every text colour token declared in the design files, paired with the surfaces it is used on, has a CSS-pair ratio of at least 4.8:1 (the headroom that survives rendering and the scanlines), with the disabled-control grey listed as the one exclusion; (b) in every board's head the overlays' `z-index` values are below the lowest text-bearing layer's; (c) `#3a4650` colours no text outside disabled controls. A later row that strays fails the gate.

## Verify

- **Composited sampling, every board and the station**, at design size and device scale 2, in Chromium (and Safari through `safaridriver`, now that CDH-0030 has the method): for every text element, the minimum contrast of its painted glyph pixels over the ground beneath them, overlays included. The bar is 4.5:1 on every element except disabled controls, which are listed. Use CDH-0030's foreground/background swatch method or AUDIT-CDH-0030-REVIEW's coverage method (`logs/scratch/design-review/cdh-0030-review/sweep30.py`); report the per-board counts before and after, so the 238 becomes 0.
- The station page is byte-identical unless a shared file forces a change; if it changes, its 16 pixel cases run again.
- Sprites and Tray change only by the token value; diff images at design size for every board show the words lighter and nothing moved.
- The fixture paints `ui-monospace` (CDH-0030's font caveat): run the sweep once with JetBrains Mono available locally if the vendor copy allows, and say which font painted.
- `make check` green with the new tests; 0 blocking lint findings.

Report, close out and commit as for CDH-0023, then stop for Cowork's native pass (the words in the pane at the corners, board 7's captions, the look of the edges with the vignette behind the text).

## Outputs

- `tests/test_design_contrast.py`: the static check of D.8, under `make check`.
- `docs/audit/cockpit-design/cdh-0032-implementation.md`: the implementation report, with every delivered file's SHA-256, the per-board counts before and after, every check and every score.
- The changed design files under `docs/design/cockpit-v0/` (the boards, `Tray.dc.html`; the station only if a shared file forces it).

## Acceptance

- No text element on any board or the station paints below 4.5:1 after overlays, in Chromium and in Safari.
- The decoration is still there and still behind the words; the look at the centre of every board is unchanged.
- The token has headroom and a test keeps it; the reserved captions read.
