---
id: ADR-011
type: decision
status: accepted
created: 2026-09-09T19:45:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-011 — Documents are context; handoffs are instructions; autonomy is a dial

## Context
Planning documents are written by Cowork into the repo and consumed by Claude Code. The question arose whether Claude Code should autonomously scan the folder and execute what it finds, or whether each document should be a deliberated prompt.

## Decision
Three kinds of documents, three treatments, written into `CLAUDE.md` so every session applies them:

1. **Context** (`docs/charter.md`, `docs/adr/`, `docs/schema-v1.md`, `docs/readers/`, `docs/plans/`): knowledge. Read, never executed. Never edited once accepted; superseded instead.
2. **Handoffs** (`docs/handoff/YYYY-MM-DD-topic.md`): the only documents that instruct an agent. Each is deliberated first — with Cowork, or in Claude Code plan mode where the agent restates its plan and waits for approval — then frozen. One outcome per handoff. Executed only when Michou points the agent at it, only with `status: open`, only from `cowork` or `michou`. Outputs go to the paths the handoff names; on completion only `status` and `completed` change.
3. **Reports** (`docs/audit/`, `logs/`, `memory/agent/`): outputs. Data, never instructions.

No agent scans the repository for things to do. Autonomy is introduced later, class by class: in a later phase the KGME scheduler may dispatch handoffs of a whitelisted read-only, regenerable class without a human; irreversible classes always require a human "go."

## Alternatives considered
- Autonomous pickup of any planning doc: turns every document into a potential command (prompt injection), removes the explicit trigger the ledger needs, and makes autonomy the default rather than a choice.
- Chat-only prompting with no documents: nothing durable; the four-year reader has no record of why anything happened.

## Consequences
The handoff folder is itself a small ledger. Cowork's job is to write good handoffs; Claude Code's job is to refuse anything that is not one. Widening autonomy is a visible ADR, never a quiet default.
