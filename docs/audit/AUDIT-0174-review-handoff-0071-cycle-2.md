---
id: AUDIT-0174
type: report
status: final
handoff: HANDOFF-0071
author: codex
source: inferred
sources: ["HANDOFF-0071", "staged diff sha256 78187627b0e20c08e26208adbbcdc151358ef1878d9a727716799f096444db58"]
tier: 2
created: 2026-11-18T16:23:43-08:00
period: 2026-11-18
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F2, F8]
---

# Review of HANDOFF-0071, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `78187627b0e20c08e26208adbbcdc151358ef1878d9a727716799f096444db58`. Verdict **BLOCK**: blocking 2, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/roles_run.py:273 | Outcomes now set both `ref` and `parent`. Success and nonzero-exit tests assert that no `agent:run` intent remains open. | No further change required. |
| F2 | blocking | kgme/roles.py:239; kgme/roles_run.py:92 | Ordinary tool narrowing is implemented, but validation and launch interpret tool strings differently. At `work`, `tools = ["Read", "Read,NotebookEdit"]` passes lint because `tool_name()` checks only the `Read` prefix. Launch refusal checks only for `(`. The resulting argv contains `--tools Read,Read,NotebookEdit`, while the deny universe omits `NotebookEdit`. The restriction therefore remains bypassable. | Require each role tool to match a complete supported bare name before constructing permissions or argv. Add regression coverage rejecting comma-separated and other malformed entries, with no child or intent created. |
| F3 | blocking, resolved | kgme/roles.py:212; kgme/roles_run.py:122 | The arbiter’s narrower ruling is implemented: cheap levels and models are blocked, launch refuses cheap roles, and `run_cheap_role` is absent. Both lint and launch have regression coverage. | No further change required. |
| F4 | blocking, resolved | kgme/roles_run.py:214 | Preparation and child execution after the intent now record classified outcomes on recoverable errors, interruption, and unexpected exceptions. All 4 failure-path tests assert closure. | No further change required. |
| F5 | blocking, resolved | kgme/roles.py:178; kgme/roles_io.py:143 | Scalar fields are checked before membership operations, and malformed IDs use the source path as their parsing key. Tests cover malformed fields and continued reporting for another role. | No further change required. |
| F6 | blocking, resolved | kgme/roles_io.py:36 | Default lint reads indexed role and rubric blobs; `--all` reads the working tree. Regression coverage includes divergent copies, working-tree role deletion, and staged rubric deletion. | No further change required. |
| F7 | cosmetic | kgme/atlas.py:202; kgme/atlas.py:219; kgme/cli_parser.py:213 | The test split and helper renames are complete, but 3 new public functions still have unannotated parameters: `add` in both atlas helpers and `subcommands` in `add_agent`. This leaves the annotation portion of F7 open under ADR-015. | Annotate the callback and parser parameters. |
| F8 | blocking | kgme/roles_run.py:124 | Launch filters lint findings using a path reconstructed from unvalidated role fields rather than the actual source path. For example, `roles/build/reader.toml` declaring `id = "build.alias"` and `tier_max = 1` produces blocking findings against `reader.toml`; running `build.alias` filters for `alias.toml`, discards both findings, and proceeds. | Preserve the actual source path through role lookup and use it to select findings. Add a mismatched-ID regression with a forbidden tool or Tier 1 declaration, asserting refusal before any child or intent. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/roles_run.py:273 | Outcomes now set both `ref` and `parent`. Success and nonzero-exit tests assert that no `agent:run` intent remains open. | No further change required. |
| F2 | blocking | kgme/roles.py:239; kgme/roles_run.py:92 | Ordinary tool narrowing is implemented, but validation and launch interpret tool strings differently. At `work`, `tools = ["Read", "Read,NotebookEdit"]` passes lint because `tool_name()` checks only the `Read` prefix. Launch refusal checks only for `(`. The resulting argv contains `--tools Read,Read,NotebookEdit`, while the deny universe omits `NotebookEdit`. The restriction therefore remains bypassable. | Require each role tool to match a complete supported bare name before constructing permissions or argv. Add regression coverage rejecting comma-separated and other malformed entries, with no child or intent created. |
| F3 | blocking, resolved | kgme/roles.py:212; kgme/roles_run.py:122 | The arbiter’s narrower ruling is implemented: cheap levels and models are blocked, launch refuses cheap roles, and `run_cheap_role` is absent. Both lint and launch have regression coverage. | No further change required. |
| F4 | blocking, resolved | kgme/roles_run.py:214 | Preparation and child execution after the intent now record classified outcomes on recoverable errors, interruption, and unexpected exceptions. All 4 failure-path tests assert closure. | No further change required. |
| F5 | blocking, resolved | kgme/roles.py:178; kgme/roles_io.py:143 | Scalar fields are checked before membership operations, and malformed IDs use the source path as their parsing key. Tests cover malformed fields and continued reporting for another role. | No further change required. |
| F6 | blocking, resolved | kgme/roles_io.py:36 | Default lint reads indexed role and rubric blobs; `--all` reads the working tree. Regression coverage includes divergent copies, working-tree role deletion, and staged rubric deletion. | No further change required. |
| F7 | cosmetic | kgme/atlas.py:202; kgme/atlas.py:219; kgme/cli_parser.py:213 | The test split and helper renames are complete, but 3 new public functions still have unannotated parameters: `add` in both atlas helpers and `subcommands` in `add_agent`. This leaves the annotation portion of F7 open under ADR-015. | Annotate the callback and parser parameters. |
| F8 | blocking | kgme/roles_run.py:124 | Launch filters lint findings using a path reconstructed from unvalidated role fields rather than the actual source path. For example, `roles/build/reader.toml` declaring `id = "build.alias"` and `tier_max = 1` produces blocking findings against `reader.toml`; running `build.alias` filters for `alias.toml`, discards both findings, and proceeds. | Preserve the actual source path through role lookup and use it to select findings. Add a mismatched-ID regression with a forbidden tool or Tier 1 declaration, asserting refusal before any child or intent. |

## Verdict

BLOCK with 2 blocking findings open.

## Notes

Reviewed SHA-256 prefix **`78187627b0e20c08`**, verified before and after inspection. No tests were run and no files were changed. Reported test results remain builder-supplied evidence; sandbox limitations are not findings against this diff.

All 5 acceptance items have tests or stated live evidence:

1. Role creation is covered by `tests/test_roles_agent.py:21`.
2. Forbidden tools and Tier 1 are covered by `tests/test_roles_lint.py:75`, subject to F2 and F8.
3. Department listing has automated coverage and AUDIT-0170’s reported Build (3), Audit (1), Finance (1) output.
4. Role-attributed intent/outcome events are covered by `tests/test_roles_run.py:47`. AUDIT-0170 reports a real child launch that stopped at authentication; a completed live model turn remains unverified.
5. Atlas relationships are covered by `tests/test_roles_agent.py:60` and reported generated-node evidence.

The 3 new production modules and 4 test/helper modules are below 300 lines. The patch adds no dependency, `TODO`, or `shell=True`; its subprocess calls use argument lists. The 2 human-path diffs exist separately under scratch and are outside the reviewed patch hash. The reported plugin-MCP residual is not reopened here.
