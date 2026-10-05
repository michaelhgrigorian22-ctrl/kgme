---
id: AUDIT-0027
type: report
status: final
handoff: HANDOFF-0032
author: codex
source: inferred
sources: ["HANDOFF-0032", "staged diff sha256 7f806a93df3594bf81e35c460876508b8271f43c761f4eae6300e70271b58a44"]
tier: 2
created: 2026-09-23T18:21:53-07:00
period: 2026-09-23
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4]
---

# Review of HANDOFF-0032, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `7f806a93df3594bf81e35c460876508b8271f43c761f4eae6300e70271b58a44`. Verdict **BLOCK**: blocking 4, transient 0, cosmetic 0, advisory 4 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/policy/test_agents.py:269 | Refusal evidence is insufficient in 2 branches. Model-written `agent_message` text can establish an approval denial; otherwise, any relevant attempt without an observed effect becomes a refusal, even with zero errors or an unnamed layer. Reading the deliberately nonexistent Tier 1 tripwire could therefore pass on “file not found.” | Require tool or enforcement evidence tied to the requested operation. Keep model claims, unrelated failures, and missing results inconclusive. Add fast regression cases for each false-pass path. |
| F2 | blocking | tests/policy/test_agents.py:120 | All 10 cells use cleanup that unconditionally deletes `docs/canary-probe.md` if present. A pre-existing human file can be deleted even by an unrelated probe, and the write probe can overwrite it first. | Reject an occupied target before launching any cell, including symlinks, and remove only an artifact owned by this run. Test preservation of a pre-existing file. |
| F3 | blocking | tests/policy/test_agents.py:169 | Both launchers ignore process return codes and terminal failure events. A failed invocation producing no attempts becomes `inconclusive: not attempted`, and `finish()` accepts it. This records a tooling failure as a completed advisory measurement. | Validate process and stream completion. Record invocation failures separately with the appropriate ADR-016 class and fail the run without attributing failure to enforcement. Add synthetic failure-stream tests. |
| F4 | blocking | kgme/canary.py:114 | The cell’s intent is written only after the worker returns, through `finish()`. An interruption after a consequential probe leaves no cell intent, contrary to ADR-013 §4’s write-ahead contract; Codex has no hook pair to cover that gap. | Write the intent before launching the worker and close that same intent afterward. Preserve an unmatched intent on interruption and record handled failures against it. |
| F5 | advisory | kgme/canary.py:62 | An absent layer combined with a declined operation returns `inconclusive`, overriding rule 5’s required `advisory: layer missing`. Neither result passes, but the network verdict becomes dependent on model behavior. | Give layer absence precedence over a voluntary decline, retain “not attempted” as the observation, and test the combined case. |
| F6 | advisory | tests/policy/test_agents.py:149; kgme/canary.py:103 | ADR-015 separation is incomplete: the 335-line agent module combines execution, parsing, observation, and cleanup; `keep()` and `record()` perform writes without effect prefixes. Several public helpers lack complete type annotations. | Separate pure interpretation from effects, use `read_*`, `write_*`, or `run_*` names, and complete annotations and effect documentation. |
| F7 | advisory | kgme/hooks/common.py:46 | The new `KGME_TEST_STREAMS` switch is an ambient configuration exception to ADR-015. Inheritance alone redirects ordinary hook events into disposable test streams; the branch does not identify a canary session. | Prefer explicit test invocation configuration, or document an adopted exception and constrain routing to identified canary sessions. |
| F8 | advisory | tests/policy/test_agents.py:34 | The 2 parametrized agent tests carry only the `agents` marker. Their 10 cells lack the test-level ADR-016 class required separately from ledger outcome classes. | Add the applicable failure-class markers while preserving per-cell outcome classification. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/policy/test_agents.py:269 | Refusal evidence is insufficient in 2 branches. Model-written `agent_message` text can establish an approval denial; otherwise, any relevant attempt without an observed effect becomes a refusal, even with zero errors or an unnamed layer. Reading the deliberately nonexistent Tier 1 tripwire could therefore pass on “file not found.” | Require tool or enforcement evidence tied to the requested operation. Keep model claims, unrelated failures, and missing results inconclusive. Add fast regression cases for each false-pass path. |
| F2 | blocking | tests/policy/test_agents.py:120 | All 10 cells use cleanup that unconditionally deletes `docs/canary-probe.md` if present. A pre-existing human file can be deleted even by an unrelated probe, and the write probe can overwrite it first. | Reject an occupied target before launching any cell, including symlinks, and remove only an artifact owned by this run. Test preservation of a pre-existing file. |
| F3 | blocking | tests/policy/test_agents.py:169 | Both launchers ignore process return codes and terminal failure events. A failed invocation producing no attempts becomes `inconclusive: not attempted`, and `finish()` accepts it. This records a tooling failure as a completed advisory measurement. | Validate process and stream completion. Record invocation failures separately with the appropriate ADR-016 class and fail the run without attributing failure to enforcement. Add synthetic failure-stream tests. |
| F4 | blocking | kgme/canary.py:114 | The cell’s intent is written only after the worker returns, through `finish()`. An interruption after a consequential probe leaves no cell intent, contrary to ADR-013 §4’s write-ahead contract; Codex has no hook pair to cover that gap. | Write the intent before launching the worker and close that same intent afterward. Preserve an unmatched intent on interruption and record handled failures against it. |
| F5 | advisory | kgme/canary.py:62 | An absent layer combined with a declined operation returns `inconclusive`, overriding rule 5’s required `advisory: layer missing`. Neither result passes, but the network verdict becomes dependent on model behavior. | Give layer absence precedence over a voluntary decline, retain “not attempted” as the observation, and test the combined case. |
| F6 | advisory | tests/policy/test_agents.py:149; kgme/canary.py:103 | ADR-015 separation is incomplete: the 335-line agent module combines execution, parsing, observation, and cleanup; `keep()` and `record()` perform writes without effect prefixes. Several public helpers lack complete type annotations. | Separate pure interpretation from effects, use `read_*`, `write_*`, or `run_*` names, and complete annotations and effect documentation. |
| F7 | advisory | kgme/hooks/common.py:46 | The new `KGME_TEST_STREAMS` switch is an ambient configuration exception to ADR-015. Inheritance alone redirects ordinary hook events into disposable test streams; the branch does not identify a canary session. | Prefer explicit test invocation configuration, or document an adopted exception and constrain routing to identified canary sessions. |
| F8 | advisory | tests/policy/test_agents.py:34 | The 2 parametrized agent tests carry only the `agents` marker. Their 10 cells lack the test-level ADR-016 class required separately from ledger outcome classes. | Add the applicable failure-class markers while preserving per-cell outcome classification. |

## Verdict

BLOCK with 4 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `7f806a93df3594bf`.

The retained streams support the reported Claude write failure and `rm -rf` denial. The permission failure itself is not a finding against this diff. HANDOFF-0032 remains open; its reported matrix contains 1 pass, 1 fail, 4 inconclusive cells, and 4 advisories.

Timing and clean-tree acceptance have stated builder evidence. I did not rerun tests or modify files. No new dependencies, `TODO`, or `shell=True` appeared in the patch. The hook-test split and same-line tilde regression are present.
