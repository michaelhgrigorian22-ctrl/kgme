---
id: HANDOFF-0047
type: handoff
created: 2026-10-16T00:35:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0045]
plan_ref: PLAN-PHASE-1 step 7d
---

# Handoff 0047 — Session levels: the launcher, three settings files, the ledger pinned to the main checkout

## Why
ADR-022 (proposed) makes a session's allowance a named level started by one command and recorded in the ledger. This handoff builds the levels that need no orchestration (`tight`, `work`, and the `loose` permission set) and the two prerequisites every worktree-based mode needs: one ledger regardless of checkout, and appends that stay whole when several sessions write at once. `crew` is HANDOFF-0048.

## What
1. **Settings files**, one per level, in a `sessions` folder under `control/policy/` (human paths since HANDOFF-0045: each arrives as a diff Michou applies), each a plain JSON file the launcher passes with `--settings`:
   - `tight.json`: `permissions.disableAutoMode` and `permissions.disableBypassPermissionsMode` `"disable"`; no allow rules; the project deny list applies as always.
   - `work.json`: `sandbox.enabled` true, `sandbox.allowUnsandboxedCommands` false, `sandbox.failIfUnavailable` true, `sandbox.filesystem.allowWrite` the repository root and the temp directory; `permissions.disableBypassPermissionsMode` `"disable"`.
   - `loose.json`: as `work`, plus `sandbox.filesystem.allowWrite` replaced at launch by the task's `Outputs`, `tests/` and `logs/scratch/` (the launcher writes a per-run copy under `logs/scratch/sessions/<run>/` and hashes that); a pinned `permissions.allow` list (Read, Grep, Glob, Edit on the `Outputs` paths, `Bash(make check)`, `Bash(uv run --frozen pytest *)`, `Bash(git add *)`, `Bash(git commit *)`, `Bash(git diff *)`, `Bash(git status *)`); no network domains.
2. **`kgme session <level> [--handoff ID] [-- extra claude args]`** in `kgme/session.py` and `kgme/cli.py`. It builds `claude --setting-sources project,local --settings <file> --permission-mode <plan|auto|dontAsk>` (plus `-p`, `--permission-prompts none`, `--max-turns`, `--max-budget-usd` for `loose`, values from `kgme.toml [sessions]`) with `--model` from `kgme.toml [models]`, appends one `note` (`job: session`, payload: level, settings sha256, the full argv, `claude --version`, model id) and `exec`s. A shell function `kgs` mirrors `kgh`.
3. **One ledger whatever the checkout.** The ledger and trace directories resolve from `git rev-parse --path-format=absolute --git-common-dir` (the main checkout's `.git`, whose parent is the main checkout), never from the running copy's package location or `CLAUDE_PROJECT_DIR`. A session in any worktree of this repository appends to the main checkout's `logs/ledger/`. Outside a git repository the resolution fails closed (the hook exits 2), as the guard does today.
4. **Concurrent appenders.** A test starts 8 processes appending 500 events each through `kgme/ledger.py`; every line parses, the count is exactly 4,000, ids are unique, and no line is split. If the single-writer lock of HANDOFF-0040 is not already what serialises appends, it becomes so.
5. **Canary cells, one set per level** (agent tier, `make canary-agents`), each a ledger event labelled by layer: `tight` refuses an Edit; `work` refuses `Bash(touch ~/kgme-canary)` at the sandbox layer and an unlisted host at the network layer; `loose` refuses an Edit outside the toy `Outputs`, a Bash write outside them, any network call, and `WebFetch`; each level's start `note` carries the settings sha.

## Outputs
`control/policy/sessions/{tight,work,loose}.json`, `kgme/session.py`, `kgme/cli.py`, `kgme/paths.py` (ledger root), `kgme/ledger.py` (lock, if needed), `kgme.toml` (`[sessions]` caps, as a diff for Michou), `tests/test_session.py`, `tests/test_ledger_concurrency.py`, `tests/test_paths_worktree.py` (a temporary worktree writes to the main ledger), canary rows, a section in `docs/readers/` named by Michou (proposed: `docs/readers/sessions.md`, as a diff).

## Acceptance test (under fifteen minutes)
`kgme session tight` opens in plan mode and the start note names the level and sha; an edit is refused. `kgme session work` from a temporary worktree writes its hook events into the main checkout's ledger and none into the worktree's. The concurrency test passes. `make canary-agents` shows every new cell with its layer.

## Reviewer
Codex read-only under `kgme review`. Two-cycle rule and red command first apply.

## Reversibility
Door: two-way. Blast radius: one new command, three settings files, the ledger's path resolution. `git revert`; plain `claude` never changed.

## Needs from Michou
Adoption with ADR-022. The `[sessions]` caps for `loose` (proposed: 60 turns, 15 USD per run). Whether `kgs work` replaces plain `claude` as his daily launch (recommended once the canary cells pass).

## Report
`docs/audit/2026-10-DD-session-levels.md`. Set `status: done`, `completed:`. Commit `session: levels as launcher lines, one ledger per repository (HANDOFF-0047)`.
