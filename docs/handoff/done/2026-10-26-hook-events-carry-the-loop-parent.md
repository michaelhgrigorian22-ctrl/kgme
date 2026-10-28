---
id: HANDOFF-0063
type: handoff
created: 2026-10-26T20:30:00-07:00
from: michou
to: claude-code
status: done
completed: 2026-10-27T23:05:29-07:00
report: docs/audit/2026-10-27-hook-events-under-the-loop-parent.md
tier: 2
depends_on: [HANDOFF-0043]
audit_ref: "AUDIT-0148 F4, ruled advisory by the arbiter pair (claude-opus-5-5, claude-fable-5-1), both asking for this follow-up"
---

# Handoff 0063: a loop session's hook events sit under the loop's first intent

## Why
HANDOFF-0043's acceptance test asks for one tree under the loop's first intent. The toy meets it, because its builder stub writes `parent` from `KGME_LOOP_PARENT`. A real `kgme session loose` session's events come from the live hooks, which take `parent` from `kgme/hooks/common.py` `read_session_parent`: the session's own first event. So a real run's tool events form their own tree. `kgme loop` writes a `loop:` note naming the session id, so the run is reachable through its run id, but not through `parent`. The arbiter pair ruled AUDIT-0148 F4 advisory, on the ground that the live hook modules are outside 0043's Outputs, and both arbiters asked for this proposal.

## What
1. **`read_session_parent`** returns `KGME_LOOP_PARENT` when it is set, has the shape of an event id, and the session has no first event yet. The session's own first event, the loop's `session` note, then sits under the loop's intent, and every later pair under that event, as today.
2. **Tests on the production constructors.** `tests/test_hooks.py` runs the pre and post hooks through `run_hook` with the variable set and unset, and asserts the parent chain. A malformed value is ignored, never trusted.
3. **The guard module changes only through a staged copy** (the live-guard rule): edit in scratch, test on the test streams, copy in whole.

## Outputs
`kgme/hooks/common.py`, `tests/test_hooks.py`.

## Acceptance test
A hook pair run with `KGME_LOOP_PARENT=<an intent id>` and a fresh session id has its first event's `parent` equal to that id. The same run without the variable, or with a value that is not an event id, keeps today's chain. `make check` green.

## Reviewer
Codex under `kgme review`.

## Needs from Michou
Adoption, after HANDOFF-0043 lands.
