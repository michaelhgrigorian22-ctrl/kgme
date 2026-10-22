---
id: AUDIT-0089
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 380028cbe73393b318b45a4791f1d022992de9a2c92076ba13d8e3e73ce424a6"]
tier: 2
created: 2026-10-22T00:09:26-07:00
period: 2026-10-22
review_cycle: 6
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F16, F18]
---

# Review of HANDOFF-0055, cycle 6

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `380028cbe73393b318b45a4791f1d022992de9a2c92076ba13d8e3e73ce424a6`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:370` | Landing uses the trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:159` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:386` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:292` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:286`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:165`; `kgme/merge.py:378` | Check timeouts reach the transient handler. Both timeout regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook test and activation instructions remain present. | The implementation remains present. |
| F13 | blocking, resolved | `kgme/merge.py:223`; `tests/test_merge.py:531` | A divergent main commit prevents the fast-forward and triggers a fresh trial. The existing regression requires 2 trials, correct parents, and a clean checkout. | The regression remains covered. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The staged reader still attributes publication to the post-commit hook. Its correction remains a separate scratch diff. | Apply `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:223`; `kgme/merge.py:375`; `tests/test_merge.py:601` | Interrupted-landing recovery remains unproved and incomplete. Git installs the checkout/index before updating `HEAD`; failure acquiring `refs/heads/main.lock` can therefore leave main unchanged with the trial changes staged. This handler records `transient`, deletes the trial ref, and subsequent runs wait on the staged difference without repairing it. The new test raises before invoking Git, so it exercises no partial update. This follows from the [Git checkout implementation](https://raw.githubusercontent.com/git/git/v2.50.1/merge.c) and [merge completion sequence](https://raw.githubusercontent.com/git/git/v2.50.1/builtin/merge.c). | Retain sufficient recovery state and reconcile interrupted landings while preserving user changes. Inject an actual failure after checkout changes begin, such as a held main ref lock, and verify consistent ref/index/tree state and recovery on restart. |
| F17 | blocking, resolved | `kgme/merge.py:223`; `tests/test_merge.py:559` | Git refuses the unfinished merge. The new regression starts an empty-tree `--no-commit` merge after the quiet check and requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The requested regression is present. |
| F18 | blocking | `kgme/merge.py:220`; `kgme/merge.py:223`; `kgme/merge.py:361` | The replacement landing no longer rechecks the checkout’s branch. If another process switches from main to a branch at the same commit after `read_checkout`, the parent check still passes and `git merge --ff-only` advances that other branch. The run reports success although main never received the design commit, then invokes sync on the switched checkout. Git merges into the [current branch](https://git-scm.com/docs/git-merge/2.50.0). | Bind landing to main under synchronization with checkout changes. Add a regression switching branches after the quiet read; require refusal with neither branch modified by landing. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:370` | Landing uses the trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:159` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:386` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:292` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:286`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:165`; `kgme/merge.py:378` | Check timeouts reach the transient handler. Both timeout regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook test and activation instructions remain present. | The implementation remains present. |
| F13 | blocking, resolved | `kgme/merge.py:223`; `tests/test_merge.py:531` | A divergent main commit prevents the fast-forward and triggers a fresh trial. The existing regression requires 2 trials, correct parents, and a clean checkout. | The regression remains covered. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The staged reader still attributes publication to the post-commit hook. Its correction remains a separate scratch diff. | Apply `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:223`; `kgme/merge.py:375`; `tests/test_merge.py:601` | Interrupted-landing recovery remains unproved and incomplete. Git installs the checkout/index before updating `HEAD`; failure acquiring `refs/heads/main.lock` can therefore leave main unchanged with the trial changes staged. This handler records `transient`, deletes the trial ref, and subsequent runs wait on the staged difference without repairing it. The new test raises before invoking Git, so it exercises no partial update. This follows from the [Git checkout implementation](https://raw.githubusercontent.com/git/git/v2.50.1/merge.c) and [merge completion sequence](https://raw.githubusercontent.com/git/git/v2.50.1/builtin/merge.c). | Retain sufficient recovery state and reconcile interrupted landings while preserving user changes. Inject an actual failure after checkout changes begin, such as a held main ref lock, and verify consistent ref/index/tree state and recovery on restart. |
| F17 | blocking, resolved | `kgme/merge.py:223`; `tests/test_merge.py:559` | Git refuses the unfinished merge. The new regression starts an empty-tree `--no-commit` merge after the quiet check and requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The requested regression is present. |
| F18 | blocking | `kgme/merge.py:220`; `kgme/merge.py:223`; `kgme/merge.py:361` | The replacement landing no longer rechecks the checkout’s branch. If another process switches from main to a branch at the same commit after `read_checkout`, the parent check still passes and `git merge --ff-only` advances that other branch. The run reports success although main never received the design commit, then invokes sync on the switched checkout. Git merges into the [current branch](https://git-scm.com/docs/git-merge/2.50.0). | Bind landing to main under synchronization with checkout changes. Add a regression switching branches after the quiet read; require refusal with neither branch modified by landing. |

## Verdict

BLOCK: 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`380028cbe73393b3`**, verified before and after inspection. No files were changed and no tests were executed. F16 and F18 follow from static inspection. Sandbox diagnostics were not findings against the diff.

All **6 acceptance scenarios** have tests or stated evidence. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree still requires the documented hook activation. The supplied gate log reports **457 passed, 34 deselected**, and **0 blocking lint findings**.

Module contracts and named production effects are present; subprocesses use argument lists. No dependencies, executable `TODO`, or `shell=True` were introduced. ADR-015’s approximate **300-line** target remains exceeded: `merge.py` has **387** lines, its tests **615**, and the existing CLI **395**.

F16 remains blocking for a second consecutive cycle; the review-loop protocol calls for an arbiter ruling.
