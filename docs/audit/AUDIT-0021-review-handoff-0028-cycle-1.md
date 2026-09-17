---
id: AUDIT-0021
type: report
status: final
handoff: HANDOFF-0028
author: codex
source: inferred
sources: ["HANDOFF-0028", "staged diff sha256 37839bf2f3dca483d7872930162cc5d8925fe86aff1c0cc8334b94e7c7100213"]
tier: 2
created: 2026-09-17T12:59:26.126-07:00
period: 2026-09-17
review_cycle: 1
reviewer: gpt-6-astra
verdict: PASS
open_blocking: []
---

# Review of HANDOFF-0028, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `37839bf2f3dca483d7872930162cc5d8925fe86aff1c0cc8334b94e7c7100213`. Verdict **PASS**: blocking 0, transient 0, cosmetic 0, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | tests/test_hooks.py:415 | The regression exercises `resolve_all` through `decide`, but never exercises `script_candidates`. Reverting the second call-site fix would leave this test passing while restoring the crash on allowed Bash calls. | Assert that `script_candidates` accepts the same tilde-containing command, or add a hook-level exit-0 assertion. |

## Verdict

PASS

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | tests/test_hooks.py:415 | The regression exercises `resolve_all` through `decide`, but never exercises `script_candidates`. Reverting the second call-site fix would leave this test passing while restoring the crash on allowed Bash calls. | Assert that `script_candidates` accepts the same tilde-containing command, or add a hook-level exit-0 assertion. |

## Verdict

PASS

## Notes

Reviewed SHA-256 prefix **`37839bf2f3dca483`**. Static review only; no pytest or hooks executed, and no files changed.

The 2 modified call sites retain absolute-path resolution and symlink following. Unknown-user fragments remain subject to the existing blocklist and file-tool boundaries; successful home expansion is unchanged. No fence regression was identified under ADR-013 §2.

Every original acceptance item has tests or stated live evidence: [AUDIT-0014](/Users/michaelgrigorian/Projects/Automate/docs/audit/2026-09-15-permissions-and-hooks.md:45) records all 7 checks, supported by the existing exit-code, transaction-pair, payload-hash, refusal, and startup-failure tests. The builder’s pre-swap compilation and exercise remain stated evidence, not independently rerun.

Under ADR-015, the guard is 182 lines; the test file grows from an already oversized 408 to 421 lines. The patch adds no dependencies, subprocesses, or TODOs. Existing effect boundaries and module docstrings remain intact.
