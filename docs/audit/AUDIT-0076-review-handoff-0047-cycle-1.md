---
id: AUDIT-0076
type: report
status: final
handoff: HANDOFF-0047
author: codex
source: inferred
sources: ["HANDOFF-0047", "staged diff sha256 a4c64dd6ec47ea1ab9314c249a4d685ae497cc1b779063f3f362eab270d4db0a"]
tier: 2
created: 2026-10-21T16:10:53-07:00
period: 2026-10-21
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6, F7]
---

# Review of HANDOFF-0047, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `a4c64dd6ec47ea1ab9314c249a4d685ae497cc1b779063f3f362eab270d4db0a`. Verdict **BLOCK**: blocking 7, transient 0, cosmetic 0, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/session.py:134](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:134) | `loose` accepts any working directory outside the main checkout, including an unrelated empty directory. `execvpe` preserves that directory, while the rendered settings contain neither KGME’s hooks nor its deny list. Those project settings are discovered from Claude’s working directory, so this launch can omit the mandatory guard. The new test explicitly permits this case. [Settings discovery](https://code.claude.com/docs/en/settings#where-claude-code-keeps-the-local-file-in-a-git-repository). | Verify the workspace belongs to this repository and loads its mandatory policy before launching. Reject unrelated directories and add coverage for missing hooks and deny rules. |
| F2 | blocking | [kgme/session.py:106](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:106) | Extra arguments can widen the named level. For example, `--allowedTools WebFetch` passes through unchanged and grants the tool that `loose` must refuse. The recorded level and settings hash therefore do not establish the claimed allowance. [CLI permission flags](https://code.claude.com/docs/en/cli-reference#cli-flags). | Validate extra arguments against permitted options. Reject options that change permissions, settings sources, workspace boundaries, or configured caps, and test those rejections. |
| F3 | blocking | [kgme/session.py:215](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:215) | A session launched from a worktree writes its note into the main ledger but writes its payload under the worktree’s `base`. Its relative `payload_ref` consequently points to a missing file when resolved from the main checkout. The existing worktree test covers hook payloads only. | Store session payloads under the main checkout and make their references relative to it. Add a worktree launcher test that reads the recorded payload from the main checkout. |
| F4 | blocking | [kgme/ledger.py:69](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:69) | The ledger pin covers `read_default_dirs` and `read_test_dirs`, but `read_base_dirs` still routes directly to the supplied checkout. Production callers including capture, brief, clean, and atlas therefore retain a path to a separate worktree ledger, contrary to What §3. | Route production ledger writers through the common-directory resolver. Preserve explicit isolated test directories separately, and test a production caller from a worktree. |
| F5 | blocking | [kgme/session.py:148](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:148) | Handoff eligibility is not validated. The reused lookup deliberately includes `done/`, and the launcher checks neither `status: open` nor `from: cowork` or `michou`. It can therefore launch an unattended task using a non-executable handoff under the repository’s constitution. | Validate the handoff’s location and frontmatter before granting its Outputs. Add rejection cases for completed handoffs and unauthorized authors. |
| F6 | blocking | [tests/policy/test_agents_sessions.py:182](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:182) | The 7 canary cells do not record the rendered level settings’ hash. `settings_sha` hashes user settings, while `fingerprints` covers project settings. `write_level` neither hashes its run copy nor emits a session start note, despite the module’s claim. The evidence cannot identify the level configuration exercised. | Bind each cell to the exact rendered settings bytes, argv, and level before launch. Assert that the recorded digest matches the file supplied through `--settings`. |
| F7 | blocking | [tests/policy/test_agents_sessions.py:186](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:186) | The assertion accepts inconclusive observations. The audit records 3 such cells: `tight` writes and both network probes. None exercised an enforcement layer, so the required refusals remain unproved despite a successful test return. This is separate from the acknowledged cwd residual. | Obtain attributable refusal evidence for these required cells and make the acceptance check distinguish demonstrated refusal from inconclusive results. |
| F8 | advisory | [kgme/session.py:58](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:58) | `render` is documented as pure but calls filesystem-dependent `Path.resolve`. Its logic also shares a module with process and filesystem effects, weakening ADR-015’s explicit separation. | Move path canonicalization into a named effects function and pass resolved paths into the pure renderer. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [kgme/session.py:134](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:134) | `loose` accepts any working directory outside the main checkout, including an unrelated empty directory. `execvpe` preserves that directory, while the rendered settings contain neither KGME’s hooks nor its deny list. Those project settings are discovered from Claude’s working directory, so this launch can omit the mandatory guard. The new test explicitly permits this case. [Settings discovery](https://code.claude.com/docs/en/settings#where-claude-code-keeps-the-local-file-in-a-git-repository). | Verify the workspace belongs to this repository and loads its mandatory policy before launching. Reject unrelated directories and add coverage for missing hooks and deny rules. |
| F2 | blocking | [kgme/session.py:106](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:106) | Extra arguments can widen the named level. For example, `--allowedTools WebFetch` passes through unchanged and grants the tool that `loose` must refuse. The recorded level and settings hash therefore do not establish the claimed allowance. [CLI permission flags](https://code.claude.com/docs/en/cli-reference#cli-flags). | Validate extra arguments against permitted options. Reject options that change permissions, settings sources, workspace boundaries, or configured caps, and test those rejections. |
| F3 | blocking | [kgme/session.py:215](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:215) | A session launched from a worktree writes its note into the main ledger but writes its payload under the worktree’s `base`. Its relative `payload_ref` consequently points to a missing file when resolved from the main checkout. The existing worktree test covers hook payloads only. | Store session payloads under the main checkout and make their references relative to it. Add a worktree launcher test that reads the recorded payload from the main checkout. |
| F4 | blocking | [kgme/ledger.py:69](/Users/michaelgrigorian/Projects/KGME/brain/kgme/ledger.py:69) | The ledger pin covers `read_default_dirs` and `read_test_dirs`, but `read_base_dirs` still routes directly to the supplied checkout. Production callers including capture, brief, clean, and atlas therefore retain a path to a separate worktree ledger, contrary to What §3. | Route production ledger writers through the common-directory resolver. Preserve explicit isolated test directories separately, and test a production caller from a worktree. |
| F5 | blocking | [kgme/session.py:148](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:148) | Handoff eligibility is not validated. The reused lookup deliberately includes `done/`, and the launcher checks neither `status: open` nor `from: cowork` or `michou`. It can therefore launch an unattended task using a non-executable handoff under the repository’s constitution. | Validate the handoff’s location and frontmatter before granting its Outputs. Add rejection cases for completed handoffs and unauthorized authors. |
| F6 | blocking | [tests/policy/test_agents_sessions.py:182](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:182) | The 7 canary cells do not record the rendered level settings’ hash. `settings_sha` hashes user settings, while `fingerprints` covers project settings. `write_level` neither hashes its run copy nor emits a session start note, despite the module’s claim. The evidence cannot identify the level configuration exercised. | Bind each cell to the exact rendered settings bytes, argv, and level before launch. Assert that the recorded digest matches the file supplied through `--settings`. |
| F7 | blocking | [tests/policy/test_agents_sessions.py:186](/Users/michaelgrigorian/Projects/KGME/brain/tests/policy/test_agents_sessions.py:186) | The assertion accepts inconclusive observations. The audit records 3 such cells: `tight` writes and both network probes. None exercised an enforcement layer, so the required refusals remain unproved despite a successful test return. This is separate from the acknowledged cwd residual. | Obtain attributable refusal evidence for these required cells and make the acceptance check distinguish demonstrated refusal from inconclusive results. |
| F8 | advisory | [kgme/session.py:58](/Users/michaelgrigorian/Projects/KGME/brain/kgme/session.py:58) | `render` is documented as pure but calls filesystem-dependent `Path.resolve`. Its logic also shares a module with process and filesystem effects, weakening ADR-015’s explicit separation. | Move path canonicalization into a named effects function and pass resolved paths into the pure renderer. |

## Verdict

BLOCK with 7 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `a4c64dd6ec47ea1a`, verified against the patch and `review.sha`.

No files were changed and no tests were run. Git’s denied temporary-cache creation was a tooling limitation, not a finding.

The concurrency test covers 8 processes × 500 events, JSON parsing, unique IDs, and complete event coverage. The patch introduces no dependencies, `TODO`, or `shell=True`; its subprocess calls use argument lists.

The audit records Michou’s acceptance of removing staging/commit permissions and of the cwd residual. Those decisions are not reopened here; F1 concerns the separate loss of mandatory project policy.
