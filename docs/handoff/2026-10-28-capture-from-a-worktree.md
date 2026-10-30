---
id: HANDOFF-0065
type: handoff
created: 2026-10-28T00:55:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0047, HANDOFF-0050]
plan_ref: PLAN-PHASE-1 step 10d
---

# Handoff 0065 — `kgme capture` from a worktree writes that worktree, not the one vault and the one ledger

## Why
Found by the design session on 2026-10-28 00:50 and measured by Cowork: the design worktree (`~/Projects/KGME/design`) has two dirty files that neither Codex nor the design session touched. `logs/ledger/2026-10.jsonl` holds five events, all `kgme.capture` (two intents, two outcomes, one note) between 2026-10-27T16:50:59 and 16:51:17; `memory/inbox/friction-log.md` holds one new line, `- 2026-10-27 16:51 — 14% usage left till nov 1st`. Michou ran `kgme capture friction` from a shell whose working directory was the design worktree. HANDOFF-0047 §3 says every checkout writes the one ledger, and `ledger.read_record_root` is built to return the main checkout for any git checkout (review cycle 1 F4, cycle 2 F10), falling back to `base` only when `read_main_checkout` raises. From the design worktree it wrote the worktree's copy, so either the fallback fired or capture does not go through it for the vault write. The vault is `main`'s: a line captured into the design branch's `memory/inbox/` can never land, because the design track's lanes do not include `memory/` and `kgme merge design` refuses the commit.

## What
1. **Measure first.** From the design worktree, with a temporary ledger root or a dry run if capture has one: which root `read_record_root` and `read_main_checkout` return, and which path the vault write resolves to. Record both in the report. The hooks' own resolution (`git rev-parse --git-common-dir`, which the post-commit hook uses) is the reference.
2. **Fix the named cause, nothing else.** A capture from any worktree of the repository writes the main checkout's vault file and the main checkout's ledger, by the same resolution the hooks use; a run outside any checkout of the repository is refused with the reason printed. If the measurement shows `read_main_checkout` failing for a worktree whose `.git` file names an absolute path, the fix is there, and every job that calls `read_record_root` gets it at once; the report names them.
3. **The stray records.** Finished records are never edited and the ledger is never written by hand. Michou re-captures the words on `main` (`kgme capture friction "14% usage left till nov 1st"`), so the vault line and its ledger events exist where they belong, with today's time; this handoff's report quotes the five stray events and the original time (16:51 PDT, 2026-10-27) in full, and the design worktree's two files are restored to their committed state by Michou (`git checkout -- logs/ledger/2026-10.jsonl memory/inbox/friction-log.md` in the worktree). The record survives in the report; the worktree is clean.

## Outputs
`kgme/ledger.py` or `kgme/capture_io.py`, whichever the measurement names, `tests/test_capture_worktree.py` (a capture from a worktree writes the main checkout's vault and ledger; a run outside the repository is refused), a measurement note in the report.

## Acceptance test (under five minutes)
From a worktree made under a temporary clone, `kgme capture note "x"` writes the clone's `memory/inbox/` file and the clone's ledger, and the worktree's working tree stays clean. From a folder that is no checkout, it refuses and prints why. `make check` green.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one resolution function and one test. `git revert`.

## Needs from Michou
Adoption, after HANDOFF-0048 closes or at its next natural break. The re-capture on `main` and the restore in the worktree (item 3), in that order.

## Report
`docs/audit/2026-10-DD-capture-from-a-worktree.md`. Set `status: done`, `completed:`. Commit `capture: a worktree's capture writes the one vault and the one ledger (HANDOFF-0065)`.
