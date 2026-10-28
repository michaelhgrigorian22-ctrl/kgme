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

## 2026-09-20T15:31:58-07:00 — claude-code — Schema version record: v1.2 → v1.3 (not a correction)
- **What:** `docs/schema-v1.md` is now v1.3 (draft), on Michou's ruling of 2026-09-20 after HANDOFF-0031's first dry run over the real roots: the ten Phase 0 reports (created 2026-09-09 to 2026-09-11) carry no `period`, eight carry `source: fetched` without `origin`, one carries `source: inferred` without `sources`. They were written under v1.0 and v1.1, which required none of it.
- **Changed:** the schema, not the record. `period`, and `origin` or `sources`, are required of reports created on or after 2026-09-14; earlier reports are held to the fields that existed when they were written, and `kgme lint` applies the date. In the same pass `docs/README.md` received its frontmatter block (HANDOFF-0030 item 5, `id: DOCS-README`) as an approved diff, and a `modified` value Claude Code had written that morning without seconds in `docs/STATUS.md` was corrected to the schema's shape.
- **Lesson:** a validator's first run over a real corpus finds what the schema's author could not see from the document alone; the second fitting (v1.3) followed the first (v1.2) by six days, and both moved the rule, not the record.

## 2026-10-15T23:52:36-07:00 — claude-code — Path changes, 2026-10-15 (HANDOFF-0049)
- **What:** the repository was relabelled by role. Finished handoffs, audits and accepted ADRs keep their words; this entry is the map from the paths they name to the paths that exist.
- **`tools/` → `control/`**, every subfolder unchanged: `control/hooks/`, `control/git-hooks/` (`core.hooksPath`), `control/policy/profiles/`, `control/review/`, `control/schema/`.
- **Handoffs by state:** finished handoffs `docs/handoff/<name>.md` → `docs/handoff/done/<name>.md` (27); HANDOFF-0024 and proposals 0006, 0007, 0008, 0009, 0010, 0016 → `docs/handoff/archive/`. Open handoffs stay at the top; live proposals stay in `docs/handoff/proposed/`.
- **ADR-019's `tools/ledger`** is `kgme/ledger.py`, the one writer.
- **Report links:** each finished handoff now names its report in `report:`. The nine names that never existed: `2026-09-15-packaging.md` (HANDOFF-0025) → `docs/audit/2026-09-14-packaging.md`; `2026-09-15-packaging.md` (HANDOFF-0026) → `docs/audit/2026-09-14-ledger.md`, the report that names 0026; `2026-09-16-permissions-and-hooks.md` (0027, 0028) → `docs/audit/2026-09-15-permissions-and-hooks.md`; `2026-09-17-review-wrapper.md` (0029) → `docs/audit/2026-09-16-review-wrapper.md`; `2026-09-18-validator.md` (0031) → `docs/audit/2026-09-20-validator.md`; `2026-09-19-canaries.md` (0032) → `docs/audit/2026-09-20-canaries.md`; `2026-09-20-loop-0.md` (0033, 0034) → `docs/audit/2026-10-08-loop-0.md`; and this file's first entry's `2026-09-10-machine-audit.md`, renamed that day, is `docs/audit/2026-09-09-machine-audit.md`. Three more named no dated file (0018's `<date>`, 0040's `2026-10-DD`) or none (0005, 0030): 0018 → `docs/audit/2026-09-11-finance-python-disposal.md`, 0040 → `docs/audit/2026-10-08-push-on-commit.md`, 0030 → `docs/audit/2026-09-20-validator.md` (closed there), 0005 → `docs/audit/2026-09-09-machine-audit.md` (the run it unblocked records it).
- **Lesson:** a report path predicted in a handoff is a guess at a date; from now on the closing step writes the real one into `report:`, and `kgme lint` checks it exists.

## 2026-10-21T00:45:00-07:00 — claude-code — HANDOFF-0050: "every earlier finding resolved" was false (AUDIT-0061, AUDIT-0062)
- **Wrong:** the cycle-4 dispositions of HANDOFF-0050's review, and the cycle-3 paragraph of `docs/audit/2026-10-16-capture-and-daily.md`, said every earlier finding was resolved. AUDIT-0061 (cycle 3) left F10 open beside F12 (`open_blocking: [F10, F12]`), and AUDIT-0062 (cycle 4) recorded the contradiction and kept F10 blocking. The claim restated the builder's belief instead of the audit's verdict.
- **Changed:** the report now states each cycle's open findings as its audit records them (cycle 3: F10 still blocking, F12 new; cycle 4: F12 resolved, F10 still blocking, then the halt). The report was uncommitted, so the fix is in the commit that closes HANDOFF-0050; this entry is the record. F10 itself was closed by Michou's override and Cowork's ruling (2026-10-21, ledger `01M5EMAEG872P34RMNTER7D86P`): the mechanism was removed, and every write into an existing vault file is a whole-file atomic replace.
- **Lesson:** a disposition's "resolved" is the reviewer's word, read from the last audit's `open_blocking` line, never the builder's summary of its own fixes.

## 2026-10-22T01:32:53-07:00 — cowork — Future-dated times on 2026-10-21 (STATUS, HANDOFF-0055)
- **Wrong:** `docs/STATUS.md` was stamped `modified: 2026-10-21T23:40:00-07:00` and "Last updated 2026-10-21 23:40 PDT", and HANDOFF-0055 `created: 2026-10-21T23:30:00-07:00`, but both were committed at 15:57:39 PDT (`f8609e9`). The Project's start-here note said "Written 23:55 PDT" and was written at 16:02 PDT. The session wrote clock times about seven and a half hours ahead, the slip this file's first entry records.
- **Changed:** STATUS carries the true time of its next update (2026-10-22T01:32:53-07:00). HANDOFF-0055 is a finished record and keeps its `created`; this entry is its correction: it was written before 15:57:39 PDT on 2026-10-21. The start-here note was rewritten with the true time.
- **Lesson:** a time written into a record is read from the clock in Michou's zone (`TZ=America/Los_Angeles date`), never estimated; the Cowork VM runs on UTC.

## 2026-10-22T01:32:53-07:00 — cowork — HANDOFF-0056 drafted as open among the proposals
- **Wrong:** following a shortcut in the Project's start-here note, Cowork wrote HANDOFF-0056 into the proposals folder at 23:39 PDT with `from: michou` and `status: open`, before Michou had adopted it. An open handoff among the proposals fails the working-tree coherence test, so `make check` went red and `kgme review` held HANDOFF-0055's cycle 5 back until Michou adopted 0056 at 23:52 (`43f3ce0`). Caught by the check; nothing was committed wrong.
- **Changed:** a proposal Cowork writes carries `from: cowork` and `status: proposed`, as `CLAUDE.md` defines one; adoption sets both as Michou moves the file. The start-here note's rule is corrected.
- **Lesson:** a convention in a hand-off note is checked against `make check` before it is followed; the checks, not the note, define a valid tree.

## 2026-10-25T23:08:13-07:00 — cowork — three commit boxes swept Claude Code's staged work onto `main`
- **Wrong:** on 2026-10-25 Cowork gave Michou three terminal boxes of the form `git add <paths>` then `git commit -m …` with no pathspec on the commit (the 0057 adoption at 16:52, the 0037 F11 amendment at 22:47, `9865a93`; the cockpit reader at 22:56, `9d6f9db`). A commit without a pathspec takes the whole index, so the second and third carried Claude Code's staged HANDOFF-0037 page, icon, manifest, tests and reports before review cycles 4 and 5 had passed; cycle 4 then found one real defect in that page (the runs pane hidden behind an open detail), fixed in `27ccba2` at 23:02. Nothing unreviewed remains on `main`; for fifteen minutes it held a page with that defect. Found by Claude Code in its closing report.
- **Changed:** a commit box names its files on the commit itself, `git add <paths>` then `git commit -m "…" -- <paths>`, never a bare `git commit`; the Project's start-here note is corrected the same evening.
- **Lesson:** "commit by explicit pathspec" means the pathspec on `git commit`; staging by path does nothing to protect what someone else already staged.

## 2026-10-28T10:21:46-07:00 — cowork — a terminal box ran past a refused merge and swept Claude Code's staged work onto `main`
- **Wrong:** at 10:17 Cowork gave Michou a box for the hand merge of `design` (the `cockpit-design` reader had been edited on both sides) with `git merge --no-ff design` first and `git commit -m "…"` without a pathspec after it, because a merge commit cannot take one, and told him in prose to run it only after Claude Code's HANDOFF-0048 commit had cleared the index. He ran it at 10:20 with the index still holding 0048's thirty-five staged, unreviewed files (the loop had halted at cycle 3 and nothing is committed over a halt). The merge refused, as it should; zsh ran the next lines anyway; the bare commit took the whole index: `7849748`, titled as a merge, is 0048's diff plus the reader, pushed by the hook. `kgme approve` then refused `9c360af`, correctly, since `design` was not merged. Found by Michou pasting the output back; Cowork had the staged index in front of it at 10:17.
- **Changed:** not reverted. Claude Code had launched cycle 4 three seconds before the slip and stopped it at 10:25:42 with nothing written; the hook's retry then merged `design` cleanly on top of the hand-edited reader (`0d627a9`), so a revert would have undone an edit a landed merge relies on. Cowork ruled at 10:30: the code stays where it landed, cycle 4 reviews the saved diff (sha16 `1be61e246a9a5ade`, byte-identical to `7849748`) against the tree at HEAD, and on PASS only the audits are committed, their message naming `7849748` as the commit that carried the code; a defect found by cycle 4 is a follow-up commit, as on 2026-10-25. The first line of Cowork's repair box (`git revert … && git cherry-pick -n …`) was never run; this entry's first draft said it had been, and was corrected before commit. A commit box that must include a line without a pathspec (a merge commit) is one `&&` chain, so a refused step stops the rest, and is given only when `git diff --cached --quiet` is true; a pre-commit guard that refuses a shell commit holding a non-human path is proposed (HANDOFF-0067).
- **Lesson:** the start-here rule ("name the files on the commit") has one case it cannot cover, the merge commit, and that case needs a mechanical guard, not a sentence. The Project's start-here note is corrected the same day.
