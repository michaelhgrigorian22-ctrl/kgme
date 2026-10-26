# KGME — Kuang Grade Mark Eleven

Michou's local-first, multi-model personal agent system. Everything that matters is plain text in this repository. The constitution for every agent is `CLAUDE.md`.

## What is where

**Brain** — what KGME knows and has decided
- `docs/` — the charter, current state, plans, decisions, guides, handoffs, reports, design (index: `docs/README.md`)
- `memory/` — the Obsidian vault: Michou's notes, the daily notes, the inbox, and what agents write in `memory/agent/`

**Commands** — the rules agents run under
- `control/` — the guard and ledger hooks, the git hook, the policy profiles, the reviewer prompts, the schema entry point
- `CLAUDE.md` (and `AGENTS.md`, the same file for Codex) — how agents work here
- `kgme.toml` — all configuration

**Engine** — the code
- `kgme/` — the Python package behind the `kgme` command
- `jobs/` — one folder per job: what it does, what it may touch, how it runs
- `cockpit/` — the local app over the ledger: `kgme cockpit` serves it on `127.0.0.1:8642`; the Dock icon opens the page but does not start the server (launchd waits for Phase 3)
- `tests/` — the test suites and the policy canaries; `make check` runs them

**Record** — what happened
- `logs/ledger/` — every intent and outcome, append-only, tracked
- `docs/audit/` — the reports and review audits

## Where to look
| To find | Look in |
|---|---|
| the current state | `docs/STATUS.md` |
| what is being built | `docs/handoff/` (open), `docs/handoff/proposed/` (proposed) |
| why something is the way it is | `docs/adr/` |
| how a tool works | `docs/readers/` |
| what happened | `logs/ledger/` and `docs/audit/` |
| Michou's notes | `memory/` |
