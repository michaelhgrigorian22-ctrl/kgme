---
id: AUDIT-0094
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 c035458b6c1de379c6c432bf94d55c307c95397cd70c5f00d7b675432ffc0b78"]
tier: 2
created: 2026-10-22T01:44:48-07:00
period: 2026-10-22
review_cycle: 11
reviewer: gpt-6-astra
verdict: PASS
open_blocking: []
---

# Review of HANDOFF-0055, cycle 11

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `c035458b6c1de379c6c432bf94d55c307c95397cd70c5f00d7b675432ffc0b78`. Verdict **PASS**: blocking 0, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:434` | Landing uses the tested trial commit; the regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:166` | NUL-delimited paths and disabled rename detection preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:460` | Successful landing invokes `run_sync`; the bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:344` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:338`; `tests/test_merge.py:407` | Open intents prevent the early return; reconciliation requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:61` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:100` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ledger ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes; the recorded 61 seconds complies. | The ruling and measurement were verified. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | Previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:452` | Trial-check and clone timeouts reach the transient handler; both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:257`; `tests/test_merge.py:531` | A main move detected before invocation triggers a fresh trial; the regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section; the actual-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The reader attributes publication to `kgme sync`, matching F3. | The correction remains present. |
| F16 | blocking, resolved | `kgme/merge.py:278`; `tests/test_merge.py:812` | The landing boundary now catches `Exception`, including `UnicodeDecodeError`. The new regression requires exactly 1 blocking outcome naming an intact recovery ref and no sync. | Cowork’s follow-up is implemented; the saved red run reproduces the prior transient outcome. |
| F17 | blocking, resolved | `kgme/merge.py:259`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge; the regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:265`; `tests/test_merge.py:676` | Successful diagnostics detect the switched branch, produce a named blocking outcome, and return before sync. | Branch-switch and diagnostic-exception coverage remain present. |
| F19 | blocking, resolved | `kgme/merge.py:262`; `tests/test_merge.py:722` | Recovery refs remain separate from disposable trial storage; coverage preserves the original ref through 1 dry run and 1 new design head, then verifies repair and resumed landing. | The protection remains present. |

## Verdict

PASS

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:434` | Landing uses the tested trial commit; the regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:166` | NUL-delimited paths and disabled rename detection preserve both endpoints and spaces. | Both regressions remain present. |
| F3 | blocking, resolved | `kgme/merge.py:460` | Successful landing invokes `run_sync`; the bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:344` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain present. |
| F5 | blocking, resolved | `kgme/merge.py:338`; `tests/test_merge.py:407` | Open intents prevent the early return; reconciliation requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:61` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains present. |
| F7 | blocking, resolved | `kgme/approve.py:100` | Approval selection compares parsed instants, then event IDs. | Both ordering cases remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Ledger ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes; the recorded 61 seconds complies. | The ruling and measurement were verified. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | Previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:172`; `kgme/merge.py:452` | Trial-check and clone timeouts reach the transient handler; both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:257`; `tests/test_merge.py:531` | A main move detected before invocation triggers a fresh trial; the regression requires 2 trials, correct parents, and a clean checkout. | The regression remains present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section; the actual-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic, resolved | `docs/readers/merging.md:23` | The reader attributes publication to `kgme sync`, matching F3. | The correction remains present. |
| F16 | blocking, resolved | `kgme/merge.py:278`; `tests/test_merge.py:812` | The landing boundary now catches `Exception`, including `UnicodeDecodeError`. The new regression requires exactly 1 blocking outcome naming an intact recovery ref and no sync. | Cowork’s follow-up is implemented; the saved red run reproduces the prior transient outcome. |
| F17 | blocking, resolved | `kgme/merge.py:259`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge; the regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains present. |
| F18 | blocking, resolved | `kgme/merge.py:265`; `tests/test_merge.py:676` | Successful diagnostics detect the switched branch, produce a named blocking outcome, and return before sync. | Branch-switch and diagnostic-exception coverage remain present. |
| F19 | blocking, resolved | `kgme/merge.py:262`; `tests/test_merge.py:722` | Recovery refs remain separate from disposable trial storage; coverage preserves the original ref through 1 dry run and 1 new design head, then verifies repair and resumed landing. | The protection remains present. |

## Verdict

PASS

## Notes

Reviewed SHA-256 prefix **`c035458b6c1de379`**, verified before and after inspection. No files were modified and no tests were run. The saved follow-up gate reports **495 passed, 34 deselected, and 0 blocking lint findings**.

All **6 acceptance scenarios** have tests or stated evidence: hook landing (`tests/test_merge.py:218`, plus the 61-second measurement), forbidden-path refusal (`:138`), red-trial isolation (`:153`), staged-file wait and retry (`:175`), harness refusal (`tests/test_approve.py:59`), and terminal approval with retrieval (`:89`). Terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree’s hook activation remains explicitly deferred.

ADR-015 module contracts, named effects, pure decision helpers, and subprocess argument lists remain present. This patch introduces **0 dependencies**, no `TODO`, and no `shell=True`. The previously recorded size deviation remains: `merge.py` has **461 lines**, its tests **837**, and the CLI **395**, against the approximate **300-line** target.
