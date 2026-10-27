---
id: AUDIT-CDH-0031-REVIEW
type: report
created: 2026-10-27T16:05:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0031
  - AUDIT-CDH-0031
  - docs/audit/cockpit-design/cdh-0019-declutter.md
  - AUDIT-CDH-0032-REVIEW
  - docs/design/cockpit-v0/ at 5be85a8
  - logs/scratch/design-review/cdh-0031/
  - logs/scratch/design-review/cdh-0031-review/
tier: 2
status: final
handoff: CDH-0031
period: "2026-10-27"
reviewed_sha: 5be85a8
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh, service version 42 (all 11 boards republished from 5be85a8; the live boards matched a73d62e before the publish; version 41 was an editor save); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 18 (5be85a8; the live body matched 0907f28 before the publish)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW40 | blocking | `station/index.html`, the room chips (`.chip-room`, their padding and line gap under the 8 px scale) | The precision pass grew the deck's room chips from 57 to 71 px tall (42 → 51 for the two one-line chips) and the overlaps CW34 closed at zero are back: at 800 × 600, four chip pairs overlap (Workshop over Dock by 107 × 12 px, Workshop over Engine room, Review chamber over Archive by 107 × 12, Airlock under Archive by 172 × 6); at 400 × 700, two pairs (Workshop/Dock and Review chamber/Archive, 87 × 3). At 1440 × 900 there are none. The same measurement on `a73d62e` gives 0, 0 and 0. Natively at the pane's 800 × 600 the Workshop chip sits on the Dock chip and Archive on Airlock (`native-station-v18-chips-overlap.png`). CDH-0031 A.1 says a documented size wins over the grid and is listed; the chips' width budget (222 px, CW34) was kept but their height was not budgeted, and the report did not measure chip-to-chip overlaps. | One fix cycle under CDH-0019: keep the 8 px scale where it fits, return the chips to a vertical budget that gives 0 chip-to-chip overlaps at 400 × 700, 800 × 600 and 1440 × 900 at the default framing (the 57 / 42 px of `a73d62e`, or any budget that measures 0), list the exception in `tests/test_design_precision.py` so the grid check allows it, and add the three-size overlap count to that test so it cannot come back. A check that failed, no score. |
| CW41 | record | `docs/audit/cockpit-design/cdh-0031-implementation.md`, the commit `5be85a8` | The declutter commit appended a "Coverage addendum" to the finished CDH-0031 report and reworded one sentence of its hashes section. An addendum is the track's way of correcting a final report (CDH-0023); the rewording is an edit of a finished record. Nothing in it is wrong. | Record; the lessons line already says finished records get addenda, not edits. 1 × 0.1 = 0.1. |

### Verdict

BLOCK: 1 (CW40). Everything else in CDH-0031 and the declutter holds and is recorded below; the canvas is not approvable until the chips measure 0 overlaps at the three sizes again.

### Notes

**Scope.** Cowork's native and standalone review of CDH-0031 (`5a03da1`, the precision pass, closed under the restated contrast rule Michou approved at 17:50 on 2026-10-26, tally 10 of 10) and the declutter commit under CDH-0019 (`5be85a8`, 37 cuts, Michou's direct instruction of the same time). ADR-023: the reviewer is never the builder; both reports are read as data and their checks repeated by other means. `main` has absorbed design through `70b3412` (HANDOFF-0062 cleared the landing); `5a03da1` and `5be85a8` land with its next commit.

**Delivered and republished.** The eleven boards at `5be85a8` were projected fresh from the committed sources (the shared projection module, the CDH-0027 method) and measured here; the committed files were published as review copy version 42 and the station body as KGME Station version 18, after the live files' hashes were compared with the previous publishes (no editor drift in either).

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| Contrast, the restated rule | board minima unchanged or better in both engines; every pair ≥ 4.5; 178 / 190 pair decreases, none over the 0.3 line that needs naming | Composited sweep of all 11 boards (`sweep31.py`, the AUDIT-CDH-0030-REVIEW method): 0 failures over 1,460 measured elements; every board minimum at or above its CDH-0032 reading (Main 5.00 → 5.02, Blocking 5.12, Wall 4.77 → 5.02; Sprites 5.203 → 5.185, a 0.018 difference inside this method's run-to-run noise, which Codex's record has as exactly equal in both engines) | yes |
| The 8 px scale, borders, type | every padding, gap and margin on the scale with the listed exceptions; 1 px `#1e2a33` structural borders; the 22/14/12/11/9 scale, tabular figures | Read in the sources and seen natively on boards 1 and 3 and the station; `font-variant-numeric: tabular-nums` on the clock and the HUD counts; not re-measured element by element (the precision tests are the standing record) | recorded |
| One easing, three durations | `MOTION = {120, 240, 480, cubic-bezier(0,0,.2,1)}`; follow 493.5 ms, pane 246 / 245.8 ms, chip ring 12.1 ms on Metal | Computed styles on the station: every transition 0.12 s `cubic-bezier(0, 0, 0.2, 1)` on the chips and HUD controls; `--response/--state/--travel/--ease` = 120 / 240 / 480 ms and the one curve; the only animations left are the `blink` and the cast's documented ambient ones. Durations are not re-timed here: SwiftShader paints a frame every 0.6 to 1.4 s, so Codex's Metal numbers are the record | yes (timing recorded) |
| One focus ring | 2 px cyan, −2 px offset, 120 ms, every surface | Standalone with real Tab presses after the transition: `2px solid rgb(57,208,255)`, offset −2 px, 0.12 s on `#pause`, all seven room chips in order, `#trayopen`; the pane's Tab in the browser pane did not reach the frame (the host takes it), so the ring is a standalone fact | yes |
| Response and settle | first response 10.2 ms; retarget settles 496.5 ms; an interrupted pane reverses from where it is | Escape closes the pane at 1440, 800 and 400 once a frame has painted (an earlier reading at 1440 was this harness's 500 ms wait being shorter than one SwiftShader frame); the pane hides through `onfinish`, so it reverses from its current state as the report says | yes |
| Calm, rooms, overflow, errors | — | Calm hides the stage, keeps 7 rooms, 3 / 1 / 1 columns at 1440 / 800 / 400, 0 px overflow; 0 page or console errors on the committed page at three sizes | yes |
| **Chip overlaps (CW34's budget)** | not measured in CDH-0031 or the declutter | **4 pairs at 800 × 600, 2 at 400 × 700, 0 at 1440** on `5be85a8`; 0 / 0 / 0 on `a73d62e`; natively visible at the pane's 800 × 600 | **no: CW40** |
| The declutter, 37 cuts | each cut listed with the retained fact, key or rule | Every row of the table read against the guard: each removed line carries no fact, names no key and states no rule that is not kept elsewhere (D13's no-dispatch rule stays in board 10's Rules; D25's reduced-motion rule stays there too; the quiet threshold, every "as of" and every key legend remain). Natively: board 1 without its header subline and the build attribution; the station's footer without "the station is decoration over the ledger" and the wall's calm note without its narration. Sprites and Tray change only by the cut text. 0 contrast change. | yes |
| The standing checks | `tests/test_design_precision.py`, 486 tests | Read; not re-run on the VM today; the gate output in both reports is the record | recorded |
| JetBrains Mono | uncertified | unchanged: the fixtures paint `ui-monospace` | recorded |

**Rulings.** None new from this pass. CW40 is a failed check, repaired in the fix loop without a score; the one addition to the record is CW41 at 0.1.

**Evidence** is under `logs/scratch/design-review/cdh-0031-review/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `sweep31.py`, `sweep31.json` (all boards at `5be85a8`, as painted and overlays hidden) | `1b81f2a39559b86399ad1c642142559217615053b775805d191b534d96120024`, `20e907134c8b316d3feca8ae2f167d411247d8f60566e7f61659e735133fa1da` |
| `station31b.py`, `station31b.json` (chip overlaps on `5be85a8` and `a73d62e` at three sizes, focus, follow, Escape, pane) | `d4250d7370f4e71f5256d274832bd7c0137d91d5786ce765c6df77a11b4fd034`, `afc4bfd11c560fa08ed8092ab9a41db1be42ea63a30e2096f7ab7eba8411a5c4` |
| `native-station-v18-800x600.jpg`, `native-station-v18-chips-overlap.png` | `e358a0d7a3d5025bd29ad0ab2cde95dc67643483648c45512790ca767bac7dd4`, `d71ceba579cbbddc6ba5efdf30997411705408037246a6fe0e909cd2baf90323` |
| `native-v42-board01-motion.jpg` | `597a22ef06e8ce1c2ed32f0e84097eb2fe921b7ba78280384a7354f78d13950b` |

**Next.** Codex takes CW40 as a CDH-0019 fix cycle (no row is `ready`; the fix loop applies the newest review's blocking finding). After it, Cowork's native pass of that cycle; if 0 overlaps hold at the three sizes and nothing else moved, that commit is the approval sha: `kgme approve --what canvas --sha <commit>`. This report is not that approval.
