---
id: AUDIT-0006
type: report
status: final
handoff: HANDOFF-0017
author: claude-code
source: fetched
tier: 2
created: 2026-09-10T09:20:00-07:00
---

# finance-python inventory (read-only) - 2026-09-10

Read-only survey per HANDOFF-0017, which re-scopes disposal from all of `~/Projects/Finance` (kept, untouched) to the old `finance-python` project only. Nothing was created, moved, or deleted. Counts from `find`, `du`, `stat`, `git`, and `mdfind` run between 09:05 and 09:15 on 2026-09-10. The `timeout` utility does not exist on this Mac; one early search batch silently failed on it and was re-run without it, so every figure below comes from a search that actually executed.

## 0. Locate

`find ~ -maxdepth 8` (pruning `~/Library`, `~/.Trash`, venvs, `node_modules`, `~/.nvm`, `~/.cache`, `site-packages`), `find ~/Library ~/.cache ~/.nvm ~/.local -maxdepth 9`, the cloud mounts, and `mdfind` (Spotlight indexing is enabled on `/`) agree on the following. `~/.Trash` cannot be listed by this session (`Operation not permitted`, a TCC restriction); it was not searched.

| Hit | What it is | In disposal unit? |
|---|---|---|
| `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/` | the project: `CLAUDE.md`, `.claude/`, `src/`, `notebooks/`, `.venv` | **yes, this is the unit** |
| `…/finance-python/src/finance_python/` | the underscore folder Michou saw: the project's own package | yes (inside the unit) |
| `~/Reference/FinanceToolkit/` | git clone of `github.com/JerBouma/FinanceToolkit`, branch `main`, 1 commit (shallow), clean, no local changes; 828 files, 81 MB | no (reported only) |
| `~/Reference/OpenBB/` | git clone of `github.com/OpenBB-finance/OpenBB`, branch `develop`, 1 commit (shallow), clean; 2,218 files, 342 MB | no (reported only) |

No directory named `finance-python`, `finance_python`, or `financetoolkit` exists anywhere else: not under `~/Library`, `~/.cache` (the `uv` cache holds no such package), `~/.nvm`, `~/.local`, iCloud Drive, or OneDrive. `~/Downloads/finance-python`, `~/finance-python`, and `~/Projects/Finance/Active/finance-python` do not exist; they survive only as stale entries in VS Code and Claude Code state (§5).

**The Finder view was a search result, not a folder.** Every loose file Michou listed resolves to one of the two reference clones, and the two folders in the same view are the project and its package:

| File in the Finder view | Actual location |
|---|---|
| `error_model.py` | `~/Reference/FinanceToolkit/financetoolkit/utilities/` |
| `euribor_model.py` | `~/Reference/FinanceToolkit/financetoolkit/fixedincome/` |
| `evar_model.py` | `~/Reference/FinanceToolkit/financetoolkit/risk/` |
| `fixedincome_controller.py` | `~/Reference/FinanceToolkit/financetoolkit/fixedincome/` |
| `fmp_model.py` | `~/Reference/FinanceToolkit/financetoolkit/` |
| `Finance Toolkit - 0. README Examples.ipynb` | `~/Reference/FinanceToolkit/examples/` |
| `etf_info.py` | `~/Reference/OpenBB/openbb_platform/…/` (five copies, one per provider) |
| `famafrench_router.py` | `~/Reference/OpenBB/openbb_platform/providers/famafrench/openbb_famafrench/` |
| `examples.md` | `~/Reference/OpenBB/openbb_platform/obbject_extensions/charting/` |
| `exposure.py` | `…/finance-python/src/finance_python/themes/` (the only one of the ten that is his) |
| `finance_python/` | `…/finance-python/src/finance_python/` |
| `finance-python/` | `…/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/` |

No directory contains those ten files together, so there is no second disposal unit. The two `~/Reference` clones are upstream open-source code with zero local commits and clean trees; they are regenerable with `git clone` and are outside this handoff's scope.

## 1. Directories

| Candidate | Exists | Files | `du -sh` | Newest content mtime |
|---|---|---:|---:|---|
| `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python` | yes | 24,747 | 913 MB | `tasks/todo.md`, 2026-05-13 18:50 (newest file of any kind is a `.DS_Store` written 2026-09-10 09:02 by Finder browsing) |
| `~/Projects/Finance/Active/finance-python` | **no** | | | |
| `~/finance-python` | **no** | | | |
| `~/Downloads/finance-python` (from VS Code history) | **no** | | | |

Of AUDIT-0005's two virtual environments, **one is inside the unit**: `finance-python/.venv` (Python 3.13, 24,609 files, 906 MB, of which `site-packages` is 24,027 files / 850 MB). The other, `equity-quicktester/.venv` (2,510 files, 54 MB), belongs to the sibling project `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/equity-quicktester/` and is **out of scope**. So the unit accounts for 24,747 of AUDIT-0005's 28,071 files and 913 MB of its 1.8 GB. The project has not been worked on since 2026-05-13, just under four months.

## 2. Git

One `.git`, at the unit root. Branch: unborn `HEAD` (`git rev-parse HEAD` fails, "unknown revision"). Commits: 0. Remote: none. Working tree: 14 untracked entries, which is everything (`src/`, `notebooks/`, `scripts/`, `tasks/`, `data/`, `.claude/`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`, `.env.example`, `.DS_Store`). AUDIT-0005 §5 is confirmed: `git init` was run and nothing was ever committed. The `.git` directory (19 files, 80 KB, all of it default hook samples and an empty object store) carries no history. No other `.git` exists inside the unit, and `src/finance_python` is a plain package directory, not a nested repository.

## 3. Contents besides the venv

Files outside `.venv`, by extension: 34 `.py`, 22 `.pyc` (in eight `__pycache__` directories), 20 `.md`, 14 `.sample` (git hook templates in `.git/hooks`), 6 `.png`, 5 `.ipynb`, 3 `.gitignore`, 2 `.pptx` (one is an Office lock file `~$…`), 2 `.gitkeep`, 1 each of `.xlsx`, `.csv`, `.pkl`, `.json`, `.html`, `.toml`, `.lock`, `.example`, `.tag` (`.ruff_cache/CACHEDIR.TAG`), `.python-version`, and one extension-less file `notebooks/Pitch_2 /Rev Machine`.

Layout of the human-authored part:

- `src/finance_python/`: 22 modules in `alb/` (`model.py`, `valuation.py`, `valuation_excel.py`, `data.py`, `wrds_data.py`, `charts.py`, `theme.py`), `models/` (`dcf.py`, `comps.py`, `wacc.py`, `base.py`), `data/edgar.py`, `themes/` (`registry.py`, `exposure.py`, `customer_concentration.py`, `base.py`), `utils/`, `viz/`.
- `notebooks/`: `ALB/` (four notebooks `00_thesis` to `03_valuation`, `build_deck.py`, `ALB_Long_Pitch_v1_DRAFT.pptx`, `02_pitch_charts.html`, six exported chart PNGs), `toolkit/` (six numbered scripts `01_edgar_fetch.py` to `06_pipeline.py` plus `README.md`), `Pitch_2 /` (`Practice for Revenue machine.xlsx`, `Rev Machine`), `INTRO_PYTHON.ipynb`.
- `scripts/`: `smoke_test_models.py`, `smoke_test_themes.py`, `smoke_test_edgar.py`, `screen_photonic_energy.py`.
- `tasks/`: `todo.md`, `AUDIT.md`, `lessons.md`, `coverage.md`.
- Root: `CLAUDE.md` (2,519 bytes), `README.md` ("Personal Python environment for fundamental L/S equity research, portfolio tracking, commodity fundamentals (metals + gases), and light derivatives modeling"), `pyproject.toml`, `uv.lock`, `.python-version` (3.13), `.gitignore`, `.env.example`.

`.claude/` (names only): `settings.json`; agents `quant-analyst`, `edgar-researcher`, `model-builder`; rules `python-style`, `modeling-standards`, `data-conventions`; skills `find-exposure`, `build-comps`, `pull-filings`, `run-dcf`, `earnings`, `screen`, `analyze`. No `commands/` directory.

**Paid-source data.** `data/` holds two files: `data/cache/edgar/MOD_10k_latest.pkl` (164 KB, an EDGAR cache, free source) and `data/outputs/screens/screen_photonic_energy_20260509.csv` (13.5 KB, a screen output). `data/.gitignore` says data files "may contain licensed data", and `pyproject.toml` declares the `wrds` package and `src/finance_python/alb/wrds_data.py` exists, but **no WRDS or FMP data file is present**. No `.env` exists, only `.env.example`; nothing was opened.

**Not a FinanceToolkit copy.** The unit's modules (`dcf`, `comps`, `wacc`, `edgar`, `themes/*`, `alb/*`) share no filename with the FinanceToolkit package, and FinanceToolkit is not installed in the venv (`site-packages/financetoolkit` absent). The FinanceToolkit and OpenBB code on this machine lives solely in the `~/Reference` clones. Nothing in list (b) below moves to list (a) on that basis.

## 4. Uniqueness

64 distinct basenames exist outside the regenerable set. Six also appear elsewhere under `~/Projects/Finance`, all in `equity-quicktester/` and all generic scaffolding: `__init__.py`, `.env.example`, `.gitignore`, `pyproject.toml`, `README.md`, `uv.lock`. **58 of 64 names are unique to the unit**, including every source module, notebook, task note, agent, rule, and skill. `ALB_Long_Pitch_v1_DRAFT.pptx` has no same-named twin, but the `ALBEMARLE ` folder holds `ALB_Pitch_Deck.pptx`, `ALBDECK_FINAL.pptx`, `ALBDECK_FINAL [Autosaved].pptx`, and `ALBDECKOLD.pptx`; the draft in the unit is by name an earlier version of that deck, kept in the archive set in case it is not.

## 5. References outside the directory (paths only)

- **Claude Code state, `~/.claude/projects/`:** two directories. `-Users-michaelgrigorian-Projects-Finance-Active-finance-python/` (380 KB, 5 files: one session transcript and two subagent transcripts with their `.meta.json`), regenerable. `-Users-michaelgrigorian-finance-python/` (8 KB, 2 files: `memory/MEMORY.md` and `memory/feedback_pitch_process.md`). **The second is not a transcript but a project-scoped memory note written during a session in the long-gone `~/finance-python` location; it may hold guidance Michou gave and is treated as archive material, not junk.**
- **`~/.claude.json`:** two project keys, `/Users/michaelgrigorian/finance-python` and `/Users/michaelgrigorian/Projects/Finance/Active/finance-python`, both dangling.
- **Memory tree `~/.claude/projects/-Users-michaelgrigorian/memory/`, seven files mention `finance-python`:** `home_layout.md`, `user_profile.md`, `project_equity_quicktester.md`, `decisions/adr/ADR-0001-phase0-brain-audit.md`, `decisions/adr/ADR-0002-phase1-claude-md-rewrite.md`, `decisions/adr/ADR-0003-phase2-memory-restructure.md`, `lessons/validate-comps-peer-set.md`.
- **`~/.claude/CLAUDE.md` and `~/AGENTS.md`:** zero lines mention `finance-python`. Both carry, at line 16, the conventions pointer quoted in §6.
- **VS Code:** `globalStorage/storage.json` has 3 entries: `file:///Users/michaelgrigorian/Downloads/finance-python`, `file:///Users/michaelgrigorian/finance-python`, `file:///Users/michaelgrigorian/Projects/Finance/Active/finance-python`. `workspaceStorage/` has 3 matching directories (`6a2b70f3…`, `80682a54…`, `dc6ca7fa…`), one per historical path. All three paths are dead; the current path was never opened in VS Code under this name.
- **Shell:** `~/.zsh_history` contains 37 lines mentioning `finance-python` (count only).

Taken together: the project has lived at four paths (`~/Downloads/finance-python` → `~/finance-python` → `~/Projects/Finance/Active/finance-python` → the present archive folder), and every external reference points at one of the three dead ones.

## 6. The conventions pointer

`~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 (identical): "`~/Projects/Finance/Active/MODELING_CONVENTIONS.md` is authoritative for all model construction; conflicts with any other instruction file resolve in its favor." Confirmed: `~/Projects/Finance/Active/MODELING_CONVENTIONS.md` is **absent**. Present, not opened: `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md` (28,756 bytes, modified 2026-07-22 09:54) and the root copy `~/Projects/Finance/MODELING_CONVENTIONS.md` (14,588 bytes, modified 2026-06-18 13:24). A third copy, `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/MRVL/MODELING_CONVENTIONS copy.md`, also exists. V2 is twice the size and five weeks newer than the root copy, which suggests it is the current one; that is Michou's call.

## Disposal recommendation

**(a) Delete outright, all regenerable.** Inside the unit: `.venv` (24,609 files, 906 MB; rebuilt by `uv sync` from `pyproject.toml` and `uv.lock`), `.git` (19 files, 80 KB, zero commits), `.ruff_cache` (40 KB), eight `__pycache__` directories (22 `.pyc`), `.DS_Store` files, and the Office lock file `notebooks/ALB/~$ALB_Long_Pitch_v1_DRAFT.pptx`: 24,667 files in all. Outside the unit: the Claude Code transcript directory `~/.claude/projects/-Users-michaelgrigorian-Projects-Finance-Active-finance-python/` (380 KB) and the three VS Code `workspaceStorage` directories (VS Code recreates them; the recent-list entries in `storage.json` are cleared from the UI, see (c)).

**(b) Archive to `~/Archive/finance-python-2026-09/` with a `sha256` manifest before any deletion.** The 80 remaining files, 6.16 MB: all of `src/`, `notebooks/`, `scripts/`, `tasks/`, `data/` (two files), `.claude/`, and the root files (`CLAUDE.md`, `README.md`, `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `.env.example`). Plus, from outside the unit, the two memory files in `~/.claude/projects/-Users-michaelgrigorian-finance-python/memory/`. Everything in this list is unique on this machine (§4) and was never committed anywhere (§2). At 6 MB the archive is trivial; the venv was 99.3% of the bytes.

**(c) References to clean.** Shown-diff-then-approve edits (ADR-004): `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 (repoint the conventions rule to whichever file Michou names current; no `finance-python` mention to remove); memory notes `home_layout.md` and `project_equity_quicktester.md` (state the archive path; the three ADRs and the lesson are historical records and stay as written). Machine state that can simply be removed once the archive is verified: the two dangling project keys in `~/.claude.json` (a JSON edit, shown first), the transcript directory above, and the `-Users-michaelgrigorian-finance-python/` directory after its two memory files are archived. Michou's own, in the UI: VS Code's three dead entries in the "Open Recent" list (`storage.json` is rewritten by VS Code and should not be hand-edited), and, if he wants, the 37 `~/.zsh_history` lines, which are harmless and are left alone by the proposal.

The proposed handoff carrying out (c) → (b) → (a), gated on a completed Time Machine backup for the final removal, is `docs/handoff/proposed/2026-09-10-finance-python-disposal.md` (HANDOFF-0018).
