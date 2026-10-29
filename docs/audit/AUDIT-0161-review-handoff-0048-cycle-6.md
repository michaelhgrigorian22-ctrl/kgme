---
id: AUDIT-0161
type: report
status: final
handoff: HANDOFF-0048
author: codex
source: inferred
sources: ["HANDOFF-0048", "staged diff sha256 d49517a49ac340e9cf3a06f7a37f356030a42a8951876dcc5e3d7d030c5d291d"]
tier: 2
created: 2026-10-28T20:29:30-07:00
period: 2026-10-28
review_cycle: 6
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F23, F24]
---

# Review of HANDOFF-0048, cycle 6

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `d49517a49ac340e9cf3a06f7a37f356030a42a8951876dcc5e3d7d030c5d291d`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | tests/test_loose_route.py:37 | Isolation remains fixed. The live run supplies partial acceptance evidence; production acceptance remains unfinished. | Keep the handoff open and complete the deferred acceptance. |
| F2 | advisory | kgme/session_logic.py:88 | Argument and branch-validation residuals retain their recorded downgrade. | Retain them on the approval screen and adopt the follow-up. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | This patch preserves removal of the shared `.git` writable root. | Complete the deferred live ref-write refusal check. |
| F4 | blocking, resolved | kgme/workspace.py:120 | Escaping Outputs remain rejected. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:246 | Routing and repeated-plan fixes remain unchanged. | None. |
| F6 | blocking, resolved | tests/test_loop_codex.py:140 | Full split-ruling delivery and its regression remain unchanged. | None. |
| F7 | blocking, resolved | kgme/adapters/codex.py:99 | Complete-record cursor handling and duplicate suppression remain unchanged. | None. |
| F8 | blocking, resolved | kgme/loop.py:580 | Crew-to-loop ancestry remains connected. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Task-model propagation remains unchanged. | None. |
| F10 | blocking, resolved | kgme/crew_io.py:656 | Process registration and clearing remain intact. The new termination defect is F23. | Complete the deferred production Claude quarantine case. |
| F11 | blocking, resolved | kgme/crew_io.py:868 | Integration retains every integrated task’s acceptance check. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:915 | Integration review retains its detached candidate checkout and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:808 | Merge-gate exceptions remain quarantine-producing refusals. | None. |
| F14 | advisory | kgme/crew_io.py:491 | Scanner identity remains visible; the pinned-scanner rollout retains its recorded deferral. | Complete installation, hash verification, configuration and production evidence together. |
| F15 | blocking, resolved | kgme/skills.py:143 | Installed-copy verification and destination tracking remain unchanged. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:343 | Audit-glob materialization remains unchanged. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | Structural debt remains: `crew_io.py` has 987 lines, `crew.py` 431, `workspace.py` 349 and `loop.py` 835. Effect naming and separation gaps remain. | Complete the recorded structural follow-up. |
| F18 | blocking, resolved | kgme/crew.py:173 | Shared harness/model resolution remains unchanged. | None. |
| F19 | blocking, resolved | kgme/crew_io.py:462 | Tracked and untracked stray-write checks remain intact. | None. |
| F20 | blocking, resolved | kgme/review_run.py:192 | Task reviews retain Outputs, acceptance command and description. | None. |
| F21 | blocking, resolved | kgme/crew_io.py:297 | The planner still reads complete verified ruling payloads. | None. |
| F22 | cosmetic, resolved | kgme/crew_io.py:294 | The docstring now acknowledges the clipped-summary fallback. | None. |
| F23 | blocking | kgme/loop.py:390 | Termination now ignores surviving group members absent from the initial snapshot. If a SIGTERM handler spawns a child and exits, `proc.poll()` reaps the original leader and the intersection becomes empty. The function returns while the new child remains alive in the same group. No PID reuse is required. The added test covers an already-existing, cooperative child only. | Preserve termination coverage for children created during shutdown while checking process identity. Add a regression where a SIGTERM handler spawns a surviving child before exiting. |
| F24 | blocking | kgme/adapters/claude.py:41 | The advertised “exact commands” disagree with the pinned rules for valid directory Outputs without a trailing slash. For `kgme/widgets`, the prompt emits `git add -- kgme/widgets` and `git commit --only kgme/widgets -m …`; `session_logic.render` instead permits forms beginning `kgme/widgets/`. Following the prompt reproduces the permission denial this fix addresses. The regression covers only file Outputs. | Normalize directory command paths consistently with the permission renderer and test directory Outputs with and without trailing slashes. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | tests/test_loose_route.py:37 | Isolation remains fixed. The live run supplies partial acceptance evidence; production acceptance remains unfinished. | Keep the handoff open and complete the deferred acceptance. |
| F2 | advisory | kgme/session_logic.py:88 | Argument and branch-validation residuals retain their recorded downgrade. | Retain them on the approval screen and adopt the follow-up. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | This patch preserves removal of the shared `.git` writable root. | Complete the deferred live ref-write refusal check. |
| F4 | blocking, resolved | kgme/workspace.py:120 | Escaping Outputs remain rejected. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:246 | Routing and repeated-plan fixes remain unchanged. | None. |
| F6 | blocking, resolved | tests/test_loop_codex.py:140 | Full split-ruling delivery and its regression remain unchanged. | None. |
| F7 | blocking, resolved | kgme/adapters/codex.py:99 | Complete-record cursor handling and duplicate suppression remain unchanged. | None. |
| F8 | blocking, resolved | kgme/loop.py:580 | Crew-to-loop ancestry remains connected. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Task-model propagation remains unchanged. | None. |
| F10 | blocking, resolved | kgme/crew_io.py:656 | Process registration and clearing remain intact. The new termination defect is F23. | Complete the deferred production Claude quarantine case. |
| F11 | blocking, resolved | kgme/crew_io.py:868 | Integration retains every integrated task’s acceptance check. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:915 | Integration review retains its detached candidate checkout and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:808 | Merge-gate exceptions remain quarantine-producing refusals. | None. |
| F14 | advisory | kgme/crew_io.py:491 | Scanner identity remains visible; the pinned-scanner rollout retains its recorded deferral. | Complete installation, hash verification, configuration and production evidence together. |
| F15 | blocking, resolved | kgme/skills.py:143 | Installed-copy verification and destination tracking remain unchanged. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:343 | Audit-glob materialization remains unchanged. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | Structural debt remains: `crew_io.py` has 987 lines, `crew.py` 431, `workspace.py` 349 and `loop.py` 835. Effect naming and separation gaps remain. | Complete the recorded structural follow-up. |
| F18 | blocking, resolved | kgme/crew.py:173 | Shared harness/model resolution remains unchanged. | None. |
| F19 | blocking, resolved | kgme/crew_io.py:462 | Tracked and untracked stray-write checks remain intact. | None. |
| F20 | blocking, resolved | kgme/review_run.py:192 | Task reviews retain Outputs, acceptance command and description. | None. |
| F21 | blocking, resolved | kgme/crew_io.py:297 | The planner still reads complete verified ruling payloads. | None. |
| F22 | cosmetic, resolved | kgme/crew_io.py:294 | The docstring now acknowledges the clipped-summary fallback. | None. |
| F23 | blocking | kgme/loop.py:390 | Termination now ignores surviving group members absent from the initial snapshot. If a SIGTERM handler spawns a child and exits, `proc.poll()` reaps the original leader and the intersection becomes empty. The function returns while the new child remains alive in the same group. No PID reuse is required. The added test covers an already-existing, cooperative child only. | Preserve termination coverage for children created during shutdown while checking process identity. Add a regression where a SIGTERM handler spawns a surviving child before exiting. |
| F24 | blocking | kgme/adapters/claude.py:41 | The advertised “exact commands” disagree with the pinned rules for valid directory Outputs without a trailing slash. For `kgme/widgets`, the prompt emits `git add -- kgme/widgets` and `git commit --only kgme/widgets -m …`; `session_logic.render` instead permits forms beginning `kgme/widgets/`. Following the prompt reproduces the permission denial this fix addresses. The regression covers only file Outputs. | Normalize directory command paths consistently with the permission renderer and test directory Outputs with and without trailing slashes. |

## Verdict

BLOCK with 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix: **`d49517a49ac340e9`**, matching `review.sha`. No files were changed and no tests were run. The ledger records cycle 6’s gate as green at `2026-10-28T20:25:49-07:00`; `red-c6.txt` records the 3 pre-fix regression failures.

Acceptance coverage is distributed across the plan, workspace, merge-gate, crew, adapter, loose-route and policy tests. The new tests target detached-group detection, termination of an existing detached child and command generation for 2 file Outputs. They do not cover F23 or F24.

The recorded live run confirms 4 plan cycles, a completed Codex route, stray-write quarantine and rejection of incomplete integration. Both Claude builders failed before review. Successful production completion, all 4 seeded quarantine cases, `awaiting approval`, human fast-forward approval and the under-30-minute acceptance remain unproved as a complete run. Those completion obligations retain the existing deferral; they are not additional findings.

The patch adds no dependency, `TODO` or `shell=True`. The disclosed group-only behavior of `workspace.kill_recorded_group` remains outside this patch.
