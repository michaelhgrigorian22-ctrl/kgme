---
id: AUDIT-0148
type: report
status: final
handoff: HANDOFF-0043
author: codex
source: inferred
sources: ["HANDOFF-0043", "staged diff sha256 65e2b180711bab65192d19a45b506b9ab5af3b8a4c7a51301f58b67148994256"]
tier: 2
created: 2026-10-26T18:28:25-07:00
period: 2026-10-26
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11]
---

# Review of HANDOFF-0043, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `65e2b180711bab65192d19a45b506b9ab5af3b8a4c7a51301f58b67148994256`. Verdict **BLOCK**: blocking 11, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/loop.py:349 | The default launcher supplies no user prompt, and `start_builder` closes stdin. The existing session launcher forwards those arguments; its carried system context does not supply an execution request. The toy replaces this launch entirely. | Ensure the session receives the adopted handoff’s execution request. Test the actual launcher through a stub harness that validates its inputs. |
| F2 | blocking | kgme/loop.py:466 | The production path cannot complete build → review → commit. `loose` requires a worktree, `run_review` refuses worktrees, and the pinned loose permissions exclude staging, committing and invoking review. The supervisor supplies none of those operations. The audit acknowledges the review gap at line 96; deferring it to 0048 leaves 0043 nonfunctional. | Provide a permitted, trusted route for reviewing and committing the workspace’s exact diff. Exercise that route under the actual loose restrictions. |
| F3 | blocking | kgme/loop.py:493 | Closure requires only an earlier successful PASS outcome. A PASS followed by a red gate or failed review attempt still produces `closed`; no commit or completed handoff is required. This can report success with `commit none` and unfinished work. | Validate the final gate, review and deliverable state together. Test PASS followed by a red gate, failed review and missing commit; distinguish “ready, diffs pending” from completed work. |
| F4 | blocking | kgme/loop.py:463 | `KGME_LOOP_PARENT` connects only the toy’s events. Production hooks ignore it and create their own session tree through `read_session_parent`. The audit confirms this at line 97, so the acceptance requirement of one tree under the first intent is unmet. | Establish the parent relationship through the production session and hook path, and test those actual event constructors. |
| F5 | blocking | kgme/review_run.py:479 | If 1 arbiter fails, the remaining reply is settled as agreement. If both fail, `_supervise` has already marked the finding arbitrated and never retries it. A transient failure therefore either bypasses the required pair or permanently disables arbitration. | Require 2 valid, distinct replies before settlement. Retain incomplete arbitration as pending and retry transient failures with recorded handling. Test both partial and total failure. |
| F6 | blocking | kgme/loop.py:158 | When both disagreeing options are irreversible, `min` still selects one automatically. ADR-023 §3 requires a split among one-way doors to reach Michou. The existing test covers only 1 irreversible option competing with a reversible option. | Return an escalation state when no reversible option exists, prevent automatic execution, and test a split containing 2 irreversible options. |
| F7 | blocking | kgme/review_run.py:358 | Ruling validation accepts missing fields, treats `"false"` as reversible, accepts blast radii outside 1–5, and raises on a nonnumeric radius. Malformed model output can therefore select an unsafe option or crash supervision instead of becoming a recorded failed reply. | Validate all required fields and their exact types and ranges. Reject malformed replies without settlement or an uncaught exception. |
| F8 | blocking | kgme/review.py:178 | Any blocking outcome ordered after a ruling is treated as proof that the ruling was executed. Because automatic arbitration runs alongside the builder, a review started before the ruling can finish afterward and trigger a false halt without any intervening fix. | Tie the halt measure to recorded execution of the ruling and a subsequent review. Test an already-running review completing after settlement. |
| F9 | blocking | kgme/review_run.py:425 | The arbiter receives only the first 60,000 characters of the diff, without a truncation notice or access to omitted content. This patch is 126,074 bytes. Findings concerning later files can therefore be settled without the evidence amendment 20 requires. | Supply the complete relevant evidence with explicit provenance, or refuse settlement when it cannot be supplied. Test a finding beyond the current cutoff. |
| F10 | blocking | kgme/loop.py:471 | Each restart replaces `run.usage`. If a builder consumes tokens before a limit and then resumes, the closing payload reports only the final attempt, understating the per-handoff usage required by amendment 18. | Preserve usage per attempt and aggregate compatible counters and cost. Test 2 attempts that both report nonzero usage. |
| F11 | blocking | kgme/loop.py:310 | Queue admission accepts `from: cowork`, although adoption amendment 13 specifically restricts this unattended queue to `from: michou`. The broader interactive handoff rule does not satisfy that narrower admission condition. | Enforce the adopted queue condition and test rejection of an otherwise-open Cowork handoff. |
| F12 | cosmetic | kgme/loop.py:1; kgme/review_run.py:1; tests/test_loop.py:1 | ADR-015’s structure conventions are not met: these files contain 622, 496 and 393 lines. `loop.py` mixes logic with effects, and effect names including `start_builder`, `signal_group`, `kill_group` and `_passed` evade the prescribed naming convention. | Separate logic and effects into focused modules near the 300-line guideline, and use the prescribed effect prefixes. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/loop.py:349 | The default launcher supplies no user prompt, and `start_builder` closes stdin. The existing session launcher forwards those arguments; its carried system context does not supply an execution request. The toy replaces this launch entirely. | Ensure the session receives the adopted handoff’s execution request. Test the actual launcher through a stub harness that validates its inputs. |
| F2 | blocking | kgme/loop.py:466 | The production path cannot complete build → review → commit. `loose` requires a worktree, `run_review` refuses worktrees, and the pinned loose permissions exclude staging, committing and invoking review. The supervisor supplies none of those operations. The audit acknowledges the review gap at line 96; deferring it to 0048 leaves 0043 nonfunctional. | Provide a permitted, trusted route for reviewing and committing the workspace’s exact diff. Exercise that route under the actual loose restrictions. |
| F3 | blocking | kgme/loop.py:493 | Closure requires only an earlier successful PASS outcome. A PASS followed by a red gate or failed review attempt still produces `closed`; no commit or completed handoff is required. This can report success with `commit none` and unfinished work. | Validate the final gate, review and deliverable state together. Test PASS followed by a red gate, failed review and missing commit; distinguish “ready, diffs pending” from completed work. |
| F4 | blocking | kgme/loop.py:463 | `KGME_LOOP_PARENT` connects only the toy’s events. Production hooks ignore it and create their own session tree through `read_session_parent`. The audit confirms this at line 97, so the acceptance requirement of one tree under the first intent is unmet. | Establish the parent relationship through the production session and hook path, and test those actual event constructors. |
| F5 | blocking | kgme/review_run.py:479 | If 1 arbiter fails, the remaining reply is settled as agreement. If both fail, `_supervise` has already marked the finding arbitrated and never retries it. A transient failure therefore either bypasses the required pair or permanently disables arbitration. | Require 2 valid, distinct replies before settlement. Retain incomplete arbitration as pending and retry transient failures with recorded handling. Test both partial and total failure. |
| F6 | blocking | kgme/loop.py:158 | When both disagreeing options are irreversible, `min` still selects one automatically. ADR-023 §3 requires a split among one-way doors to reach Michou. The existing test covers only 1 irreversible option competing with a reversible option. | Return an escalation state when no reversible option exists, prevent automatic execution, and test a split containing 2 irreversible options. |
| F7 | blocking | kgme/review_run.py:358 | Ruling validation accepts missing fields, treats `"false"` as reversible, accepts blast radii outside 1–5, and raises on a nonnumeric radius. Malformed model output can therefore select an unsafe option or crash supervision instead of becoming a recorded failed reply. | Validate all required fields and their exact types and ranges. Reject malformed replies without settlement or an uncaught exception. |
| F8 | blocking | kgme/review.py:178 | Any blocking outcome ordered after a ruling is treated as proof that the ruling was executed. Because automatic arbitration runs alongside the builder, a review started before the ruling can finish afterward and trigger a false halt without any intervening fix. | Tie the halt measure to recorded execution of the ruling and a subsequent review. Test an already-running review completing after settlement. |
| F9 | blocking | kgme/review_run.py:425 | The arbiter receives only the first 60,000 characters of the diff, without a truncation notice or access to omitted content. This patch is 126,074 bytes. Findings concerning later files can therefore be settled without the evidence amendment 20 requires. | Supply the complete relevant evidence with explicit provenance, or refuse settlement when it cannot be supplied. Test a finding beyond the current cutoff. |
| F10 | blocking | kgme/loop.py:471 | Each restart replaces `run.usage`. If a builder consumes tokens before a limit and then resumes, the closing payload reports only the final attempt, understating the per-handoff usage required by amendment 18. | Preserve usage per attempt and aggregate compatible counters and cost. Test 2 attempts that both report nonzero usage. |
| F11 | blocking | kgme/loop.py:310 | Queue admission accepts `from: cowork`, although adoption amendment 13 specifically restricts this unattended queue to `from: michou`. The broader interactive handoff rule does not satisfy that narrower admission condition. | Enforce the adopted queue condition and test rejection of an otherwise-open Cowork handoff. |
| F12 | cosmetic | kgme/loop.py:1; kgme/review_run.py:1; tests/test_loop.py:1 | ADR-015’s structure conventions are not met: these files contain 622, 496 and 393 lines. `loop.py` mixes logic with effects, and effect names including `start_builder`, `signal_group`, `kill_group` and `_passed` evade the prescribed naming convention. | Separate logic and effects into focused modules near the 300-line guideline, and use the prescribed effect prefixes. |

## Verdict

BLOCK: 11 blocking findings remain open.

## Notes

Reviewed SHA-256 prefix: `65e2b180711bab65`, matching `review.sha`.

The toy tests cover closure, agreeing arbitration and queue continuation, split settlement, stall handling, reset-time and fallback pauses, and `caffeinate`. They substitute the launcher and hook behavior implicated in F1, F2 and F4. Split settlement is tested directly rather than through a complete builder execution.

The audit states 759 passing tests and live responses from both configured arbiters. I did not rerun tests or modify files. Tooling restrictions are not findings against the diff.

The stated rulings on compaction, parser scope and the unverified Claude limit form were accepted. No dependency changes, `TODO`, or `shell=True` were introduced.
