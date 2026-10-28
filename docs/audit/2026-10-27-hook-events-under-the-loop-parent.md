---
id: AUDIT-0154
type: report
status: final
handoff: HANDOFF-0063
author: claude-code
source: inferred
sources: ["HANDOFF-0063", "AUDIT-0148", "kgme/hooks/common.py", "tests/test_hooks.py", "AUDIT-0152", "AUDIT-0153"]
tier: 2
created: 2026-10-27T23:08:00-07:00
period: 2026-10-27
---

# HANDOFF-0063: a loop session's hook events sit under the loop's first intent

**State: done.** PASS at cycle 2 (AUDIT-0153, created 2026-10-27T23:05:29-07:00). Two files changed, the two the handoff names.

## What was built
- **`kgme/hooks/common.py`, `read_session_parent`.** Before the session has a first event, the loop's first intent named in `KGME_LOOP_PARENT` is the parent, when the value has the exact shape of an event id (`events.ULID_PATTERN.fullmatch`); once the session has an event, that event is the parent, as today. A value of any other shape (empty, a word, a lowercase ULID, one with a leading `8`, one character short, a `canary:` prefix, a `../` prefix, a trailing newline, a leading space) is ignored and the chain stays today's. The constant `LOOP_PARENT_ENV` names the variable beside `CANARY_STREAMS`, the one other ambient switch (HANDOFF-0032's adopted exception to ADR-015).
- **The chain a `kgme loop` run now has.** The loop's intent → the session's first hook intent and its outcome (both with `parent` = the loop's intent, since the post hook takes its parent from the intent it closes) → every later pair and the `session:end` note under that first intent. A session that made no call still ends under the loop's intent.
- **The staged-copy rule.** The module was edited in `logs/scratch/handoff-0063/common.py`, imported and exercised against the test streams there (set, unset, six malformed values), then copied in whole, and the live guard was probed once after each copy. Nothing was edited in place.

## Tests on the production constructors (`tests/test_hooks.py`, 12 new cases)
- The pre and post hooks through the entry points with the variable set and a fresh session: the first pair's `parent` is the loop's id, the second pair's is the first intent's; `session_end` too.
- The same without the variable: today's chain (`None`, `None`, first, first).
- Nine malformed values, parametrized, each leaving the chain untouched for the pair and for `session_end`.
- A `session_end` alone under the variable sits under the loop's intent.

## Review
- **Cycle 1 (AUDIT-0152, BLOCK).** F1: `.match()` let a ULID with a trailing newline through, and the ledger's `fullmatch` would then have refused the first call; fixed with `fullmatch`, red first on the live module (`logs/scratch/handoff-0063/red-c2.txt`: the `<ULID>\n` case failed, 8 passed). F2: the diff touched `tests/hooktools.py`, outside the two Outputs; restored to HEAD, the environment override now lives in the test file. F3 (cosmetic): the helpers are `_run_pair` and `_run_hook_in`, with docstrings naming their effects.
- **Cycle 2 (AUDIT-0153, PASS).** F4 (advisory, recorded): the F2 disposition named no red command for the scope correction. Acknowledged: a scope check has no command of its own; `git diff --staged --stat` listing two files is the evidence, and this report records it.
- **A red gate between the cycles (`gate:HANDOFF-0063:2`, failing=5)** was the builder's own doing: two untracked HANDOFF-0048 modules in the working tree failed `ruff`. They were moved to scratch and the cycle rerun; the gate reads the working tree, so a second handoff's files wait outside it while a first is under review.

## Acceptance
`make check` green at cycle 1 (788 passed) and at the cycle 2 gate. The acceptance test's three cases are the three tests above. `completed:` is AUDIT-0153's `created`, 2026-10-27T23:05:29-07:00.
