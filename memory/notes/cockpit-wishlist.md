---
id: 20260911T170000
type: note
created: 2026-09-11T17:00:00-07:00
modified: 2026-09-11T17:20:00-07:00
status: active
tier: 2
source: stated
author: human
project: "[[kgme]]"
---

# Cockpit wishlist

*Scaffolded by Cowork on 2026-09-11 from Michou's words; the entries are his. This is the UX research for the cockpit (ADR-017). One entry per interaction: what it does, why it is good, the keystroke. Taste is the spec. Add freely; nothing here is built until Loop 0 exists.*

## Principle
Preserve the grammar, replace the surface. The cockpit should feel local and keyboard-first; functionality at peak in every detail is what turns alright into great. (stated 2026-09-11)

## From Claude Code
- **`/btw` — side question without touching the conversation.** Answers from context only, no tools, works while Claude is working, never enters history, `f` forks it into a subagent. In the cockpit: a side lane that reads a run's context without writing to it, routed to the cheapest model, usable across Claude *and* Codex runs. (stated 2026-09-11)
- **Keyboard shortcuts generally** — Esc to interrupt, queued messages while a turn runs, `Ctrl+O` transcript, `!` shell mode, vim mode. The cockpit mirrors Claude Code's configurable keybindings so muscle memory transfers. (stated 2026-09-11)
- 

## From Codex
- 

## From Warp
- 

## From Obsidian
- 

## Model routing
- **Model selector** — pick the model per message, across Claude, Codex, Groq, local. (stated 2026-09-11)
- **"Optimized" mode** — no selection; the cockpit answers with the most efficient model for the question. Must show which model answered, why, and what it cost, and be overridable in one keystroke. (stated 2026-09-11)
- **Claude-style commands and tools across all models** — the same slash commands and the same tool set regardless of which model is answering. (stated 2026-09-11)

## Transparency
- **See the code running in VS Code while in the app.** The editor follows what the agents and jobs are doing, live. (stated 2026-09-11)
- **Everything coded is visible in VS Code, organized within the project.** Everything trackable and easily auditable; nothing hidden in an app bundle or a separate tree. (stated 2026-09-11)

## Aesthetic
- **Cyberpunk.** The graphic design has to be cyberpunk. (stated 2026-09-11)
- 

## Things I do NOT want
- 
