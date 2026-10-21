---
id: AUDIT-CDH-0016
type: report
created: 2026-10-21T01:24:31-07:00
handoff: CDH-0016
period: "2026-10-21"
source: inferred
sources:
  - CDH-0016
  - CDH-0001
  - AUDIT-CDH-0001
  - AUDIT-CDH-0003
  - AUDIT-CDH-0012
  - AUDIT-CDH-0013
  - AUDIT-CDH-0014
  - AUDIT-CDH-0015
  - ADR-016
  - ADR-017
  - docs/readers/cockpit-design.md
  - control/review/design-prompt.md
  - control/review/design-reference/ui-ux-pro-max/
  - docs/design/cockpit-v0/ at d2f1d295c5292c2cb43278caae4982e92b7aa99c
  - logs/scratch/design-review/cdh-0012/
  - logs/scratch/design-review/cdh-0014/
  - logs/scratch/design-review/cdh-0015/
  - logs/scratch/design-review/cdh-0016/
author: codex
status: final
tier: 2
reviewed_sha: d2f1d295c5292c2cb43278caae4982e92b7aa99c
---

## Findings

The station's two blocking findings from AUDIT-CDH-0013 are repaired at the reviewed SHA. The full design gate still finds two older host-board contrast failures, already identified as CW17 and CW18 and scheduled for independent verification of their later CDH-0017 repair. This report judges the historical tree, not the current worktree. Paths below are relative to docs/design/cockpit-v0/ unless stated otherwise.

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | Main.dc.html:34, :148; Wall.dc.html:33 and its muted timeline cells | At this SHA, inline muted text #6f8290 remains on cyan-focused background #0e1a22: 4.4317:1, below the 4.5:1 gate. The station and tray already use #7a8d9b and pass at 5.1371:1. The other two host tints pass for this pair: Blocking 4.6681:1; Pending 4.5583:1. This is the existing CW17 defect, not a station regression. | Verify CDH-0017's class-based muted override on boards 3 and 9; preserve the other boards' chosen tints. |
| F2 | blocking | Disconnected.dc.html:36, :59-64 | The stale wrapper applies saturate(.12) brightness(.72) to #6f8290 text. Linearized-sRGB contrast of the filtered header text against #0a0c10 is 2.9006:1. The mounted tray's repaired summary does not repair its host's timestamp suffix, labels and stale metadata. This is CW18. | Verify CDH-0017's lighter muted token through the actual filter and cascade, including the mounted tray. |
| F3 | advisory | docs/audit/cockpit-design/cdh-0015-implementation.md, F2 closure; cdh-0015/manifest.json, resizeWhileCalm400 | Seven nonzero chip boxes are not proof that seven chips fit inside the viewport. The 360 by 700 capture visibly clips room labels at both horizontal edges; the phone manifest has only chipsVisible: 7 and no chip rectangles. The 1200 by 800 rectangles and screenshot do support restoration there. | Keep the historical audit unchanged. Qualify the phone claim in this review: the deck returns, but complete chip containment is not established; use viewport-intersection bounds for future captures. |

## Verdict

BLOCK: 2 blocking findings at d2f1d29, both pre-existing host contrast defects; the station cycle's original blocking findings are closed.

## Notes

**Scope and identity.** The 26-file design tree was extracted from d2f1d295c5292c2cb43278caae4982e92b7aa99c without checking out or changing design source. Compared with the previous reviewed dd90ca6 tree, only station/index.html, station/README.md, Tray.dc.html and Keys.dc.html differ. The source-set SHA-256 is `bec170c0b9fa1e3c6cdfbe1219b65e92301a12afb0fbd6c6f32d05e79c163e4a`, using sorted UTF-8 records of repository path, NUL, file SHA-256 and LF. The scratch manifest lists every file. The canvas order, native support mechanism, canonical cast and shared motion files remain unchanged. The review supports Michou's approval process and the next scoped build; it grants no canvas or application approval.

| Reviewed source | SHA-256 |
| --- | --- |
| `Keys.dc.html` | `6ab106dcc65cfb2ddc27648942d69b3b2f8688e4d52eec3279ff38a32fd2e4f5` |
| `Tray.dc.html` | `72e5d11cd22bdc9af65711d06dfee3493bf6623f2b6c87a707d2e3e0d87bfd34` |
| `station/README.md` | `ce60ff78a5db634219935836700663d317cbf2a36c41fa8869d3db0f2389bf97` |
| `station/index.html` | `6bede5e68377b45366e5aa844d5184e8905e6d68f69dc3d674f99e45cd04501f` |
| `station/sample-events.jsonl` | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |

**AUDIT-CDH-0013 closure.** Independent Node evaluation used functions extracted from this exact station source, not a rewritten lifecycle. The exhausted retry returns transient/nominal; the halt and halt-plus-bookkeeping cases return blocked/HALT; approval returns transient/nominal. Separate subsequent intent, outcome and approval cases all clear the active halt. All five null-parent root intents remain waiting. With gaps of 180 and 600 seconds, the 390-second ordinary median produces no quiet suffix at 380 or 390 seconds, then quiet at 391 and 450 seconds. Both tray anatomy copies and the README use that same convention.

With a zero-size hidden stage, resize performs zero camera or renderer writes. Returning at 1200 by 800 and 360 by 700 produces finite horizontal bounds of approximately ±12.30 and ±4.21714 respectively and sizes all four render targets; setCalm(false) calls resize. These are function evaluations with controlled dimensions, not browser observations. The two supplied resize captures show a returning scene; F3 limits the phone containment claim.

All 15 supplied CDH-0012 evidence hashes match its corrected table; its four historical design-file hashes also match dd90ca6. All eight CDH-0014 and eleven CDH-0015 table hashes match, including four delivered design files. The committed 40-record sample and supplied 43-record synthetic sample both pass kgme.events.validate_event. The handoff's older count of 42 is superseded by the report's explicit extra bookkeeping event. The named synthetic approval has null status. Only decorative SVGs remain aria-hidden in crew wrappers; updateRow supplies mapping, abbreviated run, lifecycle, quiet suffix, elapsed time, event and chip in its complete explicit name. The supplied accessibility measurements report zero hidden bubbles out of six and one review row found by its full role/name; no new accessibility-tree observation is claimed.

**Rubric checks.** The station has one atomic contextual status region, updated only when its full sentence changes. The tray declares it only in its bar branch; the pane does not duplicate it. Supplied measurements report one station live region and retained connected focus through a count change. The supplied focused pane row is between both HUDs at 1440 by 900 and 400 by 800; these are the specific tested states, not proof for every room button or replay moment. The source measures HUD heights and offsets the pane, with a bottom constraint at phone width.

Independent evaluation confirms that pausing freezes replay time, resuming does not accumulate the paused interval, and all five tested character shortcuts do nothing for editable targets. The control retains its toggle name and aria-pressed state; reduced motion starts it paused. Supplied screenshots show play at 19:41:00 in both native HUD crops. Live motion preference, actual speech and native keyboard behavior were not exercised here. Supplied station targets are at least 24 by 24 CSS pixels. The host-board filter exception recorded by CW22 is a historical allowance, not a new independent measurement; CDH-0018 checks the later explicit 24-pixel minimum. Board 7 states focus scope and its text-field exception.

Three.js rows 1, 5, 6, 7 and 9 are met in source: one pinned 0.182.0 ESM graph, one WebGLRenderer, DPR capped at 2, and orthographic bounds/projection updated on visible resize. Rows 2 and 3 do not apply: no capsules or OrbitControls. Row 4's orbit recipe does not govern the chosen pan interaction, whose two axes both contribute. Row 8's alpha-compositing premise does not apply to this opaque stage. The station adds no remote font or dispatch/approval action; the only declared external package is the pinned three.js import map. The native artboards retain their established editor support and allowed font links, as AUDIT-CDH-0003 records.

**Cast and performance.** The unchanged seven assets total 54,782 bytes and 582 SVG elements; shared CSS/JS brings the total to 76,295 bytes, below 512 KiB. AUDIT-CDH-0001 supplies the two prior approximately 30-second target-Mac fixture profiles: 50 static portraits and one selected detail, 33.33 ms mean RAF intervals in both motion and calm, zero long tasks, input-to-next-frame p95 27.60/29.20 ms and scroll p95 0.20/0.10 ms. These are attributed historical cast measurements, not station or native-canvas performance. The just-completed merge gate passed all 360 tests, including the unchanged cast drift checks; no source changed during this review.

**Images actually inspected.** All eight current images below were opened. The five standalone PNGs belong to Cowork's Chromium 1194/SwiftShader VM run; the three native artifact captures are supplied native evidence, not a new Codex session. Their manifests identify a local wrapper and the committed station body. That body hash matches the report; the local wrapper and local three.js copy are unavailable in this worktree, so no fresh standalone station rendering was attempted. Phone overlap and clipping remain visible; still images do not prove interaction or screen-reader output. Native interaction and station target-Mac performance remain unverified by Codex.

| Image under logs/scratch/design-review/ | SHA-256 |
| --- | --- |
| `cdh-0014/standalone-pane-under-hud-1440x900.png` | `a4e3f5e8b1bf86bee63d2f3e3c42f84c3c630d5359ba4f1f8f798c6ffa09b7e7` |
| `cdh-0014/standalone-pane-under-hud-400x800.png` | `22f1ddcca3f6687e5b2981c1116ff7fca0ada88d7fe0d032e3157637cd808667` |
| `cdh-0014/standalone-paused-1440x900.png` | `dfb55906ff27be317fa2a2f5a50e2cf6fa00be65106cf356dcd5170dc58c86cc` |
| `cdh-0014/native-artifact-v5-pane-running.jpg` | `9b0ee4819eb0436763f5ff3959120f516e5cb18a7095d39472a345335be05d6b` |
| `cdh-0014/native-artifact-v5-paused-hud-1.png` | `1dcf1d18996d5f78d6443d1222d0595a0c32e5ad7577380ed83de0fc909a6e87` |
| `cdh-0014/native-artifact-v5-paused-hud-2.png` | `0af2a155eccfcfafa1ee8cad8023c85c9a8e337a668d1c223e435310bfafd80c` |
| `cdh-0015/standalone-deck-after-calm-resize-1200x800.png` | `538345946d1af46af1223a9f084c8b3ab37b7545e7911c75e511bb1d787f7093` |
| `cdh-0015/standalone-deck-after-calm-resize-360x700.png` | `35326c8d59f2aff293f89968ad0e02302df8224332ff28a5d203cca2d0bd70e3` |

**Independent check artifacts.** These text files remain gitignored under logs/scratch/design-review/cdh-0016/.

| File | SHA-256 |
| --- | --- |
| `check-source.mjs` | `5229500ee7b6e98bbe8e2d97938fe45c4d44063d1af412813a16ea10b1845bfb` |
| `source-checks.json` | `b9b9e37d0f5233376b3eec8e6d3685b715c3c14a63c1e01535aa706ab7434d5d` |
| `contrast.json` | `ace7a5648f7ce7341480ecfbef07cafaa9d57d3e036bf23a0edc6938cc0e4a0c` |
| `source-manifest.json` | `6826ff61324c11577172148dbf4dea6e5c7ddf44f4687cce15b912d2222008af` |

**Scores and taste.** F1/F2 are measured checks, so require no judgement score. F3's evidence qualification is 1 × 0.1 = 0.1: record it without rewriting history. The first three taste changes remain the previously scored HUD-to-deck separation (2 × 0.5 = 1.0), bubbles away from room chips (2 × 0.3 = 0.6), and wider calm-grid columns (2 × 0.3 = 0.6); all are already assigned to CDH-0017 and are not new requests. The three existing personal-judgement questions remain with Michou.

Report validation: `uv run --no-sync kgme lint --root docs/audit/cockpit-design` returned 17 notes, 0 blocking, 15 advisory and 1 cosmetic; this report has only the expected advisory for `reviewed_sha`.
