---
id: AUDIT-CDH-0025
type: report
created: 2026-10-22T11:18:51-07:00
handoff: CDH-0025
period: "2026-10-22"
source: inferred
sources:
  - CDH-0025
  - docs/design/cockpit-v0/
  - logs/scratch/design-review/cdh-0025/
author: codex
status: final
tier: 2
---

# CDH-0025 implementation

Activity is drawn as columns on five operating boards and in board 1's specimen. Source, CSS geometry, accessibility names and the repository gate pass. This is builder verification; Cowork's native review is pending. The row starts from d67613c, after CDH-0023; its System-field closeout correction is separately committed as 1a43e0d. Michou's answer is recorded in the separate ac6351b commit. The implementation stops here under the current two-row mandate.

## Data and behavior

Each desk panel takes the last 60 entries of its original 96-entry array; Wall retains all 240. Order is unchanged. Each known count controls column height on the fixed 0–5 scale, with zero genuinely zero-height and five or more capped with +. Cyan outlines make every nonzero column boundary readable independently of the optional fill ramp. B and P are glyphs, not colour-only state. Each of the 480 bucket elements has its time and exact known count in an accessible name and a native title; no digit is printed inside a column.

The existing 7 and 9 entries are pending/blocking sentinels, not event quantities. Their numeric counts are null, their marks are P? and B?, and their labels and summaries explicitly say count unavailable. They draw no quantitative bar. Known totals and peaks exclude both. Michou confirmed "Keep counts explicitly unavailable" in this session; this is acted on, not an unresolved brief. Board 1 separately supplies nine labelled specimen values, including 5, 8, a counted blocking bucket and a counted pending bucket, to demonstrate cap and state behavior without changing source readings.

The time labels describe the start of each one-minute bucket, ending with the current partial minute from the sample clock. The disconnected chart uses the snapshot's 19:52 minute, not its later disconnected clock. This makes the desk contract 60 buckets and the wall contract 240. The axis states 60 minutes or 4 hours, with 1 min/bucket. Old left-edge labels that implied a 61st or 241st minute are corrected to this convention. Times are drawing labels derived from the sample, not newly fetched events.

The summary is one paragraph below the chart and axis; it wraps in the existing narrow panel rather than clipping. It gives peak, total, blocking times and pending times where applicable. The old digit cells and prose captions are removed. No other panel or operational fact is redesigned.

| Board | Buckets | First–last bucket | Total | Peak/min | Panel height before → after, px |
| --- | --- | --- | --- | --- | --- |
| Main | 60 | 18:53–19:52 | 88 | 5 | 210.9688 → 210.9688 |
| Blocking | 60 | 08:50–09:49 | 68 known | 4 known | 210.9688 → 226.9063 |
| Pending | 60 | 18:54–19:53 | 83 known | 4 known | 195.0313 → 242.8438 |
| Disconnected | 60 | 18:53–19:52 | 85 | 4 | 191.9219 → 191.9688 |
| Wall | 240 | 15:53–19:52 | 131 | 5 | 245.0313 → 245.0313 |

Blocking is at 09:49 and pending at 19:53. Their missing counts are explicitly excluded, so 68 and 83 are known totals, and their peak 4 values are known peaks. Every other count is unchanged. The 232 px desk and 440 px wall panel widths are preserved. The Blocking and Pending height increases are exactly their summary's additional wrapped lines. Main and Wall retain their heights. Disconnected trades 19 px of chart height for the newly required axis, retaining its panel height within 0.0469 px of rounding. The full component-board projection confirms identical positions, widths and heights for every surrounding panel after the compact specimen is fitted.

## Verification

Node checks compare all retained raw values with their source arrays, count every bucket, verify every state, time, label, mark and summary, and check nine specimen cases. The CSS projections use the actual source styles and render functions at 1440 px, and 2560 for Wall. All known column heights match count/5 within 0.03 px, with values of five or more at the cap; unknowns and zeros are zero-height. Chrome's accessibility tree exposes all 480 bucket names plus the nine specimen names. No page, console, HTTP or external-request errors occurred. All six column captures and the full component projection are recorded below; representative live, pending, wall and specimen captures were visually inspected.

Contrast uses linearized sRGB after the actual stale filter where present. Ordinary summary text is 5.3236:1 against the panel; marks are 15.1151:1 on their ground; cyan bar edges are 10.1408:1. The disconnected summary and axis use the existing stale-safe token a3b0b8: 4.6703:1 after saturate(.12) and brightness(.72). Its marks would be 7.8716:1 and its bar edges are 4.9383:1. The local projections use fallback monospace and do not prove native canvas paint or screen-reader behavior in the artifact host.

The first layout check found an extra row from the disconnected header; removing the redundant duration there left the duration on its axis. The full component projection found a 42 px expansion; a 32 px specimen and shorter legend preserve the surrounding panel dimensions. The stale context was added to the fixture and its new text token corrected before the final contrast pass. These were local implementation checks, not additional native review findings.

The final offline make check passes ruff, format, kgme lint with 0 blocking findings, and 360 tests, 10 deselected. The initial sandbox attempt could not open the existing uv cache; the approved offline command completed. Report frontmatter is linted separately after closeout. No dependency was installed and no network was used.

## Decisions, lessons and stop

CW29's 2 × 0.4 = 0.8 decision is built and remains on the approval screen pending native review; F7's bucket contract is built at 2 × 0.2 = 0.4. The unknown-count treatment is Michou's explicit ruling, executed and separately recorded, with the recommendation tally 6 of 6. New reversible choices are 2 × 0.2 = 0.4 for partial-minute labels anchored to the sample clock, 1 × 0.2 = 0.2 for wrapping the summary within the fixed panel width, and 1 × 0.1 = 0.1 for a compact component specimen. The stale-safe text and high-contrast bar boundary are mechanical checks, not approval questions. The 40-line lessons file now records that a state sentinel must never be silently treated as a count.

Cowork must inspect native paint, focus and clicks and publish the artifacts. No Cowork row is marked done or ready. CDH-0024, CDH-0026 and CDH-0027 remain untouched. Main advanced externally from the recorded e91c98d5a9af85cf21e49179bfaa9e670e26ae5e to b9390c1bc348068baad7f92fa9ac1611a52230d0 during the run. Step 1 remains done in 67bfebb; no merge or push was attempted.

## Delivered text SHA-256

The report is excluded from its own digest.

| File | SHA-256 |
| --- | --- |
| docs/design/cockpit-v0/Main.dc.html | 7a9886c19087ec59d433a8e7bd263eb5b1758744d48bee30a5b9416f8a09dcf8 |
| docs/design/cockpit-v0/Blocking.dc.html | 3fb14e7b9483bcc709be93954034be14e57de992912e44c9d82c9b88f7e12a65 |
| docs/design/cockpit-v0/Pending.dc.html | e38fe0f52d4055e03f7cc423ada6472a2f89a84ee60898db596b2c51912b1bff |
| docs/design/cockpit-v0/Disconnected.dc.html | 680df82aff96a9586ac523b911c5777a23f996d0c97841d784b9d31d2868ec26 |
| docs/design/cockpit-v0/Wall.dc.html | 853b2a885aaa87ab5900f519800979ec90cf9f10d648858abf7253ae4c426670 |
| docs/design/cockpit-v0/Components.dc.html | c1a70e13d5d907843a8f8c10cbabb44a6de745a6c7c6684f1e0eed58781f1efa |
| docs/readers/cockpit-design-lessons.md | 0d827dd8f1836274e8296c9ef7f8300839227f8668daafccdaa73b808019313a |
| docs/handoff/cockpit-design/2026-10-22-activity-columns.md | ee8eeb0b640ddd4b63b77ebaf9ea6698377c30154e8e87a63a841c12f91b0889 |
| docs/handoff/cockpit-design/README.md | be47d17eb69f922bc5bbc96666fcdbddb489ae16468438ee820218a7490b1e4b |

## Evidence SHA-256

All evidence remains gitignored under logs/scratch/design-review/cdh-0025/.

| Evidence | SHA-256 |
| --- | --- |
| columns-Blocking.png | 42549f65e4dd595d1ccb9e9304f6b0d3906fe1474632d84fcba285f00fe6a7b4 |
| columns-Components.png | 8bfbbd7bb1c84189085274555ef674c58548b15cfda497382cf9b340aa2beb42 |
| columns-Disconnected.png | 0592ea8363131a2b206461d96599d76a9d9f37283fcb59f772ca74188559503a |
| columns-Main.png | c810b313c583eff8f8c09654359f27790955bdfd4417552f2506f5951de1d296 |
| columns-Pending.png | 84b0f80119341583a8bc8d1be9cda9e20559d4384c5ce5b36c3d7a64061d269e |
| columns-Wall.png | fcf6fb5e3f6bd27ef5e2e909c75dee5ec683a90d1b2a089ce73b48ada5fc8d5a |
| full-Components.png | e700bb249308ab6220129164a4f445efb11668a565861e929c11bfe85930d583 |
| bucket-inputs.json | efdc926d7dbe794ace57474f23604f01ef72012476850e6e9b8c37f499fe5788 |
| source-checks.json | 9004f7bb99e80b707d54a431866add87058fdfb27ce5001aaf435e1604b8f9f5 |
| css-manifest.json | 805913009129b0631099279b3dd31b3ddb405779d3e83dfcbb09d85ff03fcca3 |
| check-source.mjs | 336345b07aaeedd163b01d5270c052b5a88ae587f194884a53ee36e0b10af0b5 |
| projection.mjs | bdcd18cf433d1e427574edf19ceaf43fd0c812dbc90222f995a03569842da5ec |
| verify.mjs | 99daecaa2950a61f1e7a60031c92fd863cb6fe1a112b9903a415b6caad52f297 |
| make-check.log | 01d9e3c57cde1aa821307ef8771126ddde0d3dd2d0b143e49c37f23e4a2a5152 |
