---
id: HANDOFF-0066
type: handoff
created: 2026-10-28T01:20:00-07:00
from: michou
to: michou
status: open
tier: 2
depends_on: [HANDOFF-0048]
audit_ref: "AUDIT-0157 F2, ruled advisory by the arbiter pair (claude-opus-5-5, claude-fable-5-1), both asking for this follow-up"
---

# Handoff 0066 — the guard validates a loose builder's `git add` and `git commit` arguments before each call

## Why
HANDOFF-0048 amendment 2 lets a `loose` builder in a KGME workspace stage and commit on its own task branch by pathspec. The pinned list does the first half: one `Bash(git add -- <path>)` rule per Outputs entry and one `Bash(git commit --only <path> -m *)`, so `git add -A`, `git commit -a`, a bare commit and a checkout are refused (measured live, 2026-10-28). A prefix rule cannot see what follows the message: `--amend`, a second pathspec, a flag. The merge gate refuses a branch that carries a path outside the Outputs, so nothing lands, but the builder's own commit is not refused at the call. The arbiter pair ruled AUDIT-0157 F2 advisory on that ground and asked for a guard-side check as the follow-up.

## What
1. **Guard rule 6, in loop mode only** (`KGME_LOOP_HANDOFF` set): a Bash line whose segment starts with `git add` or `git commit` is parsed as git parses it; the call is refused when any pathspec is outside the Outputs list the guard already reads (rule 5), when `git add` carries `-A`, `-u`, `--all` or `.`, when `git commit` carries `-a`, `--amend`, `--no-verify` or no `--only <path>`, or when the workspace's `HEAD` is not the branch `KGME_LOOP_BRANCH` names (set by `kgme session loose --task` from the workspace record at launch). The refusal names the rule, as rule 5's does.
2. **The live-guard rule** stands: `kgme/hooks/guard.py` (pure) and `kgme/hooks/pre_tool_guard.py` change through a staged copy, exercised on the test streams and copied in whole.
3. **Cells**: `tests/test_guard_loop.py` for the pure decisions (`--amend`, a second pathspec after the message, `-a`, `-A`, a branch mismatch, and the allowed forms); `tests/test_loose_route.py` gains two refusal cells, `git commit --only <path> -m x --amend` and `git commit --only <path> other.py -m x`.

## Outputs
`kgme/hooks/guard.py`, `kgme/hooks/pre_tool_guard.py`, `kgme/session.py` (`KGME_LOOP_BRANCH`), `tests/test_guard_loop.py`, `tests/test_loose_route.py`.

## Acceptance test
From a workspace under the committed `loose.json`, a session is refused `git commit --only kgme/toy.py -m x --amend`, `git commit --only kgme/toy.py tests/other.py -m x` and `git add -- kgme/toy.py tests/other.py`, each by the guard with rule 6 named, and still commits `git commit --only kgme/toy.py -m x`. `make check` green.

## Needs from Michou
Adoption, after HANDOFF-0048 closes.
