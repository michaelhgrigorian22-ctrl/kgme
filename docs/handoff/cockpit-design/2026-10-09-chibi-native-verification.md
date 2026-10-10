---
id: CDH-0004
type: handoff
created: 2026-10-09T23:06:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0003]
design_track: HANDOFF-0036
---

# CDH-0004: Read-only design review of the native board (after CDH-0003)

## Outcome and authority

An independent, read-only review of CDH-0003's commit on branch `design`, in Codex's reviewer role (Michou, 2026-10-09 23:13: Codex reviews only until HANDOFF-0042). Executable when Michou adopts it and pastes the start prompt into Codex after CDH-0003 is `done`. The reviewer reads source and the captures; it does not edit, commit, or approve. Revised 2026-10-09T23:18:00-07:00.

## Do

1. From `~/Projects/Automate-design` on branch `design`, run the design review prompt as updated by CDH-0003 step 8, in read-only mode, with the captures under `logs/scratch/design-review/cdh-0003/` as image input:
   `codex exec -s read-only -m gpt-6-astra "$(cat tools/review/design-prompt.md)" > logs/scratch/design-review/cdh-0004-review.md`
2. The prompt's three sections apply: Findings (`F` ids, one ADR-016 class each, file:line), Verdict (`PASS` or `BLOCK: N`), Notes. Judge board 10 against AUDIT-CDH-0002 (CW1–CW3 must be resolved; CW4 and CW5 are closed as drawn and are not findings), the one rule, the keyboard map, Phase 2 dashing, contrast, and whether each actor's `<symbol>` matches its file under `chibi/`.
3. Cowork turns the scratch file into `docs/audit/cockpit-design/cdh-0004-design-review.md` with report frontmatter (`id: AUDIT-CDH-0004`, `author: codex`, `source: inferred`, the reviewed sha), commits it on `design` by pathspec, and returns the findings to Michou for rulings.

## Closeout

Findings return to Michou. Accepted fixes go to Cowork as a further CDH; a `PASS` here plus Michou's own look at the review copy is what HANDOFF-0036's acceptance test is run against. The design-track files are merged to `main` on Michou's word, never by this handoff.
