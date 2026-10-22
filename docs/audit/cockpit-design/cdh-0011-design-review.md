---
id: AUDIT-CDH-0011
type: report
created: 2026-10-14T00:23:28-07:00
handoff: CDH-0011
period: "2026-10-14"
source: inferred
sources:
  - CDH-0011
  - CDH-0009
  - CDH-0010
  - CDH-0001
  - AUDIT-CDH-0001
  - AUDIT-CDH-0003
  - AUDIT-CDH-0008
  - AUDIT-CDH-0009
  - AUDIT-CDH-0010
  - ADR-016
  - ADR-017
  - ADR-019
  - docs/readers/cockpit-design.md
  - tools/review/design-prompt.md
  - docs/handoff/cockpit-design/README.md
  - docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md
  - memory/notes/cockpit-wishlist.md
  - docs/design/cockpit-v0/station/ at 373de74ad64fcd262a8240790016b940c24753ef
  - docs/design/cockpit-v0/ at 4f3e06c904bd212b1b44b62f2476535e2fbd7092
  - tests/test_design_sprites.py
  - kgme/events.py
  - logs/scratch/design-review/cdh-0009/
  - logs/scratch/design-review/cdh-0010/
  - logs/scratch/design-review/references/station-reel-1-rooms.jpg
  - logs/scratch/design-review/references/station-reel-2-trading-desk.jpg
  - logs/scratch/design-review/references/station-reel-3-hud.jpg
author: codex
status: final
tier: 2
reviewed_sha: 4f3e06c904bd212b1b44b62f2476535e2fbd7092
reviewed_shas:
  station: 373de74ad64fcd262a8240790016b940c24753ef
  tray: 4f3e06c904bd212b1b44b62f2476535e2fbd7092
---

## Findings

The tray closes the 6 findings from AUDIT-CDH-0008, with the cascade qualification in T1. The station has 6 blocking findings. Paths below are relative to `docs/design/cockpit-v0/`; each finding concerns the committed design, with source inference distinguished from supplied captures. This review supplies Michou's disposition decision and Cowork's next design cycle.

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| S1 | blocking | `station/index.html:89`, `:190`, `:459`, `:461`, `:487`, `:506`, `:511`, `:546` | Calm loses facts. The opaque wall at z-index 8 covers the HUD at 6 without repeating its clock, ledger counts or replay context. Its Bridge says only `you`, and its Airlock always says `guarded · nothing pending`; neither reproduces the live fixture state or event. At sample event 30, Michou's note exists in a bubble but is excluded from `liveRuns()` and hence from the wall. After a newer builder event, the guard's still-visible refusal bubble also has no equivalent wall event. Separately, the `halted` boolean changes hull/frame colour without a persistent textual halt field. These are losses of signal when decoration is removed. | Render both layouts from 1 shared textual snapshot that includes system/replay context, current room states, relevant fixture events and an explicit halt state. Keep each bubble's fact available in that snapshot while the bubble is displayed. Check calm at the refusal, human note and halt, including after a newer event. |
| S2 | blocking | `station/index.html:286`, `:289`, `:291`, `:295`; `station/README.md:10`; `station/sample-events.jsonl:1`, `:15`, `:19`, `:22` | The lifecycle calculation contradicts its written rules in 2 reproducible cases. Unmatched initial intents are excluded solely because `parent` is null: source evaluation returns `working` for sample events 1, 15, 19 and 22, although each newest event is an intent without an outcome. Conversely, any historical blocking note permanently returns `blocked`, even after a later successful outcome; the README and board 11 say blocked while the run has not moved since. Counts and lights inherit those incorrect words. | Separate hierarchy (`parent`) from intent/outcome pairing (`ref`), and define blocking precedence against the relevant subsequent activity. Verify initial hook/job intents and a blocking note followed by resumed activity. Preserve the exhausted-retry exception and the recorded event class. |
| S3 | blocking | `station/index.html:162`, `:316`, `:362` | All 7 room buttons and their state text are mounted by CSS2DRenderer inside `#stage[aria-hidden="true"]`. Hiding the decorative canvas therefore also hides the room controls and bubbles from the accessibility tree. The buttons remain ordinary focusable buttons inside that hidden subtree; visible words alone do not supply equivalent accessible controls. This is a source-level semantic defect, without a claim of a measured screen-reader session. | Apply `aria-hidden` to the WebGL canvas and decorative artwork only. Keep the room controls and factual text in an exposed overlay, with accessible names that include their state. Verify keyboard focus and the accessibility tree in the delivered page. |
| S4 | blocking | `station/index.html:520`, `:536`, `:542`, `:585` | Open-pane rows are deleted and recreated on every word refresh, at intervals just over 250 ms; calm recreates its whole room grid at the same cadence. A keyboard-focused row is therefore removed from the document on the next refresh, with no focus restoration or stable run key. The painted `.focus` class is merely reassigned to row 1. This source path prevents persistent keyboard focus while the replay runs. | Retain the existing controls by run/room identity and update their text, or explicitly preserve the focused identity when replacement is necessary. Verify that Tab focus remains on 1 selected row across several refreshes. This does not require dispatch or any Phase 2 action. |
| S5 | blocking | `station/index.html:82`, `:85`, `:86`, `:524` | The 10 px quiet suffix keeps `--dim: #6f8290` on focused ground `#0e1a22`: **4.4317:1**, below **4.5:1**. The focus correction covers `.run` and `.l2`, but omits `.life .q`. This is reachable when the first builder becomes quiet and its pane is opened; it is independent of transparent scene backgrounds. | Include the quiet suffix in the focused text treatment. `#7a8d9b` on that ground measures **5.1371:1**. Recheck every muted descendant of the focused station row. |
| S6 | blocking | `station/index.html:12`, `:13`, `:14`, `:213` | The station declares 2 additional remote origins, Google Fonts CSS and font delivery, beyond the authorized pinned three.js package. AUDIT-CDH-0009 itself attributes part of the artifact's 20 to 50 second load wait to the font stylesheet. The requirement is that the page load only the pinned package and repository files; describing three.js as the only remote *script* does not satisfy it. | Remove the remote font links/preconnects and use the existing local font stack, or a separately authorized local font asset. Retain the pinned three.js import map and verify the final network request list. |
| S7 | advisory | `station/README.md:10`; `station/index.html:296`; `Tray.dc.html:882`, `:947` | The 2 quiet definitions still differ: board 11 uses 1 median gap, whereas the station uses 3 median gaps with a 3-minute floor. For the second builder, its intents at 19:41:30 and 19:44:10 imply a 160-second gap: at 19:48 the station returns working without quiet, while the tray's prose would mark quiet. This is a definition inconsistency separate from the 2 erroneous transitions in S2. | Have Michou select 1 threshold and document it in both anatomy copies and the station README/code, including the fewer-than-2-intents fallback. Preserve quiet as a subset of working. |
| S8 | advisory | `station/index.html:242`, `:381`, `:575`, `:581`, `:587` | Reduced motion is sampled once at module load. An initial reduced setting skips bloom and snaps walks/camera; CSS removes fades. A later system preference change updates the CSS but cannot update the captured boolean, so bloom and walks remain enabled. Calm skips the 2 render calls but keeps the frame loop, camera/walk updates and 250 ms DOM rebuilds. No new target-Mac runtime measurements establish the station's motion/calm cost. | Observe preference changes and gate scene motion/work accordingly. In the next authorized browser verification, test a live reduced-motion change and record separate station motion/calm measurements; retain the distinction from the older cast-only benchmark. |
| S9 | advisory | `station/index.html:96`, `:98`; supplied `cdh-0009/standalone-calm-wall-2560x1080.png` and `standalone-phone-400x800.png` | The delivered files match their recorded hashes, but 2 captures do not demonstrate the committed CSS. The calm image visibly retains 4 run portraits although `body.calm .chibi` hides them. The 400 px phone capture retains corner micro-labels and an overflowing harness line although the 720 px media rule hides those labels and permits `.val` wrapping. The capture hashes prove delivery identity, not which exact page bytes produced those pixels. | Record the served source SHA, document wrapper and viewport for fresh calm/phone captures, and explain the existing differences. Keep the old evidence as attributed historical captures. Do not treat these 2 images as proof of final-source calm or responsive behavior. |
| T1 | advisory | `Tray.dc.html:21`, `:33`, `:36`, `:37`, `:39` | The new button reset has specificity `(0,1,1)`, outranking `.tr-row` and `.tr-focus` at `(0,1,0)`: it removes the intended 5 px/6 px padding, top border and focus fill. The later `.tr-l1 .tr-run` also wins the equal-specificity colour contest with `.tr-focus .tr-run`, leaving the run ID `#6f8290`. The current static focus still passes contrast on the underlying panel, but the claimed **5.1371:1** for all focused muted lines and unchanged row geometry do not describe the ordinary source cascade. Hover separately wins with `(0,2,0)`. | Lower the reset's specificity or make the row/focus overrides explicit; place the focused run-ID override after the base rule. Preserve the 2 px keyboard outline, then remeasure the actual focused and hovered pairs. If the tint is restored, correct the run-ID override at the same time so **4.4317:1** does not return. |

## Verdict

BLOCK: 6 blocking findings.

## Notes

**Scope and source identity.** The station was reviewed at `373de74ad64fcd262a8240790016b940c24753ef`, and the tray at `4f3e06c904bd212b1b44b62f2476535e2fbd7092`. The station is byte-identical between those commits. All 26 current design files were read or parsed and compared byte-for-byte with the applicable reviewed commit before using worktree line references. The initial branch was `design`, HEAD `bc0a14b3921744111721cd87d20b6e306111ce29`, with a clean tracked worktree. No design source was changed.

The CDH-0010 commit changes exactly 1 design file, `Tray.dc.html`, by 48 added and 38 removed lines. All 22 pre-existing non-tray files still match AUDIT-CDH-0008's source table at `5182d6a`; the only additional files are the 3 station sources below. Thus host boards, canonical cast, board 10 and canvas metadata did not move in this cycle. T1 concerns unintended cascade changes inside the edited tray itself. The SHA-256 digest over all 26 sorted records `repository-path + NUL + file-sha256 + LF` is `2aabfa29da7e15d783399d85be2dff25f8c1a2c0300808ed4ab608337cf09386`.

| Reviewed file | SHA-256 |
| --- | --- |
| `station/index.html` | `937196d6767571f1b7ee07de448c2c12558f95dbf7e024773d08104086d8f4bb` |
| `station/sample-events.jsonl` | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |
| `station/README.md` | `1734602fc0cff126363213ea39d4dc37a3643954847a2c04fb6aa54124ffb1d2` |
| `Tray.dc.html` | `446655b1ed4f0ae8b019820e1a4c51fad9ab6e8dd0e29ec8801e83d7dc2440ed` |

**The 6 tray closures.** F1's readability gate passes on the actual source cascade: run IDs are **4.5926:1** and the corrected second line **5.3236:1** on panel `#11151c`; muted run IDs on hover are **4.6397:1**. The intended `#7a8d9b`/`#0e1a22` pair is **5.1371:1**, but T1 prevents attributing that pair to every focused field. These are source-derived ratios, not a native computed-style observation. F2 passes: `#cfe6ef` after `saturate(.12) brightness(.72)` becomes RGB **(160.9194, 162.9066, 163.6842)** and measures **7.7166:1** on `#0a0c10`. F3 supplies **9** button template sites, accessible action names and a **2 px** focus-visible outline. The row labels include actor mapping, run, lifecycle/quiet, elapsed time, event and chip. Application handlers remain outside this drawing's scope.

F4's retry-after-exhaustion exception appears in both anatomy copies, **2 occurrences**, agrees with the station's retry test, and preserves the blocking event chip. F5 evaluates to `2 working (1 quiet) · 1 transient` for **3** open runs. F6 is supported by Cowork's **4** native before/after captures plus **4** same-region crops: the bar's 3 portraits and pane's 3 portraits disappear, while text, row facts and positions remain aligned at the supplied resolution. This closes the requested native evidence gap; Codex did not operate the native editor. CW17/CW18's host-board contrast issues remain the existing out-of-scope advisories and are not counted again.

**Independent checks.** The source's actual lifecycle functions were evaluated in Node without a browser or source alteration. Besides S2's **4** sample-root cases, sample event 29 and event 40 correctly return waiting; a constructed blocking-note-then-success sequence returns blocked, confirming the historical-note rule. The actual tray component, evaluated with a minimal DCLogic props stub, returns the live **3-run**, idle **0-run** and stale **2-run** summaries. These checks establish source-data behavior only.

All **40** sample JSONL records pass the repository's `validate_event()` and serialization checks, carry all **16** fields in schema order, have unique strictly increasing ULID-shaped IDs, and resolve every non-null parent/ref to an earlier sample event. Every outcome ref points to an intent. The sample embeds no raw file body or vendor transcript object; its summaries include abbreviated command examples inherited from the boards. This is a structural fixture check, not certification of a production writer's ADR-019 redaction boundary, actual execution, or the existence/content of referenced payloads. No payload was read. The **40** records contain **0** halt notes and **0** approval events, so the delivered replay cannot visually demonstrate those cases.

The existing sprite suite passed **30 tests in 0.04 s** using `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/kgme-cdh0011-uv uv run --offline --no-sync pytest -q -p no:cacheprovider tests/test_design_sprites.py`. The checks compare **14** symbol bodies, **14** material mappings, shared CSS and portrait crops across boards 10/11. The station's shared chibi CSS block also equals board 10's byte-for-byte; its loader transfers every canonical SVG child unchanged, reads each root's material style and portrait crop, and assigns **0** `is-animated` classes. The **7** SVGs parse, contain **0** external image references and retain the **6** material roles. The reel's **3** inspected frames support the borrowed room/follow/bubble interaction pattern; their trading content, bright palette and character assets are absent from the station source/captures.

| Canonical actor asset | Bytes | SVG elements, including root/metadata |
| --- | ---: | ---: |
| `arbiter.svg` | 8,166 | 76 |
| `builder.svg` | 8,775 | 98 |
| `guard.svg` | 8,053 | 88 |
| `michou.svg` | 8,730 | 95 |
| `reviewer.svg` | 7,988 | 86 |
| `scribe.svg` | 6,717 | 71 |
| `stranger.svg` | 6,353 | 68 |
| All 7 assets | 54,782 | 582 |

Shared `characters.css` and `characters.js` add **21,513 bytes**, giving **76,295 bytes**, or **74.51 KiB**, against the provisional **512 KiB** target. No byte count establishes runtime performance. The unchanged native cast keeps its 49 static specimens, 24 px portraits, 72 px detail and 1 eligible selected animation with at most 2 authored endpoints per motion. AUDIT-CDH-0001's earlier target-Mac measurements used 50 portraits plus 1 detail over 2 approximately 30-second runs: motion/calm mean RAF intervals **33.33/33.33 ms**, p95 **33.40/33.40 ms**, and **0/0** long tasks. Those supplied measurements concern the standalone cast fixture, not this station's WebGL/bloom, DOM refreshes or native canvas.

The station's **1** keyboard handler binds `1` through `7`, Escape, `a`, `c` and `r`, all named in its own footer. These are page-local view/replay commands. No handler dispatches, approves, selects a model or writes the ledger. The **7th** room is dashed and says `phase 2 · inactive`; following it is view navigation. The station imports **1** pinned three.js package, including its addons; that permitted package graph is distinct from S6's extra font origins. The repository fetches are the **7** SVGs and **1** sample ledger file. No claim is made that the deferred board-7 station key map or board-9 `w` cycle has been delivered.

**Contrast and browser limits.** Codex calculated contrast from linearized sRGB relative luminance, `(Llighter + 0.05)/(Ldarker + 0.05)`, and used the CSS saturation matrix followed by the brightness multiplier for F2. On opaque bubble surface `#11151c`, dim timestamps measure **4.5926:1**, ordinary text **14.1290:1**, and magenta **5.4239:1**. S5 fails even without overlays. These values do not certify all scene composites: room chips use **82%** opaque grounds, the pane **92%**, the HUD is transparent, and camera movement/bloom can change the pixels behind them. Those actual HUD/chip/background combinations remain unverified.

An isolated headless launch through the installed Playwright and Google Chrome failed with `browserType.launch: Target page, context or browser has been closed` before a page could open. No dependency was installed, no approval boundary was bypassed, and no local HTTP page was rendered in this review. The handoff's source-and-captures fallback was therefore used. Native keyboard focus, accessibility-tree behavior, OS reduced-motion changes, rendered contrasts under camera movement, and station target-Mac performance remain unobserved by Codex. Source findings S3/S4 are deductions from the DOM ownership and refresh paths, not claimed browser measurements. The **1** WEBM file was hashed but not played; its filename/report duration is not an independent timing measurement.

**Observed images and provenance.** Codex opened **17** delivered still images and **3** reel references as image input. Every one of the **18** delivered evidence files, including the WEBM, matches the post-delivery hash in AUDIT-CDH-0009 or AUDIT-CDH-0010. Native station images are Cowork-attributed artifact v1/v2 captures, not native `.dc.html` canvas captures. Station `standalone-*` files are attributed Chromium captures, reportedly using locally vendored three.js; they are distinct from the repository page's remote loading path. Tray `native-*` files are attributed to the private canvas review copy. The **4** tray crops are enlarged cuts of those captures, not independent observations. S9 records the source/pixel contradictions rather than silently certifying final-source behavior.

| Evidence directory | Images opened |
| --- | --- |
| `logs/scratch/design-review/cdh-0009/` | `native-artifact-v1-pane-800px-19-48.jpg`, `native-artifact-v1-pane-20-04.jpg`, `native-artifact-v2-pane-19-54.jpg`, `native-artifact-v2-hud-replay-2.png`, `standalone-wall-2560x1080.png`, `standalone-follow-workshop-2560x1080.png`, `standalone-calm-wall-2560x1080.png`, `standalone-desk-1440x900.png`, `standalone-phone-400x800.png`. |
| `logs/scratch/design-review/cdh-0010/` | `native-board3-calm-off-left.jpg`, `native-board3-calm-off-right.jpg`, `native-board3-calm-on-left.jpg`, `native-board3-calm-on-right.jpg`, `crop-bar-calm-off.png`, `crop-bar-calm-on.png`, `crop-pane-calm-off.png`, `crop-pane-calm-on.png`. |
| `logs/scratch/design-review/references/` | `station-reel-1-rooms.jpg`, `station-reel-2-trading-desk.jpg`, `station-reel-3-hud.jpg`. |

The images show the station's **7** named rooms, the followed Workshop, lifecycle/count text, the refusal and human-note bubbles, and replay counter **2** after a reset. They also show bubble/chip overlap, already recorded as CW16, and crowding between HUD and scene labels at narrow widths. They do not supply a halt demonstration or a before/after reduced-motion sequence. The tray captures show the corrected quiet subset wording, **3** open rows and calm's retained text. Native observations remain supplied evidence, separate from the independent arithmetic and source evaluations above.

**Taste, advisory only.** My first **3** presentation changes would be to reserve a clear top band between HUD and room labels, move bubbles away from room chips, and give the calm room grid more width per text row at 2560 px. These are Michou's choices, separate from S1 through S9 and T1.

The delivery is confined to **3** paths: this report, CDH-0011's adoption/completion frontmatter, and its single Codex queue row. No design file, ADR, config, existing report, evidence file or main-branch file was edited; no commit or push was performed. Cowork can commit the 3 delivery files on `design`. This verdict does not approve HANDOFF-0036 or start HANDOFF-0037. The configured `.Codex` memory index path was absent; the existing `.claude` memory index was found and read, and no handoff prerequisite was missing.
