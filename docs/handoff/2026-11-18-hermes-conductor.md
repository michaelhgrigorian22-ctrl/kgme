---
id: HANDOFF-0073
type: handoff
created: 2026-11-18T00:30:00-08:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0071, HANDOFF-0045, HANDOFF-0047]
---

# Proposal 0073 — Hermes as the conductor: it talks and dispatches, the repo is touched only through `kgme`

## Why
- **Michou, 2026-11-18.** Hermes Agent (Nous Research) is now where he talks to Opus 5.5, and it can start loops in its own terminal. It bills through his Claude login (`billing_provider = anthropic`, the Keychain item `Claude Code-credentials`), not through Nous.
- **The gap.** KGME's guard, ledger hooks, sandbox and session levels are Claude Code mechanisms (ADR-022, HANDOFF-0028, HANDOFF-0045). Hermes's own terminal and file tools fire none of them. A Hermes edit or a git command in the repo would skip the human paths and leave no record.
- **The aim.** Make Hermes Blaw's one orchestrator you talk to, under ADR-025 §1. It plans, dispatches and reports. Every change to the repo goes through a `kgme` command, which launches Claude Code under the full rules.

## What
1. **Measure first.** Read Hermes's installed version and config (`~/.hermes/config.yaml`, its command-approval and tool settings, `terminal.backend`) and report what it can enforce:
   - Can it allow terminal commands by pattern?
   - Can it disable its file-write tools for a folder?
   - Can its terminal run as a different user or in a container?
   
   Cite the source line for each answer. Nothing below is built on a guess about Hermes.
2. **Fence Hermes.** Configure Hermes so that, inside `~/Projects/KGME/`:
   - its terminal runs only `kgme …`, read-only git (`status`, `log`, `diff`, `show`) and read-only views (`ls`, `cat`, `grep`, `rg`)
   - its file write and edit tools are off
   
   If Hermes cannot enforce this, say so, and propose the strongest fallback it does support (its Docker terminal backend with the repo mounted read-only, or a separate macOS user under the Tier 1 evaluation of HANDOFF-0038). Don't build the fallback before Michou rules.
3. **Attribute its runs.** Hermes's terminal sets `KGME_CONDUCTOR=hermes`. `kgme` records it on the `session`, `loop`, `crew` and `agent:run` events it writes, so the ledger shows which runs Hermes started.
4. **Give it a role and a skill.**
   - Under the registry from 0071, `conductor.hermes`: kind `manager`, escalates to `michou`.
   - The skill `skills/kgme-conductor/SKILL.md`: read `docs/STATUS.md` and the ledger, dispatch only through `kgme loop`, `kgme crew`, `kgme session` and `kgme agent run`, never edit, report in plain words, ask Michou only under ADR-023's threshold.
   - Link the skill wherever Hermes reads skills.
5. **Providers.** `kgme.toml [providers]` gains `nous = "none"`: no KGME content goes through Nous Portal until Michou rules otherwise. Hermes runs KGME work on the `anthropic` provider only.
6. **Toolbox row** for Hermes Agent as an installed harness (ADR-020 §2), with its version.

## Rulings at adoption (Michou, 2026-11-18)
- **Nous stays out.** `kgme.toml [providers]` gets `nous = "none"`. No KGME content goes through Nous Portal, and Hermes runs KGME work on the `anthropic` provider only.
- **Order.** §1, the read-only measurement, may run now in a `tight` session alongside 0071's build. §§2–6 start only after 0071 passes, in a fresh `work` session.

## Outputs
`kgme/` attribution (the event writers), the role under `roles/conductor/`, `skills/kgme-conductor/`, canary cells under `tests/`, the measurement report under `docs/audit/`.

Human paths, delivered as diffs for Michou to apply: `kgme.toml [providers]`, the toolbox row, and the Hermes config changes (in his home folder, outside the repo).

## Acceptance test (under five minutes)
From a Hermes session in the repo:
1. Asking Hermes to edit `kgme/cli.py` directly is refused.
2. `git commit` is refused.
3. Writing to `control/` is refused.
4. `kgme agent run build.integrator "summarise the last crew run"` runs, and its ledger events carry `conductor: hermes`.
5. `kgme lint` passes on the new role.

## Reviewer
Codex through `kgme review`. Rulings go to the arbiter pair under ADR-023.

## Reversibility
Remove the role, the skill and the attribution field in one revert, and restore Hermes's config from the copy the builder saves before changing it.

## Needs from Michou
- Adopt after 0071 passes.
- Rule on Nous: the recommendation is `none`, since Opus already runs on the `anthropic` provider and Nous adds nothing KGME needs.
- If the measurement shows Hermes can't fence its own tools, choose between the Docker backend and a separate macOS user.
