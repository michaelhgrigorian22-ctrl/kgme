---
id: AUDIT-0001
type: report
created: 2026-09-09T19:38:51-07:00
author: claude-code
source: fetched
tier: 2
handoff: HANDOFF-0001
status: final
---

# Machine audit — 2026-09-09

Read-only survey per HANDOFF-0001. No file outside this report was created or modified; nothing was installed. Where a check required `sudo`, it was skipped and marked. Where a file might contain secrets, only presence or field names are recorded — never values.

## A. Machine and OS

| Finding | Value |
|---|---|
| OS | macOS 26.6.2 (build 25G83) |
| Arch | arm64 |
| Model | MacBook Pro (Mac16,8) |
| Chip | Apple M4 Pro |
| Cores | 12 (8 performance, 4 efficiency) |
| RAM | 24 GB (25,769,803,776 bytes; `system_profiler` reports 24 GB) |
| Disk `/` | 460 Gi total, 12 Gi used, 232 Gi available (5 % capacity, APFS) |
| FileVault | On |
| Gatekeeper | assessments enabled |
| Application firewall | **disabled** (State = 0) |
| Time Machine destinations | none configured |
| Time Machine latest backup | mount failed (`Error Domain=com.apple.backupd.ErrorDomain Code=17`) |
| `pmset` sleep | 0 (never) — currently prevented by `coreaudiod`, `sharingd`, `caffeinate`, `runningboardd`, `powerd`, `useractivityd`, `Claude` |
| `pmset` displaysleep | 0 (never) |
| `pmset` disksleep | 10 min |
| `pmset` hibernatemode | 3 |
| `pmset` powernap | 1 |
| `pmset` ttyskeepawake | 1 |
| `pmset` tcpkeepalive | 1 |
| `pmset` womp (wake-on-LAN) | 1 |
| `pmset` standby | 1 |
| Uptime | 9 days, 20:36 |

`pmset` does not expose a distinct "prevent sleep on power" key here; the effective setting is `sleep 0` unconditionally, so the Mac never sleeps automatically regardless of power source. Sleep is currently additionally asserted by seven processes, of which `caffeinate` and `Claude` are the notable non-system ones.

## B. Developer toolchain

| Tool | Present | Version / path |
|---|---|---|
| Xcode Command Line Tools | yes | `/Library/Developer/CommandLineTools` |
| Homebrew (`brew`) | **not installed** | — |
| git | yes | 2.50.1 (Apple Git-155) |
| `git config --global user.name` | **empty** | — |
| `git config --global user.email` | **empty** | — |
| GitHub CLI (`gh`) | **not installed** | — |
| `~/.ssh` | **does not exist** | — |
| `gh auth status` | n/a | — |
| `python3` #1 | yes | `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` → Python 3.14.4 |
| `python3` #2 | yes | `/usr/local/bin/python3` → Python 3.14.4 |
| `python3` #3 (system) | yes | `/usr/bin/python3` → Python 3.9.6 |
| `uv` | yes | 0.11.7 at `~/.local/bin/uv` |
| `pyenv` | not installed | — |
| `conda` | not installed | — |
| `pipx` | not installed | — |
| `~/.pyenv` | absent | — |
| `node` | yes | v25.9.0 via nvm (`~/.nvm/versions/node/v25.9.0/bin/node`) |
| `npm` | yes | 11.12.1 |
| `nvm` | yes | dir present at `~/.nvm` |
| `fnm` | not installed | — |
| `volta` | not installed | — |
| VS Code CLI (`code`) | yes | 1.130.0 arm64 at `~/.local/bin/code` |
| `claude` (Claude Code) | yes | 2.1.267 (installed under nvm's node) |
| `codex` (Codex CLI) | **not installed** | — |
| `ollama` | yes | 0.33.3 at `/usr/local/bin/ollama` |
| `ollama list` | 0 models pulled | — |
| Playwright | not installed | `npx playwright` would fetch package (skipped) |

VS Code extensions installed (11): `charliermarsh.ruff`, `github.copilot-chat`, `ms-python.debugpy`, `ms-python.python`, `ms-python.vscode-pylance`, `ms-python.vscode-python-envs`, `ms-toolsai.jupyter`, `ms-toolsai.jupyter-keymap`, `ms-toolsai.jupyter-renderers`, `ms-toolsai.vscode-jupyter-cell-tags`, `ms-toolsai.vscode-jupyter-slideshow`.

Apps in `/Applications` (from the target list): **present** — Obsidian, Ollama, Visual Studio Code, Google Chrome, Claude, ChatGPT, Warp. **Absent** — 1Password, Bitwarden, Docker, iTerm.

## C. Existing Claude Code / agent configuration

`~/.claude/` exists. Top-level entries (names only): `.DS_Store`, `.last-cleanup`, `agents/`, `backups/`, `cache/`, `CLAUDE.md`, `commands/`, `debug/`, `history.jsonl`, `hooks/`, `mcp-needs-auth-cache.json`, `plans/`, `plugins/`, `projects/`, `session-env/`, `sessions/`, `settings.json`, `shell-snapshots/`, `skills/`, `tasks/`, `telemetry/`.

`~/.claude/settings.json` — top-level keys only: `$schema`, `agentPushNotifEnabled`, `hooks`, `permissions`, `skipWorkflowUsageWarning`. Contents not printed.

`~/.claude.json` — present. No `mcpServers` key found; therefore no MCP servers configured at the Claude Code CLI level.

`~/.claude/CLAUDE.md` — **present** (45 lines). Global instructions. This file is applied to every Claude Code session, including inside `~/Projects/Automate`. It is layered above the repo `CLAUDE.md`; the repo file cannot un-say what the global file says.

Skills / agents / commands (names only):
- `~/.claude/skills/`: `grill-me`
- `~/.claude/agents/`: `data-fetcher.md`, `model-auditor.md`, `report-writer.md`
- `~/.claude/commands/`: `distill.md`

Claude Desktop MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`): file present; `mcpServers` count = 0; other top-level keys `coworkUserFilesPath`, `preferences`.

`CLAUDE.md`, `AGENTS.md`, `.mcp.json`, `.claude/` under `~/Projects` (max depth 4):
- `~/Projects/Automate/CLAUDE.md`
- `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/CLAUDE.md`
- `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/.claude/`
- `~/Projects/School/Active/ADA-MT1-PREPFOLDER/.claude/`

Under `~/Documents`: none.

## D. Browser

Google Chrome — profiles read from `~/Library/Application Support/Google/Chrome/Local State`, display names only:
1. `MICHAEL - CMC`
2. `woke yard`

Both profiles appear signed-in in `Local State`.

Claude in Chrome extension (id `fmpnliohjhemenmnlpbfagaolkdacoja`): **not present** in `Default/Extensions/`, `Profile 1/Extensions/`, or `Profile 2/Extensions/`. (Note: `Default` profile directory exists but is unused; the two live profiles are `Profile 1` and `Profile 2`.)

## E. Scheduled things already running

`~/Library/LaunchAgents` (names only, 5 items):
- `com.Box.Box-Edit.launch.plist`
- `com.box.Box-Local-Com-Server.launch.plist`
- `com.google.GoogleUpdater.wake.plist`
- `com.google.keystone.agent.plist`
- `com.google.keystone.xpcservice.plist`

`launchctl list` non-Apple entries (selected; PID means currently running):
- `com.avast.userinit`, `com.avast.Antivirus` (PID 2852), `com.avast.hub` (PID 2856) — Avast antivirus stack active
- `com.ollama.ollama` (PID 7032)
- `com.anthropic.claudefordesktop.ShipIt`, `application.com.anthropic.claudefordesktop.*` (PID 98258) — Claude for Desktop running with its updater
- `us.zoom.updater`, `application.us.zoom.xos.*`, `us.zoom.updater.login.check`
- `com.microsoft.update.agent`, `com.microsoft.SyncReporter`, `com.microsoft.OneDriveLauncher`, `com.microsoft.OneDriveStandaloneUpdater`, `application.com.microsoft.Word.*`, `application.com.microsoft.Excel.*`
- `com.Box.Box-Edit.launch`, `com.box.Box-Local-Com-Server.launch`, `application.com.Box.Box-Edit.*`, `application.com.box.Box-Local-Com-Server.*`
- `com.google.GoogleUpdater.wake`, `application.com.google.Chrome.*`
- `com.openssh.ssh-agent`
- `application.dev.warp.Warp-Stable.*`, `application.md.obsidian.*`

`crontab -l`: none.

## F. File-system layout

`~/Projects` — 5 subfolders (excluding `.DS_Store`):

| Folder | File count | Total size | Spaces in paths |
|---|---|---|---|
| `Automate` | 27 | 136 K | no |
| `Finance` | 28,071 | 1.8 G | **yes** (e.g. `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/`) |
| `Personal` | 75 | 111 M | **yes** (many document filenames) |
| `School` | 2,579 | 1.8 G | **yes** (many filenames and folders) |
| `Tools` | 18 | 512 K | no |

Depth-2 layout summary:
- `Automate/`: `CLAUDE.md`, `.gitignore`, `docs/` (adr, plans, handoff, readers, audit, charter.md, schema-v1.md, README.md), `memory/` (inbox, agent, daily, notes, templates, attachments).
- `Finance/`: `Archive/` (large mixed pitches folder, many `.xlsx`/`.pdf`/`.docx` with spaces); other subfolders exist but the archive dominates.
- `Personal/`: `Documents/` (many PDFs, resumes, forms), `Misc/`.
- `School/`: `Archive/` dominated by class materials and pitches.
- `Tools/`: `md2pdf/` (Node project with `package.json`, `md2pdf.mjs`, `node_modules/`).

`~/` top level (names only): `AGENTS.md`, `Applications`, `Archive`, `Bin`, `Claude`, `Desktop`, `Documents`, `Downloads`, `Library`, `Movies`, `Music`, `OneDrive - Claremont McKenna College`, `Pictures`, `Projects`, `Public`, `Reference`.

- `~/AGENTS.md` — a loose file at `$HOME` (not the constitution symlink this repo will create; separate artifact).
- `~/OneDrive - Claremont McKenna College` — path contains spaces.

`~/Downloads` — 27 top-level items, 418 M total.
`~/Desktop` — 13 top-level items, 4.5 M total.

Git repositories under `~/Projects` (max depth 3): **none found**. (Depth was capped per handoff; repos nested deeper — e.g. anything inside `finance-python/` — were not enumerated.)

Obsidian vaults under `~` (max depth 4, `.obsidian` directory presence): **none found**. `~/Projects/Automate/memory/` is the intended vault location but does not yet have `.obsidian/`.

## G. Accounts (names only)

- Chrome signed-in profile count: **2** (both profiles carry sign-in fields).
- Password manager CLI: `op` (1Password) **not installed**; `bw` (Bitwarden) **not installed**.

## Gaps and risks noticed

Facts, not fixes. Ordered by likely severity for KGME Phase 0.

1. **No git identity.** `git config --global user.name` and `user.email` are both empty. HANDOFF-0002 step 3 is designed to stop at this state; it will need Michou's decision on name/email before repo init proceeds. Charter/ADR-004 want machine-written commits attributable, so this is a Phase 0 blocker.
2. **No Time Machine destination configured.** Latest-backup mount also fails. Charter and ADR-008 both require Time Machine running; without it the "reversible" property of most work only holds for what is in git.
3. **Application firewall off** (`State = 0`). Not in the Phase 0 §3 fix-now list explicitly, but the security posture ADR-008 assumes contradicts this default.
4. **No SSH key material** (`~/.ssh` does not exist). Fine while everything is local, but blocks a private GitHub remote when Phase 0 §7 arrives.
5. **Homebrew not installed** and `gh` not installed. Phase 0 §3 names both; downstream fixes (installing `gh`, later `codex`, potentially `op` or `bw`) will either need Homebrew or an explicit alternative decision.
6. **`pmset` set to never sleep, sleep additionally asserted by seven processes including Claude.** Uptime 9 days 20 h corroborates this. The morning-heartbeat design has not been decided yet (Phase 0 §3, §4), but the current setting is a decision by inertia, not by intent — worth flagging so Michou chooses on purpose.
7. **Global `~/.claude/CLAUDE.md` (45 lines) applies to every session in this repo.** The repo's `CLAUDE.md` cannot override it silently; anything in the global file is quietly authoritative inside `~/Projects/Automate` until it is read and reconciled. Phase 0 §3 explicitly lists "know any global CLAUDE.md" as a fix-now candidate.
8. **Three parallel Python installs** (`/Library/Frameworks/...` 3.14, `/usr/local/bin/python3` 3.14, `/usr/bin/python3` 3.9.6). Phase 0 §3 wants a single `uv` story; `uv` is present, but the other Pythons need a documented "leave alone, never used for KGME" posture rather than an accidental one.
9. **Paths with spaces under `~/Projects/Finance`, `~/Projects/Personal`, and `~/Projects/School`.** Phase 0 §3 names this. `Automate` and `Tools` are clean; the noisy directories are the pitch/archive folders. `~/OneDrive - Claremont McKenna College` also has spaces but is out of scope for Phase 0.
10. **Codex CLI not installed.** The constitution names Codex as second builder / independent reviewer. Missing today; not a KGME blocker, but the AGENTS.md symlink HANDOFF-0002 will create has no consumer yet.
11. **Avast antivirus stack running** (three launchd labels, two live PIDs). Not on the Phase 0 list; worth noting because Avast will scan files KGME writes and may quarantine or slow scripted operations later. Not proposed as a fix.
12. **Stray `~/AGENTS.md` at `$HOME`.** Its presence at the home directory is orthogonal to the `AGENTS.md` HANDOFF-0002 will create *inside the repo*, but it may confuse future readers about which is authoritative. Reporting existence only; contents not opened.
13. **No git repositories under `~/Projects` at depth 3.** Nothing lost; simply the current state — this repo will be the first once HANDOFF-0002 runs. Deeper repos (e.g. inside `finance-python/`) were not enumerated because the handoff capped depth at 3.
14. **Claude for Desktop `mcpServers` count = 0 and Claude Code has no `mcpServers` key.** No MCP servers currently silently apply to sessions in this repo. That is a *good* state (nothing to reconcile), recorded here for symmetry with finding 7.
15. **Ollama has zero models pulled.** Not a Phase 0 gap per §3 (§5 handles this later), but worth noting so it is not forgotten when Phase 0 §5 runs.

## HANDOFF-0002 — repo init (halted at step 3 gate)

Attempted 2026-09-09T19:41:00-07:00. Halted before `git init`; no repository was created, no symlink was made, no commit was written. HANDOFF-0002 frontmatter left as `status: open`.

- **Step 1** — CWD confirmed `/Users/michaelgrigorian/Projects/Automate`; `CLAUDE.md` present.
- **Step 2 — Frontmatter lint result.** 22 markdown files under `docs/` and `memory/` were checked for the three required keys `id`, `type`, `status` in their top YAML block (with `CLAUDE.md`, `docs/README.md`, and `memory/templates/` exempt per the handoff). **21 pass; 1 fails.**
    - `docs/audit/2026-09-09-machine-audit.md` — missing key `status`.
    - Note: this failure is in the audit report Claude Code authored earlier this session per HANDOFF-0001's frontmatter template, which prescribed `id, type, created, author, source, tier, handoff` and did not include `status`. The lint rule and the HANDOFF-0001 template disagree. Per HANDOFF-0002's rule ("Report any file that fails; do not fix it") the file was left as-is; Cowork should reconcile whether audit reports carry a `status` field, or update the lint rule.
- **Step 3 — Git identity gate.** `git` is installed (2.50.1), but `git config --global user.name` and `git config --global user.email` are both empty. Per HANDOFF-0002 step 3, this is a designed stop. Identity was not configured.
- **Steps 4–9 not executed** (`.gitignore` review, `git init`, `AGENTS.md` symlink, staging, commit, `git log`/`git ls-files` output).
- **Downstream implication.** HANDOFF-0003 declares `depends_on: HANDOFF-0002` and its body requires HANDOFF-0002 to be `done`. HANDOFF-0003 was therefore not started; its `status` remains `open`.

**What Michou needs to decide before HANDOFF-0002 can resume:** the name and email address to configure with `git config --global`. This is not for me to pick — commit authorship is durable and public-facing once the repo is pushed. Once supplied, HANDOFF-0002 can be re-run from step 3.

