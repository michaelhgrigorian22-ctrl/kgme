---
id: ADR-005
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-005 — Note schema v1: frontmatter, stable identifiers, ISO dates

## Context
Notes must be commensurable — comparable and queryable across the vault like rows of a data frame — and interpretable without any plugin, in 2030 as in 2026. Michou lives between time zones; ambiguous dates are the classic long-horizon regret.

## Decision
- Every note under `memory/` carries a YAML frontmatter block (Obsidian "properties") defined in `docs/schema-v1.md`.
- Required on every note: `id`, `type`, `created`, `modified`, `status`, `tier`, `source`, `author`. Type-specific fields per the schema.
- `id` is a stable, opaque string, unique in the vault, and never changes. The filename is a human title and may change freely; scripts key off `id`.
- Dates are ISO 8601 with an explicit timezone offset, everywhere.
- The set of note types is kept under ten. The schema file carries a version; a schema change is a migration with a script, never an in-place drift.
- Wikilinks are permitted (plain text, convertible). No plugin-specific syntax in canonical notes; Dataview queries live only in dashboard notes under `memory/agent/`.

## Alternatives considered
- Free-form notes with tags only: cheap to start, impossible to query or migrate later.
- Filenames as identifiers: break on every rename.

## Consequences
Writing a note by hand requires a template (one keystroke in Obsidian). Agents validate frontmatter before writing. A linter job checks the vault against the schema.
