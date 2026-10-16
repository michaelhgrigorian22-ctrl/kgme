---
id: HANDOFF-0027
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-09-15T01:05:00-07:00
report: docs/audit/2026-09-15-permissions-and-hooks.md
depends_on: HANDOFF-0025
plan_ref: PLAN-PHASE-1 step 2
---

# Handoff 0027 (proposed) — Repo-scoped `.claude/settings.json`

## Why
AUDIT-0002 found the global Claude Code settings in `auto` mode with a twenty-entry allowlist and `skipAutoPermissionPrompt` on, and its `Read(./.env)` deny CWD-relative (finding C7). ADR-008 and ADR-013 §2 require a repo-scoped file in ask-mode with explicit allow and deny. This is the settings half of the original step 1; the hooks follow in 0028 once the ledger exists. Ships with 0028 as one commit pair.

## What
1. `.claude/settings.json` in the repo, committed. `permissions.defaultMode: "default"` (the documented ask-mode value).
2. Allow: `Bash(uv run *)`, `Bash(make check)`, `Bash(make canary-agents)`, `Bash(git status)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(ls *)`, `Read`, `Edit` and `Write` scoped to `kgme/**`, `tests/**`, `tools/**`, `jobs/**`, `cockpit/**`, `memory/agent/**`, `logs/**`, `docs/audit/**`, `docs/handoff/proposed/**`.
3. Deny: `Bash(rm -rf *)`, `Bash(rm -fr *)`, `Bash(rm -r *)`, `Bash(sudo *)`, `Bash(security *)`, `Bash(curl * | bash)`, `Bash(curl * | sh)`, `Bash(wget * | sh)`, `Bash(git push --force*)`, `Bash(git push -f*)`, `Read(**/.env)`, `Read(**/.env.*)`, `Read(~/.ssh/**)`, `Read(~/Library/Keychains/**)`, `Read(memory/private/**)`, and the Tier 1 path from `kgme.toml` once it exists. Everything else asks.
4. Verify on the installed Claude Code version, by test and not by assumption, that the project file's `defaultMode` overrides the global `auto` and `skipAutoPermissionPrompt`. If it does not, record that in the report and propose the global change as a separate handoff; do not edit the global file here.

## Outputs
`.claude/settings.json`; a "verified on version X" line in the report.

## Acceptance test (under five minutes, one session)
In a fresh Claude Code session in the repo: `Read` of a planted temp `.env` is refused; `Bash(git push --force)` is refused; `Bash(uv run kgme --help)` runs without a prompt; `Bash(echo hi)` prompts. The refusal survives the global `auto` mode.

## Reviewer
Michou runs the session by hand; Codex reviews the file under the loop.

## Reversibility
Delete `.claude/settings.json`; the global settings apply again.

## Needs from Michou
The five-minute live session. Confirmation of the Tier 1 path string to deny (the path only, never the contents).

## Report
`docs/audit/2026-09-16-permissions-and-hooks.md`: the file, the version verified, the session transcript excerpt. Set `status: done`, `completed:`. Commit `policy: repo-scoped permissions (HANDOFF-0027)`.
