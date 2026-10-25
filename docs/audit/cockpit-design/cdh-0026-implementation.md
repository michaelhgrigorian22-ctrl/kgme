---
id: AUDIT-CDH-0026
type: report
created: 2026-10-24T20:04:06-07:00
handoff: CDH-0026
period: "2026-10-24 to 2026-10-25"
source: inferred
sources:
  - CDH-0026
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0026/
author: codex
status: final
tier: 2
---

# CDH-0026 implementation

Selection and causality are built from d96ade8, after CDH-0024's separate closeout and commit. Michou authorized rows 13 and 14 in order, then a stop for Cowork. This is builder verification, not a native review or canvas approval. Main remains a7efad19d3bd41dde649ef37f926192aa1b570b2; no merge or push occurred.

## Delivery

Boards 3, 4 and 5 each have 1 selected-run context strip, rendered through the tray's context view with portrait, actor, run identity, lifecycle, elapsed time and latest event. A labelled ◆ connects the tray and timeline. The selected event on Main belongs to the reviewer, so its tray selection now follows that run; the earlier builder-focused caption that also claimed nothing was selected is removed. Every original timeline event, activity value and run fact is compared before and after, with only selection flags allowed to change. Captions' remaining facts are checked in their new destinations. Pending's full run ID is retained in its strip. Blocking's halt-record run ID remains distinct from its reviewed-run identity.

The 3 causal connectors are explicit. Main joins the 19:43:00 cycle intent to the 19:43:03 first transient outcome. Blocking moves the 3 filled, numbered strike marks to the escalation evidence, where the connector terminates at AUDIT-0029's packet link; F1, all 3 cycles and the refusal-evidence root cause remain in text. Pending replaces the empty outcome row and repeated waiting field with an open connector naming the intent and its future ref, with elapsed time 1 m 34 s and the 19:53:48 observation preserved. Recovery and reconciliation explanations retain their distinct facts.

Wall has 1 shared event band across timeline, payload and detail, with matching labelled markers on all 3 columns. Its selected-event object supplies the band, selected row summary and payload excerpt; duplicated event identity, timestamp and actor lines leave the detail header. The unrelated builder-session stream is replaced by the reviewer's attempt 1, exit code 1 and empty text. The payload file referenced by the drawing is absent locally, and the station's synthetic event uses another ID and no payload, so neither is presented as the drawing's raw bytes. The panel explicitly labels the 3-field JSON as a drawn excerpt derived from the selected event's summary, with full bytes not supplied. This limitation remains for Cowork's native pass; no vendor schema or unseen payload is asserted.

The station keeps at most 1 current bubble per room. After each rendered projection, newest-first rectangle checks hide older overlaps immediately, including during opacity transitions. Offscreen bubbles and bubbles under the HUD or pane are also hidden. The original 7-second real-time lifetime remains for runs and fixtures; the arbiter's prior 9-second exception now uses the same 7-second rule required by this handoff. Hidden voices retain their textual event in the room's snapshot. A followed room gains 1 dispatch sentence joining actual speaker, time, event kind, room and summary. Room chips expose the latest event text and its full accessible name; the pane and calm wall retain the snapshot's words, including fixture and closed-run events.

## Verification

| Check | Observed result |
| --- | --- |
| Source comparison | All original event records, activity values and run facts match; every migrated caption's retained facts have a checked destination. |
| Desk fixtures | Boards 3, 4 and 5 at 1440 × 1000, normal/calm: 1 strip per board, each 51.875 px tall, with unchanged normal/calm geometry and 0 horizontal overflow. |
| Wall fixture | 2560 × 1000, normal/calm: the band spans all 3 evidence columns, whose bounds start below it without overlap; reviewer payload values agree with the selected sample. |
| Text and accessible names | New desk text pairs are at least 5.1371:1; wall band pairs at least 9.7857:1. Labelled selection markers appear in Chromium's accessibility tree. |
| Replay at 1440 × 900 | 61 observations over 60.0013 s at ×2, 19:41:20 → 19:43:20; 44 observations with visible speech, maximum 2 concurrent rooms, 0 overlaps and 0 duplicated room voices. |
| Replay at 400 × 700 | 61 observations over 60.0018 s at ×2 over the same range; 37 observations with visible speech, maximum 2 concurrent rooms, 0 overlaps and 0 duplicated room voices. |
| Dispatch | Both widths show kgme.review, 19:43:03 outcome, Review chamber and the first failed reviewer's text. Phone pane remains between HUD bounds. |
| Focus and calm | At each width, 22 focused-room observations cover all 7 rooms; every target is within the deck band and passes center hit testing. Calm has 7 rooms, 3/1 columns and 0 overflow. The system pane retains its fields, focuses Close and restores focus to its trigger. |
| Collision/lifetime functions | 6 checks against the actual source functions cover same-room replacement, nonoverlap, newest overlap, exact 7-second expiry, cleanup and offscreen hiding. |
| Errors and gate | 0 page, console, HTTP or external-request errors; offline make check passes ruff, formatting, lint with 0 blocking findings and 360 tests, 10 deselected, in 32.46 s. |

All 4 board captures and both followed-room captures were inspected. CSS fixtures project source templates and component values without the native canvas runtime or remote font. The station uses the existing local three@0.182.0 copy. No dependency was installed. The first fixture run found that a context leaf shared its wrapper's generated class; separating those classes fixed the doubled layout selector. The final board checks followed the connector layout and accessible-name corrections. The 60-second station measurements are unchanged by those board-only refinements. Cross-realm Node comparisons were normalized to JSON in the harness; this was not a product change.

Closeout validation completed on 2026-10-25T12:53:28-07:00. The 360-test gate and browser measurements ran on 2026-10-24; final document lint has 0 blocking findings.

## Scores and boundary

The handed-off decisions are implemented: context strip 0.9; tray/timeline marker 0.6; wall selection 0.8 and F6 0.4; each of 3 connectors 0.8; bubbles and dispatch 1.2. Each decision at or above 0.5 remains on the README's approval screen. Reversible implementation choices: reuse the tray's context view, 2 × 0.2 = 0.4; a labelled diamond marker, 1 × 0.2 = 0.2; place the strike connector beside the packet, 2 × 0.2 = 0.4; clearly identify missing full payload bytes and show only the summary-derived excerpt, 2 × 0.2 = 0.4; exclude clipped/occluded bubbles while keeping their words, 2 × 0.1 = 0.2. No additional brief is needed. The lessons file stays at 40 lines and records the root/leaf class distinction.

Rows 13 and 14 are done as builder deliveries. Cowork's native paint, interactions and publication remain pending. Row 15, CDH-0027 with CW32 and CW33, stays proposed until CDH-0026's native pass. No content in that handoff was changed.

## Delivered text SHA-256

The report excludes its own digest. Shared README hashes describe this delivery only.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/Main.dc.html | d8ad1c74abfe6cb4e5ad023e2fe259fd6dc92c95eebfa3d174a388b0a87984e9 |
| docs/design/cockpit-v0/Blocking.dc.html | fd5025a2869d4696a6414c9219453ec8143265368522dd1c9320f9243eaecbbe |
| docs/design/cockpit-v0/Pending.dc.html | a24871500004907af4748348d7e9051d712d78b63390d1a22e07bae3f6163eaa |
| docs/design/cockpit-v0/Wall.dc.html | c2ac76ed5353f2643044bf0043783fe292559be3e80d09d996a25301ae6873ea |
| docs/design/cockpit-v0/Tray.dc.html | a57c9eb32861147efabfbe152ff7c4548f524185a35982ad7cc3de10352449b4 |
| docs/design/cockpit-v0/station/index.html | eb056cac5c5110708d253b65ee702ff96b1c7237a785eff4b708495915956ab3 |
| docs/handoff/cockpit-design/2026-10-22-selection-and-causality.md | e289cddd88d7852d99d1e779421f1a4daa9c70983df020bb9853e8af3aad9d76 |
| docs/handoff/cockpit-design/README.md | 7c117d35e749cc377f9c47f6100704ac2a9763263d11251100eaf712c089e0bb |
| docs/readers/cockpit-design-lessons.md | a28a0663aa750ee1b5b79ff86b10d44c70484db66c06e290b61aca9ab5e63b7c |

## Evidence SHA-256

All evidence remains local and gitignored.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/cdh-0026/board-Main.png | 8cc1a6ab1caae35e31b9dd7b589ecfc47037aabc78cfe2541b81235582508a7c |
| logs/scratch/design-review/cdh-0026/board-Blocking.png | 82aca9003be8d670d8b8eee085e0c2b44c7876257c3268cdda2486e102db52c3 |
| logs/scratch/design-review/cdh-0026/board-Pending.png | 24d0ebcf469e03ee01554bb9795662fab3bd63c7fe5965ecd1891cf240235e61 |
| logs/scratch/design-review/cdh-0026/board-Wall.png | c78a83e2fede7e7e7ae8903e599154e1f6328bd8bdb1a586f5d4a0de27679941 |
| logs/scratch/design-review/cdh-0026/station-dispatch-1440.png | d416e382d095722beb37f45d4ebc92a4d4e2395458be4a75358705a4176cf8e6 |
| logs/scratch/design-review/cdh-0026/station-dispatch-400.png | 0b81c107bff32dfc7e4cf08b87ee4a5a1f8116fe759a551604fe740e3cec7512 |
| logs/scratch/design-review/cdh-0026/station-calm-1440.png | 25414e2ad277bbd21d559332a4d87957fecaef7f980f19db567fd4503f2bffad |
| logs/scratch/design-review/cdh-0026/station-calm-400.png | aa6a2615a8e4b1d3877e1b7e0cc41909be697a46c547f619bf634c06587c1528 |
| logs/scratch/design-review/cdh-0026/source-checks.json | 374c84ad7a25f31b9a3394a98f58e33f1026cafac531b78dacfcc7ed33b656ae |
| logs/scratch/design-review/cdh-0026/bubble-checks.json | 96c4376d1e4251ba92cecec9fb8be3608a8c2647a88df15dbae74c532ede3468 |
| logs/scratch/design-review/cdh-0026/css-manifest.json | a5629cd64cb3b0542cb1ca586268e1e7bb92136674f9b2bef27713809162e68b |
| logs/scratch/design-review/cdh-0026/check-source.mjs | d7c69191ccc1e67695007e8fcfde977b952e57d510c7ee331916b21b70346efa |
| logs/scratch/design-review/cdh-0026/check-bubbles.mjs | d543baebaf50269891ab1abeb238bcb9f346e0d160c9b368ef32bfb439a2e14d |
| logs/scratch/design-review/cdh-0026/projection.mjs | bdcd18cf433d1e427574edf19ceaf43fd0c812dbc90222f995a03569842da5ec |
| logs/scratch/design-review/cdh-0026/verify.mjs | dfb08e12cd4609ed9ce362e1493bfe47afc6bda86017983fb4d1bddd49a70eab |
| logs/scratch/design-review/cdh-0026/make-check.log | ba93f298b42b03a1c3d70a1940f574e245f8a57b07046b410656dcfcd7042b86 |
| logs/scratch/design-review/cdh-0026/closeout-lint.log | a26995d90ef6c34998e64b8a07011648de7d4d4f20f4beebe63f4b91bcb29d40 |
