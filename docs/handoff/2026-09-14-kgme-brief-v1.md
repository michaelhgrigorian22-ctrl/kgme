---
id: HANDOFF-0034
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0026, HANDOFF-0031, HANDOFF-0033]
plan_ref: PLAN-PHASE-1 step 9
---

# Handoff 0034 (proposed) — Loop 0: `kgme brief` v1, model-free

## Why
The first loop that works end to end: manual, read-only against canonical inputs, local, no model call (Michou's ruling 2026-09-14, all four reviewers). It exercises the ledger's intent/outcome pair, the validator, the manifest, and `kgme clean`, and produces the artefact the cockpit will show. v2 adds a model for prose only after a week of hand runs.

## What
1. `jobs/brief/job.md` (purpose, inputs, outputs, side effects), `jobs/brief/run.py` (thin: argument parsing, `intent`, call into `kgme/brief.py`, `outcome`), `kgme/brief.py` (`build_brief(inputs, date) -> str`, pure) and `kgme/brief_io.py` (effects: `read_inputs`, `write_brief`).
2. Inputs: notes under `memory/notes/` and `memory/agent/` with `type: reminder, status: open`; `type: task, status in {open, doing}`; `memory/daily/<today>.md` if present; `memory/inbox/friction-log.md`. Machine briefs are excluded so the job never reads its own output. Every input is validated with `kgme/lint.py` first; a `blocking` finding on an input is a `blocking` outcome for the run.
3. Output `memory/agent/brief/YYYY-MM-DD.md`: frontmatter `type: note, status: active, tier: 2, author: kgme, source: inferred, sources: [every input id]`; `id` and `created` preserved on replacement, `modified` updated. Body: `# Brief YYYY-MM-DD`, `## Due and overdue`, `## Today`, `## Open tasks`, `## Friction since last brief`, `## Inputs` (id, path, sha256 of each). Deterministic sort by due, then priority, then id. Missing daily note and empty sections are stated, never silently omitted.
4. Transaction: `key: brief:<date>`; `intent` before any write; write to a temp file in the same directory, `fsync`, `os.replace`; `outcome` after. On start, `open_intents("brief")` is reconciled by hashing the destination against the intended hash recorded in the intent's payload.
5. `--dry-run` prints the body to stdout, writes no file, appends a single `note` event.
6. Templates shipped so the vault can be seeded: `memory/templates/reminder.md`, `task.md`, `daily.md`, each schema-valid once the Obsidian placeholders are filled.

## Outputs
`jobs/brief/{job.md,run.py}`, `kgme/brief.py`, `kgme/brief_io.py`, `memory/templates/{reminder,task,daily}.md`, `tests/test_brief.py`, `kgme brief` wired in `cli.py`.

## Acceptance test (under five minutes; the four ADR-015 job tests, each carrying an ADR-016 class, plus dry run)
Run twice on a seeded test vault: one artefact, identical `id` and `created`. `SIGKILL` after the intent: the next run reports and reconciles the orphan intent. A planted forbidden file in an input path: refused, `blocking` outcome logged, no artefact written. Delete the artefact with `kgme clean briefs --yes` and regenerate it byte-identical from ledger plus `memory/`. `--dry-run` writes no file and exactly one `note` event.

## Reviewer
Codex under `kgme review`. Michou reads the first real brief.

## Reversibility
`git revert`; `kgme clean briefs` removes every artefact.

## Needs from Michou
Seeding the vault (HANDOFF-0035) so the brief has something to say. A ruling on the section names if he wants different ones.

## Report
`docs/audit/2026-09-20-loop-0.md` under "HANDOFF-0034 — brief". Set `status: done`, `completed:`. Commit `jobs: kgme brief v1, Loop 0 (HANDOFF-0034)`. The week of hand runs starts on this commit.
