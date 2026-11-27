---
id: AUDIT-0181
type: report
status: final
handoff: HANDOFF-0078:plan
author: codex
source: inferred
sources: ["HANDOFF-0078:plan", "staged diff sha256 a1f6b99b302f2474e501ec467931858da266ba73fa3d9c2d3691ff930f2ad88c"]
tier: 2
created: 2026-11-27T13:02:36-08:00
period: 2026-11-27
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5]
---

# Review of HANDOFF-0078:plan, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `a1f6b99b302f2474e501ec467931858da266ba73fa3d9c2d3691ff930f2ad88c`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | plan | The `audit` and `report` acceptance commands use `&&`, but `kgme/crew_io.py:444` executes `shlex.split(command)` without a shell. The second command never executes; `audit` instead passes extra arguments to `kgme lint`. | Express each check as one executable command, such as an interpreter invocation that performs assertions and runs subprocesses with explicit argument lists. |
| F2 | blocking | plan:audit | Even after F1 is fixed, lint plus one heading does not establish that §1 supplied the evidence required by §2. The task explicitly permits answers pending Michou’s output, while `names` and `code-tools` depend on those answers. The command also accepts the “§2 not built” outcome without distinguishing it from readiness to build. | Validate the required evidence structure and establish an explicit build-ready condition. Pending prerequisite measurements or no reachable hook must keep §2 undispatched and route the report for the required ruling. |
| F3 | blocking | plan:report | The plan substitutes report code blocks for the files expressly required under `logs/scratch/handoff-0078/`: installation changes, the conditional plugin and install step, the DEBT diff, and any measurement script. Being gitignored explains why these files do not merge; it does not remove the deliverables. The report’s heading check cannot detect their absence. | Assign production of the actual scratch files, record their accessible workspace locations, and specify how they reach Michou. Preserve report copies if useful, and check the applicable artifacts rather than only a heading. |
| F4 | blocking | plan:code-tools | `tests/test_hermes_fence.py:114` currently requires `delegate_task` without a base directory to pass. Rule 3 requires refusal for this code-running tool. No task owns that test file, so the required implementation conflicts with the existing suite and cannot pass the crew’s `make check` merge gate. | Add the file to this task’s Outputs and acceptance coverage. Explicitly reconcile this necessary assertion change with the handoff’s instruction that other fence tests remain unchanged. |
| F5 | blocking | plan:audit | `AUDIT-0181` is hardcoded throughout the plan but is not reserved. It is currently the next available ID, and `kgme/review_run.py:254–260` allocates that ID when recording this plan review, before the audit task runs. The proposed report would therefore reuse an allocated ID. | Coordinate a collision-free report ID with the main-checkout audit allocator and update every dependent reference. Merely incrementing the hardcoded number before another review repeats the allocation problem. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | plan | The `audit` and `report` acceptance commands use `&&`, but `kgme/crew_io.py:444` executes `shlex.split(command)` without a shell. The second command never executes; `audit` instead passes extra arguments to `kgme lint`. | Express each check as one executable command, such as an interpreter invocation that performs assertions and runs subprocesses with explicit argument lists. |
| F2 | blocking | plan:audit | Even after F1 is fixed, lint plus one heading does not establish that §1 supplied the evidence required by §2. The task explicitly permits answers pending Michou’s output, while `names` and `code-tools` depend on those answers. The command also accepts the “§2 not built” outcome without distinguishing it from readiness to build. | Validate the required evidence structure and establish an explicit build-ready condition. Pending prerequisite measurements or no reachable hook must keep §2 undispatched and route the report for the required ruling. |
| F3 | blocking | plan:report | The plan substitutes report code blocks for the files expressly required under `logs/scratch/handoff-0078/`: installation changes, the conditional plugin and install step, the DEBT diff, and any measurement script. Being gitignored explains why these files do not merge; it does not remove the deliverables. The report’s heading check cannot detect their absence. | Assign production of the actual scratch files, record their accessible workspace locations, and specify how they reach Michou. Preserve report copies if useful, and check the applicable artifacts rather than only a heading. |
| F4 | blocking | plan:code-tools | `tests/test_hermes_fence.py:114` currently requires `delegate_task` without a base directory to pass. Rule 3 requires refusal for this code-running tool. No task owns that test file, so the required implementation conflicts with the existing suite and cannot pass the crew’s `make check` merge gate. | Add the file to this task’s Outputs and acceptance coverage. Explicitly reconcile this necessary assertion change with the handoff’s instruction that other fence tests remain unchanged. |
| F5 | blocking | plan:audit | `AUDIT-0181` is hardcoded throughout the plan but is not reserved. It is currently the next available ID, and `kgme/review_run.py:254–260` allocates that ID when recording this plan review, before the audit task runs. The proposed report would therefore reuse an allocated ID. | Coordinate a collision-free report ID with the main-checkout audit allocator and update every dependent reference. Merely incrementing the hardcoded number before another review repeats the allocation problem. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `a1f6b99b302f2474`. Acceptance commands were inspected, not executed; no files were modified.

The policy tasks’ shared Outputs justify their serial dependencies. The handoff specifies no incompatible harness or model requirement. `make check` already runs at the crew merge gate, so its omission from individual acceptance commands is not an additional finding.
