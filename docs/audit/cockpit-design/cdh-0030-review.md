---
id: AUDIT-CDH-0030-REVIEW
type: report
created: 2026-10-26T00:40:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0030
  - AUDIT-CDH-0030
  - docs/design/cockpit-v0/ at 0907f28
  - logs/scratch/design-review/cdh-0030/
  - logs/scratch/design-review/cdh-0030-review/
tier: 2
status: final
handoff: CDH-0030
period: "2026-10-26"
reviewed_sha: 5b84c41
review_canvas: "nothing republished: no design source changed at 5b84c41. The private artifacts stay at review copy service version 39 and KGME Station version 17 (both 0907f28)."
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW37 | blocking (F1 widened) | every desk board and the wall; `.lbl`, `.mut`, `.micro`, `.tr-*` and the key legends at `#6f8290`; the overlays `.vig` (z 2), `.frame` (z 3), `.scan` (z 4) in each board's head | AUDIT-CDH-0030's F1 names Main's clock label (2.13:1). The mechanism is wider than a corner: the muted token `#6f8290` on the panel tint `#11151c` is 4.59:1 by the CSS pair and paints at 4.47 to 4.55:1 in every renderer measured (Codex on Metal 4.554; this review on SwiftShader 4.484), so it has no headroom, and the three overlays sit above the words and take the edges and corners to 1.6 to 3.9:1. Standalone, 238 of 1,524 measured text elements fail across the eleven boards as painted (113 below 4.0); with the overlays hidden, 82 muted-token elements still fail at 4.47 to 4.48. Sprites and Tray carry no overlays and still show the token at the edge. | One repair row, **CDH-0032**: the overlays go beneath the text layer and the muted token moves to `#7a8d9b` (CDH-0017's focused-row token, 5.1:1 on the tint before overlays); verified by composited-pixel sampling of every text element on every board and the station. Layering 3 × 0.2 = 0.6, token 2 × 0.3 = 0.6, both decided and listed for the approval screen. |
| F2 | blocking (confirmed) | `Keys.dc.html:36–38`, `.f2 small` and `.f2 b` at `#3a4650` | Board 7's twelve reserved-key captions ("approve · p2", "decline · p2", "model · p2", "queue message · p2" and their keys) paint at 1.91:1 on `#0e1218` here, 1.94 in Codex's two engines. They are readable descriptions, not disabled controls. | Into CDH-0032: the captions at the muted token, the key frame stays dashed and inert. 2 × 0.2 = 0.4. |
| F3 | advisory (confirmed, a note) | Safari's keyboard setting | Plain Tab leaves focus on the document unless "Press Tab to highlight each item" is on; Option-Tab reaches all seven rooms. Not a page defect; the station's focus order is the one every earlier review measured. | Recorded on the README's WebKit line; no row. 1 × 0.2 = 0.2. |
| CW38 | correction (a record) | `docs/handoff/cockpit-design/2026-10-25-webkit-check.md`, the observation paragraph added in `68e1ae0` | The paragraph says Safari rendered the station but "no clickables ran anything and no keybinds did much". Codex's audit shows every key and click working in WebKit; Michou clarified he had clicked into Safari's automation window while the tests ran, and a window under WebDriver ignores a human's input. The handoff is `done`, so its body is not edited: this entry, the README's WebKit line and a `docs/corrections.md` entry on `main` (outside the design lanes; drafted for Michou) are the correction. | A lessons line: don't judge a page from a Safari window under WebDriver. |

### Verdict

PASS on the audit; the audit's own verdict (BLOCK: 2) stands, both findings taken, and the canvas at `0907f28` is not approvable until CDH-0032 lands.

### Notes

**Scope.** Cowork's review of AUDIT-CDH-0030, Codex's read-only WebKit check of the design at `0907f28` (committed `5b84c41`). ADR-023: the reviewer is never the builder; Codex's report is read as data and its two blocking findings reproduced by other means. No WebKit is reachable from here (container, VM and pane are Chromium), so the Safari-specific facts are taken from Codex's evidence under `logs/scratch/design-review/cdh-0030/` (safaridriver on Safari 26.6.2, `safari-manifest.json`, `validated-pixels.json`) and the contrast facts are reproduced in Chromium, which the audit shows paints the same.

**Method, this review.** The eleven boards were rendered from Codex's CDH-0027 static projections (`logs/scratch/vendor/cdh-0030-<board>.html`, whose `inputs.json` hashes match the design files at HEAD) in headless Chromium 1243 under SwiftShader at device scale 2 and each board's `canvas.json` size, with animation stilled. For every element holding text: A, the board as painted; B, the same board with every glyph fill transparent (`-webkit-text-fill-color`), which is the composited ground under each word, overlays included; a white-fill capture per non-overlapping group of elements gives per-pixel glyph coverage; the element's ratio is the minimum WCAG contrast of its reconstructed full-coverage colour over B across its ≥ 90 % pixels. The same again with `.vig`, `.scan`, `.frame`, `.tx` and `.ty` hidden. Disabled controls (8) and visually hidden text (65) are listed and excluded; 149 elements with no painted glyph pixel at the floor (mostly 9 px micro-labels and the sprite sheet's captions) are listed as unmeasured. Script and results: `sweep30.py`, `sweep30.json`.

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| F1, Main's clock label | 2.1255:1 Safari, 2.1196 Chromium at (40, 32) | 2.2434:1 at (52, 36), [63,77,88] on [8,13,17]; with the overlays hidden 4.85:1 on the ground | confirmed |
| F1, the mechanism | "ordinary labels on the other operating boards show the same overlay mechanism" | 238 of 1,524 elements below 4.5 as painted (Main 42, Wall 59, Blocking 31, Pending 28, Empty 26, Keys 13, Components 10, Tray 10, Disconnected 10, Phase2 6, Sprites 3); 113 below 4.0, every one under an overlay at an edge or corner; the `◦ ◦ ◦` micro-label at (60, 883) is the floor on five boards at 1.55 to 1.63 | confirmed and widened |
| the muted token's headroom | Sprites and Tray minimum 4.554:1 (no overlays) | the same boards 4.484:1; overlays hidden on every board, 82 `#6f8290` elements at 4.47 to 4.48 and none above 4.49; CSS pair 4.593 | new: CW37's second half |
| F2, board 7's captions | 1.9352 Safari, 1.9419 Chromium | 1.9118:1, [57,69,79] on [14,18,24], twelve captions, the same with overlays hidden | confirmed |
| F3, Safari's Tab | 22 Option-Tab observations per width, 0 obscured | not reproducible here; `focus-probe.json` read; consistent with every earlier Chromium focus pass | taken as a note |
| the station | 16 cases, minimum 4.554 over 164,944 points after the departing-crew frame is discarded | not re-measured: the station has no overlay above its text (every surface opaque, AUDIT-CDH-0027-0029-REVIEW), and `validated-pixels.json` shows the 1.015 deck case replaced by a settled 4.882 | recorded |
| interaction in WebKit | 7 digit keys, `a`, `Esc`, `c`, `p`, `r`, pane buttons by native click, 0 errors at two sizes | not reproducible here; `interaction-timing.json` and `safari-manifest.json` read; Michou's clarification on the record | taken |
| frame intervals, fonts | 16.67 ms mean at 1440; one 1.6 s stall at 400 under occlusion; remote font not certified | SwiftShader is not a benchmark; the font caveat carries into CDH-0032's verify (the fixture paints `ui-monospace`) | recorded |

**Why both halves.** Moving the overlays beneath the words alone leaves the token at 4.47 to 4.55 as rendered, one CSS filter or one tint away from failing again; raising the token alone leaves the corners at 2:1. `#7a8d9b` is already the focused-row value on the same boards (CDH-0017, 5.1 to 5.4:1 before overlays), so the change is a token value, not a new colour. The vignette, glow, scanlines and tick rails keep their place in the look (the one rule: noise that carries no fact), only below the text.

**Rulings this pass**, both below the asking line, decided and listed on the README's open list: where the overlays sit in z (3 × 0.2 = 0.6) and the token change inside CDH-0032 rather than CDH-0031 (2 × 0.3 = 0.6). CDH-0031 stays as written and follows CDH-0032; its contrast line ("unchanged or better on every text pair") now reads against CDH-0032's composited numbers.

**Evidence** is under `logs/scratch/design-review/cdh-0030-review/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `sweep30.py` | `3c88a7faea59323fa42914d6f69c2ed743575e7e3ae86d3dbbe6c70c776267d3` |
| `sweep30.json` (per element, as painted and overlays hidden, all boards) | `72fb30b00c7eaf834d3c28a530f8ee4a5fbc7cd4aff41175bb5e5814de6db4d3` |
| `Main-A.png`, `Main-B.png` (as painted; glyphs transparent) | `759d260bc573be00584d74edfe114c7f93dd97dde4ea607271759f062d68a36f`, `59457bf7d5da66dc529335237887f2682ff97ae50ed9021667556eabe4d8c161` |
| `Keys-A.png`, `Keys-B.png` | `759a2352a825413c77f6b6ab6dc12904157310921c7404581f0931ef42ec9f54`, `a9eac22771870a1852e554b378d4036d6510f78e8078a06d695a5aecf3c75040` |
| `Wall-A.png` | `dd3dcc726b8a2edf1013e797d0ad7883b78735b2d421488529e561ff266c3619` |

**Next.** CDH-0032 is queue row 20, `ready` now; CDH-0031 (row 19) follows its native pass; the approval sha is the commit after both: `kgme approve --what canvas --sha <commit>`. This report is not that approval.
