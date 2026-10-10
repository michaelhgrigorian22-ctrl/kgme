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
| CDH-0003 | Cowork | Rebuild board 10 as native artboard markup from the approved cast (AUDIT-CDH-0002 CW1 blocking, CW2, CW3); retire the stale sprite constraints in the readers and review prompt; republish the review copy. Proposed 2026-10-09; awaiting Michou's adoption. | [Native board](2026-10-09-chibi-native-board.md) |
| CDH-0004 | Codex, GPT-6 Astra (read-only review) | Independent design review of CDH-0003's commit on branch `design`. Proposed; adopted by pasting the start prompt after CDH-0003 is done. | [Design review](2026-10-09-chibi-native-verification.md) |

Both handoffs were explicitly adopted by Michou on 2026-10-09: "theyre good to go i just want to plug and play codex to start working and then just say the word to cowork to read the folder and move forward given the brief". Their files now carry `from: michou` and `status: open`. Codex mechanically recorded Michou's adoption; it did not adopt its own proposal. This approval covers the written local implementation and verification plans, including the scoped board 10 edits. It does not grant final canvas approval.

## Status 2026-10-09 23:18

CDH-0001 done 22:44. CDH-0002 done 22:58, verdict `BLOCK: 1 blocking finding` (`docs/audit/cockpit-design/cdh-0002-cowork-verification.md`): the board-10 iframe does not render in the native canvas. The artwork is approved: Michou approved the cast as drawn on the sticker contact sheet (2026-10-09 23:04); CW4 and CW5 closed as drawn.

Working rules from 2026-10-09 23:13 (Michou): the design track works in the worktree `~/Projects/Automate-design` on branch `design`, commits freely by pathspec, never touches `main`; Codex reviews only until a builder profile exists (HANDOFF-0042, after 0034), so CDH-0003 is Cowork's and CDH-0004 is Codex's review; no binaries are committed; captures live under `logs/scratch/design-review/` (the `memory/attachments/cockpit/` paths cited in AUDIT-CDH-0001, AUDIT-CDH-0002, CDH-0001 and CDH-0002 predate the move of 23:11 and now read `logs/scratch/design-review/chibi-reference/` and `logs/scratch/design-review/chibi-review/`). Next: Michou adopts CDH-0003; Cowork builds; then CDH-0004.

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
