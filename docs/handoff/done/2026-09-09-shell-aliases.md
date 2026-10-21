---
id: HANDOFF-0015
type: handoff
created: 2026-09-09T22:00:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-09T23:20:00-07:00
report: docs/audit/2026-09-09-machine-audit.md
tier: 2
depends_on: HANDOFF-0002
---

# Handoff 0015 — Shell aliases so agents launch from the repo, never from `$HOME`

Michou wants Codex (and Claude Code) to live in `~/Projects/Automate` by default. Launching from `$HOME` made Codex inherit `~/AGENTS.md` and wander into Claude Code's memory (AUDIT-0002 §4). The fix is a habit made mechanical.

## Steps
1. Back up: `cp ~/.zshrc ~/.zshrc.bak.$(date +%Y%m%d)` (create `~/.zshrc` if absent).
2. Append this block, verbatim, to `~/.zshrc`:
   ```
   # KGME — always work from the repo (HANDOFF-0015)
   export KGME_HOME="$HOME/Projects/Automate"
   alias kgme='cd "$KGME_HOME"'
   alias kgme-claude='cd "$KGME_HOME" && claude'
   alias kgme-codex='codex --cd "$KGME_HOME"'
   alias kgme-codex-exec='codex --cd "$KGME_HOME" exec'
   ```
3. `source ~/.zshrc`, then verify: `type kgme-codex` prints the alias; `kgme && pwd` prints the repo path.
4. Check Warp: if Warp has a "launch configuration" or default starting directory setting, report where it is (do not change it) so Michou can point new tabs at `$KGME_HOME` himself.

## Reversibility
Delete the block from `~/.zshrc` (or restore the backup). Nothing else is touched.

## Do not
Modify `~/.codex/config.toml`, `~/.claude/settings.json`, Warp settings, or anything outside `~/.zshrc`.

## Report
Append a short **"HANDOFF-0015 — aliases"** section to `docs/audit/2026-09-09-machine-audit.md` (what was added, verification output, the Warp setting location if found). Set `status: done` with `completed:`. Commit: `env: KGME shell aliases (HANDOFF-0015)`.
