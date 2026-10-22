---
id: AUDIT-0084
type: report
status: final
handoff: HANDOFF-0055
author: codex
source: inferred
sources: ["HANDOFF-0055", "staged diff sha256 aae3507c93029d6e8a420aca33739195fca71a2f2c1a35aa9f923996d351d35c"]
tier: 2
created: 2026-10-21T21:21:10-07:00
period: 2026-10-21
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7, F8]
---

# Review of HANDOFF-0055, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `aae3507c93029d6e8a420aca33739195fca71a2f2c1a35aa9f923996d351d35c`. Verdict **BLOCK**: blocking 8, transient 0, cosmetic 2, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/merge.py:259` | The trial checks `track_sha`, but the live merge uses the moving branch name. A second design commit made during the trial can therefore land without either checks or lane validation, while the ledger names the first commit. | Merge the tested SHA. Add a test that advances `design` during the trial with a forbidden change. |
| F2 | blocking | `kgme/merge.py:147` | `git diff --name-only` reports the destination of a detected rename. Moving `control/review/example.md` into `docs/design/example.md` can pass the lanes check while deleting a forbidden source path. Whitespace splitting also corrupts filenames containing spaces. | Use NUL-delimited output with rename detection disabled, or validate both rename endpoints. Test an outside-to-inside rename and filenames containing spaces. |
| F3 | blocking | `kgme/merge.py:259` | A successful `git merge` invokes `post-merge`, not `post-commit`. Only `post-commit` exists here, and the proposed hook pushes before merging. The new merge therefore remains unpushed until another sync trigger, contrary to What §2. | Invoke the existing sync mechanism after recording the successful merge, or supply an appropriate hook. Verify against a local bare remote without requiring another commit. |
| F4 | blocking | `kgme/merge.py:203` | A competing trigger disappears after the 5-second lock wait. If a main commit occurs during the first trial, its trigger can exit here; the first run subsequently detects the changed main SHA and exits too. Neither run lands the waiting design commit. Heads are also captured before acquiring the lock. | Preserve pending triggers or perform a bounded retry against refreshed heads. Test a main commit arriving during an active trial. |
| F5 | blocking | `kgme/merge.py:237` | After the intent is appended, clone/Git failures, Git timeouts, or a missing check executable escape without an outcome. Subsequent runs do not reconcile the open intent. This violates the required 1-intent/1-outcome record. | Close handled failures with an appropriately classified outcome and reconcile interrupted runs. Test subprocess failure and timeout paths. |
| F6 | blocking | `kgme/approve.py:83` | Approval names are unrestricted, but lookup uses a prefix. Approving `canvas:draft` makes that event eligible for `--show canvas`; line 94 then prints `draft:<sha>` as the commit. This can select approval for the wrong object. | Parse the key unambiguously and compare the complete name, or reject delimiter-bearing names consistently. Test these 2 names together. |
| F7 | blocking | `kgme/approve.py:85` | Comparing timestamp strings does not reliably select the newest approval across timezone offsets. On the same date, `01:10-08:00` is later than `01:50-07:00`, but this code selects the latter. Equal timestamps also select the first event. | Compare parsed instants with an event-ID tie-breaker. Test differing offsets and equal timestamps. |
| F8 | blocking | `tests/test_merge.py:204` | The 60-second acceptance claim tests a replacement hook and a trivial Makefile, omitting the supplied hook’s sync and atlas steps. The supplied full-check evidence reports pytest alone taking 69.60 seconds. There is no evidence that the required production path meets the bound. | Exercise the supplied hook and full trial in a temporary repository copy. Meet the 60-second requirement or obtain an explicit handoff amendment. |
| F9 | cosmetic | `kgme/merge.py:228`; `tests/test_merge.py:27`; `tests/test_approve.py:21` | Several effectful helpers lack ADR-015 prefixes: `outcome`, `git`, `commit_on`, `merge_events`, and `approvals`. | Rename them with `run_*`, `write_*`, or `read_*` prefixes and document missing helper contracts. |
| F10 | cosmetic | `tests/test_merge.py:69` | Five tests lack an ADR-016 class: those starting at lines 69, 84, 99, 148, and 175. | Add an explicit class marker to each test. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/merge.py:259` | The trial checks `track_sha`, but the live merge uses the moving branch name. A second design commit made during the trial can therefore land without either checks or lane validation, while the ledger names the first commit. | Merge the tested SHA. Add a test that advances `design` during the trial with a forbidden change. |
| F2 | blocking | `kgme/merge.py:147` | `git diff --name-only` reports the destination of a detected rename. Moving `control/review/example.md` into `docs/design/example.md` can pass the lanes check while deleting a forbidden source path. Whitespace splitting also corrupts filenames containing spaces. | Use NUL-delimited output with rename detection disabled, or validate both rename endpoints. Test an outside-to-inside rename and filenames containing spaces. |
| F3 | blocking | `kgme/merge.py:259` | A successful `git merge` invokes `post-merge`, not `post-commit`. Only `post-commit` exists here, and the proposed hook pushes before merging. The new merge therefore remains unpushed until another sync trigger, contrary to What §2. | Invoke the existing sync mechanism after recording the successful merge, or supply an appropriate hook. Verify against a local bare remote without requiring another commit. |
| F4 | blocking | `kgme/merge.py:203` | A competing trigger disappears after the 5-second lock wait. If a main commit occurs during the first trial, its trigger can exit here; the first run subsequently detects the changed main SHA and exits too. Neither run lands the waiting design commit. Heads are also captured before acquiring the lock. | Preserve pending triggers or perform a bounded retry against refreshed heads. Test a main commit arriving during an active trial. |
| F5 | blocking | `kgme/merge.py:237` | After the intent is appended, clone/Git failures, Git timeouts, or a missing check executable escape without an outcome. Subsequent runs do not reconcile the open intent. This violates the required 1-intent/1-outcome record. | Close handled failures with an appropriately classified outcome and reconcile interrupted runs. Test subprocess failure and timeout paths. |
| F6 | blocking | `kgme/approve.py:83` | Approval names are unrestricted, but lookup uses a prefix. Approving `canvas:draft` makes that event eligible for `--show canvas`; line 94 then prints `draft:<sha>` as the commit. This can select approval for the wrong object. | Parse the key unambiguously and compare the complete name, or reject delimiter-bearing names consistently. Test these 2 names together. |
| F7 | blocking | `kgme/approve.py:85` | Comparing timestamp strings does not reliably select the newest approval across timezone offsets. On the same date, `01:10-08:00` is later than `01:50-07:00`, but this code selects the latter. Equal timestamps also select the first event. | Compare parsed instants with an event-ID tie-breaker. Test differing offsets and equal timestamps. |
| F8 | blocking | `tests/test_merge.py:204` | The 60-second acceptance claim tests a replacement hook and a trivial Makefile, omitting the supplied hook’s sync and atlas steps. The supplied full-check evidence reports pytest alone taking 69.60 seconds. There is no evidence that the required production path meets the bound. | Exercise the supplied hook and full trial in a temporary repository copy. Meet the 60-second requirement or obtain an explicit handoff amendment. |
| F9 | cosmetic | `kgme/merge.py:228`; `tests/test_merge.py:27`; `tests/test_approve.py:21` | Several effectful helpers lack ADR-015 prefixes: `outcome`, `git`, `commit_on`, `merge_events`, and `approvals`. | Rename them with `run_*`, `write_*`, or `read_*` prefixes and document missing helper contracts. |
| F10 | cosmetic | `tests/test_merge.py:69` | Five tests lack an ADR-016 class: those starting at lines 69, 84, 99, 148, and 175. | Add an explicit class marker to each test. |

## Verdict

BLOCK with 8 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`aae3507c93029d6e`**, verified before and after inspection. No files were changed and no tests were run. Sandbox diagnostics were not treated as findings.

All 6 acceptance scenarios have corresponding tests, subject to F8’s integration and timing gap. The builder supplies live evidence for Claude Code refusal and the real branch’s dry-run refusal; approval from Michou’s terminal remains explicitly untested.

The temporary-clone substitution is explained by ledger isolation and existing worktree-sensitive tests. The human-applied configuration, hook, settings, and reader artifacts exist in scratch; they remain unapplied.

The new modules have the required module docstrings and remain below 300 lines. `cli.py` reaches 388 lines, extending an acknowledged existing size exception. No dependencies, `TODO`, or `shell=True` were introduced.
