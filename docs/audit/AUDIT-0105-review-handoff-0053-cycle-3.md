---
id: AUDIT-0105
type: report
status: final
handoff: HANDOFF-0053
author: codex
source: inferred
sources: ["HANDOFF-0053", "staged diff sha256 9bf0823c3389eedc8a5070b9d7850c0186dc620558698594b2091ddb7ac36ea1"]
tier: 2
created: 2026-10-25T09:19:28-07:00
period: 2026-10-25
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8]
---

# Review of HANDOFF-0053, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `9bf0823c3389eedc8a5070b9d7850c0186dc620558698594b2091ddb7ac36ea1`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | [kgme/cheap.py:146](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:146) | The verifier now carries absolute secret-path denies and all 3 configured filename patterns. The regression covers planted files and secret-root configuration; the recorded red run demonstrates the original exposure. | No further change for the reported verifier exposure. |
| F2 | blocking, resolved | [kgme/cheap.py:244](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:244) | Both agent homes remain denied at the permission and sandbox layers, with regression coverage. | No further change. |
| F3 | blocking, resolved | [kgme/cheap.py:55](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:55) | Subprocesses use argument lists. The 6 rejection cases still cover shell syntax and refusal before export. | No further change. |
| F4 | blocking, resolved | [kgme/cheap.py:419](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:419) | Both reported launch and patch failures reach the terminal note and return exit 2. Both regressions remain present. | No further change for the reported failures. |
| F5 | cosmetic | [kgme/cheap.py:1](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:1) | Deferred. `cheap.py`, `test_cheap.py`, and `session.py` contain 456, 461, and 409 lines. Pure logic remains mixed with effects; session documentation still omits the cheap route. | Complete the recorded separation and documentation follow-up. |
| F6 | cosmetic, resolved | [tests/policy/test_agents_cheap.py:69](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:69) | The Ollama probe remains inside the live fixture, avoiding collection-time network access. | No further change. |
| F7 | cosmetic, resolved | [tests/policy/test_agents_cheap.py:28](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:28) | All 4 live tests inherit `blocking`; the toy test also carries its class marker. | No further change. |
| F8 | blocking | [kgme/cheap.py:281](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:281) | The live session’s Bash sandbox still receives only fixed roots, omitting the 3 filename denies. An allowed pytest script can construct a `.env` path outside those roots and return its contents to the cloud model. Static hook scanning cannot enforce dynamically constructed paths. The report explicitly acknowledges this exposure; F1’s regression exercises only the final verifier. | Enforce the inherited filename restrictions at the live Bash sandbox boundary, or equivalently restrict readable locations. Add a regression using harmless planted files and dynamically constructed paths through an allowed Bash command. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | [kgme/cheap.py:146](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:146) | The verifier now carries absolute secret-path denies and all 3 configured filename patterns. The regression covers planted files and secret-root configuration; the recorded red run demonstrates the original exposure. | No further change for the reported verifier exposure. |
| F2 | blocking, resolved | [kgme/cheap.py:244](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:244) | Both agent homes remain denied at the permission and sandbox layers, with regression coverage. | No further change. |
| F3 | blocking, resolved | [kgme/cheap.py:55](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:55) | Subprocesses use argument lists. The 6 rejection cases still cover shell syntax and refusal before export. | No further change. |
| F4 | blocking, resolved | [kgme/cheap.py:419](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:419) | Both reported launch and patch failures reach the terminal note and return exit 2. Both regressions remain present. | No further change for the reported failures. |
| F5 | cosmetic | [kgme/cheap.py:1](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:1) | Deferred. `cheap.py`, `test_cheap.py`, and `session.py` contain 456, 461, and 409 lines. Pure logic remains mixed with effects; session documentation still omits the cheap route. | Complete the recorded separation and documentation follow-up. |
| F6 | cosmetic, resolved | [tests/policy/test_agents_cheap.py:69](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:69) | The Ollama probe remains inside the live fixture, avoiding collection-time network access. | No further change. |
| F7 | cosmetic, resolved | [tests/policy/test_agents_cheap.py:28](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:28) | All 4 live tests inherit `blocking`; the toy test also carries its class marker. | No further change. |
| F8 | blocking | [kgme/cheap.py:281](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:281) | The live session’s Bash sandbox still receives only fixed roots, omitting the 3 filename denies. An allowed pytest script can construct a `.env` path outside those roots and return its contents to the cloud model. Static hook scanning cannot enforce dynamically constructed paths. The report explicitly acknowledges this exposure; F1’s regression exercises only the final verifier. | Enforce the inherited filename restrictions at the live Bash sandbox boundary, or equivalently restrict readable locations. Add a regression using harmless planted files and dynamically constructed paths through an allowed Bash command. |

## Verdict

BLOCK: 1 open blocking finding, F8.

## Notes

Reviewed SHA-256 prefix **`9bf0823c3389eedc`**, matching `review.sha`. No files were changed and no tests were run.

Acceptance behavior has deterministic tests and 4 stated live results covering repair, patch application, `make check`, export isolation, refusals, and ledger placement. The report discloses using a fresh clone instead of a worktree. Its **551 passed** result is builder-reported, not independently rerun.

F1 closes the final-verifier exposure. F8 concerns the separate live-session boundary documented in [the report](/Users/michaelgrigorian/Projects/KGME/brain/docs/audit/2026-10-24-cheap-lane.md:37). The reader-section draft exists outside this patch; its completion remains under F5.
