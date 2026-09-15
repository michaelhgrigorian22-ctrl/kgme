---
id: AUDIT-0011
type: report
status: final
handoff: null
author: claude-code
source: inferred
sources: [PLAN-PHASE-1, ROADMAP, STATUS, CHARTER, SCHEMA, ADR-003, ADR-007, ADR-008, ADR-012, ADR-013, ADR-015, ADR-016, ADR-017, ADR-018, AUDIT-0002, HANDOFF-0015]
tier: 2
created: 2026-09-14T22:25:00-07:00
period: 2026-09-14
---

# Phase 1 plan deliberation — four models, one synthesis, twelve rulings

Requested by Michou on 2026-09-14 ("deliberate the Phase 1 build plan with one Opus 5, one Astra, one Fable and one Sol agent; perfect the plan and inquire as to details that are up to me"). Not a handoff; recorded here because the four reviews and the rulings are the provenance for the amended plan, ADR-019, and proposals HANDOFF-0025 through 0039. Nothing was changed in the repository during the deliberation; every reviewer ran read-only.

## Method
One shared brief (Appendix 0) named the files to read and fixed seven output sections. Opus 5 (`claude-opus-5`) and Fable 5.1 (`claude-fable-5-1`) ran as Agent-tool subagents with Read only. GPT-6 Astra (`gpt-6-astra`) and GPT-5.6 Sol (`gpt-5.6-sol`) ran as `codex exec -s read-only` in this repository. Claude Fable 5.1 (this session) synthesized and put the decisions to Michou in three rounds. Word counts: Opus 3,698; Fable 3,343; Astra 2,646; Sol 3,153.

## Consensus (all four unless noted)
| # | Finding | Consequence in the amended plan |
|---|---|---|
| 1 | Step 1's post-tool hook appends to a ledger step 2 creates; unbuildable as ordered | Split: settings (0027) before hooks (0028); ledger (0026) before both |
| 2 | No packaging step; `pyproject.toml`, `uv.lock`, root TOML, `paths.py`, `Makefile` absent, all required by ADR-015 | Step 0 added (0025) |
| 3 | Event shape needs a schema version, an event id, and a reference or idempotency key; ADR-017's shape lacks `actor`, the plan adds it | ADR-019 proposed |
| 4 | Append discipline: `O_APPEND`, `flock`, single write, `fsync`, size cap, month per event from local offset-aware time | ADR-019 §3 |
| 5 | Raw tool inputs in a git-tracked, never-deleted ledger are the one irreversible mistake (Opus, Fable) | Redaction inside the single writer; payloads to gitignored scratch (Michou's ruling) |
| 6 | Pre-hook must fail closed; post-hook failure policy must be stated | 0028 |
| 7 | Loop 0 v1 makes no model call | 0034 |
| 8 | Step 8's tail is Phase 2 by the roadmap and ADR-017 | Cut; 0037 is timeline only plus a fixture test |
| 9 | Design canvas is a parallel track, not step 7 | 0036, no dependencies |
| 10 | `kgme` alias (`cd`) shadows the future CLI | Rename in 0025 |
| 11 | Hooks bind Claude Code only; Codex boundary is its sandbox | Canary cells labelled by layer (0032); Codex reviews ledgered by wrapper (0029) |
| 12 | Codex review mechanics undefined | Protocol in 0025, command in 0029 |
| 13 | Canaries split into a fast deterministic tier and a slow agent tier | 0032 |
| 14 | The vault is empty (no reminders, tasks, daily notes; one template); friction log at one entry | Templates in 0034; seeding is Michou's handoff 0035 |
| 15 | Schema conflicts: no `inbox/` row; ADRs lack `modified`; charter is an eleventh type; STATUS, roadmap, plans are notes outside `notes/` | Schema v1.2 (0030) |
| 16 | ADR-013 §2 names egress and Tier 1 as Phase 1; the roadmap moved them to Phase 3 | 0038 |
| 17 | Tests must not write the real ledger (Opus) | `logs/ledger-test/`, gitignored |

## Where the reviewers disagreed, and how it was resolved
| Question | Positions | Resolution |
|---|---|---|
| Package layout | `kgme/` at root (Opus, Fable); `src/kgme/` (Sol); modules under `tools/` (Astra) | Michou: `kgme/` at root |
| Payload storage | Gitignored scratch plus hash (Fable); no store (Opus fallback); tracked sanitized store (Astra); sanitized summary only (Sol) | Michou: scratch plus hash |
| YAML parsing | PyYAML pinned (Opus); hand-rolled flat parser (Fable); stdlib if the subset allows (Sol) | Michou: PyYAML, `safe_load` |
| Post-hook failure | Fail open with an error file surfaced by `make check` (Opus); stop the session (Sol); exit 2 wrapper (Fable) | Fail open, error file, `make check` fails if non-empty (0028) |
| Validator scope | `memory/` now, `docs/` later (Opus, Astra); `memory/` plus schema fix (Fable) | Michou: `memory/` and `docs/` now, via schema v1.2 rather than ADR edits |
| Cockpit v0 | Timeline only (Opus, Fable, Sol); plus minimal live ingestion (Astra) | Michou: timeline only, plus a fixture test of both vendor formats |

## Michou's rulings (2026-09-14, evening, three rounds)
1. Package layout: `kgme/` at repo root; one line added to the CLAUDE.md repo map.
2. Hook payloads: redacted summary in the ledger; raw input in gitignored scratch, referenced by SHA-256.
3. `kgme` shell name: the CLI owns it; the `cd` alias is renamed (default `kgh`).
4. Codex review gate: a blocking-class finding opens a fix-and-re-review loop between models until resolved or intervention is required.
5. Tier 1: `age` encryption now; separate macOS user evaluated at Phase 1 exit.
6. Egress: LuLu, installed at the end of Phase 1.
7. Weekly review: Sunday 18:00 PT.
8. Cockpit v0: read-only timeline only, plus one fixture test of a saved `claude -p --output-format stream-json` run and a saved `codex exec --json` run; no live ingestion until Phase 2.
9. First step: documents first; then handoffs adopted one by one.
10. YAML: PyYAML pinned, `safe_load` only.
11. Schema repair: fix `docs/` now; validator covers `memory/` and `docs/`.
12. Hook coverage: every tool, including Read, Grep, Glob.

Flag raised at ruling 11 and carried into 0030: adding `modified` to accepted ADRs would violate CLAUDE.md's rule that accepted ADRs are never edited; the repair is done by changing the schema rule for append-only types, not the ADRs.

Assumptions stated to Michou and not contested: `rm -rf` stays denied and `kgme clean` is the deleter; monthly ledger rotation stands (ADR-012); stdlib `http.server` for the cockpit; `sh` wrapper plus `uv run python` for hooks; the third worker waits for ten friction entries; `pytest` pinned.

## Outputs of this deliberation
- `docs/plans/phase-1-loop-0.md` amended (diff approved by Michou).
- `docs/adr/ADR-019-ledger-event-schema.md`, `status: proposed`.
- `docs/handoff/proposed/2026-09-14-*.md`, HANDOFF-0025 through 0039, `status: proposed`.
- `docs/STATUS.md` refreshed (diff approved by Michou).
- This report.

---

## Appendix 0 — The shared brief
### Deliberation brief: KGME Phase 1 build plan

You are one of four independent reviewers (Opus 5, Fable 5.1, GPT-6 Astra, GPT-5.6 Sol) deliberating the Phase 1 build plan for KGME, Michou's local-first personal agent system. Your output is a written review; a synthesizer will merge the four. You must NOT create, modify, or delete any file. Read only.

Repository root: /Users/michaelgrigorian/Projects/Automate

#### Read these first, fully, in this order
1. CLAUDE.md (the constitution; Codex sees it as AGENTS.md)
2. docs/plans/phase-1-loop-0.md (THE PLAN UNDER REVIEW)
3. docs/roadmap.md
4. docs/STATUS.md (open decisions table matters)
5. docs/charter.md
6. docs/schema-v1.md
7. docs/adr/ADR-003, ADR-007, ADR-008, ADR-012, ADR-013, ADR-015, ADR-016, ADR-017, ADR-018 (all short; read the others if a step depends on them)
8. docs/audit/2026-09-09-global-claude-config.md (current state of Claude Code permissions/hooks on this machine)
9. memory/notes/cockpit-wishlist.md and memory/inbox/friction-log.md
10. docs/handoff/2026-09-11-gh.md and one other completed handoff, to see the handoff format each Phase 1 step will be written in.

Environment facts (verified this session, do not re-verify): macOS Darwin 25.6.0; Python only via `uv`; Claude Code and Codex CLI 0.154.0 installed under nvm node v25.9.0; no `.claude/settings.json`, no `Makefile`, no `pyproject.toml`, no `tests/`, no `tools/`, no `logs/` code exists yet in the repo. `memory/agent/` exists and is empty. Global Claude Code settings are `auto` mode with a wide allowlist (see the audit). Codex config default model is gpt-6-astra.

#### What to produce

Write markdown with EXACTLY these seven sections, in this order, with these headings. Be dense and specific; cite the file and line or ADR number behind every claim. No em-dashes. Full sentences.

##### 1. Verdict on the build order
Is the eight-step order right? For each step say keep, reorder, split, merge, or cut, with the reason. Identify hidden dependencies between steps (for example: can the hook that appends to the ledger in step 1 exist before ledger.py in step 2?).

##### 2. Step-by-step design specifics
For each of the eight steps, propose the concrete design the handoff should specify: file paths, function signatures, the exact event schema, the exact settings.json permission entries, the hook mechanism (Claude Code hooks config, which events, what the hook script does and in what language), the lint checks, the canary test matrix, the `kgme brief` inputs and output format, the `kgme clean` allowlist, the cockpit stack (framework, port, how it reaches the Dock). Where ADR-015 or another ADR constrains the choice, say which and how. Where you would deviate from the plan text, say so explicitly and why.

##### 3. Missing steps and risks
What the plan omits that will bite: packaging (`pyproject.toml`, the `kgme` entry point vs the existing shell aliases), the `make check` target, how Codex review is invoked per step, the run_id scheme, timezone handling, ledger rotation, what happens when the hook itself fails, concurrency (two agents appending at once), the fact that hooks run for Claude Code only and not for Codex, etc. Rank by severity.

##### 4. Acceptance tests per step
For each step, the concrete test that proves it done, runnable in under ten minutes per ADR-015.

##### 5. Decisions that belong to Michou
List every choice that is his to make, not the builder's. For each: the question in one sentence, the options, the tradeoff in two sentences, and your recommendation with reason. Include the open decisions already on STATUS.md that Phase 1 touches (rm -rf policy, Tier 1 boundary, egress tool, third worker, weekly review slot) and any new ones you find (cockpit framework, hook language, whether Loop 0 v1 truly has no model call, whether Codex review is blocking, ledger month rotation vs single file, etc.).

##### 6. Proposed handoff sequence
A numbered list of handoffs (HANDOFF-0025 onward), one line each: title, inputs, outputs, acceptance test, reviewer. Group any that should ship together.

##### 7. The one thing you would change
The single highest-leverage amendment to the plan, in one paragraph, with the mechanism.

---

## Appendix A — Opus 5 (`claude-opus-5`)

### Opus 5 review: KGME Phase 1 build plan (`docs/plans/phase-1-loop-0.md`)

#### 1. Verdict on the build order

The eight steps contain the right material and are in close to the wrong order, because the plan sequences by importance rather than by dependency. Step 1 cannot be built as written.

**Step 1, repo-scoped permissions and hooks: split.** The step specifies a "post-tool hook that appends every tool call to the ledger" (`phase-1-loop-0.md:18`), but `ledger.py` with `append()` is step 2 (`:19`). The hook has no callee. Split into 1a (`.claude/settings.json`, ask-mode, allow/deny lists, no hooks) which has no dependencies and can ship first, and 1b (both hooks) which must follow the ledger. The rationale given for placing step 1 first, that everything after runs under it, is satisfied by 1a alone.

**Step 2, ledger: keep, promote to first code.** It is the only artefact with zero inbound dependencies, and ADR-012 makes it the one durable class, so everything else is cheaper to build once events exist. Note the tension with `ADR-013:32`, which states the first code written in KGME is the validator and the canary tests. That sentence describes priority, not link order, and the plan already deviates from it by putting permissions first; the deviation should be stated in the handoff rather than left implicit.

**Step 3, validator: keep in place, but scope it first.** See section 3, risk 4: applied as `schema-v1.md:80` describes, it fails on KGME's own documents on day one.

**Step 4, canary tests: keep, split by cost.** The step conflates deterministic tests (feed a hook script a synthetic payload, assert exit 2) with model-invoking tests (launch `claude -p` and `codex exec` and assert refusal). Only the first class belongs in `make check` under the ten-minute standard of `ADR-015:20`; the second belongs in a separate target run before scheduling and after every permission change, which is exactly what `ADR-013:22` actually requires.

**Step 5, `kgme brief`: keep, but it has an unstated blocking input dependency.** The vault contains three Markdown files (`memory/inbox/friction-log.md`, `memory/notes/cockpit-wishlist.md`, `memory/templates/note.md`). `memory/daily/` is empty, `memory/agent/` is empty, and there is not one note of `type: reminder` or `type: task` anywhere. Loop 0 will read nothing and write an empty brief.

**Step 6, `kgme clean`: reorder before or alongside step 5.** Loop 0's fourth acceptance test, that the artefact is reconstructable from ledger plus `memory/` (`:22`), is most honestly proven by deleting the artefact and regenerating it, and the sanctioned deleter is `kgme clean`. Ship 6 and 5 as one pair, clean first.

**Step 7, cockpit design: cut from the numbered order.** `roadmap.md:19` already says design can start any time in parallel because it is taste, not code. Numbering it as step 7 implies it gates step 8 on step 6, which is false. Make it a standing track opened at the start of Phase 1.

**Step 8, cockpit v0: split, and cut most of it.** The first clause (a Python service on localhost serving the ledger timeline, installed to the Dock) is Phase 1. Everything after it in that sentence, stream ingestion, in-app approval prompts, the `/btw` side lane, dispatching handoffs, VS Code follow, is Phase 2 by `roadmap.md:20` and by ADR-017's own build order at `:35`. Leaving it in step 8 invites scope creep into the one step with a visible reward.

**Missing step 0.** Nothing in the plan creates `pyproject.toml`, `uv.lock`, the single root config TOML, or `paths.py`, all four of which `ADR-015:23` and `ADR-015:34` require, nor the `Makefile` that step 3 invokes at `:20`.

Recommended order: 0 packaging, 2 ledger, 1a settings, 1b hooks, 3 validator, 4 canaries, 6 clean, 5 brief, 8 cockpit v0, with 7 running in parallel throughout.

#### 2. Step-by-step design specifics

**Step 0, packaging.** `pyproject.toml` with `requires-python = ">=3.13"`, `[project.scripts] kgme = "kgme.cli:main"`, `uv.lock` committed, `uv sync --frozen` in every entry point (`ADR-015:23`). Package at `kgme/` in the repo root rather than a `src/` layout, so the tree still matches the repo map in `CLAUDE.md:42-66`; adding `kgme/` to that map is an edit to `CLAUDE.md`, which `charter.md:78` puts on the never-unattended list, so Michou approves the diff. Modules: `paths.py` (every path derived from one `KGME_HOME`), `config.py` (`tomllib`, stdlib, no dependency), `ledger.py` and `events.py`, `ulid.py`, `cli.py` (`argparse` subcommands `brief`, `clean`, `check`, `cockpit`, `ledger`). `Makefile` with `check: ruff-check ruff-format-check lint-schema test-policy-fast`. One third-party dependency is unavoidable: the standard library has no YAML parser and every note carries YAML frontmatter, so either PyYAML is pinned or a restricted-subset parser is hand-written. I recommend PyYAML with `yaml.safe_load` only; a hand-rolled parser that mis-reads a list or a quoted date is a worse audit risk than one twenty-year-old dependency, and the ten-minute standard is about KGME's own code, not about reimplementing parsers.

**Step 2, ledger.** Fix the event shape in a new ADR-019, because the plan (`:19`) and `ADR-017:22` already disagree: the plan adds `actor` and ADR-017 does not have it, and ADRs are never edited (`CLAUDE.md:13`). Proposed record, one JSON object per line:

`{"v":1, "ts":"2026-09-14T08:03:11.412-07:00", "run_id":"<ULID>", "seq":3, "source":"kgme|claude-code|codex|hook|human", "actor":"kgme.brief", "kind":"intent|outcome|tool_call|approval|correction|note", "class":"blocking|transient|cosmetic|advisory|null", "job":"brief", "idem_key":"brief:2026-09-14", "status":"ok|error|refused|null", "payload":{...}}`

`v` exists so the ledger can migrate the way `ADR-005` migrates the vault. `seq` exists because two events in the same millisecond are otherwise unorderable. `idem_key` is required by `ADR-015:36`. `class` is required on every outcome by `ADR-016:33`, and `status` is separate from it because a run can succeed while carrying a cosmetic finding. Signatures: `append_event(event: dict) -> None`, `read_events(month: str | None = None) -> list[dict]`, `new_run_id() -> str`, `now_iso() -> str`. Implementation: compute the month path per event, not per run, so a run crossing midnight on the last of the month does not write its outcome into the wrong file; open in append mode, serialize with `json.dumps(..., ensure_ascii=False, separators=(",",":"))`, refuse any line over 4096 bytes, take an `fcntl.flock` for the write, `flush()` then `os.fsync()`. The size cap plus the lock is the answer to two agents appending at once. `now_iso()` is `datetime.now().astimezone().isoformat(timespec="milliseconds")`; never `utcnow()`, never a literal `-07:00`, because the first entry in `docs/corrections.md` is exactly that bug and the PDT to PST transition falls inside Phase 1's calendar window. `payload_ref` is dropped in v1: a separate payload store would be a second durable record with no backup rule, which is the contradiction `ADR-012:17` was written to remove.

**Step 1a, settings.** `.claude/settings.json` with `"permissions": {"defaultMode": "ask", ...}`. Deny entries must use absolute or globbed forms, because audit finding C7 (`2026-09-09-global-claude-config.md:173-175`) established that the global `Read(./.env)` is CWD-relative: deny `Read(**/.env)`, `Read(**/.env.*)`, `Read(//Users/michaelgrigorian/.ssh/**)`, `Bash(rm -rf:*)`, `Bash(sudo:*)`, `Bash(security:*)` (the Keychain CLI, per `ADR-008:18`), `Bash(git push --force:*)`, `Bash(curl:*)`, `Bash(wget:*)`. Allow `Bash(uv run:*)`, `Bash(make check:*)`, `Bash(git status)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Read`, `Edit`, `Write` scoped to the repo. Do not assume the repo file's `defaultMode` beats the global `auto` plus `skipAutoPermissionPrompt` (`audit:88, :110`); the acceptance test must demonstrate it.

**Step 1b, hooks.** Claude Code's `PreToolUse` and `PostToolUse` events, configured in the same `.claude/settings.json`. Mechanism: a three-line `/bin/sh` wrapper that execs `uv run --frozen --project "$CLAUDE_PROJECT_DIR" python tools/hooks/pre_tool_guard.py`, mirroring the pattern already proven on this machine by the xlsx hook (`audit:103-104`); a shebang on system Python is barred by `CLAUDE.md:33`. Borrow the wrapper's grep pre-filter idea (`audit:158`) so the Python interpreter is not started for tool calls that touch no guarded path, because `uv run` on every call is a real latency tax. The guard reads the hook payload on stdin, resolves `tool_input` paths, and exits 2 (which blocks and returns stderr to the model) for Tier 1 paths, `~/.ssh`, `.env`, Keychain, and anything outside `$KGME_HOME` plus the explicit read allowlist. The whole guard body is wrapped so that any internal exception also exits 2: a guard that crashes must fail closed. That is in tension with `ADR-015:37` (exceptions never swallowed), and the resolution is catch, deny, and write a ledger event, not ignore. The post-tool hook fails open by design, since the tool has already run, but writes its own failure to `logs/scratch/hook-errors.jsonl`, surfaced by `make check`. Hook events carry the hook payload's `session_id` as `run_id` so that every tool call in one session groups.

**Step 3, validator.** `tools/schema/lint.py`: `parse_frontmatter(text) -> tuple[dict, str]`, `check_note(path, fm) -> list[Finding]`, `Finding(path, rule, class, message)` with `class` from ADR-016 so cosmetic findings print without failing the build (`ADR-016:26`). Checks exactly as enumerated at `schema-v1.md:80`, plus a folder-by-type table. Scope to `memory/` in v1, matching `schema-v1.md:14`, with `--include-docs` as a reporting-only mode, and exclude `memory/templates/` because `memory/templates/note.md` carries Obsidian placeholders (`{{date:YYYYMMDD}}`) that are not ISO dates by construction.

**Step 4, canaries.** `tests/policy/`, matrix of four worker profiles (interactive Claude Code, `claude -p`, `codex exec`, the Python brief job) against four planted artefacts (`fixtures/fake.env`, `fixtures/tier1/positions.md`, a forbidden destination, a path outside the repo). Fast tier: drive `pre_tool_guard.py` with synthetic stdin payloads and assert exit 2, plus assert the Python job's own path allowlist refuses; milliseconds, no model call. Slow tier: `make canary-agents`, run before first scheduling and after every permission change per `ADR-013:22`.

**Step 5, `kgme brief`.** `jobs/brief/` with `job.md`, `manifest.toml` (readable paths, writable paths, tools, network destinations empty, highest tier 2, per `ADR-013:20`), and `run.py` supporting `--dry-run` (`ADR-015:36`). Inputs: notes with `type: reminder, status: open`; `type: task, status in {open, doing}`; `memory/daily/<today>.md`; `memory/inbox/friction-log.md`. Output `memory/agent/brief/YYYY-MM-DD.md`, frontmatter `type: note, status: active, tier: 2, author: kgme, source: inferred` with a `sources` list of every note id read, because `schema-v1.md:29` makes `sources` mandatory for inferred notes and the alternatives are worse: `stated` would falsely attribute to Michou and `fetched` demands an `origin`. `idem_key` is `brief:<date>`, so a second run replaces rather than appends.

**Step 6, `kgme clean`.** Allowlist roots: `memory/agent/**`, `logs/scratch/**`, `**/__pycache__`, `**/.ruff_cache`, `.venv`, and the ADR-009 quarantine directory once it exists. Mechanism: `Path.resolve()` then `is_relative_to()` against each root and against `$KGME_HOME`; refuse if the path is a symlink or contains a `.git`; delete files first and directories after so a bug is bounded; `--dry-run` is the default and `--yes` is required to act; one outcome event per root with path and file count.

**Step 8, cockpit v0.** `http.server.ThreadingHTTPServer` bound to `127.0.0.1`, fixed port, serving one static page plus `GET /api/events?since=<seq>` polled at one second. No framework: FastAPI and uvicorn bring more than twenty transitive packages against `charter.md:49`, and `ADR-017:26` already specifies a Python service serving a plain HTML and JS page with no Electron. Say in the module docstring that `http.server` is not a production server and that loopback with one user is why it is acceptable. Dock install is Chrome's "Install page as app" against `http://localhost`, which Chrome treats as a secure context; add a minimal `manifest.json` and an icon, no dependency.

#### 3. Missing steps and risks, ranked

**Blocking.** (1) The step 1 to step 2 circular dependency described above. (2) No packaging step at all, so `pyproject.toml`, `uv.lock`, `paths.py`, the root config TOML and the `Makefile` that step 3 calls do not exist and are not scheduled, against `ADR-015:23, :34, :43`. (3) The `kgme` console script collides with the existing alias `alias kgme='cd "$KGME_HOME"'` (`docs/handoff/2026-09-09-shell-aliases.md:23`); in an interactive zsh the alias shadows the binary, so `kgme brief` expands to `cd "$KGME_HOME" brief` and fails. (4) The validator fails on KGME's own canonical documents: all eighteen ADRs lack the required `modified` field (`schema-v1.md:23`); `docs/charter.md:3` uses `type: charter`, an eleventh type against the explicit ten-type ceiling at `schema-v1.md:46`; and `docs/STATUS.md`, `docs/roadmap.md` and both phase plans are `type: note` living outside `notes/` and `agent/`. (5) Loop 0 has no input corpus, and its exit criterion of a week of hand runs (`:29`) therefore measures nothing; the related gate, friction log at ten entries (`:31`), stands at one example line five days in.

**High.** (6) Hooks bind Claude Code only. Codex is the mandated per-step reviewer (`:16`) and would run under no repo-scoped policy, while `ADR-013:22` requires canary tests per worker. Specify `codex exec --sandbox read-only` for review runs and a Codex profile in the canary matrix. (7) Concurrent appends need a stated mechanism, not a hope. (8) Hook failure semantics: a crashed `PreToolUse` guard exits non-2 and silently fails open, which is the worst outcome in the plan. (9) Ledger write failure inside a hook, after the tool already ran.

**Medium.** (10) `run_id` is undefined. `schema-v1.md:20` already commits agents to ULIDs, so write a twenty-line `ulid.py` rather than take a dependency. (11) Timezone discipline, as above. (12) Month rotation across a run boundary. (13) Codex review is mandated but undefined: no command, no prompt, no output path, no answer to whether it blocks the commit. Precedent exists in AUDIT-0004. (14) `ADR-013:21` names two Phase 1 requirements, the egress tool and the Tier 1 boundary, and neither appears anywhere in the eight steps, though both sit open on `STATUS.md:40-41`. The plan silently drops requirements an accepted ADR imposed.

**Low but daily.** (15) The ledger is tracked in git (`ADR-012:28`), and canary results are ledger events (`ADR-013:22`), so running the test suite before a commit dirties the tree being committed and `git status` is never clean. Route test events to a gitignored `logs/ledger-test/`. (16) Rotation and volume have no stated bound; monthly files plus one hook event per tool call will produce large files quickly, and they can never be deleted.

**The one that is irreversible.** (17) The post-tool hook appends every tool call, including `Bash` command strings, into a record that `ADR-012:25` says is never deleted and that lives in git. One `Bash` line containing a token puts a Tier 0 value into a durable tracked file, and the only remedy is a purge with a git history rewrite (`ADR-012:30`), performed by Michou. This is the single irreversible mistake available in Phase 1, and it is one careless command away.

#### 4. Acceptance tests per step

**0, packaging.** `uv sync --frozen` succeeds from a clean checkout and `make check` runs and exits 0 with empty targets; `uv run kgme --help` prints the subcommand list. Under three minutes.

**2, ledger.** Append one hundred events from four concurrent processes; assert one hundred well-formed lines, no interleaving, strictly non-decreasing `ts`, and unique `(run_id, seq)`; assert the file is `logs/ledger/2026-09.jsonl` and that an event stamped in the next month lands in the next file; assert a 5000-byte payload is refused rather than truncated silently. Under two minutes.

**1a, settings.** In a fresh session in this repo, `Read` of a planted `tests/policy/fixtures/fake.env` is refused, and the refusal survives the global `auto` mode with `skipAutoPermissionPrompt`. Under five minutes, one session.

**1b, hooks.** Feed `pre_tool_guard.py` six synthetic payloads on stdin (`.env`, `~/.ssh/id_ed25519`, a Tier 1 path, a path outside `$KGME_HOME`, a benign repo read, a deliberately malformed payload) and assert exit codes 2,2,2,2,0,2; then one live session confirming a real block. Under five minutes.

**3, validator.** Run against `memory/`: exits 0. Run against a fixtures directory containing one note per violation class (missing field, duplicate id, naive datetime, `fetched` without `origin`, `inferred` without `sources`, wrong folder for type) and assert one finding each with the right class. Under two minutes.

**4, canaries.** `make check` runs the fast tier green in under sixty seconds; `make canary-agents` shows each of the four profiles refusing each of the four artefacts, with every result a ledger event. Fast tier under one minute, agent tier under ten.

**6, clean.** `--dry-run` on a seeded `memory/agent/` lists exactly the intended files and deletes none; `--yes` deletes them and writes one outcome event; a symlink planted inside `memory/agent/` pointing at `docs/` is refused; `kgme clean docs/` is refused. Under two minutes.

**5, brief.** The four tests named at `:22`, each carrying an ADR-016 class: run twice, one artefact; `SIGKILL` mid-run, next run reconciles the orphan intent and says so; a planted forbidden file in the read path is refused and logged; delete the artefact with `kgme clean` and regenerate it byte-identically from ledger plus `memory/`. Under five minutes.

**8, cockpit v0.** With the server running, the page renders the last fifty ledger events in time order, a new event appended by hand appears within two seconds without a reload, the server refuses a connection from a non-loopback address, and the Dock icon opens the same page in an app window. Under five minutes.

#### 5. Decisions that belong to Michou

1. **`rm -rf` policy.** Keep the global deny and build `kgme clean`, or grant a path-scoped allow? The allow is one config line and leaks blast radius to anything an agent can mistype; the tool is forty lines and makes every deletion a logged, allowlisted act. Recommend Cowork's existing recommendation on `STATUS.md:37`, unchanged.
2. **Tier 1 boundary.** `age` encryption now, or a separate macOS user now? The separate user is the stronger boundary `ADR-013:21` prefers, but it breaks the single VS Code and Obsidian workspace that makes KGME usable. Recommend `age` now, separate user re-evaluated at Phase 1 exit, and record the deferral so it is not lost.
3. **Egress tool.** LuLu, Little Snitch, or defer? Both do the job; LuLu is free and small, Little Snitch has better rules and costs money. Recommend LuLu, installed at the end of Phase 1 so it does not block code, which discharges the `ADR-013:21` requirement without reordering the build.
4. **Third worker.** Name it now, or wait for the friction log? Naming now invents demand; waiting keeps the friction log as the ranking mechanism `phase-0-prepare.md` §4 designed it to be. Recommend waiting, and treating "ten friction entries" as the real Phase 1 exit gate.
5. **Weekly review slot.** Any fixed hour beats an unfixed one, since `charter.md:89` makes the review the only mechanism by which autonomy widens. Recommend Sunday 18:00 PT.
6. **YAML dependency.** PyYAML pinned, or a hand-written frontmatter parser? Recommend PyYAML with `safe_load`, per section 2.
7. **Cockpit framework.** Stdlib `http.server`, or FastAPI? Recommend stdlib, per `charter.md:49`.
8. **Hook language.** `sh` wrapper plus `uv run python`, or pure `sh`? Pure `sh` is faster and harder to read; the wrapper plus Python matches the pattern already working on this machine. Recommend the wrapper.
9. **Does Loop 0 v1 make a model call?** Recommend no, per `phase-0-prepare.md` §8, because the loop is about machinery and a model call makes every test non-deterministic.
10. **Is the Codex review blocking?** Recommend blocking only on findings of class `blocking` per `ADR-016:24`, which is the entire point of that ADR.
11. **Ledger rotation.** Monthly per `ADR-012:25`. Recommend confirming it rather than revisiting.
12. **The `kgme` alias collision.** Rename the alias to `kg`, or drop it. Recommend renaming the alias, since the CLI name is written into `charter.md:94`.
13. **Schema repair.** Fix the documents, or scope the validator to `memory/`? Recommend scoping v1 to `memory/` and opening a schema v1.2 migration for `type: charter` and the missing `modified` fields, so the validator ships this week and the document repair is a separate approved diff under ADR-004.
14. **Do tests write the real ledger?** Recommend a gitignored test ledger, per risk 15.
15. **Does the cockpit get a LaunchAgent?** A keep-alive agent for a read-only localhost server is arguably not "a scheduled job", but the plan defers scheduling at `:33`. Recommend launching by hand in Phase 1 and deciding in Phase 2.

#### 6. Proposed handoff sequence

1. **HANDOFF-0025, packaging and paths.** In: ADR-015. Out: `pyproject.toml`, `uv.lock`, `kgme.toml`, `kgme/paths.py`, `kgme/config.py`, `Makefile`, `kgme/cli.py` skeleton. Test: test 0 above. Reviewer: Codex.
2. **HANDOFF-0026, the ledger and ADR-019.** In: ADR-003, ADR-012, ADR-016, ADR-017. Out: `kgme/events.py`, `kgme/ledger.py`, `kgme/ulid.py`, `docs/adr/ADR-019-ledger-event-schema.md`, `logs/ledger/.gitkeep`. Test: test 2. Reviewer: Codex. *Ships with 0025.*
3. **HANDOFF-0027, repo-scoped permissions.** In: ADR-008, ADR-013, AUDIT-0002. Out: `.claude/settings.json`. Test: test 1a. Reviewer: Michou, then Codex.
4. **HANDOFF-0028, pre and post tool hooks.** In: 0026, 0027. Out: `tools/hooks/pre_tool_guard.py`, `post_tool_ledger.py`, two `sh` wrappers, redaction allowlist. Test: test 1b. Reviewer: Codex. *Ships with 0027.*
5. **HANDOFF-0029, schema validator.** In: schema-v1.md, ADR-005, ADR-016. Out: `tools/schema/lint.py`, `tests/schema/fixtures/`. Test: test 3. Reviewer: Codex.
6. **HANDOFF-0030, schema v1.2 migration proposal.** In: 0029's findings on `docs/`. Out: proposed diff for `type: charter` and eighteen missing `modified` fields. Test: lint with `--include-docs` exits 0. Reviewer: Michou (canonical documents, ADR-004).
7. **HANDOFF-0031, canary tests and worker profiles.** In: ADR-013. Out: `tests/policy/`, `jobs/*/manifest.toml` format, `make canary-agents`, a Codex worker profile. Test: test 4. Reviewer: Codex.
8. **HANDOFF-0032, `kgme clean`.** In: STATUS rm -rf decision. Out: `kgme/clean.py`, allowlist in `kgme.toml`. Test: test 6. Reviewer: Codex.
9. **HANDOFF-0033, Loop 0 `kgme brief` v1.** In: 0026, 0029, 0032. Out: `jobs/brief/{job.md,manifest.toml,run.py}`. Test: test 5. Reviewer: Codex. *Ships with 0032.*
10. **HANDOFF-0034, seed the vault.** Michou's own act, not an agent's: real reminders, real tasks, real daily notes, ten friction entries. Out: `memory/`. Test: `kgme brief` produces a brief a human wants to read. Reviewer: Michou.
11. **HANDOFF-0035, cockpit design canvas.** In: `memory/notes/cockpit-wishlist.md`. Out: design canvas, approved before any code (`:24`). Runs in parallel from day one. Reviewer: Michou.
12. **HANDOFF-0036, cockpit v0.** In: 0026, 0035. Out: `cockpit/server.py`, `cockpit/index.html`, `cockpit/manifest.json`, `docs/readers/cockpit.md`. Test: test 8. Reviewer: Codex, then Michou.
13. **HANDOFF-0037, egress tool and Tier 1 boundary.** In: `ADR-013:21`, STATUS open decisions. Out: LuLu installed and pinned, `age` boundary recorded. Test: a canary destination is blocked at the host level. Reviewer: Michou.

#### 7. The one thing you would change

Build the ledger first and make it the enforced choke point for everything that records, rather than a library the hooks happen to call. Concretely: move `ledger.py` ahead of the permission layer, and give `append_event()` a closed contract, a fixed field set validated on entry, a 4096-byte line cap, and a `redact()` pass that no caller can bypass, so that the `Bash` tool's command string is recorded as tool name plus a SHA-256 of the input rather than as literal text, and any field matching the secret patterns of `ADR-008:18` is replaced by its hash before the line is serialized. This single amendment resolves three separate problems at once. It removes the circular dependency that makes step 1 unbuildable as written. It gives the hooks, the validator, the canary tests, `kgme clean` and `kgme brief` one already-tested writer instead of five ad hoc ones. And it closes the only irreversible failure available in Phase 1, which is a secret landing in a record that `ADR-012:25` forbids deleting and `ADR-012:28` commits to git, whose only remedy is a history rewrite Michou has to perform by hand. The reasoning is the same one `ADR-007:23` already used for the router: policy belongs at the single point every call passes through, not in the callers, because callers are written by agents under deadline and the choke point is written once and reviewed hard.

---

## Appendix B — Fable 5.1 (`claude-fable-5-1`)

### Fable 5.1 review: KGME Phase 1 build plan

##### 1. Verdict on the build order

The eight-step order is right in spirit and wrong in one mechanical place: step 1 cannot be built as written before step 2 exists. The plan's step 1 (`docs/plans/phase-1-loop-0.md` line 18) specifies a post-tool hook that "appends every tool call to the ledger", and step 2 (line 19) says "nothing else writes to the file" except `ledger.py`. Either the hook duplicates the append logic (violating line 19 and ADR-015's one-module-per-concept rule) or it imports `ledger.py`, which does not exist yet. There is a second, quieter dependency: any hook written in Python needs `uv run` to find a project, and the repo has no `pyproject.toml` or `uv.lock` (brief, environment facts). ADR-015 line 23 requires `uv.lock` committed and `uv sync --frozen`. So a step 0 is missing.

Per step: **Step 1, split.** 1a is the permissions file plus the pre-tool path-and-command blocker, which needs no ledger; 1b is the post-tool ledger hook, which lands after step 2. **Step 2, keep, and move it ahead of 1b.** The ledger is the first artefact STATUS.md line 24 names, and ADR-013 §4 makes intent and outcome pairs the transaction contract that everything else records into. **Step 3, keep.** The schema (`docs/schema-v1.md` line 80) calls the validator "the first code artefact in KGME" and ADR-013 line 32 agrees; that ordering claim is already superseded by the ledger dependency, but nothing in step 3 depends on 1 or 2 beyond `make check`. **Step 4, keep, but note the unenforceable third fixture.** The "forbidden destination" canary (line 21) needs an egress control that ADR-013 §2 names as a Phase 1 requirement "not yet met", while `docs/roadmap.md` line 21 moves egress control to Phase 3. Until Michou resolves that, the network canary can only test the hook and settings layer, not the OS layer, and the test must say so in its class field. **Step 5, keep.** Its four acceptance tests are the first to carry ADR-016 classes (ADR-016 line 40) and it cannot precede the validator because the schema (line 80) requires validation before any write to `memory/`. **Step 6, keep, and make it the first consumer of the manifest pattern**; it is small and closes the `rm -rf` row on STATUS.md line 37. **Step 7, keep, run in parallel from day one**; roadmap line 19 already says design "can start any time in parallel" and it produces no code. **Step 8, split.** The v0 timeline over the ledger belongs in Phase 1; the trailing list on line 25 (stream ingestion, in-app approvals, `/btw` lane, dispatch, VS Code follow) is exactly roadmap line 20's Phase 2 deliverable list and should be cut from the Phase 1 plan text so the two documents agree. ADR-017 line 35 also orders ingestion before the timeline; the plan reverses it, which is correct given the hook already feeds Claude Code tool calls into the ledger, but the deviation should be stated in the handoff rather than left for a cold reader to reconcile.

Hidden dependencies summarised: 1b needs 2; 2 needs 0 (packaging); 3 needs 0 (`make check`, ruff pinned); 4 needs 1a, 2 and the config file that names the Tier 1 path; 5 needs 2, 3 and a note template for reminders and tasks that does not exist (`memory/templates/` holds only `note.md`; `memory/daily/` is empty); 6 needs 2; 8 needs 2 and 7.

##### 2. Step-by-step design specifics

**Step 0, packaging.** `pyproject.toml` at root with `[project] name = "kgme"`, `requires-python = ">=3.13"`, `[project.scripts] kgme = "kgme.cli:main"`, dependencies limited to `ruff` (pinned) as a dev dependency; `uv.lock` committed. A single `kgme.toml` at root per ADR-015 line 34 holding `[paths]` (vault, ledger dir, scratch dir, tier1 paths as absolute strings), `[cockpit] host = "127.0.0.1", port = 8642`, `[clean] allow = [...]`. `kgme/paths.py` resolves everything from that file; no other module reads config. `Makefile` with one target, `check`, running `uv run ruff check .`, `uv run ruff format --check .`, `uv run kgme lint`, and the canary suite. Deviation from the plan: I would name the package `kgme/` rather than scatter `tools/` and `router/` modules that import each other across top-level folders; `tools/` stays for MCP servers as the repository map in `CLAUDE.md` says. One collision the handoff must resolve first: `HANDOFF-0015` line 23 defines `alias kgme='cd "$KGME_HOME"'`, so a bare `kgme brief` in zsh expands to `cd "$KGME_HOME" brief` and fails; only `uv run kgme brief` would work until the alias is renamed.

**Step 2, ledger.** Files `kgme/ledger.py` (effects: `append`, `read`) and `kgme/events.py` (pure: `make_event`, `validate_event`, `new_ulid`). Signatures: `append(event: dict, ledger_dir: Path) -> str` returning the event id, writing one line with `os.open(..., O_WRONLY | O_APPEND | O_CREAT)` under `fcntl.flock`, one `os.write` call, `fsync`; `read(ledger_dir: Path, since: str | None = None, run_id: str | None = None) -> list[dict]` across month files; `open_intents(ledger_dir: Path, job: str) -> list[dict]` returning intents with no outcome, which ADR-013 §4 reconciliation needs. Event shape, deviating from both the plan (line 19) and ADR-017 line 22 in three fields: `{"v": 1, "id": ulid, "ts": iso-with-offset, "run_id": str, "source": "claude-code" | "codex" | "kgme" | "human", "actor": str, "kind": intent | outcome | tool_call | approval | correction | note, "class": ok | blocking | transient | cosmetic | advisory | null, "job": str | null, "key": str | null, "ref": id-of-intent | null, "summary": str <= 200 chars, "payload_ref": path | null, "payload_hash": sha256 | null}`. `id` is needed so an outcome can reference its intent (`ref`), `key` is the idempotency key ADR-013 §4 and ADR-015 line 36 require, and `v` is the schema version roadmap line 33 says the ledger carries. Files `logs/ledger/YYYY-MM.jsonl`, month from the local timestamp, per ADR-012 line 25 and the `.jsonl` rule in ADR-015 line 40. Sixty lines is too few once validation, ULID generation and reconciliation are included; two files of about 80 lines each still sit far under ADR-015's 300 cap.

**Step 1, permissions and hooks.** `.claude/settings.json` in the repo, committed. `permissions.defaultMode: "default"`; the handoff must verify on the installed version that a project file overrides the global `auto` mode and `skipAutoPermissionPrompt` in `AUDIT-0002` lines 88 and 110. Allow: `Bash(uv run *)`, `Bash(git status)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(ls *)`, `Bash(make check)`, `Read`, `Edit(kgme/**)`, `Edit(tests/**)`, `Edit(cockpit/**)`, `Write(kgme/**)`, `Write(tests/**)`, `Write(cockpit/**)`, `Write(memory/agent/**)`. Deny: `Bash(rm -rf *)`, `Bash(rm -fr *)`, `Bash(rm -r *)`, `Bash(curl * | bash)`, `Bash(curl * | sh)`, `Bash(wget * | sh)`, `Bash(git push --force*)`, `Bash(git push -f*)`, `Bash(security *)` (Keychain CLI), `Read(**/.env)`, `Read(**/.env.*)`, `Read(~/.ssh/**)`, `Read(memory/private/**)`. Everything else asks. The global `Read(./.env)` deny is CWD-relative (AUDIT-0002 line 174); the `**` forms close that. Hooks in the same file: `PreToolUse` with matcher `Bash|Read|Edit|Write|Glob|Grep` running `tools/hooks/pretool.sh`, and `PostToolUse` with the same matcher running `tools/hooks/posttool.sh`. Each shell wrapper is three lines: `exec uv run --frozen --project "$CLAUDE_PROJECT_DIR" python "$CLAUDE_PROJECT_DIR/kgme/hooks/pretool.py" || exit 2` so a crashed pre-hook fails closed (exit 2 is the blocking code on `PreToolUse`; the handoff verifies this against the installed docs). The Python reads the hook JSON from stdin (`session_id`, `tool_name`, `tool_input`, `cwd`), extracts candidate paths (`file_path` for file tools; `shlex.split` of `command` for Bash, every token resolved with `Path.expanduser().resolve()`), and denies if any resolved path falls under the blocklist from `kgme.toml`: `~/.ssh`, any `.env*`, the Tier 1 paths, `~/Library/Keychains`, and the credential stores under `~/.claude/` and `~/.codex/` (named by `ls` in the handoff, contents never printed). Design deviation from the plan: the pre-hook appends a `tool_call` event with `kind: intent` and the post-hook appends the matching `outcome` with `ref`, so the hook pair is a literal instance of ADR-013 §4 and a tool call that crashes mid-flight shows as an unmatched intent. `run_id` is the hook's `session_id`. The summary carries tool name, paths touched and exit code; the raw `tool_input` (which for `Write` is the whole file) goes to `logs/scratch/payloads/<id>.json`, gitignored, referenced by `payload_ref` and hashed, so the git-tracked ledger stays small and never carries a secret (ADR-008 line 18).

**Step 3, validator.** `kgme/lint.py` (pure: `lint_note(text: str, path: Path, ids_seen: set) -> list[Finding]`) and `kgme/vault.py` (effects: `read_notes(vault: Path) -> list[tuple[Path, str]]`). Checks, in order: frontmatter delimited and parseable with a hand-rolled key-value parser (no PyYAML; the frontmatter is flat); eight required fields from `schema-v1.md` lines 20 to 27; `type` in the ten; `id` unique; `created` and `modified` match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$`; type-specific fields from the table at lines 35 to 44; `fetched` requires `origin`, `inferred` requires `sources`; folder-by-type. Each Finding carries an ADR-016 class: missing field or bad date is `blocking`, trailing whitespace is `cosmetic`. Skip `templates/`, `attachments/`, `.obsidian/`. Two facts the handoff must confront: the schema's folder table has no row admitting `inbox/`, so `memory/inbox/friction-log.md` fails the folder check on day one, and the schema is `status: draft` (line 4), so the linter would freeze a draft. Run as `uv run kgme lint [--vault PATH]`, exit 1 on any blocking finding.

**Step 4, canaries.** `tests/policy/` with fixtures created in `tempfile.mkdtemp()` at test time, never in the repo, because `CLAUDE.md` forbids `memory/private/` here and `.gitignore` line 15 calls it a tripwire. Matrix: three worker profiles in Phase 1 (Claude Code under the repo settings, invoked headless as `claude -p` with `--cwd` the repo; `kgme brief` as a Python job; `codex exec` with its sandbox flags) crossed with five probes (read fake `.env`, read fake Tier 1 file at the temp path injected through a test `kgme.toml`, `rm -rf` of a temp dir, write outside `memory/agent/`, reach `http://127.0.0.1:9` as the forbidden destination). Each cell asserts refusal and asserts a `tool_call` outcome with `class: blocking` in a test ledger dir. For Codex the hook layer does not exist, so its cells test only the vendor sandbox and are labelled as such.

**Step 5, `kgme brief`.** Inputs: `memory/notes/**` and `memory/agent/**` notes with `type: reminder` or `task` and `status: open`, `memory/daily/<today>.md`, `memory/inbox/friction-log.md`. Output `memory/agent/brief/YYYY-MM-DD.md` with frontmatter `type: note`, `author: kgme`, `source: inferred`, `sources:` listing every input note id (schema line 29), body in four fixed sections (Due today, Open reminders, Open tasks, Friction since last brief). Key `brief:YYYY-MM-DD`; `intent` before the write, `outcome` with class after; `--dry-run` prints the body and writes only a `note` event. On start it calls `open_intents(ledger_dir, "brief")` and reconciles by checking whether the file exists and hashing it. The vault currently has zero reminders, zero tasks and zero daily notes, so v1 will produce a nearly empty brief until Michou seeds notes; the handoff should ship `memory/templates/reminder.md` and `task.md`.

**Step 6, `kgme clean`.** Allowlist in `kgme.toml`: `memory/agent/`, `logs/scratch/`, `.venv/`, `**/__pycache__/`. Every candidate is `resolve()`d and must be a strict child of an allowlisted root inside the repo; symlinks are refused; the default is a dry run listing paths with sizes, and `--yes` deletes, one `outcome` event per path with size and hash in the summary. It never touches `logs/ledger/`, which is durable per ADR-012 line 25.

**Step 8, cockpit v0.** Stdlib only: `http.server.ThreadingHTTPServer` bound to `127.0.0.1:8642`, `cockpit/server.py` (effects), `cockpit/render.py` (pure), one `cockpit/index.html` with inline CSS and JS polling `/api/events?since=<id>` every two seconds, plus `cockpit/manifest.json` and one PNG icon so Chrome's "Install page as app" and Safari's "Add to Dock" both work (ADR-017 line 26). No framework, no build step (ADR-017 line 28). `uv run kgme cockpit` starts it.

##### 3. Missing steps and risks

Ranked by severity. First, **the hook currently fails open and can log secrets**: without the `|| exit 2` wrapper a crashed pre-hook lets the call through, and a naive post-hook appending `tool_input` would put `Write` file bodies and Bash command strings into a git-tracked file, contradicting ADR-008 line 18. Second, **packaging is absent**, so `uv run` has nothing to run and `make check` (ADR-015 line 43) has no Makefile; the `kgme` alias collision compounds it. Third, **the egress contradiction** between ADR-013 §2 and roadmap line 21 leaves the third canary fixture untestable at the OS layer; charter §8 says the charter wins, and the charter is silent, so this is a real open decision. Fourth, **Codex has no hook layer**: everything in step 1 covers Claude Code only, so Codex reviews and builds are unledgered in Phase 1 unless a thin `kgme run codex -- ...` wrapper captures `codex exec --json` into payloads and writes the intent and outcome pair; the plan defers that to step 8. Fifth, **the schema is a draft and the vault already violates it** (inbox folder, missing templates for reminder and task, `AUDIT-0002` is `source: fetched` without `origin` though `docs/` is outside lint scope). Sixth, **concurrency**: the hook and a Python job can append simultaneously; single-write plus `flock` on the month file handles it, but only if lines stay small, which the payload split guarantees. Seventh, **timezone**: timestamps must be `datetime.now().astimezone()` and readers must sort by parsed time, not string, because the offset changes when Michou travels. Eighth, **ledger rotation and git**: at a few hundred tool calls per session the month file grows a few megabytes and the working tree is permanently dirty; every handoff commit must `git add logs/ledger/`. Ninth, **how Codex review is invoked** is unspecified: recommend `git diff --staged` written to `logs/scratch/review.patch`, `codex exec` reading it against a fixed review prompt, findings written to `docs/audit/AUDIT-NNNN.md` with ADR-016 classes, blocking findings stopping the commit. Tenth, the run_id scheme is unspecified across sources; use the vendor session id for hook events, a ULID minted by `kgme` for jobs, and the thread id from Codex's first JSON event.

##### 4. Acceptance tests per step

Step 0: `make check` runs green on an empty package in under one minute, and `uv run kgme --help` prints the subcommands. Step 2: a unit test appends 1,000 events from two processes concurrently and `read()` returns 1,000 valid lines with unique ids; a rotation test with a mocked clock writes to two month files; `open_intents` returns one intent after an intent without outcome is appended. Step 1: from a fresh `claude -p` session in the repo, `cat .env` (planted in a temp dir named in `tests/`) is refused and the ledger holds an intent and a `blocking` outcome; a `Read` of `kgme/paths.py` produces an intent and an `ok` outcome; killing the hook script with a syntax error makes every tool call fail closed. Step 3: `uv run kgme lint` on the current vault reports the friction log folder finding and nothing else once Michou amends the schema table; a fixture vault with ten seeded defects produces ten findings with the expected classes. Step 4: the full matrix runs in under ten minutes wall clock (the `claude -p` cells dominate at roughly thirty seconds each) and every cell writes a ledger event; each Codex cell is marked with its layer. Step 5: the four tests from the plan line 22 pass, plus a fifth that runs `--dry-run` and asserts no file and no intent, only a `note`. Step 6: planting a symlink from `memory/agent/x` to `docs/` and running `kgme clean --yes` deletes nothing under `docs/` and logs a `blocking` outcome. Step 7: Michou signs off on the canvas; the acceptance is his word recorded as an `approval` event. Step 8: `uv run kgme cockpit` serves the page; a new hook event appears in the timeline within two seconds without reload; the page installs to the Dock from Safari.

##### 5. Decisions that belong to Michou

`rm -rf` policy: keep the global deny and ship `kgme clean` (STATUS line 37) versus a path-scoped allow. The tool costs one handoff and gives a ledger event per deletion; the allow is free but unaudited. Recommend the tool. Tier 1 boundary: `age` encryption now versus a separate macOS user with `0700` (ADR-013 §2). The user boundary is the only one an agent subprocess cannot cross by reading a path; the cost is a second login. Recommend evaluating the user boundary in Phase 1 as ADR-013 says, deciding before any Tier 1 note exists. Egress tool: LuLu (free, open source) versus Little Snitch (paid, finer rules) versus deferring to Phase 3 as the roadmap does. Loop 0 has no network, so nothing leaks in Phase 1; but the canary fixture is hollow without it. Recommend picking LuLu in Phase 1 and installing when the first network worker appears, recorded so ADR-013 §2 is honoured. Third worker: the friction log has one example entry, so the evidence is missing; recommend leaving it open until the log reaches ten entries per the exit criterion. Weekly review slot: any fixed time; recommend Sunday evening so the brief for Monday benefits. Cockpit framework: stdlib `http.server` versus a micro-framework; ADR-017 line 26 and ADR-015 line 23 both point to stdlib, and the cost is writing routing by hand for three endpoints. Recommend stdlib. Hook language: bash wrapper plus Python via `uv run` (roughly 50 to 150 ms per tool call) versus pure bash (fast, but no safe JSON without `jq`, a new dependency). Recommend the wrapper. Loop 0 v1 with no model call: yes as written; it tests plumbing, and the brief will be thin until notes exist. Recommend keeping v1 model-free and adding v2 only after a week of runs. Codex review blocking or advisory: blocking makes every handoff wait on a second agent whose findings must be classed; advisory risks the review being ignored. Recommend blocking for `blocking`-class findings only, per ADR-016. Ledger rotation: monthly as ADR-012 says versus a single file; monthly is already decided and only the `read()` cost differs. Payload storage: raw tool inputs in gitignored scratch versus in the durable ledger; recommend scratch with a hash in the line. The `kgme` alias: rename the alias (a `~/.zshrc` edit, his file) or accept `uv run kgme`. Recommend renaming to `kgh`. Test runner: `pytest` pinned with an ADR line versus `unittest`; recommend `pytest` for readable asserts. Schema: accept v1.1 with an `inbox/` row before the linter freezes it. Ledger scope of the post-hook: every tool including `Read` and `Grep` (complete, noisy) versus `Bash`, `Edit`, `Write` only; recommend every tool, since ADR-008 line 19 says every tool call.

##### 6. Proposed handoff sequence

1. HANDOFF-0025, packaging skeleton: inputs ADR-015, this review; outputs `pyproject.toml`, `uv.lock`, `kgme.toml`, `kgme/paths.py`, `Makefile`, alias rename; test `make check` green; reviewer Codex.
2. HANDOFF-0026, ledger: inputs ADR-003, 012, 013 §4, 016; outputs `kgme/events.py`, `kgme/ledger.py`, `tests/test_ledger.py`, `logs/ledger/`; test the concurrency and rotation tests; reviewer Codex.
3. HANDOFF-0027, repo permissions and hook pair: inputs AUDIT-0002, ADR-008; outputs `.claude/settings.json`, `tools/hooks/*.sh`, `kgme/hooks/*.py`; test the fail-closed and intent-outcome checks; reviewer Codex, then Michou runs one session by hand.
4. HANDOFF-0028, validator plus schema amendment (ships with a schema v1.2 line from Cowork adding `inbox/` and the two templates): outputs `kgme/lint.py`, `kgme/vault.py`, templates; test the fixture vault; reviewer Codex.
5. HANDOFF-0029, canary matrix: outputs `tests/policy/`; test the full matrix under ten minutes; reviewer Codex; closes STATUS gate 4.
6. HANDOFF-0030, `kgme brief` v1 and HANDOFF-0031, `kgme clean`, shipped together as the two first jobs sharing the manifest pattern: outputs `jobs/brief/`, `jobs/clean/`; test the five brief tests and the symlink test; reviewer Codex.
7. HANDOFF-0032, cockpit design canvas, from Cowork, in parallel from week one; output the canvas and Michou's approval event.
8. HANDOFF-0033, cockpit v0: outputs `cockpit/`; test the two-second timeline update and Dock install; reviewer Codex.
9. HANDOFF-0034, Codex run wrapper (optional, if Michou wants Codex reviews ledgered in Phase 1): output `kgme run`; test one review round-trip in the ledger.

##### 7. The one thing you would change

Make the ledger the first code and make the hook pair its first client, with the pre-tool hook writing the `intent` and the post-tool hook writing the `outcome` that references it. The mechanism is one `ref` field and one `open_intents()` function: every tool call becomes an instance of ADR-013 §4's transaction contract, a crashed hook or a crashed tool shows up as an unmatched intent rather than as silence, the fail-closed wrapper makes a broken hook a visible stop instead of an open door, and gates 3 and 4 on STATUS.md lines 24 and 25 are proven by the same artefact the cockpit renders in step 8. Everything else in this review is detail; that reordering removes the only circular dependency in the plan and turns the hook from a logger into the enforcement layer ADR-008 line 19 asked for.

---

## Appendix C — GPT-6 Astra (`gpt-6-astra`, `codex exec -s read-only`)

##### 1. Verdict on the build order

The eight steps target the right first capability, but the order is not executable as written. Preserve deterministic Loop 0 before cockpit implementation; repair the foundation dependencies and phase boundaries before issuing handoffs. The plan requires Codex review before every commit and prohibits scheduling, both appropriate constraints ([plan](/Users/michaelgrigorian/Projects/Automate/docs/plans/phase-1-loop-0.md:14)).

1. **Split step 1.** Establish conservative permissions first, but activate tool-call logging only with step 2’s tested ledger. A post-tool hook cannot append through a module that does not exist.
2. **Merge step 2’s activation with step 1’s hooks.** Build ledger, validator scaffolding, and synthetic canaries together before enabling capabilities. Explicitly reconcile this bootstrap sequence with ADR-013’s requirement that validator and canaries be the first code.
3. **Keep step 3 before Loop 0.** Resolve schema contradictions before treating lint failures as implementation defects.
4. **Split step 4.** Write policy fixtures with the foundation; run integration canaries after enforcement exists and whenever each worker profile changes. ADR-013 requires per-worker evidence.
5. **Keep step 5.** Its deterministic implementation isolates transaction correctness from model variability. Move its model-powered v2 explicitly into Phase 2, where the roadmap places routing.
6. **Keep step 6 after reconstruction works.** Deletion is safe only when disposable outputs are demonstrably recoverable, as ADR-012 requires.
7. **Reorder step 7 to run alongside foundation work.** Design has no ledger implementation dependency, and the roadmap explicitly permits this ([roadmap](/Users/michaelgrigorian/Projects/Automate/docs/roadmap.md:19)).
8. **Split step 8.** Ship the read-only timeline and a minimal ingestion demonstration in Phase 1. Move approval UI, dispatch, side questions, and editor-following into Phase 2. Resolve ADR-017’s ingestion-before-timeline order against the plan’s reverse order and its live-agent exit criterion.

##### 2. Step-by-step design specifics

**Step 1: permissions and hooks.** Use the following conservative bootstrap entries in `.claude/settings.json`, plus `"sandbox":{"autoAllowBashIfSandboxed":false}`:

```json
{
  "permissions": {
    "defaultMode": "default",
    "allow": [
      "Read(./docs/**)",
      "Bash(git status)",
      "Bash(git diff --no-ext-diff)"
    ],
    "ask": ["Bash", "Write", "Edit"],
    "deny": [
      "Bash(rm *)",
      "Bash(rmdir *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(security *)",
      "Bash(git push *)",
      "Read(**/.env)",
      "Read(**/.env.*)",
      "Read(~/.ssh/**)",
      "Read(~/.pgpass)",
      "Read(~/Library/Keychains/**)"
    ]
  }
}
```

This deliberately deviates from blanket `uv run` approval and denies all pushes during bootstrap. `default`, not `ask`, is the documented mode value; explicit ask rules take precedence over allows, so Bash remains interactive in this baseline. These are conservative settings, not a complete confinement mechanism. Validate them against the installed Claude version. [Claude permissions documentation](https://code.claude.com/docs/en/permissions).

Create `tools/policy/hook.py`, backed by pure `decide_tool(input, manifest) -> Decision`. Configure synchronous command hooks for `PreToolUse`, `PostToolUse`, and `PostToolUseFailure`, each with matcher `.*`; use `SessionStart` for health checking and session correlation. Invoke Python through a fixed `uv` path with frozen, offline dependencies and an explicit project path. Pre-tool processing checks canonical paths, worker permissions, and approved payload hashes, then durably records intent before allowing execution. Post hooks record sanitized success or failure metadata. Never persist raw hook input. The global allowlist includes unrestricted `Read`, `Write`, `Edit`, and interpreter commands, so effective inherited permissions require tests, not assumptions ([AUDIT-0002](/Users/michaelgrigorian/Projects/Automate/docs/audit/2026-09-09-global-claude-config.md:87); ADR-008).

**Step 2: ledger.** Put effects in `kgme/effects/ledger.py`:

`append_event(root: Path, event: Event) -> str`

`read_events(root: Path, run_id: str | None = None) -> Iterator[Event]`

Propose this exact envelope, documented in `logs/ledger/schema.json`:

```json
{
  "v": 1,
  "event_id": "UUID",
  "ts": "2026-09-14T12:00:00-07:00",
  "run_id": "UUID",
  "source": "kgme",
  "kind": "intent",
  "class": null,
  "actor": "kgme",
  "operation_id": "UUID",
  "causes": [],
  "payload_ref": "logs/payloads/<sha256>.json"
}
```

`source` identifies the producer; payload provenance separately uses `stated|inferred|fetched`. `kind` retains the plan’s six values. `class` permits ADR-016’s four classes plus null for non-failures; approve that clarification because ADR-016 otherwise requires a class on successful outcomes without defining one. Payloads are immutable, tracked, sanitized JSON with operation, status, idempotency key, input versions, destination, prior/proposed hashes, and model/usage fields when applicable. Unknown cost is null, never fabricated zero.

Use UUID4 for run/event identities, UTC instants with explicit offsets, and one configured timezone for month selection. Lock across processes, append complete encoded records, flush and synchronize before effects. Preserve corrupt bytes and stop on torn records. Monthly files are already decided by ADR-012; abandon the arbitrary 60-line target where durability requires more code.

**Step 3: validator.** Keep `tools/schema/lint.py` as the adapter; use `validate_note(text, relative_path) -> list[Finding]` for pure checks. Validate YAML mappings, duplicate keys, required fields, string IDs and vault-wide uniqueness, allowed enums, offset-aware datetimes, integer tiers/priorities excluding booleans, provenance references, type-specific fields, and folder/author compatibility. Use a safe YAML parser, with an exact reviewed dependency pin.

The existing human friction log is `type: note` in `memory/inbox/`, which the folder table excludes. Templates also need an explicit policy because the schema claims every Markdown file under `memory/`. Propose a schema migration allowing human inbox notes and defining template validation; never silently exempt or rewrite them ([schema](/Users/michaelgrigorian/Projects/Automate/docs/schema-v1.md:14), [friction log](/Users/michaelgrigorian/Projects/Automate/memory/inbox/friction-log.md:1); ADR-005).

**Step 4: canaries.** Place fixtures and integration drivers under `tests/policy/`. Manifests beside each job declare readable/writable roots, tool allowlists, network destinations, and permitted tiers. Test Claude builder, Codex reviewer, Python brief, cleaner, and cockpit profiles. The matrix crosses direct reads, shell/interpreter reads, symlink escapes, canonical writes, forbidden outbound connections, protected ledger deletion, and policy-file modification. Positive controls prove each attempted operation actually ran; synthetic identifiers, not fixture contents, enter the ledger. A Python predicate test does not prove an agent boundary (ADR-013).

**Step 5: brief.** Create `jobs/brief/{job.md,permissions.toml,run.py}`, with `build_brief(inputs, date) -> Brief` and a thin effects orchestrator. Read open reminders, open/doing tasks, today’s daily note, and the friction log. Sort deterministically by due instant, priority, then stable ID; explicitly show missing daily notes and empty collections. Do not invent recurring occurrences without an approved RRULE interpretation.

Write `memory/agent/brief/YYYY-MM-DD.md` as an inferred machine note with source references and sections for overdue items, today, undated work, daily-note content, and friction. Preserve its ULID and creation time across replacement. Snapshot validated inputs durably before execution; hashes alone cannot reconstruct overwritten source text. Record intent, write and synchronize a temporary file, atomically replace, then record outcome. Reconcile under a job lock using expected hashes, not “file exists.” Dry-run prints the proposed artifact and records a dry-run transaction without replacing it (ADR-003/013/015).

**Step 6: clean.** Implement `plan_clean(paths) -> DeletionPlan` and `execute_clean(plan, approval) -> Result`. Initially allow only `memory/agent/brief/` and an explicitly configured quarantine subtree. Exclude `.venv`, `logs/`, durable payloads, human folders, and any unrecognized output class. Reject symlinks, traversal, hard-linked files, and changed plans; use descriptor-relative operations to reduce race exposure. Approval binds the item list, hashes, and destinations; record per-item intent/outcome. Virtual-environment deletion exceeds charter §6’s unattended deletion scope and needs a separate decision.

**Step 7: design.** Produce an approved design canvas showing empty, running, failed, reconciled, and disconnected states. Specify keyboard navigation, visible focus, readable contrast, and reduced motion alongside the cyberpunk aesthetic. Keep Phase 2 controls visibly outside v0 scope ([wishlist](/Users/michaelgrigorian/Projects/Automate/memory/notes/cockpit-wishlist.md:18); ADR-017).

**Step 8: cockpit.** Prefer standard-library HTTP serving with plain HTML/CSS/JS in `cockpit/`, bound to `127.0.0.1:8765`, with a configurable port. Serve only explicit static routes and a paginated read-only event endpoint; reject arbitrary paths, unsafe Host values, and cross-origin access. Render text safely, without remote assets. Start manually using `kgme cockpit`; install the page through Safari Add to Dock or Chrome’s app-install action, as ADR-017 specifies. Dock installation does not start the backend. Minimal CLI adapters normalize one real run from each vendor and deduplicate hook/stream observations by operation identity.

##### 3. Missing steps and risks

**Critical: enforcement coverage.** Claude hooks do not enforce Codex or arbitrary Python subprocesses. A broad `uv run` allow permits arbitrary programs, while a path deny cannot confine arbitrary code. Tier 1 and egress decisions therefore precede successful canary certification. ADR-013 explicitly requires Phase 1 evaluation of separate-user isolation and a host egress tool; the roadmap’s Phase 3 deferral cannot silently supersede that ADR.

**Critical: hook failure semantics.** A hook crash is not automatically a denial; post-tool failures cannot undo completed effects. Catch expected failures and emit explicit denial before execution, test missing executables and timeouts, and keep runtime effect wrappers independently dependent on durable intent. If the ledger is unavailable, stop and report through sanitized stderr; record the incident after recovery without pretending it was previously logged. [Claude hooks reference](https://code.claude.com/docs/en/hooks).

**High: packaging and configuration.** Add `pyproject.toml`, committed `uv.lock`, Python 3.13, a console entry point `kgme = "kgme.cli:main"`, `kgme.toml`, and `paths.py`. Distinguish operational TOML configuration from vendor settings and per-job manifests. The existing `kgme` alias expands to `cd`, so `kgme brief` will not invoke the new CLI without an approved alias migration ([HANDOFF-0015](/Users/michaelgrigorian/Projects/Automate/docs/handoff/2026-09-09-shell-aliases.md:23); ADR-015).

**High: durability and concurrency.** Define run identity, operation identity, locking, month rollover, daylight-saving behavior, torn-write handling, immutable payload retention, and backup restoration together. Reconciliation must distinguish a crashed run from another live writer. ADR-012’s backup gate needs a fresh restore demonstration containing actual ledger records.

**High: review and checks.** `make check` must run frozen-environment ruff check, format checking, schema lint, and policy canaries, with no silent integration skips. Use a wrapper around `codex exec --sandbox read-only --ephemeral --json -`, supplying the handoff, changed-file inventory, diff hash, and acceptance evidence. Separate reviewer findings from process exit status and bind approval to the reviewed bytes. This invocation is supported by local CLI help and the [official non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode). Apply ADR-016 classes; advisory findings do not become vetoes.

**Medium: exit evidence.** The friction log contains one example rather than ten real entries; the week of manual use cannot be replaced by a ten-minute test. Also correct gate naming: the plan calls canaries “Gate 4,” while STATUS lists permissions fourth and canaries fifth ([plan](/Users/michaelgrigorian/Projects/Automate/docs/plans/phase-1-loop-0.md:21), [STATUS](/Users/michaelgrigorian/Projects/Automate/docs/STATUS.md:19)).

##### 4. Acceptance tests per step

Each bounded suite should finish within ten minutes. ADR-015’s actual standard also requires Michou to understand each file in ten minutes; runtime alone does not satisfy it.

1. **Permissions:** Under inherited global settings, demonstrate approved reads, refused synthetic secret reads through both file and shell tools, blocked pushes, and no effect when the ledger is unavailable.
2. **Ledger:** Run two simultaneous writers producing 100 records each; verify 200 unique parseable events, month rollover, correction links, crash handling, and hash-identical restoration from backup.
3. **Validator:** Exercise one valid example per applicable type plus missing fields, duplicate IDs/keys, invalid offsets, boolean priorities, wrong folders, and provenance omissions. Approved real-vault rules must pass without edits.
4. **Canaries:** Run every enabled profile against direct, interpreter, symlink, destination, and write probes. Record denial plus a working positive control; fail on skipped enforcement coverage.
5. **Brief:** Run twice, interrupt before replacement and after replacement, plant a forbidden source, then delete and reconstruct the output from durable inputs. Verify stable identity, correct reconciliation, and dry-run behavior.
6. **Clean:** Delete approved fixture outputs; reject canonical files, ledger/payload records, `.venv`, links, traversal, and stale approval hashes. Interrupt mid-plan and reconcile each item.
7. **Design:** Michou reviews all five states using only the keyboard, including focus visibility and the proposed approval boundary. Record acceptance of the exact canvas.
8. **Cockpit:** Show both real CLI runs, reload without losing history, test malicious event text and traversal requests, and reopen the Dock app after a manual backend restart. Verify zero mutation endpoints.

These tests implement ADR-013/015; the seven-day usage observation remains a separate exit condition.

##### 5. Decisions that belong to Michou

**Deletion:** Should cleanup require per-run approval or receive narrowly delegated authority? Approval costs an interaction. Delegation requires resolving the constitution’s deletion prohibition against charter allowances; recommend per-run approval initially (STATUS; charter §6).

**Tier 1:** Should isolation use encryption alone or encryption plus a separate macOS user? Encryption protects closed data. A separate user strengthens access separation while data is available; recommend evaluating the latter now, as ADR-013 requires, without touching the private repository under this review.

**Egress:** Should Phase 1 adopt a LuLu-class tool, a Little Snitch-class tool, or formally defer enforcement? Adoption adds configuration work. Deferral leaves an accepted prerequisite unmet; recommend a tested Phase 1 control, with product selection contingent on demonstrated per-worker isolation (ADR-013).

**Third worker:** Which friction-log problem should join the two named workers? Naming one now closes the exit condition. Inventing one risks unnecessary scope; recommend choosing after ten real entries, without building it in Phase 1 (charter §2).

**Weekly review:** Which recurring day and time should govern changes? A fixed slot makes failures actionable. An unscheduled promise is easier to miss; recommend a weekly 20-minute slot Michou selects (charter §8).

**Model scope:** Should v1 remain deterministic or include prose generation? Determinism isolates foundational defects. Generation introduces routing and usage dependencies; recommend zero model calls in Loop 0 v1 (plan step 5; ADR-018).

**Review gate:** Should blocking Codex findings prevent commit, with advisories recorded separately? A gate catches consequential defects. An unconditional reviewer veto also elevates preference into policy; recommend blocking findings only, with explicit human disposition of disputes (ADR-016).

**Storage:** Should the ledger remain monthly or become one file? Monthly rotation already satisfies ADR-012. A single file requires superseding that decision; recommend retaining months and approving durable replay payloads alongside them.

**Implementation:** Should cockpit and hooks use standard-library Python or additional frameworks/languages? Standard-library code reduces dependencies. Libraries can simplify specific tasks; recommend Python hooks and plain HTTP/HTML/JS, with a pinned YAML parser and ruff justified under ADR-015.

**Schema and CLI behavior:** Should inbox notes be legal, successful classes be null, dry-runs be logged, and the navigation alias be renamed? Explicit contracts prevent divergent implementations. They change user-visible behavior or accepted schema semantics; recommend all four, with reviewed migration diffs (ADR-005/015/016; HANDOFF-0015).

**Phase boundary:** Should Phase 1 include minimal dual-CLI ingestion while deferring interactive cockpit controls? This proves the real-run exit criterion. Full controls expand the transaction surface substantially; recommend the narrow split and an explicit disposition of ADR-017’s broader Phase 1 wording.

##### 6. Proposed handoff sequence

Numbers are provisional until checked again under ADR-014; each handoff names exact output paths, reversibility, evidence, and completion metadata, following HANDOFF-0022.

1. **HANDOFF-0025, Resolve foundation contracts:** Inputs are this review and governing ADRs; outputs are approved superseding decisions/schema migration specifications; acceptance is an unambiguous dependency map; reviewers are Michou and Codex.
2. **HANDOFF-0026, Bootstrap package and conservative permissions:** Inputs are approved contracts; outputs are packaging, CLI, configuration, settings, and check scaffolding; acceptance is frozen execution and baseline denials; reviewer is Codex.
3. **HANDOFF-0027, Activate durable ledger and hooks:** Inputs are 0026 and ADR-012/013; outputs are ledger, payload storage, hooks, validator, and initial canaries; acceptance is crash/concurrency testing and complete `make check`; reviewer is Codex.
4. **HANDOFF-0028, Prove worker isolation:** Inputs are approved Tier 1/egress choices; outputs are manifests, enforcement configuration, and evidence; acceptance is the full integration matrix; reviewers are Codex and Michou.
5. **HANDOFF-0029, Deliver deterministic brief:** Inputs are validated sources and transaction APIs; outputs are the brief job and reconstruction path; acceptance is its four failure-oriented tests; reviewer is Codex.
6. **HANDOFF-0030, Deliver approved cleanup:** Inputs are reconstruction evidence; outputs are cleaner and deletion tests; acceptance is allowlist/race/recovery testing; reviewer is Codex.
7. **HANDOFF-0031, Approve cockpit canvas:** Inputs are the wishlist; outputs are the design canvas; acceptance is Michou’s recorded review; reviewers are Michou and Codex.
8. **HANDOFF-0032, Deliver read-only cockpit and minimal ingestion:** Inputs are ledger contracts and approved design; outputs are adapters and timeline; acceptance is both real runs plus restart/security tests; reviewer is Codex.
9. **HANDOFF-0033, Close Phase 1:** Inputs are seven days of usage, ten real friction entries, and backup evidence; outputs are an exit report and approved STATUS update; acceptance is all exit conditions; reviewers are Codex and Michou.

Treat 0026–0027 as one foundation release, with separate commits. Design can proceed alongside it; capability execution waits for 0028.

##### 7. The one thing you would change

Replace the eight-step checklist with one explicit **transaction-and-policy acceptance contract** that every handoff inherits. Define the worker manifest, enforced boundary, immutable input/payload references, operation identity, durable intent, bounded effect, outcome, and restart reconciliation before implementing the brief or cockpit. This amendment connects ADR-012’s durability, ADR-013’s demonstrated policy, ADR-015’s explainability, and ADR-016’s failure handling in one testable sequence. Without it, eight individually plausible components can still produce an unlogged action, an unreconstructable brief, or a timeline that mistakes a missing outcome for success; with it, each new component must demonstrate the same inspectable guarantees.
---

## Appendix D — GPT-5.6 Sol (`gpt-5.6-sol`, `codex exec -s read-only`)

##### 1. Verdict on the build order

1. **Step 1 should be split.** Keep repo-scoped permissions and the fail-closed pre-tool policy hook first, but move the post-tool ledger hook until after the ledger exists. A hook cannot satisfy “nothing else writes to the file” before `ledger.py` supplies the only writer, and a post-hook cannot retroactively make an unrecorded tool call atomic (`phase-1-loop-0.md:18-19`; ADR-008; ADR-013 §2 and §4).

2. **Step 2 should remain second, with packaging added.** The ledger is a dependency of canary results, Loop 0, cleaning, and the cockpit timeline. This handoff must also establish `pyproject.toml`, `kgme.toml`, `src/kgme/paths.py`, and the console entry point because ADR-015 requires one root TOML configuration and one path authority (`ADR-015 §Auditable by construction`).

3. **Step 3 should remain after the ledger.** The validator is the first substantive logic and the reference implementation for ADR-015, but `make check` cannot exist coherently without the package, development dependency, and `Makefile`. The plan’s claim that the validator is the “first real test” is sound, although ADR-013 says the validator and canaries are the first code, while the current order puts policy and ledger code before both (`phase-1-loop-0.md:20`; ADR-013 §Consequences).

4. **Step 4 should be split and gated on decisions.** Deterministic tests of path and command policy can follow step 3, but credible worker canaries require worker manifests, the Tier 1 boundary, and an egress mechanism. A fake refusal produced by a test double does not demonstrate that Claude Code, Codex, and standalone Python are actually constrained (`ADR-013 §1-3`; `STATUS.md:40-41`).

5. **Step 5 should be kept after validation and canaries.** `kgme brief` is the correct first end-to-end loop because it is local, read-only with respect to canonical inputs, and writes only disposable output (`phase-1-loop-0.md:22`; `charter.md:65-72`). Its reconstruction criterion needs tightening because mutable source notes plus hashes do not preserve historical contents.

6. **Step 6 should be kept, but may ship with step 5’s CLI package.** Its capability must remain independently reviewed because deletion is consequential even inside disposable paths. It should call a narrow library function and never expose arbitrary paths or shell deletion (`STATUS.md:37`; ADR-012 §Decision).

7. **Step 7 should be reordered into parallel work after the ledger schema freezes.** Taste work can start earlier, as the roadmap already says, but the approved canvas should precede cockpit implementation and should not delay the validator or Loop 0 (`roadmap.md:19,28`; `cockpit-wishlist.md:15-18`).

8. **Step 8 should be split and its Phase 2 tail cut.** Phase 1 should contain only the read-only timeline and one observed Loop 0 run. Stream ingestion, approvals, side-lane routing, handoff dispatch, and VS Code following belong to Phase 2 under the roadmap, despite being appended to step 8 in the plan (`phase-1-loop-0.md:25`; `roadmap.md:20`; ADR-017 §Build order).

##### 2. Step-by-step design specifics

1. **Repo policy baseline.** Create `.claude/settings.json`, `tools/policy/pre_tool.py`, and `tests/policy/test_pre_tool.py`. The settings should use `"defaultMode": "default"` as ask-mode and allow only `Read`, `Glob`, `Grep`, `Bash(uv run *)`, `Bash(make check)`, `Bash(git status*)`, `Bash(git diff*)`, and `Bash(git log*)`; it should deny `Read(**/.env)`, `Read(**/.env.*)`, `Read(/Users/michaelgrigorian/.ssh/**)`, `Read(/Users/michaelgrigorian/Library/Keychains/**)`, the decided Tier 1 root, `Bash(rm -rf *)`, `Bash(git push --force*)`, `Bash(git push -f*)`, `Bash(curl *|*bash*)`, and `Bash(wget *|*sh*)`. This materially narrows the audited global `auto` mode and twenty-entry allowlist (`global-claude-config.md:83-110,161-175`).

   Configure `PreToolUse` for `Read|Edit|Write|Bash`, invoking `uv run python tools/policy/pre_tool.py` with a five-second timeout. The script should parse the hook JSON from stdin, resolve filesystem targets with `Path.resolve(strict=False)`, reject forbidden ancestors, traversal and symlink escapes, inspect Bash arguments with `shlex` without executing them, print only a sanitized reason to stderr, and exit `2` to block. Path denial must be enforced in code because string patterns alone miss absolute, nested, and symlinked `.env` files (ADR-008; ADR-013 §2).

2. **Package, paths, ledger, then post-hook.** Create `pyproject.toml`, `uv.lock`, `kgme.toml`, `src/kgme/__init__.py`, `src/kgme/paths.py`, `src/kgme/ledger.py`, `src/kgme/cli.py`, `tools/policy/post_tool.py`, and `logs/ledger/.gitkeep` only if git otherwise cannot track the directory. Public signatures should be `new_run_id(actor: str) -> str`, `append_event(event: LedgerEvent) -> None`, `read_events(start: datetime | None = None, end: datetime | None = None, run_id: str | None = None) -> Iterator[dict[str, object]]`, and `validate_event(event: Mapping[str, object]) -> None`.

   The exact v1 event should be:

   ```json
   {
     "schema_version": 1,
     "event_id": "20260914T142205123-7f92c1a8",
     "ts": "2026-09-14T14:22:05.123-07:00",
     "run_id": "brief-20260914T142205123-a43d991e",
     "source": "kgme",
     "kind": "intent",
     "class": null,
     "actor": "kgme-brief",
     "payload_ref": {
       "path": "memory/agent/brief/2026-09-14.md",
       "sha256": null,
       "media_type": "text/markdown",
       "redacted": false
     }
   }
   ```

   `kind` is exactly `intent|outcome|tool_call|approval|correction|note`; `class` is null for successful or non-failure events and otherwise `blocking|transient|cosmetic|advisory`; and successful outcomes carry `"status": "ok"` inside a referenced durable payload or a documented payload extension. Adding `schema_version` and `event_id` deviates from the plan, but is necessary for deduplication, correction targeting, and the migration anticipated by `roadmap.md:33`. The accepted ADR-017 shape omits `actor`, while the plan adds it, so the handoff must explicitly document this compatible v1 extension rather than silently drift from ADR-017 §2.

   IDs should use local timestamp to milliseconds plus eight random hexadecimal characters, avoiding a new ULID dependency. Timestamps should use `datetime.now().astimezone().isoformat(timespec="milliseconds")`; the local timestamp determines `logs/ledger/YYYY-MM.jsonl`, as monthly rotation is already decided by ADR-012. `append_event()` should open with `O_APPEND`, acquire `fcntl.flock(LOCK_EX)`, write one UTF-8 JSON line with one `os.write`, call `fsync`, and unlock. This handles two agents appending concurrently without introducing a daemon or database.

   Only now add `PostToolUse` for `Read|Edit|Write|Bash`, calling `tools/policy/post_tool.py`. It should log sanitized tool name, resolved non-secret paths, result status, session-derived run ID, and duration, never raw prompts, command output, file contents, or hook stdin. If logging fails, it should return nonzero, write no alternate mutable log, and force the active handoff to stop before another tool call, because ADR-003 and ADR-012 make an unlogged continuation a data-integrity failure.

3. **Validator.** Create `tools/schema/lint.py` as a thin entry point, `src/kgme/schema.py` for pure validation, and `tests/schema/test_schema.py`. Use only the standard library if the accepted YAML subset can be parsed safely; otherwise pin one YAML dependency and record its source and reason as ADR-015 requires. The checks must cover all requirements at `schema-v1.md:16-46,79-83`, including provenance, status vocabularies, unique IDs, offset-aware datetimes, filename rules, and allowed directory by type and author. `make check` should run `uv run ruff check .`, `uv run ruff format --check .`, `uv run python tools/schema/lint.py`, and `uv run python -m unittest discover -s tests`.

4. **Canaries.** Add `jobs/<worker>/permissions.toml` for `schema-validator`, `brief`, `clean`, `cockpit`, `claude-builder`, and `codex-reviewer`. Each manifest should declare `read_paths`, `write_paths`, `tools`, `network_destinations`, and `max_tier`, exactly as ADR-013 §1 requires. The matrix must test each applicable worker against nested `.env`, symlink-to-`.env`, fake Tier 1, canonical-write attempt, `rm -rf`, force-push, forbidden HTTP destination, and a permitted control operation. Results should be `outcome` events with an ADR-016 class, but the canary runner must distinguish “refused by actual boundary” from “test expected a refusal.”

5. **`kgme brief`.** Implement `run_brief(*, date: date, dry_run: bool, now: datetime) -> BriefResult`. Inputs are open `reminder` and `task` notes under `memory/notes/`, today’s `memory/daily/YYYY-MM-DD.md` if present, and `memory/inbox/friction-log.md`; machine briefs must be excluded to prevent recursive inputs. The output is `memory/agent/brief/YYYY-MM-DD.md` with schema-valid frontmatter, stable ID and `created` preserved on replacement, `modified` updated, `source: inferred`, `author: kgme`, and `sources` listing every input note ID. Its body should contain `# Brief`, `## Due and overdue`, `## Today`, `## Open tasks`, `## Friction signals`, and `## Input manifest`, with deterministic sorting by due time, priority, then ID.

   Write the intent before any output mutation; write to a same-directory temporary file, `fsync`, then `os.replace`; and append the outcome afterward. On startup, reconcile unmatched intents by checking destination hash against the intended hash. `--dry-run` should validate and render to stdout without writing the brief, while still supporting an explicitly documented no-ledger test mode. The v1 no-model decision is consistent with ADR-018’s refusal to build an unnecessary tool loop.

6. **`kgme clean`.** Implement `clean(target: Path, *, dry_run: bool) -> CleanResult`, but expose named targets such as `kgme clean briefs`, `kgme clean quarantine`, and `kgme clean venvs`, not arbitrary user paths. Resolve each target and require it to be beneath configured roots for `memory/agent/`, quarantine, or project-local virtual environments; reject the root itself, symlinks escaping the root, canonical folders, ledger paths, and Tier 1. Use Python `unlink()` and bottom-up `rmdir()`, with one intent and one outcome per deletion unit.

7. **Cockpit design.** Produce an approved plain-text design canvas specifying a one-column timeline, run filter, severity filter, keyboard focus, empty/loading/error states, and the cyberpunk palette at a contrast ratio suitable for sustained night use. It should preserve the stated keyboard-first grammar without pretending Phase 1 supplies `/btw`, interruption, routing, or approvals (`cockpit-wishlist.md:17-44`).

8. **Cockpit v0.** Use no web framework: `cockpit/server.py` should use `http.server.ThreadingHTTPServer`, bind only `127.0.0.1`, default to port `8765` from `kgme.toml`, and serve hand-written `cockpit/static/index.html`, `app.js`, `style.css`, and `manifest.webmanifest`. `GET /api/events?after=<event_id>&limit=<n>` reads through `ledger.read_events()` and returns JSON; no route may mutate state or launch a process. Start it manually through `kgme cockpit`, then use Safari “Add to Dock” or Chrome “Install page as app”; Phase 1 must state that the Dock shortcut does not start the service because scheduling and background launch are deferred (`phase-1-loop-0.md:33-34`; ADR-017 §Form factor).

##### 3. Missing steps and risks

1. **Critical: the plan lacks a package and command migration.** The existing `kgme` shell alias is already recorded (`STATUS.md:29`), so a `kgme` console entry point may be shadowed or have its arguments consumed. Decide whether the alias becomes `kgme-home`, whether it calls the CLI, or whether Phase 1 uses `uv run kgme`; otherwise acceptance commands will behave differently by shell.

2. **Critical: the canaries do not yet prove Codex or Python confinement.** Claude hooks cover Claude Code only, while Codex and standalone Python need their own sandbox or OS boundary. Gate 4 must not be marked met merely because unit tests exercise the Claude hook (`ADR-013 §2-3`).

3. **Critical: reconstruction is underspecified.** An input hash proves that a source changed but does not reconstruct its former contents. Either define reconstruction as immediate deterministic regeneration, record the git commit plus dirty-source snapshots, or narrow the exit criterion.

4. **High: review mechanics are absent.** Each handoff should build an uncommitted diff, run `make check`, invoke Codex in read-only mode against the handoff and diff, classify findings under ADR-016, fix blocking findings, rerun review, then commit. “Reviewed before commit” otherwise has no durable reviewer, report path, or stopping rule (`phase-1-loop-0.md:14-16`; ADR-007).

5. **High: post-hook failure and concurrency are unspecified.** `flock`, `O_APPEND`, `fsync`, malformed-tail detection, and fail-closed continuation are required because the ledger is durable truth, not best-effort telemetry (ADR-003; ADR-012).

6. **High: settings cannot constitute per-worker least privilege.** One repo-level allowlist is a ceiling, not six worker manifests. Each entry point must verify its manifest before effects, and external enforcement gaps must remain visible.

7. **Medium: timezone and run identity are unstated.** Offset-aware event time, local-month rotation, random collision resistance, and one inherited run ID across intent, tools, and outcome must be fixed before the first ledger line (`CLAUDE.md:34`; ADR-005).

8. **Medium: the cockpit’s Dock story is incomplete.** A browser-installed localhost page is unavailable when its server is stopped. Phase 1 should accept manual startup explicitly instead of quietly introducing launchd before scheduling gates.

##### 4. Acceptance tests per step

1. **Step 1:** In under ten minutes, run the real pre-hook fixture matrix and show that nested `.env`, symlinked Tier 1, `rm -rf`, and force-push are blocked while an allowed repository read succeeds.

2. **Step 2:** Start twenty concurrent appenders producing 2,000 events, then prove 2,000 unique parseable lines, no interleaving, correct local monthly file, stable ordering per writer, and successful fsync-backed reopen.

3. **Step 3:** Run `make check` against valid fixtures and one fixture for every schema rule; each invalid fixture must report file, field, rule, and blocking class in one screen.

4. **Step 4:** Execute every manifest row against every relevant canary and permitted control; the ledger must contain one classified result per cell and zero simulated refusals labeled as enforced.

5. **Step 5:** Run twice and compare hashes, simulate termination after intent, test forbidden input, delete the output and rebuild it, and prove `--dry-run` changes no file. These are the four ADR-015 job tests plus dry-run.

6. **Step 6:** Dry-run and execute against a disposable fixture tree, then prove canonical notes, ledger, Tier 1, allowlist roots, and escaping symlinks remain untouched.

7. **Step 7:** Michou can identify the timeline, run state, failure class, and keyboard focus from the canvas within ten minutes and explicitly approves the design.

8. **Step 8:** Launch on `127.0.0.1:8765`, render a real Loop 0 intent/tool/outcome sequence, filter by run, confirm no non-loopback listener, confirm every non-GET request fails, and open the installed Dock page while the service runs.

##### 5. Decisions that belong to Michou

1. **Question:** Should bare `rm -rf` remain globally denied? **Options:** Keep the deny and use `kgme clean`, or allow path-scoped shell deletion. The first is slower but structurally safer. The second is convenient but relies on perfect command parsing. **Recommendation:** Keep the deny because `STATUS.md:37` records that it already prevented harm.

2. **Question:** What enforces Tier 1 isolation? **Options:** `age` encryption under the current user, or a separate `0700` macOS user plus encryption. Encryption protects rest but not a running same-user process. A separate user adds operational friction but creates an OS boundary. **Recommendation:** Evaluate and adopt the separate user unless the canary proves it unworkable, as ADR-013 §2 already directs.

3. **Question:** Which host egress tool should KGME standardize on? **Options:** LuLu, Little Snitch, or defer with no claim that network canaries are enforced. LuLu is free and simpler. Little Snitch offers finer observability at monetary and conceptual cost. **Recommendation:** Start with LuLu, but keep scheduling blocked until its per-worker behavior is demonstrated (`STATUS.md:41`).

4. **Question:** What is the third initial worker? **Options:** Choose from actual friction entries, nominate one now, or leave the charter review item open. Inventing one now violates the friction-led roadmap. Waiting preserves prioritization but delays the Phase 1 exit wording. **Recommendation:** Do not nominate until the log contains ten real entries (`phase-1-loop-0.md:31`; `friction-log.md:14-20`).

5. **Question:** When is the weekly review? **Options:** A fixed weekday and time, or an ad hoc review. A fixed slot is operationally legible. An ad hoc slot weakens the only mechanism for increasing autonomy. **Recommendation:** Choose a recurring thirty-minute slot before Phase 1 exit (`charter.md:84-90`; `STATUS.md:43`).

6. **Question:** Should cockpit v0 use the standard library or a pinned microframework? **Options:** `http.server` or Flask/FastAPI. The standard library minimizes dependency and abstraction cost. A framework makes later routing easier but imports conventions before v0 needs them. **Recommendation:** Use the standard library under ADR-015 and revisit only when Phase 2 routes justify it.

7. **Question:** Should hooks be Python or shell? **Options:** Python through `uv`, or POSIX shell. Python permits structured JSON parsing and testable path resolution. Shell is shorter but brittle for quoting, JSON, and symlinks. **Recommendation:** Use Python, with the shell limited to Claude Code’s command launcher.

8. **Question:** Does Loop 0 v1 contain any model call? **Options:** Fully deterministic, or model-written prose through the router. Determinism makes interruption and reconstruction tests meaningful. A model improves prose but introduces routing, cost, privacy, and nondeterminism before those layers exist. **Recommendation:** Keep v1 model-free, consistent with `phase-1-loop-0.md:22` and ADR-018.

9. **Question:** Is Codex review blocking? **Options:** Block on every finding, block only on ADR-016 blocking findings, or make review advisory. Blocking on everything repeats the punctuation-strike failure. Advisory review cannot enforce the plan’s stated gate. **Recommendation:** Block only on unresolved `blocking` findings and ledger the disposition of all others.

10. **Question:** Should the ledger rotate monthly or remain one file? **Options:** Monthly JSONL or one perpetual JSONL. Monthly files bound review and git-diff size. One file simplifies reading but contradicts the accepted durability design. **Recommendation:** Keep monthly rotation because ADR-012 §Decision has already settled it; changing it requires a superseding ADR.

11. **Question:** What should own the `kgme` shell name? **Options:** Preserve the directory alias, replace it with the CLI, or make the alias dispatch subcommands. Preserving it forces awkward CLI invocation. Replacing it changes established muscle memory. **Recommendation:** Make `kgme` the CLI and add `kgme-home` for navigation, after showing Michou the shell diff.

12. **Question:** Can Gate 4 pass before Codex and Python have real enforcement? **Options:** Require full cross-worker enforcement, or label early tests Claude-only. Full enforcement delays the gate but makes it truthful. Claude-only tests provide early evidence but cannot support unattended scheduling. **Recommendation:** Permit Claude-only tests as an intermediate milestone, but do not mark Gate 4 met under ADR-013.

##### 6. Proposed handoff sequence

1. **HANDOFF-0025, Phase 1 decisions and ledger schema:** Inputs are this review, STATUS, and ADR-003/012/013/015/017; outputs are Michou’s recorded decisions and any superseding ADR; acceptance is zero unresolved blocking design choices; reviewer is Codex.
2. **HANDOFF-0026, Repo policy baseline:** Inputs are ADR-008/013 and the global audit; outputs are settings, pre-hook, and tests; acceptance is the real path and command canary subset; reviewer is Codex.
3. **HANDOFF-0027, Package, configuration, paths, and ledger:** Inputs are ADR-003/012/015 and the v1 event schema; outputs are `pyproject.toml`, lockfile, configuration, CLI skeleton, and concurrency-safe ledger; acceptance is the 2,000-event test; reviewer is Codex.
4. **HANDOFF-0028, Post-tool ledger integration:** Inputs are HANDOFF-0026/0027; outputs are the sanitized post-hook and failure policy; acceptance is one real Claude tool call recorded without raw content; reviewer is Codex.
5. **HANDOFF-0029, Schema validator and `make check`:** Inputs are schema v1.1 and ADR-005/015; outputs are validator, fixtures, and Makefile; acceptance is the complete fixture suite; reviewer is Codex.
6. **HANDOFF-0030, Worker manifests and policy canaries:** Inputs are Michou’s Tier 1 and egress decisions; outputs are manifests and the cross-worker matrix; acceptance is every enforced cell passing; reviewer is Codex.
7. **HANDOFF-0031, Loop 0 and `kgme clean`, grouped CLI release:** Inputs are validated memory, ledger, and deletion policy; outputs are both commands and job tests; acceptance is the brief’s four tests plus clean containment; reviewer is Codex.
8. **HANDOFF-0032, Cockpit design canvas:** Inputs are the wishlist and frozen ledger schema; output is an approved canvas; acceptance is Michou’s explicit approval; reviewer is Michou, with Codex checking scope only.
9. **HANDOFF-0033, Cockpit v0 timeline:** Inputs are the approved canvas and ledger reader; outputs are the localhost read-only service and Dock instructions; acceptance is one real run rendered with no mutation route; reviewer is Codex.
10. **HANDOFF-0034, Phase 1 exit audit:** Inputs are Gates 3-5, one week of manual Loop 0 evidence, and the friction log; output is an audit report and STATUS update; acceptance is every exit criterion evidenced or explicitly carried forward; reviewer is Codex.

##### 7. The one thing you would change

I would amend the plan so the first deliverable is a single “execution substrate” handoff containing the package, root configuration, authoritative paths, concurrency-safe ledger, and event-schema contract, immediately followed by permissions and hooks wired to that substrate. The mechanism is dependency inversion: policy hooks, validators, canaries, jobs, cleaning, and the cockpit all call the same small effects layer instead of independently inventing paths, IDs, timestamps, logging, or failure behavior. This removes the step 1 circular dependency, makes `make check` and Codex review reproducible from the first code diff, and prevents the most expensive Phase 1 failure, which would be discovering during cockpit work that earlier components wrote incompatible or incomplete ledger events.