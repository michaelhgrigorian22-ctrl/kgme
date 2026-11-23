---
id: AUDIT-0176
type: report
status: final
handoff: HANDOFF-0073
author: codex
source: inferred
sources: ["HANDOFF-0073", "staged diff sha256 5821df73927dfa4ba7453c6ab8ff8ef9c9f4e081b3245c797dcf009d764de320"]
tier: 2
created: 2026-11-23T13:10:49-08:00
period: 2026-11-23
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5]
---

# Review of HANDOFF-0073, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `5821df73927dfa4ba7453c6ab8ff8ef9c9f4e081b3245c797dcf009d764de320`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/hermes_fence.py:296 | The fence treats the hook’s `cwd` as the tool’s working directory. Installed Hermes supplies its **process** directory, while terminal and file tools use a separate session directory. After a session enters KGME from elsewhere, a relative `write_file("kgme/cli.py")` can therefore pass as outside KGME. | Obtain the authoritative session directory for each call, and refuse ambiguous relative targets. Add coverage where process and session directories differ. |
| F2 | blocking | kgme/hermes_fence.py:193 | Directory tracking assumes every `cd` executes successfully and discards shell control flow. From the repository, `cd /dev/null; rm kgme/cli.py` passes inspection because the simulated directory becomes `/dev/null`; the real `cd` fails and the deletion executes in the repository. | Preserve execution semantics or conservatively check subsequent commands against every possible directory. Add failed, skipped and piped `cd` cases. |
| F3 | blocking | kgme/hermes_fence.py:61 | The patch recognizer misses Hermes’s supported `***Delete File:` spelling and `*** Move File: source -> destination` operation. A patch containing 1 recognized proposal edit plus an unrecognized deletion or move under `kgme/` passes the fence. | Match the installed patch grammar, inspect both move endpoints, and reject unrecognized operations. Add mixed allowed/forbidden patch cases. |
| F4 | blocking | kgme/hermes_fence.py:144 | Any executable whose basename is `kgme` receives the dispatch exemption, including `/tmp/kgme`. Hermes can create that executable outside the protected root and invoke it inside KGME to perform arbitrary writes. | Restrict dispatch to the trusted KGME executable and supported launcher forms; resolve executable paths and symlinks before authorization. |
| F5 | blocking | tests/test_hermes_fence.py:198 | The added hook-renamed acceptance case has neither a corresponding test nor stated live evidence. This test removes the interpreter while retaining the wrapper; it does not establish that Hermes blocks when the hook script itself cannot start. | Add coverage through Hermes’s hook dispatcher with the script absent, or record the specified live acceptance result. |
| F6 | cosmetic | kgme/hermes_fence.py:81 | The new module is 336 lines and mixes filesystem effects into `resolve`, `touches`, `judge_terminal` and `decide`, without ADR-015’s effect naming or separation from policy logic. | Extract filesystem and entry-point effects into `read_*` / `run_*` helpers and keep policy decisions pure. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | kgme/hermes_fence.py:296 | The fence treats the hook’s `cwd` as the tool’s working directory. Installed Hermes supplies its **process** directory, while terminal and file tools use a separate session directory. After a session enters KGME from elsewhere, a relative `write_file("kgme/cli.py")` can therefore pass as outside KGME. | Obtain the authoritative session directory for each call, and refuse ambiguous relative targets. Add coverage where process and session directories differ. |
| F2 | blocking | kgme/hermes_fence.py:193 | Directory tracking assumes every `cd` executes successfully and discards shell control flow. From the repository, `cd /dev/null; rm kgme/cli.py` passes inspection because the simulated directory becomes `/dev/null`; the real `cd` fails and the deletion executes in the repository. | Preserve execution semantics or conservatively check subsequent commands against every possible directory. Add failed, skipped and piped `cd` cases. |
| F3 | blocking | kgme/hermes_fence.py:61 | The patch recognizer misses Hermes’s supported `***Delete File:` spelling and `*** Move File: source -> destination` operation. A patch containing 1 recognized proposal edit plus an unrecognized deletion or move under `kgme/` passes the fence. | Match the installed patch grammar, inspect both move endpoints, and reject unrecognized operations. Add mixed allowed/forbidden patch cases. |
| F4 | blocking | kgme/hermes_fence.py:144 | Any executable whose basename is `kgme` receives the dispatch exemption, including `/tmp/kgme`. Hermes can create that executable outside the protected root and invoke it inside KGME to perform arbitrary writes. | Restrict dispatch to the trusted KGME executable and supported launcher forms; resolve executable paths and symlinks before authorization. |
| F5 | blocking | tests/test_hermes_fence.py:198 | The added hook-renamed acceptance case has neither a corresponding test nor stated live evidence. This test removes the interpreter while retaining the wrapper; it does not establish that Hermes blocks when the hook script itself cannot start. | Add coverage through Hermes’s hook dispatcher with the script absent, or record the specified live acceptance result. |
| F6 | cosmetic | kgme/hermes_fence.py:81 | The new module is 336 lines and mixes filesystem effects into `resolve`, `touches`, `judge_terminal` and `decide`, without ADR-015’s effect naming or separation from policy logic. | Extract filesystem and entry-point effects into `read_*` / `run_*` helpers and keep policy decisions pure. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix: **`5821df73927dfa4b`**, matching `review.sha`.

F1 is supported by installed Hermes’s `agent/shell_hooks.py:87`, `tools/terminal_tool.py:1086` and `tools/file_tools_paths.py:305`. F3 is supported by `tools/patch_parser.py:54`. These source files were read directly; no secrets were read.

Acceptance items 1–3 and the proposal-write case have fixture coverage. Item 4 has mocked attribution coverage across all 4 event writers. Item 5 has a role-lint test and reported lint success. The report explicitly leaves live acceptance outstanding.

No tests were run or files changed. Sandbox/tooling failures were not counted against the diff. The 4 installation artifacts remain outside the reviewed patch in scratch storage. No new Python dependency, `TODO` or `shell=True` was found.
