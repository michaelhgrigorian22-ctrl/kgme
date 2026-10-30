---
name: kgme-builder
description: Build one crew task of a KGME handoff from its own workspace at the loose level, to a PASS review and one commit of the task's Outputs on the task branch by pathspec, with nobody watching.
---

# kgme-builder

You are a `loose` builder in a KGME workspace (`~/Projects/KGME/work/<handoff>-<task>/`), on branch `crew/<handoff>/<task>`, with one task: its Outputs, its acceptance check and its description came on your first line. `CLAUDE.md` governs; this skill is the route.

## The route (HANDOFF-0048 amendment 2)
1. **Red first.** Run the task's acceptance check and see it red. If it is green already, say so and stop: the task is misdescribed.
2. **Build** inside the Outputs (plus `tests/` and `logs/scratch/`); the guard and the sandbox refuse everything else, and the merge gate refuses it again later. Keep files near 300 lines, effects named `read_*`, `write_*`, `run_*` and apart from logic (ADR-015).
3. **Check.** The acceptance check red first, then green. Do not take `make check` run here as the gate: the sandbox denies the network the server tests need and the loop fence colours the hook tests, so it is red here while green at the gate; the review (step 4) runs `make check`, ruff and lint included, outside the sandbox and reports a red one to you.
4. **Stage and review.** `git add -- <path>`, one call per Output, then
   `uv run --frozen --project <main checkout> kgme review --handoff <handoff>:<task>`
   exactly as your first line gives it (the main checkout is the one that line names, `~/Projects/KGME/brain` for the real crew; the review runs outside the sandbox, its ledger and audit are the main checkout's, its gate and diff are this workspace's). The level's list names each Output's path exactly: a `git add` with two paths, or a review without `--project`, is refused. A BLOCK comes back as an audit file; fix each blocking finding starting from a red command, write `logs/scratch/dispositions.md` (one line per finding), and run the next cycle with `--dispositions logs/scratch/dispositions.md`. Two cycles on one finding go to the arbiter pair by themselves; execute the ruling.
5. **Commit on PASS**, by pathspec, one call per Output:
   `git commit --only <path> -m "crew: <task> (<handoff>)"`
   Never `git add -A`, `git commit -a`, `--amend`, a commit naming two paths, a checkout, a push, or a commit on any other branch; the level refuses them and the gate quarantines a branch that carries anything outside the Outputs.
6. **Stop.** The crew's merge gate, the integration and Michou's approval are not yours.

## Never
Edit a human path, a dependency file, `kgme.toml`, the hooks, or the handoff. Touch another task's Outputs. Run the reviewer with write access. Ask: there is nobody; decide, record why in your dispositions, keep going, and stop only when progress stops.
