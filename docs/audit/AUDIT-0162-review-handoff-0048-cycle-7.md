---
id: AUDIT-0162
type: report
status: final
handoff: HANDOFF-0048
author: codex
source: inferred
sources: ["HANDOFF-0048", "staged diff sha256 5c74018b30ada021f452616864c9e94a3a7962eb56a2d9be10041ac8a6c5b53a"]
tier: 2
created: 2026-10-28T20:42:09-07:00
period: 2026-10-28
review_cycle: 7
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F23]
---

# Review of HANDOFF-0048, cycle 7

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `5c74018b30ada021f452616864c9e94a3a7962eb56a2d9be10041ac8a6c5b53a`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | tests/test_loose_route.py:37 | Isolation remains fixed. Production acceptance remains incomplete under the recorded deferral. | Keep the handoff open until acceptance completes. |
| F2 | advisory | kgme/session_logic.py:94 | Argument and branch-validation residuals retain their recorded downgrade. | Retain them on the approval screen and adopt the follow-up. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | The shared `.git` writable root remains excluded. | Complete the deferred live ref-write refusal check. |
| F4 | blocking, resolved | kgme/workspace.py:120 | Escaping Outputs remain rejected. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:246 | Routing and repeated-plan fixes remain unchanged. | None. |
| F6 | blocking, resolved | tests/test_loop_codex.py:140 | Full split-ruling delivery and its regression remain unchanged. | None. |
| F7 | blocking, resolved | kgme/adapters/codex.py:99 | Complete-record cursor handling and duplicate suppression remain unchanged. | None. |
| F8 | blocking, resolved | kgme/loop.py:594 | Crew-to-loop ancestry remains connected. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Task-model propagation remains unchanged. | None. |
| F10 | blocking, resolved | kgme/crew_io.py:656 | Process registration and clearing remain intact. Termination remains addressed under F23. | Complete the deferred production Claude quarantine case. |
| F11 | blocking, resolved | kgme/crew_io.py:868 | Integration retains every integrated task’s acceptance check. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:915 | Integration review retains its detached candidate checkout and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:808 | Merge-gate exceptions remain quarantine-producing refusals. | None. |
| F14 | advisory | kgme/crew_io.py:491 | Scanner identity remains visible; the pinned-scanner rollout retains its recorded deferral. | Complete installation, hash verification, configuration and production evidence together. |
| F15 | blocking, resolved | kgme/skills.py:143 | Installed-copy verification and destination tracking remain unchanged. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:343 | Audit-glob materialization remains unchanged. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | Structural debt remains: `crew_io.py` has 987 lines, `crew.py` 431, `workspace.py` 349 and `loop.py` 849. Effect naming and separation gaps remain. | Complete the recorded structural follow-up. |
| F18 | blocking, resolved | kgme/crew.py:173 | Shared harness/model resolution remains unchanged. | None. |
| F19 | blocking, resolved | kgme/crew_io.py:462 | Tracked and untracked stray-write checks remain intact. | None. |
| F20 | blocking, resolved | kgme/review_run.py:192 | Task reviews retain Outputs, acceptance command and description. | None. |
| F21 | blocking, resolved | kgme/crew_io.py:297 | The planner still reads complete verified ruling payloads. | None. |
| F22 | cosmetic, resolved | kgme/crew_io.py:294 | The docstring correctly acknowledges the clipped-summary fallback. | None. |
| F23 | blocking | kgme/loop.py:385 | The same-group shutdown child is now covered, but sampled groups do not establish identity or complete descendant coverage. A TERM handler can spawn a child with `start_new_session=True` and exit before the next poll. Once reparented, that child belongs neither to a known group nor to the leader’s visible descendants, so `kill_group` returns with it alive. Separately, a group can disappear and its ID be reused between polls; `known & occupied` then retains an unrelated group for SIGKILL. | Preserve shutdown coverage and process identity across polling gaps. Add regressions for a newly detached, reparented shutdown child and group disappearance/reuse between snapshots. |
| F24 | blocking, resolved | kgme/adapters/claude.py:43 | Prompt generation and permission rendering now share `is_folder`; the regression covers directory Outputs with and without trailing slashes alongside a file Output. | None. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | tests/test_loose_route.py:37 | Isolation remains fixed. Production acceptance remains incomplete under the recorded deferral. | Keep the handoff open until acceptance completes. |
| F2 | advisory | kgme/session_logic.py:94 | Argument and branch-validation residuals retain their recorded downgrade. | Retain them on the approval screen and adopt the follow-up. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | The shared `.git` writable root remains excluded. | Complete the deferred live ref-write refusal check. |
| F4 | blocking, resolved | kgme/workspace.py:120 | Escaping Outputs remain rejected. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:246 | Routing and repeated-plan fixes remain unchanged. | None. |
| F6 | blocking, resolved | tests/test_loop_codex.py:140 | Full split-ruling delivery and its regression remain unchanged. | None. |
| F7 | blocking, resolved | kgme/adapters/codex.py:99 | Complete-record cursor handling and duplicate suppression remain unchanged. | None. |
| F8 | blocking, resolved | kgme/loop.py:594 | Crew-to-loop ancestry remains connected. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Task-model propagation remains unchanged. | None. |
| F10 | blocking, resolved | kgme/crew_io.py:656 | Process registration and clearing remain intact. Termination remains addressed under F23. | Complete the deferred production Claude quarantine case. |
| F11 | blocking, resolved | kgme/crew_io.py:868 | Integration retains every integrated task’s acceptance check. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:915 | Integration review retains its detached candidate checkout and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:808 | Merge-gate exceptions remain quarantine-producing refusals. | None. |
| F14 | advisory | kgme/crew_io.py:491 | Scanner identity remains visible; the pinned-scanner rollout retains its recorded deferral. | Complete installation, hash verification, configuration and production evidence together. |
| F15 | blocking, resolved | kgme/skills.py:143 | Installed-copy verification and destination tracking remain unchanged. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:343 | Audit-glob materialization remains unchanged. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | Structural debt remains: `crew_io.py` has 987 lines, `crew.py` 431, `workspace.py` 349 and `loop.py` 849. Effect naming and separation gaps remain. | Complete the recorded structural follow-up. |
| F18 | blocking, resolved | kgme/crew.py:173 | Shared harness/model resolution remains unchanged. | None. |
| F19 | blocking, resolved | kgme/crew_io.py:462 | Tracked and untracked stray-write checks remain intact. | None. |
| F20 | blocking, resolved | kgme/review_run.py:192 | Task reviews retain Outputs, acceptance command and description. | None. |
| F21 | blocking, resolved | kgme/crew_io.py:297 | The planner still reads complete verified ruling payloads. | None. |
| F22 | cosmetic, resolved | kgme/crew_io.py:294 | The docstring correctly acknowledges the clipped-summary fallback. | None. |
| F23 | blocking | kgme/loop.py:385 | The same-group shutdown child is now covered, but sampled groups do not establish identity or complete descendant coverage. A TERM handler can spawn a child with `start_new_session=True` and exit before the next poll. Once reparented, that child belongs neither to a known group nor to the leader’s visible descendants, so `kill_group` returns with it alive. Separately, a group can disappear and its ID be reused between polls; `known & occupied` then retains an unrelated group for SIGKILL. | Preserve shutdown coverage and process identity across polling gaps. Add regressions for a newly detached, reparented shutdown child and group disappearance/reuse between snapshots. |
| F24 | blocking, resolved | kgme/adapters/claude.py:43 | Prompt generation and permission rendering now share `is_folder`; the regression covers directory Outputs with and without trailing slashes alongside a file Output. | None. |

## Verdict

BLOCK with 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`5c74018b30ada021`**, independently verified against the patch and `review.sha`. No files were changed and no tests were run. The ledger records cycle 7’s gate as green at `2026-10-28T20:40:42.599-07:00`; `red-c7.txt` records the 2 pre-fix regression failures.

F23 follows directly from the code: after a previously unseen detached child is reparented, its snapshot row is `(child, 1, child_group)`. With the original group gone, `tree_groups` returns an empty set. The new regression instead keeps its child in the original group and checks only that group. Observing occupancy at successive polls also does not prove uninterrupted occupancy between them.

Acceptance coverage remains distributed across the route, plan, workspace, adapter, merge-gate, crew and policy tests. The recorded live run demonstrates 4 plan cycles, a completed Codex route, stray-write quarantine and rejection of incomplete integration. Successful production completion, all 4 seeded quarantine cases, `awaiting approval`, human fast-forward approval and the under-30-minute requirement remain unproved together. Their existing deferral stands.

The patch adds no dependency, `TODO` or `shell=True`. The disclosed behavior of `workspace.kill_recorded_group` remains outside this diff.
