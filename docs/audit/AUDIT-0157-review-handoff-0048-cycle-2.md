---
id: AUDIT-0157
type: report
status: final
handoff: HANDOFF-0048
author: codex
source: inferred
sources: ["HANDOFF-0048", "staged diff sha256 1383e5b72043204d7a9e499946368ccd91f089cb032050fc3c894b1efe301cd8"]
tier: 2
created: 2026-10-28T00:53:06-07:00
period: 2026-10-28
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F6, F7, F14, F18, F19, F20]
---

# Review of HANDOFF-0048, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `1383e5b72043204d7a9e499946368ccd91f089cb032050fc3c894b1efe301cd8`. Verdict **BLOCK**: blocking 8, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_loose_route.py:34 | Acceptance remains incomplete. The reviewed test reuses `HANDOFF-9048`; `route-live-5.txt` fails after prior review history affects the run. `route-live-6.txt` passes with a newer, process-specific handoff ID absent from this patch. The crew test substitutes stub builders and does not demonstrate the complete production acceptance route. | Include the test-isolation fix in the reviewed patch and supply acceptance coverage through the production adapters, including the four seeded quarantines. Keep the handoff open. Human-path application remains Michou’s step. |
| F2 | blocking | kgme/session_logic.py:88 | The narrower rules still permit trailing arguments. For example, `git commit --only kgme/toy.py -m probe --amend` matches the generated wildcard. Additional pathspecs also fit after the message. The existing guard validates neither these arguments nor the branch before each write; the branch check occurs only at launch. | Validate parsed git arguments, every pathspec, and the recorded branch immediately before each mutation, or use a constrained supervisor. Test trailing `--amend`, extra paths, and a branch change after launch. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | The explicit shared `.git` writable root is removed. Codex staging and committing now belong to the supervisor; the adapter test checks the narrowed roots. | None for the original defect. Retain the requested live ref-write refusal evidence. |
| F4 | blocking, resolved | kgme/workspace.py:120 | The plan parser drops absolute and escaping paths, and workspace creation rejects tasks containing them. The regression test covers both entry points. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:228 | Settled rulings now reach the planner, and repetition detection accounts for intervening rulings. The seeded downgrade test exercises an unchanged plan returning successfully. | None. |
| F6 | blocking | kgme/crew_io.py:543 | Codex now uses the common loop, but recommended rulings still do not enter its next request. `run_codex_cycle` returns only the findings table; `_run_one` constructs and starts the next request before `_supervise` performs arbitration. A recommended correction can therefore remain unseen by the builder. | Settle pending arbitration before restarting Codex, then include its recommendation and reason in the request. Test a persistent blocker requiring execution of a recommended option. |
| F7 | blocking | kgme/adapters/codex.py:92 | Starts, file changes, and interrupted outcomes are added, but partial JSON lines can disappear permanently. An incomplete final line fails parsing while `state["lines"]` still advances; the completed version of that same line is skipped on the next poll. | Advance only past complete records and retain the unfinished suffix. Test records split across polls and reconcile emitted events against the complete stream. |
| F8 | blocking, resolved | kgme/crew_io.py:586 | The crew intent now enters the loop’s parent interface, and `KGME_LOOP_PARENT` continues the ancestry through hooks. The shared-loop test asserts the crew-to-loop-to-tool chain. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Claude’s launcher now takes the model resolved into the workspace record. The launcher test verifies that an explicit task model overrides the global builder model. | None for the original Claude defect. See F18 for the remaining dispatch defaults. |
| F10 | blocking, resolved | kgme/crew_io.py:588 | Both harnesses use the process-registration callback, which records and clears the builder’s process group. The common-loop test verifies that lifecycle. | None for the missing registration. Include the production Claude quarantine case in the outstanding acceptance evidence. |
| F11 | blocking, resolved | kgme/crew_io.py:800 | Integration reruns every integrated task’s acceptance command. The later-task regression test verifies that breaking an earlier oracle prevents approval readiness. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:848 | Integration review now reads a detached checkout of the candidate SHA while retaining the main checkout’s audit and ledger destinations. The test inspects candidate files and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:739 | Merge-gate execution exceptions become refusals followed by quarantine. Missing acceptance executables and acceptance timeouts become red checks; the missing-command test verifies that an independent task continues. | None for the original merge-gate escape. |
| F14 | blocking | kgme/crew_io.py:347 | Configured scanners now require a matching executable hash, but an absent scanner still silently selects the eight local regex rules. The proposed configuration leaves gitleaks commented out, and no real pinned-scanner quarantine evidence is supplied. Section 5’s required scanner remains optional in production. | Fail closed until the required scanner is configured and pinned. Supply its toolbox/install proposal and exercise the seeded-key quarantine through that scanner once applied. |
| F15 | blocking, resolved | kgme/skills.py:143 | Lint now hashes installed copy contents against the canonical source and remembers external copy destinations. Tests cover edits on either side and ordinary subsequent lint discovery. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:339 | The glob iterator is consumed with `list(...)`; the original always-failing assertion is corrected. The remaining route-test failure is separate and covered by F1. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | The pure task definitions moved, but the structural issue remains: `crew_io.py` has 919 lines, `crew.py` 403, and `workspace.py` 349. Effects such as `skill_sha256`, `is_ours`, and adapter `start`/`kill` still lack ADR-015’s prefixes. | Complete the recorded module split, effect naming, and public annotations in the follow-up. |
| F18 | blocking | kgme/crew_io.py:579 | Dispatch defaults remain inconsistent. A blank Codex task model is resolved for telemetry but the unresolved task reaches `adapter.argv`, so `-m` is omitted. `parse_plan` also hardcodes Claude when the harness is omitted. Reassigning an explicit Codex task to Claude preserves its Codex model. | Resolve and validate harness/model together before recording or launching the task. Pass that resolved task throughout dispatch. Test omitted fields and Codex-to-Claude fallback with distinct model IDs. |
| F19 | blocking | kgme/crew_io.py:523 | The supervisor stages only declared Outputs, while the merge gate inspects only committed branch changes. An additional uncommitted write to `kgme.toml` or another forbidden output can therefore disappear from gate consideration instead of quarantining the task. The conformance cell supplies a fabricated changed-path list directly to the pure gate, bypassing this production gap. | Inspect tracked and untracked workspace changes before selective staging and reject forbidden changes. Exercise the actual supervisor and merge gate with the seeded extra write. |
| F20 | blocking | kgme/review_run.py:176 | Task reviews still receive the complete handoff’s What and Acceptance test, without the approved task description, Outputs, acceptance command, or plan context. A legitimate first task of a three-task handoff is consequently presented as an incomplete implementation of the whole handoff. Toy reviewers cannot expose this mismatch. | Carry the approved task contract into task-review prompts and reserve whole-handoff completion checks for integration. Test the prompt contents for a partial task. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_loose_route.py:34 | Acceptance remains incomplete. The reviewed test reuses `HANDOFF-9048`; `route-live-5.txt` fails after prior review history affects the run. `route-live-6.txt` passes with a newer, process-specific handoff ID absent from this patch. The crew test substitutes stub builders and does not demonstrate the complete production acceptance route. | Include the test-isolation fix in the reviewed patch and supply acceptance coverage through the production adapters, including the four seeded quarantines. Keep the handoff open. Human-path application remains Michou’s step. |
| F2 | blocking | kgme/session_logic.py:88 | The narrower rules still permit trailing arguments. For example, `git commit --only kgme/toy.py -m probe --amend` matches the generated wildcard. Additional pathspecs also fit after the message. The existing guard validates neither these arguments nor the branch before each write; the branch check occurs only at launch. | Validate parsed git arguments, every pathspec, and the recorded branch immediately before each mutation, or use a constrained supervisor. Test trailing `--amend`, extra paths, and a branch change after launch. |
| F3 | blocking, resolved | kgme/adapters/codex.py:42 | The explicit shared `.git` writable root is removed. Codex staging and committing now belong to the supervisor; the adapter test checks the narrowed roots. | None for the original defect. Retain the requested live ref-write refusal evidence. |
| F4 | blocking, resolved | kgme/workspace.py:120 | The plan parser drops absolute and escaping paths, and workspace creation rejects tasks containing them. The regression test covers both entry points. | None. |
| F5 | blocking, resolved | kgme/crew_io.py:228 | Settled rulings now reach the planner, and repetition detection accounts for intervening rulings. The seeded downgrade test exercises an unchanged plan returning successfully. | None. |
| F6 | blocking | kgme/crew_io.py:543 | Codex now uses the common loop, but recommended rulings still do not enter its next request. `run_codex_cycle` returns only the findings table; `_run_one` constructs and starts the next request before `_supervise` performs arbitration. A recommended correction can therefore remain unseen by the builder. | Settle pending arbitration before restarting Codex, then include its recommendation and reason in the request. Test a persistent blocker requiring execution of a recommended option. |
| F7 | blocking | kgme/adapters/codex.py:92 | Starts, file changes, and interrupted outcomes are added, but partial JSON lines can disappear permanently. An incomplete final line fails parsing while `state["lines"]` still advances; the completed version of that same line is skipped on the next poll. | Advance only past complete records and retain the unfinished suffix. Test records split across polls and reconcile emitted events against the complete stream. |
| F8 | blocking, resolved | kgme/crew_io.py:586 | The crew intent now enters the loop’s parent interface, and `KGME_LOOP_PARENT` continues the ancestry through hooks. The shared-loop test asserts the crew-to-loop-to-tool chain. | None. |
| F9 | blocking, resolved | kgme/session.py:191 | Claude’s launcher now takes the model resolved into the workspace record. The launcher test verifies that an explicit task model overrides the global builder model. | None for the original Claude defect. See F18 for the remaining dispatch defaults. |
| F10 | blocking, resolved | kgme/crew_io.py:588 | Both harnesses use the process-registration callback, which records and clears the builder’s process group. The common-loop test verifies that lifecycle. | None for the missing registration. Include the production Claude quarantine case in the outstanding acceptance evidence. |
| F11 | blocking, resolved | kgme/crew_io.py:800 | Integration reruns every integrated task’s acceptance command. The later-task regression test verifies that breaking an earlier oracle prevents approval readiness. | None. |
| F12 | blocking, resolved | kgme/crew_io.py:848 | Integration review now reads a detached checkout of the candidate SHA while retaining the main checkout’s audit and ledger destinations. The test inspects candidate files and cleanup. | None. |
| F13 | blocking, resolved | kgme/crew_io.py:739 | Merge-gate execution exceptions become refusals followed by quarantine. Missing acceptance executables and acceptance timeouts become red checks; the missing-command test verifies that an independent task continues. | None for the original merge-gate escape. |
| F14 | blocking | kgme/crew_io.py:347 | Configured scanners now require a matching executable hash, but an absent scanner still silently selects the eight local regex rules. The proposed configuration leaves gitleaks commented out, and no real pinned-scanner quarantine evidence is supplied. Section 5’s required scanner remains optional in production. | Fail closed until the required scanner is configured and pinned. Supply its toolbox/install proposal and exercise the seeded-key quarantine through that scanner once applied. |
| F15 | blocking, resolved | kgme/skills.py:143 | Lint now hashes installed copy contents against the canonical source and remembers external copy destinations. Tests cover edits on either side and ordinary subsequent lint discovery. | None. |
| F16 | blocking, resolved | tests/test_loose_route.py:339 | The glob iterator is consumed with `list(...)`; the original always-failing assertion is corrected. The remaining route-test failure is separate and covered by F1. | None. |
| F17 | cosmetic | kgme/crew_io.py:1 | The pure task definitions moved, but the structural issue remains: `crew_io.py` has 919 lines, `crew.py` 403, and `workspace.py` 349. Effects such as `skill_sha256`, `is_ours`, and adapter `start`/`kill` still lack ADR-015’s prefixes. | Complete the recorded module split, effect naming, and public annotations in the follow-up. |
| F18 | blocking | kgme/crew_io.py:579 | Dispatch defaults remain inconsistent. A blank Codex task model is resolved for telemetry but the unresolved task reaches `adapter.argv`, so `-m` is omitted. `parse_plan` also hardcodes Claude when the harness is omitted. Reassigning an explicit Codex task to Claude preserves its Codex model. | Resolve and validate harness/model together before recording or launching the task. Pass that resolved task throughout dispatch. Test omitted fields and Codex-to-Claude fallback with distinct model IDs. |
| F19 | blocking | kgme/crew_io.py:523 | The supervisor stages only declared Outputs, while the merge gate inspects only committed branch changes. An additional uncommitted write to `kgme.toml` or another forbidden output can therefore disappear from gate consideration instead of quarantining the task. The conformance cell supplies a fabricated changed-path list directly to the pure gate, bypassing this production gap. | Inspect tracked and untracked workspace changes before selective staging and reject forbidden changes. Exercise the actual supervisor and merge gate with the seeded extra write. |
| F20 | blocking | kgme/review_run.py:176 | Task reviews still receive the complete handoff’s What and Acceptance test, without the approved task description, Outputs, acceptance command, or plan context. A legitimate first task of a three-task handoff is consequently presented as an incomplete implementation of the whole handoff. Toy reviewers cannot expose this mismatch. | Carry the approved task contract into task-review prompts and reserve whole-handoff completion checks for integration. Test the prompt contents for a partial task. |

## Verdict

BLOCK with 8 open blocking findings.

## Notes

Reviewed SHA-256 prefix: **`1383e5b72043204d`**, verified before and after inspection. No files were modified and no tests were run.

Retained evidence reports `make check` exiting 0 with **834 passed, 2 skipped**, and Codex conformance **4 passed**. The later route run reports **1 passed**, but uses test changes outside this patch. These results support specific fixes without establishing complete acceptance.

The authorized human-path deferral is acknowledged. It does not establish acceptance completion or justify the scanner’s permissive fallback. No added `TODO`, `shell=True`, or dependency-manifest change was found.
