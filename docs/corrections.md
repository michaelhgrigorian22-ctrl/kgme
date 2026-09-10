---
id: CORRECTIONS
type: note
status: active
created: 2026-09-09T20:10:00-07:00
modified: 2026-09-09T20:10:00-07:00
author: cowork
source: stated
tier: 2
---

# Corrections — append-only

The ledger's ancestor. When a document is corrected after the fact, the correction is recorded here as a new entry: what was wrong, what changed, who changed it, when. Entries are never edited or removed. Once `logs/` exists this file is superseded by ledger events; it stays as the record of Phase 0.

## 2026-09-09T20:10:00-07:00 — cowork — Day-one timezone error in all Cowork-authored documents
- **Wrong:** every `created`/`modified` timestamp and every filename date written by Cowork on day one used the sandbox's UTC clock but was labelled `-07:00` (e.g. `2026-09-10T02:30:00-07:00`). The true local time was the evening of 2026-09-09 PDT. Claude Code's own timestamps in the audit report were correct and exposed the discrepancy.
- **Changed:** all Cowork-authored `2026-09-10T02:MM` → `2026-09-09T19:MM`, `2026-09-10T03:MM` → `2026-09-09T20:MM`; prose dates `2026-09-10` → `2026-09-09`; files `docs/handoff/2026-09-10-*.md` and `docs/audit/2026-09-10-machine-audit.md` renamed to `2026-09-09-*`; the audit report's heading and one internal path string updated to match. Content of HANDOFF-0001 (done) otherwise untouched.
- **Lesson:** exactly the ambiguity ADR-005 warns about, made by the author of ADR-005. Rule going forward: Cowork reads the machine's clock (via the mounted folder) before stamping anything; filename dates are the local date.

## 2026-09-09T20:10:00-07:00 — cowork — Report frontmatter did not match the schema
- **Wrong:** HANDOFF-0001 told Claude Code to write the audit with `type: audit` and no `status` field; `docs/schema-v1.md` defines the type as `report` with `status: final`. HANDOFF-0002's lint caught the missing `status`.
- **Changed:** `docs/audit/2026-09-09-machine-audit.md` frontmatter now `type: report`, `status: final`. Future handoffs specify report frontmatter from the schema.

## 2026-09-09T21:40:00-07:00 — cowork — Handoff and report id collision
- **Wrong:** Cowork wrote the Codex review handoff as `HANDOFF-0006` (report `AUDIT-0003`) at 21:05, after Claude Code had already, correctly, numbered its proposed fixes `HANDOFF-0006…0012` at 20:24 and its fix plan `AUDIT-0003`. Cowork did not check the folder before assigning ids.
- **Changed:** the Codex review handoff is now `HANDOFF-0013`, writing `AUDIT-0004`. Filename unchanged (`2026-09-09-review-proposed-fixes.md`). Proposed 0006–0012 keep their ids.
- **Rule going forward:** whoever assigns the next id lists `docs/handoff/`, `docs/handoff/proposed/`, and `docs/audit/` first. Until the ledger issues ids automatically, this is a human/agent discipline.

## 2026-09-09T23:35:00-07:00 — cowork — Dependency record: Codex CLI
- **What:** `@openai/codex` 0.154.0, installed by Michou via `npm install -g` under nvm Node 25.9.0; signed in with his ChatGPT Plus account. Smoke test (`codex exec` reading `CLAUDE.md`) passed inside the repo.
- **Why:** ADR-007 second builder / independent reviewer. First job: HANDOFF-0013.
- **Note:** globally installed under nvm, so it lives in that Node version's `bin`; a Node version switch hides it. Candidate to move to a pinned Homebrew install once Homebrew exists.

## 2026-09-09T23:45:00-07:00 — cowork — Scope error in the Finance disposal
- **Wrong:** HANDOFF-0014 and the proposed HANDOFF-0016 targeted all of `~/Projects/Finance` for disposal, on Cowork's misreading of Michou's request. `~/Projects/Finance` (Active / Archive / past memos and theses) is his most important work product and is to be kept. The target was the old `finance-python` project inside it.
- **Changed:** HANDOFF-0016 marked `abandoned` with `superseded_by: HANDOFF-0017`. AUDIT-0005 stands as a factual inventory (its counts are correct); its "disposal recommendation" section is void. HANDOFF-0017 re-scopes to `finance-python` only.
- **Lesson:** when a request names a folder for deletion, confirm the exact path back before writing any handoff that could lead to deletion. Michou caught it before anything ran; the inventory-before-disposal rule is what made that possible.
