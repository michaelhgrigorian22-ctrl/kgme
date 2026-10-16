---
id: LESSONS-COCKPIT-DESIGN
type: note
status: active
created: 2026-10-16T00:20:00-07:00
modified: 2026-10-16T14:50:00-07:00
author: cowork
source: stated
tier: 2
---
# Lessons — the design track (read at the start of every CDH; 40 lines max, condense rather than append)

This file lives under `docs/readers/` because schema v1.4 lets a note live only there, in `docs/` itself, `docs/plans/` or the vault (`kgme/schema.py` FOLDERS); `docs/handoff/cockpit-design/` admits handoffs and its `README.md`. The per-skill `lessons.md` path ADR-023 names needs a one-line exemption in `kgme/vault.py` beside README's — the substantive track's call.

Delivery and evidence
- `device_commit_files` with a stagedPath used before can send the stale upload. Every report and design file goes out from a fresh path, and its sha is checked on the Mac before the commit. Bitten twice (AUDIT-CDH-0013 F4).
- Capture hashes are taken on the Mac after delivery, never on the VM. PNGs from headless Chromium are not re-encoded; JPEGs from the browser pane are what the pane gives.
- A SwiftShader screenshot takes seconds; at ×20 that is minutes of replay. Evaluate the check first, screenshot second, and record the replay clock before and after each capture. For a precise moment, load with `?at=HH:MM:SS&speed=2`.
- A synthetic sample used for a check is labelled, kept under `logs/scratch/design-review/<cdh>/`, validated with `kgme.events.validate_event`, and never committed to the design folder.

The canvas editor and the pane
- `<dc-import name="X" prop="{{val}}">` mounts sibling `X.dc.html`; a child's `<helmet>` CSS applies in the parent, so prefix its classes; it may mount twice on one board.
- Toggling a board's Tweak makes the editor re-save that file (attribute quoting only). Diff against the repository before republishing the review copy.
- Screenshots work with the pane hidden. The Tweaks icon needs the pointer tool, not the hand. Zoom from the menu, pan with wheel ticks (~87 px each); a drag flings. `#artboard-<id>` appears in the hash once a board is selected.
- The artifact frame takes clicks but not keys from the pane, and does not expose its accessibility tree to it: keys, focus and names are measured standalone; clicks and pixels natively.
- A hidden tab pauses rAF; cap the per-frame delta or the first frame back jumps a replay past its end (CW15's cause).

Measurement
- Contrast is computed as Codex computes it: linearized sRGB, (L1+.05)/(L2+.05); a CSS filter is applied to the text before the ratio. Inline `style="color:…"` cannot be overridden by a class: use a class for muted text.
- Chromium joins a button's inline spans without spaces when it names it from content; give dense rows an explicit, complete `aria-label`.
- An emulated reduced-motion change does not always fire the matchMedia listener; poll once a second as well.
- A zero-specificity reset (`:where(button)`) keeps component rules in charge; `.tr-root :where(button)` is still (0,1,0).

The loop
- Codex commits its own three delivery files and takes the next ready row; Cowork applies blocking findings as the next cycle and Michou vetoes after the fact (2026-10-14 00:41). Under ADR-023, checks are run, not asked; judgement calls are scored (stakes × edge ≥ 1.5 asks, batched, with a recommendation) and the scores recorded in the README's open list.
- Codex is not told to start until its queue row is `ready` with a committed sha; while it runs, nothing it will `git add` (its handoff, the README) is edited.
- Git from the VM: `GIT_DIR=$HOME/mnt/KGME/brain/.git/worktrees/Automate-design GIT_WORK_TREE=$HOME/mnt/KGME/design` (the home is `~/Projects/KGME` since HANDOFF-0049; the worktree's metadata keeps its old name), `-c core.hooksPath=/dev/null -c gc.auto=0`; the VM cannot delete in the Mac's folders, so an auto-gc leaves `HEAD.lock` behind — move it aside under `.git`, never delete it.
- From 2026-10-16 (CDH-0019) Codex builds and reviews in one always-on session; Cowork reviews its builds natively and publishes the artifacts; new work still enters as a `ready` row written by Cowork or Michou, and the merge of `main` into `design` is a builder's task, rehearsed first in a clone.
- The one quiet threshold reproduces the boards' drawn samples; a rule that contradicts a drawn sample is wrong, not the sample.
