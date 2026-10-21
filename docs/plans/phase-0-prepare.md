---
id: PLAN-PHASE-0
type: note
status: active
created: 2026-09-09T20:05:00-07:00
modified: 2026-09-10T09:50:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — Phase 0: Prepare

Phase 0 is everything that happens *before* the first capability is built: understanding the machine, fixing the ground it stands on, learning the tools, and observing real needs. Target: about two weeks. Nothing in Phase 0 is wasted if the design changes. This file is canonical; the claude.ai Project "Automation" carries a mirror.

## 1. How the surfaces fit together

| Surface | Where it runs | Role in KGME | Reads / writes |
|---|---|---|---|
| **Cowork** | Cloud sandbox linked to the Mac; sees this folder through a mount (Linux VM — cannot run macOS commands, install software, or touch launchd) | Architect, researcher, reviewer, phone-side overseer. Writes plans, ADRs, handoffs; reads reports back; web research; cloud scheduled tasks | Repo files, Project docs, shared memory |
| **Claude Code** | Natively on the Mac (terminal or VS Code extension) — full macOS access | Builder and operator. Installs, configures, runs, commits. Later, KGME jobs invoke it via `claude -p` | `CLAUDE.md`, `.claude/`, `.mcp.json`, the whole repo |
| **Codex CLI** | Natively on the Mac (ChatGPT login) | Second builder / independent reviewer | `AGENTS.md` (symlink to `CLAUDE.md`), repo |
| **KGME runtime** | launchd → Python → `claude -p` / `codex exec` / Groq / Ollama | The thing itself, once built | `memory/`, `jobs/`, ledger |

**The contract is the repo.** `CLAUDE.md` is read automatically by Claude Code every session; Cowork reads and edits the same file. Skills in `.claude/skills/`, hooks in `.claude/settings.json`, and MCP servers in `.mcp.json` are plain files both surfaces see. Whatever is in the repo is what every agent believes.

**The briefing layer is the claude.ai Project.** Decision log, plans, later the charter — the context any Claude needs entering a session on any surface, including a phone. The repo's `docs/` is canonical; the Project mirrors status and pointers. A future KGME job publishes `docs/STATUS.md` to the Project; until then Cowork updates it by hand.

**Handoff protocol** (ADR-011): Cowork writes `docs/handoff/YYYY-MM-DD-<topic>.md`; Michou opens Claude Code here and says *"Read docs/handoff/<file> and carry it out"*; Claude Code plans, gets approval, executes, writes its report to the named path, flips `status` to `done`; Cowork reads the report back. First handoff: `docs/handoff/done/2026-09-09-machine-audit.md`.

## 2. Sequence

1. **Audit** (Claude Code, ~15 min, read-only) — handoff 0001 → `docs/audit/2026-09-09-machine-audit.md`.
2. **Fix the ground** (Claude Code, from the audit) — the fix-now list below, each item its own small handoff.
3. **Repo skeleton** (Claude Code) — `git init`; `.gitignore` (Obsidian workspace files, `.env`, `logs/*.jsonl`, `.DS_Store`); `AGENTS.md → CLAUDE.md` symlink; first commit of the documents already present.
4. **Obsidian** (Michou, 30 min) — open the vault at `memory/`; core plugins only for week one.
5. **Ollama** (Claude Code) — pull one chat model and one embedding model; verify the endpoint; measure memory headroom.
6. **Charter and ADRs** (Michou with Cowork) — review the `[REVIEW]` passages in `docs/charter.md`; accept; commit.
7. **Accounts** (Michou) — GitHub + one private repo; password manager + CLI; personal Google with 2FA; Canvas iCal feed URL into Keychain; dedicated KGME Chrome profile logged into the school account.
8. **Observe for the full two weeks** (Michou) — friction log; sleep and presence pattern; account inventory.

## 3. Fix-now list (candidates — confirm against the audit)
- FileVault on; Time Machine running to a real destination.
- One Python story: `uv` only; other Pythons left alone and never used for KGME.
- Homebrew; `gh`; git identity; SSH key registered with GitHub.
- No spaces in any path under `~/Projects`; kebab-case folders. Rename before scripts depend on them.
- `~/Projects` as the single home for code and vaults; nothing KGME-related on the Desktop or in Downloads.
- Know which Chrome profiles exist and which accounts they hold before creating the KGME profile.
- Decide whether the Mac stays awake on power (`pmset`) so a morning heartbeat actually fires — informed by two weeks of observation.
- Know any global `CLAUDE.md` or MCP servers that would silently apply inside this repo.

## 4. Observe before building
- **Friction log** — `memory/inbox/friction-log.md`, one dated line per entry. At the end of Phase 0 this ranks the first capabilities.
- **Sleep and presence** — lid closed at 7am? On power overnight? Phone before laptop? The heartbeat and control-surface design follow from this.
- **Account inventory** — which Google account holds what; which Chrome profile is signed into which; where Canvas notifications land. This becomes the routing table for the browser worker.

## 5. Exit criteria
- Audit report exists; every fix-now item done or consciously deferred (recorded in the decision log).
- Repo initialised, first commit, private GitHub remote (Tier 2/3 only).
- Vault opens in Obsidian; friction log has ≥ 10 entries.
- Ollama serves a chat model and an embedding model; memory headroom recorded.
- Charter accepted; ADR-001…011 committed.
- Accounts ready: GitHub, password manager CLI, personal Google (2FA), Canvas iCal subscribed, KGME Chrome profile logged in.
- First loop chosen from the friction log.

## 8. Narrowed on 2026-09-10 (after the external audit)

The audit's central point stands: infrastructure choices were running ahead of evidence of which recurring task deserves automation, and the friction log has one example entry. Phase 0 is therefore narrowed to the ground layer plus **one measured loop**, and everything else waits for demonstrated need.

**Keep in Phase 0:** backup + restore test · GitHub account, `gh auth login`, private remote · firewall (global state only) · Homebrew and `gh` (amended proposals) · `finance-python` disposal (0018) · global-config pointer fixes · charter acceptance · ADR-012/013/014 acceptance · repo-scoped `.claude/settings.json` (ask-mode) · the validator (`control/schema/lint.py`) · policy canary tests (`tests/policy/`) · friction log, two weeks.

**Loop 0 — `kgme brief` (manual, read-only, local).** Invoked by hand, no scheduler. Reads only `memory/` (open reminders and tasks, today's daily note, the friction log). Validates every note it reads against the schema. Writes one derived artefact, `memory/agent/brief/YYYY-MM-DD.md`, and two ledger events (`intent`, `outcome`) per ADR-013 §4. Acceptance checks, each a test: running twice on the same day replaces rather than duplicates; killing it mid-run leaves an intent without an outcome that the next run reconciles; a planted forbidden file in the read path is refused and the refusal is a ledger event; the artefact can be regenerated from the ledger plus `memory/`. No model call is required for the first version — the loop is about the machinery; the model joins when the brief needs prose.

**Deferred until Loop 0 passes or the friction log demands it:** Ollama models, embeddings, Playwright, the browser worker, Telegram, Groq, any path renaming outside `Automate`, any scheduled job.

**Revised exit criteria for Phase 0:** the five gates in `STATUS.md` met; Loop 0 passes its four checks; friction log ≥ 10 entries; charter accepted; `finance-python` disposed.
