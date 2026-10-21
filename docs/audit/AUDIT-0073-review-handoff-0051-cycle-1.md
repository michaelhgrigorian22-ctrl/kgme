---
id: AUDIT-0073
type: report
status: final
handoff: HANDOFF-0051
author: codex
source: inferred
sources: ["HANDOFF-0051", "staged diff sha256 82fc8efb0860698a450d957bf1005fd2c022edadaa7ad78a6060685910e96b40"]
tier: 2
created: 2026-10-21T13:09:01-07:00
period: 2026-10-21
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4, F5, F6]
---

# Review of HANDOFF-0051, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `82fc8efb0860698a450d957bf1005fd2c022edadaa7ad78a6060685910e96b40`. Verdict **BLOCK**: blocking 6, transient 0, cosmetic 0, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/atlas_read.py:76` | The containment check covers `atlas/` but not its children. With `atlas/module` symlinked to another directory, lines 83–89 read and replace files outside `atlas/`, violating What §1. The test covers only a symlink at the atlas root. | Check every destination’s ancestry before reading or writing. Add a nested-directory symlink test proving the external directory remains unchanged. |
| F2 | blocking | `kgme/atlas_read.py:64` | The Tier 1 check validates the project root, but `README.md.is_file()` and `read_text()` follow symlinks. An otherwise permitted project can therefore read a README pointing into Tier 1 or another forbidden file, bypassing ADR-002. | Read the README through the existing regular-file, no-symlink helper. Add a test using a synthetic protected destination. |
| F3 | blocking | `control/git-hooks/post-commit:33` | The atlas command is below the main-only exit at line 20. Commits on `design` or another branch never regenerate the atlas, contrary to regeneration after every commit. Existing hook tests explicitly preserve this behavior. | Keep pushing restricted to `main`, but run local atlas regeneration on other branches too. Test the two commands separately and verify atlas generation after a commit. |
| F4 | blocking | `kgme/atlas_read.py:29` | Folder nodes derive exclusively from files passing `READ_ROOTS`. Consequently, the existing `memory/`, `logs/`, and `cockpit/` folders cannot appear, despite What §1 requiring every top-level folder. | Derive folder inventory from tracked paths independently of content-reading filters. Test folders containing no eligible source files. |
| F5 | blocking | `kgme/atlas.py:215` | Outputs link only to files already assigned recognized nodes. HANDOFF-0034 therefore loses 4 explicitly named output links: `jobs/brief/job.md` and its 3 memory templates. The fixture tests only Python output links. | Represent and link the existing files named in Outputs, including non-code files. Add assertions for these 4 concrete outputs. |
| F6 | blocking | `kgme/atlas_read.py:58` | Relative project paths resolve against the process’s working directory, ignoring `base`. Thus `projects = ["../design"]` can select a different directory or fail depending on where `kgme atlas` is invoked. This also bypasses ADR-015’s centralized path handling. | Resolve configured paths through `kgme.paths` against `base`. Test identical results from 2 different working directories. |
| F7 | advisory | `docs/audit/2026-10-21-atlas.md:55` | Acceptance evidence remains incomplete. ADR-019 is demonstrated through a 3-edge route, rather than a direct HANDOFF-0034 link; post-commit timing and the opened graph view are explicitly pending. The report also describes 3 configuration/document changes as unapplied although this patch includes them. | Reconcile the ADR-019 interpretation with the handoff, update the report to the reviewed state, and record the remaining integration and visual evidence. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/atlas_read.py:76` | The containment check covers `atlas/` but not its children. With `atlas/module` symlinked to another directory, lines 83–89 read and replace files outside `atlas/`, violating What §1. The test covers only a symlink at the atlas root. | Check every destination’s ancestry before reading or writing. Add a nested-directory symlink test proving the external directory remains unchanged. |
| F2 | blocking | `kgme/atlas_read.py:64` | The Tier 1 check validates the project root, but `README.md.is_file()` and `read_text()` follow symlinks. An otherwise permitted project can therefore read a README pointing into Tier 1 or another forbidden file, bypassing ADR-002. | Read the README through the existing regular-file, no-symlink helper. Add a test using a synthetic protected destination. |
| F3 | blocking | `control/git-hooks/post-commit:33` | The atlas command is below the main-only exit at line 20. Commits on `design` or another branch never regenerate the atlas, contrary to regeneration after every commit. Existing hook tests explicitly preserve this behavior. | Keep pushing restricted to `main`, but run local atlas regeneration on other branches too. Test the two commands separately and verify atlas generation after a commit. |
| F4 | blocking | `kgme/atlas_read.py:29` | Folder nodes derive exclusively from files passing `READ_ROOTS`. Consequently, the existing `memory/`, `logs/`, and `cockpit/` folders cannot appear, despite What §1 requiring every top-level folder. | Derive folder inventory from tracked paths independently of content-reading filters. Test folders containing no eligible source files. |
| F5 | blocking | `kgme/atlas.py:215` | Outputs link only to files already assigned recognized nodes. HANDOFF-0034 therefore loses 4 explicitly named output links: `jobs/brief/job.md` and its 3 memory templates. The fixture tests only Python output links. | Represent and link the existing files named in Outputs, including non-code files. Add assertions for these 4 concrete outputs. |
| F6 | blocking | `kgme/atlas_read.py:58` | Relative project paths resolve against the process’s working directory, ignoring `base`. Thus `projects = ["../design"]` can select a different directory or fail depending on where `kgme atlas` is invoked. This also bypasses ADR-015’s centralized path handling. | Resolve configured paths through `kgme.paths` against `base`. Test identical results from 2 different working directories. |
| F7 | advisory | `docs/audit/2026-10-21-atlas.md:55` | Acceptance evidence remains incomplete. ADR-019 is demonstrated through a 3-edge route, rather than a direct HANDOFF-0034 link; post-commit timing and the opened graph view are explicitly pending. The report also describes 3 configuration/document changes as unapplied although this patch includes them. | Reconcile the ADR-019 interpretation with the handoff, update the report to the reviewed state, and record the remaining integration and visual evidence. |

## Verdict

BLOCK with 6 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`82fc8efb0860698a`**, verified before and after inspection. No files were changed and no tests were run. Git’s sandbox cache warnings were treated solely as tooling limits.

The 2 new implementation modules contain 249 and 124 lines, separate logic from effects, and provide module docstrings covering purpose, inputs, outputs, and side effects. No new dependencies, added `TODO`, or `shell=True` were found; subprocess calls use argument lists.

Tests cover deterministic regeneration, several required graph links, and git exclusion. The report states 271 notes generated in 0.29 seconds; that evidence was read, not independently reproduced.
