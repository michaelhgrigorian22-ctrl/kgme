---
id: HANDOFF-0054
type: handoff
created: 2026-10-21T01:40:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-21T02:10:00-07:00
report: docs/audit/2026-10-21-coherence-commit.md
depends_on: [HANDOFF-0049]
plan_ref: PLAN-PHASE-1 step 9a
---

# Handoff 0054 — The coherence check resolves paths against the commit, not the machine

## Why
Finding from the design track's merge attempt (CDH-0019 step 1, 2026-10-21 01:13): `tests/test_coherence.py::test_the_whole_tree_is_coherent` fails in any fresh checkout. `read_existing_paths` in `kgme/vault.py` walks the working tree, so a path resolves when something on this machine happens to have created it: `logs/trace` (`docs/STATUS.md`) and `logs/scratch/review.patch` (`docs/readers/review-loop.md`) exist in `brain/` only because the hooks and `kgme review` ran there. Cowork reproduced it on `main` at `bda141b` with the tracked set in place of the walk: six findings appear, five under `kgme clean` target roots (`logs/trace`, `logs/scratch` twice, `logs/scratch/review.patch`, `logs/ledger-test`) and one folder that holds no tracked file (`memory/attachments`, present here only through a `.DS_Store`). The check becomes blocking on 2026-10-23 (`kgme.toml [coherence] blocking_from`). Arbiter's route (Cowork, 2026-10-21): the answer must be a function of the commit, so `main`, the design worktree, a fresh clone and a crew workspace agree; the design track's interim placeholders cover it until this lands.

## What
1. **Existing paths are the index, not the walk.** `read_existing_paths` becomes the paths `git ls-files` lists (tracked and staged) with every parent folder; the `os.walk` and `SKIP_WALK` go. A document naming a file that exists only on this machine (untracked, not ignored) is now a finding, as it would be in any other checkout.
2. **Regenerable roots are absent by design.** A path at or under a `kgme.toml [clean.targets]` entry resolves whether or not it exists: those are, by definition, the places that are regenerated and may be emptied. Glob entries match as globs. The list is read from `kgme.toml`, never copied into code. `ABSENT_BY_DESIGN` stays for its three non-regenerable cases.
3. **`memory/attachments/.gitkeep`**, tracked, so Obsidian's attachments folder is part of every checkout's vault.
4. **Red command first:** `test_the_whole_tree_is_coherent` run against a fresh `git clone --no-hardlinks` of the repository in a temporary directory fails before the change and passes after. Plus fixture cases: a path under a clean target resolves with its root absent; an untracked file that exists does not resolve; a staged new file does.

## Outputs
`kgme/vault.py`, `kgme/coherence.py`, `tests/test_coherence.py`, `memory/attachments/.gitkeep`; where the coherence check is described (`README.md` or the reader that names it), one sentence, as a diff Michou approves if it is a reader.

## Acceptance test (under five minutes)
`make check` green in `brain/` and in a fresh clone; `kgme lint` in a fresh clone shows no `coherence-path` finding that the walk-based check did not; the design worktree's placeholders (`logs/trace/`, `logs/scratch/review.patch`) can be deleted and its `make check` stays green.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one reader function and one rule in the lint. `git revert`.

## Needs from Michou
Adoption. Order: after 0045 commits, before 0051 (0051 makes `atlas` a clean target and relies on rule 2).

## Report
`docs/audit/2026-10-DD-coherence-commit.md`, named in `report:` on closing. Commit `lint: coherence resolves against the commit; regenerable roots absent by design (HANDOFF-0054)`.
