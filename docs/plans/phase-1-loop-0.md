---
id: PLAN-PHASE-1
type: note
status: active
created: 2026-09-11T23:50:00-07:00
modified: 2026-10-14T00:40:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — Phase 1: Loop 0 and the cockpit

Phase 0 built the ground: backup proven, repo off-machine, toolchain pinned, charter and eighteen ADRs accepted. Phase 1 writes the first code — the boring, load-bearing kind — and ends with one loop that works end to end and a first screen that shows it. Everything is built to ADR-015 and reviewed by Codex before commit. Nothing is scheduled in Phase 1.

*Amended 2026-09-14 after a four-model deliberation (AUDIT-0011) and Michou's rulings of the same evening. The original eight steps are kept below as the record of what was planned; the amended order replaces them as the plan. Every step is a proposal under `docs/handoff/proposed/` until Michou adopts it.*

## Build order, amended 2026-09-14 (each step is one handoff; each ends with a review under the loop protocol)

| # | Step | Handoff | Depends on | Why here |
|---|---|---|---|---|
| 0 | **Packaging, paths, review-loop protocol.** `pyproject.toml`, committed `uv.lock`, `kgme.toml`, `kgme/paths.py`, `kgme/config.py`, `kgme/cli.py`, `Makefile` with `check`; PyYAML, ruff, pytest pinned; the review protocol in `docs/readers/review-loop.md`; the `kgme` alias renamed so the CLI owns the name; one line added to the CLAUDE.md map for `kgme/` | 0025 | — | ADR-015 requires all of it; nothing else runs without a project for `uv run` |
| 1 | **Ledger.** `kgme/ledger.py` as the single writer with redaction inside it; `kgme/events.py`; `kgme/ulid.py`; ADR-019 fixes the event shape; a fixture test that one saved `claude -p --output-format stream-json` run and one saved `codex exec --json` run parse into the shape | 0026 | 0 | Every later step records into it; the shape must be fixed before the first line |
| 2 | **Repo-scoped permissions.** `.claude/settings.json`: ask-mode, explicit allow, deny for `rm -rf`, `sudo`, `security`, `curl | bash`, force-push, `.env`, `~/.ssh`, Keychain, Tier 1 | 0027 | 0 | The settings half of the original step 1; needs no ledger |
| 3 | **Hook pair.** Pre-tool guard blocks by resolved path and fails closed; post-tool hook writes the `outcome` with `ref` to the guard's `intent`; every tool recorded; raw input to gitignored scratch, redacted summary to the ledger | 0028 | 1, 2 | The hooks half of the original step 1; the ledger's first client |
| 4 | **`kgme review`.** The review protocol as a ledgered command with loop state read from the ledger; blocking findings iterate between models, bounded per ADR-016, escalate to Michou at the bound | 0029 | 3 | Codex has no hook layer; its reviews must leave a trace |
| 5 | **Schema v1.2 and the `docs/` repair.** Append-only types drop `modified`; `note` admitted under `docs/`, `docs/plans/`, `memory/inbox/`; charter exempted by path; templates excluded; no ADR edited | 0030 | — | Without it the validator fails on KGME's own documents on day one |
| 6 | **Validator.** `kgme/lint.py`, `kgme/vault.py`, `tools/schema/lint.py`; covers `memory/` and `docs/`; findings carry ADR-016 classes; `make check` runs it | 0031 | 0, 5 | The reference example of the ten-minute standard |
| 7 | **Canary tests and worker manifests.** Fast tier in `make check`; agent tier in `make canary-agents`; every cell a ledger event labelled by enforcement layer | 0032 | 1, 3, 6 | Gate "canary tests" on STATUS |
| 7b | **`kgme sync`: push on every commit, ledger committed at session end.** Post-commit hook pushes; `SessionEnd` hook commits `logs/ledger/` by pathspec and pushes; never force, never blocking, offline is `transient` | 0040 | 0, 1 | Added 2026-10-08: the remote sat two commits behind for weeks; Gate 1 is only met while pushes happen |
| 7c | **Guard: destructive git denied by rule; Outputs scoping in loop mode; per-entry fingerprints.** Deny `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`, `stash drop`; loop runs write only inside their handoff's `Outputs`; canary digest names the hook that changed | 0045 | 7 | A mechanical rule for a mechanical violation; 0043 needs it before it runs unwatched |
| 8 | **`kgme clean`.** Named targets only, allowlisted roots, one event per deletion; bare `rm -rf` stays denied | 0033 | 1 | Loop 0's reconstruction test deletes with it |
| 9 | **Loop 0 — `kgme brief` v1.** Manual, read-only, local, no model call; four acceptance tests with classes; `--dry-run`; reminder, task, daily templates shipped | 0034 | 1, 6, 8 | The loop |
| 9b | **Design-track registration.** `kgme lint` validates git-known files (`--all` for the tree); schema v1.5 track folders; `codex-builder` profile; binaries out of tree | 0042 | 9, 0041 | The worktree is the separation today; this makes it the repo's |
| 10 | **Seed the vault.** Michou's own act: real reminders, tasks, daily notes, ten friction entries | 0035 | 9 | The vault is empty; an empty brief measures nothing |
| 11 | **Cockpit design canvas.** From the wishlist; five states; keyboard map; Phase 2 controls drawn greyed. Approved by Michou before any cockpit code | 0036 | — | Parallel track from day one; taste, not code |
| 12 | **Cockpit v0.** Stdlib server on `127.0.0.1`, one page, the timeline over the ledger, installed to the Dock. Read-only; nothing else | 0037 | 1, 11 | The first pixel |
| 12b | **`kgme review --loop`.** Build → gate → review → dispose → arbitrate → close with nobody in it; merge manual; two-cycle halt unattended; dead-man switch; compaction logged; grilled before adoption (amended 2026-10-14) | 0043 | 9, 9b, 12, 7c | The loop Michou asked for, bounded by ADR-016 and a kill path |
| 13 | **LuLu, `age`, the separate-user evaluation.** Egress rule for the Python profile; Tier 1 at rest; the evaluation ADR-013 asked for | 0038 | 7 | ADR-013 §2's two Phase 1 requirements, discharged at the end so they never block code |
| 13b | **The toolbox.** ADR-020; `docs/toolbox.md` with first rows (four vendored skills, the brief's data sources with egress hosts); lint checks. The scout half waits for 13 (LuLu) as its own handoff | 0044 | 9 | A dependency as a cheap, visible act |
| 14 | **Exit audit.** Evidence from the ledger; STATUS to Phase 2; first weekly review | 0039 | 9, 10, 12, 13 | Exit on evidence |

Steps 0 and 1 ship together; 2 and 3 together; 8 and 9 together. Step 11 has no dependency and opens now.

## Decisions folded into the order (Michou, 2026-09-14)
`kgme/` at the repo root · redacted summaries in the ledger, raw payloads in gitignored scratch · the CLI owns `kgme`, the `cd` alias is renamed · blocking review findings iterate between models until resolved or escalated · `age` now, separate macOS user evaluated at exit · LuLu at the end of Phase 1 · weekly review Sunday 18:00 PT · cockpit v0 is the timeline only plus a vendor-format fixture test · documents first, handoffs adopted one by one · PyYAML pinned · validator covers `memory/` and `docs/` · every tool call recorded.

## Deviations from accepted documents, stated
- ADR-013 §Consequences says the first code is the validator and the canary tests. Packaging and the ledger precede them for dependency reasons: the validator needs a project and a pinned YAML parser, and canary results are ledger events. Priority is unchanged; link order is.
- ADR-017 §Build order puts stream ingestion before the timeline. The hooks already feed Claude Code tool calls into the ledger, so the timeline has real runs to show without ingestion; ingestion is Phase 2. ADR-019 supersedes ADR-017 §2's event shape only.
- The roadmap moved egress control and the Tier 1 boundary to Phase 3; ADR-013 §2 names them Phase 1. The ADR wins; both land in step 13.

## Exit criteria
- Gates 3, 4, 5 on STATUS met (ledger written, permissions + hooks demonstrated, canary tests passing with every cell's enforcement layer named).
- Loop 0 passes its four tests and has been run by hand for a week against a seeded vault.
- Cockpit v0 shows the ledger timeline and at least one real run.
- Friction log ≥ 10 entries; the first three workers named, or the third explicitly left open on the friction log's evidence.
- LuLu installed with the Python profile's rule; `age` procedure written; the separate-user evaluation ruled on.
- The first weekly review held at Sunday 18:00 PT.

## Deferred until Phase 1 exits
Scheduling · Ollama models and embeddings · browser worker · Telegram · Groq · live ingestion of vendor event streams · in-app approvals · the `/btw` lane · dispatch from the cockpit · VS Code follow · migration plan for `Finance/`, `School/`, `Personal/` · Loop 0 v2 with a model for prose. · `kgme dream` (0046: the week's ledger read out of band, instincts proposed; after 0043 and the heartbeat) · the scout half of 0044 (after 0038) · ADR-021's gate in the router (Sentinel) · confidential-inference providers as a Tier 1 path (a later ADR).

## Record: the original eight steps (2026-09-11), superseded above
1. Repo-scoped permissions and hooks. 2. Ledger. 3. Validator. 4. Canary tests. 5. Loop 0 `kgme brief`. 6. `kgme clean`. 7. Cockpit design. 8. Cockpit v0 with ingestion, approvals, side lane, dispatch, VS Code follow. The deliberation found step 1 unbuildable before step 2, no packaging step, step 8's tail belonging to Phase 2, and the two ADR-013 requirements missing; AUDIT-0011 has the full record.
