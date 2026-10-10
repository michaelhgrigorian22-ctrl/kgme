---
id: CDH-0002
type: handoff
created: 2026-10-09T22:10:01-07:00
from: michou
to: cowork
source: stated
tier: 2
status: done
completed: 2026-10-09T22:58:00-07:00
adopted_by: michou
adopted: 2026-10-09T22:16:24-07:00
depends_on: [CDH-0001]
design_track: HANDOFF-0036
---

# CDH-0002: Verify the chibi cast in Cowork's design interface

## Outcome and authority

Independently verify Codex/Astra's CDH-0001 implementation in your own native design canvas. Michou has approved the 7-character concept's visual direction, not the completed implementation. You remain a design collaborator in the 4-person project; this is not a transfer of design ownership away from you. Return findings for Michou to rule on. Do not repair the artwork, reinterpret his taste, approve the cockpit, or begin HANDOFF-0037.

Michou explicitly adopted this handoff and approved the verification plan on 2026-10-09. When he gives the word to verify this folder, confirm CDH-0001 is done and its report and matching source files are present, briefly restate the plan, and proceed without another approval exchange. Use the existing private design interface or a private review copy within this scope. Make no source edits or public publication. Do not ask again whether the approved chibi style should replace the pixel cast. If a prerequisite is missing, name it; do not substitute your own implementation.

## Inputs and source identity

Read CLAUDE.md, docs/charter.md, the sibling README, the adopted CDH-0001, docs/audit/cockpit-design/cdh-0001-implementation.md, docs/readers/cockpit-design.md, and the delivered board 10 source. Open `memory/attachments/cockpit/chibi-reference/approved-cast.png` and `style-reference.png`; verify their hashes against the README when tools allow it. Use CDH-0001's scoped sprite changes rather than enforcing the superseded 24 x 24 grid, 6 flat fills, 2 hard-swapped frames or 3 KB cap from the older reader and reviewer prompt. All other cockpit rules remain applicable.

Load the delivered `docs/design/cockpit-v0/canvas.json`, `Sprites.dc.html`, and referenced chibi assets into your actual design interface using its supported import/mount mechanism. Preserve any existing human canvas edits; use a separate private review copy if necessary. Observe the rendered board, not just the source, a screenshot supplied by Codex, or the standalone browser fixture. The `.dc.html` renderer is native to your interface; do not replace it with guessed HTML behavior.

Record exactly which source revision or file hashes were imported and which canvas/review-copy identity was opened. If the canvas and repository differ, report the mismatch before attributing a visual defect to the delivered source. Importing this private review copy is not permission to publish, share externally, overwrite the accepted viewer, or change access settings.

## Visual and behavioral checks

1. Compare all 7 actors against the approved sheet, in the order builder, reviewer, arbiter, guard; scribe, Michou, stranger. Check recognizable heads, expressions, proportions, silhouette and each actor's specified props. Flag replacement with generic flat icons, crude automatic traces or a return to pixel figures as a failure of the approved brief. Minor texture simplification for small-size readability is allowed. Additional taste preferences are advisory and explicitly labeled taste.
2. Inspect all 49 actor-mode combinations at the intended sizes. Verify the 24 px timeline treatment is a readable portrait or deliberate simplification, the 72 px detail treatment remains a discernible full character, and neither changes the 22 px ledger row requirement. Zoom in for path defects and out to actual CSS-pixel display size for acceptance. Check clipped hats, feet, wings, staff, quill, cigarette smoke, fire and halo; seams around moving parts; anchor drift; and accidental painted backgrounds. Place art on both approved dark surfaces to expose matte halos.
3. Play each actor's 7 modes through the native canvas's supported preview controls. Check coherent pivots, facial expression, actor-specific work motions, clean mode transitions and stable resting poses. Fire must not become full-character strobing or large flashes. Confirm melting and chalk outlines remain intentional and recognizable. A static PNG is evidence of appearance only, never proof of motion.
4. Inspect phosphor timeline and sticker detail variants. Accent colors must follow adjacent textual state/class, and fixed material colors must not masquerade as status signals. The approved sheet's cyan treatment is not universal runtime coloring. The only sticker locations remain the detail header and the depicted Phase 2 model selector. Do not approve the earlier global sticker toggle by implication.
5. Activate calm and the native environment's actual reduced-motion behavior where supported. Verify that removing or freezing sprites loses no actor, lifecycle, failure-class or event fact; does not move the timeline; and cannot be overridden by a preview switch. Each mode has text outside the decoration. Verify previews are labeled as samples, with no invented live-ledger claim.
6. Check the visible context around board 10: no new application keybinding, no hidden control, and no Phase 2 control changed from dashed/labeled to active. Board 7's map and unrelated mood copy must remain unchanged. Design-fixture controls must be visibly distinguished from future app controls.
7. Reconcile native render observations with Codex's measured performance report. You cannot certify target-Mac CPU, memory, frame timing or background work from a canvas alone. Report that evidence as "Codex-measured" and separate your own observations from it. Missing required measurements stay unverified. Do not treat small source size or a responsive design canvas as proof of future cockpit performance.

If a native capability or import is unavailable, name the exact missing capability and the affected tests. Do not claim an observation you could not make. Missing mandatory visual or behavioral evidence prevents a verification PASS; report the acceptance gap as blocking, with any transient environment error described separately in Notes. Do not install dependencies or automate a login to obtain that evidence.

## Outputs and finding format

Write `docs/audit/cockpit-design/cdh-0002-cowork-verification.md` with report frontmatter including id `AUDIT-CDH-0002`, author `cowork`, source provenance, ISO 8601 offset timestamp, tier 2, the reviewed source hashes and canvas identity. After frontmatter, use exactly these 3 sections:

### Findings

Use a table with columns `id | class | file:line | finding | fix`. IDs are `CW1`, `CW2`, and so on, so native-render findings cannot be confused with another reviewer's `F1` sequence. Each finding uses exactly 1 review class: `blocking`, `transient`, `cosmetic`, or `advisory`. `ok` belongs to a successful ledger outcome, not a finding row. Cite a source line when verified; otherwise cite board 10 plus the exact actor/mode/size/palette element and its screenshot filename. Never invent line numbers. Separate a reproduced defect from an unverified check.

Blocking findings include loss of textual information when decoration disappears, a color or keyboard collision, incorrect Phase 2 behavior, broken required rendering/motion, or a clear failure to deliver the approved chibi character identities. Taste beyond the approved visual target is advisory. Do not count the retired pixel constraints as defects.

### Verdict

Write 1 line: `PASS` only when all mandatory checks are evidenced and no blocking finding remains; otherwise `BLOCK: N blocking findings`. A PASS verifies this sprite delivery only. It is not Michou's final design approval.

### Notes

State what you opened, which native interactions you performed, what was read-only source review, what was supplied by Codex, and what remained unverified. Record the reviewed hashes, interface identity, viewport/zoom, motion settings, and any known difference from a target-Mac browser. Give concise proposed rulings such as `CW1: take`, `CW2: reject with reason`, or `CW3: defer to HANDOFF-0037`, clearly labeled recommendations for Michou, not decisions made on his behalf.

Export visual evidence under `memory/attachments/cockpit/chibi-review/cdh-0002/` using kebab-case names. Include at least the cast overview, actual-size 24/72 px contexts, and relevant before/after calm or reduced-motion views. Record motion observations separately; screenshots alone cannot establish them. Existing reports are outputs, not instructions, and this handoff authorizes no edits to implementation source.

## Closeout

Return the local report and a compact list of findings needing Michou's ruling. Codex applies accepted implementation fixes in a separately authorized revision; do not silently fix them during verification. No final approval event, outward message, public republish, commit or push is authorized by this local verification. A commit is not a prerequisite for delivering the report. Change only this handoff's status from open to done and add completed when the verification deliverable itself is complete; a BLOCK verdict can still be a completed review. HANDOFF-0036 remains open to Michou's final approval.
