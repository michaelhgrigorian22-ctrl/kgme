---
id: HANDOFF-0029
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-09-17T12:55:00-07:00
depends_on: HANDOFF-0028
plan_ref: PLAN-PHASE-1 step 4
---

# Handoff 0029 (proposed) — `kgme review`: the review loop as a ledgered command

## Why
0025 wrote the review protocol as a document and 0025 through 0028 ran it by hand. Codex has no hook layer, so its reviews leave no ledger trace unless a wrapper records them. This handoff turns the protocol into `kgme review`, so every review is an intent/outcome pair bound to a diff hash, and the loop bound is enforced by code rather than memory.

## What
1. `kgme/review.py` (effects: `run_codex_review`, `write_audit`; logic: `classify_findings`, `loop_state`). `kgme review [--reviewer gpt-6-astra] [--arbiter opus]`: stages the diff, runs `make check`, writes `logs/scratch/review.patch`, appends `intent`, invokes `codex exec -s read-only -m <reviewer> --json` with the fixed prompt from `docs/readers/review-loop.md`, parses findings, requires an ADR-016 class on each, writes `docs/audit/AUDIT-NNNN-review-<handoff>.md`, appends `outcome` with the diff hash, the class counts, and the verdict.
2. Loop state kept in the ledger, not in a file: cycles per root cause and distinct blocking root causes are read back from prior `outcome` events with the same handoff id. Halt conditions per the protocol; a halt appends a `note` with the escalation packet and prints it.
3. Tooling failures (no network in sandbox, 429, curl 000) are classed `transient` and never count, per the 2026-09-11 lesson.

## Outputs
`kgme/review.py`, `tests/test_review.py` (loop state from a synthetic ledger), the fixed reviewer prompt at `tools/review/prompt.md`.

## Acceptance test (under ten minutes)
One round-trip on a toy diff produces an AUDIT file with classed findings and an `outcome` bound to the diff hash; a synthetic ledger with three cycles on one root cause makes `loop_state` return halt; a synthetic 429 in the reviewer output is classed transient and does not count.

## Reviewer
Codex, reviewing the tool that will review it. Michou reads the first escalation packet format.

## Reversibility
`git revert`; the protocol document still stands for hand use.

## Needs from Michou
Nothing beyond the loop bound being right: three distinct blocking root causes, three cycles on one. Say if he wants a different bound.

## Report
`docs/audit/2026-09-17-review-wrapper.md`. Set `status: done`, `completed:`. Commit `review: kgme review wrapper and loop state (HANDOFF-0029)`.
