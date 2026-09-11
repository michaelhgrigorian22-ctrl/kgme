---
id: ADR-012
type: decision
status: accepted
created: 2026-09-10T09:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: ADR-004 (partial)
---

# ADR-012 — Three data classes; the ledger is durable, never regenerable; forget vs purge

*Proposed in response to the external audit of 2026-09-10 (finding 1). Becomes accepted on Michou's word and commit.*

## Context
ADR-003 makes the ledger authoritative, including approvals. ADR-004 listed `logs/` among regenerable machine output, and `.gitignore` excluded `logs/*.jsonl`. Taken together the only record of an approval was deletable and unbacked — a contradiction. ADR-003 also left "forget" ambiguous between hiding a fact and destroying it.

## Decision
Three classes, each with its own backup and restoration rule:

| Class | Examples | Rule |
|---|---|---|
| **Canonical human documents** | `docs/`, `memory/notes/`, `memory/inbox/`, `memory/daily/` | Protected (ADR-004). In git. Backed up. Never overwritten by an agent without an approved diff. |
| **Durable event records** | `logs/ledger/*.jsonl`, `docs/corrections.md`, `docs/handoff/`, `docs/audit/` | Append-only. **Never deleted, never "regenerated."** Tracked in git (ledger files rotate monthly) until volume forces a separate store — at which point they get their own backup rule, never a weaker one. |
| **Disposable derived outputs** | `memory/agent/`, dashboards, caches, embeddings indexes | Regenerable from the two classes above plus sources. Deletable at any time. |

`.gitignore` is corrected: ledger files are tracked; only secrets, caches, and Obsidian workspace state are ignored.

**Forget vs purge.** `forget` is a reversing event: the fact is suppressed from every derived view and every future prompt, and history retains it. `purge` physically removes content from history; it is permitted only for Tier 0 leakage or an explicit privacy demand from Michou, requires his approval per instance, is itself recorded as a purge event carrying only a hash of what was removed and the reason, and — because the ledger is in git — implies a history rewrite, which is the one sanctioned exception to "never force-push," performed by Michou, not an agent.

## Alternatives considered
- Ledger outside git with its own backup: workable later; today it would be the only unbacked durable record on the machine.
- Treating everything under `logs/` as disposable: the contradiction this ADR removes.

## Consequences
ADR-004's list of regenerable locations no longer includes `logs/`. The ledger has a storage cost in git; accepted. A restore test (ADR-013) must show the ledger survives a machine loss.
