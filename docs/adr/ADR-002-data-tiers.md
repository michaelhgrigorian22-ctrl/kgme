---
id: ADR-002
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-002 — Data classification tiers, enforced by topology

## Context
Michou's stated policy: bank and portfolio information must not leave the machine by default (he may explicitly choose to share a single position); moderately personal data may be used because usefulness requires it; anything so sensitive that it is a security risk regardless of safeguards must stay out of the system entirely.

## Decision
Four tiers, each living in a different place, so the boundary is enforced by the filesystem and the router's policy layer rather than by prompt wording.

| Tier | Contents | Location | Models permitted |
|---|---|---|---|
| 0 — Excluded | Credentials, account numbers, session cookies, OAuth tokens, secret URLs | Password manager / Keychain only. The vault may hold a pointer, never the value | None |
| 1 — Local-only | Portfolio, positions, balances, financial figures | Its own repository (`memory/private/`, elsewhere on disk), never inside the main repo, never on GitHub in plaintext | Local (Ollama) only. Cloud jobs run with a filesystem view that excludes it |
| 2 — Personal | Notes, tasks, reminders, calendar, coursework, correspondence | Main vault | Claude, Codex, and providers on an explicit allowlist |
| 3 — Public | Web content, filings, anything already public | Anywhere | Any model, including free tiers |

Sharing a Tier 1 fact outward is a per-item, per-request, human-confirmed act, written to the ledger. Never a standing permission.

## Alternatives considered
- One vault with sensitivity tags in frontmatter: relies on every job honouring the tag; a single miss leaks. Rejected.
- Encrypt everything, share nothing: makes the system useless for its purpose.

## Consequences
Two repositories. The Tier 1 backup question (strictly local vs encrypted off-machine) is open and must be decided before Tier 1 data is entered. Every tool declares the highest tier it may read.
