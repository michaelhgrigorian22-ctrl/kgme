---
id: AUDIT-CDH-0019-CHIP-BUDGET-REVIEW
type: report
created: 2026-10-28T00:40:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0019
  - AUDIT-CDH-0031-REVIEW
  - docs/audit/cockpit-design/cdh-0019-chip-budget.md
  - docs/design/cockpit-v0/ at 9c360af
  - logs/scratch/design-review/cdh-0019-chip-budget/
  - logs/scratch/design-review/cdh-0019-chip-budget-review/
tier: 2
status: final
handoff: CDH-0019
period: "2026-10-28"
reviewed_sha: 9c360af
review_canvas: "private artifacts: KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 19 (9c360af; the live body matched 5be85a8 before the publish); KGME Cockpit v0 review copy stays at service version 42 (5be85a8; no board changed)"
---

### Findings

None.

### Verdict

PASS. CW40 is closed; nothing else on the track is open. `9c360af` is the approval candidate.

### Notes

**Scope.** Cowork's native and standalone review of the CDH-0019 fix cycle for CW40 (`9c360af`): the deck's room chips back inside a vertical budget after the precision pass grew them. The cycle changes two declarations in `.chip-room` (`gap` 4 → 1 px, `padding` 8 → 4 px), adds the three-size overlap count to `tests/test_design_precision.py` with the chip exception listed, and nothing else; the report's scratch assertion that every other byte equals `002db55` is consistent with the diff (one line in the station, the test, the report, the README).

| check | Codex measured | Cowork measured | holds |
|---|---|---|---|
| Chip-to-chip overlaps, default framing | 0 / 0 / 0 at 400 × 700, 800 × 600, 1440 × 900 (2 / 4 / 0 before), normal and reduced motion; 7 distinct visible chips | Standalone on the committed page (`station9c.py`, two settled samples per size): **0 / 0 / 0**, chips 57 px and 40 px tall (71 / 51 on `5be85a8`, which the same run reproduces at 4 / 2 / 0). Natively at the pane's 800 × 600 on version 19 the seven chips sit clear of one another; Workshop beside Dock, Archive above Airlock (`native-station-v19-chips-clear.png`) | yes |
| The chips' width budget (CW34) | the 222 px event-line cap untouched | max chip width 223 px, as at `a73d62e` | yes |
| Focus ring after the change | 54 stops at three sizes, 2 px cyan, −2 px, all in view | Real Tab presses at 800 × 600 after the 120 ms transition: `2px solid rgb(57,208,255)` on `#pause`, all seven chips in order and the tray; every stop in the viewport | yes |
| Station contrast | 16 cases, 0 failures, minimum 4.5926 Chromium, 4.5299 Safari | Not re-swept here: the change is padding and gap on an opaque chip, every chip text surface stays on `#0a0c10`, and the sweep at `5be85a8` read the chips at ≥ 4.59; Codex's 16-case record stands | recorded |
| The standing test | `test_station_room_chips_have_zero_overlaps_at_default_framing` × 3 sizes; 489 tests | Read: the test projects the room anchors through the orthographic camera from the sources and lets Chrome lay the chips out, asserting 0 overlaps and 7 visible chips per size; the exception for the 1 px chip gap is listed. Not re-run on the VM; the gate output in the report is the record | recorded |
| Scope | 4 delivery files; ledger and inbox modifications excluded | `logs/ledger/2026-10.jsonl` and `memory/inbox/friction-log.md` are dirty in the worktree and belong to KGME's runtime, not to this cycle; left alone | yes |

**Rulings.** None. Codex scored its symmetric 4 px inset at 2 × 0.1 = 0.2 (the alternative, 8 px horizontal padding, left one 2.5 px overlap at 800 × 600); recorded on the open list.

**Evidence** is under `logs/scratch/design-review/cdh-0019-chip-budget-review/`; hashes taken on the Mac after delivery.

| File | SHA-256 |
|---|---|
| `station9c.py`, `station9c.json` (overlaps, heights, focus and follow on `9c360af` and `5be85a8` at three sizes) | `935a21b0d93b01d6a4ffd29ad588b9ee5bab6156368176c8bee0d7c5c53536ef`, `136ef3ccf602a99c7d967c05d9e7cbb36006cc599cf2d8b51d7d02f884cb3be9` |
| `native-station-v19-800x600.jpg`, `native-station-v19-chips-clear.png` | `3613f2e3b069a817f8edd66002a8584f1c253af3bcea0cf652a37618ce4acaeb`, `1b35425918e4b7c06239f82cbdc46fac322fbaf16afa317a977bd945bace3cba` |

**Next.** The canvas at `9c360af` has passed every row before approval: CDH-0030 (the WebKit check, repaired by CDH-0032), CDH-0031 (the precision pass, repaired here) and the declutter. The four design commits since `70b3412` land on `main` with its next commit; `kgme approve` accepts any commit on `main`, so once `9c360af` is an ancestor of `main` the command is `kgme approve --what canvas --sha 9c360af --note "…"`. This report is not that approval.
