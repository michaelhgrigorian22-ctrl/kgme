---
id: HANDOFF-0030
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: cowork
tier: 2
status: done
completed: 2026-09-20T15:35:00-07:00
depends_on: null
plan_ref: PLAN-PHASE-1 step 5
---

# Handoff 0030 (proposed, for Cowork and Michou) — Schema v1.2 and the `docs/` frontmatter repair

## Why
Michou ruled 2026-09-14 that the validator covers `memory/` and `docs/` and that `docs/` is repaired now. Applied as written, `schema-v1.md` fails on KGME's own documents: the eighteen ADRs lack `modified`; `docs/charter.md` is `type: charter`, an eleventh type against the ten-type ceiling; STATUS, roadmap, and both plans are `type: note` outside `notes/` or `agent/`; `memory/inbox/friction-log.md` is a human `note` in a folder the type table does not admit; `memory/templates/note.md` carries Obsidian placeholders that are not ISO dates. The repair collides with CLAUDE.md, which says accepted ADRs are never edited. The resolution is to change the schema rule, not the ADRs. This is a document handoff: Cowork drafts the schema change, Michou approves the diffs, Claude Code applies them.

## What (schema v1.2, proposed rules)
1. `modified` is not required on append-only types (`decision`, `handoff`, `report`): an append-only record is never modified by construction. No ADR file is touched.
2. `note` is permitted under `docs/` and `docs/plans/` (governance notes: STATUS, roadmap, plans) and under `memory/inbox/` (human captures). The `note` row's "Lives in" column gains those three locations.
3. `docs/charter.md` and its `type: charter`: **pending Michou's separate ruling (2026-09-14).** The options are a path exemption with the reason written into the schema (the charter is governed by charter §8), or an eleventh type by ADR. Until he rules, the validator treats the charter as a path exemption and reports it as `advisory`, never `blocking`.
4. `memory/templates/` is excluded from validation by path; templates are not notes.
5. Any `docs/` file still failing after rules 1 to 4 (a missing `status`, a naive date) is fixed by a minimal frontmatter edit shown as a diff per ADR-004. Expected set after a dry run of the validator: to be listed by HANDOFF-0031's first run and attached here.
6. `schema-v1.md` version line becomes 1.2 with a changelog entry; `status: draft` stays until Michou says otherwise.

## Outputs
`docs/schema-v1.md` (v1.2, diff approved), the minimal frontmatter diffs on non-ADR `docs/` files (approved), nothing under `docs/adr/`.

## Acceptance test
`kgme lint` (from 0031) on `memory/` and `docs/` exits 0 with zero `blocking` findings and no ADR modified (`git diff --stat docs/adr/` is empty).

## Reviewer
Michou (canonical documents, ADR-004). Codex checks that no ADR changed.

## Reversibility
`git revert`; the schema returns to 1.1.

## Needs from Michou
Approval of the schema diff and each frontmatter diff. A ruling if he prefers an eleventh `charter` type by ADR instead of the path exemption.

## Report
Cowork records the change in `docs/corrections.md` as a schema version, not a correction. Claude Code sets `status: done`, `completed:` on adoption. Commit `schema: v1.2, append-only types drop modified, docs/ notes admitted (HANDOFF-0030)`.
