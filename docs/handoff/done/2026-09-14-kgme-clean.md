---
id: HANDOFF-0033
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-14T00:32:07-07:00
report: docs/audit/2026-10-08-loop-0.md
depends_on: HANDOFF-0026
plan_ref: PLAN-PHASE-1 step 8
---

# Handoff 0033 (proposed) — `kgme clean`: the disposable-class deleter

## Why
STATUS records Cowork's recommendation, confirmed by all four reviewers and by Michou on 2026-09-14: bare `rm -rf` stays denied everywhere, and agents get a tool that can delete only inside the disposable class (ADR-012) with an explicit allowlist and a ledger event per deletion. It ships ahead of `kgme brief` because Loop 0's fourth test, reconstruction, is proven by deleting the artefact with this tool and regenerating it. Ships with 0034 as one pair.

## What
1. `kgme/clean.py`: `plan_clean(target) -> list[Path]` (pure, given a listing) and `execute_clean(plan) -> CleanResult` (effects). Named targets only, never arbitrary paths: `briefs` (`memory/agent/brief/`), `agent` (all of `memory/agent/`), `scratch` (`logs/scratch/`, including `payloads/`), `trace` (`logs/trace/`, the untracked read-only tool stream, ADR-019 §2), `caches` (`**/__pycache__`, `.ruff_cache`, `.pytest_cache`), `venv` (`.venv`), `ledger-test` (`logs/ledger-test/` and `logs/trace-test/`). Allowlist roots live in `kgme.toml` `[clean]`.
2. Every candidate is `resolve()`d and must satisfy `is_relative_to()` against its root and against `KGME_HOME`; symlinks are refused; any path containing `.git` is refused; `logs/ledger/` is refused unconditionally.
3. `--dry-run` is the default and prints the plan with sizes; `--yes` deletes, files first then empty directories bottom-up; one `intent` for the plan, one `outcome` per path with size and hash in the summary.
4. `kgme clean <anything not in the target list>` exits 2 with the list of targets.

## Outputs
`kgme/clean.py`, `jobs/clean/job.md` (already has its manifest from 0032), `tests/test_clean.py`.

## Acceptance test (under two minutes)
Dry run on a seeded `memory/agent/` lists exactly the seeded files and deletes none; `--yes` deletes them and writes one outcome per file; a symlink planted at `memory/agent/x` pointing at `docs/` is refused with a `blocking` outcome and `docs/` is untouched; `kgme clean docs/` is rejected as an unknown target; `kgme clean ledger` does not exist.

## Reviewer
Codex under `kgme review`.

## Reversibility
`git revert` of the code. Deleted disposable output is regenerable by design; nothing else is reachable.

## Needs from Michou
Confirmation that `venv` belongs in the named targets, since charter §6 lists deleting outside `memory/agent/` and quarantine among things never done unattended. `kgme clean` is never unattended in Phase 1 (nothing is scheduled), but the target list is a policy statement.

## Report
`docs/audit/2026-09-20-loop-0.md` under "HANDOFF-0033 — clean". Set `status: done`, `completed:`. Commit `jobs: kgme clean, allowlisted deleter (HANDOFF-0033)`.
