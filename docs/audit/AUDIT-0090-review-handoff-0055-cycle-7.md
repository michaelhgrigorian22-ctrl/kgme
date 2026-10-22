---
id: AUDIT-0090
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 2fc4b036a189a16963ea02d8166c9894d5c7d06bd1433fbb15252f427a2cf491"]
tier: 2
created: 2026-10-22T00:23:29-07:00
period: 2026-10-22
review_cycle: 7
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F16, F19]
---

# Review of HANDOFF-0055, cycle 7

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `2fc4b036a189a16963ea02d8166c9894d5c7d06bd1433fbb15252f427a2cf491`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:420` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:163` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:448` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:332` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:326`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:169`; `kgme/merge.py:439` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:245`; `tests/test_merge.py:531` | A moved main triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains covered. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The staged reader still attributes publication to the post-commit hook. Its correction remains a separate scratch diff. | Apply `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:251`; `kgme/merge.py:439`; `tests/test_merge.py:601` | Option A handles returned Git failures, but a landing `TimeoutExpired` skips all 3 post-checks. If Git has already installed the trial’s index, the outer handler records `transient` and deletes the recovery ref. The timeout regression still raises before invoking Git, so it cannot detect this path. | Perform bounded state verification after landing exceptions too. Preserve the trial ref and record 1 blocking outcome for partial or unverifiable state. Add a regression that raises after an actual partial landing; retain transient treatment when the checkout is verified unchanged. |
| F17 | blocking, resolved | `kgme/merge.py:248`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains covered. |
| F18 | blocking, resolved | `kgme/merge.py:252`; `tests/test_merge.py:672` | Under option A, the post-check detects the switched branch, records a named blocking outcome, and returns before sync. The regression requires unchanged main and no false `ok`. | The ruled detection mechanism is present. |
| F19 | blocking | `kgme/merge.py:165`; `kgme/merge.py:367`; `kgme/merge.py:444` | The preserved recovery ref is also disposable trial storage. After a blocking landing, `--dry-run` bypasses the latch; a new design commit bypasses it through a different key. Either run can replace and then delete `refs/kgme/merge-trial` while the checkout remains unrepaired, invalidating the recorded repair command. Neither path reaches the landing post-checks. | Protect unresolved recovery state across design heads and dry runs. Keep disposable trials separate from the preserved ref. Add blocked-landing regressions followed by a dry run and by a new design commit; require the original recovery ref to remain unchanged. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/merge.py:420` | Landing uses the tested trial commit. The regression excludes a later forbidden design commit. | The fix remains present. |
| F2 | blocking, resolved | `kgme/merge.py:163` | NUL-delimited paths with renames disabled preserve both endpoints and spaces. | Both regressions remain covered. |
| F3 | blocking, resolved | `kgme/merge.py:448` | Successful landing invokes `run_sync`. The bare-remote regression checks publication without another commit. | The fix remains present. |
| F4 | blocking, resolved | `kgme/merge.py:332` | Waiting triggers retain the longer lock bound, heads refresh under lock, and moved-main trials retry up to 3 times. | Both regressions remain covered. |
| F5 | blocking, resolved | `kgme/merge.py:326`; `tests/test_merge.py:407` | Open intents prevent the early return. The already-landed regression requires exactly 1 closing outcome across 2 subsequent runs. | The fix remains present. |
| F6 | blocking, resolved | `kgme/approve.py:60` | Delimiter-bearing names are rejected, and lookup matches the complete parsed name. | The regression remains covered. |
| F7 | blocking, resolved | `kgme/approve.py:99` | Approval selection compares parsed instants, then event IDs. | Both ordering regressions remain covered. |
| F8 | advisory, resolved | `docs/audit/2026-10-21-design-lands.md:37` | Verified ruling `01M5H4F2VTTE7RGGDAKVKNJZV9` accepts about 2 minutes. The recorded 61 seconds complies. | The ruling and corrected report remain present. |
| F9 | cosmetic, resolved | `tests/test_approve.py:21`; `tests/test_merge.py:257` | The previously identified helpers retain their corrected contracts or effect prefixes. | The corrections remain present. |
| F10 | cosmetic, resolved | `tests/test_merge.py:80` | All 5 previously unclassified tests retain explicit class markers. | The corrections remain present. |
| F11 | blocking, resolved | `kgme/merge.py:169`; `kgme/merge.py:439` | Trial-check and clone timeouts reach the transient handler. Both regressions require 1 intent and 1 outcome. | The fix remains present. |
| F12 | blocking, resolved | `control/git-hooks/post-commit:34`; `kgme/cli.py:332` | The hook selects main’s runtime, and the CLI reads main’s configuration. | The actual-hook test and activation instructions remain present. |
| F13 | blocking, resolved | `kgme/merge.py:245`; `tests/test_merge.py:531` | A moved main triggers a fresh trial. The regression requires 2 trials, correct parents, and a clean checkout. | The regression remains covered. |
| F14 | advisory, resolved | `tests/test_merge.py:65`; `tests/test_merge.py:491` | The helper replaces the TOML section. The actual design-hook test supplies divergent branch settings and verifies refusal under main’s lanes. | The integration coverage remains present. |
| F15 | cosmetic | `docs/readers/merging.md:23` | The staged reader still attributes publication to the post-commit hook. Its correction remains a separate scratch diff. | Apply `logs/scratch/handoff-0055/merging.md.diff` through the human-path workflow. |
| F16 | blocking | `kgme/merge.py:251`; `kgme/merge.py:439`; `tests/test_merge.py:601` | Option A handles returned Git failures, but a landing `TimeoutExpired` skips all 3 post-checks. If Git has already installed the trial’s index, the outer handler records `transient` and deletes the recovery ref. The timeout regression still raises before invoking Git, so it cannot detect this path. | Perform bounded state verification after landing exceptions too. Preserve the trial ref and record 1 blocking outcome for partial or unverifiable state. Add a regression that raises after an actual partial landing; retain transient treatment when the checkout is verified unchanged. |
| F17 | blocking, resolved | `kgme/merge.py:248`; `tests/test_merge.py:559` | The quiet-point recheck preserves an unfinished merge. The regression requires main unchanged, `MERGE_HEAD` preserved, and a transient outcome. | The regression remains covered. |
| F18 | blocking, resolved | `kgme/merge.py:252`; `tests/test_merge.py:672` | Under option A, the post-check detects the switched branch, records a named blocking outcome, and returns before sync. The regression requires unchanged main and no false `ok`. | The ruled detection mechanism is present. |
| F19 | blocking | `kgme/merge.py:165`; `kgme/merge.py:367`; `kgme/merge.py:444` | The preserved recovery ref is also disposable trial storage. After a blocking landing, `--dry-run` bypasses the latch; a new design commit bypasses it through a different key. Either run can replace and then delete `refs/kgme/merge-trial` while the checkout remains unrepaired, invalidating the recorded repair command. Neither path reaches the landing post-checks. | Protect unresolved recovery state across design heads and dry runs. Keep disposable trials separate from the preserved ref. Add blocked-landing regressions followed by a dry run and by a new design commit; require the original recovery ref to remain unchanged. |

## Verdict

BLOCK: 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`2fc4b036a189a169`**, verified before and after inspection. No files were changed and no tests were executed. The supplied gate log reports **460 passed, 34 deselected**, and **0 blocking lint findings**.

The F16/F18 ledger rulings were verified. This review accepts option A’s recorded race window. F16 concerns skipped verification after exceptions; F19 concerns loss of the recovery ref after detection.

All **6 acceptance scenarios** have tests or stated evidence. Human-terminal approval uses a marker-free fixture; no live approval by Michou is claimed. The design worktree still requires the documented hook activation.

Module contracts and named production effects are present; subprocesses use argument lists. No dependencies, executable `TODO`, or `shell=True` were introduced. ADR-015’s approximate **300-line** target remains exceeded: `merge.py` has **449** lines, its tests **685**, and the existing CLI **395**.

## Escalation

```
ESCALATION HANDOFF-0055: review loop halted after 7 cycles.
What failed: F16 has stood blocking for 3 consecutive cycles. Class: blocking.
Evidence:
  F16 `kgme/merge.py:251`; `kgme/merge.py:439`; `tests/test_merge.py:601`: Option A handles returned Git failures, but a landing `TimeoutExpired` skips all 3 post-checks. If Git has already installed the trial’s index, the outer handler records `transient` and deletes the recovery ref. The timeout regression still raises before invoking Git, so it cannot detect this path.
  F19 `kgme/merge.py:165`; `kgme/merge.py:367`; `kgme/merge.py:444`: The preserved recovery ref is also disposable trial storage. After a blocking landing, `--dry-run` bypasses the latch; a new design commit bypasses it through a different key. Either run can replace and then delete `refs/kgme/merge-trial` while the checkout remains unrepaired, invalidating the recorded repair command. Neither path reaches the landing post-checks.
Options: override (kgme review override --handoff HANDOFF-0055 --reason ...), reject (revert the working tree), retry (fix, then override, then kgme review again); a disputed class goes to the arbiter claude-opus-5-5 once, recorded with kgme review rule.
Recommended default: override and continue when the remaining findings are understood; reject when they are not.
If you do nothing: nothing is committed.
```
