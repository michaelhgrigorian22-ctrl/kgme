---
id: AUDIT-CDH-0008
type: report
created: 2026-10-13T15:54:42-07:00
handoff: CDH-0008
period: "2026-10-13"
source: inferred
sources:
  - CDH-0008
  - CDH-0007
  - CDH-0001
  - docs/handoff/cockpit-design/README.md
  - docs/readers/cockpit-design.md
  - tools/review/design-prompt.md
  - docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md
  - ADR-016
  - ADR-017
  - memory/notes/cockpit-wishlist.md
  - AUDIT-CDH-0001
  - AUDIT-CDH-0003
  - AUDIT-CDH-0005
  - AUDIT-CDH-0007
  - docs/design/cockpit-v0/ at 5182d6ab65e2a7f7b299f04ff1f9f00e3a7f5205
  - tests/test_design_sprites.py
  - logs/scratch/design-review/cdh-0007/
  - logs/scratch/design-review/PROVENANCE-2026-10-12.md
author: codex
status: final
tier: 2
reviewed_sha: 5182d6ab65e2a7f7b299f04ff1f9f00e3a7f5205
---

## Findings

Paths in this table are relative to `docs/design/cockpit-v0/` unless stated otherwise. The 3 blocking findings apply the explicit contrast and semantic-control rules in `docs/readers/cockpit-design.md`; they do not require a working application or reinterpret the native template syntax.

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | `Tray.dc.html:33`, `:35`, `:38`, `:814` | The focused row combines muted `#6f8290` run IDs, elapsed time and latest-event text with ground `#0e1a22`. Its calculated contrast is **4.4317:1**, below the required **4.5:1** at 10/11 px. This fails even with calm on and every decorative overlay removed. The same pair is used by the pane and both anatomy examples, so the new tray inherits a failing focus treatment. | Give focused muted text a passing colour or retain the approved `#11151c` surface with the existing outline. Verify the actual focused pair at or above 4.5:1 in boards 1, 3, 9 and 11; do not round 4.4317 up to the threshold. |
| F2 | blocking | `Disconnected.dc.html:33`, `:57`, `:64`; `Tray.dc.html:27`, `:805` | Board 6 mounts the 14 px `stale` summary inside `filter:saturate(.12) brightness(.72)`. The muted token becomes approximately RGB **(90.03, 91.67, 92.88)**, yielding **2.9006:1** on `#0a0c10`, before the optional static/vignette layers. Thus `stale`, the 2 lifecycle counts and `as of 19:52:14` are text but fail the 4.5:1 readability rule. Calm does not remove this filter. | Preserve a passing text treatment outside the dimming filter, or choose a post-filter text colour that meets 4.5:1. Keep the stale word and timestamp explicit; grey portraits alone cannot replace them. Recheck the mounted board-6 tray, since the standalone sheet does not apply the parent's filter. |
| F3 | blocking | `Tray.dc.html:798`, `:811`, `:814`, `:826`; the repeated sheet/board row templates | The tray promises open, close and jump-to-run actions, but its action labels are spans and its selectable run rows are plain divs. The source contains **0 buttons, links or tabindex attributes**. The drawn focus outline does not make a row a semantic action target. This violates the review's real-button/link rule and board 7's mouse-access promise; a printed `Enter` hint does not provide equivalent access. | Draw the open/close actions as named buttons and the run jump as a real button or link, including a visible focus state. Apply this to all 3 row templates. Preserve the sample-only canvas and keep application event handling within HANDOFF-0037. |
| F4 | advisory | `Tray.dc.html:872`, `:873`, `:935`, `:936`, `:990`; `Main.dc.html:228` | The written transient rule requires the latest outcome to have class transient and promises an amber chip. The exhausted-review sample instead shows lifecycle **TRANSIENT** with a **BLOCKING** latest-event chip, repeated on boards 3, 5, 6 and 9. Distinct lifecycle and event-class fields are valid, but these 2 rules do not explain the sample's retry-after-exhaustion exception or its precedence over the blocked rule. | Specify the scheduled-retry exception and rule precedence in both copies of the anatomy text, or align the sample with the stated rule. Keep the recorded blocking event class intact; do not change it merely to match a pose. |
| F5 | advisory | `Tray.dc.html:975`, especially `:978` and `:980` | The 3-run sample reads `2 working · 1 transient · 1 quiet`, while its pane correctly says `3 open`. Quiet is counted inside working and then displayed beside the other counts with the same separator. The arithmetic is internally consistent as an overlapping subset, but the collapsed wording invites a 4-run reading without the anatomy explanation. | Make the subset explicit, for example `2 working (1 quiet) · 1 transient`, or show the total with an equally explicit qualifier. Preserve the requested quiet fact and the 3-open total. |
| F6 | advisory | `Main.dc.html:167`; `Tray.dc.html:93`, `:795`; `docs/audit/cockpit-design/cdh-0007-implementation.md:77` | Native calm with the tray mounted was explicitly not observed in CDH-0007, and none of the 12 supplied images establishes it. The parent props, child attribute and hide rule are present, and source evaluation preserves every row fact, but that does not verify the native import boundary or unchanged layout under the tweak. | In the next authorized native verification, capture board 3 before/after its parent calm tweak with both tray instances mounted, checking hidden portraits, retained words and unchanged geometry. Record reduced-motion observation separately if available. |

## Verdict

BLOCK: 3 blocking findings.

## Notes

The review covers CDH-0007's active-runs tray on boards 1, 3, 4, 5, 6, 7 and 9, plus its board-11 component, at `5182d6ab65e2a7f7b299f04ff1f9f00e3a7f5205`. It supplies Michou's disposition decision and Cowork's next design iteration. It does not approve HANDOFF-0036 or begin HANDOFF-0037. The result is 3 blocking findings and 3 advisories. All 23 design files were read or parsed and matched byte-for-byte against that commit before their worktree paths were used. The initial branch was `design`, HEAD was `86b7aca04a35736cd6c51d9d1bb64cdb72a675fc`, and git status was clean. Boards 2, 8 and 10 and the canonical cast were reviewed as context; unrelated pre-existing design issues are outside this tray verdict.

**What passes in the scoped design.** Each expanded row supplies 6 text fields: actor mapping, short run ID, lifecycle, elapsed time, latest-event summary and event-class chip. The 100% board-3 and board-11 captures show them, including `working` with `quiet 4m`, and the distinct transient lifecycle/blocking-class case in F4. The requested count, lifecycle, quiet, stale and class facts are not conveyed solely by colour or portrait. The collapsed view is a lifecycle aggregate; actor mappings are explicit in the expanded pane. The 24 px portrait geometry, phosphor materials and crops match board 10 and the canonical SVGs. The run IDs match the corresponding board-3 group headers, and tray rows leave the existing 22 px event-row design untouched. The captured run IDs remain legible, so this review does not raise a clipping finding on them.

Board 7 has exactly 1 physical `a` keycap, now solid and labelled `active runs`, plus 1 explanatory legend entry. These repeat 1 action rather than define competing bindings. The legend includes the tray-specific Enter/run-filter outcome; its j/k, Enter and Esc meanings are contextual navigation. The new component adds 0 application key handlers and introduces no competing `a` binding. It contains 0 dispatch, approval or model-choice controls. References to Phase 2 in its explanatory rules are not controls. Board 4 retains the written halt and blocking count, and board 6 explicitly retains the last-known counts with stale and timestamp, subject to F2.

**Checks performed in this review.** `uv run --offline --no-sync pytest -q -p no:cacheprovider tests/test_design_sprites.py` passed **30 tests in 0.03 s**, with bytecode and pytest cache writes disabled. The 14 body comparisons and 14 material comparisons cover 7 actors across boards 10 and 11; 1 additional check compares their shared chibi CSS and 1 checks the 7 portrait crops. The test source was also identical to the reviewed commit. Its SHA-256 is `5e811848a5fd6bbcf209f39fa6c9164951a831723e202a29de89fb0c0a182c64`.

An in-memory Node evaluation of the actual component classes, with only a minimal DCLogic props stub, reproduced the 5 host summaries: board 3 and board 9 each have 3 open runs; boards 4, 5 and 6 each have 2. For all 5, changing calm preserved the complete decorated run records and summary. An empty input produced `idle`, and an unknown actor with an explicit mapping selected the stranger artwork. This is a source-data check, not native rendering, keyboard execution or layout measurement. The component has 0 portrait instances with `is-animated`; the copied 15-keyframe library therefore adds no eligible portrait animation. Its calm selector hides artwork using visibility, preserving its boxes, and its reduced-motion media rule disables symbol animation. Native import/tweak behaviour remains subject to F6. The source adds no independent tray motion; existing host-board effects are not new tray animations.

Contrast was calculated from source sRGB tokens with linearized relative luminance and `(Llighter + 0.05) / (Ldarker + 0.05)`. Muted text passes on ordinary ground at **4.9131:1**, ordinary panel at **4.5926:1**, and hover ground at **4.6397:1**. F1 tests the separate focus ground, which fails. F2 applies the CSS saturation matrix at 0.12 and brightness multiplier at 0.72 to the text before the same contrast calculation against the unfiltered HUD ground. Its result also fails in calm, where the optional overlays are absent. These are computed design ratios, not claims of photometric measurements from compressed screenshots.

**Cast size and supplied performance evidence.** The 7 canonical SVGs parse as vector source and retain their 6 material roles. Counts below include each SVG root and metadata.

| Asset | Raw bytes | SVG elements |
| --- | ---: | ---: |
| `arbiter.svg` | 8,166 | 76 |
| `builder.svg` | 8,775 | 98 |
| `guard.svg` | 8,053 | 88 |
| `michou.svg` | 8,730 | 95 |
| `reviewer.svg` | 7,988 | 86 |
| `scribe.svg` | 6,717 | 71 |
| `stranger.svg` | 6,353 | 68 |
| All 7 SVGs | 54,782 | 582 |
| `characters.css` plus `characters.js` | 21,513 | Not applicable. |
| Target comparison total | 76,295 | Not applicable. |

The total is **74.51 KiB**, or **14.55%** of the provisional 512 KiB target. The native tray source adds 80,974 bytes, including its copy of the cast and shared CSS; source size establishes no runtime-performance result. Board 10's selected preview remains the only sprite instance eligible to animate, with hidden/offscreen/calm/reduced-motion guards and at most 2 authored endpoint poses per moving part.

AUDIT-CDH-0001 supplies the prior Codex measurements from 2 approximately 30-second standalone captures with 50 static portraits and 1 selected working builder: headless Chrome 155.0.8059.39, Apple M4 Pro, 12 logical CPUs, 24 GiB RAM, 1440 × 1100 CSS px, DPR 2. Motion/calm RAF means were **33.33/33.33 ms**, p95 **33.40/33.40 ms**, long tasks **0/0**, input-to-next-frame p95 **27.60/29.20 ms**, and scroll-to-next-frame p95 **0.20/0.10 ms**, with 56 input and 56 scroll samples per capture. Working had 1 active effect at start/end and calm had 0; the fixture's maximum was 3 effects on 1 idle detail. AUDIT-CDH-0003 supplies 101 static raster comparisons and 49 selection checks in a browser projection, and explicitly cautions that getAnimations() missed moving SVG use-tree effects. None of those measurements was repeated here or measures the mounted tray, native canvas performance, physical-display smoothness or whole-cockpit cost.

**Images and provenance.** All 12 files below were opened as image input, and every SHA-256 matches the post-delivery value in AUDIT-CDH-0007. Native origin is Cowork-attributed to the report's private review copy, version `1791931057-6ece (22)`; this review did not access that page or interact with a browser. These are native-canvas capture evidence, distinct from approved reference artwork and the older standalone/projection evidence. The 2026-10-12 provenance correction concerns CDH-0004/0006 delivery re-encoding; the current CDH-0007 captures have 0 hash mismatches.

The board-11 before-fix image visibly clips the stale timestamp. The after-fix image shows the summary wrapping and content inside the enlarged 940 px frame, supporting closure of CW10 and CW11. The report says the other 11 images predate those 2 cosmetic fixes and that an editor-normalized file was later replaced by the repository version. Accordingly, they evidence the visible tray design but are not all final-commit exports. The board-3 images show both imports and 3 text rows; board 4 shows its 2-run blocked summary; board 5 its waiting/transient summary; board 6 its stale timestamp; board 9 its 3-row pane and header; the combined boards-1/7 image shows the anatomy and solid `a` key. Several captures crop the overall artboard, so this report does not infer unseen edges from their names.

| Capture under `logs/scratch/design-review/cdh-0007/` | SHA-256 |
| --- | --- |
| `native-board-11-bar-and-pane-100pct.jpg` | `ac044c38910b256d9ac8ed97f7dee881e73a2cef822dd32965dea52fdc5f5d48` |
| `native-board-11-stale-overflow-before-fix-100pct.jpg` | `acd38acb3bbc9f49faaac7f5a4f868ddd7e944b8abb45cf78853f115cab7b667` |
| `native-board-11-whole-after-fix-38pct.jpg` | `791dfe8d07a559cd169fb8c328db7f9e3364beca49be921328e7f7d88b7fd286` |
| `native-board-3-detail-pane-100pct.jpg` | `4ec50378dc86a8ed460705420876d868772c230ff96909128025bcc5a2f8c5fa` |
| `native-board-3-header-tray-100pct.jpg` | `ef56541ea33d634072a86ae95406741008342494289092fa402f9565478dc099` |
| `native-board-3-whole-50pct.jpg` | `ed1d4f84ffcf07710a249f51eca968af4796037e03d3b6ca33dda7c7db74c105` |
| `native-board-4-blocked-50pct.jpg` | `90ceb1d6d60b01d772c3413dc85b9a80a21aa1c9a65eca33dd6aff91cdc33979` |
| `native-board-5-waiting-50pct.jpg` | `8ee56059f7f89fde19bce5a34871474031a24b3206e7483b89c6288f581ea688` |
| `native-board-6-stale-50pct.jpg` | `d585469e7ac9dec60ab202583d98f18af5c0a3788557fc31b13d3f33eafb377a` |
| `native-board-9-header-50pct.jpg` | `f28cac983ae257039aa706f9d3129f0b01db8cc3afc0fa5bfe7a8396d1b2a270` |
| `native-board-9-tray-column-50pct.jpg` | `7ec8da12c27fbc8a3251430b4380d7b59e35b21228866842ebe69b8ee988436b` |
| `native-boards-1-and-7-50pct.jpg` | `23d8caf981ea7ae8f3feebe9b7e48547a60bbff37936b8f4ef4d764309ebcc80` |

Native calm across the mounted parent/child components, actual reduced-motion behaviour, hidden/offscreen behaviour, keyboard navigation, accessibility-tree behaviour and native performance remain unverified in this review. A static capture cannot establish the absence of animation over time. The 0 eligible tray animation classes are a separate source observation. CW12's third header line on boards 3/5 and CW13's crowded Wall header remain Cowork's existing advisories; they are not added to the blocking count here.

**Source identity.** The following 23 SHA-256 values identify the complete reviewed design tree. Paths are relative to `docs/design/cockpit-v0/`. The aggregate digest is `9c12e6f5a63cd25de2e4734c335391e3b08751db95e5112e4acfc5b739d01171`, computed over sorted records of repository-relative path, NUL, file SHA-256 and LF.

| Source file | SHA-256 |
| --- | --- |
| `Blocking.dc.html` | `eefd7e7ef27458c2c0626e2937c1739c117eac249374867f860073624c63c72f` |
| `Components.dc.html` | `a0d8fa4d0f3124938812e22bbe03961ad5467df82357c838fcdf0f373e4b52d7` |
| `Disconnected.dc.html` | `a49ae7f37b3b10d841070b5ddd6922fc63bbda4f0fa9b7e5eb369eca87248a98` |
| `Empty.dc.html` | `5de581859ed272ac290af6041253c6496583b357e576e849cabc06ec5400fddd` |
| `Keys.dc.html` | `59f71290673176bf625ac35a7f60e97fd48e491bfe2c1785cecac3aa51c29026` |
| `Main.dc.html` | `304145c4cd9280329799202fa82dc9f004f60598a30ca5f953b52cafad3dd1d3` |
| `Pending.dc.html` | `652f9a3b3d26ea47eb4fb79f7eeb5cbf1e65373b4089f6dc93831e391b8c3a55` |
| `Phase2.dc.html` | `5bd59761b2dbc37ad9bf1620e9cb5dec1300f6209c4f9791168f228039161539` |
| `Sprites.dc.html` | `e54f58bfd3dd315d0e82830587008be202b761f6c7593b5e7d344f433683ca7a` |
| `Tray.dc.html` | `a414b31eead9b82ce086bdbe1feca38682212749fa4ceb46cc263da6ff0ebab2` |
| `Wall.dc.html` | `719bbe0630167574315fe37a63a3869a1401d1bbe2335b3aedb8297544cb16c3` |
| `canvas.json` | `a082ca20ffbb0397227613bdb483df80c869c1893bf0f6501ae9ffa266bf897f` |
| `chibi/README.md` | `c4059a5ee64560bdcc10e96786882cc92c5ebfbbfc7640efd70c938a99b054e2` |
| `chibi/arbiter.svg` | `8d7bb211574d347a5038dfb1b38aa7facc414369f24d7e640102059b16bdcdc1` |
| `chibi/builder.svg` | `c366fb0c40d5d1df0e547fd4cf77f9fdb1b5931a9d194594cb16481e6f38404e` |
| `chibi/characters.css` | `7fcb692d48d26201744cf6795c899cdbaa9a93750bbb9d952407921bcd19a020` |
| `chibi/characters.js` | `900872eec1de4f457c120eeeedb068d4a2346ceeb9e803acfb20ac3dd0b4e26e` |
| `chibi/guard.svg` | `da6639d6cabae91e7fa622754a6fc27c9dc7c823e3657d34340a76729f6b31fa` |
| `chibi/michou.svg` | `46831a1e9d6ebf8991beb59b0281779ee6bc7869798fd2b168822b0f2bdfa9c7` |
| `chibi/preview.html` | `2681c521c3de5091b82f4cb1c829071d4f3be8e60c54fb0a6e1c1d19561aff23` |
| `chibi/reviewer.svg` | `f444d74e398ab00a5a52e9160c50bf433113ba9115e0fe65efbb51b13e9a062b` |
| `chibi/scribe.svg` | `cba7d68489569c0dc783086829752807af719b3473dd9d0286a00807d39fc026` |
| `chibi/stranger.svg` | `7fed1b5845d5934e37580d7070c35adfbabb9e84cc9b87a0e536ef602ab81516` |

**Taste, advisory only.** My first 3 presentation changes would be to reserve a stable header row for the tray and usage bars at 1440 px, shorten the repeated key hints in the expanded footer, and move the long board-11 lifecycle explanations into a visually quieter reference area. These are Michou's choices, not acceptance conditions, and are separate from F1 through F6.

The delivery is limited to 3 paths: this report, CDH-0008's adoption/completion frontmatter, and its 1 queue-row status. No design source, ADR, config, existing report, evidence image or main-branch file is edited; no commit or push is performed. Cowork can commit the 3 delivery files on design. The configured global memory index was absent at `/Users/michaelgrigorian/.Codex/projects/-Users-michaelgrigorian/memory/MEMORY.md`; the review used the repository context and all handoff prerequisites were present.
