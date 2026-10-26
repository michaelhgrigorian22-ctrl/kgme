---
id: AUDIT-0123
type: report
status: final
handoff: HANDOFF-0044
author: codex
source: inferred
sources: ["HANDOFF-0044", "staged diff sha256 813d750d6d61ec4ab8b8ceda1946bcca0bfee4ab649c94fc6ba3bb1078f9e7db"]
tier: 2
created: 2026-10-25T23:57:33-07:00
period: 2026-10-25
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F3, F4]
---

# Review of HANDOFF-0044, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `813d750d6d61ec4ab8b8ceda1946bcca0bfee4ab649c94fc6ba3bb1078f9e7db`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 0, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/toolbox.py:198` | HTMLParser now reads the exact `src` attribute. The regression covers remote `src` alongside local `data-src`. | None. |
| F2 | blocking, resolved | `kgme/toolbox.py:396` | Recursive discovery covers nested HTML pages, with a regression for a remote script. | None. |
| F3 | blocking | `kgme/toolbox.py:166` | Missing locks, packages, versions and hashes are checked, but any nonempty hash passes. The successful fixture at `tests/test_toolbox.py:41` uses `sha256:aa`, which is not a SHA-256 digest. The claimed hash backing remains unvalidated. | Validate the algorithm and 64 hexadecimal digest characters. Add malformed-hash regressions and correct the fixture. |
| F4 | blocking | `kgme/toolbox.py:339` | Ancestor symlinks remain unchecked. If `skills/alias` links to repository `memory/notes`, holding `skills/alias/example.md` passes: the leaf is not a symlink and resolves inside the repository. Line 367 then hashes the protected target despite the allowed-directory restriction. | Reject symlinks in every path component before traversal or reading. Add a harmless internal-target regression that verifies no content read occurs. |
| F5 | blocking, resolved | `kgme/toolbox.py:391` | The schema version now controls licence severity; regressions cover 1.7 and 1.8. | None. |
| F6 | cosmetic, resolved | `docs/audit/2026-10-25-toolbox.md:72` | The report now records ADR-020’s acceptance in `7aa1f44`, verified against that commit. | None. |
| F7 | advisory | `kgme/toolbox.py:1` | The new module has 401 lines, exceeding ADR-015’s approximately 300-line convention. | Separate filesystem effects from pure checks to reduce file size and strengthen the existing boundary. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `kgme/toolbox.py:198` | HTMLParser now reads the exact `src` attribute. The regression covers remote `src` alongside local `data-src`. | None. |
| F2 | blocking, resolved | `kgme/toolbox.py:396` | Recursive discovery covers nested HTML pages, with a regression for a remote script. | None. |
| F3 | blocking | `kgme/toolbox.py:166` | Missing locks, packages, versions and hashes are checked, but any nonempty hash passes. The successful fixture at `tests/test_toolbox.py:41` uses `sha256:aa`, which is not a SHA-256 digest. The claimed hash backing remains unvalidated. | Validate the algorithm and 64 hexadecimal digest characters. Add malformed-hash regressions and correct the fixture. |
| F4 | blocking | `kgme/toolbox.py:339` | Ancestor symlinks remain unchecked. If `skills/alias` links to repository `memory/notes`, holding `skills/alias/example.md` passes: the leaf is not a symlink and resolves inside the repository. Line 367 then hashes the protected target despite the allowed-directory restriction. | Reject symlinks in every path component before traversal or reading. Add a harmless internal-target regression that verifies no content read occurs. |
| F5 | blocking, resolved | `kgme/toolbox.py:391` | The schema version now controls licence severity; regressions cover 1.7 and 1.8. | None. |
| F6 | cosmetic, resolved | `docs/audit/2026-10-25-toolbox.md:72` | The report now records ADR-020’s acceptance in `7aa1f44`, verified against that commit. | None. |
| F7 | advisory | `kgme/toolbox.py:1` | The new module has 401 lines, exceeding ADR-015’s approximately 300-line convention. | Separate filesystem effects from pure checks to reduce file size and strengthen the existing boundary. |

## Verdict

BLOCK with 2 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`813d750d6d61ec4a`**, matching `review.patch` and `review.sha`.

All 5 acceptance items have tests or stated evidence. `make-check-c2.txt` records **624 passed, 42 deselected**, successful Ruff checks and **0 blocking** lint findings. `red-c1.txt` records the **8** reported pre-fix failures. The missing model licence and unpinned Playwright MCP remain documented user exceptions.

The implementation introduces **0** dependencies, subprocesses or TODOs. Module docstrings state purpose, inputs, outputs and effects; filesystem effects use `read_*` names.

No tests were executed or files changed during this review. ADR-024 was unavailable and concerns deferred work. F3 and F4 persist into cycle 2, so the review-loop protocol calls for arbitration.
