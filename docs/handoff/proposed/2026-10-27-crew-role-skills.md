---
id: HANDOFF-0064
type: handoff
created: 2026-10-27T23:40:00-07:00
from: claude-code
to: michou
status: proposed
tier: 2
depends_on: [HANDOFF-0048]
---

# Proposal 0064: the crew's role skills and agent files, for Michou to apply

## Why
HANDOFF-0048 §7 and amendment 10: the planner, builder and integrator roles are skills under `skills/`, and the agent files only load them; both are human paths Michou applies. Cowork was to draft them; the builder of 0048 drafted them on 2026-10-27 so the crew's first run has a planner to carry. A draft under `docs/handoff/proposed/agents/` with skill frontmatter fails `kgme lint` (every `.md` under `docs/` is a note), so the six files sit under `logs/scratch/handoff-0048/skills/` with a `README.md` that applies them, and this note is their record.

## What
Six files, verbatim under `logs/scratch/handoff-0048/skills/`:
- `kgme-planner-SKILL.md` → `skills/kgme-planner/SKILL.md`: the plan format the gate parses, the rules the gate enforces, how to split along seams, how to answer a refusal or a finding with `## Dispositions`.
- `kgme-builder-SKILL.md` → `skills/kgme-builder/SKILL.md`: the route of amendment 2 from a workspace: red first, build inside the Outputs, gate, `kgme review --handoff <handoff>:<task>` through the main checkout's code, one commit by pathspec on PASS, and the never-list.
- `kgme-integrator-SKILL.md` → `skills/kgme-integrator/SKILL.md`: the reader of a crew run's record and the one approval screen; never merges.
- `kgme-planner-agent.md`, `kgme-builder-agent.md`, `kgme-integrator-agent.md` → `.claude/agents/kgme-<role>.md`: `model: inherit`, load the skill, nothing else.

## How to apply
The README's loop copies each skill into `skills/kgme-<role>/SKILL.md` with an empty `lessons.md` beside it and each agent file into `.claude/agents/`; then `uv run --frozen kgme skills install` (Michou's command) links the skills where every harness reads them and records the state of `~/.claude/skills/` as measured.

## Needs from Michou
Adoption, or edits to the drafts first; the six files are his to change.
