---
id: AUDIT-0103
type: report
status: final
handoff: HANDOFF-0053
author: codex
source: inferred
sources: ["HANDOFF-0053", "staged diff sha256 333118cf872d632c1195b57feb813366bf5b97bd9714bd50f0139e546676905e"]
tier: 2
created: 2026-10-24T20:12:42-07:00
period: 2026-10-24
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4]
---

# Review of HANDOFF-0053, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `333118cf872d632c1195b57feb813366bf5b97bd9714bd50f0139e546676905e`. Verdict **BLOCK**: blocking 4, transient 0, cosmetic 3, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/cheap.py:136](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:136) | The final red-command check executes model-edited code outside Claude’s sandbox, with the launcher’s filesystem and network access. An edited imported module can therefore read denied roots or modify the main checkout before review. | Run verification within the same enforced filesystem and network boundary. Add a regression proving that imported code cannot access a planted forbidden file or write outside the export. |
| F2 | blocking | [kgme/hooks/pre_tool_guard.py:53](/Users/michaelgrigorian/Projects/KGME/brain/kgme/hooks/pre_tool_guard.py:53) | The cheap guard retains `allow_outside`, including `~/.claude/projects`, which `kgme.toml:87` identifies as containing project memory. The template allows `Read`, and the added denies omit this location. Other projects’ memory and transcripts remain readable, violating the code-only boundary. | Restrict the cheap route’s external reads and add refusal coverage for project memory and transcripts through file tools and Bash. |
| F3 | blocking | [kgme/cheap.py:137](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:137); [tests/policy/test_agents_cheap.py:167](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:167) | Both subprocess calls use shell strings with `shell=True`, explicitly prohibited by ADR-015. | Parse and validate the supported command into an argument list, reject unsupported shell syntax, and use argument lists at both sites. |
| F4 | blocking | [kgme/cheap.py:347](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:347) | After the start note, a launch exception or patch-generation failure escapes before the end note. For example, a missing `claude` executable leaves an unmatched start and no recorded failure, contrary to What §4 and ADR-015. | Add a failure boundary that records the terminal reason and available artifacts whenever the ledger remains writable. Cover launch and patch-generation failures. |
| F5 | cosmetic | [kgme/cheap.py:1](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:1) | The new module has 370 lines and combines pure policy/model/result logic with process and filesystem effects. `tests/test_cheap.py` has 332 lines; `session.py` grows from 360 to 409. This misses ADR-015’s separation and approximately 300-line conventions. | Separate pure logic from effects and split tests by concern. Update the session module’s documentation to describe the new route. |
| F6 | cosmetic | [tests/policy/test_agents_cheap.py:41](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:41) | `ollama_up` performs network I/O without an effects name or docstring. Its module-level invocation also probes Ollama during collection before agent tests are deselected. | Move the probe into the live fixture, give it a `read_*` or `run_*` name, and document its inputs, output, and network effect. |
| F7 | cosmetic | [tests/policy/test_agents_cheap.py:28](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:28) | The 4 live tests carry only `agents`; the toy test also lacks an ADR-016 class. | Add the appropriate class markers, consistent with the existing session canaries. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/cheap.py:136](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:136) | The final red-command check executes model-edited code outside Claude’s sandbox, with the launcher’s filesystem and network access. An edited imported module can therefore read denied roots or modify the main checkout before review. | Run verification within the same enforced filesystem and network boundary. Add a regression proving that imported code cannot access a planted forbidden file or write outside the export. |
| F2 | blocking | [kgme/hooks/pre_tool_guard.py:53](/Users/michaelgrigorian/Projects/KGME/brain/kgme/hooks/pre_tool_guard.py:53) | The cheap guard retains `allow_outside`, including `~/.claude/projects`, which `kgme.toml:87` identifies as containing project memory. The template allows `Read`, and the added denies omit this location. Other projects’ memory and transcripts remain readable, violating the code-only boundary. | Restrict the cheap route’s external reads and add refusal coverage for project memory and transcripts through file tools and Bash. |
| F3 | blocking | [kgme/cheap.py:137](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:137); [tests/policy/test_agents_cheap.py:167](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:167) | Both subprocess calls use shell strings with `shell=True`, explicitly prohibited by ADR-015. | Parse and validate the supported command into an argument list, reject unsupported shell syntax, and use argument lists at both sites. |
| F4 | blocking | [kgme/cheap.py:347](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:347) | After the start note, a launch exception or patch-generation failure escapes before the end note. For example, a missing `claude` executable leaves an unmatched start and no recorded failure, contrary to What §4 and ADR-015. | Add a failure boundary that records the terminal reason and available artifacts whenever the ledger remains writable. Cover launch and patch-generation failures. |
| F5 | cosmetic | [kgme/cheap.py:1](/Users/michaelgrigorian/Projects/KGME/brain/kgme/cheap.py:1) | The new module has 370 lines and combines pure policy/model/result logic with process and filesystem effects. `tests/test_cheap.py` has 332 lines; `session.py` grows from 360 to 409. This misses ADR-015’s separation and approximately 300-line conventions. | Separate pure logic from effects and split tests by concern. Update the session module’s documentation to describe the new route. |
| F6 | cosmetic | [tests/policy/test_agents_cheap.py:41](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:41) | `ollama_up` performs network I/O without an effects name or docstring. Its module-level invocation also probes Ollama during collection before agent tests are deselected. | Move the probe into the live fixture, give it a `read_*` or `run_*` name, and document its inputs, output, and network effect. |
| F7 | cosmetic | [tests/policy/test_agents_cheap.py:28](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_cheap.py:28) | The 4 live tests carry only `agents`; the toy test also lacks an ADR-016 class. | Add the appropriate class markers, consistent with the existing session canaries. |

## Verdict

BLOCK with 4 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `333118cf872d632c`, matching `review.sha`.

Acceptance items have tests or stated evidence: deterministic coverage addresses routing, export contents/history, policy construction, patch application, and both ledger notes. The report records a 9-turn live fix, patch replay and `make check` in a clone, plus the 3 refusal cells. It explicitly discloses that the acceptance test did not finish uninterrupted; remaining assertions were checked separately.

The clone substitution, model-tag change, and authorized hook scope expansion are documented. The requested reader diff exists in scratch but is outside the staged patch. No dependency or `TODO` is introduced.

No tests were run or files modified. Git’s sandbox cache warnings were treated as tooling limits, not findings.
