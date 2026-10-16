---
id: AUDIT-CDH-0017
type: report
created: 2026-10-16T00:45:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0017
  - CLAUDE.md on main at 3fd6855 (ADR-023, "How decisions are made")
  - docs/design/cockpit-v0/ at 2e14d66
  - docs/handoff/cockpit-design/README.md ("Open list, scored") at 2e14d66
  - logs/scratch/design-review/cdh-0017/
tier: 2
status: final
handoff: CDH-0017
period: "2026-10-16"
reviewed_sha: 2e14d66
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 29; KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 6"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW24 | advisory | `docs/readers/cockpit-design-lessons.md` | The lessons file lives under `docs/readers/`, not at the `docs/handoff/cockpit-design/lessons.md` path the relay named: schema v1.4 lets a note live only under `docs/`, `docs/plans/`, `docs/readers/` or the vault, and `kgme lint` blocks it in a handoff folder (only `README.md` is exempt, `kgme/vault.py`). The README, the queue prompt and CDH-0017 point at the reader path. | The substantive track may add a `lessons.md` exemption beside README's in `kgme/vault.py` if ADR-023's per-skill convention is wanted literally; then the file moves back in one commit. |
| CW25 | cosmetic | `station/index.html` (bubbles) | Of ten bubbles measured at three moments, one touched a chip's bottom edge by a pixel (a front-row crew member's bubble against the room in front's chip). Nothing was covered; the other nine were clear. | Accept; or hang bubbles 4 px lower. Below the threshold (1 × 0.2). |

### Verdict

PASS

### Notes

**Authority.** ADR-023 (`git show main:CLAUDE.md`, accepted 2026-10-16), relayed by the substantive session on 2026-10-15 23:30: checks over questions; judgement calls scored and asked only at stakes × edge ≥ 1.5, batched, with a recommendation each; rulings executed; build for addenda; a lessons file read at the start of every CDH. Every open item of the design track was scored; the table is the README's "Open list, scored" section and is reproduced in short below. Three items are asked in one brief after this report; the rest were decided here.

**Delivered** on branch `design` as `2e14d66` (`design: the open list under ADR-023 (CDH-0017)`): five host boards, the station page and README, the lessons file, the queue prompt (reads the lessons first), the README (scores, rules, rows); `tests/test_design_sprites.py` 30 passed; `kgme lint` 0 blocking.

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/Main.dc.html` | `b2010aef6498bf452b99fe574ad65fd841f1229e38d1f17d52073399163d4017` |
| `docs/design/cockpit-v0/Blocking.dc.html` | `ec2c61c00c4bcc085a78f77e0c1628807c42acd5ec844dae673890cac06f7b6e` |
| `docs/design/cockpit-v0/Pending.dc.html` | `15cb75b53c47267ff85689e0646a1cff068581f82c8cfd2dab5176e523e414da` |
| `docs/design/cockpit-v0/Wall.dc.html` | `e939782d18b31c7e3826d836d6a658f8fd3979f6891c5c8636b3f016000833cb` |
| `docs/design/cockpit-v0/Disconnected.dc.html` | `4e13f38b0113f91be1b316820193d6d45b79220e4e2b975a6e0480e0f8f03592` |
| `docs/design/cockpit-v0/station/index.html` | `e14eac978ef4c3f4db9a28a61e2181a698683d62bed3b8da08ae24c09156d67c` |
| `docs/design/cockpit-v0/station/README.md` | `ddccdff36108a52c13855b40fb4095fdd0a1576a0f997b23c6edd2efc5afffc9` |
| `docs/readers/cockpit-design-lessons.md` | `c550111071bc69e79ac4a704451fba23190d4adabf5466eecc2e854a87a1b61e` |

**Checks, run and fixed** (contrast by the arithmetic AUDIT-CDH-0008 and AUDIT-CDH-0013 use: linearized sRGB, (L1+.05)/(L2+.05), a filter applied to the text before the ratio):

| id | what changed | measured |
|---|---|---|
| CW17 | Boards 3, 4, 5 and 9: every inline `style="color:#6f8290"` (13, 9, 13 and 17 spans) became `class="mut"`; `.mut{color:#6f8290}` and `.focus .mut{color:#7a8d9b}` sit after each board's `.focus` rule, so the focused timeline row's time, job and Δt read `#7a8d9b` on that board's focus tint. | `#7a8d9b` on `#0e1a22` (boards 3, 9) 5.137:1; on `#1c0f16` (board 4) 5.411:1; on `#1a150c` (board 5) 5.284:1. The unfocused pair is unchanged (`#6f8290` on `#11151c`, 4.593:1). |
| CW18 | Board 6: its 29 `#6f8290` tokens became `#a3b0b8`, and a rule lifts the mounted tray's muted classes the same way under `.stale`. | Under `saturate(.12) brightness(.72)`, `#a3b0b8` becomes RGB (124.2, 125.3, 126.0): 4.764:1 on the ground `#0a0c10`, 4.670:1 on the filtered panel; `#6f8290` was 2.901:1. The next candidate down, `#9aa7b0`, fails at 4.353:1. |
| CW22 | Boards 3 and 4: the four filter buttons carry `min-height:24px` (board 5 and 9 draw none). | 24 px by the box; before, about 20 px with a 26 px pitch (the spacing exception, now unnecessary). |

**Decided below the threshold and built** (standalone, headless Chromium 1194 with SwiftShader, `check17.mjs`; the halt captures use the 43-line synthetic sample):

| item | score | what changed | measured |
|---|---|---|---|
| CW16, Codex taste 2 | 2 × 0.3 = 0.6 | A bubble hangs below its crew member's tag (`top: calc(100% + 16px)`, the arrow pointing up) instead of rising above its head, where it met the room's chip. A first attempt beside the crew put bubbles under the chips of their own room and was measured, rejected and replaced. | Bubble boxes against chip boxes at three moments: 3 of 3 clear at the refusal, 1 of 1 clear under the halt, 5 of 6 clear at the note with one touching a chip's bottom edge by a pixel (CW25). Captures `standalone-deck-bubbles-below-*.png`. |
| CW19 | 2 × 0.3 = 0.6 | The HUD's hull field shows `HALT · <the note's key>`; the wall's header and the review chamber's line keep the sentence. | Under the synthetic halt: HUD `HALT · halt:review:HANDOFF-0040`, wall header `HALT · halt: review:HANDOFF-0040 struck out three times (ADR-016); nothing moves until Michou approves`; the HUD stays two rows (135 px). Captures `standalone-*-halt-key-1440x900.png`. |
| Codex taste 1 | 2 × 0.5 = 1.0 | The deck's home framing (`HOME`, the camera's look-at) moved from (0.5, 0, 0) to (−0.8, 0, −1.4), chosen from three probes. | The top chip's top edge 76 px under the HUD at 1440 × 900 (was 23 px); 185 px at 2560 × 1080; the deck's lowest chip 250 px above the footer. |
| Codex taste 3 | 2 × 0.3 = 0.6 | The calm grid's columns are at least 400 px (`minmax(400px, 1fr)`). | Six columns of 403 px at 2560 (were seven of 341). Capture `standalone-calm-wall-2560x1080.png`. |

**Decided below the threshold and kept as drawn** (recorded, no build): S7 the quiet threshold (2 × 0.3); CW12 the third header line (2 × 0.4); CW13 board 9's header (2 × 0.3); CW20 the empty portrait column in calm (1 × 0.2); CW23 the replay paused under reduced motion (2 × 0.4); crew size on the wall (2 × 0.5); bubble persistence (2 × 0.4); the sticker placement (2 × 0.6); the mood micro-label copy (1 × 0.5); `Enter` in the tray sets the `r` filter (3 × 0.4). Those at ≥ 0.5 are listed for the approval screen in the README.

**Asked, batched, in the brief that follows this report:** the station's look as a whole (4 × 0.7 = 2.8; recommendation: keep the direction and iterate in cycles); whether the station replaces or joins board 9's wall when the cockpit is built (4 × 0.6 = 2.4; recommendation: joins, `w` cycles desk → wall → station); whether "you" should resemble Michou (3 × 0.8 = 2.4; recommendation: no likeness, the chalk silhouette stays). The README records whether each recommendation is taken.

**Evidence** under `logs/scratch/design-review/cdh-0017/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `standalone-deck-bubbles-below-at-refusal-1440x900.png` | `15029e9e90db9b5e96eb65365148589d9893b3c5da2465bd569d0dad2c65bf6a` |
| `standalone-deck-bubbles-below-at-note-1440x900.png` | `9eff0adf47935e1c69ad7b0af1b8df4607a1f99662cb0bb2abffd104a9e8b475` |
| `standalone-deck-halt-key-1440x900.png` | `b3db9c2d60f433c8d094b660c56bdc2879c4c5fd6669b6d1e5bbf7bcb39c9f3a` |
| `standalone-calm-halt-key-1440x900.png` | `b9ec162872d89d2b3a1c2bc0604e3c95c9687f475fe254fbc545bf40f471f0fe` |
| `standalone-calm-wall-2560x1080.png` | `38e66ebb96d19bfaef4c53a800618b53eb37e74a3fbb123a56273970b5b3b00f` |
| `manifest.json` | `169385641de9d50427ac3e6c7f8372201783306cc21c38a6ffd02e7b79b56f11` |

The scripts (`check17.mjs`) and the first draft of the lessons file (`lessons-first-draft.md`, before the frontmatter and the move) sit beside them. The review copy version 29 carries the five boards; KGME Station version 6 the station.

**Next:** CDH-0018, Codex's read-only review of this cycle at `2e14d66`, is `ready` in the README's Codex queue behind CDH-0016. This report is not Michou's design approval.
