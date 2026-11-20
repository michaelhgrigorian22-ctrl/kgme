---
id: READER-ROLES
type: note
status: active
created: 2026-11-18T00:00:00-08:00
modified: 2026-11-18T00:00:00-08:00
author: claude-code
source: inferred
sources: ["ADR-025", "HANDOFF-0071", "kgme/roles.py", "kgme/roles_io.py", "kgme/roles_run.py"]
tier: 2
---

# Reader: roles and departments

*Written 2026-11-18 by Claude Code for HANDOFF-0071. The decision is ADR-025.*

## What it is
An agent is one file, `roles/<department>/<role>.toml`, with its rubric at `roles/<department>/rubrics/<role>.md`. A role names a session level (`control/policy/sessions/`) and optionally a profile (`control/policy/profiles/`), and may narrow them but never widen them. It grants nothing, so `roles/` is not a human path: any agent may draft a role, and `kgme lint` is the fence.

## The fields
| Field | What it holds |
|---|---|
| `id` | `<department>.<role>`, matching the path |
| `department`, `purpose`, `kind` | the folder; one line; `manager` (one per department) or `worker` |
| `skill` | a folder under `skills/` holding a `SKILL.md` |
| `model` | `standard`, `strong` or `inherit`; `cheap` is refused, being the cheap lane's (AUDIT-0173 F3) |
| `level`, `profile` | `tight`, `work` or `loose` (`cheap` is not a role level in v1); an optional profile |
| `slice`, `tools` | `kgme atlas --around` targets; tool names within the level |
| `tier_max`, `escalates_to` | 2 or 3, never more sensitive than the level reaches; a role id or `michou` |
| `rubric` | three to six dimensions, at least one a gate, with the standing `intent` and `context` gates |

What a level allows: `tight`, `kgme.toml [hooks] read_only_tools`; `work`, the `claude-builder` profile's `tools`, or the role's own profile's; `loose`, the tool names of its template's `permissions.allow`, minus `deny`. Ceilings: 2 for `tight`, `work` and `loose`. `tier_max = 1` is always refused (ADR-021).

## Commands
- `kgme agent list`: the roles by department, with a count each.
- `kgme agent show <id>`: the file, what its level allows, the model it resolves to, its chain.
- `kgme agent new <department> <role>`: a lint-clean role, rubric and stub skill (`skills/kgme-<department>-<role>/`), never over an existing file; it prints what is still missing.
- `kgme agent run <id> "<task>"`: the role's level as `kgme session` builds it, with the role's model, its skill and atlas slice in a system-prompt file, the task as the prompt. `--print` runs headless and is `tight`'s only. `--handoff` passes a handoff to a `loose` role. The launch is narrowed to the role's `tools`: `--tools` names them as the only built-in tools, and the run copy of the level's settings denies every other tool; a scoped rule, or a profile's path or network fences other than `claude-builder`'s at `work`, is refused by name. A role that fails lint never runs.

## In the ledger
Each run writes an `agent:run` intent before the launch and an outcome after it, both keyed `agent:<id>` and sharing the run id of the session note, whose payload carries `role`. The session's own hook events nest under the intent through `KGME_LOOP_PARENT`. To follow one role: `kgme ledger read --stream ledger | grep '"agent:build.integrator"'`, then the run id.

## The org chart
`kgme atlas` draws each role (kind `role`) linked to the role it escalates to or to `michou` (kind `head`) and to its skill, and each department (kind `department`) linked to its roles.

## Declared
Build: `build.planner` (manager, `tight`), `build.builder` (`loose`), `build.integrator` (`tight`). Audit: `audit.auditor` (`tight`, answers to Michou; its skill is a stub until HANDOFF-0046).
