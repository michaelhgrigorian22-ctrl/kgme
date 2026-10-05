---
id: AUDIT-0028
type: report
status: final
handoff: HANDOFF-0032
author: codex
source: inferred
sources: ["HANDOFF-0032", "staged diff sha256 f81aade8cfb294d034845591a57d45180a5e7feff8866dcd986da3cf5cc4448d"]
tier: 2
created: 2026-09-28T09:33:29-07:00
period: 2026-09-28
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F3, F9]
---

# Review of HANDOFF-0032, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `f81aade8cfb294d034845591a57d45180a5e7feff8866dcd986da3cf5cc4448d`. Verdict **BLOCK**: blocking 3, transient 0, cosmetic 0, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/canary_stream.py:157](/Users/michaelgrigorian/Projects/Automate/kgme/canary_stream.py:157) | Refusal attribution remains incomplete. `hook_refusals()` counts every refusal in the session. Consequently, an aimed attempt returning ENOENT or no result becomes a pass when 1 unrelated call was refused. Target substring matching also does not establish the requested operation. | Correlate refusal evidence with the attempted operation, target, and tool-call ID. Add regressions combining unrelated refusals with missing-file and missing-result attempts. |
| F2 | blocking, resolved | [tests/policy/test_agents.py:217](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:217) | An occupied target, including a symlink, prevents launch. Cleanup preserves pre-existing files, symlinks, and different content; a preservation regression is present. | No further change required for the original finding. |
| F3 | blocking | [kgme/canary_stream.py:93](/Users/michaelgrigorian/Projects/Automate/kgme/canary_stream.py:93); [tests/policy/test_agents.py:219](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:219) | Two failure paths remain. A Claude terminal `result` with `is_error: true` is marked complete and accepted if the process exits 0. A missing executable raises `OSError` outside the timeout handler, leaving no classified outcome. The regression does not exercise these paths through `measure()`. | Validate terminal success separately from terminal presence. Record ordinary launch failures against the existing intent. Add orchestration regressions for both paths. |
| F4 | blocking, resolved | [tests/policy/test_agents.py:210](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:210) | The intent now precedes `launch()`. Normal and handled transient outcomes close that same intent; interruption leaves it unmatched. | No further change required for the original ordering defect. |
| F5 | advisory, resolved | [kgme/canary.py:81](/Users/michaelgrigorian/Projects/Automate/kgme/canary.py:81) | Layer absence now outranks a voluntary decline, while the observation retains “not attempted.” The combined case has a regression. | No further change required. |
| F6 | advisory | [kgme/canary.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/canary.py:197); [tests/policy/test_canary.py:24](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_canary.py:24) | The parser split and 294-line agent module address part of ADR-015. Effects remain under unprefixed names, including `occupied`, `remove_artifact`, `effect_seen`, `hook_refusals`, and `measure`. Public helpers still have incomplete annotations. | Finish effect naming and separation, complete public annotations, and document each effect’s inputs and outputs. |
| F7 | advisory, resolved | [kgme/hooks/common.py:51](/Users/michaelgrigorian/Projects/Automate/kgme/hooks/common.py:51) | The documented exception now requires the `canary:<ULID>` form; ordinary stray values no longer redirect hook events. | No further change required under the documented exception. |
| F8 | advisory, resolved | [tests/policy/test_agents.py:33](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:33) | Module-level `agents` and `blocking` markers now cover all 10 cells. | No further change required. |
| F9 | blocking | [tests/policy/test_agents.py:231](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:231); [docs/handoff/2026-09-14-canary-tests.md:8](/Users/michaelgrigorian/Projects/Automate/docs/handoff/2026-09-14-canary-tests.md:8) | The completion gate accepts inconclusive cells because it rejects only `fail`. The latest run has 3 inconclusive cells with present layers, yet the handoff is marked done. AUDIT-0026 explicitly acknowledges that the refusal acceptance criterion remains unmet. | Require demonstrated refusal for present-layer acceptance. Keep completion pending until evidence satisfies that criterion or an explicit revised acceptance decision covers these 3 cells. Preserve the authorized layer-missing advisories. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/canary_stream.py:157](/Users/michaelgrigorian/Projects/Automate/kgme/canary_stream.py:157) | Refusal attribution remains incomplete. `hook_refusals()` counts every refusal in the session. Consequently, an aimed attempt returning ENOENT or no result becomes a pass when 1 unrelated call was refused. Target substring matching also does not establish the requested operation. | Correlate refusal evidence with the attempted operation, target, and tool-call ID. Add regressions combining unrelated refusals with missing-file and missing-result attempts. |
| F2 | blocking, resolved | [tests/policy/test_agents.py:217](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:217) | An occupied target, including a symlink, prevents launch. Cleanup preserves pre-existing files, symlinks, and different content; a preservation regression is present. | No further change required for the original finding. |
| F3 | blocking | [kgme/canary_stream.py:93](/Users/michaelgrigorian/Projects/Automate/kgme/canary_stream.py:93); [tests/policy/test_agents.py:219](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:219) | Two failure paths remain. A Claude terminal `result` with `is_error: true` is marked complete and accepted if the process exits 0. A missing executable raises `OSError` outside the timeout handler, leaving no classified outcome. The regression does not exercise these paths through `measure()`. | Validate terminal success separately from terminal presence. Record ordinary launch failures against the existing intent. Add orchestration regressions for both paths. |
| F4 | blocking, resolved | [tests/policy/test_agents.py:210](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:210) | The intent now precedes `launch()`. Normal and handled transient outcomes close that same intent; interruption leaves it unmatched. | No further change required for the original ordering defect. |
| F5 | advisory, resolved | [kgme/canary.py:81](/Users/michaelgrigorian/Projects/Automate/kgme/canary.py:81) | Layer absence now outranks a voluntary decline, while the observation retains “not attempted.” The combined case has a regression. | No further change required. |
| F6 | advisory | [kgme/canary.py:197](/Users/michaelgrigorian/Projects/Automate/kgme/canary.py:197); [tests/policy/test_canary.py:24](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_canary.py:24) | The parser split and 294-line agent module address part of ADR-015. Effects remain under unprefixed names, including `occupied`, `remove_artifact`, `effect_seen`, `hook_refusals`, and `measure`. Public helpers still have incomplete annotations. | Finish effect naming and separation, complete public annotations, and document each effect’s inputs and outputs. |
| F7 | advisory, resolved | [kgme/hooks/common.py:51](/Users/michaelgrigorian/Projects/Automate/kgme/hooks/common.py:51) | The documented exception now requires the `canary:<ULID>` form; ordinary stray values no longer redirect hook events. | No further change required under the documented exception. |
| F8 | advisory, resolved | [tests/policy/test_agents.py:33](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:33) | Module-level `agents` and `blocking` markers now cover all 10 cells. | No further change required. |
| F9 | blocking | [tests/policy/test_agents.py:231](/Users/michaelgrigorian/Projects/Automate/tests/policy/test_agents.py:231); [docs/handoff/2026-09-14-canary-tests.md:8](/Users/michaelgrigorian/Projects/Automate/docs/handoff/2026-09-14-canary-tests.md:8) | The completion gate accepts inconclusive cells because it rejects only `fail`. The latest run has 3 inconclusive cells with present layers, yet the handoff is marked done. AUDIT-0026 explicitly acknowledges that the refusal acceptance criterion remains unmet. | Require demonstrated refusal for present-layer acceptance. Keep completion pending until evidence satisfies that criterion or an explicit revised acceptance decision covers these 3 cells. Preserve the authorized layer-missing advisories. |

## Verdict

BLOCK with 3 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `f81aade8cfb294d0`.

The retained streams and ledger support 3 refusals, 3 inconclusive cells, and 4 layer-missing advisories. All 10 cells have paired intents and outcomes carrying the settings digest. Timing and clean-tree acceptance have stated builder evidence.

The permission rules, guard rule 4, settings-digest recording, and arbiter update are present. Changed Python files stay below 300 lines. No new dependencies, executable `TODO`, or `shell=True` were introduced; subprocesses use argument lists.

No pytest or agent runs were performed, and no files were changed. Sandbox tooling limits were not counted against the diff.
