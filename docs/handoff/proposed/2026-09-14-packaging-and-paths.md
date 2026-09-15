---
id: HANDOFF-0025
type: handoff
created: 2026-09-14T22:25:00-07:00
from: claude-code
to: claude-code
tier: 2
status: proposed
depends_on: null
plan_ref: PLAN-PHASE-1 step 0
---

# Handoff 0025 (proposed) — Packaging, paths, and the review-loop protocol

## Why
Nothing in the original Phase 1 plan creates the project that every later step assumes. ADR-015 requires Python 3.13 through `uv` with a committed `uv.lock`, all configuration in one root TOML, all paths from one `paths.py`, and a `make check` target; step 3 of the plan invokes `make check` with no Makefile in the repository. Every hook, job, and test in Phase 1 runs through `uv run --project`, which needs a `pyproject.toml` to exist. This is step 0 of the amended plan (AUDIT-0011). It also fixes the review protocol every later handoff uses, because this handoff is itself the first thing reviewed under it.

## What
1. `pyproject.toml` at the root: `[project] name = "kgme"`, `requires-python = ">=3.13"`, `[project.scripts] kgme = "kgme.cli:main"`, runtime dependency `pyyaml` pinned (Michou's ruling 2026-09-14: `safe_load` only), dev dependencies `ruff` and `pytest` pinned. Record each with what, why, source, version in the ADR-015 dependency line of this handoff's report.
2. `uv lock`; commit `uv.lock`. `uv sync --frozen` is the only install path.
3. `kgme.toml` at the root: `[paths]` (vault, ledger_dir, ledger_test_dir, scratch_dir, payloads_dir, tier1_paths as absolute strings), `[cockpit] host = "127.0.0.1", port = 8642`, `[clean]` named targets and allowlist roots, `[hooks]` blocklist patterns.
4. `kgme/__init__.py`, `kgme/paths.py` (every path derived from `KGME_HOME`, the repo root, and `kgme.toml`; no other module reads config), `kgme/config.py` (`tomllib`, stdlib), `kgme/cli.py` (`argparse`; subcommands `brief`, `clean`, `lint`, `review`, `cockpit`, `ledger`, each a stub that prints "not built: HANDOFF-00NN").
5. `Makefile` with `check`: `uv sync --frozen`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run kgme lint` (no-op until 0031), `uv run pytest tests/ -m "not agents"`. A second target `canary-agents` is a placeholder until 0032.
6. `docs/readers/review-loop.md`: the protocol. Builder stages the diff, runs `make check`, writes `git diff --staged` to `logs/scratch/review.patch`; reviewer is `codex exec -s read-only -m gpt-6-astra --json` with a fixed prompt that requires an ADR-016 class on every finding; findings go to `docs/audit/AUDIT-NNNN.md`. A `blocking` finding opens a fix-and-re-review cycle on the new diff hash. If builder and reviewer disagree on whether a finding is blocking, one model from the other lab arbitrates once (Opus 5 when Codex reviewed). Bound per ADR-016 and the 2026-09-11 lesson: strikes count distinct blocking root causes, tooling failures (sandbox network, 429s, curl 000) never count, halt at three distinct unresolved blocking root causes or three cycles on one. A halt sends Michou the ADR-016 escalation packet and nothing proceeds until he answers. The commit binds to the reviewed hash.
7. `.gitignore`: add `logs/ledger-test/` and `logs/scratch/payloads/` (already covered by `logs/scratch/`; state it).
8. `CLAUDE.md` repository map: add one line `kgme/  the Python package: paths, config, ledger, events, cli` under `tools/`. Show the diff; Michou approves before it is written (charter §6).
9. `~/.zshrc`: rename `alias kgme='cd "$KGME_HOME"'` to `alias kgh='cd "$KGME_HOME"'` (Michou's ruling 2026-09-14; the name defaults to `kgh` until he names another). Show the one-line diff; Michou approves; `source ~/.zshrc`.

## Outputs
`pyproject.toml`, `uv.lock`, `kgme.toml`, `Makefile`, `kgme/{__init__,paths,config,cli}.py`, `docs/readers/review-loop.md`, `.gitignore` (two lines), `CLAUDE.md` (one line, approved), `~/.zshrc` (one line, approved).

## Acceptance test (under three minutes)
From a clean checkout: `uv sync --frozen` succeeds; `make check` exits 0 with empty targets; `kgme --help` lists the six subcommands; `kgh && pwd` prints the repo path; `type kgme` resolves to `.venv/bin/kgme`, not an alias.

## Reviewer
Codex (`gpt-6-astra`), under the protocol this handoff writes. First use of the loop.

## Reversibility
`git revert` of the commit removes every repo file. The `~/.zshrc` line is restored by hand from the diff shown. `.venv/` is deleted with `rm -rf .venv` by Michou (the global deny applies to agents; `kgme clean venv` exists from 0033).

## Needs from Michou
Approval of the CLAUDE.md line and the alias rename diff; a different alias name if `kgh` is wrong; objection to `pytest` if he prefers `unittest` (one fewer dependency).

## Report
`docs/audit/2026-09-15-packaging.md` (next AUDIT id): versions and hashes of the three pinned dependencies, `make check` output, the two approved diffs. Set `status: done`, `completed:`. Commit `build: packaging, paths, review-loop protocol (HANDOFF-0025)`.
