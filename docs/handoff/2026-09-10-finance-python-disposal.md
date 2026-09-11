---
id: HANDOFF-0018
type: handoff
created: 2026-09-10T09:25:00-07:00
from: michou
to: claude-code
status: open
tier: 2
depends_on: HANDOFF-0017
supersedes: HANDOFF-0016
audit_ref: "AUDIT-0006: one real finance-python at ~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python; 24,667 regenerable files (906 MB venv), 80 unique files (6.16 MB), never committed; 3 dead paths referenced by VS Code and Claude Code state."
---

> **Decision recorded 2026-09-11 (Michou, via Cowork):** the current modeling conventions file is `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md`. Step (c) repoints `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 to it (shown-diff-then-approve). The June root copy and the MRVL copy are left untouched.

# Handoff 0018 - Dismantle `finance-python`: repoint, archive, then delete

## Scope, stated first
The disposal unit is exactly `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/` and the outside references AUDIT-0006 §5 lists. **Nothing else under `~/Projects/Finance` is touched**, including the sibling `equity-quicktester/` and its venv, the `ALBEMARLE ` folder, and the three `MODELING_CONVENTIONS` copies. `~/Reference/FinanceToolkit` and `~/Reference/OpenBB` are out of scope.

## Why
AUDIT-0006 found the project untouched since 2026-05-13, `git init`-ed with zero commits and no remote, 906 MB of rebuildable venv wrapped around 6.16 MB of code, notebooks, agents, and notes that exist nowhere else. Every outside reference (VS Code recents, two Claude Code project keys, two state directories, two memory notes) points at one of three paths that no longer exist. The stale `CLAUDE.md` and `.claude/` inside it are the reason for disposal: they are an older agent configuration that competes with KGME's.

## Needs from Michou before this runs
1. Which conventions file is current: `Active/MODELING_CONVENTIONS_V2.md` (28.8 KB, 2026-07-22) or the root `MODELING_CONVENTIONS.md` (14.6 KB, 2026-06-18). The global pointer at line 16 of `~/.claude/CLAUDE.md` and `~/AGENTS.md` is broken today regardless of this disposal.
2. Whether to commit the archived tree to a local git repository before deletion (recommended: yes, local only, no remote).
3. Approval after each of the three steps; the handoff stops and reports between them.

## Step (c): references outside the unit
1. Show the diff, then edit `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 to point at the file chosen in Needs 1. Human-authored files: diff shown, approval, then write (ADR-004).
2. Show the diff, then add one line each to `~/.claude/projects/-Users-michaelgrigorian/memory/home_layout.md` and `project_equity_quicktester.md` recording that `finance-python` now lives at `~/Archive/finance-python-2026-09/`. The three ADRs and `lessons/validate-comps-peer-set.md` are historical records: untouched.
3. Show the diff, then remove the two dangling keys `/Users/michaelgrigorian/finance-python` and `/Users/michaelgrigorian/Projects/Finance/Active/finance-python` from the `projects` object in `~/.claude.json`. Back up first: `cp ~/.claude.json ~/.claude.json.bak.HANDOFF-0018`. Do this only while no Claude Code session other than the executing one is running, since Claude Code rewrites this file.
4. Report the three VS Code "Open Recent" entries for Michou to clear in the UI (File → Open Recent → Clear Recently Opened, or remove the three individually). Do not edit `storage.json`.
5. Leave `~/.zsh_history` alone.
6. Report and stop.

## Step (b): archive with a manifest
1. Preconditions: step (c) approved.
2. `mkdir -p ~/Archive/finance-python-2026-09/tree ~/Archive/finance-python-2026-09/claude-memory`.
3. Build the manifest from the source before copying: from inside the unit, `find . -type f -not -path './.venv/*' -not -path './.git/*' -not -path '*/__pycache__/*' -not -path './.ruff_cache/*' -not -name .DS_Store -not -name '~$*' -print0 | xargs -0 shasum -a 256 > ~/Archive/finance-python-2026-09/MANIFEST.sha256`. Expected: 80 lines (AUDIT-0006 §3). Stop if the count differs.
4. Copy, do not move: `rsync -a --exclude .venv --exclude .git --exclude __pycache__ --exclude .ruff_cache --exclude .DS_Store --exclude '~$*' "<unit>/" ~/Archive/finance-python-2026-09/tree/`.
5. Copy the two memory files: `cp ~/.claude/projects/-Users-michaelgrigorian-finance-python/memory/*.md ~/Archive/finance-python-2026-09/claude-memory/` and append their hashes to the manifest.
6. Verify: `cd ~/Archive/finance-python-2026-09/tree && shasum -a 256 -c ../MANIFEST.sha256` (memory lines checked from their own directory) must report zero failures. Stop on any failure.
7. Write `~/Archive/finance-python-2026-09/README.md`: source path, date, AUDIT-0006, the four historical paths the project lived at, manifest count, and the note that it was never committed.
8. If Needs 2 is yes: `git -C ~/Archive/finance-python-2026-09/tree init -b main && git add -A && git commit -m "finance-python as archived 2026-09"`. Show `git status` before `add`; confirm no `.env` is present (AUDIT-0006 found only `.env.example`).
9. Report and stop. The unit is still intact.

## Step (a): delete regenerable content, then the unit
1. Preconditions: step (b) verified with zero failures and approved.
2. Inside the unit, delete only: `.venv`, `.git`, `.ruff_cache`, every `__pycache__`, every `.DS_Store`, and `notebooks/ALB/~$ALB_Long_Pitch_v1_DRAFT.pptx`. Print `du -sh` of each target before removal. Expected residue: 80 files, all present in the archive.
3. Re-verify the residue against the manifest from inside the unit (`shasum -a 256 -c`). Zero failures required.
4. Outside the unit: `rm -rf ~/.claude/projects/-Users-michaelgrigorian-Projects-Finance-Active-finance-python` (transcripts) and, only after step (b) item 6 verified the memory copies, `rm -rf ~/.claude/projects/-Users-michaelgrigorian-finance-python`. Remove the three VS Code `workspaceStorage` directories `6a2b70f30b17ba6b6cb7b7c2c85c1ba0`, `80682a549d6651cdb79f4dd24d07e275`, `dc6ca7fa6083e0ad0dff2c24db11102d` only while VS Code is closed.
5. **Gate:** `tmutil latestbackup` must succeed with a snapshot dated after step (b) completed. Today it fails (no destination, HANDOFF-0006 pending). If it fails, stop here: the 80-file residue stays in place as a second copy and the handoff reports "archived, residue retained pending backup".
6. After the gate passes: `mv "<unit>" ~/.Trash/finance-python-$(date +%Y%m%d)`. Trash, not `rm`; the agent never empties the Trash.
7. Report and set `status: done`.

## Reversibility
- (c) Every edit is diffed and approved; `~/.claude.json` has an explicit backup. Reverse by restoring the old line or the backup.
- (b) Adds files only. Reverse with `rm -rf ~/Archive/finance-python-2026-09`.
- (a) items 2 and 4: `.venv` rebuilds with `uv sync` from the archived `pyproject.toml` and `uv.lock` (Python 3.13); caches regenerate; the empty `.git` and the transcripts carry nothing recoverable that anyone needs. Not reversible in place, but nothing unique is lost because (b) has been hash-verified.
- (a) item 6: reversible from the Trash until Michou empties it, then from Time Machine.

## Risks
The only unique bytes are 6.16 MB of code, notebooks, and notes plus two memory files; the manifest built before the copy and checked after it, then checked again on the residue, is what protects them. The `~/.claude.json` edit is the one step that touches a live tool's state; the backup and the "no other session running" condition bound it. If Michou chooses the wrong conventions file in Needs 1, the fix is a second one-line edit, not data loss.

## Do not
Touch any path under `~/Projects/Finance` outside the unit. Touch `~/Reference/`. Empty the Trash. Push any repository. Edit VS Code's `storage.json`. Open `.env.example`, `wrds_data.py`, or the `.pkl` cache. Modify any other proposal.

## Report
`docs/audit/<date>-finance-python-disposal.md` (`type: report`, `status: final`, `handoff: HANDOFF-0018`, `author: claude-code`, `source: fetched`, `tier: 2`), one section per step with the manifest count, both `shasum -c` results, and the `tmutil latestbackup` output at the gate. Commit: `archive: finance-python disposal (HANDOFF-0018)`.
