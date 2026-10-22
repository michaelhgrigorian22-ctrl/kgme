---
id: AUDIT-CDH-0015
type: report
created: 2026-10-15T23:45:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0015
  - AUDIT-CDH-0013
  - docs/design/cockpit-v0/station/ at d2f1d29
  - docs/design/cockpit-v0/Tray.dc.html at d2f1d29
  - logs/scratch/design-review/cdh-0015/
tier: 2
status: final
handoff: CDH-0015
period: "2026-10-15"
reviewed_sha: d2f1d29
review_canvas: "private artifacts: KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 5; KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 28"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW21 | advisory | `station/index.html` (rows, `aria-label`) | A row's name is given explicitly after all (mapping, run, word, quiet, elapsed, event, chip, comma-separated), not left to its visible text: Chromium joins the row's inline spans without spaces (`kgme.review01M4F8NR…P04Ftransient4m 15s…`), which is unreadable as a name. The two are kept in step by `updateRow()`. | None; recorded because AUDIT-CDH-0013 F6 offered either route and the visible-text route failed in measurement. |

### Verdict

PASS

### Notes

**Ruling.** Michou, 2026-10-15 22:56: "go ahead", under the 2026-10-14 00:41 rule. Every finding of AUDIT-CDH-0013 taken.

**Delivered** on branch `design` as `d2f1d29` (`design: station cycle 3 (AUDIT-CDH-0013 F1-F6) and the rubric checks (CDH-0015, CDH-0014)`), one build with CDH-0014; four design files changed, the sample, the cast and the other boards byte-identical to `dd90ca6`:

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/station/index.html` | `6bede5e68377b45366e5aa844d5184e8905e6d68f69dc3d674f99e45cd04501f` |
| `docs/design/cockpit-v0/station/README.md` | `ce60ff78a5db634219935836700663d317cbf2a36c41fa8869d3db0f2389bf97` |
| `docs/design/cockpit-v0/Tray.dc.html` | `72e5d11cd22bdc9af65711d06dfee3493bf6623f2b6c87a707d2e3e0d87bfd34` |
| `docs/design/cockpit-v0/Keys.dc.html` (CDH-0014) | `6ab106dcc65cfb2ddc27648942d69b3b2f8688e4d52eec3279ff38a32fd2e4f5` |

`tests/test_design_sprites.py`: 30 passed. `kgme lint`: 0 blocking. The station's body (the artifact) is the committed page without its wrapper, sha `dc1cbca6b2eea29bef6ead46bdde45a151a0ed91eef70d6fe5760fbb093acb2d`.

**Finding by finding.** "Evaluated" is the page's own functions run in Node on the committed sample and on constructed sequences (`check-lifecycle.mjs`, output `lifecycle-eval.txt`); "standalone" is headless Chromium 1194 with SwiftShader on the VM, the committed body served over HTTP with the import map pointed at the vendored `three@0.182.0` (`manifest.json`: served shas, wrapper, viewport, the replay clock before and after each capture).

| id | ruling | what changed | closed by |
|---|---|---|---|
| F1 | take | `activeHalt(run)`: the newest `halt:` note that no intent, outcome or approval has followed, the same subsequent-activity rule `lifecycle()` uses; `snapshot()` reads it for the hull text, the wall and the hull colour. | Evaluated: exhausted retry → `transient`, hull `nominal`; halt → `blocked`, `HALT`; halt then an ordinary note → `blocked`, `HALT`; halt, note, then approval → `transient`, `nominal`; halt then approval → the same. In the page, with the synthetic sample (a bookkeeping note at 19:53:30 between the halt and the approval): at 19:53:40 the HUD reads `HALT · …` and the review chamber `1 blocked · ruled 19:53:30`; at 19:54:35 `nominal` and `1 transient`. |
| F2 | take | `resize()` measures the HUD first (for the pane and the wall) and returns before sizing when the stage is hidden; `setCalm(false)` calls `resize()` before the next frame. | Standalone: `c`, viewport 1440 × 900 → 1200 × 800, `c`: canvas 1200 × 800, stage 1200 wide, all seven room buttons visible inside the viewport with 44 px boxes, the Workshop button focusable; at 400 × 800 → 360 × 700 likewise (canvas 360 × 700, seven chips visible). Captures `standalone-deck-after-calm-resize-*.png`. |
| F3 | take | The ordinary median (the mean of the two middle gaps for an even count), said in board 11's two anatomy copies, the README and the code. | Evaluated: gaps 180 s and 600 s → 390 s; 450 s after the last event `quiet 7m`, 380 s after it no suffix. The boards' samples are unchanged (`quiet 4m` on `3f9e…` at 19:52:14). |
| F4 | take | AUDIT-CDH-0012's evidence table now carries the hashes on the Mac (Codex's measured values) with the cause stated: the report had been delivered from a stale upload before its table was refreshed after the final capture run. Committed `1f138f0`. | The table matches `shasum` on the Mac for all thirteen files. The delivery path now uses a fresh staged path for every report. |
| F5 | take | The synthetic approval's `status` is `null`; the file gained the bookkeeping note F1 needed, so it is 43 lines. | On the Mac, `kgme.events.validate_event` over the file: 43/43 valid. The evaluation was rerun on the corrected file. |
| F6 | take | Crew wrappers are no longer `aria-hidden`; only the portrait svg is (`chibi()` sets it), so a crew member's tag and its last bubble — a fixture's last summary — are readable outside calm. Rows carry a complete name (CW21). | Standalone, outside calm at 19:43: zero bubbles under an `aria-hidden` ancestor of six; the guard's bubble text `19:42:02 refused: Read names a blocklisted path memory/private/ (guard rule 4) refused` is exposed (`getByText` finds it twice: the bubble and the row); the review run's row is found by role with the name `kgme.review 01M4F8NR…P04F, transient, 4m 15s, cycle 1 tooling exhausted · not a strike · retry after 23:06, blocking` — the transient lifecycle and the blocking chip both in the name. |

**Observed natively** (the published artifacts in the browser pane): see AUDIT-CDH-0014's native section for the station version 5 and the review copy version 28; the native and standalone observations are shared between the two reports since the build is one.

**Evidence** under `logs/scratch/design-review/cdh-0015/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `standalone-deck-after-calm-resize-1200x800.png` | `538345946d1af46af1223a9f084c8b3ab37b7545e7911c75e511bb1d787f7093` |
| `standalone-deck-after-calm-resize-360x700.png` | `35326c8d59f2aff293f89968ad0e02302df8224332ff28a5d203cca2d0bd70e3` |
| `manifest.json` | `df9f17a1f2269c4c0e8804395cd63032e2705f1ce8943af50ff3002326c85a5d` |
| `sample-events-halt-synthetic.jsonl` (43 lines, test only) | `db20ca89ab973d8c43c9bc43ed256c60187ca66f9440f427ea8f3abfaa500558` |
| `lifecycle-eval.txt` | `f15b2e009501be88238f34171bf925a1905f907a1014c253618094c39b2bbeef` |
| `check15.mjs` | `91888a2d152a8f06641c4233eab6eb78e8947398e7ea2f835059acf727de927a` |
| `check-lifecycle.mjs` | `029741840c083ec296e026e75bddeacb34e51230b843d6af77aca542f19513be` |

**Still open for Michou:** as before (CW12, CW13, CW16–CW20, Codex's three taste notes), plus the reduced-motion default of CDH-0014 (the replay starts paused).

**Next:** CDH-0016, Codex's read-only review of this cycle and CDH-0014 at `d2f1d29`, is `ready` in the README's Codex queue. This report is not Michou's design approval.
