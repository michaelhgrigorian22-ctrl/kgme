---
id: AUDIT-CDH-0024
type: report
created: 2026-10-24T19:35:08-07:00
handoff: CDH-0024
period: "2026-10-24"
source: inferred
sources:
  - CDH-0024
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0024/
author: codex
status: final
tier: 2
---

# CDH-0024 implementation

The persistent disconnect band and CW31 correction are built from aa71b32 on design. Michou authorized rows 13 and 14 in order, with separate reports and commits and no merge or push. This is builder verification; Cowork's native pass remains pending. Main starts and remains a7efad19d3bd41dde649ef37f926192aa1b570b2.

## Delivery and evidence

Board 6 replaces the central modal and whole-workspace filter with 1 persistent band beneath the compact header. Its 13 checked fact destinations preserve last event and age, refused origin, retry cadence and attempt, durability, recovery, retry and calm hints. The grey static frame remains. The snapshot has 1 as-of boundary; the timeline and detail are focusable, and the header tray retains its stale state without another timestamp. Recovery instructions, the Dock and Phase 3 explanation, the ledger path and the frame's meaning live under board 7's When disconnected heading and System fields. The ledger path now fills its previously absent field, once.

CW31 compares numeric values, not string presence: board 7 supplies 18/20, board 6 renders 18/20, and its measured fill is 90%. The label derives from the same numeric value as the fill; additional 80%, 90% and 100% inputs preserve that equality, and 31% remains hidden.

At 1440 × 900, the band is 1368 × 70.30 px, from y=86.94 to 157.23. Timeline and detail start at y=189.17, with 0 overlap or horizontal overflow. Normal and calm fixtures have identical geometry. Tab visits the header tray, band, timeline and detail; all 4 targets have a solid outline and pass center hit testing. The measured muted text pairs have a minimum ratio of 7.7181:1. There is no snapshot filter. All 3 fixture pages record 0 page, console, HTTP or external-request errors. Board and help captures were visually inspected. CSS projection uses the source templates and component values, without the native canvas runtime or remote font; native behavior remains unverified.

The offline make check passes ruff, formatting, lint with 0 blocking findings, and 360 tests, 10 deselected. The local listener and uv cache initially required sandbox approval; approved local/offline commands completed. A case-sensitive harness assertion was corrected for the help heading's CSS uppercase; it was not a product failure. Source verification and the fixture were rerun after moving the ledger path into its System field.

## Decisions

B2 is Michou's taken 1.5 ruling. The single snapshot boundary (0.8) and recovery help (0.6) are implemented and remain on the existing approval screen. CW31 (0.4) follows the record. Reversible implementation choices: remove the stale filter entirely, preserving grey static and explicit stale state, 2 × 0.1 = 0.2; focusable band, timeline and detail regions, 2 × 0.1 = 0.2; ledger path fills its named System field, 1 × 0.1 = 0.1. No new brief is needed. CDH-0026 follows; CDH-0027 remains proposed.

## Delivered text SHA-256

The report excludes its own digest. Shared README hashes describe this delivery only.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/Disconnected.dc.html | 041b01186a6bcb21e38fbdabac815161b73f80b69bffd6cea6ba51238019b6a0 |
| docs/design/cockpit-v0/Keys.dc.html | e3322dc4373abe5943388f0da40d84de25d4ce91cae376871d1f7e3c3c83f991 |
| docs/handoff/cockpit-design/2026-10-22-disconnect-band.md | 3dd846d40138f55dd805cd8f0fe3a0695a811617681b2384c43becd38fec5ebe |
| docs/handoff/cockpit-design/README.md | 13748110f218d1ab8dfaaba0bb959aa0c72da0bdc11a801e1a9d8443b38f884f |

## Evidence SHA-256

All evidence is gitignored and remains local.

| File | SHA-256 |
| --- | --- |
| logs/scratch/design-review/cdh-0024/board.png | 7a4bf45bd2eedcf5029c5ab455105161a7352ddabc883ba75645b5ef2c4303e3 |
| logs/scratch/design-review/cdh-0024/calm.png | 4e4289794e3de72eeb8120d7bd2d020c208ed3f986fbb954c995ce6c554a7a02 |
| logs/scratch/design-review/cdh-0024/keys.png | f7e9740d17c0b46a8c2dc18dc9ecff7e6bb789ab8e38dd4639b2b8722037c1e8 |
| logs/scratch/design-review/cdh-0024/source-checks.json | ffecffbb6a7c019d93c26a6d131c3781f3978484e9b9dd283452e7129a630b7b |
| logs/scratch/design-review/cdh-0024/css-manifest.json | a1d5e7bc715cb444fefd162389ad95f5ffca9dbbee8d3537b6093b7a2c9a241f |
| logs/scratch/design-review/cdh-0024/check-source.mjs | 8715958fe67c6929324351251805a16d6835e94b49f1b2d8606930057018dc90 |
| logs/scratch/design-review/cdh-0024/projection.mjs | bdcd18cf433d1e427574edf19ceaf43fd0c812dbc90222f995a03569842da5ec |
| logs/scratch/design-review/cdh-0024/verify.mjs | 577c76805706c8de6e0f012411efcbd551cb294b90e0b30b1bb3b86ffba725e0 |
