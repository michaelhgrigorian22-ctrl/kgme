---
id: AUDIT-0178
type: report
status: final
handoff: HANDOFF-0073
author: codex
source: inferred
sources: ["HANDOFF-0073", "staged diff sha256 d0905d2557119e0107a8837452da3f4670043f7dcc5c2a6beb1ba1fffc66851d"]
tier: 2
created: 2026-11-23T16:54:46-08:00
period: 2026-11-23
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F10]
---

# Review of HANDOFF-0073, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `d0905d2557119e0107a8837452da3f4670043f7dcc5c2a6beb1ba1fffc66851d`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/hermes_fence_policy.py:153 | Unknown terminal directories receive strict checks, and relative write targets are refused. Regression coverage remains. | No further fix. |
| F2 | blocking, resolved | kgme/hermes_fence_parse.py:161 | Quote removal precedes directory-change detection. Tests include the three-stage `c''d` case from outside and unlexable commands. | No further fix under the ruled threat model. |
| F3 | blocking, resolved | kgme/hermes_fence_parse.py:226 | The parser checks all recognised patch operations and both Move endpoints; unknown operations refuse the patch. | No further fix. |
| F4 | blocking, resolved | kgme/hermes_fence_policy.py:179 | Direct dispatch selects the brain’s resolved `kgme`; the launcher requires the exact project form. The original executable-name finding remains closed. | No further fix for the original finding. F10 addresses inherited executable lookup separately. |
| F5 | blocking, resolved | docs/audit/AUDIT-0176-hermes-conductor.md:56 | The report now records all 3 installed-dispatcher probes passing, including refusal with the hook renamed away. The tested patch and reviewed patch differ only in this report. | No further pre-landing evidence fix. Complete the stated post-landing acceptance. |
| F6 | cosmetic, resolved | kgme/hermes_fence.py:126 | Parsing, policy and effects are separated into 273-, 322- and 182-line modules. The effectful entry point is `run_decide`; tests are split. | No further fix. |
| F7 | blocking, resolved | kgme/hermes_fence_policy.py:214 | Terminal views are removed. Git permits exactly 2 arguments, restricted to the 4 bare reads. The `rg --hostname-bin` regression is covered. | No further fix for the option surface. |
| F8 | blocking, resolved | kgme/hermes_fence.py:47 | Canonicalisation checks on-disk spelling and filesystem identity, including existing ancestors of new files. Case-alias regressions cover writes, patches and terminal containment. | No further fix. |
| F9 | blocking, resolved | kgme/hermes_fence.py:77 | Delete and both Move endpoints preserve the final entry while resolving parents. Protected-symlink regressions implement the ruling. | No further fix. |
| F10 | blocking | kgme/hermes_fence.py:111 | Executable trust still depends on inherited `PATH`: `shutil.which` selects `git` and `uv` from it, and `clean_env` forwards it to dispatched KGME, whose child launch uses bare `claude`. Starting Hermes from another environment can therefore select different executables during ordinary allowed calls. The live probe confirms inherited PATH survives. This affects inside calls without requiring an adversarial outside shell. | Pin trusted executable locations and construct a fixed child PATH independently of Hermes’s inherited PATH. Add regression coverage for an alternate environment and relative PATH entries. |
| F11 | cosmetic | docs/audit/AUDIT-0176-hermes-conductor.md:17 | The summary still says the live probes have not run; lines 94 and 140 also leave them outstanding, contradicting the 3 recorded PASS results. | Update those statements to distinguish completed pre-landing probes from pending post-landing acceptance. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/hermes_fence_policy.py:153 | Unknown terminal directories receive strict checks, and relative write targets are refused. Regression coverage remains. | No further fix. |
| F2 | blocking, resolved | kgme/hermes_fence_parse.py:161 | Quote removal precedes directory-change detection. Tests include the three-stage `c''d` case from outside and unlexable commands. | No further fix under the ruled threat model. |
| F3 | blocking, resolved | kgme/hermes_fence_parse.py:226 | The parser checks all recognised patch operations and both Move endpoints; unknown operations refuse the patch. | No further fix. |
| F4 | blocking, resolved | kgme/hermes_fence_policy.py:179 | Direct dispatch selects the brain’s resolved `kgme`; the launcher requires the exact project form. The original executable-name finding remains closed. | No further fix for the original finding. F10 addresses inherited executable lookup separately. |
| F5 | blocking, resolved | docs/audit/AUDIT-0176-hermes-conductor.md:56 | The report now records all 3 installed-dispatcher probes passing, including refusal with the hook renamed away. The tested patch and reviewed patch differ only in this report. | No further pre-landing evidence fix. Complete the stated post-landing acceptance. |
| F6 | cosmetic, resolved | kgme/hermes_fence.py:126 | Parsing, policy and effects are separated into 273-, 322- and 182-line modules. The effectful entry point is `run_decide`; tests are split. | No further fix. |
| F7 | blocking, resolved | kgme/hermes_fence_policy.py:214 | Terminal views are removed. Git permits exactly 2 arguments, restricted to the 4 bare reads. The `rg --hostname-bin` regression is covered. | No further fix for the option surface. |
| F8 | blocking, resolved | kgme/hermes_fence.py:47 | Canonicalisation checks on-disk spelling and filesystem identity, including existing ancestors of new files. Case-alias regressions cover writes, patches and terminal containment. | No further fix. |
| F9 | blocking, resolved | kgme/hermes_fence.py:77 | Delete and both Move endpoints preserve the final entry while resolving parents. Protected-symlink regressions implement the ruling. | No further fix. |
| F10 | blocking | kgme/hermes_fence.py:111 | Executable trust still depends on inherited `PATH`: `shutil.which` selects `git` and `uv` from it, and `clean_env` forwards it to dispatched KGME, whose child launch uses bare `claude`. Starting Hermes from another environment can therefore select different executables during ordinary allowed calls. The live probe confirms inherited PATH survives. This affects inside calls without requiring an adversarial outside shell. | Pin trusted executable locations and construct a fixed child PATH independently of Hermes’s inherited PATH. Add regression coverage for an alternate environment and relative PATH entries. |
| F11 | cosmetic | docs/audit/AUDIT-0176-hermes-conductor.md:17 | The summary still says the live probes have not run; lines 94 and 140 also leave them outstanding, contradicting the 3 recorded PASS results. | Update those statements to distinguish completed pre-landing probes from pending post-landing acceptance. |

## Verdict

BLOCK with 1 open blocking finding.

## Notes

Reviewed sha256 prefix **`d0905d2557119e01`**. The live probes identify **`6c80a1b2dc54e267`**; comparison confirms only the audit report changed between those patches.

All 5 original acceptance items have test coverage: protected writes, git refusal, attribution through a stubbed agent launch, and role linting. The additional proposal-write case has coverage; hook-renamed refusal now has stated live evidence. Probe (c) verifies dispatch authorisation and rewriting, not execution of a real agent run.

No tests were run and no files were changed. The reported 125 passes were not independently reproduced. No new dependency, `TODO`, or `shell=True` was found in the added implementation. The missing `docs/DEBT.md` and sandbox limitations are not findings against this diff.
