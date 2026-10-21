---
id: HANDOFF-0052
type: handoff
created: 2026-10-21T00:50:00-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0050]
plan_ref: PLAN-PHASE-1 step 9c
---

# Handoff 0052 (proposed) — Kept copies in the brief: a save capture kept is named the next morning, and the rest are counted with the command that clears them

## Why
HANDOFF-0050 keeps every file a capture swaps out as `.<name>.capture-<id>` and deletes nothing (the rulings on review cycle 6, F13 and F15, option A). A copy that no longer matches its recorded hashes holds a save of Michou's that the file lacks. Two places find it today: the next capture into the same file, and `kgme clean kept`. A past day's note never gets a next capture, so a save kept beside one is found only when someone runs `kgme clean kept`, which nothing schedules (approval-screen item, cycle 7, score 0.6: copies pile up, one per line added). The brief is read every morning and already reads `memory/daily` and `memory/inbox`; it is where a kept save should surface. Anything checkable becomes a check (ADR-023).

## What
1. **`## Kept copies` in the brief.** For every `.*.capture-*` under `memory/`, the brief applies the same test as `kgme capture` and `kgme clean kept` (one function, reused from `kgme/capture_recover.py`, never a second copy of the rule):
   - a copy with no `kept` note, or whose bytes hash to neither recorded value, is listed by name with the file it belongs to: "holds a save `<file>` lacks: merge it by hand, then delete it";
   - the copies that still match are one line: their count, their total size, and `kgme clean kept --yes`.
   No copies: the section says so, as every empty section does. Read-only: the brief deletes nothing.
2. **Manifest.** `jobs/brief/manifest.toml` gains read access to `memory/**/.*.capture-*`; nothing else widens.
3. **Schedule, later.** When the Phase 3 heartbeat exists, `kgme clean kept --yes` runs nightly after `kgme daily`; a refusal is a `blocking` outcome the brief already shows. Until then it runs by hand from the brief's line.

## Outputs
`kgme/brief.py` or `kgme/brief_read.py` (the section), `jobs/brief/job.md` (Inputs and Output), `jobs/brief/manifest.toml`, tests in `tests/test_brief*.py`, a sentence in `docs/readers/capture.md` (as a diff Michou approves).

## Acceptance test (under ten minutes)
A fixture vault with three copies beside a past day's note and the friction log: one matching the file as read, one matching the capture's own bytes, one edited after the fact. The brief names the edited one and its file, and counts the other two with their size and the command. `kgme clean kept --yes` refuses and removes nothing. After the edited copy is deleted by hand, `kgme clean kept --yes` removes the other two and the next brief says there are none.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one brief section, one read path. `git revert`.

## Needs from Michou
Adoption after 0050 is committed; it can run beside 0045 or 0051.

## Report
`docs/audit/2026-10-DD-kept-copies.md`, named in `report:` on closing. Commit `brief: kept copies named each morning (HANDOFF-0052)`.
