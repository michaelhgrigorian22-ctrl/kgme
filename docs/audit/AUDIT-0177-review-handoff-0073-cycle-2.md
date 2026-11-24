---
id: AUDIT-0177
type: report
status: final
handoff: HANDOFF-0073
author: codex
source: inferred
sources: ["HANDOFF-0073", "staged diff sha256 b6aa17331f0861f8106731bbaf3c2e8a00be5de6af879e8ef3f14e481f7966b1"]
tier: 2
created: 2026-11-23T14:02:35-08:00
period: 2026-11-23
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F2, F5, F7, F8, F9]
---

# Review of HANDOFF-0073, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `b6aa17331f0861f8106731bbaf3c2e8a00be5de6af879e8ef3f14e481f7966b1`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/hermes_fence.py:434 | Unknown terminal directories now receive strict checks, and relative write targets are refused. Tests cover differing process and session directories. | No further fix for the original finding. |
| F2 | blocking | kgme/hermes_fence.py:444 | Directory changes are detected in raw command text. With the process outside KGME and absolute `workdir` set to the home directory, `c''d Projects; c''d KGME; c''d brain; rm kgme/cli.py` passes: no individual argument resolves inside KGME from the initial directory, and the regex misses the quoted `cd` spellings. The shell executes all 3 directory changes. | Detect directory-changing commands after quote removal, and refuse syntax whose directory effects remain uncertain. Add this outside-to-inside case. |
| F3 | blocking, resolved | kgme/hermes_fence.py:294 | The recognizer matches the installed V4A markers, checks both move endpoints, and refuses unknown operations. Mixed-operation coverage addresses the original grammar omissions. | No further grammar fix. F9 concerns endpoint resolution separately. |
| F4 | blocking, resolved | kgme/hermes_fence.py:455 | Dispatch now selects the brain’s resolved executable or the constrained launcher form. Tests reject impostor executables and wrong projects. | No further fix for the original finding. |
| F5 | blocking | docs/audit/AUDIT-0176-hermes-conductor.md:61 | The required live evidence remains absent. The installer contains 3 dispatcher probes, but the reported run used a stand-in `hermes`; the staged test still removes only the interpreter. Neither establishes the installed dispatcher’s hook-renamed behavior. | Run the prepared probes against installed Hermes and quote their actual results in the report, as the ruling requires. |
| F6 | cosmetic | kgme/hermes_fence.py:616 | Policy decisions are now pure, but the module has grown to 672 lines, and effectful `decide` still lacks an effect prefix. The test module is also 397 lines. | Split parsing, policy and effects into focused modules near ADR-015’s 300-line guideline; rename the effectful entry function. |
| F7 | blocking | kgme/hermes_fence.py:507 | Only `rg --pre` is excluded. An inside call such as `rg --hostname-bin=/tmp/helper --hyperlink-format=default --color=always x README.md` passes and can execute `/tmp/helper`. Installed `rg --help` explicitly documents this execution behavior. The clean environment does not prevent it. | Restrict accepted options to verified read-only behavior, including refusing `--hostname-bin`. Add a harmless executable-launch regression case. |
| F8 | blocking | kgme/hermes_fence.py:157 | Containment compares case-sensitive `Path` components. On this filesystem, `Projects/KGME` and `Projects/kgme` identify the same directory, but the installed Python’s `os.path.realpath` preserves non-symlink component spelling. An absolute `write_file` target through lowercase `Projects/kgme/brain/kgme/cli.py` is therefore classified outside and allowed. | Resolve containment using filesystem identity or canonical on-disk component names, including existing ancestors of new files. Cover case aliases on macOS. |
| F9 | blocking | kgme/hermes_fence.py:382 | Every patch target is fully dereferenced. Hermes instead preserves the final symlink for Delete and Move (`tools/file_tools.py:166–171`). A protected repository symlink pointing outside is consequently authorized as an outside target, although deletion or movement modifies the repository entry itself. | Retain operation types and check entry paths for Delete and Move, resolving their parents while preserving the final component. Add protected-symlink cases. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | kgme/hermes_fence.py:434 | Unknown terminal directories now receive strict checks, and relative write targets are refused. Tests cover differing process and session directories. | No further fix for the original finding. |
| F2 | blocking | kgme/hermes_fence.py:444 | Directory changes are detected in raw command text. With the process outside KGME and absolute `workdir` set to the home directory, `c''d Projects; c''d KGME; c''d brain; rm kgme/cli.py` passes: no individual argument resolves inside KGME from the initial directory, and the regex misses the quoted `cd` spellings. The shell executes all 3 directory changes. | Detect directory-changing commands after quote removal, and refuse syntax whose directory effects remain uncertain. Add this outside-to-inside case. |
| F3 | blocking, resolved | kgme/hermes_fence.py:294 | The recognizer matches the installed V4A markers, checks both move endpoints, and refuses unknown operations. Mixed-operation coverage addresses the original grammar omissions. | No further grammar fix. F9 concerns endpoint resolution separately. |
| F4 | blocking, resolved | kgme/hermes_fence.py:455 | Dispatch now selects the brain’s resolved executable or the constrained launcher form. Tests reject impostor executables and wrong projects. | No further fix for the original finding. |
| F5 | blocking | docs/audit/AUDIT-0176-hermes-conductor.md:61 | The required live evidence remains absent. The installer contains 3 dispatcher probes, but the reported run used a stand-in `hermes`; the staged test still removes only the interpreter. Neither establishes the installed dispatcher’s hook-renamed behavior. | Run the prepared probes against installed Hermes and quote their actual results in the report, as the ruling requires. |
| F6 | cosmetic | kgme/hermes_fence.py:616 | Policy decisions are now pure, but the module has grown to 672 lines, and effectful `decide` still lacks an effect prefix. The test module is also 397 lines. | Split parsing, policy and effects into focused modules near ADR-015’s 300-line guideline; rename the effectful entry function. |
| F7 | blocking | kgme/hermes_fence.py:507 | Only `rg --pre` is excluded. An inside call such as `rg --hostname-bin=/tmp/helper --hyperlink-format=default --color=always x README.md` passes and can execute `/tmp/helper`. Installed `rg --help` explicitly documents this execution behavior. The clean environment does not prevent it. | Restrict accepted options to verified read-only behavior, including refusing `--hostname-bin`. Add a harmless executable-launch regression case. |
| F8 | blocking | kgme/hermes_fence.py:157 | Containment compares case-sensitive `Path` components. On this filesystem, `Projects/KGME` and `Projects/kgme` identify the same directory, but the installed Python’s `os.path.realpath` preserves non-symlink component spelling. An absolute `write_file` target through lowercase `Projects/kgme/brain/kgme/cli.py` is therefore classified outside and allowed. | Resolve containment using filesystem identity or canonical on-disk component names, including existing ancestors of new files. Cover case aliases on macOS. |
| F9 | blocking | kgme/hermes_fence.py:382 | Every patch target is fully dereferenced. Hermes instead preserves the final symlink for Delete and Move (`tools/file_tools.py:166–171`). A protected repository symlink pointing outside is consequently authorized as an outside target, although deletion or movement modifies the repository entry itself. | Retain operation types and check entry paths for Delete and Move, resolving their parents while preserving the final component. Add protected-symlink cases. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `b6aa17331f0861f8`.

No files were changed and no tests were run. Findings derive from the patch, installed Hermes and Python source, installed ripgrep help, and read-only filesystem inspection. Sandbox failures were not counted against the diff.

The 5 original acceptance items have repository-side coverage for refusal, dispatch selection, attribution and role linting. Actual Hermes dispatch remains unverified; the added hook-renamed acceptance remains open under F5.

The staged report still describes cycle-1 behavior, including allowing `cd` and command joiners, and cites 64 tests. Update it to match cycle 2 before landing. The audit-ID collision remains deferred under the existing ruling.
