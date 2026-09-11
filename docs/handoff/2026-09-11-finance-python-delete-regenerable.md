---
id: HANDOFF-0024
type: handoff
created: 2026-09-11T23:10:00-07:00
from: cowork
to: claude-code
tier: 2
depends_on: HANDOFF-0018
supersedes: "HANDOFF-0018 step (a) only"
status: abandoned
reason: "Not needed: 0018 step (a) was completed on 2026-09-11 after Michou ran the deletions himself and ruled that the unit stays in place; the Backblaze gate became moot. Kept as the record of the re-gating decision."
---

# Handoff 0024 — finance-python: delete the regenerable content (step (a) of 0018, re-gated on Backblaze)

HANDOFF-0018 completed steps (c) and (b): pointers fixed, the unique 80 files and two memory notes archived at `~/Archive/finance-python-2026-09/` with a verified sha256 manifest and a git baseline. Its step (a) was gated on `tmutil latestbackup`, which can never succeed here because Michou uses Backblaze, not Time Machine (HANDOFF-0019). Claude Code reported this correctly and stopped. This handoff replaces that gate and carries out step (a) only. **Nothing here touches the archive, `~/Projects/Finance` outside the unit, or any human file.**

## Gate (read-only)
1. Backblaze must have transmitted the archive: `grep -c "Archive/finance-python-2026-09" /Library/Backblaze.bzpkg/bzdata/bzlogs/bzreports_lastfilestransmitted/*` — report the count per file. Require ≥ 80 matching lines in total (one per archived file). If fewer, **stop**: the archive is not yet off-machine; wait and re-run.
2. Re-verify the archive on disk: `cd ~/Archive/finance-python-2026-09 && shasum -a 256 -c MANIFEST.sha256 | grep -c OK` must equal 80, and `MANIFEST-claude-memory.sha256` must verify 2/2.

## Delete (Michou approves at the prompt; list the exact paths first)
3. Inside `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/`: `.venv/`, `.git/`, `.ruff_cache/`, every `__pycache__/`, every `.DS_Store`, and `notebooks/ALB/~$ALB_Long_Pitch_v1_DRAFT.pptx`. Print `du -sh` of each before and the total after.
4. Outside the unit: `~/.claude/projects/-Users-michaelgrigorian-Projects-Finance-Active-finance-python/` (transcripts, regenerable) and `~/.claude/projects/-Users-michaelgrigorian-finance-python/` (its two memory files are already archived — verify the archive copies once more by hash before removing).
5. Do **not** delete the unit's remaining 80 human files. They stay in place until Michou decides, separately, whether the working copy goes too; the archive is the copy of record either way.

## Report
Append **"HANDOFF-0024 — step (a)"** to `docs/audit/2026-09-11-finance-python-disposal.md`: gate counts, paths deleted, bytes freed, what remains. Set `status: done`, `completed:`. Also set HANDOFF-0018 `status: done` with a `completed:` line and a note "step (a) via HANDOFF-0024". Commit `disposal: finance-python regenerable content deleted after Backblaze gate (HANDOFF-0024)`.
