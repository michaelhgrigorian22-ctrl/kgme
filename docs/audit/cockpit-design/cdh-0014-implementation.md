---
id: AUDIT-CDH-0014
type: report
created: 2026-10-15T23:50:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0014
  - tools/review/design-reference/ui-ux-pro-max/ at 85691f9
  - tools/review/design-prompt.md at 1f138f0
  - docs/design/cockpit-v0/ at d2f1d29
  - logs/scratch/design-review/cdh-0014/
  - logs/scratch/design-review/cdh-0015/
tier: 2
status: final
handoff: CDH-0014
period: "2026-10-15"
reviewed_sha: d2f1d29
review_canvas: "private artifacts: KGME Cockpit v0 review copy https://claude.ai/artifact/KYyjZUs7BqUgAikypG4Jsh version 28 (Tray, Keys); KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf version 5"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW22 | advisory | `Main.dc.html`, `Blocking.dc.html`, `Pending.dc.html`, `Wall.dc.html`, `Disconnected.dc.html` (the filter buttons) | Board 3's four filter buttons draw at about 20 CSS px tall (10 px type, 2 px padding, 1 px border). They pass `web-target-size` (ux-guidelines 104) by the spacing exception: 6 px gaps put their centres 26 px apart, so 24 px circles do not intersect; no host board was edited for it. | Michou's call: leave as drawn with this exception recorded, or raise them to 24 px in the five host boards in a later cycle. |
| CW23 | advisory | `station/index.html` (reduced motion) | Under reduced motion the replay starts paused and the control reads `play`; a reader who wants the demonstration presses `p`. This is the rubric's default (`auto-rotation-controls`, row 108: stop when reduced motion is requested) and Cowork's default for the page. | Michou may prefer the replay to run with walks and fades off, as before; one line to change. |

### Verdict

PASS

### Notes

**Authority.** Relayed by Michou on 2026-10-15 22:43 from the substantive Cowork session's review of `nextlevelbuilder/ui-ux-pro-max-skill`: a rubric only, never the generator. The rubric is vendored at `tools/review/design-reference/ui-ux-pro-max/` (`85691f9`, pinned `56ea9cf1`, MIT, three text files and the LICENSE, hashes in its `PROVENANCE.md`) and cited in `tools/review/design-prompt.md` (`1f138f0`) with the WCAG 2.1.4 rule the rubric lacks. One correction to the relay for the record: in the source repository the files sit under `.claude/skills/ui-ux-pro-max/`, and the live-badge rule is row 118 while `focus-not-obscured` is row 100.

**Delivered** on branch `design` as `d2f1d29`, one build with CDH-0015 (its report lists the four changed files and their hashes). What each check measured and changed:

| check | rule | what changed | measured (standalone, headless Chromium 1194 with SwiftShader, `check15.mjs`; manifest in `cdh-0014/` and `cdh-0015/`) |
|---|---|---|---|
| 1 count changes as one status | `contextual-live-badge-updates`, ux-guidelines 118 | The tray (board 11's bar, every host) and the station's HUD gain one visually hidden `role="status" aria-atomic="true"` span reading `active runs: <summary>`; nothing else in either is live; the station updates it only when the sentence changes. | One status region on the page, `aria-atomic="true"`, one live region in all; text `active runs: 1 working` → `active runs: 2 working · 1 transient` while a focused pane row stayed `document.activeElement`, connected, through the change. |
| 2 focus never obscured | `focus-not-obscured`, row 100; sticky navigation, row 2 | The station's pane top follows the measured HUD (`--hudtop`, set with the wall's padding in `layoutHud()` on resize and on every words refresh); at ≤ 720 px the pane's bottom follows the bottom HUD (`--hudbottom`). The boards' headers are in flow, not sticky, so their timelines scroll under nothing; no host board changed. | 1440 × 900: HUD bottom 134.9, pane top 147, the focused last row 279.9–325.8, bottom HUD from 826.1: clear. 400 × 800: HUD bottom 370.3, focused last row 557.0–603.0, bottom HUD from 666.2: clear (before the fix the row ran to 675.0 under the bottom HUD). Captures `standalone-pane-under-hud-*.png`. |
| 3 a pause for the replay | `auto-rotation-controls`, row 108 | A HUD control (`pause` / `play`, `aria-pressed`, one name `pause the replay, key p`) and the `p` key; the footer names it; under reduced motion the replay starts paused (CW23). | `p` froze the clock (19:44:36 at +1.2 s and at +3.2 s), the control read `play` with `aria-pressed="true"`; the control resumed it; under emulated reduced motion the page loaded paused at 19:40:00 with bloom off. Capture `standalone-paused-1440x900.png`. |
| 4 24 × 24 CSS px targets | `web-target-size`, row 104 | The tray's and the station's `Esc closes` buttons are 24 px tall (inline-flex, `min-height:24px`); the pause control 24 px; room chips, rows and the bar already taller. Board 3's filter buttons: the spacing exception, CW22. | Every visible button at 1440 and at 400: room chips 44 px tall, the bar 279 × 24, pause 88 × 24, `Esc closes` 78 × 24, rows 360 × 46; none under 24 in either list. |
| 5 WCAG 2.1.4 character-key shortcuts | the rule added to `design-prompt.md` | Board 7's intro says single-character keys act only while focus is on the cockpit's own surface and never inside a text field (the filter line takes text; there only Enter and Esc act), `?` lists them, remapping is Phase 2. The station's handler ignores events whose target is an input, textarea, select or editable element; its footer says so. | With a test-only text field focused: `c` did not toggle calm, `a` did not open the pane, `p` did not pause; the field received `cap`. Board 7's sentence is in the committed file and the review copy (version 28). |
| 6 the station against `stacks/threejs.csv` rows 1–9 | rows 1–9 | Recorded in the station README. 1 met (pinned `three@0.182.0`, core and addons on one release; the rubric's current 0.185.1 is a version choice for HANDOFF-0044). 2 not applicable (no capsules). 3 not applicable (no OrbitControls: a fixed isometric orthographic view, by design). 4 met by design: the drag pans the look-at target in the ground plane, both axes respond; there is no orbit to get wrong. 5 met (one ESM graph through the import map). 6 met (one `WebGLRenderer`; the `CSS2DRenderer` is DOM). 7 met (`Math.min(devicePixelRatio, 2)`). 8 not applied: the canvas composites over nothing (`#stage` is the opaque ground; the composer's targets are opaque), so the row's purpose does not arise. 9 met (orthographic bounds from the aspect on every resize, `updateProjectionMatrix()` called). | Source. |

**Observed natively** (the published artifacts in the browser pane, 800 × 1073): the station version 5 at 19:40:40 of the replay with the HUD's `replay · p` control reading `pause`, `hull · nominal`, and the footer's `p pause` and shortcut sentence; a click on the control paused the replay — the control read `play` in amber and the clock stayed at `19:41:00` across two captures a few seconds apart — and a second click resumed it. The frame does not take keys from the pane and does not expose its accessibility tree to it (as in CDH-0009), so the status region, the focus checks and the row names were measured standalone. The review copy version 28 carries board 7's sentence and the tray's status span.

**Evidence** under `logs/scratch/design-review/cdh-0014/` (hashes taken on the Mac after delivery; the manifest is the one run's, shared with `cdh-0015/`):

| File | SHA-256 |
|---|---|
| `standalone-pane-under-hud-1440x900.png` | `a4e3f5e8b1bf86bee63d2f3e3c42f84c3c630d5359ba4f1f8f798c6ffa09b7e7` |
| `standalone-pane-under-hud-400x800.png` | `22f1ddcca3f6687e5b2981c1116ff7fca0ada88d7fe0d032e3157637cd808667` |
| `standalone-paused-1440x900.png` | `dfb55906ff27be317fa2a2f5a50e2cf6fa00be65106cf356dcd5170dc58c86cc` |
| `manifest.json` | `df9f17a1f2269c4c0e8804395cd63032e2705f1ce8943af50ff3002326c85a5d` |
| `design-prompt-insert.txt` (the paragraph added to the prompt) | `1e796f9af88212319716706810bdf00fff95a245dc7ff6a30780260563dfe336` |
| `native-artifact-v5-pane-running.jpg` | `9b0ee4819eb0436763f5ff3959120f516e5cb18a7095d39472a345335be05d6b` |
| `native-artifact-v5-paused-hud-1.png` | `1dcf1d18996d5f78d6443d1222d0595a0c32e5ad7577380ed83de0fc909a6e87` |
| `native-artifact-v5-paused-hud-2.png` | `0af2a155eccfcfafa1ee8cad8023c85c9a8e337a668d1c223e435310bfafd80c` |

**Toolbox row (ADR-020):** follows when HANDOFF-0044 lands; the substantive session adds it to 0044's first rows.

**Next:** CDH-0016, Codex's read-only review of this and CDH-0015 at `d2f1d29`, is `ready` in the README's Codex queue — the first review under the cited rubric.
