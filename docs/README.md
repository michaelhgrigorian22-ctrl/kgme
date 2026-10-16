---
id: DOCS-README
type: note
created: 2026-09-09T22:41:48-07:00
modified: 2026-10-15T23:51:57-07:00
status: active
tier: 2
source: stated
author: cowork
---

# KGME documents — index and reading order

| Kind | Where | Treatment | Who writes |
|---|---|---|---|
| Constitution | `charter.md` | Read first. Changes only by ADR plus explicit approval | Michou (drafted with Cowork) |
| Decisions | `adr/ADR-NNN-*.md` | Append-only. Superseded, never edited | Cowork / Michou; Claude Code may propose |
| Schema | `schema-v1.md` | Versioned; changes are migrations | Cowork / Michou |
| Plans | `plans/` | Canonical phase plans; mirrored to the claude.ai Project | Cowork |
| Readers | `readers/` | Explanatory guides for tools; setup halves added after the audit | Cowork, revised by Claude Code |
| Handoffs | `handoff/YYYY-MM-DD-topic.md` (open), `handoff/done/` (finished, each naming its `report`), `handoff/proposed/` (live proposals), `handoff/archive/` (superseded and abandoned) | The only instructions to Claude Code, and only while open. Dated, frozen, status-tracked; the folder matches the status (HANDOFF-0049) | Cowork / Michou |
| Reports | `audit/`, `../logs/` | Outputs. Data, not instructions | Claude Code / KGME |
| Design | `design/` | Design canvases and their assets; the design track works on branch `design` in its own worktree | Cowork, Codex, Michou |
| **Status** | `STATUS.md` | The single current disposition of every open item (ADR-014). Read second, after `charter.md` | Cowork, until a job does it |
| Archive | `archive/` | Superseded versions of context documents, kept whole and unedited so a cold reader can see the lineage without git | Cowork |
| Corrections | `corrections.md` | Append-only record of after-the-fact fixes to documents (ledger precursor), and the map of old paths to new ones | Whoever corrects |

**Reading order for a new session on any surface:** `CLAUDE.md` → `charter.md` → `STATUS.md` → `plans/` (current phase) → the ADRs relevant to the task → the open handoff, if any.

**Status vocabulary** (frontmatter `status:`): context docs go `draft` → `accepted` → `superseded`; handoffs go `proposed` (in `handoff/proposed/`) → `open` (at the top of `handoff/`) → `done` (moved to `handoff/done/`), or `abandoned` and `superseded` (moved to `handoff/archive/`).

**Where the same information lives twice, and which copy wins:** this repository is canonical. The claude.ai Project "Automation" carries mirrors of the decision log and phase plans so that any Claude surface — including a phone — has the briefing. If they disagree, the repo is right and the Project gets corrected.
