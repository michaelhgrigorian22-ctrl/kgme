---
id: HANDOFF-0031
type: handoff
created: 2026-09-14T22:25:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0025, HANDOFF-0030]
plan_ref: PLAN-PHASE-1 step 6
---

# Handoff 0031 (proposed) — The schema validator and `make check`

## Why
`schema-v1.md` line 80 names the validator as the first code artefact; ADR-013 §Consequences agrees. It moved behind packaging and the ledger for dependency reasons stated in AUDIT-0011, and behind 0030 because without the v1.2 rules it fails on `docs/` on day one. It is the reference example of ADR-015's ten-minute standard.

## What
1. `kgme/lint.py` (pure): `parse_frontmatter(text) -> tuple[dict, str]` using `yaml.safe_load`; `lint_note(text, path, ids_seen) -> list[Finding]`; `Finding(path, rule, class, message)` with ADR-016 classes (missing field, bad date, duplicate id, wrong folder: `blocking`; trailing whitespace: `cosmetic`).
2. `kgme/vault.py` (effects): `read_notes(roots) -> list[tuple[Path, str]]` over `memory/` and `docs/`, skipping `memory/templates/`, `memory/attachments/`, `.obsidian/`, and `docs/archive/`.
3. Checks exactly as `schema-v1.md` v1.2 §Validation and §Scope enumerate (committed 2026-09-14 under HANDOFF-0030: exempt paths skipped, `handoff` uses `from` and needs no `source`, append-only types need no `modified`, unknown fields and id-format drift are `advisory`), plus folder-by-type. **Michou's note (2026-09-14):** `yaml.safe_load` turns ISO datetimes into `datetime` objects, so the offset regex must run on the raw frontmatter string, or the value must be re-serialized with `isoformat()` before the check; a naive `datetime` (no `tzinfo`) is a `blocking` finding. The v1.2 rules in detail: frontmatter present and parseable; required fields per type; `id` unique across both roots; `type` in the ten; `created` (and `modified` where required) match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$`; type-specific fields; `fetched` has `origin`; `inferred` has `sources`; folder allowed for type and author.
4. `tools/schema/lint.py` as the thin entry point; `kgme lint [--root PATH ...] [--include-cosmetic]`; exit 1 on any `blocking` finding; one line per finding: path, rule, class, message.
5. `Makefile` `check` target now runs `uv run kgme lint`.
6. `tests/test_lint.py` with a fixtures directory holding one note per violation class.

## Outputs
`kgme/lint.py`, `kgme/vault.py`, `tools/schema/lint.py`, `tests/test_lint.py`, `tests/fixtures/vault/` (about ten small files).

## Acceptance test (under two minutes)
`kgme lint` on `memory/` and `docs/` exits 0; the fixture directory yields exactly one finding per planted violation with the expected class; `make check` is green end to end.

## Reviewer
Codex under `kgme review`.

## Reversibility
`git revert`.

## Needs from Michou
Nothing, provided 0030 is done. The list of any `docs/` files the first dry run flags goes back to 0030.

## Report
`docs/audit/2026-09-18-validator.md`. Set `status: done`, `completed:`. Commit `schema: validator and make check (HANDOFF-0031)`.
