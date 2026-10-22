---
id: AUDIT-0086
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 2ffd20e94b7c0befceb2c9976c467272364c451bba3d468649fc7b6528dadfaa"]
tier: 2
created: 2026-10-21T23:29:37-07:00
period: 2026-10-21
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F12]
---

# Review of HANDOFF-0055, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `2ffd20e94b7c0befceb2c9976c467272364c451bba3d468649fc7b6528dadfaa`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:328` | The live merge uses the tested SHA. The regression excludes a later forbidden commit. | Implemented. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. Both regressions remain covered. | Implemented. |
| F3 | blocking, resolved | `kgme/merge.py:341` | Successful merges invoke `run_sync`; the bare-remote regression verifies publication without another commit. | Implemented. |
| F4 | blocking, resolved | `kgme/merge.py:255` | Waiting triggers receive the longer lock bound, heads refresh under the lock, and moved-main trials retry up to 3 times. | Implemented, with contention and moved-main tests. |
| F5 | blocking, resolved | `kgme/merge.py:249`; `tests/test_merge.py:397` | Open intents prevent the early no-work return. Reconciliation runs under the lock; the landed-commit regression verifies exactly 1 closing outcome across 2 subsequent runs. | Implemented. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | Implemented and covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Selection compares parsed instants, then event IDs. Both ordering regressions remain covered. | Implemented. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ledger ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` records Michou’s amendment to “within about two minutes.” The measured 61 seconds complies; the report acknowledges missing the original bound. | Resolved by the verified ruling and corrected report. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_approve.py:124`; `tests/test_merge.py:247` | `run_git` now has its contract, and the 3 previously named helpers have effect prefixes. | Implemented. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests retain explicit class markers. | Implemented. |
| F11 | blocking, resolved | `kgme/merge.py:162`; `kgme/merge.py:335` | Check timeouts now reach the transient handler. The 2 timeout regressions verify exactly 1 intent and 1 outcome. | Implemented. |
| F12 | blocking | `docs/audit/2026-10-21-design-lands.md:112`; `kgme/cli.py:325` | The design trigger selects the triggering worktree’s code and configuration. The existing design checkout lacks `kgme/merge.py`, so the drafted hook skips it; the prescribed merge into `main` does not update that checkout. When the module exists, `run_track` reads that worktree’s `kgme.toml`, allowing branch-local lane/check changes to govern a merge into `main`. The worktree test directly calls the main implementation with main settings, missing both cases. | Resolve the main checkout before selecting the runtime and configuration, and supply hook wiring for the existing design worktree. Test the actual design hook without a subsequent main commit, including divergent worktree settings. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:328` | The live merge uses the tested SHA. The regression excludes a later forbidden commit. | Implemented. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. Both regressions remain covered. | Implemented. |
| F3 | blocking, resolved | `kgme/merge.py:341` | Successful merges invoke `run_sync`; the bare-remote regression verifies publication without another commit. | Implemented. |
| F4 | blocking, resolved | `kgme/merge.py:255` | Waiting triggers receive the longer lock bound, heads refresh under the lock, and moved-main trials retry up to 3 times. | Implemented, with contention and moved-main tests. |
| F5 | blocking, resolved | `kgme/merge.py:249`; `tests/test_merge.py:397` | Open intents prevent the early no-work return. Reconciliation runs under the lock; the landed-commit regression verifies exactly 1 closing outcome across 2 subsequent runs. | Implemented. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | Implemented and covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Selection compares parsed instants, then event IDs. Both ordering regressions remain covered. | Implemented. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ledger ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` records Michou’s amendment to “within about two minutes.” The measured 61 seconds complies; the report acknowledges missing the original bound. | Resolved by the verified ruling and corrected report. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_approve.py:124`; `tests/test_merge.py:247` | `run_git` now has its contract, and the 3 previously named helpers have effect prefixes. | Implemented. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests retain explicit class markers. | Implemented. |
| F11 | blocking, resolved | `kgme/merge.py:162`; `kgme/merge.py:335` | Check timeouts now reach the transient handler. The 2 timeout regressions verify exactly 1 intent and 1 outcome. | Implemented. |
| F12 | blocking | `docs/audit/2026-10-21-design-lands.md:112`; `kgme/cli.py:325` | The design trigger selects the triggering worktree’s code and configuration. The existing design checkout lacks `kgme/merge.py`, so the drafted hook skips it; the prescribed merge into `main` does not update that checkout. When the module exists, `run_track` reads that worktree’s `kgme.toml`, allowing branch-local lane/check changes to govern a merge into `main`. The worktree test directly calls the main implementation with main settings, missing both cases. | Resolve the main checkout before selecting the runtime and configuration, and supply hook wiring for the existing design worktree. Test the actual design hook without a subsequent main commit, including divergent worktree settings. |

## Verdict

BLOCK: 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`2ffd20e94b7c0bef`**, verified before and after inspection. No files changed and no tests executed. The supplied gate log reports **451 passed, 34 deselected**, with **0 blocking lint findings**.

All **6 explicit acceptance scenarios** have tests or stated evidence under the amended timing bound. Human-terminal approval uses a marker-free fixture; no live human approval is claimed. F12 concerns the additional design-side trigger required by What §3.

Module contracts are present, subprocesses use argument lists, and no dependencies, `TODO`, or `shell=True` were introduced. File lengths exceed the approximate 300-line convention: `merge.py` has **342**, its tests **415**, and the already oversized CLI **388**. Human-applied hook, configuration, deny-rule, and reader drafts remain in scratch.
