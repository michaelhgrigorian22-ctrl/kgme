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

## 2026-09-10T09:45:00-07:00 — cowork — "Copied library" inference in HANDOFF-0017 was wrong
- **Wrong:** Cowork wrote into HANDOFF-0017 that the loose files in Michou's Finder view "match the open-source FinanceToolkit package's module names, so most of it is a copied library, regenerable with pip," and asked Claude Code to confirm by comparing "a few" files. The external audit (2026-09-10, finding 3) objected before the report landed: a sample cannot prove a whole tree unmodified, and basenames cannot prove content. AUDIT-0006 then showed the Finder view was a Spotlight search result spanning two `~/Reference` clones and the project itself; the project's 80 human files are Michou's own code and notes, none of it a library copy.
- **Changed:** nothing was deleted; the recommendation in AUDIT-0006 keeps all 80 files in the archive set. HANDOFF-0017 is `done` and stays as written; this entry records that its premise was wrong and the audit's evidence rule is adopted in ADR-013 spirit: classification as regenerable requires a pinned comparison source and a complete manifest, never a sample.
- **Lesson:** a plausible inference in a handoff becomes tomorrow's deletion scope. Handoffs state what to measure, not what the answer probably is.

## 2026-09-10T09:45:00-07:00 — cowork — Ledger contradiction (ADR-003 vs ADR-004 vs .gitignore)
- **Wrong:** ADR-004 listed `logs/` as regenerable and `.gitignore` excluded `logs/*.jsonl`, while ADR-003 made the ledger authoritative. Found by the external audit (finding 1).
- **Changed:** ADR-012 (proposed) defines three data classes and makes the ledger durable and tracked; `.gitignore` now tracks `logs/ledger/` and ignores only `logs/scratch/`. ADR-004 is partially superseded on acceptance.

## 2026-09-11T23:40:00-07:00 — cowork — Deletion gate written for Time Machine on a Backblaze machine
- **Wrong:** HANDOFF-0018 (drafted by Claude Code from Cowork's HANDOFF-0017 template) gated its deletion step on `tmutil latestbackup`, which can never succeed since Michou chose Backblaze on 2026-09-11. Cowork's HANDOFF-0024 then re-gated all of step (a) on the Backblaze log, blunter than necessary: a backup gate on regenerable content protects nothing.
- **Changed:** ruling recorded — the gate applies only to items whose originals are unique-but-archived; regenerable content needs no gate. Michou ran the deletions himself (global `rm -rf` deny held, as designed) and ruled the unit's working copy stays. HANDOFF-0024 abandoned as unnecessary; kept as the record.
- **Lesson:** gates name the *evidence*, not the *tool*; and a handoff template must be re-read when an upstream decision (backup method) changes.

## 2026-09-14T22:55:00-07:00 — cowork — Schema version record: v1.1 → v1.2 (not a correction)
- **What:** `docs/schema-v1.md` is now v1.2 (draft), written under HANDOFF-0030 after Michou's rulings of 2026-09-14: the validator covers `memory/` and `docs/`; the charter is exempted by path rather than given an eleventh type ("lenient on the charter"). Applied as written, v1.1 failed on KGME's own record: eighteen accepted ADRs without `modified`, twenty-four handoffs with `from` and no `author`/`source`, the charter and the schema file with types outside the ten, governance notes outside `memory/notes/`, a template with placeholders, an archive whose files share ids with the live documents they were versions of.
- **Changed:** the schema, not the record. Append-only types drop `modified`; `handoff` uses `from` and needs no `source`; `note` admitted under `memory/inbox/`, `docs/`, `docs/plans/`, `docs/readers/`; exempt paths named with reasons (`memory/templates/`, `memory/attachments/`, `.obsidian/`, `docs/charter.md`, `docs/schema-v1.md`, `docs/archive/`); status vocabularies gain `proposed` (decision, handoff) and `superseded` (handoff); `completed` required only on `done`; unknown fields permitted and reported `advisory`; findings classed per ADR-016. Nothing under `docs/adr/` or `docs/handoff/` touched. Beyond HANDOFF-0030's six rules, four additions were needed for the acceptance test to be reachable and are flagged for Michou's approval of the diff: the `handoff` author/source rule, the `docs/schema-v1.md` and `docs/archive/` exemptions, the `docs/readers/` location, and the status vocabularies.
- **Known item-5 finding for HANDOFF-0031's dry run:** `docs/README.md` has no frontmatter. It is a `note` in `docs/` root and takes a minimal frontmatter block (`id: DOCS-README`) as an approved diff; nothing else is expected to fail.
- **Lesson:** a schema written before the documents it governs existed is a guess; v1.2 is the first version fitted to a real corpus. Rule adopted into the schema's provenance section: when the schema and an append-only record disagree, the schema moves.
