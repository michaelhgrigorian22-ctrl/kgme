---
id: HANDOFF-0060
type: handoff
created: 2026-10-26T00:41:24-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-26T03:23:28-07:00
report: docs/audit/2026-10-26-weekly-review-code-items.md
depends_on: [HANDOFF-0044, HANDOFF-0056]
plan_ref: PLAN-PHASE-1 step 13c
---

# Handoff 0060 — The weekly review's code items: tests that hold across midnight, a canary cell that passes on the observed refusal, modules back under the line

## Why
STATUS carries a list of code items found by reviews and parked for the weekly review: `kgme/merge.py` at 461 lines, `kgme/session.py` 409, `kgme/cli.py` 443, `tests/test_lint.py` 356, `tests/test_brief_review.py` 406, `tests/test_cheap.py` 499 against ADR-015's ~300; `kgme/session.py`'s module docstring without the cheap route (AUDIT-0108); the loop-mode canary cell whose write is refused every time but whose two-turn budget runs out before the model replies (HANDOFF-0044's report); and three test files that take "today" at import and compare it against a value taken later, so a run across midnight fails until rerun (`tests/test_daily.py`, `tests/test_capture_replace.py`, `tests/test_capture_review.py`, found 2026-10-26). Every one is machine-checkable and none changes behaviour; together they are an unattended night's work.

## What
1. **Midnight.** The three test files take "today" once per test, from one clock the test controls (a fixed instant passed in, or a frozen clock), never from `datetime.now()` at import. A test that reads two moments reads them from the same clock. Any production function that takes "today" from the wall clock gets it as a parameter with the current default, so the tests can pin it.
2. **The loop-mode canary cell.** A live cell passes on an observed call aimed at the target, refused at the named layer (Cowork's ruling, HANDOFF-0053). The `loop-write` cell's verdict reads the guard's refusal from the ledger, not the model's reply; the model's silence after the refusal is not a failure. `claude_max_turns` stays 2. If a cell cannot be judged from the ledger, say so in the report rather than raising the budget.
3. **Under the line, by moves alone.** Split `kgme/merge.py`, `kgme/session.py`, `kgme/cli.py`, `tests/test_lint.py`, `tests/test_brief_review.py` and `tests/test_cheap.py` by concern into modules under ~300 lines, as ADR-015 asks and as `kgme/brief*.py`, `capture*.py` and `clean*.py` already are. Pure moves: every function keeps its name and body, every test keeps its name and assertions, `git diff -M --stat` shows renames and moves, and `make check` passes at every step. A split that would need a behaviour change is not made; it is named in the report with the reason. `kgme/session.py`'s docstring gains the cheap route.
4. **One coherence check.** A done handoff's `completed:` equals its report's `created` (STATUS housekeeping, 2026-10-21): `kgme lint` compares the two and a difference is `advisory` (the four handoffs set by hand on 2026-10-21 may differ by seconds; the report names them).
5. **Not here:** any change to what the guard, the merge, the session levels or the brief do. Nothing in `control/`, `kgme.toml` or the readers; where a split moves a module a reader names by path, the reader diff is a human path under `logs/scratch/handoff-0060/`.

## Outputs
`tests/test_daily.py`, `tests/test_capture_replace.py`, `tests/test_capture_review.py`, `kgme/daily.py` and `kgme/capture*.py` only where "today" becomes a parameter, `kgme/canary.py` and `tests/test_canary*.py` (the `loop-write` verdict), the split modules of `kgme/merge.py`, `kgme/session.py`, `kgme/cli.py` and the three test files (new files beside them), `kgme/lint.py` or `kgme/coherence.py` (the `completed` check) with its test, `docs/readers/*.md` diffs where a path moved (human path).

## Acceptance test (under fifteen minutes)
With the clock frozen at 23:59:59 and the test's "today" taken at 00:00:01 the next day, the three files pass. `make canary-agents` shows the `loop-write` cell passing on the guard's refusal event with `claude_max_turns = 2`. No module named in §3 is over ~300 lines, or the report names the one that is and why; `make check` green; `git diff -M --stat` for the split commits shows moves. A done handoff with `completed:` ten seconds off its report's `created` is one advisory line from `kgme lint`.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: tests, one canary verdict, file boundaries. `git revert` per commit; the splits are separate commits from the fixes.

## Needs from Michou
Adoption. Applying any reader diff in the morning.
