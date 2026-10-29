---
id: AUDIT-CDH-0033-DIRECTION
type: report
created: 2026-10-28T20:39:36-07:00
author: codex
source: inferred
sources: [CDH-0033]
tier: 2
status: final
handoff: CDH-0033
period: "2026-10-28"
reviewed_sha: 9c360af
---

# CDH-0033 direction sketch

This is the 1 scratch direction requested at 20:30, awaiting Michou's look. The accepted hull, sky, dreadnaught and cast keep their geometry and artwork. The committed station remains byte-identical to `9c360af`; only this page is delivered. Each comparison contains 2 unscaled 1440 × 900 captures, **9c360af left, sketch right**, at the same paused replay instant, `2026-10-08T19:45:00-07:00`.

| Whole deck | Following Workshop | Calm |
| --- | --- | --- |
| [Open paired capture](../../../logs/scratch/design-review/cdh-0033/sketch/comparison-deck.png) | [Open paired capture](../../../logs/scratch/design-review/cdh-0033/sketch/comparison-workshop.png) | [Open paired capture](../../../logs/scratch/design-review/cdh-0033/sketch/comparison-calm.png) |

The sketch adds 1 warm directional key with soft 2048 px shadows; procedural brushed copper and glass with edge wear; a 64 px procedural sky cubemap; and thin edge haze. Room light cones peak at 0.065 opacity. Faint state-light pools fake the deck reflection at 0.09 maximum opacity. Bloom is retuned to strength 0.52, radius 0.30 and threshold 0.72, with brighter emissive seams. One copper-framed CSS3D bridge console shares the pane's row renderer: 4 active rows on the deck, the same 2 Workshop rows while following. The final placement clears the room chips and builder in these captures.

The quick measurement used Chrome/Metal on the M4 Pro, DPR 1, 5 seconds and 151 GPU samples per rendered state. GPU queries surround `composer.render`; they exclude CSS composition. These are final-sample **GPU mean / P95 milliseconds**, not end-to-end frame-budget results:

| State | 9c360af | Sketch |
| --- | ---: | ---: |
| Whole deck | 5.624 / 6.373 | 7.808 / 9.487 |
| Workshop | 4.667 / 6.568 | 4.917 / 8.725 |
| Calm | 0 / 0 | 0 / 0 |

Across short observations during screen placement, sketch means ranged 6.337–7.808 ms on deck and 4.917–7.370 ms following. Single removal probes suggested +0.307 ms for shadows, +0.978 ms for materials/environment/fog, +0.464 ms for volumes and −0.019 ms for reflection. All fall below the 1.471 ms deck spread and remain unresolved. Removing the **entire existing bloom pass** saved 3.763 ms; that is not the retune's marginal cost. Screen cost and startup cubemap cost remain unmeasured reliably. Effects are not additive. RAF stayed 33.332 ms mean / 33.4 ms P95 even in calm, so this session cannot establish 60 fps.

Michou's 3 choices each score stakes 4 × edge 0.5 = 2.0 and await his answer:

1. **Shadow weight:** keep the shown soft, moderate shadows or deepen them. I recommend the shown weight because the deck's fittings remain distinct without forming large black patches.
2. **Deck reflection:** keep the restrained 0.09 light pools or push toward a glossy floor. I recommend the pools because the copper highlights and words retain priority.
3. **Screen framing:** keep the opaque copper bezel or use a larger transparent hologram. I recommend this compact console, 352 px on deck and 75% scale following, because its rows stay readable against the sky and clear the crew.

Calm has **0 changed pixels out of 1,296,000** and 0 render calls. Captures recorded 0 page errors and 0 external requests, using local Three.js 0.182.0 and its CSS3D addon. [Source](../../../logs/scratch/design-review/cdh-0033/sketch/station.html), [measurements and hashes](../../../logs/scratch/design-review/cdh-0033/sketch/cost-summary.json) remain in ignored scratch. No tests or acceptance gate ran. Stop here; record his answers on the README's Asked-and-answered line only when resuming CDH-0033.

Decision closure, 2026-10-28T23:00:00-07:00: Michou selected direction 1 from the second brief, with the conditions recorded on the handoff README's Asked-and-answered line. This direction record is final; its observations above remain those of the draft, and it certifies no implementation.
