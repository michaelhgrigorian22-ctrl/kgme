---
id: AUDIT-0122
type: report
status: final
handoff: HANDOFF-0044
author: codex
source: inferred
sources: ["HANDOFF-0044", "staged diff sha256 88b72cca5a191f99894c48b0befe17635c3f55a4a7f742a13f1d948af4ac151c"]
tier: 2
created: 2026-10-25T23:47:47-07:00
period: 2026-10-25
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5]
---

# Review of HANDOFF-0044, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `88b72cca5a191f99894c48b0befe17635c3f55a4a7f742a13f1d948af4ac151c`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/toolbox.py:47` | The script regex can inspect `data-src` instead of `src`. For `<script src="https://cdn.example/x.js" data-src="/static/vendor/lib-1.0.0.js">`, it captures the local path. With that vendor row present, the remote script passes, violating the acceptance test. | Use the standard-library HTML parser to inspect the exact `src` attribute. Add this regression case. |
| F2 | blocking | `kgme/toolbox.py:272` | `glob("*.html")` excludes nested cockpit pages. A remote script in `cockpit/pages/example.html` produces no finding, although §3 requires checking every script source in `cockpit/`. | Discover HTML recursively and test a nested page containing a remote script. |
| F3 | blocking | `kgme/toolbox.py:175` | Package rows using `uv.lock` bypass verification entirely. Neither the lockfile’s existence nor the named package, version, and hashes are checked. The fixture at `tests/test_toolbox.py:51` explicitly passes without a lockfile, so the claimed hash backing can be absent. | Read the lockfile and verify each package row against its pinned entry and artifact hashes. Test missing locks, absent packages, and version mismatches. |
| F4 | blocking | `kgme/toolbox.py:253` | A `held` value is joined to `base` and read without confinement. Absolute paths, `../` paths, and symlink targets can cause lint to hash files outside the repository. Folder hashing at line 206 also follows file symlinks. This contradicts the repository-path contract and can cross protected read boundaries. | Validate resolved paths before reading, including every folder member. Reject escapes and protected targets with blocking findings. Test using harmless external fixtures. |
| F5 | blocking | `kgme/toolbox.py:119` | Missing licences are permanently classified as advisory. No schema version is read or passed into the check, so advancing to 1.8 cannot produce the blocking classification required by §3 and the committed schema. | Derive severity from the schema version and test both 1.7 and 1.8 behavior. |
| F6 | cosmetic | `docs/audit/2026-10-25-toolbox.md:72` | The report says ADR-020 remains proposed and awaits acceptance, but the committed ADR is accepted and commit `7aa1f44` records Michou’s acceptance. | Update the pending-acceptance statements before finalizing the report, citing the acceptance commit. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/toolbox.py:47` | The script regex can inspect `data-src` instead of `src`. For `<script src="https://cdn.example/x.js" data-src="/static/vendor/lib-1.0.0.js">`, it captures the local path. With that vendor row present, the remote script passes, violating the acceptance test. | Use the standard-library HTML parser to inspect the exact `src` attribute. Add this regression case. |
| F2 | blocking | `kgme/toolbox.py:272` | `glob("*.html")` excludes nested cockpit pages. A remote script in `cockpit/pages/example.html` produces no finding, although §3 requires checking every script source in `cockpit/`. | Discover HTML recursively and test a nested page containing a remote script. |
| F3 | blocking | `kgme/toolbox.py:175` | Package rows using `uv.lock` bypass verification entirely. Neither the lockfile’s existence nor the named package, version, and hashes are checked. The fixture at `tests/test_toolbox.py:51` explicitly passes without a lockfile, so the claimed hash backing can be absent. | Read the lockfile and verify each package row against its pinned entry and artifact hashes. Test missing locks, absent packages, and version mismatches. |
| F4 | blocking | `kgme/toolbox.py:253` | A `held` value is joined to `base` and read without confinement. Absolute paths, `../` paths, and symlink targets can cause lint to hash files outside the repository. Folder hashing at line 206 also follows file symlinks. This contradicts the repository-path contract and can cross protected read boundaries. | Validate resolved paths before reading, including every folder member. Reject escapes and protected targets with blocking findings. Test using harmless external fixtures. |
| F5 | blocking | `kgme/toolbox.py:119` | Missing licences are permanently classified as advisory. No schema version is read or passed into the check, so advancing to 1.8 cannot produce the blocking classification required by §3 and the committed schema. | Derive severity from the schema version and test both 1.7 and 1.8 behavior. |
| F6 | cosmetic | `docs/audit/2026-10-25-toolbox.md:72` | The report says ADR-020 remains proposed and awaits acceptance, but the committed ADR is accepted and commit `7aa1f44` records Michou’s acceptance. | Update the pending-acceptance statements before finalizing the report, citing the acceptance commit. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`88b72cca5a191f99`**, matching both the patch and `review.sha`.

All 5 named acceptance items have tests or stated evidence. The saved `make-check.txt` records **616 passed, 42 deselected**, and lint with **0 blocking** findings. The report explicitly records the missing model licence and unpinned Playwright MCP as Michou’s exceptions. Those exceptions are not re-raised here.

The new implementation and test files contain **276** and **161** lines respectively, have module-level purpose/input/output/effect documentation, and introduce no dependency, `TODO`, or subprocess. Production filesystem effects use `read_*` names. The existing CLI grows from **440 to 443** lines.

No pytest run or file changes were performed. ADR-024 was referenced by the handoff but was not present in `docs/adr/`; its deferred mod work is outside this diff.
