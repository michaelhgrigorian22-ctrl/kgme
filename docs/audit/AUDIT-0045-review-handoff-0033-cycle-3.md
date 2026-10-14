---
id: AUDIT-0045
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 7db09248775ff31da3654430334db558624edd306daba9b178bfa1352473d6db"]
tier: 2
created: 2026-10-13T12:06:28-07:00
period: 2026-10-13
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F6, F9, F10]
---

# Review of HANDOFF-0033, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `7db09248775ff31da3654430334db558624edd306daba9b178bfa1352473d6db`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_fs.py:121` | Ancestor redirection is fixed, but final-name replacement remains possible between `lstat` and `unlink`. The replacement is deleted without verification, including a symlink that must be refused. `run_rmdir_at` has the same interval. Both replacement tests intervene before these checks. | Secure the final entry against replacement through verification and deletion. Test swaps after hashing, after the final `lstat`, and before `rmdir`. |
| F2 | blocking | `kgme/clean_io.py:128` | Recovery now carries metadata and deduplicates correctly, but the persisted metadata can describe different bytes. An in-place rewrite after `_prepare` preserves device/inode: deletion reports the new hash with the old size, while interruption recovers the old hash. The supplied `digests` are unused during deletion. | Bind persisted size/hash to the version actually deleted; refuse changes before unlinking. Test an in-place rewrite followed by interruption. |
| F3 | blocking, resolved | `kgme/clean_io.py:135` | Both caught failure paths stop deletion. The regression verifies later files remain untouched. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:40` | Metadata and root-probe errors now become plan refusals. Tests cover mode `0400` children and a mode `000` root. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:212` | Refused plans receive blocking outcomes in both modes; the symlink regression checks both. | No further fix required. |
| F6 | blocking | `kgme/clean_io.py:243` | Successful deletion summaries are fixed, but preparation refusals still use raw clipping. With the regression’s long `key=x.md` path made unreadable, the refusal clips to 200 characters and expands to 220 after redaction. Ledger append rejects it, leaving the intent without its blocking outcome. This occurs before deletion. | Apply redaction-aware fitting to preparation refusals and validate every outcome path. Add the unreadable long-path regression. |
| F7 | cosmetic | `kgme/clean_io.py:158` | `read_unclosed_intents` fixes the cited helper, but new effects remain unprefixed: `_prepare`, `_stop`, `_open_matching`, and `_digest_of`. | Give these helpers appropriate `read_*`, `write_*`, or `run_*` names. |
| F8 | blocking, resolved | `kgme/clean_fs.py:136` | Payload creation now uses checked directory descriptors and exclusive, no-follow creation. The linked-payload regression verifies refusal before deletion. | No further fix required for this path-guard finding. |
| F9 | blocking | `kgme/cli.py:208` | Public `--base` replaces the repository boundary with any directory. Both manifest permissions and containment checks rebase onto it. Consequently, `--base <KGME_HOME>/docs` permits deleting `docs/memory/agent/*`, despite ADR-012 protecting `docs/`. | Constrain the public command to the authorized repository root. Keep temporary-root injection internal to tests; add a protected alternate-base refusal test. |
| F10 | blocking | `kgme/clean_fs.py:145` | The payload writer ignores `os.write`’s returned byte count. A short write is accepted before deletion, while the intent hashes the intended full text. An interrupted deletion then encounters truncated JSON during recovery. | Require a complete payload write before deletion. Test a short write and require either complete persistence or a classified refusal. |
| F11 | advisory | `jobs/clean/job.md:5` | The CLI satisfies the handoff’s invocation, but `jobs/clean/run.py` is absent despite ADR-015’s job-layout requirement. No current runtime dependency on it was identified. | Add a thin runner supporting `--dry-run`, or document an explicit exception. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_fs.py:121` | Ancestor redirection is fixed, but final-name replacement remains possible between `lstat` and `unlink`. The replacement is deleted without verification, including a symlink that must be refused. `run_rmdir_at` has the same interval. Both replacement tests intervene before these checks. | Secure the final entry against replacement through verification and deletion. Test swaps after hashing, after the final `lstat`, and before `rmdir`. |
| F2 | blocking | `kgme/clean_io.py:128` | Recovery now carries metadata and deduplicates correctly, but the persisted metadata can describe different bytes. An in-place rewrite after `_prepare` preserves device/inode: deletion reports the new hash with the old size, while interruption recovers the old hash. The supplied `digests` are unused during deletion. | Bind persisted size/hash to the version actually deleted; refuse changes before unlinking. Test an in-place rewrite followed by interruption. |
| F3 | blocking, resolved | `kgme/clean_io.py:135` | Both caught failure paths stop deletion. The regression verifies later files remain untouched. | No further fix required. |
| F4 | blocking, resolved | `kgme/clean_read.py:40` | Metadata and root-probe errors now become plan refusals. Tests cover mode `0400` children and a mode `000` root. | No further fix required. |
| F5 | blocking, resolved | `kgme/clean_io.py:212` | Refused plans receive blocking outcomes in both modes; the symlink regression checks both. | No further fix required. |
| F6 | blocking | `kgme/clean_io.py:243` | Successful deletion summaries are fixed, but preparation refusals still use raw clipping. With the regression’s long `key=x.md` path made unreadable, the refusal clips to 200 characters and expands to 220 after redaction. Ledger append rejects it, leaving the intent without its blocking outcome. This occurs before deletion. | Apply redaction-aware fitting to preparation refusals and validate every outcome path. Add the unreadable long-path regression. |
| F7 | cosmetic | `kgme/clean_io.py:158` | `read_unclosed_intents` fixes the cited helper, but new effects remain unprefixed: `_prepare`, `_stop`, `_open_matching`, and `_digest_of`. | Give these helpers appropriate `read_*`, `write_*`, or `run_*` names. |
| F8 | blocking, resolved | `kgme/clean_fs.py:136` | Payload creation now uses checked directory descriptors and exclusive, no-follow creation. The linked-payload regression verifies refusal before deletion. | No further fix required for this path-guard finding. |
| F9 | blocking | `kgme/cli.py:208` | Public `--base` replaces the repository boundary with any directory. Both manifest permissions and containment checks rebase onto it. Consequently, `--base <KGME_HOME>/docs` permits deleting `docs/memory/agent/*`, despite ADR-012 protecting `docs/`. | Constrain the public command to the authorized repository root. Keep temporary-root injection internal to tests; add a protected alternate-base refusal test. |
| F10 | blocking | `kgme/clean_fs.py:145` | The payload writer ignores `os.write`’s returned byte count. A short write is accepted before deletion, while the intent hashes the intended full text. An interrupted deletion then encounters truncated JSON during recovery. | Require a complete payload write before deletion. Test a short write and require either complete persistence or a classified refusal. |
| F11 | advisory | `jobs/clean/job.md:5` | The CLI satisfies the handoff’s invocation, but `jobs/clean/run.py` is absent despite ADR-015’s job-layout requirement. No current runtime dependency on it was identified. | Add a thin runner supporting `--dry-run`, or document an explicit exception. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`7db09248775ff31d`**, matching `review.sha`. Locations refer to the staged patch. No files were changed and no tests were run.

All 5 explicit handoff acceptance behaviors have tests. The reported **27 clean-suite passes** and **203 gate passes** remain builder evidence. The additional failure intervals above lack coverage.

New Python modules remain below approximately 300 lines and carry purpose/input/output/effect docstrings. No dependencies, subprocess calls, `shell=True`, or TODOs are added. HANDOFF-0034 material in the combined audit does not constitute review of its unstaged implementation.
