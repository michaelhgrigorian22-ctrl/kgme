---
id: CDH-0029
type: handoff
created: 2026-10-25T15:25:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: done
completed: 2026-10-25T15:44:01-07:00
report: docs/audit/cockpit-design/cdh-0029-implementation.md
adopted_by: michou
adopted: 2026-10-25T15:25:08-07:00
depends_on: [CDH-0028]
design_track: HANDOFF-0036
---

# CDH-0029: More planets, and stars

## Outcome and authority

Michou saw KGME Station version 13 (CDH-0028, `040a5ad`) natively on 2026-10-25 at 15:21: "ya defo needs more planets and some stars but its looking fire so far." The direction is taken; this row turns it up. It is `ready` now: Cowork's native pass of CDH-0028 is folded into the pass of this row, since Michou's judgement of the look was the review that mattered and he has given it.

Everything CDH-0028 fixed stays fixed: the sky carries no fact, calm removes it, reduced motion stills it, every text keeps 4.5:1 against its sampled background, no new dependency, no image files, the frame-time budget of 2 ms over the CDH-0026 baseline, the 400 px simplification.

## Do

1. **Planets: more of them.** Three became the floor. Aim for six to eight at 1440, at clearly different depths and sizes, so the sky reads as a system, not a backdrop: one or two large and near (the ringed one stays), several mid-distance, a few small and far. Vary them: banded gas giants, a cratered rock, an ice-blue one, one with a second thin ring or a close moon pair. Colours stay the cockpit's pushed palette (cyan, magenta, amber, green, dark ground), never pastel, never brighter than the deck's lines or the HUD text. Each rotates at its own slow rate (minutes per turn). None sits behind the HUD bands, a chip, a bubble or the pane; the darker bands behind the HUDs stay.
2. **Stars: a real field.** The current 900 points are too few and too even. Build at least two layers at different depths for parallax when the deck pans: a dense far layer of faint stars (thousands of points, size 1, mostly dim), and a sparser near layer of brighter ones with a few tinted cyan, magenta and amber. A gentle twinkle on a small fraction (an opacity ramp over seconds, never a flash) is allowed under full motion and stops under reduced motion. Keep the point sprites cheap: one `Points` object per layer, no per-star meshes.
3. **The wash** may gain a second ribbon or a brighter core where the planets cluster, still restrained and still darker behind the HUD bands.
4. **At 400 px** keep the simplification rule: fewer planets (the near ringed one, a moon, one far), one star layer.

## Verify

As CDH-0028's verify, with the counts recorded: planets and star points per layer at 1440 and 400; the text-background contrast sampling over every text box at the three sizes, deck and pane, calm, reduced motion on and off; sky pixels identical over 10 s under reduced motion; frame intervals over 30 s at ×2 at 1440 × 900 and 400 × 700 against the CDH-0026 baseline, within 2 ms mean and P95; chip overlaps at 400, 800 × 600 and 1440 (none); `make check` green.

Report, close out and commit as for CDH-0023, then stop for Cowork's native pass and Michou's look.

## Acceptance

- Michou looks at it natively and it is more of what he called fire: a populated, deep, trippy space with the station unchanged in it.
- No fact in the sky; calm and reduced motion unchanged in meaning; text reads; the deck leads; no dependency; no frame-time regression beyond the budget.
