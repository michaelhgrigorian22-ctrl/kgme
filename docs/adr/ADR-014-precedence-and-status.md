---
id: ADR-014
type: decision
status: proposed
created: 2026-09-10T09:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-014 — Precedence between documents, and one current status

*Proposed in response to the external audit of 2026-09-10 (finding 7). Becomes accepted on Michou's word and commit.*

## Context
Eleven ADRs were accepted while the charter and schema were still drafts; readers had to reconstruct current status across the fix plan, two reviews, the corrections record and abandoned proposals. Ids were assigned without checking existing ones. The global memory index prescribed for every session points at a path that does not exist.

## Decision
- **Precedence when documents disagree:** `CLAUDE.md` non-negotiables → accepted ADRs → accepted charter → drafts. Once the charter is accepted it moves above the ADRs: ADRs implement the charter, and an ADR that conflicts with it is superseded, not the other way round. Drafts guide and never bind.
- **ADR lifecycle:** `proposed` → `accepted` → `superseded`. Acceptance is Michou's explicit word plus the commit; an agent never accepts an ADR.
- **`docs/STATUS.md` is the single current disposition** for every unresolved finding, proposal, decision and correction, each pointing at its governing record. It is updated whenever a status changes. Historical records (plans, reviews, reports, corrections, abandoned proposals) are never edited to reflect later events; STATUS.md is where "what is true now" lives. The claude.ai Project mirror is derived from it.
- **Ids:** whoever assigns a handoff, audit or ADR id lists the relevant folders first and takes the next free number. Until the ledger issues ids, this is a checked discipline, and a collision is recorded as a correction.
- **Global instruction files** (`~/.claude/CLAUDE.md`, `~/AGENTS.md`) may not point at paths that do not exist; a dangling pointer is a defect to fix, not a note to carry.

## Consequences
The charter's acceptance becomes the next governance milestone rather than a formality. STATUS.md is created now and maintained by hand until a job maintains it.
