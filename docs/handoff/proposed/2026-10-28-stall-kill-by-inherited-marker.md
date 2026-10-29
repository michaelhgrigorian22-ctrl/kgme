---
id: HANDOFF-0068
type: handoff
created: 2026-10-28T21:05:00-07:00
from: claude-code
to: michou
status: proposed
tier: 2
depends_on: [HANDOFF-0048]
audit_ref: "AUDIT-0161 and AUDIT-0162 F23, ruled advisory by the arbiter pair (claude-opus-5-5, claude-fable-5-1), both naming this follow-up"
---

# Proposal 0068: the stall kill finds a builder's tree by an inherited marker

## Why
`kgme loop` kills a stalled builder's whole tree (HANDOFF-0048 review cycles 6 and 7, after the live toy crew of 2026-10-28 showed a healthy `make check` call invisible by process group): the leader's group, every group a Bash call of the session detached into, and every group that stays occupied through the grace window. Two residuals stand, ruled advisory by the arbiter pair (AUDIT-0162 F23): a child that detaches into a new session and is reparented between two polls escapes the tree, and a group id emptied and reused between two polls is kept as a target. Both windows are the poll's 100 ms, and an escaped process meets a read-only quarantined worktree. Identity by process ids cannot close them from user space on macOS; identity by inheritance can.

## What
1. `loop.start_builder` sets `KGME_LOOP_RUN=<the loop run's id>` in the builder's environment; every descendant inherits it, whatever its session, group or parent.
2. A reader beside `loop.read_group`: `read_marked(run)`, the pids whose environment carries the marker, from `ps -A -E -o pid=,command=` (macOS prints the user's own processes with their environment), parsed on the marker alone and never printing an environment.
3. `kill_group` signals the union of the tree it finds today and the marked pids, at SIGTERM and again at SIGKILL; a marked pid is signalled by pid, so no group id is ever hit by reuse.
4. Cells: `tests/test_loop.py` gains a leader whose SIGTERM handler starts a child in a new session and exits before the next poll (the child is gone after the kill), and a pure test of the marker parser on a fixed `ps` line; the stall cell of `tests/policy/test_agents_adapters.py` stays a stub, since a live model cannot be made to hang on cue.

## Outputs
`kgme/loop.py`, `tests/test_loop.py`.

## Acceptance test
A builder started by `kgme loop` whose Bash call double-forks a `sleep` into a new session is killed with that `sleep` when the stall switch fires; `make check` green; no environment printed in any log or ledger line.

## Needs from Michou
Adoption, after HANDOFF-0048 closes.
