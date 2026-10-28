---
id: AUDIT-0156
type: report
status: final
handoff: HANDOFF-0048
author: codex
source: inferred
sources: ["HANDOFF-0048", "staged diff sha256 f9e42081ff28d31884d52214d9b68ffe97210c85f6ea63da99d93dd46c006699"]
tier: 2
created: 2026-10-27T23:53:52-07:00
period: 2026-10-27
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16]
---

# Review of HANDOFF-0048, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `f9e42081ff28d31884d52214d9b68ffe97210c85f6ea63da99d93dd46c006699`. Verdict **BLOCK**: blocking 16, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_loose_route.py:73 | Amendment 2’s mandatory route remains unavailable under committed policy. Its tests skip when the required rules are absent. The production plan-review prompt is also absent, so `crew` refuses to start. Only role skills may remain pending under amendment 10. | Land the approved policy and prompt changes, then supply the required route and crew acceptance evidence. Keep the handoff open meanwhile. |
| F2 | blocking | kgme/session.py:218 | Task validation checks workspace, state and Outputs, but never verifies the checked-out branch or enforces commit pathspecs. The proposed broad `git add *` and `git commit *` permissions therefore lack amendment 2’s required guard. Refusing `checkout main` does not prove refusal of a commit on another branch. | Enforce the recorded task branch and explicit permitted pathspecs before each git write. Test commits on another branch, commits without pathspecs, and amendments. |
| F3 | blocking | kgme/adapters/codex.py:35 | Codex receives the main checkout’s entire `.git` directory as writable. This includes `main` and integration refs, config and other worktree metadata, allowing changes outside the task branch before any merge gate or approval. | Keep shared git metadata outside the builder’s writable roots. Perform staging and other required git mutations through a constrained supervisor. Add a ref-write refusal cell. |
| F4 | blocking | kgme/crew.py:185 | Outputs validation accepts absolute paths and `..` components. Those values reach `session.render`, which normalizes them into sandbox write allowances outside the workspace. The mechanical plan gate can therefore widen the task’s filesystem boundary. | Reject noncanonical, absolute and escaping paths before workspace creation or policy rendering. Apply the same validation to `workspace create`; test both entry points. |
| F5 | blocking | kgme/crew_io.py:233 | Plan arbitration records rulings but sends only the previous findings table back to the planner. Recommended actions never enter its next request. Additionally, the repeated-plan check at line 210 stops an unchanged plan even after a ruling downgrades its blocker. | Pass settled rulings and recommendations into the next planner request, and make repetition detection account for intervening rulings. Test downgrade and recommended-option cycles. |
| F6 | blocking | kgme/crew_io.py:467 | The separate Codex loop omits arbitration and provider-limit pause/resume, stops after 6 cycles, and treats elapsed time without a completed command as a stall even while a child command is alive. This does not implement amendment 6’s shared supervision contract. | Use the common loop machinery or equivalent shared supervision, including arbitration, measured non-convergence, limit handling and live-child-aware stall detection. |
| F7 | blocking | kgme/adapters/codex.py:93 | Only completed `command_execution` items become ledger events. File-change and other tool events are discarded, and a command killed before completion leaves no intent. The required record of every builder tool call is incomplete. | Record tool starts and terminal outcomes across supported event types, including interrupted calls. Test stream reconciliation against the emitted ledger events. |
| F8 | blocking | kgme/crew_io.py:461 | Claude receives `KGME_CREW_RUN`, but nothing consumes it. Its loop intent has no crew parent, and hooks attach to that independent loop tree. Claude tool calls therefore do not sit under the crew’s run as acceptance requires. | Pass the crew intent through the loop’s parent interface and preserve the ancestry through session hooks. Assert the complete crew-to-tool chain. |
| F9 | blocking | kgme/adapters/claude.py:28 | The selected task model never reaches Claude’s launcher. `session.read_launch` always selects `[models].builder`; `run_claude_task` passes the requested model only into loop telemetry. The approval screen can name a model that did not build the task. | Resolve defaults once and pass the selected model through the actual launcher. Test differing task, crew-default and global-builder models. |
| F10 | blocking | kgme/crew_io.py:452 | Claude’s process group is never written into its workspace record. `workspace quarantine` can consequently rename and lock a running Claude workspace without killing its builder or children; the quarantine test manually supplies the missing `pgid`. | Register and clear the actual process group through the common supervisor. Test quarantine against a Claude task launched through the production route. |
| F11 | blocking | kgme/crew_io.py:774 | Integration runs `make check` with an empty acceptance command. Earlier task acceptance checks are not rerun on the final result, so a later task can break an earlier task’s oracle while the crew still reaches `awaiting approval`. | Verify the final integration commit against the handoff’s acceptance requirements and retained task checks. Add a later-task regression case. |
| F12 | blocking | kgme/crew_io.py:780 | Integration review receives `places` pointing at the main checkout. The patch describes the integration commit, but repository reads see the old main tree. Cross-file behavior and newly added files cannot be reviewed against the actual candidate. | Run integration review in a read-only checkout of the exact candidate SHA, retaining the main checkout’s ledger and audits. |
| F13 | blocking | kgme/crew_io.py:719 | A missing acceptance executable, check timeout or git exception escapes the merge gate and aborts the crew. The task remains writable, no quarantine outcome closes it, and independent tasks stop. | Convert gate execution failures into classified outcomes with guaranteed cleanup and quarantine where required; continue independent tasks. Test missing-command and timeout paths. |
| F14 | blocking | kgme/crew_io.py:284 | Section 5’s pinned scanner is not delivered. The default uses 8 local regex rules; a configured scanner is executed from PATH without verifying its pinned version or toolbox record. | Supply the required pinned scanner and toolbox evidence, validate its identity before dispatch, and exercise its seeded-key quarantine path. |
| F15 | blocking | kgme/skills.py:123 | Copy lint compares the source hash with the installation marker, never with the installed copy’s bytes. Editing the copy alone therefore passes. External `--copy` destinations are also forgotten by ordinary `kgme lint`. | Persist installed destinations and compare actual copy contents with the canonical skill. Test copy edits, source edits and external destinations. |
| F16 | blocking | tests/test_loose_route.py:306 | `Path.glob()` returns a truthy iterator. The assertion `assert not ...glob(...)` always fails once this live test is enabled, even when no workspace audit exists. | Consume the iterator with `list` or `any`, then run the enabled route test and retain its evidence. |
| F17 | cosmetic | kgme/crew_io.py:1 | ADR-015’s structure and effect conventions are not met: this new module has 883 lines, `workspace.py` has 408, and effects include names such as `skill_sha256`, `is_ours` and `kill_recorded_group`. The pure crew module imports its task definitions from an effects-heavy workspace module. | Split orchestration along plan, task and integration boundaries; move shared values into a pure module; use the required effect prefixes and complete public annotations. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_loose_route.py:73 | Amendment 2’s mandatory route remains unavailable under committed policy. Its tests skip when the required rules are absent. The production plan-review prompt is also absent, so `crew` refuses to start. Only role skills may remain pending under amendment 10. | Land the approved policy and prompt changes, then supply the required route and crew acceptance evidence. Keep the handoff open meanwhile. |
| F2 | blocking | kgme/session.py:218 | Task validation checks workspace, state and Outputs, but never verifies the checked-out branch or enforces commit pathspecs. The proposed broad `git add *` and `git commit *` permissions therefore lack amendment 2’s required guard. Refusing `checkout main` does not prove refusal of a commit on another branch. | Enforce the recorded task branch and explicit permitted pathspecs before each git write. Test commits on another branch, commits without pathspecs, and amendments. |
| F3 | blocking | kgme/adapters/codex.py:35 | Codex receives the main checkout’s entire `.git` directory as writable. This includes `main` and integration refs, config and other worktree metadata, allowing changes outside the task branch before any merge gate or approval. | Keep shared git metadata outside the builder’s writable roots. Perform staging and other required git mutations through a constrained supervisor. Add a ref-write refusal cell. |
| F4 | blocking | kgme/crew.py:185 | Outputs validation accepts absolute paths and `..` components. Those values reach `session.render`, which normalizes them into sandbox write allowances outside the workspace. The mechanical plan gate can therefore widen the task’s filesystem boundary. | Reject noncanonical, absolute and escaping paths before workspace creation or policy rendering. Apply the same validation to `workspace create`; test both entry points. |
| F5 | blocking | kgme/crew_io.py:233 | Plan arbitration records rulings but sends only the previous findings table back to the planner. Recommended actions never enter its next request. Additionally, the repeated-plan check at line 210 stops an unchanged plan even after a ruling downgrades its blocker. | Pass settled rulings and recommendations into the next planner request, and make repetition detection account for intervening rulings. Test downgrade and recommended-option cycles. |
| F6 | blocking | kgme/crew_io.py:467 | The separate Codex loop omits arbitration and provider-limit pause/resume, stops after 6 cycles, and treats elapsed time without a completed command as a stall even while a child command is alive. This does not implement amendment 6’s shared supervision contract. | Use the common loop machinery or equivalent shared supervision, including arbitration, measured non-convergence, limit handling and live-child-aware stall detection. |
| F7 | blocking | kgme/adapters/codex.py:93 | Only completed `command_execution` items become ledger events. File-change and other tool events are discarded, and a command killed before completion leaves no intent. The required record of every builder tool call is incomplete. | Record tool starts and terminal outcomes across supported event types, including interrupted calls. Test stream reconciliation against the emitted ledger events. |
| F8 | blocking | kgme/crew_io.py:461 | Claude receives `KGME_CREW_RUN`, but nothing consumes it. Its loop intent has no crew parent, and hooks attach to that independent loop tree. Claude tool calls therefore do not sit under the crew’s run as acceptance requires. | Pass the crew intent through the loop’s parent interface and preserve the ancestry through session hooks. Assert the complete crew-to-tool chain. |
| F9 | blocking | kgme/adapters/claude.py:28 | The selected task model never reaches Claude’s launcher. `session.read_launch` always selects `[models].builder`; `run_claude_task` passes the requested model only into loop telemetry. The approval screen can name a model that did not build the task. | Resolve defaults once and pass the selected model through the actual launcher. Test differing task, crew-default and global-builder models. |
| F10 | blocking | kgme/crew_io.py:452 | Claude’s process group is never written into its workspace record. `workspace quarantine` can consequently rename and lock a running Claude workspace without killing its builder or children; the quarantine test manually supplies the missing `pgid`. | Register and clear the actual process group through the common supervisor. Test quarantine against a Claude task launched through the production route. |
| F11 | blocking | kgme/crew_io.py:774 | Integration runs `make check` with an empty acceptance command. Earlier task acceptance checks are not rerun on the final result, so a later task can break an earlier task’s oracle while the crew still reaches `awaiting approval`. | Verify the final integration commit against the handoff’s acceptance requirements and retained task checks. Add a later-task regression case. |
| F12 | blocking | kgme/crew_io.py:780 | Integration review receives `places` pointing at the main checkout. The patch describes the integration commit, but repository reads see the old main tree. Cross-file behavior and newly added files cannot be reviewed against the actual candidate. | Run integration review in a read-only checkout of the exact candidate SHA, retaining the main checkout’s ledger and audits. |
| F13 | blocking | kgme/crew_io.py:719 | A missing acceptance executable, check timeout or git exception escapes the merge gate and aborts the crew. The task remains writable, no quarantine outcome closes it, and independent tasks stop. | Convert gate execution failures into classified outcomes with guaranteed cleanup and quarantine where required; continue independent tasks. Test missing-command and timeout paths. |
| F14 | blocking | kgme/crew_io.py:284 | Section 5’s pinned scanner is not delivered. The default uses 8 local regex rules; a configured scanner is executed from PATH without verifying its pinned version or toolbox record. | Supply the required pinned scanner and toolbox evidence, validate its identity before dispatch, and exercise its seeded-key quarantine path. |
| F15 | blocking | kgme/skills.py:123 | Copy lint compares the source hash with the installation marker, never with the installed copy’s bytes. Editing the copy alone therefore passes. External `--copy` destinations are also forgotten by ordinary `kgme lint`. | Persist installed destinations and compare actual copy contents with the canonical skill. Test copy edits, source edits and external destinations. |
| F16 | blocking | tests/test_loose_route.py:306 | `Path.glob()` returns a truthy iterator. The assertion `assert not ...glob(...)` always fails once this live test is enabled, even when no workspace audit exists. | Consume the iterator with `list` or `any`, then run the enabled route test and retain its evidence. |
| F17 | cosmetic | kgme/crew_io.py:1 | ADR-015’s structure and effect conventions are not met: this new module has 883 lines, `workspace.py` has 408, and effects include names such as `skill_sha256`, `is_ours` and `kill_recorded_group`. The pure crew module imports its task definitions from an effects-heavy workspace module. | Split orchestration along plan, task and integration boundaries; move shared values into a pure module; use the required effect prefixes and complete public annotations. |

## Verdict

BLOCK with 16 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `f9e42081ff28d318`.

No files were changed and no tests were run. The supplied check log reports **825 passed, 2 skipped and 49 deselected**. It does not establish the amended live acceptance case: crew builders are stubbed in the orchestration test, required route tests skip, and AUDIT-0155 still contains result placeholders.

The unavailable memory index and sandbox diagnostics are tooling limits, not findings against this diff.
