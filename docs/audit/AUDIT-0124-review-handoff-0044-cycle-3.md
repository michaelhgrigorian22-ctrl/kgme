---
id: AUDIT-0124
type: report
status: final
handoff: HANDOFF-0044
author: codex
source: inferred
sources: ["HANDOFF-0044", "staged diff sha256 05a970e1f30c752937b214478b090d2f6e4a675c8dd3ef62b59264397f3abad9"]
tier: 2
created: 2026-10-26T00:09:54-07:00
period: 2026-10-26
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F8]
---

# Review of HANDOFF-0044, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `05a970e1f30c752937b214478b090d2f6e4a675c8dd3ef62b59264397f3abad9`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/toolbox.py:203` | The parser checks the exact `src` attribute; the regression retains remote `src` alongside local `data-src`. | None. |
| F2 | blocking, resolved | `kgme/toolbox_read.py:154` | Recursive discovery covers nested HTML pages, with a regression. | None. |
| F3 | blocking, resolved | `kgme/toolbox.py:173` | Lock hashes now require `sha256:` and 64 lowercase hexadecimal characters. The corrected fixture and 4 malformed-hash cases cover the disposition. | None. |
| F4 | blocking, resolved | `kgme/toolbox_read.py:93` | Held-path validation checks every ancestor before hashing. The internal-target regression verifies rejection of `skills/alias/example.md`. | None. |
| F5 | blocking, resolved | `kgme/toolbox.py:102` | Schema version controls licence severity, with 1.7 and 1.8 regressions. | None. |
| F6 | cosmetic, resolved | `docs/audit/2026-10-25-toolbox.md:72` | The report records ADR-020’s acceptance in verified commit `7aa1f44`. | None. |
| F7 | advisory, resolved | `kgme/toolbox_read.py:1` | The split leaves 290 lines of checks and 159 lines of filesystem effects, with documented inputs, outputs and effects. | None. |
| F8 | blocking | `kgme/toolbox_read.py:153` | Discovery bypasses the held-path guard: a symlink `cockpit/static/vendor/example.html` pointing to a protected or external file is read here before `read_held` runs at line 157. Python discovery at line 58 has the same unchecked read. F4’s helper fix therefore does not protect these 2 scanning paths. | Validate discovered paths before reading, reject symlink components with blocking findings, and add full `read_findings` regressions for `.html` and `.py` links that assert no target content is read. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/toolbox.py:203` | The parser checks the exact `src` attribute; the regression retains remote `src` alongside local `data-src`. | None. |
| F2 | blocking, resolved | `kgme/toolbox_read.py:154` | Recursive discovery covers nested HTML pages, with a regression. | None. |
| F3 | blocking, resolved | `kgme/toolbox.py:173` | Lock hashes now require `sha256:` and 64 lowercase hexadecimal characters. The corrected fixture and 4 malformed-hash cases cover the disposition. | None. |
| F4 | blocking, resolved | `kgme/toolbox_read.py:93` | Held-path validation checks every ancestor before hashing. The internal-target regression verifies rejection of `skills/alias/example.md`. | None. |
| F5 | blocking, resolved | `kgme/toolbox.py:102` | Schema version controls licence severity, with 1.7 and 1.8 regressions. | None. |
| F6 | cosmetic, resolved | `docs/audit/2026-10-25-toolbox.md:72` | The report records ADR-020’s acceptance in verified commit `7aa1f44`. | None. |
| F7 | advisory, resolved | `kgme/toolbox_read.py:1` | The split leaves 290 lines of checks and 159 lines of filesystem effects, with documented inputs, outputs and effects. | None. |
| F8 | blocking | `kgme/toolbox_read.py:153` | Discovery bypasses the held-path guard: a symlink `cockpit/static/vendor/example.html` pointing to a protected or external file is read here before `read_held` runs at line 157. Python discovery at line 58 has the same unchecked read. F4’s helper fix therefore does not protect these 2 scanning paths. | Validate discovered paths before reading, reject symlink components with blocking findings, and add full `read_findings` regressions for `.html` and `.py` links that assert no target content is read. |

## Verdict

BLOCK with 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`05a970e1f30c7529`**, matching the patch and `review.sha`. F8 follows from static inspection; no tests were executed or files changed.

All **5 acceptance items** have tests or stated evidence. `make-check-c3.txt` records **629 passed, 42 deselected**, successful Ruff checks and **0 blocking** lint findings. The missing model licence and unpinned Playwright MCP remain documented user exceptions.

The implementation introduces **0 dependencies, subprocesses or TODOs**. Filesystem effects use `read_*` names. The new test file has **296 lines**; the existing CLI grows by **3 lines** to **443**. ADR-024 is absent and concerns deferred work.
