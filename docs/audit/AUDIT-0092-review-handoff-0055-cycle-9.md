---
id: AUDIT-0092
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 cef8d829e70628aa598f643663724a0d0f90ca9c5c376865f6b15b0a36fb6200"]
tier: 2
created: 2026-10-22T01:04:34-07:00
period: 2026-10-22
review_cycle: 9
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F16]
---

# Review of HANDOFF-0055, cycle 9

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `cef8d829e70628aa598f643663724a0d0f90ca9c5c376865f6b15b0a36fb6200`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:433` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:166` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:459` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:343` | Waiting triggers retain the longer lock bound; heads refresh under lock; moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:337`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:61` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:100` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:451` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:257`; `tests/test_merge.py:531` | A main move detected before invocation triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The staged reader attributes publication to `kgme sync`, matching F3. | The correction remains present. |
| F16 | blocking | `kgme/merge.py:271`; `kgme/merge.py:451`; `tests/test_merge.py:751` | Recovery state now precedes invocation, and the new regression covers failure inside `read_landed_state`. However, the subsequent `read_sha(main, branch or "HEAD")` remains outside the guard. After the existing branch-switch scenario, a timeout or `OSError` in this diagnostic reaches the outer handler and records 1 transient outcome despite a known wrong-branch landing. The recovery ref survives, but the required blocking outcome and repair instructions are absent. Cowork’s fallback is therefore incomplete. | Enforce the blocking boundary across all post-invocation effects, including diagnostic reads. Extend the branch-switch regression to fail this read; require exactly 1 blocking outcome naming the intact recovery ref, the latch, and no sync. |
| F17 | blocking, resolved | `kgme/merge.py:259`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:265`; `tests/test_merge.py:676` | With successful diagnostic reads, option A detects the switched branch, records a named blocking outcome, and returns before sync. | The regression remains present; the diagnostic-exception gap is tracked under F16. |
| F19 | blocking, resolved | `kgme/merge.py:262`; `tests/test_merge.py:722` | Recovery refs remain separate from disposable trial storage. The regression preserves the original ref through 1 dry run and 1 new design head, then verifies repair, cleanup, and resumed landing. | The requested protection remains present. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:433` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:166` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:459` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:343` | Waiting triggers retain the longer lock bound; heads refresh under lock; moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:337`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:61` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:100` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:451` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:257`; `tests/test_merge.py:531` | A main move detected before invocation triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The staged reader attributes publication to `kgme sync`, matching F3. | The correction remains present. |
| F16 | blocking | `kgme/merge.py:271`; `kgme/merge.py:451`; `tests/test_merge.py:751` | Recovery state now precedes invocation, and the new regression covers failure inside `read_landed_state`. However, the subsequent `read_sha(main, branch or "HEAD")` remains outside the guard. After the existing branch-switch scenario, a timeout or `OSError` in this diagnostic reaches the outer handler and records 1 transient outcome despite a known wrong-branch landing. The recovery ref survives, but the required blocking outcome and repair instructions are absent. Cowork’s fallback is therefore incomplete. | Enforce the blocking boundary across all post-invocation effects, including diagnostic reads. Extend the branch-switch regression to fail this read; require exactly 1 blocking outcome naming the intact recovery ref, the latch, and no sync. |
| F17 | blocking, resolved | `kgme/merge.py:259`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:265`; `tests/test_merge.py:676` | With successful diagnostic reads, option A detects the switched branch, records a named blocking outcome, and returns before sync. | The regression remains present; the diagnostic-exception gap is tracked under F16. |
| F19 | blocking, resolved | `kgme/merge.py:262`; `tests/test_merge.py:722` | Recovery refs remain separate from disposable trial storage. The regression preserves the original ref through 1 dry run and 1 new design head, then verifies repair, cleanup, and resumed landing. | The requested protection remains present. |

## Verdict

BLOCK: 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`cef8d829e70628aa`**, verified before and after inspection. No files were changed and no tests were executed. Tooling diagnostics were not findings against the diff.

F16 follows from static control flow. The supplied red log records **1 failed regression** before the fix; the supplied gate log reports **463 passed, 34 deselected**, and **0 blocking lint findings**.

All **6 acceptance scenarios** have tests or stated evidence. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree still requires the documented hook activation. The latest reader amendment remains a separate draft.

ADR-015 module contracts and named production effects are present; subprocesses use argument lists. No dependencies, executable `TODO`, or `shell=True` were introduced. The previously recorded size deviation remains: `merge.py` has **460** lines, its tests **772**, and the CLI **395**, against the approximate **300-line** target.
