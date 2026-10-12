---
id: CDH-0005
type: handoff
created: 2026-10-11T16:55:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0003, CDH-0004]
design_track: HANDOFF-0036
---

# CDH-0005: Read-only design review of the native board

## Outcome and authority

An independent, read-only review of the rebuilt board 10 as committed on branch `design` (CDH-0003, `0bb87d5`) and verified natively by Cowork (CDH-0004), in Codex's reviewer role (Michou, 2026-10-09 23:13: Codex reviews only until HANDOFF-0042). Executable when Michou adopts it by pasting the start prompt into Codex after CDH-0004 is `done`. The reviewer reads source and captures; it does not edit, commit, or approve.

## Do

1. From `~/Projects/Automate-design` on branch `design`, run the design review prompt as updated by CDH-0003 step 8, read-only, with the captures under `logs/scratch/design-review/cdh-0003/` and `logs/scratch/design-review/cdh-0004/` as image input:
   `codex exec -s read-only -m gpt-6-astra "$(cat tools/review/design-prompt.md)" > logs/scratch/design-review/cdh-0005-review.md`
2. The prompt's three sections apply: Findings (`F` ids, one ADR-016 class each, file:line), Verdict (`PASS` or `BLOCK: N`), Notes. Judge board 10 against AUDIT-CDH-0002 (CW1–CW3 must be resolved; CW4 and CW5 are closed as drawn and are not findings) and AUDIT-CDH-0004, the one rule, the keyboard map, Phase 2 dashing, contrast, and whether each actor's `<symbol>` matches its file under `chibi/` (the drift test is the mechanical form of that check).
3. Cowork turns the scratch file into `docs/audit/cockpit-design/cdh-0005-design-review.md` with report frontmatter (`id: AUDIT-CDH-0005`, `author: codex`, `source: inferred`, the reviewed sha), commits it on `design` by pathspec, and returns the findings to Michou for rulings.

## Closeout

Findings return to Michou. Accepted fixes go out as a further CDH; a `PASS` here plus Michou's own look at the review copy is what HANDOFF-0036's acceptance test is run against.
