---
id: ADR-003
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-003 — Append-only ledger as truth; notes as derived views; provenance on every fact

## Context
Over years, the question "why does KGME believe X, and who decided Y" must be answerable. Mutable notes lose history; mutable logs lose trust. Michou endorsed the accounting framing: journal entries are never edited, corrections are posted.

## Decision
- KGME keeps an append-only event log (`logs/*.jsonl`): every run, tool call, captured fact, approval, and correction, timestamped in ISO 8601 with offset.
- The log is the truth. Notes under `memory/` are derived views and may be regenerated from the log plus sources.
- A correction or a "forget" is a new reversing entry followed by a rebuild of the affected views — never an edit to history.
- Every machine-written fact carries `source:` — `stated` (Michou said it), `inferred` (a model concluded it), or `fetched` (retrieved from a named source) — plus `author:` and a timestamp.
- Human interventions on critical loops (approvals, rejections, overrides) are first-class events, so the system can learn from them.

## Alternatives considered
- Mutable notes as truth with git history as the log: git records *that* a line changed, not *why* or by whose authority.
- A database with soft deletes: hides the journal behind a query layer; harder to read cold.

## Consequences
Log lines are never edited. Storage grows; that is acceptable and cheap. The schema (ADR-005) must carry the provenance fields. Regenerable views must actually be regenerable — a rebuild job exists before any view is trusted.
