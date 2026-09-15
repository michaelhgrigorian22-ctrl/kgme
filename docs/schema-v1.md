---
id: SCHEMA
type: schema
status: draft
version: 1.2
created: 2026-09-09T19:50:00-07:00
modified: 2026-09-14T22:55:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME note schema — v1.2 (draft)

Governs every Markdown file under `memory/` and `docs/`, minus the exemptions in **Scope** below. Defined by ADR-005; widened from `memory/` alone to both roots by Michou's ruling of 2026-09-14 (AUDIT-0011, HANDOFF-0030). Think of the vault as a data frame: each note is a row, the frontmatter is the typed columns, the body is one free-text column, and `type` decides which columns are required. Anything a query or a script needs goes above the line; anything for a human goes below it.

## Scope

The validator (`kgme lint`, HANDOFF-0031) walks `memory/` and `docs/`. These paths are outside the rules, each for a stated reason:

| Path | Why it is exempt |
|---|---|
| `memory/templates/` | Templates carry Obsidian placeholders (`{{date:...}}`) where values go. They are not notes. |
| `memory/attachments/`, `.obsidian/` | Binaries and app state, not Markdown notes. |
| `docs/charter.md`, `docs/schema-v1.md` | The two governance singletons. Each declares its own kind (`type: charter`, `type: schema`) and is governed by its own procedure — the charter by charter §8, this file by **Versioning** below — not by the type table. Michou ruled 2026-09-14 for a path exemption over an eleventh type: the ten-type ceiling exists for the vault, and a type with exactly one file would spend it on nothing. The validator neither checks nor reports these two files. |
| `docs/archive/` | Superseded versions of documents, moved out of their home folders on purpose. An archived file may share its `id` with the live document it was a version of (`docs/archive/charter-v0.1.md` and `docs/charter.md` are both `CHARTER`), and its folder no longer matches its type. What is in the archive was valid when it was live; it is not re-validated. |

Everything else under the two roots is a note and is validated.

## Required on every note

| Field | Type | Rule |
|---|---|---|
| `id` | string | Stable, opaque, unique among validated notes. **Never changes**, even if the file is renamed. Two families: vault notes carry a second-resolution timestamp from the template when a human writes them (`20260910T143205`) and a ULID when an agent does; governance documents carry a named id — `ADR-NNN`, `HANDOFF-NNNN`, `AUDIT-NNNN`, `PLAN-*`, `READER-*`, or a singleton name (`STATUS`, `ROADMAP`, `CORRECTIONS`). Uniqueness is `blocking`; format drift is `advisory`. Scripts key off `id`, never the filename. |
| `type` | enum | One of the ten types below. |
| `created` | datetime | ISO 8601 with offset: `2026-09-09T14:32:00-07:00`. |
| `modified` | datetime | Same format. Updated by whoever edits. **Not required on the append-only types** (`decision`, `handoff`, `report`): an append-only record is never modified by construction, so the field would only ever repeat `created`. Permitted while a `decision` or `handoff` is still `proposed`; it stops changing on acceptance or adoption. (v1.2) |
| `status` | enum | Type-specific vocabulary (below). |
| `tier` | int | 2 or 3 in this vault. Tier 1 notes live in the private repository; tier 0 never exists as a note. |
| `source` | enum | `stated` (Michou said it) · `inferred` (a model concluded it) · `fetched` (retrieved from a named source, see `origin`). **Not required on `handoff`**: a handoff is an instruction, not a claim about the world. (v1.2) |
| `author` | string | `human`, or the agent name: `claude-code`, `codex`, `cowork`, `kgme`. **On `handoff` the field is `from`**, which carries the same vocabulary plus `michou` for an adopted proposal; a handoff never carries `author` as well. (v1.2) |

Optional on any note: `project` (wikilink), `people` (list of wikilinks), `tags` (list), `origin` (URL or path, required when `source: fetched`), `hash` (sha256 of a fetched source), `sources` (list of wikilinks, ids, or origins — **required when `source: inferred`**, naming every fetched or stated note the inference rests on), `supersedes` (id or list of ids).

Fields not named in this file are permitted. A document may carry what its readers need (`depends_on`, `plan_ref`, `superseded_by`, `audit_ref`, `accepted_by`, `version`, `period`). The validator reports a field it does not know as `advisory`, never `blocking`, so drift stays visible without stopping work; a field that three documents share is a candidate for the next schema version. (v1.2)

## The ten types

Paths are from the repository root.

| `type` | Lives in | Type-specific fields | `status` vocabulary |
|---|---|---|---|
| `daily` | `memory/daily/YYYY-MM-DD.md` | `date` | `open` → `closed` |
| `note` | `memory/notes/` (human) · `memory/agent/` (machine) · `memory/inbox/` (human captures) · `docs/` root, `docs/plans/`, `docs/readers/` (governance notes: STATUS, roadmap, corrections, plans, readers) | — | `draft` → `active` → `archived` |
| `reminder` | `memory/notes/` or `memory/agent/` | `due` (datetime), `repeat` (RRULE string or null), `channel` | `open` → `done` \| `dismissed` |
| `task` | `memory/notes/` or `memory/agent/` | `due` (datetime or null), `project`, `priority` (1–3) | `open` → `doing` → `done` \| `dropped` |
| `project` | `memory/notes/` | `path` (external workspace, if indexed rather than contained), `mode` (`contained` \| `indexed`) | `active` → `paused` → `done` |
| `person` | `memory/notes/` | `aliases` (list), `context` (one line) | `active` → `archived` |
| `source` | `memory/agent/` | `origin`, `hash`, `fetched` (datetime), `retention` (`discard` \| `keep`) | `quarantined` → `extracted` → `discarded` \| `kept` |
| `decision` | `docs/adr/` | `supersedes` (id, list, or null) | `proposed` → `accepted` → `superseded` |
| `handoff` | `docs/handoff/` (adopted) · `docs/handoff/proposed/` (proposals and their fates) | `from`, `to`, `completed` (required when `status: done`) | `proposed` → `open` → `done` \| `abandoned` \| `superseded` |
| `report` | `docs/audit/`, `memory/agent/` | `handoff` (id, or null for a report no handoff asked for), `period` | `final` |

Ten is the ceiling. A new type is a schema version bump with a migration. The folder rule is by `type` only; folder by `status` (a `proposed` handoff sitting in `docs/handoff/`) is not checked in v1.2, because the Phase 0 record has exceptions and the record is not edited to satisfy a validator.

## Provenance rules
- **One note, one source class.** A note is `stated`, `inferred`, or `fetched` — never mixed. Synthesis is an `inferred` note whose `sources` list points at the `fetched` and `stated` notes it draws on; that is how per-fact provenance is preserved without per-sentence markup.
- A fact is `stated` only if Michou said it. A model's conclusion is `inferred`, however confident. Anything from a file, page, or feed is `fetched` and names its `origin`.
- Promoting an `inferred` fact to `stated` requires Michou's confirmation, recorded in the ledger.
- Notes never lose provenance on edit; if a human edits a machine note, `author` stays as written and the edit is a ledger event.
- Append-only documents are repaired by changing the rule, never the record. When the schema and an accepted ADR, a done handoff, or a final report disagree, the schema moves (this is how v1.2 came to be); CLAUDE.md forbids the other direction.

## Formatting rules
- Wikilinks `[[...]]` allowed. No Dataview, Templater, or other plugin syntax in canonical notes; dashboards under `memory/agent/` may use them.
- Filenames: kebab-case, no spaces, human-readable; they are titles and may change. Dated filenames use the local date.
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
Before any agent writes to `memory/` or `docs/`, the validator (`kgme lint`, the `kgme/lint.py` module of HANDOFF-0031; the first code artefact in KGME after packaging and the ledger) checks: frontmatter present and parseable; all required fields for the type, with the v1.2 exceptions above; `id` unique across both roots minus `docs/archive/`; `type` in the allowed set; type-specific required fields present; `created`, and `modified` where required, are ISO 8601 with offset; `source: fetched` has `origin`; `source: inferred` has `sources`; the file sits in a folder its `type` allows; the exempt paths in **Scope** are skipped. Findings carry an ADR-016 class: the checks above are `blocking`; unknown fields and id-format drift are `advisory`; whitespace is `cosmetic`. Only `blocking` fails the run. The HANDOFF-0002 lint checked only three keys and does not count as validation.

## Versioning
This is v1.2 (draft). Changelog:
- **1.2 (2026-09-14)** — scope widened to `docs/`; exempt paths named with reasons (templates, attachments, the charter and this file by Michou's ruling, the archive); append-only types (`decision`, `handoff`, `report`) no longer require `modified`; `handoff` uses `from` in place of `author` and does not require `source`; `note` admitted under `memory/inbox/`, `docs/` root, `docs/plans/`, `docs/readers/`; `decision` and `handoff` gain `proposed`, `handoff` gains `superseded`; `completed` required only on `done`; unknown fields permitted and reported as `advisory`; id families named; findings classed per ADR-016; paths written from the repository root. No note was edited to fit the schema; the schema was fitted to the record (HANDOFF-0030).
- 1.1 (2026-09-10) — second-resolution human ids; `sources` list for inferred notes; one-source-class rule; validation section.
- 1.0 (2026-09-09) — initial.

Changes are recorded as a new version of this file plus, once notes exist that a change would move, a migration script under `tools/schema/`. v1.2 needs no migration: it only relaxes. Every note carries no schema version field on purpose: the vault is migrated as a whole, never left mixed.
