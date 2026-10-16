---
id: HANDOFF-0016
type: handoff
created: 2026-09-09T23:30:00-07:00
from: claude-code
to: claude-code
status: abandoned
tier: 2
depends_on: HANDOFF-0014
audit_ref: "AUDIT-0005: 27,219 of 28,071 files are regenerable venvs and caches; 852 files (836.5 MB) are unique work product, including a never-committed finance-python tree."
superseded_by: HANDOFF-0017
reason: "Scope error: ~/Projects/Finance is to be kept; only finance-python is to be dismantled (Michou, 2026-09-09 23:40)"
---

# Handoff 0016 (proposed) - Dispose of `~/Projects/Finance`: repoint, archive, then delete

## Why
AUDIT-0005 (`docs/audit/2026-09-09-finance-inventory.md`) found that `~/Projects/Finance` is 97.0% regenerable by file count (two `uv` virtual environments and caches, about 960 MB on disk) and that the remaining 852 files (836.5 MB) are the analyst's own pitch models, memos, filings, and two Python projects, of which `finance-python` was `git init`-ed but never committed and has no remote. 343 of its 349 workbook and PDF filenames exist nowhere else on the machine. Two instruction files (`~/.claude/CLAUDE.md` and `~/AGENTS.md`, line 16 in each) point at `~/Projects/Finance/Active/MODELING_CONVENTIONS.md`, a path that already does not exist. Michou wants the folder gone; the charter forbids an irreversible delete without a backup, so this proposal orders the work as (c) repoint, then (b) archive with a manifest, then (a) delete regenerable content, with deletion of the archive itself gated on a verified Time Machine backup (HANDOFF-0006).

## Needs from Michou before this runs
1. Which conventions file is current: `~/Projects/Finance/MODELING_CONVENTIONS.md` (root, 2026-06-18) or `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md`. And where it should live afterwards (recommended: this repository under `docs/` or the Tier 2 memory tree, not `~/Archive`).
2. Confirmation that the five recently edited files (the MRVL workbook dated 2026-09-08 and the four `Active/thesis/` documents dated 2026-08-31 to 2026-09-07) are finished or have been relocated to wherever current work lives.
3. Whether the `finance-python` and `equity-quicktester` source trees should be committed to a git repository somewhere (recommended: yes, a private repo, before archiving) or archived as plain files only.
4. Approval of each of the three steps separately; the handoff stops after each step and reports.

## Step (c): update everything outside the folder first
1. Show the diff, then edit `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 to point at the new conventions location chosen in Needs 1. Copy the chosen conventions file to that location first (`cp`, not `mv`, so the original stays in place for step (b)). Both files are human-authored: diff shown and approved before writing (ADR-004).
2. Show the diff, then correct the two memory notes that state Finance paths as fact: `~/.claude/projects/-Users-michaelgrigorian/memory/home_layout.md` and `project_equity_quicktester.md`. One line each, recording the archive path from step (b). The other four notes that mention the folder in passing (`MEMORY.md`, `user_profile.md`, `fmp_plan_and_api.md`, `decisions/adr/ADR-0001-phase0-brain-audit.md`) are left alone.
3. Leave `~/.claude.json` and the two orphaned `~/.claude/projects/…finance-python/` directories untouched; they are session records, already unreachable by path, and Claude Code tolerates missing project paths. Record their existence in the report.
4. Add a note to `docs/handoff/proposed/2026-09-09-rename-space-paths.md`? No: proposals are not edited by other handoffs. Instead the report lists which HANDOFF-0011 targets are mooted, and Cowork re-scopes 0011.
5. Report and stop.

## Step (b): archive the unique work product with a manifest
1. Preconditions: step (c) reported done and approved; `df -h ~` shows at least 2 GB free.
2. Define the exclusion list exactly as in step (a) below. Everything else is archived.
3. `mkdir -p ~/Archive/finance-2026-09`.
4. Before moving anything, generate the manifest from the source: `cd ~/Projects/Finance && find . -type f <exclusions> -print0 | xargs -0 shasum -a 256 > ~/Archive/finance-2026-09/MANIFEST.sha256`. Expected line count: 852 (AUDIT-0005 §2); stop if it differs by more than the `.DS_Store` and lock-file noise.
5. Copy, do not move: `rsync -a --exclude-from=<exclusion file> ~/Projects/Finance/ ~/Archive/finance-2026-09/tree/`. rsync with `-a` preserves mtimes, which matter for the "outdated" evidence trail.
6. Verify: `cd ~/Archive/finance-2026-09/tree && shasum -a 256 -c ../MANIFEST.sha256` must report zero failures. Stop on any failure.
7. Write `~/Archive/finance-2026-09/README.md`: source path, date, AUDIT-0005 id, manifest line count, the six filenames that also exist in `~/Documents` and iCloud Drive (AUDIT-0005 §6) with their sha256 so duplicates can be settled later, and the note that `finance-python` was never committed.
8. If Needs 3 was "yes": `git -C ~/Archive/finance-2026-09/tree/ARCHIVE\ PITCHES\ -\ SUMMER\ 26\ INTERNSHIP/finance-python add -A && git commit` (local only, no remote, no push). Same for `equity-quicktester` after `git init -b main`. Show the file list before committing; `.env.example` is a template, but the agent verifies no real `.env` is present before `git add`.
9. Report (manifest count, verification result, archive size) and stop. `~/Projects/Finance` is still intact at this point.

## Step (a): delete the regenerable set, then the source folder
1. Preconditions: step (b) verified with zero manifest failures and approved.
2. Delete inside `~/Projects/Finance` only these paths, each listed with `du -sh` first and confirmed against AUDIT-0005 §2: `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/.venv`, `…/equity-quicktester/.venv`, `…/finance-python/.git` (zero commits), every `__pycache__`, `.ruff_cache`, `.pytest_cache`, `.ipynb_checkpoints` directory, every `.DS_Store`, and the six `~$…` Office lock files in `Active/`. Command shape: `rm -rf` on the explicit venv paths, then `find ~/Projects/Finance -type d \( -name __pycache__ -o -name .ruff_cache -o -name .pytest_cache -o -name .ipynb_checkpoints \) -prune -exec rm -rf {} +`, then `find ~/Projects/Finance -name .DS_Store -delete`. Expected result: about 852 files remain, all present in the archive.
3. Re-run the manifest check against what remains (`shasum -a 256 -c` from inside `~/Projects/Finance`) to prove the residue equals the archive.
4. **Gate:** `tmutil latestbackup` must succeed and return a snapshot dated after step (b) finished. If it fails (as it does today: destination not configured), stop here. `~/Projects/Finance` stays on disk as a second copy until HANDOFF-0006 is done and a backup containing `~/Archive/finance-2026-09` exists.
5. Only after the gate passes: `mv ~/Projects/Finance ~/.Trash/Finance-$(date +%Y%m%d)` (Trash, not `rm`, so Finder can restore it for the days before Michou empties the Trash himself; the agent never empties the Trash).
6. Report and set `status: done`.

## Reversibility
- Step (c): every edit is diffed and approved; reverse by re-applying the old line. The `cp` of the conventions file adds a copy and removes nothing.
- Step (b): adds files under `~/Archive/finance-2026-09/` and removes nothing; reverse with `rm -rf ~/Archive/finance-2026-09`.
- Step (a) items 2 to 3: the venvs are rebuilt with `uv sync` from the archived `pyproject.toml` and `uv.lock`; caches and lock files regenerate on next use; the empty `.git` carried no history. **Not reversible from inside the folder**, but nothing unique is lost because step (b) has already been verified.
- Step (a) item 5: reversible from the Trash until Michou empties it, and from Time Machine after that. This is the only irreversible-in-principle step and it is gated on the backup.

## Risks
The manifest is built before the copy and verified after, so a silent rsync truncation is caught. The main residual risk is the six same-named workbooks in `~/Documents` and iCloud Drive: if those are newer versions, the Finance copies are stale and the archive is redundant for them; if older, the archive holds the latest. The README records hashes so this is decidable later without the source folder. A second risk is that Michou keeps editing `Active/thesis/` between steps (b) and (a); the manifest re-check in step (a) item 3 catches any changed file and stops.

## Do not
Run `rm` on anything not in the step (a) exclusion list. Empty the Trash. Push any git repository. Modify `~/.claude/settings.json`, `~/.codex/config.toml`, or any file under `docs/handoff/proposed/` other than this one's status line. Read `.env` files if any are found; report their existence and skip them.

## Report
`docs/audit/<date>-finance-disposal.md` (`type: report`, `status: final`, `handoff: HANDOFF-0016`, `author: claude-code`, `source: fetched`, `tier: 2`) with one section per step, the manifest line count, the `shasum -c` result, and the `tmutil latestbackup` output at the gate. Commit: `archive: Finance folder disposal (HANDOFF-0016)`.
