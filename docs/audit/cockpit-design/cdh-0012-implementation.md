---
id: AUDIT-CDH-0012
type: report
created: 2026-10-14T01:25:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0012
  - AUDIT-CDH-0011
  - docs/design/cockpit-v0/station/ at dd90ca6
  - docs/design/cockpit-v0/Tray.dc.html at dd90ca6
  - logs/scratch/design-review/cdh-0012/
tier: 2
status: final
handoff: CDH-0012
period: "2026-10-14"
reviewed_sha: dd90ca6
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 26 (Tray); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 4"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW19 | advisory | `station/index.html` (HUD, `#hull`) | Under a halt the hull field carries the note's summary (up to 200 characters); at 1440 the HUD wraps to three rows while it does, pushing `following` down. It wraps rather than overflows (`max-width:64ch`), and a halt is meant to shout. | Michou's call: keep, or show only the note's key (`halt:review:HANDOFF-0040`) in the HUD and the full summary in the wall and the pane. |
| CW20 | cosmetic | `station/index.html` (rows) | In calm the rows keep the empty 24 px portrait column, as the tray does (visibility, not display), so text does not move between the deck and the wall. Reads as a small indent. | Accept, as the tray's F6 decision; or collapse the column in calm, which moves the text. Michou's call. |

### Verdict

PASS

### Notes

**Ruling.** Michou, 2026-10-14 00:41: "it should honestly just commit and keep working in these situations." Taken as the loop's default from now on: Codex commits its own delivery and continues the queue; Cowork applies blocking findings as the next cycle at once and he vetoes after the fact. The per-finding rulings below are therefore Cowork's defaults; the one he may want to see is S7.

**Delivered** on branch `design` as `dd90ca6` (`design: station cycle 2 and tray T1 (CDH-0012)`), after `a3558b1` (Codex's report) and `e0d8aaf` (the loop rule, the queue prompt, CDH-0012 and CDH-0013). Three design files changed; the sample ledger, the cast and every host board are byte-identical to `4f3e06c`:

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/station/index.html` | `35b5a05a2d022e319e96cba883fb44d87fc987fc2b22682439d4be6db7e50cf7` |
| `docs/design/cockpit-v0/station/README.md` | `d46c1189c0fcbac832a4c53401fb8b83ca636169476ecdd5f5cb898b4d67e42d` |
| `docs/design/cockpit-v0/Tray.dc.html` | `72799fd6c707e78a35d6d6b0ff151b9f90ba8938bef9c8a7116dac44e5118e5b` |
| `docs/design/cockpit-v0/station/sample-events.jsonl` (unchanged) | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |

`tests/test_design_sprites.py`: 30 passed. `kgme lint`: 0 blocking. The station's body (the artifact) is the committed page without its document wrapper, sha `6f97fb17b72f42ffd008aa92afdf2ad43b0a0d9e575add019dbc36ed911771c7`.

**Finding by finding.** "Source" means the committed file; "evaluated" means the page's own function run in Node on the committed sample (`check-lifecycle.mjs`, output `lifecycle-eval.txt`); "standalone" means headless Chromium 1194 with SwiftShader on the VM, the committed body served over HTTP with the import map pointed at the vendored `three@0.182.0` (`manifest.json` records the served shas, the wrapper, the viewport and the replay clock before and after every capture, because a SwiftShader screenshot takes seconds).

| id | ruling | what changed | closed by |
|---|---|---|---|
| S1 | take | `snapshot(now)` builds one textual record every 250 ms — clock, ledger line, the hull (`nominal`, or `HALT · <the note>` while a `halt:` note is a run's newest event), the tray summary, each room's state line, each run's row, and the last event of the bridge (Michou's note or approval), the airlock (the guard's last refusal) and the review chamber (the arbiter's last ruling), kept as text after their bubbles fade. The HUD, the chips, the pane, the wall and the lights all read it. The wall now sits under the HUD (`z-index:5`, padded by the HUD's measured height; the HUD gets the ground colour in calm), so calm keeps the clock, the ledger counts, the replay counter, the session, the harnesses, the hull and the summary. A `hull` field joins the HUD; the wall header repeats it. | Standalone, calm at four moments (`calmByReplayPosition` in the manifest): at the refusal (19:42:04) the airlock says `refused · guard rule 4` and its wall line carries the refusal with its chip; at the note (19:47:24) the bridge says `you · noted 19:47:20` with the note as a line; after newer events (19:52:18) the bridge says `you · asleep · last note 19:47:20`, the airlock `guarded · last refusal 19:42:02`, the review chamber `1 transient · ruled 19:49:10` with the ruling as a line; under a synthetic halt (19:53:04) the HUD and the wall both read `HALT · halt: review:HANDOFF-0040 struck out three times (ADR-016); nothing moves until Michou approves`, the review chamber `1 blocked`, the hull magenta; after the synthetic approval (19:54:34) `nominal`, the bridge `you · approved 19:54:30` with the approval as a line. The HUD is displayed in calm (`display: flex`), zero portraits visible. Captures below. |
| S2 | take | `lifecycle()` follows the written rules in order: a blocking note holds `blocked` only while no intent, outcome or approval has followed it; the exhausted-retry exception and the recorded class stay; `waiting` is the newest intent-or-outcome being an intent, whatever its `parent`; then quiet. | Evaluated: the five root intents of the sample (events 1, 7, 15, 19, 22) return `waiting` as the newest event; a blocking note as the newest event returns `blocked`; the same note followed by an intent returns `waiting`, by an intent and an outcome `working`, by an approval `working`. At the boards' moments: builder `c70d` at 19:47:00 `working · quiet 4m`, at 19:52:14 `waiting` (board 5); builder `3f9e` at 19:52:14 `working · quiet 4m` (board 3); the review run `transient` from 19:43:03 on (board 3); the Codex thread `waiting` while its pytest runs. In the page the halt note made the review run `blocked` and the approval lifted it. |
| S3 | take | `aria-hidden` moved from `#stage` to the canvas; the crew (portrait, tag, bubble) is wrapped `aria-hidden` because its facts are the rows'; the HUD's portrait stack likewise. Each room button carries `aria-label="<n> <name>: <state>"`, refreshed with the state. | Standalone: `getByRole('button', { name: /^2 Workshop/ })` finds 1, the seven room buttons are exposed (`roomButtonsExposed: 7`), `#stage` has no `aria-hidden`, the canvas has it, all 3 crew wrappers present at that moment are hidden. |
| S4 | take | `syncRows()` keys pane and wall rows by run id and updates them in place (`updateRow`: mode, word, quiet, elapsed, event, chip, label); only a run that left is removed, and if it held focus the next row takes it. The wall's seven sections are built once. The painted `.focus` is the drawing's default on the first row only while no row really has focus; `.row:focus-visible` shows the same tint under the 2 px outline. | Standalone: the first pane row focused, 1.5 s (six refreshes) later `document.activeElement` is the same element, still connected, and no row is painted `.focus` while a row has real focus; `Tab` moves to the next row (`className: row`). Capture `standalone-pane-focused-row-1440x900.png`. |
| S5 | take | `.row.focus` and `.row:focus-visible` colour the run id, the second line, the quiet suffix and the `—` chip `#7a8d9b`. | Standalone computed style on the really focused row: background `rgb(14, 26, 34)`, `.run` and `.l2` `rgb(122, 141, 155)` (the quiet suffix and the muted chip were not present on that row; the rule covers them by selector). 5.1371:1 on `#0e1a22`. |
| S6 | take | The three Google Fonts tags are gone; the type is the system monospace (`'JetBrains Mono'` first in the stack resolves locally or not at all). The README and the page comment say so. | Standalone request list: one host (the local server), paths `/station/local.html`, the vendored package, the seven SVGs, the sample; `anyFontRequest: false`. In the repository page the only remote origin is jsDelivr's pinned package. |
| S7 | take, Cowork's default | One threshold in three places (board 11's two anatomy copies, the station README, the code): quiet when a working run has had no event for longer than its median gap between intents, never less than three minutes; with fewer than two intents, three minutes. **Not the threshold CDH-0012 first wrote** (three times the median): that one contradicts board 3's own drawn sample (`3f9e21aa … quiet 4m` at 19:52:14 has a 233 s median gap, which three times over is 11.6 min), while the median with a floor reproduces every drawn sample. | Evaluated above: `quiet 4m` on board 3's run, `quiet 4m` on the first builder at 19:47, `working` without quiet while under the floor. Michou may still change it. |
| S8 | take | The preference is observed live: a `change` listener and a once-a-second poll (an emulated change in Chromium does not always fire the listener) call `setMotion()`, which adds or removes the bloom pass and snaps walks and the camera; `<html data-motion data-bloom>` carry the state for checks. Calm skips walks, the camera and the two renders; the 250 ms words refresh stays, now a keyed update. | Standalone: `data-motion=full, data-bloom=on` → under emulated reduce `reduced, off` → restored `full, on`. |
| S9 | take | Fresh standalone captures from the committed source, each with the served sha, the wrapper, the viewport and the replay clock before and after the shot (`manifest.json`). The two earlier captures AUDIT-CDH-0011 questioned (`cdh-0009/standalone-calm-wall-2560x1080.png` with four portraits, `standalone-phone-400x800.png` with micro labels) were taken from a development build of the template before the `body.calm .chibi` and the 720 px rules were added, and were not retaken; they stay as attributed historical captures of CDH-0009's development, not of its committed source. | New `standalone-calm-wall-2560x1080.png`: zero portraits, no micro labels, no horizontal scroll; `standalone-calm-wall-400x800.png`: the same at 400 px (`scrollWidth 400`, the wall's `scrollWidth 400` after `#wall .val{white-space:normal}`). |
| T1 | take | `Tray.dc.html`: the button reset is `.tr-root :where(button)` (zero specificity), so `.tr-row` keeps its padding and border and `.tr-focus` its tint; the focused-row colour rule moves after the base rules and covers `.tr-quiet` and `.tr-muted`; `.tr-row.tr-focus:hover` keeps the tint. | Headless computed style on the tray's own CSS: focused row background `rgb(14, 26, 34)`, padding `5px 6px`, border-top 1 px, run id, second line, quiet suffix and muted chip `rgb(122, 141, 155)` (5.1371:1), the tint kept under hover; a plain row's run id `rgb(111, 130, 144)` on the panel (4.5926:1), hover `rgb(15, 20, 27)`. Published as review-copy version 26. |

**CW15's cause, found and fixed in passing.** Observing version 3 in the browser pane, the replay jumped from 19:43 to `19:40:00 · replay 2` the moment the pane came back from hidden: a backgrounded tab pauses `requestAnimationFrame`, and the first frame after it resumes carried a delta of a minute or more, which at ×20 pushed the clock past the loop's end and reset it. The per-frame delta is now capped at one second of real time (`Math.min(t - lastReal, 1000)`), so a hidden tab merely pauses the replay. This is why the first published version "did not loop in the pane" in AUDIT-CDH-0009 (it had looped past the end while hidden).

**Two test affordances** were added to the page for the captures and are documented in the README: `?speed=N` (replay rate 1–60, default 20) and `?at=HH:MM:SS` (start the replay there). Both are read-only query parameters; nothing else in the page reads the URL.

**Observed natively** (the published artifacts in the browser pane, 800 × 1073): the station version 3 at 19:43:24 of the replay — the deck with two builders, the reviewer at the dock gate, the guard braced, the HUD's new `hull · nominal` field, the airlock chip reading `refused · guard rule 4` during its flash, the tray `2 working · 1 transient` — then the loop jump described above, which version 4 fixes. Keys do not reach the page from the pane (the frame does not take focus from the pane's click, as in CDH-0009), so calm, the pane and focus were observed standalone, not natively. The review copy opens at version 26 with the cycle-2 tray; its focused row was measured by computed style, not captured natively this cycle.

**Evidence** under `logs/scratch/design-review/cdh-0012/` (hashes taken on the Mac after delivery; the PNGs are Chromium's own, nothing re-encoded):

| File | SHA-256 |
|---|---|
| `standalone-pane-focused-row-1440x900.png` | `074005e29fdc1e4b98db0e7c5730f95cbd655efdbafc15d1ec6c168c9713ef87` |
| `standalone-calm-at-refusal-1440x900.png` | `c2011273c54889e07d71b4c131724f553f4cb0e2f2a5c915d68783763823686c` |
| `standalone-deck-at-refusal-1440x900.png` | `0384b8523f863591b0f25ad3d4e4d376f507fe127195889ee28b5d2a7169e574` |
| `standalone-calm-at-note-1440x900.png` | `c24ed636c7d8510cd92f103468546c66b74dc68c7061b17741a26d92dccc47e9` |
| `standalone-calm-after-newer-events-1440x900.png` | `83126976074b1ee2d09440f9751b1ac3fcdaacc298dfe405726e3a49c58221b8` |
| `standalone-calm-at-halt-1440x900.png` (synthetic sample) | `c5bb216576745e6a9428c38fce98e712a4f451a953431c60ce96b086b725074f` |
| `standalone-deck-at-halt-1440x900.png` (synthetic sample) | `746ea858c51a34bd10bc5449c2c2457dc7b6d27a06070ca9f7a8ae2019e1e0d0` |
| `standalone-calm-after-approval-1440x900.png` (synthetic sample) | `66a0ba13f3fe0a93fa57815b45f284e30db0f98ba5e1d3fcedc2410bc8646839` |
| `standalone-follow-workshop-2560x1080.png` | `55cb4d6dea9af3ac0ec82703501d3ac49f2ad444e5a42e02745eea844eaa1414` |
| `standalone-calm-wall-2560x1080.png` | `33f2ddba4fa34cd9b293418903c22deeca0d7d95526ce30a3140d1ff38f9b2f2` |
| `standalone-deck-400x800.png` | `b4dd61a43f036d9fd05fa09ea3f97bb496f8ce593372987ddc036a4c16e64522` |
| `standalone-calm-wall-400x800.png` | `528aabf646b03fa901321c71552990db5bd6a394970d8746822fb7909754768c` |
| `manifest.json` | `c436e2ba2b25497cf3ddefd1013c11f63c822eaa82177d4317d2053a63cbe67a` |
| `sample-events-halt-synthetic.jsonl` (the committed 40 lines plus a `halt:` note at 19:53:00 and Michou's approval at 19:54:30; test only) | `4bce8a97237465822bd832f3c03ff67dd023a9e8a447a32920d6684436f7b551` |
| `lifecycle-eval.txt` | `e7908de90f28e7e76647a647dcd47aca4e6ac9d536f3dd5322a21d7fd5079e8f` |

The scripts that produced them sit beside them (`check12.mjs`, `check12b.mjs`, `check12c.mjs`, `check-lifecycle.mjs`).

**Still open for Michou:** CW12, CW13, CW16, CW17, CW18 as before; CW19 and CW20 above; Codex's three taste notes from AUDIT-CDH-0011 (a clear band between the HUD and the room labels, bubbles away from the chips, wider wall rows at 2560); the station's look as a whole.

**Next:** CDH-0013, Codex's read-only re-review at `af714e9`, is `ready` in the README's Codex queue. This report is not Michou's design approval.
