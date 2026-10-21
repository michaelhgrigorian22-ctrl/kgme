---
id: HANDOFF-0001
type: handoff
created: 2026-09-09T19:10:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-09T19:40:00-07:00
report: docs/audit/2026-09-09-machine-audit.md
tier: 2
---

# Handoff 0001 — Read-only machine audit for KGME Phase 0

You are Claude Code running on Michou's MacBook Pro, in `~/Projects/Automate`.
This is the first handoff from the Cowork planning surface. Carry it out exactly;
it is **strictly read-only**. Install nothing, change nothing, delete nothing.

## Purpose
Before KGME (Kuang Grade Mark Eleven — a local-first personal agent system) is
built, we need an honest picture of the machine it will live on: what is
installed, how it is configured, where files live, and what is missing.
The output is a single markdown report that the planning surface will read back.

## Rules
1. Read-only. No `brew install`, no `git init`, no file edits outside the one report.
2. **Never print secrets.** Do not cat any credential, token, key, `.env`, or
   config file that may contain secrets. Where a file exists, report *that it
   exists* and, for config, only the *names* of entries (e.g. MCP server names),
   never values. List `~/.ssh` by filename only. Never print environment variables.
3. If a command needs sudo, skip it and note "requires sudo".
4. If a command is missing, record "not installed" and move on.
5. Write the report to `docs/audit/2026-09-09-machine-audit.md` (create `docs/audit/`).
   Nothing else is written.

## What to collect

### A. Machine and OS
- `sw_vers`, `uname -m`, `sysctl -n hw.memsize` (convert to GB), `system_profiler SPHardwareDataType` (model, chip only)
- Disk: `df -h /`
- Security posture: `fdesetup status` (FileVault), `spctl --status` (Gatekeeper),
  `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`
- Backups: `tmutil destinationinfo`, `tmutil latestbackup` (may need permissions — note if so)
- Power/sleep: `pmset -g` (sleep, displaysleep, hibernatemode, and whether "prevent sleep on power" is set); `uptime`

### B. Developer toolchain (present? version?)
- `xcode-select -p`; `brew --version`; `git --version`; `git config --global user.name` and `user.email` (these two are fine to print); `gh --version`
- `ls ~/.ssh` (names only); does a GitHub SSH key or `gh auth status` exist? (print status line only, no tokens)
- Python: `which -a python3`, each `--version`; presence of `uv`, `pyenv`, `conda`, `pipx`; `ls ~/.pyenv 2>/dev/null | head`
- Node: `node --version`, `npm --version`, `which -a node`; `nvm`/`fnm`/`volta` presence
- `code --version` (VS Code CLI); list installed VS Code extensions: `code --list-extensions`
- `claude --version`; `codex --version` (Codex CLI); `ollama --version` and `ollama list`
- Apps present in `/Applications` and `~/Applications`: report only these if found —
  Obsidian, Ollama, Visual Studio Code, Google Chrome, Claude, ChatGPT, 1Password, Bitwarden, Docker, iTerm, Warp
- Playwright: `npx --no-install playwright --version` (do not install)

### C. Existing Claude Code / agent configuration
- Does `~/.claude/` exist? List its top-level entries (names only). Does `~/.claude/settings.json` exist? If so, list only the top-level keys.
- `~/.claude.json`: if present, list only the *names* of configured MCP servers (no args, no env).
- Find every `CLAUDE.md`, `AGENTS.md`, `.mcp.json`, and `.claude/` directory under `~/Projects` (and `~/Documents` if it exists), max depth 4. Print paths only.
- Any `~/.claude/skills`, `~/.claude/agents`, `~/.claude/commands` — list names only.
- Claude Desktop MCP config: does `~/Library/Application Support/Claude/claude_desktop_config.json` exist? Server names only.

### D. Browser
- Chrome profiles: read `~/Library/Application Support/Google/Chrome/Local State` and report only the profile display names (`profile.info_cache.*.name`). Nothing else from that file.
- Is the Claude in Chrome extension installed? (Check by extension folder presence under the Default profile's `Extensions/`; report yes/no only.)

### E. Scheduled things already running
- `ls ~/Library/LaunchAgents` (names only) and `launchctl list | grep -v com.apple | head -50`
- `crontab -l` (report "none" if empty)

### F. File-system layout (the migration plan will use this)
- `ls -la ~/Projects` and, for each subfolder, depth-2 tree with file counts and total size (`du -sh`). Flag any path containing spaces.
- `ls ~ ` top level (names only). Count of items in `~/Downloads` and `~/Desktop`, and total size of each.
- Any git repositories under `~/Projects` (find `.git`, max depth 3) — path and current branch, plus whether each has a remote (`git remote -v` shows only URLs — print the host part only, e.g. github.com, not the full URL if it contains a token).
- Any Obsidian vaults already present (find `.obsidian` directories under `~`, max depth 4) — paths only.

### G. Accounts (names of things, never contents)
- Google accounts signed into Chrome: report the count of profiles that appear signed in, not the addresses.
- Is a password manager CLI present? (`op --version`, `bw --version`)

## Report format
Write `docs/audit/2026-09-09-machine-audit.md` with this frontmatter:

```
---
id: AUDIT-0001
type: audit
created: <ISO 8601 with timezone>
author: claude-code
source: fetched
tier: 2
handoff: HANDOFF-0001
---
```

Then one section per letter A–G, each as a short table or list of finding → value.
End with a section **"Gaps and risks noticed"**: anything missing, misconfigured, or
likely to bite later (e.g. FileVault off, no backups, spaces in project paths, three
Pythons, no git identity, Chrome with one profile only). Do not fix anything —
just report. Keep it factual; no recommendations beyond flagging.

When done, tell Michou the report path and the three most important gaps in one sentence each.
