---
id: HANDOFF-0042
type: handoff
created: 2026-10-09T22:55:00-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0034, HANDOFF-0041]
plan_ref: PLAN-PHASE-1 step 9b
---

# Handoff 0042 (proposed) — Register the design track: lint scope, track folders, a Codex builder profile

## Why
On 2026-10-09 the cockpit design track (HANDOFF-0036, run in its own Cowork session with Codex as a second builder) created, at Michou's request, its own handoff series `CDH-NNNN` under `docs/handoff/cockpit-design/`, its own reports under `docs/audit/cockpit-design/`, and about 6 MB of review PNGs under `memory/attachments/`. None of it is committed. Two things followed. `kgme lint` walks the whole working tree, so the design track's untracked files turned `make check` red for everyone, and the substantive track ran review cycles 5 and 6 of HANDOFF-0040 (a lock redesign, of all things) with `--skip-check` (AUDIT-0040, AUDIT-0041). And Codex wrote files and ran headless Chrome on the machine under no profile: `control/policy/profiles/` knows a `codex-reviewer` (read-only) and nothing else, so ADR-013 §3 had no cell to show for it.

Two tracks sharing one gate is fine. One track being able to redden the other's gate with uncommitted work is not. And a builder without a profile is the gap 0032 was written to close.

This is substrate work (the validator, the schema, the policy layer), not design work, and it is not urgent: the immediate separation is a second working tree for the design track (`git worktree add -b design ../Automate-design`, Michou, 2026-10-09), which takes the design track's files out of the tree `make check` walks. This handoff comes after HANDOFF-0034 (Loop 0) and before the design branch merges to `main`, since the merge is when its files meet the validator.

## What
1. **Lint scope follows git.** `kgme lint` with no `--root` validates the files git knows: tracked, plus staged. Untracked files are skipped and counted in the summary line ("N untracked skipped; `--all` walks them"). `--all` restores the whole-tree walk. `make check` uses the default. A track's unfinished work can no longer fail another track's gate; a track must pass lint before it stages, which is when it matters.
2. **Track folders, schema v1.5.** `kgme.toml [tracks]` registers a track: `cockpit-design = { handoff = "CDH", audit = "AUDIT-CDH", folder = "cockpit-design" }`. The validator admits `type: handoff` under `docs/handoff/<folder>/` and `type: report` under `docs/audit/<folder>/` for a registered track, requires their ids to carry the registered prefix, and admits one `type: note` per track folder as its index (id `INDEX-*`). Everything else about those files is validated as usual. `docs/schema-v1.md` gains the rule and a 1.5 changelog line (Cowork's diff, shown; the schema stays draft). Unregistered subfolders stay blocking.
3. **Codex builder profile.** `control/policy/profiles/codex-builder.toml`, declaring the sandbox Codex runs under when it builds (`-s workspace-write`), write roots limited to `docs/design/`, `docs/handoff/cockpit-design/`, `docs/audit/cockpit-design/`, `logs/scratch/`, never `memory/`, `kgme/`, `cockpit/`, `.claude/`, `CLAUDE.md`, or the ADRs; no network. The fast tier of the canary matrix gains the profile's rows (every probe refused; a write to `memory/attachments/` refused; a write to `docs/design/` allowed). Until this profile exists, Codex on the design track reviews only, and Cowork writes.
4. **Binaries out of the tree.** Agent review captures go to `logs/scratch/design-review/` (already gitignored under `logs/scratch/`); the design readers say so. Small PNG exports Michou makes himself may live under `docs/design/cockpit-v0/review/`, each under 300 KB. `memory/attachments/` is the vault's, written by Michou only (ADR-004). The two reference images and the eight captures now under `memory/attachments/cockpit/` move to scratch; a third-party reference image is never committed.

## Outputs
`kgme/lint.py`, `kgme/vault.py` (git-known file list, `--all`), `kgme/cli.py` (`--all`), `kgme.toml [tracks]`, `control/policy/profiles/codex-builder.toml`, `tests/policy/test_manifest.py` (profile rows), `tests/test_lint.py` (scope and track cases), `docs/schema-v1.md` (v1.5, approved diff), `docs/readers/cockpit-design.md` and `-chatgpt.md` (the two sentences about where images go; Cowork's), the move of `memory/attachments/cockpit/` to `logs/scratch/design-review/` (a `git mv` is not needed; the files were never tracked).

## Acceptance test (under two minutes)
With an untracked file carrying no frontmatter planted under `docs/`, `make check` is green and the summary names one untracked file skipped; `kgme lint --all` reports it as blocking. The current `docs/handoff/cockpit-design/` and `docs/audit/cockpit-design/` files, staged, lint with zero blocking findings. A planted `docs/handoff/other/x.md` with `type: handoff` and id `OTH-0001`, staged, is blocking (unregistered track). The codex-builder rows pass in the fast tier. No `--skip-check` was needed for this handoff's own review.

## Reviewer
Codex under `kgme review`, as the reviewer, read-only.

## Reversibility
`git revert`; the schema returns to 1.4.

## Needs from Michou
Adoption. Approval of the schema diff. A word on item 4 if he wants the reference images kept somewhere tracked (then `docs/design/cockpit-v0/reference/`, originals only, never a third-party image).

## Report
`docs/audit/2026-10-DD-design-track-registration.md`. Set `status: done`, `completed:`. Commit `lint: scope follows git, track folders, codex builder profile (HANDOFF-0042)`.
