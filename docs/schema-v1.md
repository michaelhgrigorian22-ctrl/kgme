---
id: SCHEMA
type: schema
status: draft
version: 1.1
created: 2026-09-09T19:50:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME note schema — v1 (draft)

Governs every Markdown file under `memory/`. Defined by ADR-005. Think of the vault as a data frame: each note is a row, the frontmatter is the typed columns, the body is one free-text column, and `type` decides which columns are required. Anything a query or a script needs goes above the line; anything for a human goes below it.

## Required on every note

| Field | Type | Rule |
|---|---|---|
| `id` | string | Stable, opaque, unique in the vault. **Never changes**, even if the file is renamed. Humans get a second-resolution timestamp id from the template (`20260910T143205`); agents generate a ULID. A validator rejects duplicate ids. Scripts key off `id`, never the filename. |
| `type` | enum | One of the ten types below. |
| `created` | datetime | ISO 8601 with offset: `2026-09-09T14:32:00-07:00`. |
| `modified` | datetime | Same format. Updated by whoever edits. |
| `status` | enum | Type-specific vocabulary (below). |
| `tier` | int | 2 or 3 in this vault. Tier 1 notes live in the private repository; tier 0 never exists as a note. |
| `source` | enum | `stated` (Michou said it) · `inferred` (a model concluded it) · `fetched` (retrieved from a named source, see `origin`). |
| `author` | string | `human`, or the agent name: `claude-code`, `codex`, `cowork`, `kgme`. |

Optional on any note: `project` (wikilink), `people` (list of wikilinks), `tags` (list), `origin` (URL or path, required when `source: fetched`), `hash` (sha256 of a fetched source), `sources` (list of wikilinks or origins — **required when `source: inferred`**, naming every fetched or stated note the inference rests on), `supersedes` (id).

## The ten types

| `type` | Lives in | Type-specific fields | `status` vocabulary |
|---|---|---|---|
| `daily` | `daily/YYYY-MM-DD.md` | `date` | `open` → `closed` |
| `note` | `notes/` (human) or `agent/` (machine) | — | `draft` → `active` → `archived` |
| `reminder` | `notes/` or `agent/` | `due` (datetime), `repeat` (RRULE string or null), `channel` | `open` → `done` \| `dismissed` |
| `task` | `notes/` or `agent/` | `due` (datetime or null), `project`, `priority` (1–3) | `open` → `doing` → `done` \| `dropped` |
| `project` | `notes/` | `path` (external workspace, if indexed rather than contained), `mode` (`contained` \| `indexed`) | `active` → `paused` → `done` |
| `person` | `notes/` | `aliases` (list), `context` (one line) | `active` → `archived` |
| `source` | `agent/` | `origin`, `hash`, `fetched` (datetime), `retention` (`discard` \| `keep`) | `quarantined` → `extracted` → `discarded` \| `kept` |
| `decision` | `docs/adr/` | `supersedes` | `accepted` → `superseded` |
| `handoff` | `docs/handoff/` | `from`, `to`, `completed` | `open` → `done` \| `abandoned` |
| `report` | `docs/audit/`, `agent/` | `handoff` (id), `period` | `final` |

Ten is the ceiling. A new type is a schema version bump with a migration.

## Provenance rules
- **One note, one source class.** A note is `stated`, `inferred`, or `fetched` — never mixed. Synthesis is an `inferred` note whose `sources` list points at the `fetched` and `stated` notes it draws on; that is how per-fact provenance is preserved without per-sentence markup.
- A fact is `stated` only if Michou said it. A model's conclusion is `inferred`, however confident. Anything from a file, page, or feed is `fetched` and names its `origin`.
- Promoting an `inferred` fact to `stated` requires Michou's confirmation, recorded in the ledger.
- Notes never lose provenance on edit; if a human edits a machine note, `author` stays as written and the edit is a ledger event.

## Formatting rules
- Wikilinks `[[...]]` allowed. No Dataview, Templater, or other plugin syntax in canonical notes; dashboards under `agent/` may use them.
- Filenames: kebab-case, no spaces, human-readable; they are titles and may change.
- One note per subject. A note about X goes in X's file.

## Example

```
---
id: 20260910T143205
type: reminder
created: 2026-09-09T14:32:00-07:00
modified: 2026-09-09T14:32:00-07:00
status: open
tier: 2
source: stated
author: human
due: 2026-09-14T09:00:00-07:00
repeat: null
channel: phone
project: "[[thesis]]"
---
Email reader about the chapter 2 draft.
```

## Validation
Before any agent writes to `memory/`, a validator (`tools/schema/lint.py`, the first code artefact in KGME) checks: frontmatter present and parseable; all required fields; `id` unique across the vault; `type` in the allowed set; type-specific required fields present; `created`/`modified` are ISO 8601 with offset; `source: fetched` has `origin`; `source: inferred` has `sources`; the file sits in a folder its `type` and `author` allow. The HANDOFF-0002 lint checked only three keys and does not count as validation.

## Versioning
This is v1.1 (draft). Changelog: 1.1 (2026-09-10) — second-resolution human ids; `sources` list for inferred notes; one-source-class rule; validation section. 1.0 (2026-09-09) — initial. Changes are recorded as a new version of this file plus a migration script under `tools/schema/`. Every note carries no schema version field on purpose: the vault is migrated as a whole, never left mixed.
