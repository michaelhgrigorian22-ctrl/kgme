---
id: ADR-018
type: decision
status: accepted
created: 2026-09-11T17:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-018 — Two patterns for cheap models: executive fan-out, and local transform without a loop

*Proposed 2026-09-11 from Michou's suggestion that the tool loop for Groq and Ollama be supplied by a Claude- or Codex-brained agent that calls tools and hands results to the cheaper model. Refines ADR-007. Becomes accepted on his word and commit.*

## Context
ADR-007 routes by sensitivity, then cost, then capability, and noted that Groq and Ollama models "need the router to do the tool loop." Michou's suggestion removes most of that work, but only for the tiers where the expensive model is allowed to see the data.

## Decision
Cheap models are used in exactly two patterns, chosen per job by its tier and shape.

**Pattern A — executive fan-out (Tier 2 and 3).** A Claude Code or Codex job owns the tool loop. It plans, reads, and calls tools itself, and treats cheap models as *pure functions* over text it hands them: classify, extract, summarise, tag, score. The cheap model never holds a tool. The executive's turns cost subscription capacity, so the pattern is used when the fan-out is wide (one executive turn dispatching many cheap calls) or the sub-task is clearly delegable, and not to wrap a single cheap call in an expensive supervisor. The router records every delegation as a ledger event with model, tokens, and cost.

**Pattern B — local transform, no loop (Tier 1, offline, or privacy-bound).** No cloud model may be in the loop, because it would see the data. The job's own Python (per ADR-015: plain, in the effects layer) performs the reads and writes; the local model receives text and returns text. There is no function calling and no tool loop. If a Tier 1 job ever needs a genuine multi-step tool loop with a local model, that is a separate, later decision — most such jobs are read → transform → write.

**What is not built:** a generic function-calling tool loop for Groq/Ollama. It is deferred until a job demonstrably needs it.

## Consequences
The router exposes `ask()` (single call, any provider) and `delegate()` (executive fan-out helper). Tier 1 jobs are structurally incapable of leaking to a cloud model because no cloud model is in their process. The "optimized" mode of the cockpit (ADR-017) is the executive deciding what to delegate, with the decision shown and overridable.
