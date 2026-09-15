---
id: READER-OBSIDIAN
type: note
status: active
created: 2026-09-09T20:00:00-07:00
modified: 2026-09-15T00:05:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — Obsidian in KGME

*Part 1 (mental model) written 2026-09-09. Part 2 (setup on this machine) written 2026-09-15, after the machine audit (AUDIT-0001) and schema v1.2.*

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

Ten minutes, once. Your act, not an agent's (ADR-004): the vault is your folder. Do it in any evening before HANDOFF-0035 (seed the vault); earlier is better, because the daily-note habit and the ten friction entries that 0035 needs take days to accumulate, and Obsidian is the tool that habit lives in.

**1. Open the right folder as the vault.** Launch Obsidian → *Open folder as vault* → choose `~/Projects/Automate/memory`. The vault is `memory/`, not the repo root: `.obsidian/` then lands at `memory/.obsidian/`, where `.gitignore` already expects it, and Obsidian never indexes `docs/`, `kgme/`, or `logs/`. Decline Sync and Publish when offered; git is the sync.

**2. Settings → Files and links.**
- *Default location for new notes:* in the folder specified below → `notes`.
- *Use [[Wikilinks]]:* on. *New link format:* shortest path when possible.
- *Automatically update internal links:* on (renames are free; `id` never changes, so nothing breaks).
- *Default location for new attachments:* in the folder specified below → `attachments` (excluded from validation by schema v1.2).
- *Deleted files:* confirm it reads "move to system trash" (the default). Never Obsidian's own `.trash`, which would create an untracked folder inside the vault.
- *Detect all file extensions:* off.

**3. Settings → Core plugins.** On: Files, Search, Quick switcher, Command palette, Backlinks, Outgoing links, Properties view, Page preview, Tags, Daily notes, Templates. Off: Sync, Publish, Slides, Canvas (for now), Unique note creator (the template already generates ids). Graph is optional and mostly decorative.
- *Templates:* template folder `templates`; date format `YYYY-MM-DD`; time format `HH:mm:ss`. The shipped templates override these with explicit formats (`{{date:YYYY-MM-DDTHH:mm:ssZ}}` gives ISO 8601 with offset, exactly what the schema requires), so the defaults rarely matter.
- *Daily notes:* new file location `daily`; date format `YYYY-MM-DD` (the filename is the local date, ADR-005); template file location `templates/daily` once HANDOFF-0034 ships it, with `reminder.md` and `task.md`. Until then the only template is `note.md`.
- *Hotkeys:* give *Templates: Insert template* a key (⌘⇧T is free). Every new note is: quick switcher → new name → insert template → write below the line.

**4. Settings → Editor.** *Properties in document:* visible. Leave *Strict line breaks* off. Everything else is taste.

**5. Two habits that keep the validator green.**
- Never edit `created`, `modified`, `due`, or `completed` through the property widget. Obsidian's date-time widget writes `YYYY-MM-DDTHH:mm` without the offset, and the validator will flag it as `blocking`. Edit those four in source mode (⌘E toggles) or leave them to the template.
- `id` is text, not a number, and is never edited. If Obsidian ever offers to "fix" a property type, decline; the types file is committed so the answer sticks.

**6. Commit what Obsidian created.** After the first open, `memory/.obsidian/` holds `app.json`, `appearance.json`, `core-plugins.json`, `daily-notes.json`, `templates.json`, `hotkeys.json`, and `types.json`; `workspace.json` and `cache/` are ignored. Commit the rest as `vault: Obsidian opened at memory/, core plugins and settings`. From then on the vault opens identically on any machine that clones the repo. Tell Claude Code you did it so its next commit doesn't sweep the files in with unrelated work.

**What not to do yet.** No community plugins in week one, Dataview included: each plugin is a decision (see the rules above) and belongs in the friction log first. No theme yet either; the cockpit's cyberpunk direction (0036) decides the palette and Obsidian follows it, not the other way around. No notes under `agent/` by hand: that folder is written by agents and read by you.

**Check.** `kgme lint` (from HANDOFF-0031) exits 0 with the vault open in Obsidian. Until 0031 exists, the check is that `memory/.obsidian/` contains no file the `.gitignore` does not name and every note you create starts from the template.
