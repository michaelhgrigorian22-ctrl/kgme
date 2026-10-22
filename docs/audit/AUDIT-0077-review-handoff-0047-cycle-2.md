---
id: AUDIT-0077
type: report
status: final
handoff: HANDOFF-0047
author: codex
source: inferred
sources: ["HANDOFF-0047", "staged diff sha256 88aa18149f843040eaca06ac3a478a5ee8b9bbee1baac6a0a0d8bd1cbd78477f"]
tier: 2
created: 2026-10-21T16:31:45-07:00
period: 2026-10-21
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F9, F10, F11]
---

# Review of HANDOFF-0047, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `88aa18149f843040eaca06ac3a478a5ee8b9bbee1baac6a0a0d8bd1cbd78477f`. Verdict **BLOCK**: blocking 4, transient 0, cosmetic 0, advisory 2 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/session.py:174](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:174) | Repository membership is checked, but policy validation remains a substring search. A settings file containing `pre_tool_guard` without an operative hook passes. Missing deny rules also pass; the test fixture contains none. | Validate the effective hook configuration and mandatory deny rules. Test an inert guard-name string, a nonmatching hook, and missing deny rules. |
| F2 | blocking, resolved | [kgme/session.py:99](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:99) | Extra options are now restricted to 3 output-related flags. The tests cover the 9 previously identified widening arguments. | No further change for this finding. |
| F3 | blocking, resolved | [kgme/session.py:245](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:245) | Session payloads now reside in the main checkout with references relative to it. The worktree launcher test reads the recorded payload from that checkout. | No further change for this finding. |
| F4 | blocking, resolved | [kgme/ledger.py:87](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:87) | `read_base_dirs` now resolves worktree streams to the main checkout. The separate regression this introduces for production payloads is F10. | No further change to the stream-routing fix itself. |
| F5 | blocking, resolved | [kgme/session.py:133](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:133) | The launcher now checks location, open status, and authorized author. Tests cover 4 non-executable handoff cases. | No further change for this finding. |
| F6 | advisory | [tests/policy/test_agents_sessions.py:142](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:142) | The settings hash is now recorded, closing the original configuration-identity gap. Remaining provenance incompleteness: the recorded argv omits the output flags and prompt appended at line 158; the digest assertion checks the in-memory value rather than reading the persisted note. | Record the final invocation and verify its settings digest through the saved note. |
| F7 | blocking, resolved | [tests/policy/test_agents_sessions.py:221](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:221) | The prescribed arbitration changes are present: canonical commands, network-only paired controls, strict checks for required cells, and 5 tight attempts followed by explicit `xfail` beside the deterministic proof. Tight is no longer reported as demonstrated refusal. | Retain the outstanding tight acceptance decision in the human approval packet. The separate retry-counting defect is F11. |
| F8 | advisory | [kgme/session.py:68](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:68) | `render` no longer resolves filesystem paths. ADR-015’s module separation remains incomplete: rendering and argument logic still share a module with filesystem and process effects. | Separate the pure logic from the named effects layer. |
| F9 | blocking | [kgme/session.py:238](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:238) | The launcher writes the Outputs list under the main checkout, while `hooks.common.read_places` supplies worktree-local scratch to the guard. Consequently, every file write is refused, including authorized Outputs. The saved loose-write canary explicitly reports “no Outputs list” and “every write is refused,” yet counts as a pass. | Make writer and reader resolve the same Outputs-list location. Add a worktree integration test proving that an inside-Outputs write is allowed and an outside write is refused for the intended reason. |
| F10 | blocking | [kgme/ledger.py:87](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:87) | Pinning production streams leaves production payloads behind. For example, capture and brief still construct payload paths and references from the worktree, but their events now enter the main ledger. Those references cannot resolve from the main checkout. The F4 regression test calls only the directory resolver, not a production writer. | Separate the task workspace from the shared record root across payload writers and readers. Test a production write from a worktree and resolve its recorded payload from main. |
| F11 | blocking | [tests/policy/test_agents_sessions.py:196](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:196) | Network retries reuse one cumulative listener counter. The paired control increments that counter after attempt 1; if another attempt runs, `listener.hits > 0` attributes the previous control connection to the worker and falsely reports that enforcement failed. | Isolate worker observations per attempt, excluding previous controls. Add a deterministic case with an inconclusive first attempt followed by a refused attempt. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/session.py:174](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:174) | Repository membership is checked, but policy validation remains a substring search. A settings file containing `pre_tool_guard` without an operative hook passes. Missing deny rules also pass; the test fixture contains none. | Validate the effective hook configuration and mandatory deny rules. Test an inert guard-name string, a nonmatching hook, and missing deny rules. |
| F2 | blocking, resolved | [kgme/session.py:99](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:99) | Extra options are now restricted to 3 output-related flags. The tests cover the 9 previously identified widening arguments. | No further change for this finding. |
| F3 | blocking, resolved | [kgme/session.py:245](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:245) | Session payloads now reside in the main checkout with references relative to it. The worktree launcher test reads the recorded payload from that checkout. | No further change for this finding. |
| F4 | blocking, resolved | [kgme/ledger.py:87](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:87) | `read_base_dirs` now resolves worktree streams to the main checkout. The separate regression this introduces for production payloads is F10. | No further change to the stream-routing fix itself. |
| F5 | blocking, resolved | [kgme/session.py:133](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:133) | The launcher now checks location, open status, and authorized author. Tests cover 4 non-executable handoff cases. | No further change for this finding. |
| F6 | advisory | [tests/policy/test_agents_sessions.py:142](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:142) | The settings hash is now recorded, closing the original configuration-identity gap. Remaining provenance incompleteness: the recorded argv omits the output flags and prompt appended at line 158; the digest assertion checks the in-memory value rather than reading the persisted note. | Record the final invocation and verify its settings digest through the saved note. |
| F7 | blocking, resolved | [tests/policy/test_agents_sessions.py:221](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:221) | The prescribed arbitration changes are present: canonical commands, network-only paired controls, strict checks for required cells, and 5 tight attempts followed by explicit `xfail` beside the deterministic proof. Tight is no longer reported as demonstrated refusal. | Retain the outstanding tight acceptance decision in the human approval packet. The separate retry-counting defect is F11. |
| F8 | advisory | [kgme/session.py:68](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:68) | `render` no longer resolves filesystem paths. ADR-015’s module separation remains incomplete: rendering and argument logic still share a module with filesystem and process effects. | Separate the pure logic from the named effects layer. |
| F9 | blocking | [kgme/session.py:238](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:238) | The launcher writes the Outputs list under the main checkout, while `hooks.common.read_places` supplies worktree-local scratch to the guard. Consequently, every file write is refused, including authorized Outputs. The saved loose-write canary explicitly reports “no Outputs list” and “every write is refused,” yet counts as a pass. | Make writer and reader resolve the same Outputs-list location. Add a worktree integration test proving that an inside-Outputs write is allowed and an outside write is refused for the intended reason. |
| F10 | blocking | [kgme/ledger.py:87](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:87) | Pinning production streams leaves production payloads behind. For example, capture and brief still construct payload paths and references from the worktree, but their events now enter the main ledger. Those references cannot resolve from the main checkout. The F4 regression test calls only the directory resolver, not a production writer. | Separate the task workspace from the shared record root across payload writers and readers. Test a production write from a worktree and resolve its recorded payload from main. |
| F11 | blocking | [tests/policy/test_agents_sessions.py:196](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:196) | Network retries reuse one cumulative listener counter. The paired control increments that counter after attempt 1; if another attempt runs, `listener.hits > 0` attributes the previous control connection to the worker and falsely reports that enforcement failed. | Isolate worker observations per attempt, excluding previous controls. Add a deterministic case with an inconclusive first attempt followed by a refused attempt. |

## Verdict

BLOCK with 4 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`88aa18149f843040`**, verified against the patch and `review.sha`. No files were changed and no tests were run.

The concurrency test covers 8 processes × 500 events, complete JSON lines, unique IDs, and complete event coverage. The patch adds no dependencies, executable `TODO`, or `shell=True`; subprocess calls use argument lists.

Acceptance evidence remains qualified: tight’s live refusal is unproved after 5 attempts, the real `kgme session work` worktree launch is explicitly deferred, and `kgs` installation remains pending. The recorded Bash cwd residual and removal of staging/commit permissions are accepted decisions and are not reopened here.
