---
id: AUDIT-CDH-0033-DIRECTION-2
type: report
created: 2026-10-28T22:02:16-07:00
author: codex
source: inferred
sources: [CDH-0033, AUDIT-CDH-0033-DIRECTION]
tier: 2
status: final
handoff: CDH-0033
period: "2026-10-28"
reviewed_sha: 9c360af
---

# CDH-0033: three different places

Michou's 21:20 ruling reopens the station's geometry and camera. These 3 scratch directions retain the sky, cast, 7 room identities/mappings and HTML facts. Each pair contains **9c360af left, sketch right**, at 1440 × 900. The 9 captures support direction selection, not acceptance.

| Direction | Deck | Following Workshop | Calm | GPU mean, deck / Workshop, ms |
| --- | --- | --- | --- | ---: |
| 1. Inside the ship | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-1/comparison-deck.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-1/comparison-workshop.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-1/comparison-calm.png) | 10.92 / 9.31 |
| 2. Dock and board | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-2/comparison-deck.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-2/comparison-workshop.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-2/comparison-calm.png) | 5.04 / 8.17 |
| 3. The archive cathedral | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-3/comparison-deck.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-3/comparison-workshop.png) | [Pair](../../../logs/scratch/design-review/cdh-0033/sketch-3/comparison-calm.png) | 6.54 / 4.86 |
| 9c360af baseline | | | | 5.57 / 5.89 |

Timing uses Chrome/Metal, M4 Pro, DPR 1, 5 seconds, 301 GPU samples per rendered state, replay paused at `2026-10-08T19:45:00-07:00`. GPU queries exclude CSS3D composition, startup and camera transitions. Final RAF means are approximately 16.67 ms. Short samples vary; direction 2's interior is direction 1's. These observations do not establish the 30-second ×2 budget. Calm GPU time is 0 throughout.

**1. Inside the ship.** A perspective concourse replaces the tray: walls, ceiling ribs, corridors, 7 furnished bays, door signs and mounted screens sharing the pane's rows. Following enters Workshop in 480 ms. **Plausible tonight**, concentrating B on routes and work poses. Risks are moving sign projections, DOM crew/screens painting through walls, and placement beside the pane. Phone framing is unmeasured; the corridor needs authored 400 px views.

**2. Dock and board.** A low approach retains the approved hull and dreadnaught. The 7 original buttons and live rows occupy bridge windows; boarding reaches direction 1's interior in 480 ms. **Conditional tonight:** two scene sets, focus ownership and docking consume time otherwise available for B. Oblique glass makes overview words small; the pane supplies readable detail. Phone skips the exterior and inherits the unvalidated interior framing.

**3. The archive cathedral.** Seven terraces climb around a suspended luminous volume, with arches, spiral stairs and lift shafts. Following reaches Workshop. **The least certain full A–D delivery tonight:** vertical crew routes and visibility add substantial work. Chip bounds separate, but signs and event bubbles still visibly crowd one another. The pane cuts across the architecture. At ≤720 px this prototype starts on today's calm wall, an explicit fallback awaiting phone acceptance.

All 3 calm captures differ by **0 of 1,296,000 pixels**, with 7 rooms and 0 render calls. Default deck chip overlaps are 0 at 1440; 400/800 remain unchecked. Page errors and external requests are 0. Reduced-motion branches snap travel and stop decorative motion; whole-stage stillness is unverified. No tests, contrast/focus sweep, phone timing, Safari pass or acceptance gate ran.

I recommend **1** to put the night into the crew; **3** makes the largest departure. The choice scores 4 × 0.8 = 3.2. Evidence and source hashes: [1](../../../logs/scratch/design-review/cdh-0033/sketch-1/measurements.json), [2](../../../logs/scratch/design-review/cdh-0033/sketch-2/measurements.json), [3](../../../logs/scratch/design-review/cdh-0033/sketch-3/measurements.json). Only this draft is committed; the station is untouched. Stop for Michou's pick; record the ruling and tally on resumption.

Decision closure, 2026-10-28T23:00:00-07:00: Michou selected direction 1 from the second brief, with the conditions recorded on the handoff README's Asked-and-answered line. This direction record is final; its observations above remain those of the draft, and it certifies no implementation.
