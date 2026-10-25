---
id: HANDOFF-0042
type: handoff
created: 2026-10-09T22:55:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-25T16:00:18-07:00
report: docs/audit/2026-10-25-design-track-registration.md
depends_on: [HANDOFF-0034, HANDOFF-0041, HANDOFF-0054, HANDOFF-0055]
plan_ref: PLAN-PHASE-1 step 9b
---

# Handoff 0042 — Register the design track: its ids, its folders, a Codex builder profile

*Proposed by Cowork 2026-10-09; amended by Cowork at adoption, 2026-10-25T14:01:00-07:00. Two of the four original items were built since: lint validates the commit's files (HANDOFF-0054), and the design track's binaries live under `logs/scratch/design-review/`, as the design readers say. The design branch has merged (HANDOFF-0055), so its folders now meet the validator on `main`; the track is admitted today by the README exemption and the id families of schema v1.4, not by any registration.*

## Why
The design track has its own handoff sequence (`CDH-NNNN`), its own audit sequence (`AUDIT-CDH-NNNN`), its own folders, and a builder (Codex, since 2026-10-16) with no hook layer. None of that is declared anywhere the validator or the canary matrix reads: any subfolder under `docs/handoff/` or `docs/audit/` is accepted, a CDH file could carry a HANDOFF id, and Codex builds under a sandbox nobody has written down or measured. `kgme.toml [tracks.design]` (HANDOFF-0055) is the natural home: one table that says what the track is, where it may write, and what prefixes its records carry.

## What
1. **Track registration, schema v1.6.** `kgme.toml [tracks.design]` gains, beside `lanes`: `handoff = "CDH"`, `audit = "AUDIT-CDH"`, `handoff_folder = "docs/handoff/cockpit-design/"`, `audit_folder = "docs/audit/cockpit-design/"` (a diff Michou applies). The validator: a `type: handoff` under a registered handoff folder, or a `type: report` under a registered audit folder, must carry that track's prefix, else `blocking`; a subfolder of `docs/handoff/` or `docs/audit/` that is not `done/`, `proposed/`, `archive/` or a registered track folder is `blocking`; one `README.md` per track folder stays exempt as today. `docs/schema-v1.md` gains the rule and a 1.6 changelog line (Cowork's diff; the schema stays draft). The current track files must pass unchanged.
2. **`kgme lint --all`.** The default stays the commit's files (HANDOFF-0054). `--all` also walks the working tree, and the default summary line counts the untracked files it skipped ("N untracked skipped; `--all` walks them").
3. **Codex builder profile.** `control/policy/profiles/codex-builder.toml` (a human path: a diff Michou applies), beside `codex-reviewer.toml`: the sandbox Codex builds under (`-s workspace-write`), write roots exactly the track's lanes plus `logs/scratch/`, read from the lanes (manifests resolved from `kgme.toml`, so the two cannot drift), never `memory/`, `kgme/`, `control/`, `.claude/`, `CLAUDE.md` or the ADRs; network only the two OpenAI hosts the reviewer profile names. The fast tier of the canary matrix gains its rows (the manifest test), and the agent tier gains two cells: Codex, built under that profile, asked to write outside the lanes (refused at the sandbox layer) and to open an unlisted host (refused). Cells pass only on an observed call, naming the layer that refused (the lesson of HANDOFF-0053).
4. **Record the rule.** One paragraph in `docs/readers/cockpit-design.md` on what the registration means for the track (Cowork applies it); the design track's README is the design session's.

## Outputs
`kgme/lint.py`, `kgme/vault.py`, `kgme/cli.py` (`--all`), `kgme.toml` (`[tracks.design]`, as a diff), `control/policy/profiles/codex-builder.toml` (as a diff), `tests/policy/test_manifest.py`, `tests/policy/test_agents_codex_builder.py`, `tests/test_lint.py`, `docs/schema-v1.md` (v1.6, Cowork's diff), `docs/readers/cockpit-design.md` (Cowork's paragraph).

## Acceptance test (under five minutes, plus the two agent cells)
On `main` with the diffs applied, `make check` is green and every current file under the two track folders lints with zero blocking findings. A planted, staged handoff file in an unregistered subfolder of the handoff folder is blocking; a planted file in the cockpit-design handoff folder whose id carries the HANDOFF prefix is blocking (wrong prefix). With an untracked file carrying no frontmatter planted under `docs/`, `make check` is green and the summary counts one untracked file skipped; `kgme lint --all` reports it as blocking. The codex-builder rows pass in the fast tier; both agent cells pass with a call observed.

## Reviewer
Codex read-only under `kgme review`. Codex reviewing its own future profile is a known limit: the arbiter rules on any finding about item 3.

## Reversibility
Door: two-way. Blast radius: four `kgme.toml` keys, one profile, validator rules that only add findings. Removing the keys returns the validator to today's behaviour.

## Needs from Michou
Adoption. Applying the `kgme.toml` and profile diffs. Repointing `kgq`'s Codex start at the new profile is his, after the design session reads it.

## Report
`docs/audit/2026-10-DD-design-track-registration.md`, named in `report:` on closing. Commit `lint: the design track registered, its ids and folders checked, a Codex builder profile (HANDOFF-0042)`.
