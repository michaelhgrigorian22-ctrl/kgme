---
id: AUDIT-0005
type: report
status: final
handoff: HANDOFF-0014
author: claude-code
source: fetched
tier: 2
created: 2026-09-09T23:25:00-07:00
---

# Finance folder inventory (read-only) - 2026-09-09

Read-only survey of `~/Projects/Finance` per HANDOFF-0014. Nothing inside the folder was created, moved, or deleted. All counts are from `find`, `du`, and `stat` run at about 23:15 on 2026-09-09; sizes labelled "on disk" are `du`, sizes labelled "apparent" are summed `stat` byte counts. The folder holds **28,071 files, 1.8 GB on disk**, matching the audit figure.

## 1. Top-level tree to depth 3

Depth 1 (files, on-disk size):

| Directory | Files | Size |
|---|---:|---:|
| `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/` | 27,715 | 1.5 GB |
| `Archive/` | 329 | 203 MB |
| `Active/` | 21 | 9.0 MB |
| `Resources - Academic /` (trailing space in the name) | 4 | 80 MB |
| root files: `MODELING_CONVENTIONS.md` (14.6 KB), `.DS_Store` | 2 | |

Depth 2, all directories (files, on-disk size):

| Directory | Files | Size |
|---|---:|---:|
| `ARCHIVE PITCHES…/finance-python` | 24,747 | 913 MB |
| `ARCHIVE PITCHES…/equity-quicktester` | 2,596 | 55 MB |
| `Archive/Daily Clips` | 102 | 2.8 MB |
| `ARCHIVE PITCHES…/ALBEMARLE ` | 88 | 212 MB |
| `ARCHIVE PITCHES…/REDDIT` | 81 | 47 MB |
| `ARCHIVE PITCHES…/CLOUDFLARE` | 79 | 159 MB |
| `Archive/ALTRIA` | 42 | 9.2 MB |
| `ARCHIVE PITCHES…/MRVL` | 40 | 71 MB |
| `Archive/TBBB` | 40 | 12 MB |
| `ARCHIVE PITCHES…/COWORK MODELING ` | 30 | 22 MB |
| `Archive/0001418135-25-000013-xbrl` | 26 | 9.3 MB |
| `ARCHIVE PITCHES…/MELI` | 21 | 5.9 MB |
| `Archive/FNMA CLIPS from SAM ` and `…__1` (two copies) | 8 + 8 | 408 KB each |
| `ARCHIVE PITCHES…/INSTACART ` | 8 | 3.1 MB |
| `ARCHIVE PITCHES…/TAKETWOINTERACTIVE` | 7 | 524 KB |
| `Archive/3SM Template ` | 5 | 672 KB |
| `ARCHIVE PITCHES…/$DMART ` | 5 | 348 KB |
| `Active/tmp` | 4 | 1.2 MB |
| `Active/thesis` | 4 | 56 KB |
| `ARCHIVE PITCHES…/claude valuation books ` | 4 | 19 MB |
| `ARCHIVE PITCHES…/BJ_WHOLESALE ` | 2 | 172 KB |

Depth 3, the directories that matter (top by file count): `finance-python/.venv` 24,609 files / 906 MB; `equity-quicktester/.venv` 2,510 / 54 MB; `ALBEMARLE /ALBEMARLE PITCH` 53 / 5.5 MB; `finance-python/src` 47 / 572 KB; `equity-quicktester/quicktests` 44 / 532 KB; `REDDIT/RDDT_ARCHIVES` 41 / 17 MB; `CLOUDFLARE/NET filings` 26 / 58 MB; `finance-python/notebooks` 25 / 5.3 MB; `CLOUDFLARE/memo resources` 18 / 95 MB; `CLOUDFLARE/NET archive model versions` 17 / 3.7 MB; `finance-python/.git` 19 / 80 KB; `finance-python/.claude` 14 / 60 KB. Nine top-level or depth-2 directory names carry a trailing space or a `$`; AUDIT-0001 finding 9 and proposed HANDOFF-0011 already cover this.

## 2. Where the 28,071 files are

Regenerable content, by directory (non-nested, so the `.venv` figures include their `site-packages` and `__pycache__`):

| Path | Files | Size |
|---|---:|---:|
| `finance-python/.venv` (Python 3.13; `site-packages` alone is 24,027 files / 850 MB) | 24,609 | 906 MB |
| `equity-quicktester/.venv` (Python 3.13) | 2,510 | 54 MB |
| `finance-python/.git` (empty repository, see §5) | 19 | 80 KB |
| `finance-python/.ruff_cache`, `equity-quicktester/.ruff_cache`, `equity-quicktester/.pytest_cache` | 18 | 72 KB |
| `__pycache__` directories outside the venvs (8 of them) | 36 | small |
| `.DS_Store` files | 27 | small |
| **Total regenerable** | **27,219** | **862 MB apparent, about 960 MB on disk** |

So **97.0% of the file count** (27,219 of 28,071) and roughly half the bytes are two `uv` virtual environments plus caches. No `node_modules` exists. Two further items are regenerable in a weaker sense: `Archive/0001418135-25-000013-xbrl` (26 files, 9.3 MB) is the Keurig Dr Pepper FY2024 10-K XBRL package straight from EDGAR, and `equity-quicktester/quicktests/raw_cache` (38 JSON files) is an API response cache. Both are re-fetchable, but they are listed under §3 for a keep-or-drop decision rather than deleted outright.

What is left after removing the regenerable set: **852 files, 836.5 MB apparent.**

## 3. Human work product

Counting `*.xlsx *.xlsm *.docx *.pdf *.pptx *.md *.ipynb *.py *.R`, excluding the regenerable paths above:

| Directory | xlsx | docx | pdf | pptx | md | ipynb | py | R | Files | Size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/` | 124 (31.8 MB) | 34 (1.2) | 108 (491.7) | 6 (7.4) | 43 (0.6) | 5 (1.0) | 48 (0.4) | 1 | 369 | 534.1 MB |
| `Archive/` | 85 (26.8) | 137 (3.9) | 39 (73.8) | 8 (82.6) | 3 (0.1) | | | | 272 | 187.2 MB |
| `Active/` | 2 (0.0) | 6 (0.2) | 3 (7.5) | 2 (0.0) | 3 (0.1) | | | | 16 | 7.8 MB |
| `Resources - Academic /` | 1 (0.1) | | 3 (79.9) | | | | | | 4 | 80.0 MB |
| root (`MODELING_CONVENTIONS.md`) | | | | | 1 | | | | 1 | 0.0 MB |
| **Total** | 212 | 177 | 153 | 16 | 50 | 5 | 48 | 1 | **662** | **809.0 MB** |

No `.xlsm` files exist. Three qualifications on the table:

- **36 legacy `.xls` files** fall outside the handoff's pattern: 15 under `Archive/` (10 at its root, 3 in `TBBB`, 2 in `ALTRIA`) and 21 under the pitch folders (14 of them in `CLOUDFLARE/NET filings` and `CLOUDFLARE/valuation tools`, the rest one each in TAKETWO, REDDIT (2), MELI, INSTACART, ALBEMARLE, $DMART). These look like Capital IQ or EDGAR financial exports and are treated as work product in the disposal plan.
- **The remaining 154 non-pattern, non-regenerable files** (27.5 MB) are: 41 JSON (38 of them the `raw_cache` above), 36 `.xls`, 20 PNG (memo-template page renders, notebook exports, an RStudio viewer cache), 13 HTM (the XBRL package), 8 JPG, 5 RData, 4 CSV, plus a handful of config files (`pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`, `.env.example`, two `.qmd`).
- **`Active/` is smaller than it looks.** Of its 21 files, 6 are Office lock files (`~$…` prefixes for `ALBDECK_FINAL.pptx`, `ALB_Pitch_Deck_FINAL.pptx`, `Home Depot 3 Statement Model - Final copy.xlsx`, `Citrindex_Holdings_Weights_April_26_2026.xlsx`, `WO_Long_Thesis.docx`, and a week-3 notes file) whose parent documents are no longer in `Active/`, and 4 are PNG page renders under `tmp/`. The real content is `thesis/` (4 files, the most recently edited material in the whole folder), `MODELING_CONVENTIONS_V2.md`, `STE100_WRITING_STANDARD_AGENT_READY.md`, two internship notes documents, `memo_template.pdf`, `writing standard.pdf`, and the Wolfe Research 10-K navigation guide.

The pitch archive's 491.7 MB of PDFs (108 files) is the single largest block of bytes and is mostly source filings and broker research (`CLOUDFLARE/memo resources` alone is 95 MB, `NET filings` 58 MB). These are re-downloadable in principle but are the analyst's curated reading set, so they are kept in the archive plan.

## 4. References from outside the folder

`grep -rIl "Projects/Finance" ~/.claude ~/AGENTS.md ~/Projects/Automate` returned 36 paths. Grouped:

- **Instruction files that name the folder (must change before disposal).** `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16 (identical text) declare `~/Projects/Finance/Active/MODELING_CONVENTIONS.md` authoritative for all model construction. **That path does not exist.** Two candidates do: `~/Projects/Finance/MODELING_CONVENTIONS.md` at the folder root (14,588 bytes, modified 2026-06-18) and `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md`. The pointer has been dangling since at least the `Active/` reorganisation; every Claude Code session on this machine currently loads a rule that points at nothing.
- **Claude Code project state.** `~/.claude/projects/-Users-michaelgrigorian-Projects-Finance-Active-finance-python/` (380 KB of session transcripts and subagent logs) and `~/.claude/projects/-Users-michaelgrigorian-finance-python/` (8 KB). `~/.claude.json` holds a project entry keyed `/Users/michaelgrigorian/Projects/Finance/Active/finance-python`, a path that also no longer exists (the project now lives under `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python`). Five `~/.claude/backups/.claude.json.backup.*` files carry the same key.
- **Claude Code memory (Tier 2 notes, human-relevant).** `~/.claude/projects/-Users-michaelgrigorian/memory/`: `MEMORY.md`, `home_layout.md`, `user_profile.md`, `project_equity_quicktester.md`, `fmp_plan_and_api.md`, and `decisions/adr/ADR-0001-phase0-brain-audit.md` all mention the folder.
- **This repository (data, not pointers).** `docs/audit/2026-09-09-machine-audit.md`, `docs/audit/2026-09-09-global-claude-config.md`, `docs/handoff/proposed/2026-09-09-rename-space-paths.md`, and HANDOFF-0014 itself. These describe the folder and need no edit; HANDOFF-0011 (rename paths with spaces) does list Finance directories and would be partly mooted by disposal.
- **Transcripts, file history, shell snapshots** (the remaining ~20 hits) are append-only session records under `~/.claude/` and are left alone.

## 5. Git repositories inside the folder

Exactly one: `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/.git`.

| Property | Value |
|---|---|
| Branch | unborn `HEAD` (`git rev-parse HEAD` fails: no commits) |
| Commits | 0 |
| Remote | none |
| Working tree | 14 untracked entries: everything (`src/`, `notebooks/`, `scripts/`, `tasks/`, `data/`, `.claude/`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`, `.env.example`, `.DS_Store`) |

`git init` was run and nothing was ever committed, so the `.git` directory itself carries no history and is regenerable junk, while the working tree (47 files in `src/`, 25 in `notebooks/`, plus scripts and tasks) exists **nowhere else in version control**. `equity-quicktester` has no `.git` at all. Both code projects are therefore unique data by the handoff's definition. No `.git` files (worktrees or submodules) exist.

## 6. Duplication check

349 unique `*.xlsx` / `*.pdf` basenames exist in the folder (regenerable paths excluded). Matched by filename against the locations named in the handoff, plus three obvious extras:

| Location | Present? | xlsx/pdf names there | Matches |
|---|---|---:|---:|
| `~/OneDrive - Claremont McKenna College` | directory exists, **0 files** (empty mount point) | 0 | 0 |
| `~/Library/CloudStorage/OneDrive-ClaremontMcKennaCollege` | yes, 41 files | 12 | 0 |
| `~/Archive` (Desktop, Documents, Zoom sub-folders) | yes, 75 files | 8 | 0 |
| Box (`~/Box`, `~/Library/CloudStorage/Box-Box`) | absent | | |
| `~/Documents` (extra) | yes | 19 | **5** |
| iCloud Drive (extra) | yes | 62 | **1** |
| `~/Downloads` (extra) | yes | 13 | 0 |

The six matches, all workbooks: in `~/Documents`, `Cloudflare_finalmodel_FINAL.xlsx`, `TBBB_MODEL_calibrated_v2.xlsx`, `TBBB_MODEL_V1.xlsx`, `TBBB_MODEL_v5_3SM_reverseDCF.xlsx`, `TBBB_uncalibrated.xlsx`; in iCloud Drive, `CART MODEL FINAL .xlsx`. Filename equality does not prove content equality; the archive manifest in HANDOFF-0016 records `sha256` so this can be settled then. Conclusion: **343 of 349 workbook and PDF names exist only inside `~/Projects/Finance`.** The pitch documents are not mirrored to OneDrive, Box, or `~/Archive`.

## 7. Newest modification times

Excluding `.DS_Store` and regenerable paths, the ten newest files:

| Modified | File |
|---|---|
| 2026-09-08 18:08 | `ARCHIVE PITCHES…/MRVL/NASDAQ_MRVL _Final Model and Valuation_MichaelGrigorian (1).xlsx` |
| 2026-09-07 11:16 | `Active/thesis/thesis-one-pager-simple.docx` |
| 2026-09-04 18:04 | `Active/thesis/thesis-one-pager-ai-costs.docx` |
| 2026-09-03 14:27 | `Active/thesis/thesis-one-pager.docx` |
| 2026-08-31 16:14 | `Active/thesis/thesis-topic-proposals.md` |
| 2026-08-30 15:35 | `ARCHIVE PITCHES…/REDDIT/heavy.docx` |
| 2026-07-28 08:15 | `ARCHIVE PITCHES…/REDDIT/REDDIT_MEMO_FINAL_7-24.docx` |
| 2026-07-24 17:01 | `ARCHIVE PITCHES…/REDDIT/RDDT_HOLD_concise.md` |
| 2026-07-24 16:58 | `Active/tmp/pdfs/memo_template/page-*.png` (4 files) |

Oldest content: `Archive/Daily Clips/1.21.25 H4U Clips.docx`, 2025-01-21. The folder spans about 19.5 months. **"Outdated" holds for the bulk but not for all of it:** the MRVL valuation workbook was touched yesterday and the four `Active/thesis/` files within the last nine days. Those five files should be confirmed as either finished or relocated before the folder is treated as closed.

## Disposal recommendation

**(a) Regenerable, delete outright with zero loss.** 27,219 files, about 960 MB on disk: the two `.venv` directories (both rebuildable with `uv sync` from the `pyproject.toml` and `uv.lock` that sit beside them), the empty `finance-python/.git`, the `.ruff_cache` and `.pytest_cache` directories, the 8 stray `__pycache__` directories, 27 `.DS_Store` files, and the 6 Office lock files in `Active/`. Optionally also the KDP XBRL package (26 files, 9.3 MB, re-fetchable from EDGAR by accession `0001418135-25-000013`) and `quicktests/raw_cache` (38 JSON, re-fetchable); the plan archives these two rather than deleting them because they cost 10 MB and their deletion cannot be undone without a network fetch.

**(b) Unique human work product, archive with a manifest before anything is deleted.** The 852 non-regenerable files (836.5 MB apparent), which is the 662 pattern files plus the 36 `.xls`, the `finance-python` and `equity-quicktester` source trees and configs, notebooks, exports, and the two caches above. Concretely: everything under `~/Projects/Finance` except the paths listed in (a), moved to `~/Archive/finance-2026-09/` preserving the directory structure, with `MANIFEST.sha256` (one `sha256` per file, generated before the move and verified after it) and a `README.md` recording the source path, date, and this report's id. The `finance-python` working tree is the highest-value item because it has never been committed anywhere; the MRVL workbook and `Active/thesis/` are the most recent.

**(c) Outside the folder, update first.** (1) `~/.claude/CLAUDE.md` line 16 and `~/AGENTS.md` line 16: the `MODELING_CONVENTIONS.md` pointer is already broken and must be repointed to wherever the conventions will live after disposal (candidates: the root copy or `Active/MODELING_CONVENTIONS_V2.md`, Michou chooses which is current; the natural new home is inside this repository or the Tier 2 memory tree, not `~/Archive`). (2) `~/.claude.json` project entry `/Users/michaelgrigorian/Projects/Finance/Active/finance-python` and the two `~/.claude/projects/-Users-michaelgrigorian-…finance-python/` state directories: already orphaned by the earlier move; leave the transcripts (append-only record) but note that no session will find them by path. (3) The six memory notes under `~/.claude/projects/-Users-michaelgrigorian/memory/` that name the folder: `home_layout.md` and `project_equity_quicktester.md` state paths as fact and need a one-line correction each; the others mention it in passing. (4) Proposed HANDOFF-0011 should be re-scoped after disposal, since most of the paths with spaces it targets will have moved to `~/Archive/finance-2026-09/`.

The proposed handoff that carries out (c), then (b), then (a), with deletion of the archive gated on `tmutil latestbackup`, is `docs/handoff/proposed/2026-09-09-finance-folder-disposal.md` (HANDOFF-0016).
