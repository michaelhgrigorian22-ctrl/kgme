---
id: READER-OBSIDIAN
type: note
status: active
created: 2026-09-09T20:00:00-07:00
modified: 2026-10-21T02:40:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — Obsidian in KGME

*Part 1 (mental model) written 2026-09-09. Part 2 (setup on this machine) written 2026-09-15, after the machine audit (AUDIT-0001) and schema v1.2; its vault folder moved to the repository on 2026-10-21 (HANDOFF-0051), and its daily-note habit is superseded by `kgme capture daily` and `kgme daily` (HANDOFF-0050). Part 3 (the atlas) written 2026-10-21 for HANDOFF-0051.*

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

**1. Open the right folder as the vault.** Launch Obsidian → *Open folder as vault* → choose `~/Projects/KGME/brain`, the repository itself (HANDOFF-0051; until then the vault was `memory/`). Its settings are already there, in `.obsidian/` at the top, tracked: they point new notes at `memory/notes`, attachments at `memory/attachments`, daily notes and templates at `memory/daily` and `memory/templates`, and exclude `.venv`, `logs/`, `kgme/`, `jobs/`, `control/`, `tests/`, `cockpit/`, and the caches, so Obsidian indexes the documents, the vault, and the atlas. Decline Sync and Publish when offered; git is the sync.

**2. Settings → Files and links.**
- *Default location for new notes:* in the folder specified below → `memory/notes`.
- *Use [[Wikilinks]]:* on. *New link format:* shortest path when possible.
- *Automatically update internal links:* on (renames are free; `id` never changes, so nothing breaks).
- *Default location for new attachments:* in the folder specified below → `memory/attachments` (excluded from validation by schema v1.2).
- *Deleted files:* confirm it reads "move to system trash" (the default). Never Obsidian's own `.trash`, which would create an untracked folder inside the vault.
- *Detect all file extensions:* off.

**3. Settings → Core plugins.** On: Files, Search, Quick switcher, Command palette, Backlinks, Outgoing links, Properties view, Page preview, Tags, Daily notes, Templates. Off: Sync, Publish, Slides, Canvas (for now), Unique note creator (the template already generates ids). Graph is optional and mostly decorative.
- *Templates:* template folder `memory/templates`; date format `YYYY-MM-DD`; time format `HH:mm:ss`. The shipped templates override these with explicit formats (`{{date:YYYY-MM-DDTHH:mm:ssZ}}` gives ISO 8601 with offset, exactly what the schema requires), so the defaults rarely matter.
- *Daily notes:* new file location `memory/daily`; date format `YYYY-MM-DD` (the filename is the local date, ADR-005); template file `memory/templates/daily.md`. Since HANDOFF-0050, `kgme daily` drafts the evening note and `kgme capture daily` adds your lines, so the core plugin is a way to open today's note, not to start it.
- *Hotkeys:* give *Templates: Insert template* a key (⌘⇧T is free). Every new note is: quick switcher → new name → insert template → write below the line.

**4. Settings → Editor.** *Properties in document:* visible. Leave *Strict line breaks* off. Everything else is taste.

**5. Two habits that keep the validator green.**
- Never edit `created`, `modified`, `due`, or `completed` through the property widget. Obsidian's date-time widget writes `YYYY-MM-DDTHH:mm` without the offset, and the validator will flag it as `blocking`. Edit those four in source mode (⌘E toggles) or leave them to the template.
- `id` is text, not a number, and is never edited. If Obsidian ever offers to "fix" a property type, decline; the types file is committed so the answer sticks.

**6. Commit what Obsidian changes.** The settings in `.obsidian/` are tracked (`app.json`, `appearance.json`, `core-plugins.json`, `daily-notes.json`, `graph.json`, `hotkeys.json`, `templates.json`); `workspace.json` and `cache/` are ignored. If Obsidian adds a file there (`types.json` after the first property edit), commit it on its own. From then on the vault opens identically on any machine that clones the repo. The workspace file Obsidian kept under `memory/` before the move is untracked and can be deleted.

**What not to do yet.** No community plugins in week one, Dataview included: each plugin is a decision (see the rules above) and belongs in the friction log first. No theme yet either; the cockpit's cyberpunk direction (0036) decides the palette and Obsidian follows it, not the other way around. No notes under `agent/` by hand: that folder is written by agents and read by you.

**Check.** `kgme lint` (from HANDOFF-0031) exits 0 with the vault open in Obsidian, and `git status` shows nothing in `.obsidian/` that the `.gitignore` does not name.

## Part 3 — The atlas: the graph as a lens on KGME (HANDOFF-0051)

Obsidian draws only links written inside Markdown notes, and KGME's documents name each other in backticks, which it does not read; code it cannot see at all. So `kgme atlas` writes `atlas/` at the repository's top: one short generated note per part of KGME, each linking its neighbours with `[[...]]`. The parts:
- each top-level folder;
- each module in `kgme/`, `jobs/`, and `control/`, linked to what it imports (read, never run), to the tests that import it, and to the ADRs its text cites;
- each ADR, handoff, plan row, reader, and audit, linked by what each names: `depends_on`, `plan_ref`, `Outputs`, `report`, `supersedes`, and the ADRs cited.

Each note opens with one line saying what the part is and a link to the real file. Its `kind` property (folder, module, test, job, handoff, adr, plan, reader, audit, skill, project) colours the saved graph view, which is filtered to `path:atlas`.

You never edit it. It is regenerated in the background after every commit, by a line in the post-commit hook, and Obsidian redraws when the files change. It is ignored by git, since it can be regenerated from the tree at any commit, and `kgme clean atlas --yes` may empty it. Run `kgme atlas` by hand any time; a second run on the same tree writes nothing.

**Other projects, later and only when you list them.** `kgme.toml` `[atlas] projects` names other folders by path. For each, the atlas reads its structure only: the top-level folder names, its `README.md`'s links, and the KGME parts that README names (`kgme brief`, `kgme/ledger.py`). It never reads another file's contents, and it refuses a project that holds Tier 1 data (ADR-002). Each project is one node, linked to the KGME parts it uses.
