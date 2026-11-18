---
id: HANDOFF-0071
type: handoff
created: 2026-11-17T23:45:00-08:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0045, HANDOFF-0047, HANDOFF-0048, HANDOFF-0056]
---

# Proposal 0071 — The role registry: an agent is one file

## Why
ADR-025 §2–4. Today an agent costs a handoff and Michou's application, so KGME has three. After this, an agent is one declared, linted file that grants nothing its session level does not, and every run of it is attributable in the ledger.

## What
1. **The role file:** `roles/<department>/<role>.toml`. Fields:
   - `id` (`<department>.<role>`), `department`, `purpose` (one line), `kind` (`manager` or `worker`)
   - `skill` (a folder under `skills/`)
   - `model` (`cheap`, `standard`, `strong` or `inherit`)
   - `level` (`tight`, `work`, `loose` or `cheap`) and an optional `profile` (a file under `control/policy/profiles/`)
   - `slice` (atlas `--around` targets) and `tools`
   - `tier_max` and `escalates_to` (a role id or `michou`)
   - `rubric` (`roles/<department>/rubrics/<role>.md`)
2. **`kgme lint` checks every role.** All of these are blocking:
   - every field is present and the skill exists
   - the level and the profile exist
   - `tools` is a subset of what the level allows
   - `tier_max` does not exceed the level's ceiling, and a role can never reach Tier 1
   - `escalates_to` resolves, and the chain reaches `michou` in at most three hops with no cycle
   - the rubric exists, has three to six dimensions, at least one is marked `gate`, and it carries the standing `intent` and `context` gates
3. **`kgme agent`:**
   - `list`, `show <id>`
   - `new <department> <role>` writes a lint-clean role and rubric from a template and prints what is still missing (the skill body)
   - `run <id> "<task>"` starts `kgme session <level>` with the role's model, its skill and its atlas slice, and writes `agent:run` intent and outcome events carrying the role id, so every trace in the ledger names its role
4. **Declared now.**
   - Build: `build.planner` (the manager), `build.builder` and `build.integrator`, pointing at the existing crew skills. Any of 0064's skills not yet applied is applied first. `.claude/agents/kgme-*.md` stay as they are.
   - Audit: `audit.auditor`, its skill a stub (scoring is 0046, later).
5. **The atlas** draws roles as nodes, `escalates_to` as edges and departments as groups.
6. **`roles/` is registered** wherever the coherence check and `kgme lint --all` need it. It is not a human path (ADR-025 §3).

## Outputs
- `roles/**`, `kgme/roles.py` and its CLI wiring, `kgme/lint.py` (the call into the role pass), the atlas branch in `kgme/atlas.py`, `tests/test_roles.py`, the role and rubric templates.
- Human paths, delivered as diffs for Michou to apply: the `roles/` line in `CLAUDE.md`'s folder map, and the reader `docs/readers/roles.md`.

## Rulings at adoption (Cowork, 2026-11-17, on Claude Code's pre-code statements)
- **Allowed tools are derived, as Claude Code proposed:** `loose` and `cheap` from their session JSON's `permissions.allow` (minus `deny` for `cheap`); `work` from `claude-builder.toml` or the role's own profile; `tight` from `kgme.toml [hooks].read_only_tools`. Its call on `tight` stands: plan mode is read-only.
- **Tier ceilings are 2 for `tight`, `work` and `loose`, and 3 for `cheap`**, because the cheap lane's code export never holds `memory/` or `logs/`. Its call stands. Lint requires `tier_max >= ceiling` numerically (never more sensitive than the level reaches) and refuses `tier_max = 1` outright.
- **The role pass is separate from the note schema.** `roles/` is not added to `[lint].roots`. `kgme/roles.py` holds the pass, and `kgme lint` calls it: index by default, working tree under `--all`.
- **`roles/` is not added to `[hooks].human_paths`** (ADR-025 §3).

## Acceptance test (under five minutes)
1. `kgme agent new finance analyst` writes a role and rubric that pass lint.
2. Widening that role's `tools` past its level fails lint as blocking, and so does `tier_max = 1`.
3. `kgme agent list` shows Build (3), Audit (1) and Finance (1).
4. `kgme agent run build.integrator "summarise the last crew run"` starts a session whose ledger events carry the role id.
5. The atlas shows the org chart.

## Reviewer
Codex through `kgme review`. Rulings go to the arbiter pair under ADR-023.

## Reversibility
Remove `roles/`, `kgme/roles.py` and the atlas and lint additions in one revert. Nothing that exists today reads them.

## Needs from Michou
- Accept ADR-025.
- Adopt this handoff ahead of the 0065, 0067 and 0066 queue. That queue has not moved since the loop's first real run on 0065 stopped on 2026-10-30: AUDIT-0169 returned BLOCK with F1 and F2 open, then a write was refused and the loop ended in error. The three stay adopted and resume after 0071.
- Run 0071 in an interactive `work` session reviewed with `kgme review`, not under `kgme loop`, because the loop's first real queue has not yet run clean.

## Report
`docs/audit/` per the usual route, with the acceptance test's commands and output.
