---
id: PLAN-PHASE-1
type: note
status: active
created: 2026-09-11T23:50:00-07:00
modified: 2026-09-11T23:50:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — Phase 1: Loop 0 and the cockpit

Phase 0 built the ground: backup proven, repo off-machine, toolchain pinned, charter and eighteen ADRs accepted. Phase 1 writes the first code — the boring, load-bearing kind — and ends with one loop that works end to end and a first screen that shows it. Everything is built to ADR-015 and reviewed by Codex before commit. Nothing is scheduled in Phase 1.

## Build order (each step is one handoff; each ends with a Codex review)

1. **Repo-scoped permissions.** `.claude/settings.json` in the repo: ask-mode, explicit allow for read-only commands and `uv run`, deny for `rm -rf`, `curl | bash`, any read of `.env`/`~/.ssh`/Keychain, any `git push --force`. Pre-tool hook that blocks by path (Tier 1, `~/.ssh`, `.env`) and post-tool hook that appends every tool call to the ledger. This is the first thing, because everything after it runs under it.
2. **Ledger.** `logs/ledger/YYYY-MM.jsonl`, append-only. One event shape for every source: `{ts, run_id, source, kind, class, actor, payload_ref}` where `kind ∈ {intent, outcome, tool_call, approval, correction, note}` and `class` per ADR-016. A 60-line `ledger.py` in the effects layer with `append()` and `read()`; nothing else writes to the file.
3. **Validator.** `tools/schema/lint.py` — checks every note under `memory/` against `docs/schema-v1.md` (frontmatter, required fields, unique ids, ISO dates with offset, type-specific fields, folder-by-type). Run by `make check`. First real test of ADR-015's ten-minute standard.
4. **Canary tests.** `tests/policy/`: plants a fake `.env`, a fake Tier 1 file, a forbidden destination; asserts each worker profile is refused. Results are ledger events. Gate 4 on STATUS.
5. **Loop 0 — `kgme brief`.** Manual, read-only, local, no model call in v1. Reads open reminders and tasks, today's daily note, the friction log; validates them; writes `memory/agent/brief/YYYY-MM-DD.md`; records `intent` before and `outcome` after. Four acceptance tests: duplicate run replaces; interrupted run leaves an intent the next run reconciles; a planted forbidden file is refused and logged; the artefact is reconstructable from ledger + `memory/`. `--dry-run` supported. Then v2 adds the model for prose, routed per ADR-007/018 with the decision recorded.
6. **`kgme clean`.** The disposable-class deleter (see the `rm -rf` decision on STATUS): allowlisted paths only, ledger event per deletion. Replaces any need for an `rm -rf` permission.
7. **Cockpit design.** Design canvas from `memory/notes/cockpit-wishlist.md` — cyberpunk, keyboard-first, legible at 2am. Approved by Michou before any code.
8. **Cockpit v0.** `cockpit/`: a Python service on localhost serving one page — the timeline over the ledger, read-only. Installed to the Dock from the browser. Then, in order: ingestion from `claude -p --output-format stream-json` and `codex exec --json`; in-app approval prompts; `/btw`-style side lane routed to a cheap model; dispatch a handoff from the app; VS Code follow via `code --goto`.

## Exit criteria
- Gates 3, 4, 5 on STATUS met (ledger written, permissions + hooks demonstrated, canary tests passing).
- Loop 0 passes its four tests and has been run by hand for a week.
- Cockpit v0 shows the ledger timeline and at least one live agent run.
- Friction log ≥ 10 entries; the first three workers named in the charter.

## Deferred until Phase 1 exits
Scheduling · Ollama models and embeddings · browser worker · Telegram · Groq · migration plan for `Finance/`, `School/`, `Personal/`.
