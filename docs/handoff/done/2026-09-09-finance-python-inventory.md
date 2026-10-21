---
id: HANDOFF-0017
type: handoff
created: 2026-09-09T23:45:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-10T09:28:00-07:00
report: docs/audit/2026-09-09-finance-python-inventory.md
tier: 2
depends_on: HANDOFF-0014
supersedes: HANDOFF-0016
---

# Handoff 0017 — Inventory `finance-python` (and only it) before disposal — read-only

**Scope correction.** HANDOFF-0014 was scoped to all of `~/Projects/Finance`. That was a misunderstanding: `~/Projects/Finance` (Active / Archive / past memos and theses) is Michou's most important work and is **kept, untouched**. The thing to dismantle is the old `finance-python` project — the experiment that carries its own `CLAUDE.md`, `.claude/` agents, stale memory pointers, and VS Code links. HANDOFF-0016 is abandoned. **Change nothing in this handoff.**

## Find every trace of `finance-python` — and its siblings
Michou has since shown a Finder view of the thing itself: a folder holding loose Python files (`error_model.py`, `etf_info.py`, `euribor_model.py`, `evar_model.py`, `exposure.py`, `famafrench_router.py`, `fixedincome_controller.py`, `fmp_model.py`, `examples.md`, a notebook `Finance Toolkit - 0. READ… .ipynb`) plus **two** sub-folders, `finance_python` (underscore) **and** `finance-python` (hyphen). The loose files match the open-source *FinanceToolkit* package's module names, so most of it is a copied library, regenerable with `pip`. He does not know where this folder sits. Locate it first:

0. **Locate.** `find ~ -maxdepth 6 \( -iname 'finance-python' -o -iname 'finance_python' -o -iname 'financetoolkit' \) -type d 2>/dev/null` and `find ~ -maxdepth 7 -name 'fmp_model.py' 2>/dev/null`; also `mdfind -name 'famafrench_router.py'`. Report every hit. The **parent** directory of the loose files is the disposal unit, not just the two sub-folders. Exclude `~/Library`, `~/.Trash`, and any `site-packages` path from the disposal unit (those are installed libraries, not his copy) but report them.

1. **Directories.** The audit saw `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/` (with `CLAUDE.md` and `.claude/`). Claude Code project state also names `~/Projects/Finance/Active/finance-python` and `~/finance-python`. For each candidate found in step 0 (and the audit's three): exists? path, file count, `du -sh`, newest mtime. Are the two `uv` virtual environments and caches from AUDIT-0005 (≈960 MB, 27,219 files) inside `finance-python`? Say which path.
2. **Git.** For each `finance-python` directory: is there a `.git`? branch, commit count, remote (host only), clean or dirty. AUDIT-0005 said it was `git init`-ed and never committed — confirm per path.
3. **What is actually in it besides venvs**: counts by type (`.py .ipynb .md .toml .xlsx .csv`), and its `CLAUDE.md` / `.claude/agents` / `.claude/commands` names only. Anything that looks like data pulled from paid sources (FMP/WRDS) — note size, do not open.
4. **Is anything unique to it?** For each non-venv file, does a same-named file exist elsewhere under `~/Projects/Finance` (outside `finance-python`)? Report counts; list names if under 30.
5. **References outside the directory.** Paths only, never contents:
   - `~/.claude/projects/` entries whose names contain `finance-python` (these are Claude Code session/state dirs — regenerable).
   - Files under `~/.claude/projects/-Users-michaelgrigorian/memory/` that mention `finance-python` (`grep -l`, names only).
   - `~/.claude/CLAUDE.md` and `~/AGENTS.md`: lines mentioning `finance-python` (quote the lines; they are instructions, not secrets).
   - VS Code: `~/Library/Application Support/Code/User/globalStorage/storage.json` and `workspaceStorage/*/workspace.json` entries containing `finance-python` (count and paths only).
   - Warp / shell: `~/.zsh_history` — count of lines containing `finance-python` only, never the lines.
6. **The conventions pointer**, since it is in the same files: confirm `~/Projects/Finance/Active/MODELING_CONVENTIONS.md` is absent and `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md` is present (size, mtime), plus the root copy (path, mtime). Do not open them.

## Report
`docs/audit/2026-09-09-finance-python-inventory.md` — `id: AUDIT-0006`, `type: report`, `status: final`, `handoff: HANDOFF-0017`, `author: claude-code`, `source: fetched`, `tier: 2`, `created:`. Sections 1–6, then a **"Disposal recommendation"** with three lists: (a) delete outright (venvs, caches, stale Claude Code state dirs — all regenerable); (b) archive to `~/Archive/finance-python-2026-09/` with a `sha256` manifest before deletion (anything unique: code, notebooks, notes); (c) references to clean (which files, which lines), noting that `~/.claude/CLAUDE.md`, `~/AGENTS.md`, and the memory tree are **shown-diff-then-approve** edits, and VS Code's recent list is Michou's to clear in the UI. Then write a **proposed** handoff `docs/handoff/proposed/<today>-finance-python-disposal.md` (`id: HANDOFF-0018`, `status: proposed`) doing (c) → (b) → (a), with the final `rm` of the archive gated on a completed Time Machine backup. Scope the proposal to the located disposal unit and its outside references only — it must not touch any other file under `~/Projects/Finance` or anywhere else. If the loose files are a verbatim copy of the FinanceToolkit package (compare a few against `pip download financetoolkit` metadata or the file headers), say so: that makes them regenerable and moves them from list (b) to list (a).

Set this handoff `status: done` with `completed:`. Three sentences to Michou: how many `finance-python` locations exist and which one is real; whether anything in it is unique; how many outside references point at it.
