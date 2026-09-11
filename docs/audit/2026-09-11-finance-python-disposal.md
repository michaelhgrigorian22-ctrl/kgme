---
id: AUDIT-0010
type: report
status: final
handoff: HANDOFF-0018
author: claude-code
source: fetched
tier: 2
created: 2026-09-11T14:45:00-07:00
---

# finance-python disposal - 2026-09-11

Per HANDOFF-0018, adopted by Michou at 14:30 (commit 2702979). Unit: `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/`. Michou's inputs before the run: conventions pointer → `Active/MODELING_CONVENTIONS_V2.md`; archive tree gets a local-only git baseline. Pre-run check: 80 archive-set files, newest content 2026-05-13, only `.env.example` present, 226 GB free. Finalised 2026-09-11T15:05:00-07:00 on Michou's decision below.

## Step (c): references outside the unit

1. **Global instruction files.** `~/.claude/CLAUDE.md` and `~/AGENTS.md` (separate files, not a symlink) backed up to `*.bak.20260911`. Line 16 in each changed from `~/Projects/Finance/Active/MODELING_CONVENTIONS.md` to `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md` (28,756 bytes, 2026-07-22, present). No other character changed; diff shown to Michou.
2. **Memory notes.** One line appended to each of `~/.claude/projects/-Users-michaelgrigorian/memory/home_layout.md` (after its `Active/` bullet) and `project_equity_quicktester.md` (at the end), recording the archive path and, in the second, equity-quicktester's real location. Diffs shown. The three ADRs and the lesson note untouched.
3. **`~/.claude.json`.** Backed up to `~/.claude.json.bak.HANDOFF-0018` (58,724 bytes). Removed the two dangling `projects` keys `/Users/michaelgrigorian/finance-python` and `/Users/michaelgrigorian/Projects/Finance/Active/finance-python`; 8 project keys before, 6 after; file re-parsed as valid JSON (58,178 bytes). Other Claude Code processes were running at the time; if one rewrites the file from its own in-memory copy the two keys may reappear, which is harmless and detectable by re-running the key check.
4. **VS Code.** Not edited. The three dead "Open Recent" entries (`~/Downloads/finance-python`, `~/finance-python`, `~/Projects/Finance/Active/finance-python`) are Michou's to clear in the UI.
5. **`~/.zsh_history`.** Untouched (37 lines mention the name).

## Step (b): archive with manifest

| Item | Value |
|---|---|
| Archive | `~/Archive/finance-python-2026-09/` (`tree/`, `claude-memory/`, `MANIFEST.sha256`, `MANIFEST-claude-memory.sha256`, `README.md`), 84 files, 6.3 MB |
| Manifest built from source before copy | 80 lines, as expected |
| Copy | `rsync -a` with the six exclusions; mtimes preserved |
| Verify tree | `shasum -a 256 -c`: 80/80 OK, zero failures |
| Memory notes | `MEMORY.md`, `feedback_pitch_process.md` copied from `~/.claude/projects/-Users-michaelgrigorian-finance-python/memory/`; both hashes OK |
| Git baseline | `git init -b main` in `tree/`, commit `ee4ac00` "finance-python as archived 2026-09", 77 files, no remote. Three of the 80 files are excluded from the commit by the project's own `data/.gitignore`, which ignores everything under `data/` (`data/.gitkeep`, the EDGAR `.pkl` cache, the screen `.csv`); they are present in `tree/` and in the manifest regardless. |
| `.env` | absent; only `.env.example` committed |

The unit itself is still intact at this point.

## Step (a): delete regenerable content

Michou approved step (a) at 14:50 and, in the same message, replaced the `tmutil latestbackup` gate with the Backblaze equivalent (the archive path appearing in Backblaze's transmitted-files log). Claude Code's deletion command was refused twice at the permission layer: `~/.claude/settings.json` denies `Bash(rm -rf *)` globally. That guard was left in place; Michou ran the deletion lines himself in his own terminal tab at about 14:55.

| Item | Result (verified by Claude Code after "done") |
|---|---|
| `.venv` (906 MB), `.git`, `.ruff_cache` | gone |
| `__pycache__` directories, `.DS_Store` files, Office lock file | gone (0 remaining) |
| Residue in the unit | 80 files, 6.3 MB; `shasum -a 256 -c` against the manifest: 80/80 OK |
| Archive re-check | 80/80 OK |
| `~/.claude/projects/-Users-michaelgrigorian-Projects-Finance-Active-finance-python` | removed |
| `~/.claude/projects/-Users-michaelgrigorian-finance-python` | removed at 15:05 (2 memory files, unchanged since 2026-04-22, both archived and hash-verified in `claude-memory/`) |
| VS Code `workspaceStorage` (3 dirs) | left in place; VS Code was running |

Gate (Backblaze): at 14:52 the transmitted log `11.log` (last written 13:22) had 0 lines for `Archive/finance-python-2026-09`; the uploader was idle between scans. The move of the unit to the Trash waits for the archive to appear in the log.

## Outcome

Michou's decision at 15:00: **the unit's 80 remaining files stay in place; the unit is not moved to the Trash.** Items (a)5 and (a)6 of the handoff are therefore not executed, and the Backblaze gate is moot for this handoff. Final state: `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/` holds exactly the 80 archive-set files (6.3 MB) with no venv, git, or cache content; a byte-identical, hash-verified copy with a local git baseline sits at `~/Archive/finance-python-2026-09/`; the global conventions pointer, `~/.claude.json`, and the two memory notes are corrected. Regenerable content removed from the machine: about 24,667 files and 906 MB.

Reversibility of what was done: global files and `~/.claude.json` restore from their `.bak` copies; the memory-note lines are single appended lines; the venv rebuilds with `uv sync` from the archived `pyproject.toml` and `uv.lock`; the archive can be deleted with `rm -rf ~/Archive/finance-python-2026-09` if ever unwanted.
