---
id: ADR-017
type: decision
status: accepted
created: 2026-09-11T16:30:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-017 — The cockpit: a local app that is a view over the ledger, not a new harness

*Proposed 2026-09-11 after Michou, running Claude Code and Codex side by side on another project, found no way to see what all his agents were doing in one place. Resolves the open "control surface" decision for the desk; the phone surface follows later. Becomes accepted on his word and commit.*

## Context
Claude Code and Codex each have their own terminal UI. Neither shows the other. Neither shows the ledger. Michou wants one personalised surface for observing, approving, and steering every agent KGME runs. The temptation is to build a "harness" that re-implements what those tools already do; the durable move is the same one made for Obsidian and the vault: **the files are the system; the app is a window.**

## Decision
KGME gets a **cockpit**: a small local application that does four things and no more.
1. **Launch** agent jobs headlessly through the vendors' own scriptable modes — Claude Code as a subprocess (`claude -p … --output-format stream-json`, on Michou's subscription) and Codex as a subprocess (`codex exec --json`, JSON Lines events) — plus Ollama and Groq over HTTP through the router (ADR-007).
2. **Ingest** every event those streams emit into the ledger (ADR-012) in **one event shape** regardless of source: `{ts, run_id, source, kind, class, payload_ref}`. The cockpit never holds state the ledger does not.
3. **Render** one timeline across all sources — the "single terminal" — plus per-run detail, cost, and the intent/outcome pairs of ADR-013.
4. **Gate**: permission prompts from the headless agents are routed to the cockpit's own approval UI (Claude Code's headless mode can delegate permission prompts to a custom tool; Codex's approval and sandbox flags are set per job). This is the Sentinel's human-facing half. Follow-ups to a running job are sent as the next turn of a resumed session; neither vendor supports mid-turn interjection, and the cockpit does not pretend to.

**Form factor, per ADR-015.** A Python service on `localhost` serving a plain HTML/JS page; "an app on the computer" is that page installed to the Dock from the browser (Chrome "Install page as app" / Safari "Add to Dock"). No Electron. If a native shell is ever wanted (menu-bar item, notifications), the same page is wrapped in Tauri — decided then, not now. The interactive terminal UIs remain available and untouched for when Michou wants them directly.

**Not the Agent SDK, for now.** Anthropic's Agent SDK is the polished library route but its terms direct products to API-key billing rather than a claude.ai subscription; for a personal tool on the Max plan, the documented subprocess route (`-p` + JSON output) is the right one. The SDK stays an option if API billing is ever chosen.

## Build order (Phase 1, after Loop 0)
ledger + event schema → stream ingestion from both CLIs → read-only timeline → approval prompts in-app → dispatch a handoff from the app → phone surface (Telegram) bridging to the same ledger.

## Alternatives considered
- A TUI in the terminal (Textual): keeps the terminal Michou wants to leave.
- A full custom harness (own tool loop, own model calls): re-implements two products and forfeits their skills, hooks, and memory integration.
- Swift/native from day one: a new language for both him and the agents, before the ledger even exists.

## Consequences
The cockpit is Phase 1's first UI and depends on Loop 0's ledger. The "control surface" open decision closes as: desk = cockpit, phone = Telegram later. Every agent event becomes a ledger event, which is what ADR-003 always wanted.
