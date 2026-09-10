---
id: READER-OBSIDIAN
type: note
status: draft
created: 2026-09-09T20:00:00-07:00
modified: 2026-09-09T20:00:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — Obsidian in KGME

*Part 1 (mental model) written 2026-09-09. Part 2 (setup on this machine) is added after the machine audit.*

## What it is
Obsidian is a desktop editor that opens a folder of plain Markdown files and calls it a vault. It adds what a folder lacks: links between notes, backlinks (who points here), a graph of the whole, daily notes, and *properties* — the YAML frontmatter block at the top of each file, shown as a form. It does not store anything anywhere else. Close Obsidian and the vault is still a folder; open the same folder in VS Code and it is the same files.

It does **not** track actions, sync by itself, or know about anything outside the folder. Tracking is git's job; acting is the agents' job.

## Why it is in KGME
KGME's memory layer (ADR-001) is a folder of Markdown with frontmatter (ADR-005). Obsidian is the best available *window* onto exactly that: it makes the schema visible as properties, makes links navigable, and — with one plugin later — lets the vault be queried like a data frame. It is a view, not the system. If Obsidian disappeared tomorrow, KGME would lose a nice window and nothing else.

## How you will use it
- **Reading:** the daily note is the front page. Backlinks show what touches a project or person. The graph is occasionally useful, mostly decorative.
- **Writing:** every new note starts from a template (`memory/templates/`) so the frontmatter is always there. You write below the line; the properties above it are for machines and queries.
- **Overseeing agent output:** everything agents write lands in `memory/agent/` with `author:` set to the agent (ADR-004). You can read it, query it, and delete any of it without loss. You never find your own notes rewritten.
- **Dashboards (later):** query notes under `agent/` — "open reminders by due date", "everything fetched this week" — built with Dataview, which is the only place plugin syntax is allowed.

## Rules that keep it durable
- Canonical notes must read correctly with zero plugins installed.
- Rename files freely; never change an `id`.
- The `.obsidian/` settings folder is partly committed (app, plugins list) and partly ignored (workspace layout) so the vault opens the same way on any machine without committing noise.
- Community plugins are decisions, not conveniences: each one is something canonical notes might come to depend on. Week one is core plugins only.

## What to expect in the first week
It will feel empty, and slightly pedantic, because of the frontmatter. That is correct. The value appears when the first agent job writes fifty structured notes and you can ask the vault a question instead of scrolling.

## Part 2 — Setup on this machine
*Pending the machine audit (handoff 0001). Will cover: opening the vault at `memory/`, the exact settings, core plugins to enable, the `.obsidian/` gitignore, and the template shortcut.*
