---
id: CDH-0019
type: handoff
created: 2026-10-16T14:40:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0017]
design_track: HANDOFF-0036
---

# CDH-0019: Codex becomes the design track's builder — merge `main`, take the queue, run the fix loop

## Outcome and authority

Michou, 2026-10-16 14:24: the design track's Codex session "will now be the main always on builder", in a terminal in `~/Projects/KGME/design`. This handoff is that session's standing mandate: one adoption, many cycles. Until it is adopted, Codex on this track reviews only (Michou, 2026-10-09). Adopted when Michou starts Codex with `control/review/codex-builder-prompt.md` (`tools/review/codex-builder-prompt.md` until the merge of step 1) and this row is the first `ready` one in the README's Codex queue. Under CLAUDE.md on `main` (ADR-023, "How decisions are made") and the rubric cited in the design review prompt. HANDOFF-0042, proposed on the substantive track, registers the track and the builder profile; this handoff writes that profile's boundary out in the prompt and changes nothing under `control/policy/`.

## Why now

The home moved today (HANDOFF-0049): `~/Projects/KGME/brain` on `main`, `~/Projects/KGME/design` on `design`. The design branch has not taken `main`'s relabelled tree (`tools/` → `control/`, handoffs by state, schema v1.5, the coherence checks) and is 27 commits each way from `eb72f1d`. Cowork rehearsed the merge in a clone on 2026-10-16: six "file location" notices (git relocates the files `design` added under `tools/review/` to `control/review/`) and one content conflict, `docs/readers/cockpit-design.md` (take `design`'s side of its three hunks); after that, `kgme lint` reports 0 blocking and the only real coherence finding is the stale `tools/review/design-prompt.md` string in `docs/readers/cockpit-design-chatgpt.md`. Native git on the Mac is the right place to run it, so it is the builder's first task.

## Do

1. **The merge**, once, exactly as the prompt's step 1 says: `git merge --no-ff main` from a clean tree; the reader's three hunks resolved to `design`'s side; `git add control/review`; the path strings followed in live files only (`control/review/design-prompt.md`, `docs/readers/cockpit-design-chatgpt.md`, `docs/design/cockpit-v0/station/README.md`, the README's queue section, CDH-0016 and CDH-0018); `make check` with no blocking finding and `tests/test_coherence.py` passing; one merge commit, `design: merge main (HANDOFF-0049 tree) into design; paths followed (CDH-0019)`. Any other conflict: abort, report, stop.
2. **The queue**: rows 5 (CDH-0016) and 6 (CDH-0018), the two read-only reviews, as their handoffs say; then any later `ready` row, review or build.
3. **The fix loop**: with no row `ready`, the newest review's blocking findings become one cycle (`docs/audit/cockpit-design/cdh-0019-cycle-N.md`, a dated status section in the README, one commit by pathspec), then stop for Cowork's native review. Nothing pending: one line, stop.
4. **The boundary** as the prompt states it: writes under `docs/design/`, `docs/handoff/cockpit-design/`, `docs/audit/cockpit-design/`, `docs/readers/cockpit-design*.md`, `tests/test_design_sprites.py`, `logs/scratch/` (step 1's merge files and path strings excepted); no push, no `main`, no network, no secrets, no binaries committed; commits by pathspec with the hook skipped.

## Acceptance

After step 1: `git log --oneline design..main` is empty, `make check` in the worktree ends green with only advisory or cosmetic lint findings, `ls tools` fails and `control/review/design-prompt.md` cites `control/review/design-reference/ui-ux-pro-max/`. After each cycle: a report with hashes and scores, a README status section, a commit that touches only the cycle's files, and Cowork able to republish the review copy and the station from the committed files.

## Closeout

This handoff stays `open` while the mandate runs; each cycle names its own report. It closes (`status: done`, `completed:`, `report:` the last cycle's report) when Michou ends the mandate or HANDOFF-0042 lands with the profile that replaces its boundary section.
