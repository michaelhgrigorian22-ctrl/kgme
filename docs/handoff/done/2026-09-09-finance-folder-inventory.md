---
id: HANDOFF-0014
type: handoff
created: 2026-09-09T22:00:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-09T23:32:00-07:00
report: docs/audit/2026-09-09-finance-inventory.md
tier: 2
depends_on: HANDOFF-0001
---

# Handoff 0014 — Inventory `~/Projects/Finance` before disposal (read-only)

Michou has decided `~/Projects/Finance` is outdated and wants it gone. The charter does not allow an irreversible delete of 28,071 files with no backup in place (Time Machine is not yet configured — proposed HANDOFF-0006). So the disposal happens in two moves: **inventory now (this handoff, read-only), then archive-and-remove as a separate proposal**, with true deletion only after a backup exists. **Change nothing here.**

## Collect
1. Top-level tree of `~/Projects/Finance` to depth 3: for each directory, file count and `du -sh`.
2. Where the 28,071 files actually are: count files per directory at depth 2, sorted descending; identify caches, virtual environments, `node_modules`, `__pycache__`, `.git`, `.venv`, data dumps. These are regenerable and are the likely bulk.
3. Human work product: count and total size of `*.xlsx *.xlsm *.docx *.pdf *.pptx *.md *.ipynb *.py *.R` by directory. These are the files that might be worth keeping.
4. Anything referenced from outside the folder: `grep -rIl "Projects/Finance" ~/.claude ~/AGENTS.md ~/Projects/Automate 2>/dev/null` (paths only). The audit already knows the global `~/.claude/CLAUDE.md` names `~/Projects/Finance/Active/MODELING_CONVENTIONS.md` as authoritative — confirm whether that file exists.
5. Git repositories inside the folder (any depth): path, branch, whether a remote exists (host part only), and whether the working tree is clean. An unpushed repo is unique data.
6. Duplication check: do the same pitch documents also exist under `~/OneDrive - Claremont McKenna College`, `~/Library/CloudStorage`, Box, or `~/Archive`? Compare by filename for the `*.xlsx` and `*.pdf` set; report matches as counts, not lists, unless under 20.
7. Newest modification time in the folder (`find … -type f -newer` or `stat`), to confirm "outdated".

## Report
`docs/audit/2026-09-09-finance-inventory.md` — frontmatter `id: AUDIT-0005`, `type: report`, `status: final`, `handoff: HANDOFF-0014`, `author: claude-code`, `source: fetched`, `tier: 2`, `created:`. Sections 1–7, then **"Disposal recommendation"** in three parts: (a) what is regenerable and can be deleted outright with zero loss; (b) what is unique human work product and should be moved to `~/Archive/finance-2026-09/` with a manifest (`sha256` per file) before anything is deleted; (c) what outside the folder must be updated first (global CLAUDE.md pointers, `~/AGENTS.md`, Claude Code project state under `~/.claude/projects/`). Then write a **proposed** handoff `docs/handoff/proposed/<today>-finance-folder-disposal.md` (`id: HANDOFF-0016`, `status: proposed`) that carries out (c) → (b) → (a) in that order, with deletion of the archive itself explicitly gated on `tmutil latestbackup` succeeding.

Set this handoff `status: done` with `completed:`. Tell Michou in three sentences: how much of the 1.8 GB is regenerable junk, how much is his own work product, and whether anything in there is unpushed or otherwise unique.
