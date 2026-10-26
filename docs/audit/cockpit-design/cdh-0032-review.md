---
id: AUDIT-CDH-0032-REVIEW
type: report
created: 2026-10-26T12:40:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0032
  - AUDIT-CDH-0032
  - AUDIT-CDH-0030-REVIEW
  - docs/design/cockpit-v0/ at a73d62e
  - logs/scratch/design-review/cdh-0032/
  - logs/scratch/design-review/cdh-0032-review/
tier: 2
status: final
handoff: CDH-0032
period: "2026-10-26"
reviewed_sha: a73d62e
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 40 (all 11 boards republished from a73d62e; the live boards matched 0907f28 before the publish, so version 39 had no editor drift); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf stays at version 17 (0907f28; the station source is byte-identical at a73d62e)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW39 | cosmetic (a record) | the eight HUD hosts, `.micro{background:#0a0c10}` | The corner micro-labels gained a ground-colour backing, which the handoff did not name: where a tick rail passes behind `KGME` or `◦ ◦ ◦`, the rail is interrupted by the label's box. Natively the break is a few pixels and reads as the label sitting on the rail; Codex's reason is sound (lowering the rail alone still composites under a 9 px word). Under the one rule the micro-labels are noise and carry no fact, so this is cosmetic. | Record; 1 × 0.2 = 0.2. If a later look wants the rails continuous, the labels can sit above the rail line instead of on it. |

### Verdict

PASS

### Notes

**Scope.** Cowork's native and standalone review of CDH-0032 (`a73d62e`, AUDIT-CDH-0032): the repair of AUDIT-CDH-0030's two blocking contrast findings, widened in AUDIT-CDH-0030-REVIEW (CW37). ADR-023: the reviewer is never the builder; Codex's report is read as data and its checks repeated by other means. The row was adopted at 00:50 and stopped at preflight on the unattended sandbox (AUDIT-CDH-0032-PREFLIGHT); it resumed attended at 09:50 under the substantive session's ruling of 09:34 and closed at 10:46.

**Delivered and republished.** The eleven boards at `a73d62e` were projected fresh from the committed sources with the shared projection module (`logs/scratch/design-review/cdh-0026/projection.mjs`, the CDH-0027 method), not taken from Codex's "after" fixtures, and measured here; the same committed files were published as review copy version 40 after the live boards' hashes were compared with `0907f28` (all eleven matched: no editor drift since version 39). The station source hashes `44afe7ef…` at `0907f28`, `b1e1d77` and `a73d62e`; `chibi/` is unchanged; KGME Station stays at version 17.

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| Every text element as painted, 11 boards | 323 → 0 failing runs in Chromium, 323 → 0 in Safari, over 1,592 / 1,594 default runs; minima 4.68 (Blocking) to 7.72 | Same method as AUDIT-CDH-0030-REVIEW (`sweep32.py`: glyph fills transparent for the ground, a white-fill capture per non-overlapping group for coverage normalised to each element's own brightest pixel, the full-coverage colour reconstructed, minimum over ≥ 90 % pixels), SwiftShader Chromium at device scale 2: **238 → 0 real failures** over 1,524 measured elements; minima 4.77 (Wall) to 7.54; the two residual readings on Blocking (3.36 and 3.48 at x = 1123) are the method's last-column artifact, not the board: the ground is the flat panel tint in both captures, nothing sits above the text there, and the same elements measure 5.30 and 5.20 from their interior pixels (`crop-1123-108.png`) | yes |
| The token's headroom (CW37) | `#6f8290` → `#7a8d9b` on every text declaration; Sprites and Tray change only token values | With the overlays hidden, 0 elements below 4.5 on any board (82 before); `#7a8d9b` on the panel tint reads 5.00 to 5.20 here; the Sprites and Tray diffs against `b1e1d77` are the token substitution and nothing else; the component sheet now states the value and the measurement rule | yes |
| The overlays beneath the words (F1) | `.vig`/`.flood` at z −3, `.frame`/`.tx`/`.ty`/`.sweep` at −2, `.scan`/`.static` at −1, the hosts isolated; text at 0 and above | Read in the sources; as painted and with the overlays hidden now give the same minima on every board, which is what "nothing above the words" looks like in numbers. Natively (version 40, pane at 800 × 600 and emulated 1440 × 1000, board 3 and the wall at 2560): the clock label, `KGME`, the key legend and `◦ ◦ ◦` read at the corners with the vignette visibly behind them; the centre of every board looks as before | yes |
| Board 7's captions (F2) | `.f2 small`, `.f2 b` at the token; frames dashed `#3a4650`, inert | 1.91 → 5.20 standalone; natively the reserved captions ("approve · p2", "decline · p2", "model · p2", "queue message · p2", "command · p2") read in grey inside dashed frames, no active state | yes |
| Geometry unchanged | 0 changed text rectangles on all 11 boards | Element boxes identical between the `0907f28` and `a73d62e` sweeps (same counts per board, same positions); nothing moved natively | yes |
| The standing check | `tests/test_design_contrast.py`, 404 tests pass | Read: the CSS-pair floor at 4.8:1 per token and surface with the disabled grey as the one exclusion, the overlay z-order below the text layer in every host, `#3a4650` on no text outside disabled controls. Not re-run here (no dev environment on the VM for the design tree's test suite today); Codex's gate output is the record | recorded |
| Safari | 323 → 0, 16 station cases 0 failures; 17 Wall runs occluded by the fixed layout not claimed | No WebKit here; `safari-manifest.json` and the per-run JSON read; the 17 occluded Wall runs are the fixed wall layout's own clipping, not a contrast claim | recorded |
| Fonts | `ui-monospace` painted; JetBrains Mono unavailable to the fixture, not fetched | The same here; the remote-font path stays uncertified, as the README's WebKit line says | recorded |

**Rulings.** None new. The two of AUDIT-CDH-0030-REVIEW (layering 0.6, token 0.6) and F2's 0.4 are built as decided and stay on the approval screen; CW39 is recorded at 0.2.

**Evidence** is under `logs/scratch/design-review/cdh-0032-review/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `sweep32.py` | `70a52cd0ce1c723b445341cf451235177e36788802672f0b68509fd3d16576f1` |
| `sweep32.json` (per element, as painted and overlays hidden, all boards at `a73d62e`) | `f25ba809f66d21d02ca663d2bce0fbe90b4b7737c6a09ba75f141b0757cca808` |
| `Main-A.png`, `Main-B.png` | `418e648d4687a6a31f346502d84164199484e0d7b901ce28c38da50b0790350f`, `5ffedd897325436cecfa23b9b5a000470f5877c55b5587f16ce615a8398ce116` |
| `Keys-A.png`, `Blocking-A.png`, `Wall-A.png` | `d1ca64724f29d253aa8400bceaab8cb17d727437157ae612e702a4c2ad61c79e`, `6b7e1682ecc8507f66375aeac44f23ecdf3b32bb4063520b8097d31d66779ad0`, `705650859dd7400265a1353cc71edf62d0907f531a384b3eba35f18b33d7cef9` |
| `crop-1123-108.png` (the last-column artifact, as painted over the ground) | `930912bca1febd6d1e61f3204a59c58b2c085d6108cc0bdd165d7f63d19b617a` |

**Next.** Row 19, CDH-0031 (the precision pass), is `ready`. Its contrast line reads against this report's numbers: unchanged or better on every text element, measured as painted. The approval sha is the commit after CDH-0031's native pass: `kgme approve --what canvas --sha <commit>`. This report is not that approval.
