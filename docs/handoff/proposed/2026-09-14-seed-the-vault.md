---
id: HANDOFF-0035
type: handoff
created: 2026-09-14T22:25:00-07:00
from: claude-code
to: michou
tier: 2
status: proposed
depends_on: HANDOFF-0034
plan_ref: PLAN-PHASE-1 step 10
---

# Handoff 0035 (proposed, for Michou) — Seed the vault

## Why
Verified 2026-09-14: `memory/` holds zero reminders, zero tasks, zero daily notes, and one template. The friction log has one example entry against an exit gate of ten. Loop 0 run against this vault produces an empty brief, and the exit criterion "run by hand for a week" would measure nothing. This is Michou's own act; no agent writes to `memory/notes/`, `memory/daily/`, or `memory/inbox/` (ADR-004).

## What
1. From the templates shipped in 0034, create at least five real reminders and five real tasks under `memory/notes/`, with real due dates over the next two weeks.
2. Write today's daily note at `memory/daily/YYYY-MM-DD.md` and keep it up for the week of runs.
3. Bring `memory/inbox/friction-log.md` to ten real entries in the stated one-line format; delete or keep the example line as he likes.
4. Run `kgme lint` after; fix anything it flags in his own files.

## Outputs
Human notes under `memory/notes/`, `memory/daily/`, `memory/inbox/`.

## Acceptance test
`kgme lint` exits 0; `kgme brief --dry-run` prints a brief with at least one entry in each of the first three sections; the friction log has ten dated entries.

## Reviewer
None. The brief is the review.

## Reversibility
His files; his call.

## Needs from Michou
About thirty minutes once, then two minutes a day for the week.

## Report
No report. `status: done` when the acceptance test passes; the first real brief's ledger `outcome` id is the record.

## Amendment (Cowork, 2026-10-16; Michou: "i think this is a good call")
The targets stand; the method changes. Reminders, tasks and friction come from `kgme capture` on Michou's word, and daily notes are drafted by `kgme daily` and count once he has read them (HANDOFF-0050). Obsidian is not used to seed the vault; it becomes a lens (HANDOFF-0051). This handoff depends on HANDOFF-0050.
