---
id: ADR-015
type: decision
status: proposed
created: 2026-09-11T09:30:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-015 — Code conventions: first-principles, fixable, auditable

*Proposed 2026-09-11 at Michou's request. Becomes accepted on his word and commit. Once accepted, the "Conventions" section of `CLAUDE.md` is amended to point here so every agent applies it on every diff.*

## Context
KGME's code will be written mostly by agents and reviewed by a human who is not a professional programmer. The failure mode is code that works but that nobody can explain, fix, or audit a year later. ADR-008 (small dependency surface), ADR-011 (diff review as the approval mechanism) and ADR-013 (policy demonstrated by tests) all assume code that a reviewer can actually read.

## Decision
**The standard:** Michou can read any file in the repository cold, in ten minutes, and say what it does and what it touches. Every rule below serves that sentence.

### Simple, first-principles
- Python 3.13 through `uv` only. Standard library first. A third-party dependency costs an ADR line: what, why, source, pinned version. `uv.lock` is committed; jobs run `uv sync --frozen`.
- Small pure functions with explicit inputs and outputs. No metaprogramming, no decorators beyond the standard library, no `async` unless something demands it, no class unless there is state to protect.
- One module per concept; files under ~300 lines; each file opens with a docstring stating purpose, inputs, outputs, and side effects.
- Explicit over clever, always. If a shorter form needs a comment to be understood, the longer form wins.

### Every side effect named and quarantined
- Anything that reads or writes disk, touches the network, or spawns a process lives in a thin effects layer, named by convention (`read_*`, `write_*`, `fetch_*`, `run_*`), separate from logic. Logic modules import nothing from the effects layer's dependencies.
- Consequence: every place KGME touches the world is listable with one `grep`; logic is testable without mocks.
- Subprocesses take argument lists, never shell strings (`shell=True` is banned).

### Auditable by construction
- All configuration in one TOML file at the repo root; all paths from one `paths.py`; no global mutable state.
- No environment-variable magic except secret *handles*, which fetch from Keychain at runtime (ADR-008); a secret value never appears in code, config, logs, or prompts.
- Every job is a folder with a permission manifest (ADR-013), a `run.py` that supports `--dry-run`, and idempotency by key. Every run writes `intent` and `outcome` ledger events.
- Errors fail loudly and early. Exceptions are never swallowed; every failure is a ledger event; every retry is bounded and logged.
- Comments explain *why*, never *what*. `TODO` is banned — an open item goes to the friction log or a handoff.
- Data formats: JSONL for events, YAML frontmatter for notes, SQLite through the standard-library `sqlite3` module (no ORM).
- Durable records never use the `.log` extension: backup tools (Backblaze among them) exclude `*.log` by default, which would silently put the ledger outside the backup. Ledger files are `.jsonl`; only disposable scratch output under `logs/scratch/` may be `.log`.

### Enforced mechanically where possible
- `ruff` (lint and format), pinned. Type hints on every public function. `make check` runs ruff, the schema validator, and the policy canary tests; nothing is committed if it fails.
- Every job carries the four acceptance tests: duplicate run, interrupted run, forbidden access refused, output reconstructable from the ledger.
- Git: small commits, one handoff per commit, message `<area>: <what> (<handoff id>)`, never force-push (the ADR-012 purge exception aside).

### Enforced by review where not
- An agent must explain any diff line that is not obvious, before the commit.
- If the reviewer (Codex, or Michou) cannot say what a function does from its name and docstring, it is rewritten, not documented harder.
- A file that fails the ten-minute standard is a defect, whatever it does.

## Alternatives considered
- Idiomatic-but-dense Python (comprehensions in comprehensions, dataclass hierarchies, plugin registries): faster to write for an expert, opaque to the person who must audit it.
- A framework's conventions: inherits four hundred dependencies and someone else's abstractions (ADR-001).

## Consequences
Code will be longer and plainer than a professional would write for themselves. Reviews are cheap. The first artefacts — the validator and the canary tests — are written to this standard and become the reference examples.
