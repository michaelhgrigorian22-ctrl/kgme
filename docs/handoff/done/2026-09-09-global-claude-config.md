---
id: HANDOFF-0004
type: handoff
created: 2026-09-09T20:05:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-09T20:21:00-07:00
report: docs/audit/2026-09-09-global-claude-config.md
tier: 2
depends_on: HANDOFF-0001
---

# Handoff 0004 — Reconcile the global Claude Code configuration (read-only)

The audit found a global `~/.claude/CLAUDE.md` (45 lines), hooks and permissions in `~/.claude/settings.json`, three agents, one command, one skill, and a stray `~/AGENTS.md`. All of these silently apply inside this repository. Before anything is built here, we need to know what they say. **Read-only; nothing is changed.**

## Collect and summarise (no secrets; redact anything token-like)
1. `~/.claude/CLAUDE.md` — quote it in full in the report (it is instructions, not a secret), then list every rule in it that could conflict with, duplicate, or override the repo `CLAUDE.md`. Be specific: which line, which rule here.
2. `~/.claude/settings.json` — for `hooks`: each event name and the command it runs (redact any string that looks like a key or token). For `permissions`: the allow / deny / ask lists as they are. Any other key: name only.
3. `~/.claude/agents/*.md` (`data-fetcher`, `model-auditor`, `report-writer`), `~/.claude/commands/distill.md`, `~/.claude/skills/grill-me/SKILL.md` — for each: one-paragraph summary of what it does, which tools it may use, and whether it could be triggered inside this repo.
4. `~/AGENTS.md` at `$HOME` — summarise it; state whether Codex (once installed) would read it for projects under `~/Projects`.
5. `~/.claude/projects/` — list the subdirectory names only (they are per-project state), and say whether one already exists for `~/Projects/Automate`.

## Report
Write `docs/audit/2026-09-09-global-claude-config.md` with frontmatter `id: AUDIT-0002`, `type: report`, `status: final`, `handoff: HANDOFF-0004`, `author: claude-code`, `source: fetched`, `tier: 2`, `created:` (ISO 8601 with offset). Sections 1–5 as above, then **"Conflicts and recommendations"**: for each conflict, the two options — keep the global rule (and say why it is compatible), or propose moving it into this repo's `CLAUDE.md` or removing it. Recommend; do not change anything.

Finish by setting this handoff `status: done` with `completed:`. Tell Michou in three sentences: the most important thing the global file says, whether any hook runs on every tool call, and whether anything conflicts with the repo constitution.
