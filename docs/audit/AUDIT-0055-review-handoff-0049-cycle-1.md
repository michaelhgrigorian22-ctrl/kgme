---
id: AUDIT-0055
type: report
status: final
handoff: HANDOFF-0049
author: codex
source: inferred
sources: ["HANDOFF-0049", "staged diff sha256 33bc366d9349b377bd4ed7435edc6cedc4587c47b7d24dfb347bfdab8b6dedaf"]
tier: 2
created: 2026-10-16T00:06:11-07:00
period: 2026-10-16
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7]
---

# Review of HANDOFF-0049, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `33bc366d9349b377bd4ed7435edc6cedc4587c47b7d24dfb347bfdab8b6dedaf`. Verdict **BLOCK**: blocking 7, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [Makefile:20](/Users/michaelgrigorian/Projects/Automate/Makefile:20) | The shared `core.hooksPath` now points to `control/git-hooks`, but the design checkout still contains only `tools/git-hooks`. Verified from both checkouts: design commits lose their post-commit hook, and its `make check` expects the old setting. | Preserve functioning hooks and checks in both worktrees during the migration. Add coverage for commits from each checkout. |
| F2 | blocking | [control/move-home.sh:42](/Users/michaelgrigorian/Projects/Automate/control/move-home.sh:42) | Process enumeration fails open. An `lsof` failure is suppressed by the pipeline and `\|\| true`; an empty result prints “none found” and permits both moves without establishing the required idle state. Only syntax validation is recorded. | Distinguish successful enumeration with no matching processes from enumeration failure. Refuse before mutation on failure; test busy, idle, and failed-enumeration cases. |
| F3 | blocking | [kgme/vault.py:79](/Users/michaelgrigorian/Projects/Automate/kgme/vault.py:79) | Unioning every `design` path into local existence masks broken links. For example, `docs/plans/phase-0-prepare.md:29` still names `docs/handoff/2026-09-09-machine-audit.md`, which exists only on `design` after this migration. The same union validates report targets and repository-map folders. | Keep checkout-local existence separate from explicitly identified design references. Correct the stale live link and test that another branch cannot conceal a missing local target. |
| F4 | blocking | [kgme/coherence.py:104](/Users/michaelgrigorian/Projects/Automate/kgme/coherence.py:104) | The fixed prefix list silently excludes repository paths including `.claude/settings.json`, `uv.lock`, and old `tools/` references. Their disappearance or staleness produces no finding, contrary to Part A §7’s coverage requirement. | Recognize repository paths independently of the current prefix whitelist, including hidden paths and obsolete roots. Add missing-path cases for these examples. |
| F5 | blocking | [kgme/coherence.py:21](/Users/michaelgrigorian/Projects/Automate/kgme/coherence.py:21) | `CLASS = "advisory"` is permanent. No activation criterion or promotion mechanism implements the required change to blocking after 1 week of use. | Define the promotion criterion in configuration and test findings and exit status before and after activation. |
| F6 | blocking | [tests/test_coherence.py:99](/Users/michaelgrigorian/Projects/Automate/tests/test_coherence.py:99) | The acceptance test discards every finding in open handoffs, although those documents are explicitly in scope. The report acknowledges 1 finding for the removed `docs/.Rhistory` while 0049 remains open, then claims zero for a future closed state. This patch does not establish the required zero-findings result. | Check the full required scope without the blanket exclusion and provide zero-findings evidence for the final staged tree. Describe pending results as pending. |
| F7 | blocking | [docs/audit/2026-10-15-one-home.md:31](/Users/michaelgrigorian/Projects/Automate/docs/audit/2026-10-15-one-home.md:31) | The module split supports ADR-015, but the report explicitly acknowledges 3 modified paths outside the handoff’s named Outputs: `kgme/coherence.py`, `kgme/vault.py`, and `kgme/cli.py`. Its discretionary score does not amend the constitution’s explicit output-path boundary. | Obtain a scoped addendum authorizing these paths, or implement within the authorized paths while retaining the logic/effects separation. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [Makefile:20](/Users/michaelgrigorian/Projects/Automate/Makefile:20) | The shared `core.hooksPath` now points to `control/git-hooks`, but the design checkout still contains only `tools/git-hooks`. Verified from both checkouts: design commits lose their post-commit hook, and its `make check` expects the old setting. | Preserve functioning hooks and checks in both worktrees during the migration. Add coverage for commits from each checkout. |
| F2 | blocking | [control/move-home.sh:42](/Users/michaelgrigorian/Projects/Automate/control/move-home.sh:42) | Process enumeration fails open. An `lsof` failure is suppressed by the pipeline and `\|\| true`; an empty result prints “none found” and permits both moves without establishing the required idle state. Only syntax validation is recorded. | Distinguish successful enumeration with no matching processes from enumeration failure. Refuse before mutation on failure; test busy, idle, and failed-enumeration cases. |
| F3 | blocking | [kgme/vault.py:79](/Users/michaelgrigorian/Projects/Automate/kgme/vault.py:79) | Unioning every `design` path into local existence masks broken links. For example, `docs/plans/phase-0-prepare.md:29` still names `docs/handoff/2026-09-09-machine-audit.md`, which exists only on `design` after this migration. The same union validates report targets and repository-map folders. | Keep checkout-local existence separate from explicitly identified design references. Correct the stale live link and test that another branch cannot conceal a missing local target. |
| F4 | blocking | [kgme/coherence.py:104](/Users/michaelgrigorian/Projects/Automate/kgme/coherence.py:104) | The fixed prefix list silently excludes repository paths including `.claude/settings.json`, `uv.lock`, and old `tools/` references. Their disappearance or staleness produces no finding, contrary to Part A §7’s coverage requirement. | Recognize repository paths independently of the current prefix whitelist, including hidden paths and obsolete roots. Add missing-path cases for these examples. |
| F5 | blocking | [kgme/coherence.py:21](/Users/michaelgrigorian/Projects/Automate/kgme/coherence.py:21) | `CLASS = "advisory"` is permanent. No activation criterion or promotion mechanism implements the required change to blocking after 1 week of use. | Define the promotion criterion in configuration and test findings and exit status before and after activation. |
| F6 | blocking | [tests/test_coherence.py:99](/Users/michaelgrigorian/Projects/Automate/tests/test_coherence.py:99) | The acceptance test discards every finding in open handoffs, although those documents are explicitly in scope. The report acknowledges 1 finding for the removed `docs/.Rhistory` while 0049 remains open, then claims zero for a future closed state. This patch does not establish the required zero-findings result. | Check the full required scope without the blanket exclusion and provide zero-findings evidence for the final staged tree. Describe pending results as pending. |
| F7 | blocking | [docs/audit/2026-10-15-one-home.md:31](/Users/michaelgrigorian/Projects/Automate/docs/audit/2026-10-15-one-home.md:31) | The module split supports ADR-015, but the report explicitly acknowledges 3 modified paths outside the handoff’s named Outputs: `kgme/coherence.py`, `kgme/vault.py`, and `kgme/cli.py`. Its discretionary score does not amend the constitution’s explicit output-path boundary. | Obtain a scoped addendum authorizing these paths, or implement within the authorized paths while retaining the logic/effects separation. |

## Verdict

BLOCK with 7 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`33bc366d9349b377`**, verified before and after inspection. No files were changed and no tests were executed. Git-wrapper cache errors were tooling limits, not findings against the diff.

All **27** finished handoffs’ report targets resolve to files. Both clutter targets are absent. Stored canary output records **10 passed**, with advisory and inconclusive cells disclosed. Lookup and main-checkout push behavior have test coverage.

Changed Python files remain below **300 lines**. The new production reader uses named effects and an argument-list subprocess; no dependencies, `TODO`, or `shell=True` were added. Part B and its **5** live checks remain deferred to Michou, as authorized.
