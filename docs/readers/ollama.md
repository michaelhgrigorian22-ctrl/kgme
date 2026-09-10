---
id: READER-OLLAMA
type: note
status: draft
created: 2026-09-09T20:00:00-07:00
modified: 2026-09-09T20:00:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — Ollama and local models in KGME

*Part 1 (mental model) written 2026-09-09. Part 2 (setup on this machine) is added after the machine audit.*

## What it is
Ollama is a small program that downloads open-weight language models and runs them on this Mac, exposing them through a local server (`localhost:11434`) that speaks the same protocol as the OpenAI API. No account, no network after the download, nothing leaves the machine. Models live under `~/.ollama`; each is a 0.3–10 GB file.

## Why it is in KGME
Three reasons, in order of importance.
1. **Privacy.** Tier 1 data (ADR-002) may only be read by local models. Ollama is what makes "local model" a real option rather than a phrase.
2. **Embeddings.** An embedding model is tiny and turns every note in the vault into a searchable vector, so KGME can answer "what did I decide about X in June" by meaning rather than keyword — entirely on-device. This is the quietly transformative capability.
3. **Volume and resilience.** Free, unlimited, offline. Cheap classification and tagging jobs can run all day without cost or rate limits.

## What it is not
A 12B model is a competent clerk, not an analyst. It files, tags, classifies, extracts simple structure, and summarises short texts. It does not plan, does not reason through a syllabus's ambiguous prose, and does not run the executive loop. Judgment goes to Claude (ADR-007). Groq runs the same class of open models on someone else's fast hardware — quicker, rate-limited, and not private; local is slower, unlimited, and private. KGME routes by sensitivity first.

## The memory budget
The M4 Pro has 24 GB of unified memory shared between CPU and GPU. macOS, Obsidian, VS Code, Chrome and the agents take their share; a model gets roughly 12–16 GB while the machine is in normal use. In practice: 8–14B models at 4-bit run comfortably; 20-something-B models squeeze everything else; 30B+ is not used alongside normal work. The first job of setup is to *measure* this, not assume it.

## How it plugs in
The router (`router/llm.py`) treats Ollama as one more provider behind `ask()`, via the OpenAI-compatible endpoint. Any job can be pointed at the local model by changing one argument. The ledger records local calls like any other — provider, model, tokens, duration — so cost accounting stays complete even when the cost is zero.

## Rules
- Bound to localhost only; never exposed on the network.
- Model versions are pinned. Ollama tags (`qwen3:8b`) can move to a new build silently; KGME records the exact digest it tested against and updates deliberately.
- A model is a dependency (ADR-008): what, why, and where from, in the ADR that adopts it.

## Part 2 — Setup on this machine
*Pending the machine audit. Will cover: which chat model and which embedding model to pull (checked against the current library), the sanity test, confirming the endpoint, and measuring memory pressure with everything else open.*
