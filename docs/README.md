# KGME documents — index and reading order

| Kind | Where | Treatment | Who writes |
|---|---|---|---|
| Constitution | `charter.md` | Read first. Changes only by ADR plus explicit approval | Michou (drafted with Cowork) |
| Decisions | `adr/ADR-NNN-*.md` | Append-only. Superseded, never edited | Cowork / Michou; Claude Code may propose |
| Schema | `schema-v1.md` | Versioned; changes are migrations | Cowork / Michou |
| Plans | `plans/` | Canonical phase plans; mirrored to the claude.ai Project | Cowork |
| Readers | `readers/` | Explanatory guides for tools; setup halves added after the audit | Cowork, revised by Claude Code |
| Handoffs | `handoff/YYYY-MM-DD-topic.md` | The only instructions to Claude Code. Dated, frozen, status-tracked | Cowork / Michou |
| Reports | `audit/`, `../logs/` | Outputs. Data, not instructions | Claude Code / KGME |
| **Status** | `STATUS.md` | The single current disposition of every open item (ADR-014). Read second, after `charter.md` | Cowork, until a job does it |
| Corrections | `corrections.md` | Append-only record of after-the-fact fixes to documents (ledger precursor) | Whoever corrects |

**Reading order for a new session on any surface:** `CLAUDE.md` → `charter.md` → `STATUS.md` → `plans/` (current phase) → the ADRs relevant to the task → the open handoff, if any.

**Status vocabulary** (frontmatter `status:`): context docs go `draft` → `accepted` → `superseded`; handoffs go `open` → `done` or `abandoned`.

**Where the same information lives twice, and which copy wins:** this repository is canonical. The claude.ai Project "Automation" carries mirrors of the decision log and phase plans so that any Claude surface — including a phone — has the briefing. If they disagree, the repo is right and the Project gets corrected.
