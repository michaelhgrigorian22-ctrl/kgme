---
id: ADR-001
type: decision
status: accepted
created: 2026-09-09T19:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-001 — Plain text in git is the source of truth

## Context
KGME must remain understandable and recoverable over a multi-year horizon, across changes of tools, models, and Michou's own habits. Apps die, subscriptions lapse, formats rot. Every agent surface in use (Claude Code, Codex, Cowork, Python scripts) reads and writes files natively.

## Decision
The canonical state of KGME is a git repository of plain-text files: Markdown with YAML frontmatter for knowledge and state, YAML/TOML for configuration, JSONL for the append-only ledger, SQLite for structured, queryable data. Obsidian, VS Code, and every agent are views or workers over these files, never the system itself.

## Alternatives considered
- A database-backed app or a hosted "second brain" service: faster to start, opaque, lock-in, dies with the vendor.
- An agent framework (LangGraph, CrewAI, n8n) as the core: speed at the cost of understandability and dependency mass.

## Consequences
Anything not representable as plain text in git is treated as at risk and kept out of canonical state. Tooling choices become reversible. Michou can read the whole system with a text editor.
