---
id: AUDIT-0110
type: report
status: final
handoff: HANDOFF-0042
author: codex
source: inferred
sources: ["HANDOFF-0042", "staged diff sha256 84588ecd24483537cc9c16734d444077eddc9c844303789030861ae6a2e0f2b7"]
tier: 2
created: 2026-10-25T15:42:55-07:00
period: 2026-10-25
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3]
---

# Review of HANDOFF-0042, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `84588ecd24483537cc9c16734d444077eddc9c844303789030861ae6a2e0f2b7`. Verdict **BLOCK**: blocking 3, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_lint.py:196 | The real-vault test still walks untracked files. Planting 1 frontmatter-free file under `docs/` therefore fails this test during `make check`, despite the CLI correctly skipping it. The CLI-only acceptance test misses this failure. | Use the default indexed file selection for this gate, retain separate `--all` coverage, and verify the planted-file scenario through `make check`. |
| F2 | blocking | tests/policy/test_agents_codex_builder.py:82,148 | Both probes can report refusal without proving enforcement. Substring matching accepts commands that merely mention the target; file absence proves no refusing layer; any HTTP result except `200`, including `301` or `403`, passes the network cell. The retained network stream shows DNS failure, exit `6` and HTTP `000`, which does not identify a sandbox refusal. | Reuse the exact-command and attributable-refusal logic in `canary_stream`. Treat unrelated errors as inconclusive and any actual HTTP response as network access. Add deterministic cases covering these false passes. |
| F3 | blocking | tests/policy/test_agents_codex_builder.py:93 | The unconditional strict xfail also masks an actual sandbox escape: if the outside-worktree file is written, line 115 fails and pytest accepts that failure as expected. The ruling permits an unattempted probe, not a successful forbidden write. | Restrict expected failure to the specific “not attempted” condition. An observed forbidden write must fail normally; preserve detection when a genuine refusal makes the expected-failure exemption obsolete. |
| F4 | cosmetic | kgme/vault.py:43; tests/policy/test_agents_codex_builder.py:62,132 | Three new effectful helpers, `walk_notes`, `record`, and `cheap_work_dir`, lack ADR-015’s effect prefixes. The last creates a directory despite its lookup-style name. | Rename them with appropriate `read_*` or `write_*` prefixes and state the directory-creation side effect explicitly. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | tests/test_lint.py:196 | The real-vault test still walks untracked files. Planting 1 frontmatter-free file under `docs/` therefore fails this test during `make check`, despite the CLI correctly skipping it. The CLI-only acceptance test misses this failure. | Use the default indexed file selection for this gate, retain separate `--all` coverage, and verify the planted-file scenario through `make check`. |
| F2 | blocking | tests/policy/test_agents_codex_builder.py:82,148 | Both probes can report refusal without proving enforcement. Substring matching accepts commands that merely mention the target; file absence proves no refusing layer; any HTTP result except `200`, including `301` or `403`, passes the network cell. The retained network stream shows DNS failure, exit `6` and HTTP `000`, which does not identify a sandbox refusal. | Reuse the exact-command and attributable-refusal logic in `canary_stream`. Treat unrelated errors as inconclusive and any actual HTTP response as network access. Add deterministic cases covering these false passes. |
| F3 | blocking | tests/policy/test_agents_codex_builder.py:93 | The unconditional strict xfail also masks an actual sandbox escape: if the outside-worktree file is written, line 115 fails and pytest accepts that failure as expected. The ruling permits an unattempted probe, not a successful forbidden write. | Restrict expected failure to the specific “not attempted” condition. An observed forbidden write must fail normally; preserve detection when a genuine refusal makes the expected-failure exemption obsolete. |
| F4 | cosmetic | kgme/vault.py:43; tests/policy/test_agents_codex_builder.py:62,132 | Three new effectful helpers, `walk_notes`, `record`, and `cheap_work_dir`, lack ADR-015’s effect prefixes. The last creates a directory despite its lookup-style name. | Rename them with appropriate `read_*` or `write_*` prefixes and state the directory-creation side effect explicitly. |

## Verdict

BLOCK with 3 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`84588ecd24483537`**, matching `review.sha`. No tests were run and no files were changed.

The registration, schema, reader paragraph, and builder profile are present in the surrounding tree. Tests cover registration, prefixes, CLI skipping, `--all`, and manifest boundaries. The report states a green baseline `make check`; F1 identifies the missing planted-file gate coverage.

The 2 recorded rulings, `ITEM3-LANES` and `ITEM3-WORKTREE`, remain advisory. F2 and F3 concern measurement correctness beyond those accepted limitations and require item 3 arbitration if disputed.

No dependencies were added; changed subprocess calls use argument lists. Module documentation covers purpose, inputs, outputs, and effects. File lengths are 313 lines for `lint.py`, 354 for `test_lint.py`, and 426 for the already oversized `cli.py`, exceeding ADR-015’s approximate 300-line target.
