---
id: AUDIT-0024
type: report
status: final
handoff: HANDOFF-0031
author: codex
source: inferred
sources: ["HANDOFF-0031", "staged diff sha256 98eea2978ad8ac190f4cc27583b37d8756c7357102bfb32bb0cf65c039c242b8"]
tier: 2
created: 2026-09-20T15:47:10-07:00
period: 2026-09-20
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F3]
---

# Review of HANDOFF-0031, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `98eea2978ad8ac190f4cc27583b37d8756c7357102bfb32bb0cf65c039c242b8`. Verdict **BLOCK**: blocking 1, transient 0, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/lint.py:161 | Null timestamps are rejected except for a task’s `due`. | Implemented with regression assertions for required timestamps and nullable task deadlines. |
| F2 | blocking, resolved | kgme/lint.py:180 | Provenance now requires nonempty strings; the legacy-report exemption remains intact. | Implemented with valid and invalid provenance tests. |
| F3 | blocking | kgme/lint.py:38 | Duplicate detection still misses mappings supplied through YAML merges. Replacing a valid note’s status with `<<: {status: active, "status": draft}` silently keeps `draft`. The custom scan skips the merge, and SafeLoader subsequently flattens its contents without checking their duplicate keys. | Check each original mapping, including merge sources, before flattening. Preserve legitimate merge overrides and add a regression test for this case. |
| F4 | blocking, resolved | kgme/lint.py:124 | Non-string keys produce classed findings; unexpected per-note exceptions no longer terminate the scan. | Implemented with boolean-key and scan-continuation tests. |
| F5 | blocking, resolved | kgme/vault.py:31 | Invalid roots raise an error, and the CLI exits 2. | Implemented with reader and CLI regression tests. |
| F6 | blocking, resolved | kgme/vault.py:35 | Resolved paths are deduplicated while distinct files retain duplicate-ID checks. | Implemented with overlapping-root and CLI assertions. |
| F7 | cosmetic, resolved | kgme/lint.py:67 | Multiline YAML error messages render on 1 line. | Implemented with a malformed-YAML regression assertion. |
| F8 | cosmetic, resolved | kgme/lint.py:3; kgme/schema.py:1; kgme/cli.py:4 | Module descriptions reflect schema v1.3 and the implemented validator. | Updated; the historical v1.2 reference remains appropriate. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/lint.py:161 | Null timestamps are rejected except for a task’s `due`. | Implemented with regression assertions for required timestamps and nullable task deadlines. |
| F2 | blocking, resolved | kgme/lint.py:180 | Provenance now requires nonempty strings; the legacy-report exemption remains intact. | Implemented with valid and invalid provenance tests. |
| F3 | blocking | kgme/lint.py:38 | Duplicate detection still misses mappings supplied through YAML merges. Replacing a valid note’s status with `<<: {status: active, "status": draft}` silently keeps `draft`. The custom scan skips the merge, and SafeLoader subsequently flattens its contents without checking their duplicate keys. | Check each original mapping, including merge sources, before flattening. Preserve legitimate merge overrides and add a regression test for this case. |
| F4 | blocking, resolved | kgme/lint.py:124 | Non-string keys produce classed findings; unexpected per-note exceptions no longer terminate the scan. | Implemented with boolean-key and scan-continuation tests. |
| F5 | blocking, resolved | kgme/vault.py:31 | Invalid roots raise an error, and the CLI exits 2. | Implemented with reader and CLI regression tests. |
| F6 | blocking, resolved | kgme/vault.py:35 | Resolved paths are deduplicated while distinct files retain duplicate-ID checks. | Implemented with overlapping-root and CLI assertions. |
| F7 | cosmetic, resolved | kgme/lint.py:67 | Multiline YAML error messages render on 1 line. | Implemented with a malformed-YAML regression assertion. |
| F8 | cosmetic, resolved | kgme/lint.py:3; kgme/schema.py:1; kgme/cli.py:4 | Module descriptions reflect schema v1.3 and the implemented validator. | Updated; the historical v1.2 reference remains appropriate. |

## Verdict

BLOCK with 1 open blocking finding.

## Notes

Reviewed SHA-256 prefix **`98eea2978ad8ac19`**, matching `review.sha`. Findings follow static inspection, including the installed PyYAML merge-construction code. No tests or write commands were run.

All 3 acceptance items have tests or stated live evidence. The builder reports 123 passing tests, a 6-second acceptance run, and 94 real notes yielding 0 blocking, 19 advisory, and 6 cosmetic findings. That evidence does not cover F3’s merge case.

All 7 reviewed Python files remain below 300 lines. File reads and CLI effects are separated from validation logic, and module docstrings describe their contracts. The patch introduces no dependency, TODO, or subprocess call. Existing dependencies are pinned and justified in the packaging report; the existing Makefile invokes `uv run kgme lint`. Cycle-1 deviation judgments remain unchanged.
