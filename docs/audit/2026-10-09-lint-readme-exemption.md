---
id: AUDIT-0042
type: report
status: final
handoff: HANDOFF-0041
author: claude-code
source: inferred
sources: ["HANDOFF-0041", "docs/schema-v1.md v1.4", "kgme lint output of 2026-10-09 before and after", "pytest tests/test_lint.py", "make check"]
tier: 2
created: 2026-10-09T22:36:40-07:00
period: 2026-10-09
---

# HANDOFF-0041 — `kgme lint`: `README.md` exempt by name, schema v1.4

Per HANDOFF-0041 (Cowork, 2026-10-09 22:33, pointed at by Michou the same evening), minutes after HANDOFF-0040 landed as `82737f7`.

## What changed
| Path | Change |
|---|---|
| `kgme/vault.py` `is_exempt` | returns `True` first for any file whose name is `README.md` (exact case); signature unchanged; nothing else about exemptions changes |
| `kgme/schema.py` `ID_FAMILIES` | `^CDH-\d{4}$` and `^AUDIT-CDH-\d{4}$` added |
| `kgme/lint.py` | docstring: v1.3 → v1.4 (the module docstring of `kgme/schema.py` still says v1.3; the handoff did not name it, so it is left as is) |
| `tests/test_lint.py` | `test_readme_is_exempt_by_name_and_cdh_ids_are_a_family`: under `tmp_path`, a planted `docs/handoff/some-track/README.md` and `docs/design/x/README.md` without frontmatter are skipped by `read_notes`; `docs/handoff/some-track/index.md` with the same content is still read and reports `frontmatter` blocking; `docs/readme.md` (lower case) is not exempt; `id: CDH-0007` and `id: AUDIT-CDH-0007` draw no `id-format` finding, `CDX-0007` does | pass |
| `docs/schema-v1.md` | Cowork's v1.4 text, committed with this handoff, unedited |

The rule implemented matches the v1.4 Scope row ("any `README.md`"): exemption by file name, in any folder, case exact.

## `kgme lint`, before and after
| | notes | blocking | advisory | cosmetic |
|---|---|---|---|---|
| before (22:38) | 120 | 4 | 40 | 6 |
| after | 117 | 1 | 35 | 6 |

The three notes no longer walked are `docs/README.md`, `docs/handoff/cockpit-design/README.md`, `docs/design/cockpit-v0/chibi/README.md`. The three blocking findings gone are the two on `docs/handoff/cockpit-design/README.md` (missing `modified`, folder) and the one on the chibi README (no frontmatter). The five advisory findings gone are the three id-format lines on `DOCS-README`, `INDEX-COCKPIT-DESIGN-HANDOFFS`, and the chibi README's id, and the two on `CDH-0001` and `CDH-0002` now that `CDH` is a family.

## Step 5
`docs/handoff/cockpit-design/2026-10-09-chibi-cast-implementation.md` is `status: open` (Codex is executing CDH-0001), so it is untouched. Its `author: codex` line is the one blocking finding `kgme lint` reports after this change; Cowork removes it at CDH-0002.

## `make check`
Tail of the run after the change:

```
docs/handoff/2026-09-11-finance-python-delete-regenerable.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/cockpit-design/2026-10-09-chibi-cast-implementation.md: required [blocking] a handoff carries `from`, never `author`
docs/handoff/cockpit-design/2026-10-09-chibi-cast-implementation.md: unknown-field [advisory] fields not named in the schema: adopted, adopted_by, design_track, model, verification
docs/handoff/cockpit-design/2026-10-09-chibi-cast-verification.md: unknown-field [advisory] fields not named in the schema: adopted, adopted_by, design_track
docs/handoff/proposed/2026-09-09-enable-application-firewall.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-finance-folder-disposal.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-install-gh-cli.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-install-homebrew.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-ssh-key-for-github.md: unknown-field [advisory] fields not named in the schema: reason
docs/handoff/proposed/2026-09-09-time-machine-destination.md: unknown-field [advisory] fields not named in the schema: reason
kgme lint: 117 notes, 1 blocking, 35 advisory, 6 cosmetic
make: *** [check] Error 1
make check exit=
```

Red only on that one line: the two `tests/test_lint.py` tests that assert the real tree carries no blocking finding (`test_the_real_vault_and_docs_carry_no_blocking_finding`, `test_cli_exit_codes`) and `tests/test_smoke.py`'s `lint` no-op assertion fail on it and on nothing else; `kgme lint` itself exits 1 on it. The new test passes. `ruff`, `ruff format`, `core.hooksPath`, and `hook-errors.jsonl` are green.

## Commit
By pathspec: `kgme/vault.py kgme/schema.py kgme/lint.py tests/test_lint.py docs/schema-v1.md docs/handoff/2026-10-09-lint-readme-exemption.md docs/audit/2026-10-09-lint-readme-exemption.md`; the CDH-0001 file not among them (step 5 deferred). The handoff file carries `status: done` and `completed:` inside the commit rather than after it, as every handoff in this repository does, so the record of the close is what is pushed. No file outside the pathspec was changed by this handoff; the design track's working-tree changes and HANDOFF-0033's and 0034's unstaged work were left as found. HANDOFF-0040 was already committed (`82737f7`) when this handoff arrived, so there was no 0040 staged work to leave.
