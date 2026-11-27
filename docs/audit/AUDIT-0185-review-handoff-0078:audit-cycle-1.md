---
id: AUDIT-0185
type: report
status: final
handoff: HANDOFF-0078:audit
author: codex
source: inferred
sources: ["HANDOFF-0078:audit", "staged diff sha256 313049941699f09954038b114b500287aea9b2c2c6cdf459a8f661d7445f1141"]
tier: 2
created: 2026-11-27T13:27:59-08:00
period: 2026-11-27
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5]
---

# Review of HANDOFF-0078:audit, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `313049941699f09954038b114b500287aea9b2c2c6cdf459a8f661d7445f1141`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [report:42](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/docs/audit/pending-handoff-0078-desktop-fence.md:42) | The claim that either tool name would be refused is false. `path_like` rejects strings containing whitespace (`kgme/hermes_fence_parse.py:277`), so `judge_other` allows an `mcp__terminal` call whose sole argument is `command = "echo /…/KGME/…"`. The successful command therefore does not prove the hook was absent or its verdict discarded. | Mark shell-hook delivery unknown, including the Desktop table row, until invocation and payload are measured. |
| F2 | blocking | [probe.py:75](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/probe.py:75) | Config masking misses valid YAML forms. For example, `"api_key": demo-secret` passes unchanged because the key is quoted and the value misses the token patterns. Flow mappings and multiline secrets also escape this line-based filter. Running the recommended script can expose credentials in stdout and its output file. | Emit explicitly allowed configuration fields, or redact parsed structures with coverage for quoted keys, nested mappings and multiline values. Verify using synthetic values. |
| F3 | blocking | [capture.py:33](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:33) | The instructions copy this file into a plugin directory, but `OUT` follows `__file__`. Shell and plugin records consequently land in different `capture.jsonl` files. Collecting the instructed scratch file can omit every plugin invocation. | Give both forms one explicit absolute output path under the task’s scratch directory and document it. |
| F4 | blocking | [capture.py:57](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:57) | The recorder drops the effective profile: installed `agent/shell_hooks.py:105` supplies `profile`, but this script retains only its key name. Reading process `HERMES_HOME` does not identify a per-call home override. This loses evidence needed to resolve L4. | Preserve the supplied profile and record the resolved per-call home in the plugin form. Preserve candidate directory metadata rather than only its key names. |
| F5 | blocking | [capture.py:78](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:78) | Plugin recording failures are silently swallowed. The shell error path also passes an `error` field that `record()` discards. Missing records can therefore mean recorder failure, contradicting the report’s inference that no record means no hook invocation. | Expose sanitized recording failures and establish a successful control capture before interpreting each surface’s results. Treat missing evidence as inconclusive. |
| F6 | cosmetic | [probe.py:83](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/probe.py:83) | Effectful functions such as `files`, `excerpt`, `grep`, `git`, `config` and capture’s `record` do not follow ADR-015’s effect-naming convention. | Use `read_*`, `run_*` and `write_*` names for internal effect functions, retaining required external entry-point names. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | [report:42](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/docs/audit/pending-handoff-0078-desktop-fence.md:42) | The claim that either tool name would be refused is false. `path_like` rejects strings containing whitespace (`kgme/hermes_fence_parse.py:277`), so `judge_other` allows an `mcp__terminal` call whose sole argument is `command = "echo /…/KGME/…"`. The successful command therefore does not prove the hook was absent or its verdict discarded. | Mark shell-hook delivery unknown, including the Desktop table row, until invocation and payload are measured. |
| F2 | blocking | [probe.py:75](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/probe.py:75) | Config masking misses valid YAML forms. For example, `"api_key": demo-secret` passes unchanged because the key is quoted and the value misses the token patterns. Flow mappings and multiline secrets also escape this line-based filter. Running the recommended script can expose credentials in stdout and its output file. | Emit explicitly allowed configuration fields, or redact parsed structures with coverage for quoted keys, nested mappings and multiline values. Verify using synthetic values. |
| F3 | blocking | [capture.py:33](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:33) | The instructions copy this file into a plugin directory, but `OUT` follows `__file__`. Shell and plugin records consequently land in different `capture.jsonl` files. Collecting the instructed scratch file can omit every plugin invocation. | Give both forms one explicit absolute output path under the task’s scratch directory and document it. |
| F4 | blocking | [capture.py:57](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:57) | The recorder drops the effective profile: installed `agent/shell_hooks.py:105` supplies `profile`, but this script retains only its key name. Reading process `HERMES_HOME` does not identify a per-call home override. This loses evidence needed to resolve L4. | Preserve the supplied profile and record the resolved per-call home in the plugin form. Preserve candidate directory metadata rather than only its key names. |
| F5 | blocking | [capture.py:78](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/capture.py:78) | Plugin recording failures are silently swallowed. The shell error path also passes an `error` field that `record()` discards. Missing records can therefore mean recorder failure, contradicting the report’s inference that no record means no hook invocation. | Expose sanitized recording failures and establish a successful control capture before interpreting each surface’s results. Treat missing evidence as inconclusive. |
| F6 | cosmetic | [probe.py:83](/Users/michaelgrigorian/Projects/KGME/work/handoff-0078-audit/logs/scratch/handoff-0078/probe.py:83) | Effectful functions such as `files`, `excerpt`, `grep`, `git`, `config` and capture’s `record` do not follow ADR-015’s effect-naming convention. | Use `read_*`, `run_*` and `write_*` names for internal effect functions, retaining required external entry-point names. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed patch SHA-256 prefix **`313049941699f099`**, plus its 2 referenced scratch scripts. The patch changes only the report; both scripts are below 300 lines, use standard-library dependencies and contain no `shell=True`.

The declared `pending` state and provisional report ID are permitted by this task. Acceptance remains red: scratch hashes are `uncomputed`, Desktop’s hook is `none`, and evidence is outstanding. Downstream tasks must remain undispatched.

Python validation was unavailable because `uv` attempted a prohibited cache write. That is a tooling limitation, not a finding against the diff. No pytest or live probes ran, and no files were changed.
