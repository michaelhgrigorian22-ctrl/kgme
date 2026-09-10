---
id: ADR-007
type: decision
status: accepted
created: 2026-09-09T19:45:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-007 — Model roles and routing

## Context
Michou has a Claude Max subscription (Claude Code), a ChatGPT Plus subscription (Codex CLI), plans to use Groq's free API tier, and has Ollama installed on an M4 Pro with 24 GB unified memory. Subscriptions do not include API keys for scripts; Groq and Ollama do provide programmatic access. Judgment-heavy work and cheap high-volume work have different needs; private data has different needs again.

## Decision
- **Claude Code** is the executive: planning, multi-step execution, anything touching the repo, judgment-heavy extraction. Invoked interactively or via `claude -p` from jobs.
- **Codex CLI** is the second builder and independent reviewer (`codex exec`), governed by the same constitution via `AGENTS.md`.
- **Groq** serves fast, cheap cloud calls on Tier 2/3 data where allowed: classification, extraction of simple structure, first-pass summaries.
- **Ollama** serves local, private calls: anything touching Tier 1, offline work, and embeddings for semantic search over the vault. Models in the 8–14B class (4-bit) are the comfortable range on 24 GB; larger is not used alongside normal work.
- A single router (`router/llm.py`) exposes `ask(provider, prompt, ...)` over all providers, so a job changes provider by changing one argument.
- **Every outbound call passes through a policy layer in the router** (the "Sentinel", after Meta's Muse design): it checks the data tier of the inputs against the provider's allowlist and refuses or downgrades. Routing by sensitivity, then by cost, then by capability.

## Alternatives considered
- Direct API calls to Anthropic/OpenAI from scripts: requires separate paid keys; may be added later behind the same `ask()`.
- A hosted multi-model gateway: adds a third party to every call.

## Consequences
The router is the single choke point for policy and for cost accounting (the ledger records provider, tokens, cost per call). Provider allowlists per tier are configuration, reviewed weekly.
