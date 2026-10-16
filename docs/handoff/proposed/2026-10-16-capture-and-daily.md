---
id: HANDOFF-0050
type: handoff
created: 2026-10-16T13:50:00-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0034, HANDOFF-0049]
plan_ref: PLAN-PHASE-1 step 9c
---

# Handoff 0050 (proposed) — Capture by talking, daily notes drafted: the vault fills from what Michou says, not from what he types

## Why
The vault has had nothing new from Michou since 2026-09-15: one daily note, two friction entries, the cockpit wishlist. Loop 0's brief (HANDOFF-0034, built) reads its inputs from `memory/`, and Phase 1 cannot exit until HANDOFF-0035 seeds it, which assumed he would type reminders, tasks, daily notes and friction into Obsidian. Michou, 2026-10-16: "daily notes flopped and the obsidian literally never expanded or got added to once", and on Cowork's recommendation to capture where he already talks and to draft the daily note: "i think this is a good call." He narrates his work to agents all day; the capture belongs there.

## What
1. **`kgme capture <kind> "<his words>" [--due <when>]`**, kinds `remind`, `task`, `friction`, `note`, `daily`. A job under ADR-013 (manifest: write `memory/notes/` new files only, `memory/inbox/friction-log.md` and `memory/daily/<today>.md` append only; no network; Tier 2 at most). A reminder or task is a new file from `memory/templates/reminder.md` or `task.md` with his words as the body, `source: stated`, `author: kgme`, the due date resolved to ISO 8601 with offset (an unresolvable date is a refusal that prints what it could not read). A friction entry is one line appended in the log's own format. Every capture is one ledger `intent` and `outcome`, and the command prints the exact line or file it wrote. It never edits or deletes anything that exists.
2. **Agents capture on his word.** `CLAUDE.md` gains one line under "How decisions are made": when Michou states a reminder, a task, a friction or a note in a session, the agent runs `kgme capture` with his words verbatim and shows him the result; it never paraphrases into the vault. Cowork does the same through the same command once it can run it, and until then appends with the identical format and says so.
3. **The daily note is drafted.** `kgme daily` (by hand now, 21:30 every day once the Phase 3 heartbeat exists) creates `memory/daily/<date>.md` if it does not exist, from the template's five sections. Today: the day's ledger (handoffs moved, reviews, commits, captures). Learned and Problems and solutions: from the day's audits, rulings and dispositions. Tomorrow: open handoffs and due reminders and tasks. Friction: the day's friction captures. Drafted sections carry `source: inferred`; anything Michou adds with `kgme capture daily "..."` lands verbatim under a closing "Michou" heading as `stated`. A day with nothing in the ledger writes nothing.
4. **HANDOFF-0035 is carried out through capture.** Its targets stand (five reminders, five tasks, a week of daily notes, ten friction entries); typing them in Obsidian is no longer the way. A drafted daily note counts once Michou has read it in the morning brief; adding a line is optional.
5. **Obsidian is not part of capture.** It becomes a lens only (HANDOFF-0051).

## Outputs
`kgme/capture.py`, `kgme/daily.py` (effects and pure logic split per ADR-015), `kgme/cli.py` (`capture`, `daily`), `jobs/capture/manifest.toml`, `jobs/daily/manifest.toml`, `tests/test_capture.py`, `tests/test_daily.py`, canary rows for both manifests, `CLAUDE.md` one line (as a diff Michou approves), a section in `docs/readers/` (as a diff).

## Acceptance test (under ten minutes)
`kgme capture remind "pay the Backblaze renewal" --due "friday 9am"` creates one reminder with a resolved due date and one ledger pair, and prints the file; `kgme capture friction "..."` appends exactly one formatted line; a capture into an existing file never changes a byte before its end; `kgme daily` on a day with ledger events writes one note whose sections cite the events they came from, and on a second run does nothing; `kgme brief` the next morning lists the reminder and the friction line.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: new files and appended lines in `memory/`. `git revert`; captured items are ordinary notes.

## Needs from Michou
Adoption after 0049 closes. The daily draft time (proposed 21:30). Nothing else: the habit he wanted (learned, problems and solutions, tomorrow) arrives without typing.

## Report
`docs/audit/2026-10-DD-capture-and-daily.md`, named in `report:` on closing. Commit `vault: capture by talking, daily notes drafted (HANDOFF-0050)`.
