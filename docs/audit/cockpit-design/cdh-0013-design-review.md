---
id: AUDIT-CDH-0013
type: report
created: 2026-10-15T22:52:00-07:00
handoff: CDH-0013
period: "2026-10-15"
source: inferred
sources:
  - CDH-0013
  - CDH-0012
  - CDH-0001
  - AUDIT-CDH-0001
  - AUDIT-CDH-0003
  - AUDIT-CDH-0009
  - AUDIT-CDH-0010
  - AUDIT-CDH-0011
  - AUDIT-CDH-0012
  - ADR-016
  - ADR-017
  - docs/readers/cockpit-design.md
  - tools/review/design-prompt.md
  - docs/handoff/proposed/2026-09-14-cockpit-design-canvas.md
  - memory/notes/cockpit-wishlist.md
  - docs/design/cockpit-v0/ at dd90ca6106001adfe9276899bdcad63be2a8935a
  - kgme/events.py
  - tests/test_design_sprites.py
  - logs/scratch/design-review/cdh-0009/
  - logs/scratch/design-review/cdh-0010/
  - logs/scratch/design-review/cdh-0012/
author: codex
status: final
tier: 2
reviewed_sha: dd90ca6106001adfe9276899bdcad63be2a8935a
---

## Findings

The cycle repairs the 2 original lifecycle errors, room-button ownership, refresh-time focus loss, focused contrast, font loading and tray cascade. It also supplies the requested calm scenes. However, 2 blocking defects remain in the station: an ordinary note clears the displayed halt without resuming the run, and resizing while calm leaves the returning deck with invalid dimensions. This review feeds Michou's disposition and Cowork's next design cycle. Design paths below are relative to `docs/design/cockpit-v0/`; source deductions are distinguished from the 29 supplied still images inspected.

| id | class | file:line | finding | fix |
| --- | --- | --- | --- | --- |
| F1 | blocking | `station/index.html:302`, `:518`, `:522`, `:540`, `:566` | The 2 state calculations disagree after a non-resuming note. Starting with the supplied synthetic halt at 19:53:00, append an ordinary unclassed note on the same run at 19:53:30. Evaluation of the actual functions returns lifecycle `blocked` and summary `1 blocked`, but hull `nominal`: `snapshot()` checks only the newest event, whereas `lifecycle()` keeps a blocking note active until an intent, outcome or approval follows. The HUD, calm wall and hull colour therefore clear a halt that still governs the run. The requested persistent halt signal is not fully repaired. | Derive the active halt from the same subsequent-activity rule as the lifecycle. Verify 3 cases: halt then ordinary note stays halted; halt then an authorized resumption clears it; the existing exhausted-retry exception remains transient. Keep the halt's text available after later bookkeeping notes. |
| F2 | blocking | `station/index.html:101`, `:401`, `:406`, `:633`, `:681` | The sequence `c`, resize the window, `c` destroys the deck's usable geometry. Calm sets `#stage` to `display:none`; `resize()` nevertheless reads its 0 by 0 dimensions, computes aspect `0/0`, writes `NaN` to the camera's left/right bounds, and sizes all 4 render targets to 0. Leaving calm performs no resize. The next frame renders with those invalid bounds while hiding the text wall, so the room controls and their state labels cannot return normally until another resize. This is a source deduction, independently evaluated with the hidden-stage dimensions, not an observed browser session. | Skip sizing a hidden stage and resize immediately after revealing it, or derive valid dimensions from the viewport independently of visibility. Verify calm, resize, return at 1440 and 400 px, including room-button visibility and focus. |
| F3 | advisory | `station/index.html:311`, `:314`; `station/README.md:11`; `Tray.dc.html` quiet rules in both anatomy copies | S7's multiplier mismatch is repaired, but the 3 descriptions still call the threshold the median while the code chooses the upper middle observation for an even number of gaps. With gaps of 180 and 600 seconds, the ordinary median is 390 seconds and the code uses 600; 450 seconds after the last event, it omits the quiet suffix that the written rule implies. The 180-second floor does not resolve that difference. | Either average the 2 middle gaps or explicitly name and justify the upper-median convention in all 3 descriptions. Retain the selected 1-times threshold and 3-minute floor; this finding does not reopen that choice. |
| F4 | advisory | `docs/audit/cockpit-design/cdh-0012-implementation.md`, Evidence table; `logs/scratch/design-review/cdh-0012/manifest.json` | All 12 delivered PNGs and the manifest fail their reported SHA-256 values, despite the report saying the hashes were taken on the Mac after delivery and that nothing was re-encoded. The 2 accompanying data files match. Current pixels resolve the earlier visible calm/phone contradictions, and the manifest names matching source bytes, but that is not authentication of this delivered evidence set. The older 2026-10-12 re-encoding explanation concerns different captures and cannot establish these 13 mismatches. | Reconcile the delivered files with their originals, record the actual hashes and explain any transformation or manifest edit. If re-encoding is the explanation, compare decoded pixels against the originals before claiming equality. Preserve the distinction between standalone and native evidence. |
| F5 | advisory | `logs/scratch/design-review/cdh-0012/sample-events-halt-synthetic.jsonl:42`; `kgme/events.py:149` | The synthetic approval carries `kind: approval` with `status: ok`; the repository validator rejects it with `status is set only on outcome events`. The other 41 records validate. The demonstration exercises the page's permissive JSON reader, not a fully valid event-v1 halt/resume fixture. Changing only this approval's status to null makes it validate and leaves the tested lifecycle result unchanged. | Correct the synthetic approval in the next authorized evidence delivery, validate all 42 records, and regenerate or explicitly qualify the approval evidence. The committed 40-line station sample needs no change. |
| F6 | advisory | `station/index.html:435`, `:460`, `:489`, `:589`; `:617` | The 7 room controls are now exposed, but some factual text remains excluded from their accessible presentation. Crew wrappers hide the bubbles as well as the artwork; outside calm, fixture summaries exist only in those hidden wrappers, while the room labels give a state/time and the pane excludes fixture runs. Separately, each row's explicit `aria-label` omits its elapsed value and event chip. In the exhausted-review sample the visible lifecycle is transient and the event chip is blocking, a distinction absent from that accessible name. This is a source-level accessibility follow-up, not a claimed screen-reader measurement. | Keep factual fixture summaries in an exposed text region in both layouts, with only artwork decorative. Include the chip and elapsed value in the row's accessible description or let its visible text supply them. Verify the refusal, human note and transient-lifecycle/blocking-chip combination with the accessibility tree. |

## Verdict

BLOCK: 2 blocking findings.

## Notes

**Scope and identity.** The reviewed commit is `dd90ca6106001adfe9276899bdcad63be2a8935a`, selected by the queue and AUDIT-CDH-0012's `reviewed_sha` and delivery table. The report's last sentence also mentions `af714e9`; that stale sentence was not used as the review target. All 26 design files were read or parsed and compared byte-for-byte with `dd90ca6`. Canvas metadata and Main were read first; the other boards were parsed in canvas order for visible text, controls and imports. The 3 changed files are the station page, station README and tray; the other 23 match the prior `4f3e06c` tree. The initial worktree was clean on `design`, HEAD `633874d9fcd7e4b7963db7b08e9ccf7fa4685618`. A concurrent commit `85691f9` added unrelated review material during this run; the reviewed design remained unchanged and that material was not part of this delivery.

| Reviewed source | SHA-256 |
| --- | --- |
| `station/index.html` | `35b5a05a2d022e319e96cba883fb44d87fc987fc2b22682439d4be6db7e50cf7` |
| `station/README.md` | `d46c1189c0fcbac832a4c53401fb8b83ca636169476ecdd5f5cb898b4d67e42d` |
| `station/sample-events.jsonl` | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |
| `Tray.dc.html` | `72799fd6c707e78a35d6d6b0ff151b9f90ba8938bef9c8a7116dac44e5118e5b` |

The 26-file source-set digest is `6f5bebff27615e6ccb475d036da997115e60cb2c2477af4137b8540af76e6344`, using sorted UTF-8 records `repository-path + NUL + SHA-256 + LF`. Extracting the station body, stripping its outer whitespace and appending 1 newline reproduces the manifest's body hash `6f97fb17b72f42ffd008aa92afdf2ad43b0a0d9e575add019dbc36ed911771c7`. This verifies the identified body, not the unavailable served wrapper or the pixels by association.

**Disposition of every prior finding.** Closure below concerns the original finding's stated defect, with residual issues named separately.

| Prior id | Disposition | Evidence and limit |
| --- | --- | --- |
| S1 | Partially closed; F1 remains blocking. | The 1 shared snapshot supplies fixture lines, room summaries and halt text; wall z-index 5 now sits below HUD 6. The 5 supplied calm moments retain the HUD, refusal, note, subsequent ruling, halt and approval in words. The post-halt ordinary-note case still clears the halt incorrectly. F2 is an additional calm-transition defect. |
| S2 | Closed for both original errors. | Independent Node evaluation returns waiting for all 5 null-parent root intents at sample lines 1, 7, 15, 19 and 22, covering the 4 originally cited cases. A blocking note returns blocked; subsequent intent returns waiting; subsequent intent plus successful outcome returns working; subsequent approval lifts the note's block. The supplied review run returns transient after approval because its preceding operation remains the exhausted blocking outcome. |
| S3 | Closed for room ownership. | `#stage` has no `aria-hidden`; the canvas does; all 7 buttons are anchored without a hidden wrapper and receive state-bearing names at line 559. The supplied manifest reports 7 exposed room buttons. F6 records the remaining accessible-text gap separately. |
| S4 | Closed for ordinary refreshes. | `syncRows()` retains each existing button by run id and calls `updateRow()` in place; the 7 wall sections are retained too. The manifest reports the same connected focused element after 1.5 seconds. Its `tabMovesToNextRow` value is empty, so the report's separate assertion that Tab reached another row is not verified by that record. Explicit replay reset still rebuilds rows. |
| S5 | Closed in the actual source cascade. | Both painted and keyboard-focused station rows set the run id, second line, quiet suffix and muted chip to `#7a8d9b` on opaque `#0e1a22`, independently calculated at 5.1371:1. The supplied computed styles cover the first 2 fields; the selectors establish the other 2. |
| S6 | Closed in the repository source. | The 3 font tags are removed. The only declared remote resource origin is jsDelivr's pinned `three@0.182.0`; the SVG namespace is not a fetch. The page fetches 7 repository SVGs and 1 sample JSONL. The manifest's local-vendor request list has no font request, but is supplied wrapper evidence, subject to F4, rather than a new network observation of the repository URL. |
| S7 | Partially closed; F3 remains advisory. | Both board-11 anatomy copies and the station README now specify 1 median gap, a 180-second floor and the fewer-than-2-intents fallback. The code implements those choices except for the unqualified upper-median convention. |
| S8 | Closed for the requested source correction. | A media-query change listener plus a 1-second poll updates bloom; reduced motion snaps walks and camera movement; calm skips walks, camera updates and both render calls. The supplied manifest records full/on, reduced/off, full/on. The RAF/replay and 250 ms word updates continue in calm; 0 total work is not claimed. Station-specific target-Mac performance remains unverified. |
| S9 | Partially closed; F4 and F5 qualify the evidence. | The 12 new captures have viewport/replay-interval labels and show no calm portraits or phone micro-labels. AUDIT-CDH-0012 explicitly attributes the 2 old contradictory pictures to development builds. Delivered-file authentication and the synthetic approval's schema validity remain unresolved. |
| T1 | Closed in the actual source cascade. | The reset now has specificity `(0,1,0)`, not zero overall: `:where(button)` contributes zero but `.tr-root` contributes 1 class. Later row rules therefore retain padding 5 px/6 px and a 1 px top border. Focus fill survives hover, and later focused text rules win the equal-specificity contests. |

**Independent measurements and checks.** Codex evaluated the committed lifecycle and snapshot functions in Node, without changing source. F1 was reproduced against the supplied review run by inserting 1 in-memory ordinary note between its halt and approval. Before the note, the result is blocked/HALT; after it, blocked/nominal; after an approval with schema-valid null status, transient/nominal. F2's actual `resize()` function was evaluated with hidden-stage dimensions: both camera bounds became `NaN`, and renderer, composer, labels and bloom each received 0 by 0. No browser observation is asserted for those source deductions.

Codex checked selector specificity and source order with a small in-memory selector evaluator for the applicable tray and station rules, then calculated contrast using linearized sRGB luminance. These are source-cascade calculations, not a substitute for a browser's computed-style engine. Tray painted focus and painted-focus hover resolve all 4 muted fields to the 5.1371:1 pair; an ordinary row is 4.5926:1 on `#11151c`, and ordinary hover is 4.6397:1 on `#0f141b`. Keyboard focus on a non-painted tray row retains the panel ground and a 2 px outline, so it passes at 4.5926:1. Station painted and keyboard focus both resolve to 5.1371:1. Muted text on ground is 4.9131:1, ordinary text on surface 14.1290:1 and magenta on surface 5.4239:1. These opaque-pair results do not certify every transparent HUD, chip or pane composite over a moving scene.

The 40 committed sample records pass `validate_event()` and serialization. In the 42-line synthetic file, only line 42 fails; changing only its status to null in memory passes validation. No payload or private path referenced by a sample was opened. The 1 station keyboard handler binds room keys 1 through 7, Escape, a, c and r, all named on its page. These are read-only view/replay commands. The engine room remains dashed and labelled Phase 2; no station command dispatches, approves, selects a model or writes the ledger. The tray remains a native drawing with 9 button template sites; source review does not certify native application handlers.

The required existing sprite check passed: `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/kgme-cdh-0013-uv uv run --offline --no-sync pytest -q -p no:cacheprovider tests/test_design_sprites.py` returned **30 passed in 0.05 s**. It checks the canonical symbols, materials, crops and shared styles. The 7 SVGs and both shared animation files are unchanged; the station loads each canonical SVG's children, root material style and portrait crop, and assigns 0 `is-animated` classes.

| Actor asset | Bytes | SVG elements including root |
| --- | ---: | ---: |
| arbiter.svg | 8,166 | 76 |
| builder.svg | 8,775 | 98 |
| guard.svg | 8,053 | 88 |
| michou.svg | 8,730 | 95 |
| reviewer.svg | 7,988 | 86 |
| scribe.svg | 6,717 | 71 |
| stranger.svg | 6,353 | 68 |

The 7 assets total 54,782 bytes and 582 elements; shared CSS/JS adds 21,513 bytes. The 76,295-byte total is 74.51 KiB against the provisional 512 KiB target. AUDIT-CDH-0001 supplies prior Codex measurements for 2 approximately 30-second standalone cast runs with 50 portraits and 1 selected detail on the M4 Pro Mac: motion/calm RAF means 33.33/33.33 ms, p95 33.40/33.40 ms, 0/0 long tasks, input-to-next-frame p95 27.60/29.20 ms and scroll-to-next-frame p95 0.20/0.10 ms. Those measurements and AUDIT-CDH-0003's 101 static comparisons concern the cast fixture/projection, not station WebGL performance. No new runtime-performance claim follows from the source size or passing tests.

**Images and provenance.** All 12 current PNGs were opened as image input. The captures visibly retain textual refusal, human note, ruling and hull state in calm, including after newer events; their 400 px calm layout hides portraits and wraps the HUD. They also retain the crowded deck/HUD composition at phone size. The supplied before/after replay intervals span capture time, so these are not simultaneous comparisons or timing benchmarks. The halt/approval images use the labelled synthetic file. The manifest attributes the current set to Chromium 1194/SwiftShader in Cowork's VM with a locally vendored three.js import map; it is standalone evidence, not native canvas evidence. Its 2 unqualified resource-404 console records also remain unattributed.

The actual delivered hashes below were measured by Codex. All 13 differ from AUDIT-CDH-0012's table; none is silently substituted as proof of the original capture provenance.

| File under `logs/scratch/design-review/cdh-0012/` | Actual SHA-256 |
| --- | --- |
| `standalone-pane-focused-row-1440x900.png` | `c1057d72b542a7f0e4eb2579dcbaa32578007a1e5f8b65a0051a9a27b438fb08` |
| `standalone-calm-at-refusal-1440x900.png` | `3a5a59fbbae6f97bbfa64a31371834532dc9c4a24bb51643cf1db2adf9bf25cc` |
| `standalone-deck-at-refusal-1440x900.png` | `29effc38c5bbb23c97ba7b8c5e23f8c25efa5c987f75414b2014edd72f8aafc5` |
| `standalone-calm-at-note-1440x900.png` | `0641e9bf81fe9317b31d2c8924f0bfd50630f53877f323db31080c8f1a8a8753` |
| `standalone-calm-after-newer-events-1440x900.png` | `2fb1371292da6e604f48be6273d70fbbc7a6bcc8855c9d2ab5c2637df85a8baa` |
| `standalone-calm-at-halt-1440x900.png` | `ab499f08c1edec6b5cbb54dc3c4139fbeabab9b737b7ef46c30ecd857cd3c779` |
| `standalone-deck-at-halt-1440x900.png` | `e7350c0a67db6f84b208497c9eaeb27cc2029a29fd81cdf1c095234beafdc341` |
| `standalone-calm-after-approval-1440x900.png` | `f02c54a2590d3debdcd8df8012551f9a3e1be9aa117ce4c2ae5884de43f70c47` |
| `standalone-follow-workshop-2560x1080.png` | `4eb5ea09832ff1cec77b2fc355be3b2d5e41d851007db5cf68f1b15291a9751e` |
| `standalone-calm-wall-2560x1080.png` | `d73ab706622eca3ea83a6ba0cec9243628133c81257ab101261133719b6680c5` |
| `standalone-deck-400x800.png` | `a54c9911152861f65e100079d684ced94c6561d362cd3f8b04e73ed59d209b1a` |
| `standalone-calm-wall-400x800.png` | `9e7e653d234ad6cfe0202594eca527c778564c8a5fee87ba4882c539559b6634` |
| `manifest.json` | `4e0bc575c02b65d0c6042912f467592e0defc8c8363b6b4688db3ac1174f98f3` |

The 2 matching supporting hashes are `4bce8a97237465822bd832f3c03ff67dd023a9e8a447a32920d6684436f7b551` for the synthetic JSONL and `e7908de90f28e7e76647a647dcd47aca4e6ac9d536f3dd5322a21d7fd5079e8f` for `lifecycle-eval.txt`. Historical CDH-0009's 9 still images were also opened: 4 attributed native-artifact v1/v2 captures and 5 standalone desk/wall/follow/calm/phone captures. Historical CDH-0010's 4 native board-3 calm-on/off left/right images and 4 bar/pane crops were opened as well. All 18 historical evidence files match their reports, including the 1 WEBM that was hashed but not played. Historical pixels are not evidence of the current cascade or current station source.

**Observation limits.** An isolated local headless Google Chrome launch exited 134 before returning even a data-page DOM. No station page was rendered in this review and no dependency was installed. The handoff's source-and-captures fallback was used. Native canvas interaction, screen-reader output, live preference changes, composed-scene contrast, resize restoration, physical-display smoothness and station target-Mac performance remain unobserved by Codex. The manifest's observations remain Cowork-attributed and subject to F4. The configured `.Codex` memory index was absent; no named handoff prerequisite was missing.

**Taste, advisory only.** My first 3 presentation changes would be to reserve a clear band between the HUD and room labels, place event bubbles away from the chips they obscure, and reduce the 2560 px calm grid's column count so run/event text gets more width. These are Michou's choices, separate from the 6 findings and the 2-blocking verdict.

The authorized delivery comprises 3 paths: this report, CDH-0013's adoption/completion frontmatter and its single queue row. Final design approval remains Michou's; this review does not approve HANDOFF-0036 or start HANDOFF-0037.
