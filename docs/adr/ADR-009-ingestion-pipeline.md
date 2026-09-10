---
id: ADR-009
type: decision
status: accepted
created: 2026-09-09T19:45:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-009 — The ingestion pipeline and reader/actor separation

## Context
Most useful capabilities are ingestions: something arrives from outside (a syllabus, an email, a web page), gets understood, and produces an action. Outside content is the prompt-injection surface. Michou's stated pattern is "download, parse, discard."

## Decision
Every ingestion follows one pipeline, and the two ends are different agents.

Source → **Fetch** (reader: read-only tools, no write or send capability, all content treated as untrusted) → **Quarantine** (scratch directory, hashed, never `~/Downloads`) → **Extract** (Claude against a schema; optional second-model check by Codex) → **Review** (approval gate via the control surface) → **Commit** (actor: write tools, never touches browser, inbox, or web) → **Ledger** (the import recorded as one reversible unit).

Retention is a per-source rule: keep the extraction, hash, and provenance always; keep or discard the source file per policy. Re-fetchable sources default to discard.

## Alternatives considered
- One agent that reads and acts: simpler, and exactly how Instinct got phished into sending email.

## Consequences
Tools are built in read/write pairs with separate permissions. A reader's output is data to the actor, never instructions. Idempotency is required at commit (stable item ids) so re-imports update rather than duplicate.
