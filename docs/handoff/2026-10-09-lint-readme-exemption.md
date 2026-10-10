---
id: HANDOFF-0041
type: handoff
created: 2026-10-09T22:33:00-07:00
from: cowork
to: claude-code
tier: 2
status: done
completed: 2026-10-09T22:36:40-07:00
depends_on: [HANDOFF-0031]
---

# Handoff 0041 — `kgme lint`: `README.md` is an index, exempt by name (schema v1.4)

## Why
Your note of 2026-10-09 (`logs/scratch/note-to-design-cowork.md`) found four schema findings in `docs/handoff/cockpit-design/`, two of them blocking `make check` for every track. Minutes later Codex's CDH-0001 added `docs/design/cockpit-v0/chibi/README.md`, a third README with the same disease: an index file in a folder where no `note` may live. Michou ruled the same evening (Cowork's recommendation adopted): such files stay where they are, beside what they index, and `README.md` is exempt by name — the charter precedent in schema §Scope — rather than moved to `docs/readers/`. Cowork has written the ruling into `docs/schema-v1.md` v1.4 (Scope row, `CDH-NNNN` / `AUDIT-CDH-NNNN` id families, changelog) and removed `author: codex` from CDH-0002. This handoff makes the validator agree with the schema.

## Do
1. `kgme/vault.py`, `is_exempt`: also return `True` for any file named `README.md`. A rule in code, not a `kgme.toml [lint] exempt` entry: the toml is in flight under HANDOFF-0040, and a name rule needs no entry per folder. `is_exempt` keeps its signature; nothing else about exemptions changes. `docs/README.md` keeps its frontmatter and is simply no longer walked.
2. `kgme/schema.py`, `ID_FAMILIES`: add `^CDH-\d{4}$` and `^AUDIT-CDH-\d{4}$`.
3. `kgme/lint.py` docstring: v1.3 → v1.4.
4. `tests/test_lint.py`, one deterministic test under tmp paths like the existing exemption test: a planted `docs/handoff/some-track/README.md` and a planted `docs/design/x/README.md`, both without frontmatter, are skipped; a planted `docs/handoff/some-track/index.md` with the same content is still reported; a note with `id: CDH-0007` draws no `id-format` finding.
5. `docs/handoff/cockpit-design/2026-10-09-chibi-cast-implementation.md`: if its `status` is `done` when you run, delete the single line `author: codex` and change nothing else. If it is still `open` (Codex is executing CDH-0001), leave it untouched and report it as the one remaining blocking line; Cowork removes it at CDH-0002.
6. `make check`.

## Don't
Touch `kgme.toml`, anything under `docs/design/`, the chibi assets, `docs/handoff/cockpit-design/` beyond step 5, or any HANDOFF-0040 file. Don't rename, move, or add frontmatter to any README. Don't edit `docs/schema-v1.md` further; if the rule you implement differs from its v1.4 Scope row, say so in the report and stop.

## Report
`docs/audit/2026-10-09-lint-readme-exemption.md`: `type: report`, next free `AUDIT-NNNN`, `handoff: HANDOFF-0041`, `period: 2026-10-09`, `source: inferred` with `sources`. Contents: `kgme lint` output before and after (blocking and advisory counts), the new test's result, the tail of `make check`, and the step-5 outcome.

## Commit
By pathspec only: `kgme/vault.py kgme/schema.py kgme/lint.py tests/test_lint.py docs/schema-v1.md docs/handoff/2026-10-09-lint-readme-exemption.md docs/audit/2026-10-09-lint-readme-exemption.md`, plus the CDH-0001 file only if step 5 applied. Message: `lint: README exempt by name, schema v1.4 (HANDOFF-0041)`. The post-commit hook pushes; that is expected on this track. Leave the 0040 staged work and every design-track file uncommitted. Then set this file's `status: done` and add `completed:`.

## Acceptance
`uv run kgme lint` exits 0, or reports exactly one blocking finding (CDH-0001's `author` line, step 5 deferred); the new test passes; `make check` is green or red only on that line; no file outside the pathspec changed.
