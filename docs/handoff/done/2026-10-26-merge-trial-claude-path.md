---
id: HANDOFF-0062
type: handoff
created: 2026-10-26T13:14:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-26T13:42:16-07:00
report: docs/audit/2026-10-26-merge-trial-claude-path.md
depends_on: [HANDOFF-0059, HANDOFF-0055, HANDOFF-0057]
plan_ref: PLAN-PHASE-1 step 10d
---

# Handoff 0062 — The merge trial finds `claude`: design landings refused since the mods arrived

## Why
Found by Cowork at the 2026-10-26 13:00 handover. Since Michou's morning commit brought `mods/` onto `main` (`b2ddced`, 09:37), every `kgme merge design` trial has been refused: eight red trials between 09:28:30 and 12:56:19, every one with the same two lines, `mods/kgme-capture: claude is not on PATH, so the mod cannot be validated [blocking]` and the same for `kgme-cockpit` (`logs/scratch/merge/trial-1d391c743bc6.log`, lines 212–215, and the seven before it). The design branch is five commits ahead (`066ae59`, CDH-0032 reviewed natively, PASS; CDH-0031 ready) and touches no code. The last landing is `0d13272`.

The cause is on `main`, not on `design`, and it is HANDOFF-0057's shape again: the trial runs `make check` in a clone under the hook's environment, and `control/git-hooks/post-commit` pins `PATH` to `$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin` (the lesson of AUDIT-0009, so `uv` and `gh` resolve). `kgme/mods.py` `run_check` looks `claude` up on that `PATH` (`shutil.which`, line 123) and, finding none, reports a blocking line per mod folder (line 136): a correct check in an interactive shell, a false refusal in a hook. The same `make check` is green in Claude Code's own shell, which is why the overnight run and AUDIT-0136 never saw it.

## What
1. **Measure first.** In a shell: `which -a claude` (the Housekeeping item; the stale 2.1.111 may be one of the answers), and `sh -c 'PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"; command -v claude; echo $?'`, which reproduces the hook's view. The report records both outputs. If the second finds `claude`, the cause is elsewhere (the trial's `env`, `kgme/merge.py` line 119) and the fix follows the measurement, not this text.
2. **Fix the named cause, nothing else.** The route is yours; the boundary is that the check is not weakened: a mod that `claude plugin validate` would refuse must still block in the trial. Two routes that respect it: the hook's `PATH` line gains the folder the measurement names (a human path, `control/git-hooks/post-commit`: a diff for Michou); or `kgme.toml [mods]` names the executable (`claude = "<path>"`, also a human path) and `run_check` takes it before `PATH`. A third, the mod step passing when `claude` is absent, is refused: it would make the trial green on a machine with no Claude Code and the check would measure nothing.
3. **A check that catches the next one.** `make check` gains a fast-tier case that resolves every executable the hook needs (`uv`, `gh`, `claude`, and whatever else the hook and `kgme merge` call) under the hook's own `PATH` line, read from the hook file, not retyped, so a tool moving to a folder the hook does not name is red in the shell before it is red in a trial.
4. **Close by observation.** After Michou's commit, the next commit on `main` lands the five design commits by itself, or `kgme merge design` run by hand does; the report names the landing commit and the trial log that was green.

## Outputs
`kgme/mods.py` only if route 2b is taken, `kgme/merge.py` only if the measurement names it, `tests/test_hook_path.py` (item 3), `control/git-hooks/post-commit` or `kgme.toml` (human path: a diff under `logs/scratch/handoff-0062/`), a measurement note in the report.

## Acceptance test (under five minutes)
`sh -c` with the hook's `PATH` line finds `claude`. The new test is red when a tool's folder is removed from a copy of the line and green on the real one. A fresh clone of `main` passes `make check` under the hook's environment. The design branch is level with `main` after one commit.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one `PATH` line or one `kgme.toml` key, one test. `git revert`.

## Needs from Michou
Adoption; applying the one human-path diff; running `kgme sync` once so the four merge-trial events since `1d391c7` are committed.

## Report
`docs/audit/2026-10-DD-merge-trial-claude-path.md`. Set `status: done`, `completed:`. Commit `merge: the trial resolves claude under the hook's PATH; a check for the hook's tools (HANDOFF-0062)`.
