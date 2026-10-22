---
id: CDH-0015
type: handoff
created: 2026-10-15T23:05:00-07:00
from: michou
to: cowork
tier: 2
status: done
adopted_by: michou
adopted: 2026-10-15T22:56:00-07:00
completed: 2026-10-15T23:45:00-07:00
rulings: "go ahead (Michou, 2026-10-15 22:56); blocking findings taken by default under the 2026-10-14 00:41 rule"
depends_on: [CDH-0013]
design_track: HANDOFF-0036
---

# CDH-0015: The station, cycle 3 — AUDIT-CDH-0013's findings applied

## Why

AUDIT-CDH-0013 (Codex, 2026-10-15 22:52, committed `31b2cd2`) returned `BLOCK: 2` on the station at `dd90ca6`: F1 the hull's halt is derived from the newest event only, so an ordinary note after a halt clears the HUD, the wall and the hull colour while the run stays `blocked`; F2 `resize()` reads the hidden stage's 0 × 0 box while calm, writes `NaN` camera bounds and 0 × 0 render targets, and nothing resizes on the way back. Advisories: F3 the quiet rule says "median" while the code takes the upper middle gap of an even count; F4 the twelve PNGs and the manifest under `logs/scratch/design-review/cdh-0012/` do not carry the hashes AUDIT-CDH-0012 printed (the report was delivered from a stale upload before its hash table was refreshed — the files on the Mac are the final captures; the table was wrong); F5 the synthetic approval carries `status: ok`, which `validate_event()` rejects; F6 fixture summaries live only in hidden crew wrappers outside calm, and the station rows' `aria-label` omits elapsed and chip. S1–S9 and T1 are otherwise closed. This handoff is the cycle, run together with CDH-0014's rubric checks and reviewed with them by CDH-0016.

## Do

1. **F1 [take].** One `activeHalt(run)` rule, shared by `lifecycle()` and `snapshot()`: the newest blocking `halt:` note that no intent, outcome or approval has followed. Verify by evaluation: halt then ordinary note stays halted; halt then approval clears; the exhausted-retry exception stays transient.
2. **F2 [take].** `resize()` returns without sizing when the stage is hidden; leaving calm resizes before the next frame. Verify standalone at 1440 and 400: `c`, resize, `c` — camera bounds finite, render targets sized, room buttons visible and focusable.
3. **F3 [take].** The median is the ordinary one (the mean of the two middle gaps for an even count), said once in board 11's two anatomy copies, the README and the code. The threshold and floor stay.
4. **F4 [take].** AUDIT-CDH-0012's evidence table is corrected to the hashes on the Mac (Codex's measured values), with the cause stated, delivered from a fresh upload and verified by sha before commit.
5. **F5 [take].** The synthetic approval's `status` becomes `null`; all 42 records validate with `kgme.events.validate_event`; the evaluation is rerun.
6. **F6 [take].** Only the artwork is decorative: crew wrappers are exposed, their portraits stay `aria-hidden`, so a fixture's last summary is accessible outside calm (it stays in the bubble element after the fade); station rows drop the explicit `aria-label` and let their visible text (mapping, run, word, quiet, elapsed, event, chip) be the name. Verify with the accessibility tree at the refusal, the note and the transient-lifecycle / blocking-chip row.
7. Commit together with CDH-0014's changes, republish the station (and the review copy if the tray moved), write `docs/audit/cockpit-design/cdh-0015-implementation.md`, mark this file done; CDH-0016 goes `ready` when CDH-0014 is done too.

## Acceptance

Codex's re-review finds F1 and F2 closed by evaluation and standalone observation, F3 by one wording in three places, F4 by matching hashes, F5 by validation, F6 by the accessibility tree.
