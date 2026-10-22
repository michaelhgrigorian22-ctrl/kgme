---
id: AUDIT-0091
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 5a46c9ef7d47752b6882b336ddd7bbb5ff1dc7759f397766dcf3c4189834a1e4"]
tier: 2
created: 2026-10-22T00:52:48-07:00
period: 2026-10-22
review_cycle: 8
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F16]
---

# Review of HANDOFF-0055, cycle 8

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `5a46c9ef7d47752b6882b336ddd7bbb5ff1dc7759f397766dcf3c4189834a1e4`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:439` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:163` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:467` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:350` | Waiting triggers retain the longer lock bound; heads refresh under lock; moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:344`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:459` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:255`; `tests/test_merge.py:531` | A moved main triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The staged reader now attributes publication to `kgme sync`, matching the F3 implementation. | The correction is included in this patch. |
| F16 | blocking | `kgme/merge.py:267`; `kgme/merge.py:459`; `kgme/merge.py:463`; `tests/test_merge.py:690` | The new regression covers a partial landing only when subsequent verification succeeds. After that same partial landing, a `TimeoutExpired` or `OSError` from `read_landed_state` escapes to the outer handler, which records 1 transient outcome and deletes `TRIAL_REF`. No kept ref has been created, so unverifiable partial state still loses its recovery reference and latch. | Apply Cowork’s standing fallback: after invoking the main-checkout merge, every failure becomes 1 blocking outcome with a kept ref and latch. Preserve recovery state before that invocation. Add a regression combining an actual partial landing with a failed post-check; require the blocking outcome and intact recovery ref. |
| F17 | blocking, resolved | `kgme/merge.py:258`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:267`; `tests/test_merge.py:673` | Option A detects the switched branch, records a named blocking outcome, and returns before sync. | The regression requires unchanged main and no false `ok`. |
| F19 | blocking, resolved | `kgme/merge.py:384`; `kgme/merge.py:444`; `tests/test_merge.py:719` | Kept recovery refs are separate from disposable trial storage. The regression preserves the original ref through 1 dry run and 1 new design head, then verifies repair, cleanup, and resumed landing. | The requested protection and regression are present. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:439` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:163` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:467` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:350` | Waiting triggers retain the longer lock bound; heads refresh under lock; moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:344`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:459` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:255`; `tests/test_merge.py:531` | A moved main triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The staged reader now attributes publication to `kgme sync`, matching the F3 implementation. | The correction is included in this patch. |
| F16 | blocking | `kgme/merge.py:267`; `kgme/merge.py:459`; `kgme/merge.py:463`; `tests/test_merge.py:690` | The new regression covers a partial landing only when subsequent verification succeeds. After that same partial landing, a `TimeoutExpired` or `OSError` from `read_landed_state` escapes to the outer handler, which records 1 transient outcome and deletes `TRIAL_REF`. No kept ref has been created, so unverifiable partial state still loses its recovery reference and latch. | Apply Cowork’s standing fallback: after invoking the main-checkout merge, every failure becomes 1 blocking outcome with a kept ref and latch. Preserve recovery state before that invocation. Add a regression combining an actual partial landing with a failed post-check; require the blocking outcome and intact recovery ref. |
| F17 | blocking, resolved | `kgme/merge.py:258`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:267`; `tests/test_merge.py:673` | Option A detects the switched branch, records a named blocking outcome, and returns before sync. | The regression requires unchanged main and no false `ok`. |
| F19 | blocking, resolved | `kgme/merge.py:384`; `kgme/merge.py:444`; `tests/test_merge.py:719` | Kept recovery refs are separate from disposable trial storage. The regression preserves the original ref through 1 dry run and 1 new design head, then verifies repair, cleanup, and resumed landing. | The requested protection and regression are present. |

## Verdict

BLOCK: 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`5a46c9ef7d47752b`**, verified before and after inspection. No files were changed and no tests were executed. The supplied gate log reports **462 passed, 34 deselected**, and **0 blocking lint findings**. Tooling diagnostics were not findings against the diff.

F16 follows from static control flow. The cycle 7 partial-landing fix is present, but verification exceptions remain outside its protection. This triggers the standing fallback supplied for cycle 8. The halt override `01M5H96ZPRCB7MZM56CG3JPY7M` was verified in the ledger.

All **6 acceptance scenarios** have tests or stated evidence: automatic landing, forbidden-path refusal, red-trial isolation, staged-file wait/retry, harness refusal, and terminal approval/show. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree still requires the documented hook activation.

ADR-015 module contracts and named production effects are present; subprocesses use argument lists. No dependencies, executable `TODO`, or `shell=True` were introduced. The previously noted size deviation remains: `merge.py` has **468** lines, its tests **744**, and the existing CLI **395**, against the approximate **300-line** target.
