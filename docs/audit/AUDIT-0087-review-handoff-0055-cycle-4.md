---
id: AUDIT-0087
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 70a425e80e6a683e915703b560a45f4e15c93f70963691a6678b66279bd79708"]
tier: 2
created: 2026-10-21T23:44:48-07:00
period: 2026-10-21
review_cycle: 4
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F13]
---

# Review of HANDOFF-0055, cycle 4

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `70a425e80e6a683e915703b560a45f4e15c93f70963691a6678b66279bd79708`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 1, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:340` | The live merge uses the tested design SHA. The regression excludes a later forbidden commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:353` | Successful merges invoke `run_sync`. The bare-remote regression verifies publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:262` | Waiting triggers receive the longer lock bound, heads refresh under the lock, and moved-main trials retry up to 3 times. | The contention and moved-main regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:256` | Open intents prevent the early return. Reconciliation closes an already-landed intent exactly once across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` explicitly accepts “within about two minutes.” The measured 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:247` | The previously named helpers have the required contract or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:156`; `kgme/merge.py:347` | Check timeouts reach the transient handler. Both timeout regressions assert 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook regression lands a design commit without another main commit. The report supplies the existing worktree’s wiring commands. | The implementation and activation instructions are present. |
| F13 | blocking | `kgme/merge.py:330`; `kgme/merge.py:340` | The quiet-point check and live merge are separate operations. A normal main commit between them causes `git merge` to use a different first parent from the trial. `kgme-merge.lock` excludes other merge runs, but ordinary commits do not acquire it. The untested combination can therefore land and be pushed. | Make landing conditional on the tested main SHA through atomic expected-head enforcement or equivalent synchronization. Add a regression advancing main after `read_checkout` returns and before the live merge; require a fresh trial or a refusal. |
| F14 | advisory | `tests/test_merge.py:432`; `tests/test_merge.py:444` | The configuration test calls main’s imported CLI and passed before the fix. Its branch TOML now also duplicates `[tracks.design]`. The actual-hook test has no divergent branch configuration, leaving that part of F12 without an effective regression. | Exercise the actual design hook with valid, divergent branch lanes and check settings, and verify that main’s settings govern. |
| F15 | cosmetic | `docs/readers/merging.md:23`; `kgme/merge.py:20` | These descriptions still attribute publication to the merge’s post-commit hook, contradicting the implemented F3 fix. | State that `run_merge` explicitly invokes `kgme sync` after success. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:340` | The live merge uses the tested design SHA. The regression excludes a later forbidden commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:152` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:353` | Successful merges invoke `run_sync`. The bare-remote regression verifies publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:262` | Waiting triggers receive the longer lock bound, heads refresh under the lock, and moved-main trials retry up to 3 times. | The contention and moved-main regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:256` | Open intents prevent the early return. Reconciliation closes an already-landed intent exactly once across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` explicitly accepts “within about two minutes.” The measured 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:247` | The previously named helpers have the required contract or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:70` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:156`; `kgme/merge.py:347` | Check timeouts reach the transient handler. Both timeout regressions assert 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook regression lands a design commit without another main commit. The report supplies the existing worktree’s wiring commands. | The implementation and activation instructions are present. |
| F13 | blocking | `kgme/merge.py:330`; `kgme/merge.py:340` | The quiet-point check and live merge are separate operations. A normal main commit between them causes `git merge` to use a different first parent from the trial. `kgme-merge.lock` excludes other merge runs, but ordinary commits do not acquire it. The untested combination can therefore land and be pushed. | Make landing conditional on the tested main SHA through atomic expected-head enforcement or equivalent synchronization. Add a regression advancing main after `read_checkout` returns and before the live merge; require a fresh trial or a refusal. |
| F14 | advisory | `tests/test_merge.py:432`; `tests/test_merge.py:444` | The configuration test calls main’s imported CLI and passed before the fix. Its branch TOML now also duplicates `[tracks.design]`. The actual-hook test has no divergent branch configuration, leaving that part of F12 without an effective regression. | Exercise the actual design hook with valid, divergent branch lanes and check settings, and verify that main’s settings govern. |
| F15 | cosmetic | `docs/readers/merging.md:23`; `kgme/merge.py:20` | These descriptions still attribute publication to the merge’s post-commit hook, contradicting the implemented F3 fix. | State that `run_merge` explicitly invokes `kgme sync` after success. |

## Verdict

BLOCK: 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`70a425e80e6a683e`**, verified before and after inspection. No files changed and no tests executed. The supplied gate log reports **454 passed, 34 deselected**, with **0 blocking lint findings**. Sandbox diagnostics were not findings.

All **6 acceptance scenarios** have tests or stated evidence. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree’s hook configuration remains an explicitly documented activation step.

Module contracts are present, subprocesses use argument lists, and no dependency or executable `TODO` or `shell=True` was introduced. File sizes exceed ADR-015’s approximate **300-line** target: `merge.py` has **354**, its tests **499**, and the existing CLI **395** lines. The temporary-clone substitution is explained by ledger isolation.
