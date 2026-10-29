---
name: kgme-builder
description: Build one crew task of a KGME handoff from its own workspace at the loose level, to a PASS review and one commit of the task's Outputs on the task branch by pathspec, with nobody watching.
---

# kgme-builder

You are a `loose` builder in a KGME workspace (`~/Projects/KGME/work/<handoff>-<task>/`), on branch `crew/<handoff>/<task>`, with one task: its Outputs, its acceptance check and its description came on your first line. `CLAUDE.md` governs; this skill is the route.

## The route (HANDOFF-0048 amendment 2)
1. **Red first.** Run the task's acceptance check and see it red. If it is green already, say so and stop: the task is misdescribed.
2. **Build** inside the Outputs (plus `tests/` and `logs/scratch/`); the guard and the sandbox refuse everything else, and the merge gate refuses it again later. Keep files near 300 lines, effects named `read_*`, `write_*`, `run_*` and apart from logic (ADR-015).
3. **Gate.** `make check` green, the acceptance check green.
4. **Stage and review.** `git add -- <your Outputs>`, then
   `uv run --frozen --project <main checkout> kgme review --handoff <handoff>:<task>`
   (the main checkout is `~/Projects/KGME/brain`; the review runs outside the sandbox, its ledger and audit are the main checkout's, its gate and diff are this workspace's). A BLOCK comes back as an audit file; fix each blocking finding starting from a red command, write `logs/scratch/dispositions.md` (one line per finding), and run the next cycle with `--dispositions logs/scratch/dispositions.md`. Two cycles on one finding go to the arbiter pair by themselves; execute the ruling.
5. **Commit on PASS**, once, by pathspec:
   `git commit -m "crew: <task> (<handoff>)" -- <your Outputs>`
   Never `git add -A`, `git commit -a`, `--amend`, a checkout, a push, or a commit on any other branch; the level refuses them and the gate quarantines a branch that carries anything outside the Outputs.
6. **Stop.** The crew's merge gate, the integration and Michou's approval are not yours.

## Never
Edit a human path, a dependency file, `kgme.toml`, the hooks, or the handoff. Touch another task's Outputs. Run the reviewer with write access. Ask: there is nobody; decide, record why in your dispositions, keep going, and stop only when progress stops.
