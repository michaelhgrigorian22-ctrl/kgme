---
id: AUDIT-0022
type: report
status: final
handoff: HANDOFF-0031
author: claude-code
source: fetched
origin: this repository, `kgme lint` and `make check` output of 2026-09-20, the review audits under docs/audit/
tier: 2
created: 2026-09-20T15:40:00-07:00
period: 2026-09-20
---

# HANDOFF-0031 — the schema validator and `make check`, and the close of HANDOFF-0030

Per HANDOFF-0031, adopted by Michou 2026-09-20 under his standing word through 0034. The handoff named this file with the 18th; the local date is the 20th. The validator is the reference example of ADR-015's ten-minute standard, so its modules are short and its tables read like the schema.

## What was built
| Path | Purpose | Lines |
|---|---|---|
| `kgme/schema.py` | schema v1.3 as data: the ten types, folders, status vocabularies, type-specific fields, required and known fields, id families, the instant and date shapes, the provenance cutoff | 136 |
| `kgme/frontmatter.py` | pure: `split_frontmatter`, `load_yaml` through a `SafeLoader` subclass that leaves instants as strings, with a walk over the composed node tree that refuses a key named twice in one mapping (bare, quoted, flow style, through an alias, or inside a merge source) before anything is constructed, `parse_frontmatter` | 102 |
| `kgme/lint.py` | pure: `lint_note` (every rule, each finding classed; a non-string key is a finding, not a crash), `lint_files` (id uniqueness across a run; an exception becomes a blocking finding), `counts` | 236 |
| `kgme/vault.py` | effects: `read_notes` over the roots minus the exemptions, sorted, repo-relative, each file once however the roots overlap; a root that is not a directory raises | 44 |
| `kgme/cli.py` | `kgme lint [--root PATH ...] [--base DIR] [--include-cosmetic]`: one line per finding, a summary, exit 1 on any blocking, exit 2 on a root that does not exist | +47 |
| `tools/schema/lint.py` | the entry point the schema names; calls `kgme lint` | 14 |
| `kgme.toml` `[lint]` | roots, exempt paths (the schema's Scope table), skipped directory names | +5 |
| `tests/test_lint.py`, `tests/fixtures/vault/` | nine tests; 22 fixture notes, one per violation class, each asserted to yield exactly its planted finding, plus inline notes for the review's cases (null instants, unnamed provenance, quoted and flow duplicates, boolean keys, overlapping roots, a missing root, a one-line YAML error) | 198 + 22 files |
| `docs/schema-v1.md` | v1.3: the dated provenance clause (Michou's approved diff) | +4 |
| `docs/README.md` | its frontmatter block, `id: DOCS-README` (0030 item 5, approved) | +10 |
| `docs/corrections.md` | the v1.3 schema-version record | +5 |

## The first dry run, and what each finding became
`kgme lint` over the real roots before any repair: 92 notes, 27 blocking, 17 advisory, 6 cosmetic.

| Blocking findings | Files | Resolution |
|---|---|---|
| no frontmatter | `docs/README.md` | 0030 item 5: the block Cowork proposed, applied as Michou's approved diff |
| `modified` not an instant | `docs/STATUS.md` | the builder's own error of that morning (a timestamp written without seconds); corrected |
| `created` not an instant | six review audits AUDIT-0015 to 0021 | milliseconds from the ledger's clock; the regex now accepts fractional seconds, which ISO 8601 with an offset allows, and `kgme review` writes whole seconds from here on |
| report without `period`; `fetched` without `origin`; `inferred` without `sources` | the ten Phase 0 reports, 19 findings | schema v1.3 on Michou's ruling: reports created before 2026-09-14 are held to the fields that existed when written; the rule moved, the records did not |

After the repairs: 95 notes (the three audits this handoff adds included), 0 blocking, 20 advisory, 6 cosmetic. The advisories, for the weekly review: `accepted` on ADR-019 and `supersedes` entries there that YAML read as mappings; `reason` on seven proposals; `review_cycle`, `reviewer`, `verdict`, `open_blocking` on eight review audits; `email` and `name` on the git-identity handoff; two ids outside the named families (`FRICTION-LOG`, `DOCS-README`). Candidates for v1.4's named extras and singletons. Six files carry trailing whitespace; `kgme lint --include-cosmetic` lists them.

## Acceptance test (HANDOFF-0031)
| Check | Result |
|---|---|
| `kgme lint` on `memory/` and `docs/` exits 0 | pass, after the repairs above |
| the fixture directory yields exactly one finding per planted violation with the expected class | pass: 22 files, 14 blocking, 2 advisory, 1 cosmetic, and the valid, pre-cutoff, and fractional-second files yield nothing |
| `make check` green end to end | pass, 123 tests |
| under two minutes | pass, six seconds |

## HANDOFF-0030, closed
Its acceptance was `kgme lint` exiting 0 with no ADR modified: `git diff --stat docs/adr/` is empty in this diff, and the two repairs it foresaw, the README block and a schema rule for what the record could not satisfy, are done. Status set to done in this commit.

## Review loop
Every cycle was run by `kgme review` on the staged diff; the cycle records are its audit files. Reviewer `gpt-6-astra`; no finding went to the arbiter.

| Cycle | Record | Diff | Verdict | What it found and what changed |
|---|---|---|---|---|
| 1 | AUDIT-0023 | `36b3d021b0203fc3` | BLOCK, 6 blocking, 2 cosmetic | Required timestamps accepted null; provenance was tested by truthiness; the duplicate-key scan over raw text missed quoted keys; a bare `on:` key became a boolean and crashed the run when unknown keys were sorted; a mistyped `--root` was skipped silently and exited 0; overlapping roots read a file twice and reported it as its own duplicate; YAML errors put newlines in a finding line; three docstrings still said v1.2. All accepted. Fixed: null refused except a task's `due`; `origin` and every `sources` entry must be a non-empty string; the loader refuses a constructed key seen twice; a non-string key is a blocking finding and the scan continues, and any exception in one note becomes a blocking finding; a missing root exits 2; files are read once by resolved path; finding lines collapse whitespace; docstrings updated. |
| 2 | AUDIT-0024 | `98eea2978ad8ac19` | BLOCK, 1 blocking | Seven rows verified closed. F3 survived in one shape: the check ran inside `construct_mapping`, after SafeLoader had folded a merge source (`<<`) into its parent, so `<<: {status: active, "status": draft}` kept `draft` unseen. Fixed: the check runs once over the composed node tree before anything is constructed, each mapping as written, merge sources checked as mappings of their own, a note's own key still overriding a merged one. The YAML half moved whole into `kgme/frontmatter.py` (102 lines) to keep `kgme/lint.py` (236) under the cap. |
| 3 | AUDIT-0025 | `8ed1187786e3eebf` | **PASS** | Eight rows verified closed, the merge case, merge lists, aliases, and overrides covered; no new findings. |

Strikes under the bound: F3 stood blocking for two consecutive cycles and closed on the third; no halt, no arbitration, no override. Three cycles, 17 minutes of reviewer time in all.

## Deviations, stated
- The datetime check runs on a string kept raw by a `SafeLoader` without the timestamp resolver, rather than by a second scan of the frontmatter text; same guarantee, one code path. The regex accepts an optional fractional second.
- `--base` was added so the fixture vault lints under its own folder rules; exemptions resolve against it.
- Folder by type is blocking; an author under the wrong kind of folder is advisory, since v1.2's validation sentence names the type only.
- Report filename carries the local date; 0031's proposal guessed the 18th.

## Needs from Michou, closed
The README block and the v1.3 clause were his two rulings of the day.

## Next
HANDOFF-0032, canary tests and worker manifests; its reviews run through `kgme review`, and its diff carries the two advisories left on `tests/test_hooks.py` by AUDIT-0021.
