---
id: HANDOFF-0019
type: handoff
created: 2026-09-11T10:00:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-11T13:15:00-07:00
tier: 2
depends_on: null
supersedes: HANDOFF-0006
---

# Handoff 0019 — Verify the Backblaze backup and run a restore test (read-only)

Michou has chosen Backblaze Personal Backup instead of Time Machine (no external drive). This handoff closes the first scheduling gate in `docs/STATUS.md`: **a completed backup plus a tested restore.** It is read-only on the machine; the restore itself is Michou's action in the Backblaze web UI. **Run only after Michou says the initial backup shows complete in the Backblaze app.**

## Part A — verify (Claude Code, read-only)
1. Installed and running: `ls /Library/Backblaze.bzpkg/` (names only) and `pgrep -fl bztransmit || echo "not running"`.
2. Exclusions: read `/Library/Backblaze.bzpkg/bzdata/bzexcluderules_editable.xml` and `bzexcluderules_mandatory.xml` (if readable; note "permission denied" otherwise). Report every rule whose path or extension could exclude anything under `~/Projects`, `~/Documents`, `~/Desktop`. Nothing under `~/Projects/Finance` may be excluded.
3. Proof of upload: the transmitted-files logs live under `/Library/Backblaze.bzpkg/bzdata/bzlogs/bzreports_lastfilestransmitted/` (one file per day). `grep -c "Projects/Finance" <latest two files>` and `grep -c "Projects/Automate"` — counts only, never file contents. Report the count and the log dates. If the logs are unreadable, say so; Michou confirms from the app instead.
4. Private encryption key: **cannot be verified from the command line** — Michou confirms that Settings → Security in the Backblaze app shows the private encryption key as enabled. Record his confirmation verbatim ("Michou confirms PEK enabled, 2026-09-11 hh:mm").
5. Version history: record which retention Michou selected (30-day default or 1-year extended) — his statement, verbatim.

## Part B — restore test (Michou, then Claude Code verifies)
6. Before the restore, Claude Code computes `shasum -a 256` of one file Michou names under `~/Projects/Finance/Active/` (a workbook or PDF, not a secret) and records the hash in the report.
7. Michou restores that one file from the Backblaze web UI ("View/Restore Files" → download) to `~/Downloads/kgme-restore-test/`. Entering the private key on the restore page is expected — it is how PEK restores work.
8. Claude Code computes `shasum -a 256` of the restored file and compares. Identical hashes = the gate is met. Different or missing = the gate is not met; report and stop.
9. Michou deletes `~/Downloads/kgme-restore-test/` himself.

## Report
`docs/audit/2026-09-11-backup-verification.md` — `id: AUDIT-0007`, `type: report`, `status: final`, `handoff: HANDOFF-0019`, `author: claude-code`, `source: fetched`, `tier: 2`, `created:`. Sections A1–A5, B6–B8, then one line: **"Gate 1 (completed backup + tested restore): MET / NOT MET, <timestamp>"**. Then update the first row of `docs/STATUS.md` accordingly (this is the one STATUS edit an agent may make in this handoff). Set this handoff `status: done` with `completed:`; commit `backup: Backblaze verified and restore tested (HANDOFF-0019)`.

## Do not
Change any Backblaze setting. Install anything. Print file contents from the Backblaze logs. Touch anything under `~/Projects/Finance` beyond reading one file's hash.
