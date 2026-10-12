---
id: CDH-0006
type: handoff
created: 2026-10-12T15:32:00-07:00
from: cowork
to: cowork
tier: 2
status: proposed
depends_on: [CDH-0003, CDH-0004]
design_track: HANDOFF-0036
verification: CDH-0005
---

# CDH-0006: Fix board 10's hole syntax and re-verify natively

## Outcome and authority

Resolve AUDIT-CDH-0004 CW7 (blocking), and CW8 and CW9 if Michou takes them, in `~/Projects/Automate-design` on branch `design`; re-verify board 10 natively; hand Michou the CDH-0005 paste box. Cowork implements because Codex is review-only until HANDOFF-0042 (Michou, 2026-10-09 23:13) and the fix is mechanical and already validated in the review copy. Executable on Michou's word.

## Do

1. **CW7.** In `docs/design/cockpit-v0/Sprites.dc.html`, inside `<x-dc>…</x-dc>`, rewrite every single-brace hole to double braces with the substitution `(?<![$\{])\{([A-Za-z][A-Za-z0-9_.]*)\}(?!\})` → `{{\1}}` — exactly 51 replacements, the logic block byte-identical. `logs/scratch/design-review/cdh-0004/experiment-Sprites.dc.html` (SHA-256 `a5e612fb…538a`) is that result and may be copied verbatim.
2. **CW8, if taken.** Wrap `.sprite-matrix` and `.palette-grid` in an `overflow-x:auto` box with a `min-width` on the grid, following the fixture's `.matrix-scroll` pattern; no change at 1440 px.
3. **CW9, if taken.** Update the two stale sentences in `chibi/README.md` and the fixture footer to say board 10 now renders the cast natively from inline symbols and that the fixture is the profiling harness.
4. Run `tests/test_design_sprites.py` and `kgme lint`; commit on `design` by pathspec: `design: board 10 holes as {{ }}, narrow-width scroll boxes (CDH-0006)`.
5. Republish the changed files to the private review copy (turn its `calm` tweak off), open board 10 in Play, and confirm natively: matrix, pairs, contexts, the 16 buttons, calm via Tweaks. Captures to `logs/scratch/design-review/cdh-0006/`. Write `docs/audit/cockpit-design/cdh-0006-implementation.md` (`AUDIT-CDH-0006`, report frontmatter, hashes, new source-set digest, what was observed natively) and commit it. Set this file `done` with `completed:`; hand Michou the CDH-0005 paste box with the sha to review.

## Don't

Touch the characters' drawn appearance, the seven SVGs, `characters.css`, any other artboard, ADRs, `kgme.toml`, or `main`. No binaries under `docs/` or `memory/`.
