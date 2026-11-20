---
id: AUDIT-0173
type: report
status: final
handoff: HANDOFF-0071
author: codex
source: inferred
sources: ["HANDOFF-0071", "staged diff sha256 55d7b9cb535406810822443222160b4b683e7b0b27d92c95cef9df9756e03e49"]
tier: 2
created: 2026-11-18T14:32:55-08:00
period: 2026-11-18
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6]
---

# Review of HANDOFF-0071, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `55d7b9cb535406810822443222160b4b683e7b0b27d92c95cef9df9756e03e49`. Verdict **BLOCK**: blocking 6, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/roles_run.py:173 | Outcomes set `parent=intent` but omit `ref=intent`. `ledger.open_intents()` closes intents through `ref`, so every completed agent run remains unmatched, including successful runs. | Set the outcome’s `ref`; test that successful and failed runs leave no open `agent:run` intent. |
| F2 | blocking | kgme/roles_run.py:126 | The launcher applies the session level but never applies the role’s profile or tool restrictions. Tools and tier appear only in prompt text. For example, a `work` role declaring only `Read` receives the ordinary work session’s broader permissions. This fails ADR-025 §3’s narrowing contract. | Enforce supported role/profile restrictions in the launch policy and refuse unsupported combinations. Test the effective permissions, not just lint acceptance. |
| F3 | blocking | kgme/roles_run.py:121 | The cheap branch returns before loading the role’s skill and atlas slice. `run_cheap_role()` passes only the model key and red command to the existing lane, which builds its generic prompt. Cheap roles therefore lack 2 required inputs from What §3. The mocked lane test cannot detect this. | Carry the role’s permitted context through the cheap lane while preserving its Tier 3 boundary; verify the actual constructed prompt and role attribution. |
| F4 | blocking | kgme/roles_run.py:149 | After writing an intent, session preparation and child execution have no exception handling that records an outcome. A missing `claude` executable or an interruption leaves the run without its required outcome, contrary to What §3 and ADR-015. | Close the intent with a classified failure on recoverable preparation, launch and interruption errors. Add failure-path tests. |
| F5 | blocking | kgme/roles.py:196 | Valid TOML with `id = []` reaches dictionary membership with an unhashable list and raises `TypeError`. The earlier identity finding is never returned. One malformed role therefore crashes the entire lint pass instead of producing blocking findings. | Validate scalar field types before using them; test malformed IDs and continued reporting for other roles. |
| F6 | blocking | kgme/roles_io.py:52 | Default lint lists indexed paths but reads working-tree contents, including rubric contents at line 134. A staged `tier_max = 1` followed by an unstaged repair can pass; a working-tree deletion can hide a staged role entirely. This does not validate the index required by the adoption ruling. | Read indexed blobs in default mode and working-tree contents under `--all`. Test divergent staged/unstaged roles and rubrics, including deletion. |
| F7 | cosmetic | tests/test_roles.py:39 | The new test module has 386 lines, exceeding ADR-015’s approximate 300-line target. Effect helpers such as `git`, `write` and `findings` also lack the required effect prefixes; several new public functions lack complete annotations. | Split the tests by responsibility, rename effect helpers, and complete annotations and purpose/input/output/effect documentation. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/roles_run.py:173 | Outcomes set `parent=intent` but omit `ref=intent`. `ledger.open_intents()` closes intents through `ref`, so every completed agent run remains unmatched, including successful runs. | Set the outcome’s `ref`; test that successful and failed runs leave no open `agent:run` intent. |
| F2 | blocking | kgme/roles_run.py:126 | The launcher applies the session level but never applies the role’s profile or tool restrictions. Tools and tier appear only in prompt text. For example, a `work` role declaring only `Read` receives the ordinary work session’s broader permissions. This fails ADR-025 §3’s narrowing contract. | Enforce supported role/profile restrictions in the launch policy and refuse unsupported combinations. Test the effective permissions, not just lint acceptance. |
| F3 | blocking | kgme/roles_run.py:121 | The cheap branch returns before loading the role’s skill and atlas slice. `run_cheap_role()` passes only the model key and red command to the existing lane, which builds its generic prompt. Cheap roles therefore lack 2 required inputs from What §3. The mocked lane test cannot detect this. | Carry the role’s permitted context through the cheap lane while preserving its Tier 3 boundary; verify the actual constructed prompt and role attribution. |
| F4 | blocking | kgme/roles_run.py:149 | After writing an intent, session preparation and child execution have no exception handling that records an outcome. A missing `claude` executable or an interruption leaves the run without its required outcome, contrary to What §3 and ADR-015. | Close the intent with a classified failure on recoverable preparation, launch and interruption errors. Add failure-path tests. |
| F5 | blocking | kgme/roles.py:196 | Valid TOML with `id = []` reaches dictionary membership with an unhashable list and raises `TypeError`. The earlier identity finding is never returned. One malformed role therefore crashes the entire lint pass instead of producing blocking findings. | Validate scalar field types before using them; test malformed IDs and continued reporting for other roles. |
| F6 | blocking | kgme/roles_io.py:52 | Default lint lists indexed paths but reads working-tree contents, including rubric contents at line 134. A staged `tier_max = 1` followed by an unstaged repair can pass; a working-tree deletion can hide a staged role entirely. This does not validate the index required by the adoption ruling. | Read indexed blobs in default mode and working-tree contents under `--all`. Test divergent staged/unstaged roles and rubrics, including deletion. |
| F7 | cosmetic | tests/test_roles.py:39 | The new test module has 386 lines, exceeding ADR-015’s approximate 300-line target. Effect helpers such as `git`, `write` and `findings` also lack the required effect prefixes; several new public functions lack complete annotations. | Split the tests by responsibility, rename effect helpers, and complete annotations and purpose/input/output/effect documentation. |

## Verdict

BLOCK with 6 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `55d7b9cb53540681`, verified before and after inspection.

All 5 acceptance items have tests or stated evidence in `AUDIT-0170`. Item 4’s live child stopped at authentication; that tooling limit is not a finding against the diff. The existing tests miss the runtime-policy, ledger-closure and failure-path defects above.

No pytest or write operations were performed. Reported test results were not independently rerun. The patch adds no dependencies, uses argument-list subprocess calls, and introduces neither `TODO` nor `shell=True`.
