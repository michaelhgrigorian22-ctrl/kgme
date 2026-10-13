---
id: INDEX-COCKPIT-DESIGN-HANDOFFS
type: note
created: 2026-10-09T22:10:01-07:00
author: codex
source: stated
tier: 2
status: active
adopted_by: michou
adopted: 2026-10-09T22:16:24-07:00
---

# Cockpit design handoffs

This section uses its own `CDH-0001`, `CDH-0002` sequence, at Michou's request on 2026-10-09. It does not allocate, renumber, adopt, or close any `HANDOFF-00xx` document. The parent design track remains HANDOFF-0036; the application implementation remains HANDOFF-0037.

| ID | Recipient | Deliverable | Document |
| --- | --- | --- | --- |
| CDH-0001 | Codex, GPT-6 Astra | Implement the approved chibi cast as reusable artwork and animation in the design canvas. | [Implementation](2026-10-09-chibi-cast-implementation.md) |
| CDH-0002 | Cowork | Independently inspect that implementation in Cowork's native design interface. | [Verification](2026-10-09-chibi-cast-verification.md) |
| CDH-0003 | Codex, GPT-6 Astra | Rebuild board 10 as native artboard markup from the approved cast (AUDIT-CDH-0002 CW1 blocking, CW2, CW3); retire the stale sprite constraints in the readers and review prompt. Done 2026-10-11 15:51; committed on `design` as `0bb87d5`. | [Native board](2026-10-09-chibi-native-board.md) |
| CDH-0004 | Cowork | Native verification of CDH-0003 in the private review copy. Done 2026-10-12 15:32, verdict `BLOCK: 1 blocking finding` (CW7: template holes written `{x}` instead of `{{x}}`; the board renders fully once rewritten, verified natively as an experiment). | [Native verification](2026-10-09-chibi-native-verification.md) |
| CDH-0005 | Codex, GPT-6 Astra (read-only review) | Independent design review of the native board on `design`, after CDH-0004. Proposed; adopted by pasting the start prompt. | [Design review](2026-10-11-chibi-design-review.md) |
| CDH-0006 | Cowork | CW7 (hole syntax), CW8 (scroll boxes), CW9 (harness text) applied; native re-check PASS incl. motion. Done 2026-10-12 18:02; commit `a27d2f2`. | [Hole syntax fix](2026-10-12-chibi-hole-syntax.md) |
| CDH-0007 | Cowork | The active-runs tray: the cast at work in the top bar of the main boards, expandable with `a` (Michou's idea, 2026-10-12 17:35). Done 2026-10-13 15:45, native PASS; commit `5182d6a` (board 11 + boards 1, 3, 4, 5, 6, 7, 9). | [Active-runs tray](2026-10-12-active-runs-tray.md) |
| CDH-0008 | Codex, GPT-6 Astra (read-only review) | Independent design review of the active-runs tray at `5182d6a`, after CDH-0007. Proposed; `ready` in the Codex queue. | [Tray review](2026-10-12-tray-design-review.md) |
| CDH-0009 | Cowork | The station: the ship, its rooms and the crew at work as a second wall layout, a hand-built three.js page under `docs/design/cockpit-v0/station/` (Michou's wish, 2026-10-13 13:17). Proposed. | [The station](2026-10-13-the-station.md) |

Both handoffs were explicitly adopted by Michou on 2026-10-09: "theyre good to go i just want to plug and play codex to start working and then just say the word to cowork to read the folder and move forward given the brief". Their files now carry `from: michou` and `status: open`. Codex mechanically recorded Michou's adoption; it did not adopt its own proposal. This approval covers the written local implementation and verification plans, including the scoped board 10 edits. It does not grant final canvas approval.

## Status 2026-10-13 15:45

CDH-0007 (Cowork) done, commit `5182d6a`, native PASS (AUDIT-CDH-0007): the tray is one child component, board 11, mounted with `<dc-import>` into boards 1, 3, 4, 5, 6 and 9; two cosmetic findings fixed before commit (CW10 sheet wrap, CW11 frame height), two advisories left to Michou (CW12 a third header line on boards 3 and 5 at 1440; CW13 the Wall's already-full header). **CDH-0008 is `ready`** in the Codex queue below. Proposed today: CDH-0009 (the station) here, on Michou's word. HANDOFF-0043 (`kgme review --loop`) and HANDOFF-0044 (the toolbox and the scout) sit under `docs/handoff/proposed/` on `main`, untracked; **Michou's ruling 2026-10-13 15:52: anything substantive for Claude Code (`kgme/`, `tools/`, policy, the loop) is reviewed in the substantive Cowork session first, which records the ruling; nobody asks Claude Code about them before that. CDH handoffs stay on `design`.**

## Status 2026-10-12 18:12

CDH-0001 done. CDH-0002 done, `BLOCK: 1` (iframe). Artwork approved as drawn. CDH-0003 (Codex) done, `0bb87d5`. CDH-0004 (Cowork) done, `BLOCK: 1` (hole syntax). CDH-0006 (Cowork) done, `a27d2f2`, native PASS with motion observed. **CDH-0005 (Codex) done 2026-10-12 18:01, verdict `PASS`** (AUDIT-CDH-0005): F1 advisory, capture hashes differ from the reports — explained in `logs/scratch/design-review/PROVENANCE-2026-10-12.md` (lossless re-encoding on delivery; pixels identical; hashes now recorded on the Mac); F2 cosmetic, six stale words in `chibi/README.md`, folded into CDH-0007. Next: Michou adopts CDH-0007 (the tray); CDH-0008 then goes `ready` in the queue.

Working rules (Michou, 2026-10-09 23:13): the design track works in the worktree `~/Projects/Automate-design` on branch `design`, commits freely by pathspec, never touches `main`; Codex reviews only until a builder profile exists (HANDOFF-0042, after 0034) — CDH-0003 was already running under its earlier assignment when the rule landed and was allowed to finish; no binaries are committed; captures live under `logs/scratch/design-review/` (paths under `memory/attachments/cockpit/` cited in AUDIT-CDH-0001, AUDIT-CDH-0002, CDH-0001 and CDH-0002 predate the move of 2026-10-09 23:11).

## Codex queue

Michou starts Codex with one fixed prompt, every time: `tools/review/codex-queue-prompt.md`. Codex takes the first row below whose status is `ready`, records Michou's adoption in that handoff, executes it, writes its report, and sets the row to `done`. Cowork keeps this table: a row becomes `ready` when its dependency is `done` and the sha it reviews is committed on `design`. Nothing here commits or pushes; Cowork commits Codex's report afterwards.

| # | ID | Reviews | Status | Document |
| --- | --- | --- | --- | --- |
| 1 | CDH-0005 | Board 10 native cast, commit `a27d2f2` (CDH-0003 + CDH-0006) | done 2026-10-12 | [Design review](2026-10-11-chibi-design-review.md) |
| 2 | CDH-0008 | The active-runs tray (CDH-0007), commit `5182d6a`, boards 1, 3, 4, 5, 6, 7, 9 and 11; captures under `logs/scratch/design-review/cdh-0007/` | ready | [Tray review](2026-10-12-tray-design-review.md) |

## Start here

1. **Codex on GPT-6 Astra:** When Michou points you at this folder to begin, read and execute CDH-0001. Briefly restate the plan and proceed; the plan and named edits are already approved. Do not stop for a second adoption, pixel-style decision, or approval of routine edits inside the named scope. Finish the local artwork, board 10 integration, checks, and implementation report. Show the resulting scoped diff in the delivery. Preserve all unrelated human work.
2. **Cowork:** When Michou gives the word to verify, read and execute CDH-0002. First confirm that CDH-0001 is done, its implementation report exists, and its recorded file hashes match the delivered files. Then import the supplied files into your native design interface and perform the written verification without asking for the same plan approval again. If the implementation has not been delivered, report the specific missing prerequisite; do not improvise the artwork yourself.
3. **Handoff between the two:** The folder and the implementation report are the handoff. Neither agent needs this chat history. The agents do not automatically message each other or start the other agent's work. Michou supplies the start signal. Cowork's findings return to Michou for rulings; final cockpit approval remains his.

For these 2 handoffs, local files, evidence, and reports constitute delivery. No commit or push is required to make the next step ready. Do not let the post-commit push hook turn this local authorization into publication; leave git commit/push and public sharing for an explicit instruction. Report new scope, conflicting concurrent edits, or a genuine inaccessible capability when it materially blocks the requested result, rather than re-requesting approval for the agreed work.

## Shared ownership and the decision being implemented

This is a 4-person collaboration: Michou owns taste and approval; ChatGPT contributes visual studies and critique; Codex on GPT-6 Astra implements the artwork and animation; Cowork remains a design collaborator and verifies the result in its own canvas. Cowork's participation is not being replaced.

Michou requested discernible illustrated characters instead of pixel figures, allowed the old sprite constraints to change to achieve that, supplied an anime chibi style reference, and approved the resulting 7-character concept sheet with "perfecttttt!!!!" before requesting these instructions. This is approval of the visual direction, not approval of the complete cockpit, production performance, a personal likeness, or HANDOFF-0037.

## Visual references

The local PNGs are supporting visual references, not canonical application state, executable source, animation atlases, or production dependencies. The approved sheet's painted surroundings, cyan treatment, texture density, and poses must be adapted to the existing cockpit rules. Its PNG format alone does not establish usable alpha transparency.

| Reference | Repository path | SHA-256 | Provenance |
| --- | --- | --- | --- |
| Approved cast, 1536 x 1024 px | `memory/attachments/cockpit/chibi-reference/approved-cast.png` | `a314d8f83653a4cb1354e15a1aa3d443ec3d239135760c9fbf712f34218426a1` | Generated with the built-in image tool in this design session and approved by Michou; author: codex; source: fetched. |
| Style reference, 750 x 1000 px | `memory/attachments/cockpit/chibi-reference/style-reference.png` | `519e0449af83b41775192190dec15caf5257e93d762a4c5cd9c3c52ea84598b8` | Supplied by Michou in this session as a style reference; original artist and character identity not established; author: codex for this reference record; source: stated. |

Read the approved cast as 4 actors across the top, then 3 across the bottom: builder, reviewer, arbiter, guard; scribe, Michou, stranger. The user's style reference guides rendering language only. Do not reproduce its character identity or costume.

The earlier curved builder study in ChatGPT was exploratory and predates the approved sheet. Its 4.9 KB artwork measurement is not a size measurement or performance result for the approved chibi cast. Do not use it as the visual target or cite it as proof of efficiency.

## Delivery boundaries

This adoption records authorization for the 2 local work packages. It does not claim that either has run, that Cowork has seen the new canvas, or that Michou has approved the completed cockpit. Existing unrelated staged and unstaged work must remain untouched. The reference copies and handoffs are ready on disk; execution begins when Michou points the respective agent here.
