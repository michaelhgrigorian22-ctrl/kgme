---
id: AUDIT-0088
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 683dc9cb3a255f6e3abb30280355ec7971120e28463b8726cd937345d3c0a4e4"]
tier: 2
created: 2026-10-21T23:59:56-07:00
period: 2026-10-21
review_cycle: 5
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F16, F17]
---

# Review of HANDOFF-0055, cycle 5

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `683dc9cb3a255f6e3abb30280355ec7971120e28463b8726cd937345d3c0a4e4`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:407` | Landing uses the trial commit. The regression still excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:159` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:423` | Successful landing invokes `run_sync`. The bare-remote regression verifies publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:329` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:323` | Open intents prevent the early return. The already-landed regression verifies exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their contract or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:165`; `kgme/merge.py:415` | Check timeouts reach the transient handler. Both timeout regressions assert 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook test and worktree activation instructions remain present. | The implementation remains present. |
| F13 | blocking, resolved | `kgme/merge.py:239`; `tests/test_merge.py:531` | Expected-head enforcement lands the trial commit. The regression advances main after the outer quiet check and requires 2 trials, the correct parents, and a clean checkout. | The fix and red-test evidence are present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section, avoiding duplication. The actual design-hook test now supplies divergent branch settings and verifies refusal under main’s lanes. | The requested integration coverage is present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The code docstring is corrected, but the staged reader still attributes publication to the post-commit hook. The correction exists only as a separate scratch diff. | Apply the prepared `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:239`; `kgme/merge.py:246`; `kgme/merge.py:262` | Landing advances main before copying and installing the index. An exception from `copyfile`, `read-tree`, or index installation bypasses the sole rollback branch, leaving main advanced with an old or incomplete checkout. The handler records a transient outcome; subsequent runs see design already contained and return without repair. | Make landing exception-safe and recover interrupted updates before the no-work return. Add regressions injecting failure after the ref update and during index installation, then verify consistent ref/index/tree state and recovery on restart. |
| F17 | blocking | `kgme/merge.py:231` | The locked recheck reads but ignores `checkout.in_progress`. A `--no-commit` merge starting after the outer quiet check can leave HEAD and index unchanged while creating `MERGE_HEAD`; landing then proceeds during that unfinished merge, violating What §2. | Recheck operation state while holding `index.lock`, before changing main. Add a regression starting an empty-tree merge between the outer check and landing; require a transient refusal with the pending operation preserved. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:407` | Landing uses the trial commit. The regression still excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:159` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:423` | Successful landing invokes `run_sync`. The bare-remote regression verifies publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:329` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:323` | Open intents prevent the early return. The already-landed regression verifies exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their contract or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:165`; `kgme/merge.py:415` | Check timeouts reach the transient handler. Both timeout regressions assert 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. The actual-hook test and worktree activation instructions remain present. | The implementation remains present. |
| F13 | blocking, resolved | `kgme/merge.py:239`; `tests/test_merge.py:531` | Expected-head enforcement lands the trial commit. The regression advances main after the outer quiet check and requires 2 trials, the correct parents, and a clean checkout. | The fix and red-test evidence are present. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section, avoiding duplication. The actual design-hook test now supplies divergent branch settings and verifies refusal under main’s lanes. | The requested integration coverage is present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The code docstring is corrected, but the staged reader still attributes publication to the post-commit hook. The correction exists only as a separate scratch diff. | Apply the prepared `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:239`; `kgme/merge.py:246`; `kgme/merge.py:262` | Landing advances main before copying and installing the index. An exception from `copyfile`, `read-tree`, or index installation bypasses the sole rollback branch, leaving main advanced with an old or incomplete checkout. The handler records a transient outcome; subsequent runs see design already contained and return without repair. | Make landing exception-safe and recover interrupted updates before the no-work return. Add regressions injecting failure after the ref update and during index installation, then verify consistent ref/index/tree state and recovery on restart. |
| F17 | blocking | `kgme/merge.py:231` | The locked recheck reads but ignores `checkout.in_progress`. A `--no-commit` merge starting after the outer quiet check can leave HEAD and index unchanged while creating `MERGE_HEAD`; landing then proceeds during that unfinished merge, violating What §2. | Recheck operation state while holding `index.lock`, before changing main. Add a regression starting an empty-tree merge between the outer check and landing; require a transient refusal with the pending operation preserved. |

## Verdict

BLOCK: 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`683dc9cb3a255f6e`**, verified before and after inspection. No files were changed and no tests were executed. F16 and F17 follow from static control-flow inspection.

All **6 acceptance scenarios** have tests or stated evidence: automatic landing, forbidden-path refusal, red-trial isolation, staged-file wait/retry, harness refusal, and terminal approval/show. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The existing design worktree still requires the documented hook activation.

The supplied gate log reports **454 passed, 1 failed, 34 deselected**, with **0 blocking lint findings**. Its failure concerns the unrelated HANDOFF-0056 proposal path, absent from this patch, and is not charged against this diff.

Module contracts are present, subprocesses use argument lists, and no dependency, executable `TODO`, or `shell=True` was introduced. ADR-015’s approximate **300-line** target remains exceeded: `merge.py` has **424** lines, its tests **555**, and the existing CLI **395**.
