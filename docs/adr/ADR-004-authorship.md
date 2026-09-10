---
id: ADR-004
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-004 — Human-authored vs machine-authored; canonical vs regenerable

## Context
A vault silts up with confident machine output nobody wrote. Michou must be able to delete a bad month of agent output without fear, and must never find his own words rewritten.

## Decision
- Human-authored content (`docs/`, `memory/notes/`, `memory/inbox/`, `memory/daily/`) is **canonical**: protected, backed up, never overwritten by an agent without a shown diff and explicit approval.
- Machine-authored content (`memory/agent/`, `logs/`, generated dashboards) is **regenerable**: reproducible from the ledger plus sources, deletable at any time without loss.
- The two never share a folder. Frontmatter `author:` records the writer.

## Alternatives considered
- Mixed folders with an `author` tag only: the tag is easy to ignore; folder boundaries are enforceable by hooks.

## Consequences
Every agent capability that writes must target a machine-authored location. Promotion of machine output to canonical status is a deliberate human act (move + edit), recorded in the ledger.
