---
id: DEBT
type: note
status: active
created: 2026-11-23T13:30:00-08:00
modified: 2026-11-23T13:30:00-08:00
author: cowork
source: inferred
sources: [AUDIT-0176, HANDOFF-0075]
tier: 2
---

# Known gaps (DEBT)

What is unfinished or known to be wrong, in one place (after Rat Stack's `debt.md`). `docs/STATUS.md` says what to do next; this page says what is still broken or missing. Remove a line only when the fix lands, citing the commit.

## Engine
- **The loop doesn't say why a session ended.** It hit max_turns on 2026-11-20 and reported only "ended". It also keeps none of the child's stderr.
- **A loose builder can't `git add` from its sandbox**, so a loop run can't close a real handoff (2026-11-23). Linked to the paused queue: 0065, 0066, 0067.
- **Codex can't read its own login from a builder's sandbox.** Every review runs from Michou's terminal.
- **Review audit ids are taken from the main checkout only,** so they collide with reports written in a workspace (AUDIT-0176, 2026-11-23).
- **A `work` session run from a workspace fails its session-end hooks** (`session_end` and `kgme sync` exit 2, ten entries on 2026-11-23). It writes `logs/scratch/hook-errors.jsonl` in the workspace, which turns that workspace's `make check` red until the file is moved.
- **Test stubs can outlive their test** (`tests/fixtures/loop/builder_stub.py`), and tests write to the main checkout's `logs/ledger-test/`.
- **The guard doesn't refuse `--no-verify`, `git commit -n` or `core.hooksPath` changes.** That rule is only in prompts (HANDOFF-0075, proposed).
- **Roles:** `cheap` isn't a role level in v1; Bash can't be narrowed by subcommand; rubrics are declared but not scored (0046).
- **No shared task table with atomic claims** for teams (`kgme-agent-architect/references/orchestration.md`).

## Design track
- **Design landings are blocked since 2026-11-18:** the trial clone lacks the three.js asset in `logs/scratch/vendor/` (47 setup errors).

## Policy and setup
- **Egress control:** LuLu and host rules (0038) not installed. The cheap lane and design Codex have no host rule.
- **`docs/toolbox.md`:** the deepseek-v4.1-flash row has no licence. That's advisory now and blocking from schema 1.8.
- **Sleep policy (proposal 0012)** undecided. The unattended loop needs the Mac awake.
- **The Hermes fence is not an adversarial boundary** (0073, cycle-2 ruling). It stops accidental and casual writes; an unrestricted shell outside the repo can still reach in. The real fix is OS-level: Hermes sandboxed with the repo read-only, dispatching through a request queue that a KGME runner executes (the shared-store pattern in `kgme-agent-architect/references/orchestration.md`).
- **The Hermes fence can't protect files outside the repo that trusted programs read** (`~/.gitconfig`, `~/.claude/settings.json`, shell rc files, the uv-managed Python, `~/.hermes/config.yaml`). Only a separate macOS user closes that; it's evaluated with 0038's Tier 1 boundary.

- **Hermes Desktop is not fenced** (AUDIT-0180, 2026-11-24). Desktop-sourced tool calls (named `mcp__terminal`, `mcp__write_file`, …) never reach the `kgme-fence` shell hook: a command naming a brain path ran after a gateway restart, in a brain-rooted project, with the hook approved. KGME work runs in the CLI only. To fix: find the desktop tool path in Hermes (a plugin `pre_tool_call` hook may reach it where a shell hook does not); have the fence normalise an `mcp__` prefix and refuse unknown code-running tools.
