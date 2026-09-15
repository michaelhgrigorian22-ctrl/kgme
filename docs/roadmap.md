---
id: ROADMAP
type: note
status: active
created: 2026-09-12T00:20:00-07:00
modified: 2026-09-12T00:20:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME roadmap — the view from 10,000 feet

Five phases. Each phase ends with something that works end to end, not with a pile of parts. The cockpit appears at the end of Phase 1, becomes the main surface in Phase 2, and everything after is seen through it. Dates are guesses at Michou's part-time pace; the order is not.

| Phase | What it delivers | Where the UI is | Exit test |
|---|---|---|---|
| **0 — Prepare** (done, 2026-09-09 → 11) | Backup proven, repo off-machine, toolchain pinned, charter + 18 ADRs, finance-python dismantled | Terminal only | All gates that don't need code: met |
| **1 — Foundations + Loop 0** (≈ 2–3 weeks) | Repo-scoped permissions and hooks · the ledger · the validator · canary tests · **Loop 0 `kgme brief`** · `kgme clean` · cockpit **design** (canvas from the wishlist) · **cockpit v0**: a read-only timeline over the ledger, installed to the Dock | **First pixel at step 7 (design) and step 8 (v0).** Design can start any time in parallel — it is taste, not code; building waits for the ledger | Loop 0 passes its four tests; the timeline shows a real run |
| **2 — The cockpit becomes the workplace** (≈ 4–6 weeks) | Ingest Claude Code and Codex event streams · the router with its policy layer (model selector, "optimized" mode with the decision shown and overridable) · in-app approval prompts (the Sentinel's human half) · `/btw`-style side lane on a cheap model · queued messages, interrupt, transcript · dispatch a handoff from the app · VS Code follows the run · keyboard map · the cyberpunk design system applied | **Main surface.** Terminal remains available; the cockpit is where Michou works | A full handoff cycle — write, dispatch, watch, approve, review — done from the cockpit without opening a terminal |
| **3 — Workers and the heartbeat** (≈ 6–8 weeks) | launchd heartbeat and the first *scheduled* job (the daily brief) · Ollama models + local embeddings (semantic search over the vault) · coursework → calendar: browser worker, Google Calendar tool, approval gate · Telegram phone surface bridged to the same ledger · migration plan: index Finance / School / Personal · Tier 1 access boundary · egress control | Cockpit shows scheduled runs, approvals from phone land in the same timeline | The daily brief arrives unattended every morning for two weeks without a blocking failure; syllabus → calendar works with approval |
| **4 — Compounding** (ongoing) | Weekly review automated (failures by class, routing scorecard, cost) · new workers drawn from the friction log · cockpit refinements from the wishlist · optional Tauri shell (menu bar, notifications) | The daily driver | Autonomy widened only by ADR, class by class, from evidence |

## Rules that hold across phases
- Nothing is scheduled until ADR-013's gates are met (backup, ledger, permissions, canary tests, charter). Met: backup, charter.
- Every step is a handoff; every diff is reviewed by Codex; every run is in the ledger.
- The cockpit is a view over the ledger, never a harness. All its code lives in `cockpit/`, visible in VS Code.
- Design early, build after Loop 0. The wishlist and the design canvas are always open; code waits its turn.
- Deferred items return when Loop 0 or the friction log demands them, not before.

## What could reorder this
- If the friction log shows the coursework → calendar pain is acute, its worker moves up inside Phase 3, not ahead of Phase 2's approval UI (it needs it).
- If the cockpit v0 proves the ledger schema wrong, Phase 2 starts with a schema migration (ADR-005 allows it; the ledger is versioned).
