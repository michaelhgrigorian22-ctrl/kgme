---
id: ADR-006
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-006 — Structure by type, relate by link, classify by property

## Context
Deep folder hierarchies force one classification on notes that belong to many contexts, and they rot. Michou's existing files, worked on natively by Claude Code, will need reorganising to fit (migration plan pending).

## Decision
- Folders answer exactly one question: *what kind of thing is this?* (`notes/`, `daily/`, `agent/`, `inbox/`, ...). They never encode project, topic, or state.
- Relationships are links (`[[...]]`); attributes (project, topic, status, tier) are frontmatter properties.
- Existing project folders (thesis, coverage, coursework, portfolio) need not be swallowed into the vault: KGME may *index* an external workspace — know it exists, what is due, where the latest file is — without *containing* it. Contain-vs-index is decided per folder in the migration plan.

## Alternatives considered
- Mirror Michou's mental categories as folders: one axis, endless reshuffling.
- Everything in one flat folder with tags: workable, but the type boundary is needed for ADR-004's authorship rule.

## Consequences
The vault stays shallow. Views (by project, by due date) are queries, not folders. The migration plan produces an inventory and a contain/index decision per existing folder.
