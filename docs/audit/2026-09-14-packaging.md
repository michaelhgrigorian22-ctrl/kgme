---
id: AUDIT-0012
type: report
status: final
handoff: HANDOFF-0025
author: claude-code
source: fetched
origin: this repository, staged diff sha256 33eb6a774380cb85, `make check` and `codex exec` output of 2026-09-14
tier: 2
created: 2026-09-14T23:20:00-07:00
period: 2026-09-14
---

# HANDOFF-0025 — Packaging, paths, and the review-loop protocol

Per HANDOFF-0025, adopted by Michou 2026-09-14 (`from: michou`, `status: open`). First code in the repository; first use of the review loop. Filename carries the local date (2026-09-14, 22:50 to 23:30 PDT), not the 2026-09-15 the proposal guessed; the corrections log's rule is the local date.

## What was built
| Path | Purpose | Lines |
|---|---|---|
| `pyproject.toml` | project, pins, `kgme` console script, `uv_build` backend with `module-root = ""` for the root-layout package, ruff and pytest config, five pytest markers (`agents` plus the four ADR-016 classes) | 41 |
| `uv.lock` | committed; `uv sync --frozen` is the only install path | generated |
| `.python-version` | `3.13`; uv-managed CPython 3.13.13 already on the machine | 1 |
| `kgme.toml` | `[paths]`, `[cockpit]`, `[clean]`, `[hooks]` (blocklist patterns, `read_only_tools` for the ADR-019 §2 stream rule), `[models]` (review-loop identifiers, Michou's ruling: here and in the reader, never in agent memory) | 47 |
| `kgme/__init__.py` | package docstring | 8 |
| `kgme/config.py` | `read_config()`, the one place configuration is read (effects, `read_*` per ADR-015) | 24 |
| `kgme/paths.py` | pure: `root()` from `__file__`, `resolve()`, one accessor per configured path taking the settings dict | 76 |
| `kgme/cli.py` | `argparse` skeleton, six subcommands; `lint` is a no-op exit 0 until 0031, the rest exit 2 naming their handoff | 52 |
| `tests/test_smoke.py` | eight tests, each with an ADR-016 class marker; includes a purity test on `paths.py` and a reader-versus-config sync test | 76 |
| `Makefile` | `check` (sync frozen, ruff check, ruff format check, `kgme lint`, pytest minus `agents`); `canary-agents` placeholder exiting 2 | 13 |
| `.gitignore` | `+ logs/trace/`, `logs/ledger-test/`, `logs/trace-test/` | 3 |
| `CLAUDE.md` | one repository-map line for `kgme/` (approved diff) | 1 |
| `~/.zshrc` | `alias kgme` renamed to `alias kgh`; a `kgme()` shell function added (approved; see Deviations) | 3 |

## Dependency record (ADR-015: what, why, source, pinned version)
| Package | Version | Kind | Why | Source |
|---|---|---|---|---|
| `pyyaml` | 6.0.3 | runtime | YAML frontmatter on every note; `safe_load` only (Michou's ruling 2026-09-14 over a hand-rolled parser) | PyPI |
| `ruff` | 0.16.7 | dev | lint and format, required by ADR-015 §Enforced mechanically | PyPI |
| `pytest` | 9.1.1 | dev | test runner; pulls `iniconfig` 2.3.0, `packaging` 26.3, `pluggy` 1.6.0, `pygments` 2.21.0 (and `colorama` on Windows only) | PyPI |
| `uv_build` | 0.11.7 | build backend | builds the editable install for the console script; uv's own backend, no third-party build tool; pinned exactly after review finding F3 | PyPI, same release line as the installed `uv` 0.11.7 |

Nine packages in `uv.lock` including `kgme` itself. Standard library covers TOML (`tomllib`), argument parsing, paths.

## Acceptance test (HANDOFF-0025)
| Check | Result |
|---|---|
| `uv sync --frozen` from a clean export of the staged index (`git checkout-index`) | pass; three pins installed |
| `make check` exits 0 with empty targets | pass, in the checkout and in the clean export; 8 passed in 0.02 s; ruff clean |
| `kgme --help` lists the six subcommands | pass |
| `kgh && pwd` prints the repo path in a fresh interactive zsh | pass |
| `type kgme` resolves to `.venv/bin/kgme`, not an alias | **deviation:** resolves to a shell function (see below); it is not the `cd` alias, and `kgme lint` works from `/tmp` |

## Review loop, first use
Reviewer `gpt-6-astra` via `codex exec -s read-only`, patch at `logs/scratch/review.patch`.

**Cycle 1** (diff `bdb5830619bf4f50`): BLOCK, three blocking, two advisory, one transient.
| Finding | Class | Disposition |
|---|---|---|
| F1 `paths.py` and `config.py` derive the root from `__file__`, not `KGME_HOME` | blocking, disputed | Sent to the arbiter (Opus 5) per the protocol. **Ruling: advisory.** ADR-015 forbids environment-variable magic except secret handles; the handoff phrase "derived from `KGME_HOME`, the repo root" is apposition; the shell function selects the checkout with `--project`, so the two cannot diverge. Docstring now states this. Arbiter's follow-up for a later handoff: the shell function, not Python, may verify that `$KGME_HOME` is the checkout being run. |
| F2 `tier1_paths` holds only the in-repo tripwire | blocking | Resolved by fact: Michou stated no Tier 1 repository exists on disk yet. `kgme.toml` records this; the path is added when one exists. |
| F3 `uv_build` pinned as a range | blocking | Fixed: `==0.11.7`, recorded above. |
| F4 `paths.py` claims no reads while calling a reader | advisory | Fixed anyway: `config.read_config()` is the one reader; `paths.py` is pure and takes the settings dict; a test asserts it imports no effects. |
| F5 tests carry no ADR-016 class | advisory | Fixed anyway: four class markers registered; every test marked. |
| pytest could not start in the sandbox (uv cache denied) | transient | Tooling; not counted, per ADR-016 and the review-loop reader. |

**Cycle 2** (diff `33eb6a774380cb85`): **PASS.** No new findings; F1 through F5 verified in the diff, each recorded as an advisory row noting the disposition. Static review; the sandbox ran no tests.

Strikes counted: 0 distinct unresolved blocking root causes. Cycles on one root cause: at most 2. No halt, no escalation packet.

## Deviations, stated
- `type kgme` resolves to a shell function `kgme() { uv run --frozen --project "$KGME_HOME" kgme "$@"; }`, not to `.venv/bin/kgme`. Nothing on PATH points into `.venv/bin`, and adding it would shadow the system Python in every shell; `uv tool install` would create a second environment. Michou chose the function 2026-09-14. One environment, frozen lock, from any directory.
- The reader says findings land in a separate `AUDIT-NNNN-review-<handoff>.md`; for this first hand-run use they are recorded in this report instead, one file for one handoff. `kgme review` (HANDOFF-0029) will write the separate file.
- The proposal's step 6 said the reader would be written here; it was written the night before at Michou's direction and only verified (a test checks its model table against `kgme.toml`).
- `ruff format --check .` reports "93 files already formatted" while `ruff check --show-files` lists six; the count is ruff's, not a scan outside the repository (`.venv`, caches excluded). Noted, not investigated further.

## Needs from Michou, closed
CLAUDE.md line: approved and applied. Alias rename to `kgh`: approved and applied. `pytest` over `unittest`: no objection raised. Tier 1 path: does not exist yet.

## Next
HANDOFF-0026 (ledger) is the next proposal to adopt; ADR-019 is accepted. `make check` is the gate from here on.
