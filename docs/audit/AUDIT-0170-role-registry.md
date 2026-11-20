---
id: AUDIT-0170
type: report
status: final
handoff: HANDOFF-0071
author: claude-code
source: inferred
sources: ["HANDOFF-0071", "ADR-025", "kgme/roles.py", "kgme/roles_io.py", "kgme/roles_run.py", "kgme/atlas.py", "kgme/atlas_read.py", "kgme/cli.py", "kgme/cli_parser.py", "tests/roletools.py", "tests/test_roles_lint.py", "tests/test_roles_agent.py", "tests/test_roles_run.py", "tests/test_smoke.py"]
tier: 2
created: 2026-11-18T00:30:27-08:00
period: 2026-11-18
---

# HANDOFF-0071: the role registry

The registry is built and staged, uncommitted (the staged code diff before this report was added: sha256 prefix `a3165221e6f82c40`, 22 files, 1284 insertions, 7 deletions). Every acceptance step ran in a clone carrying that diff, and steps 1, 2, 3 and 5 passed outright; step 4 started a real `claude` child and wrote the role-carrying events around it, but the child could not authenticate from this session's sandbox, so the live model turn is Michou's to run. The gate, `kgme review --handoff HANDOFF-0071`, has not run a cycle: this session's sandbox denies `~/.codex/auth.json` and `make check` cannot go green here for reasons that predate this diff (section "Gate"). No PASS exists yet, so the handoff stays `open`.

## What was built
- `roles/`: `build/planner.toml` (manager, `tight`, `strong`), `build/builder.toml` (`loose`, `inherit`), `build/integrator.toml` (`tight`, `standard`), `audit/auditor.toml` (`tight`, `strong`, escalates to `michou`), each with a rubric under `rubrics/`; `templates/role.toml`, `templates/rubric.md`, `templates/skill.md`.
- `kgme/roles.py` (pure, 244 lines): the role pass. Every rule of §2 is `blocking`; a field the registry does not know is `advisory`.
- `kgme/roles_io.py` (222 lines): the reads (roles from the index or the tree, levels, profiles), `read_findings`, `kgme agent list|show|new`.
- `kgme/roles_run.py` (197 lines): `kgme agent run`.
- `kgme/lint.py` is unchanged: the call into the role pass sits in `kgme/cli.py`'s `run_lint`, beside the coherence, toolbox and skills passes it already calls, index by default and working tree under `--all`, as the rulings at adoption require.
- `kgme/atlas.py`: role nodes (`role`), department nodes (`department`), a `michou` node (`head`), edges to the escalation target and the skill.
- `skills/kgme-auditor/`: the auditor's stub skill (§4 of the handoff). HANDOFF-0064's three skills were already applied (`skills/kgme-planner`, `kgme-builder`, `kgme-integrator`, and `.claude/agents/kgme-*.md`, commit e6916c6), so nothing was applied first.
- `tests/test_roles.py`: 32 tests, red first (collection failed on `kgme.roles` before any code existed), all green. Split after review cycle 1 (F7) into `tests/test_roles_lint.py`, `test_roles_agent.py` and `test_roles_run.py`, with `tests/roletools.py`; see "Review cycle 1" below.

## Route decisions, scored (ADR-023)
Each is stakes (1 to 5) × edge (0 to 1); none reached 1.5, so none was asked. Those at or above 0.5 are listed for the approval screen.

| Decision | Why | Stakes × edge |
|---|---|---|
| `kgme/atlas_read.py` gains one line so `roles/*.toml` reach the atlas | `read_sources` filters to six roots and three suffixes; the atlas branch in `kgme/atlas.py` sees nothing under `roles/` without it. Outside the literal Outputs; the handoff's §5 and §6 need it. | 2 × 0.3 = 0.6 |
| `kgme/roles.py` is split into `roles_io.py` and `roles_run.py` | ADR-015: about 300 lines a file, effects quarantined from logic; one file would be about 660 lines. | 1 × 0.1 = 0.1 |
| `tests/test_smoke.py` names `agent` | It pins the subcommand set; a new subcommand fails it by design. One entry and the count in the test's name. | 1 × 0.05 = 0.05 |
| `strong`, `standard` and `inherit` all resolve to `[models] builder` (`claude-opus-5-5`); `cheap` is refused after review cycle 1 (F3) | `[models]` names one Claude model; inventing a model id for `standard` would be a fabricated value. Michou may want a `standard` key in `kgme.toml` (a human path). | 2 × 0.4 = 0.8 |
| Two lint rules beyond §2: one manager per department, and `model = "cheap"` refused (after review cycle 1, F3: `cheap` is not a role level in v1) | ADR-025 §1 says one manager per department; `kgme session` already refuses a code-class model outside the cheap lane (HANDOFF-0053), so such a role could never run. | 2 × 0.2 = 0.4 |
| `agent run` starts the session as a child process, never `exec` | The outcome event has to be written after the session ends. | 1 × 0.1 = 0.1 |
| `--print` (headless `claude -p`) is `tight`'s only | At `work` or `loose`, a headless run would be an unattended write the level does not grant at `work`; at `tight` nothing can be written. | 3 × 0.2 = 0.6 |
| The session's own hook events link to the role through `KGME_LOOP_PARENT` | HANDOFF-0063's parent link already nests a session's first hook event under a named intent; reusing it means no hook code changes. The name says "loop"; the mechanism is general. | 2 × 0.3 = 0.6 |
| The role's skill, slice and identity reach the model as one `--append-system-prompt-file`, after the committed `CLAUDE.md` a `loose` launch already carries | One file, recorded with its sha256 in the run's payload. | 1 × 0.1 = 0.1 |
| `agent new` writes a stub skill `skills/kgme-<department>-<role>/` | Lint requires the skill to exist, and step 1 requires a lint-clean role; the stub is what "prints what is still missing (the skill body)" points at. | 2 × 0.2 = 0.4 |
| Levels of the declared roles: planner and integrator `tight`, builder `loose`, auditor `tight` | The crew runs the planner read-only in plan mode (`kgme/crew_io.py` `planner_argv`); the integrator reads and writes one screen to the session; the builder is the loose route; the auditor reads the ledger. Under the ruling, `tight` allows no Bash, so the integrator reads the ledger files rather than running `kgme ledger read`. | 2 × 0.3 = 0.6 |

## Acceptance test: commands and output
Run in a clone of the main checkout with the staged diff committed on top (`37a696c`), under the session scratchpad, with the clone's own `kgme` first on `PYTHONPATH` (`kgme.paths.root()` printed the clone). The clone was needed because `agent new` writes to the tree and `agent run` writes to the ledger; it is outside `logs/scratch/` because the sandbox refuses writes to a `.git/config` inside the repository.

### 1. `kgme agent new finance analyst` writes a role and rubric that pass lint
```
$ kgme agent new finance analyst
wrote roles/finance/analyst.toml
wrote roles/finance/rubrics/analyst.md
wrote skills/kgme-finance-analyst/SKILL.md
wrote skills/kgme-finance-analyst/lessons.md
still missing: the skill body in skills/kgme-finance-analyst/SKILL.md, the purpose in roles/finance/analyst.toml, and the department's own rubric dimensions
exit 0

$ kgme lint --all   (role lines and summary)
kgme lint: 368 notes, 0 blocking, 239 advisory, 8 cosmetic
exit 0
```

### 2. Widening `tools` past the level fails lint as blocking, and so does `tier_max = 1`
```
# step 2a: widen tools past tight
tools = ["Read", "Grep", "Glob", "Bash", "Edit"]
$ kgme lint --all
roles/finance/analyst.toml: role [blocking] `Bash` is not allowed at tight; it allows Glob, Grep, LS, Read, TodoRead
roles/finance/analyst.toml: role [blocking] `Edit` is not allowed at tight; it allows Glob, Grep, LS, Read, TodoRead
kgme lint: 368 notes, 2 blocking, 239 advisory, 8 cosmetic
exit 1

# step 2b: tools restored, tier_max = 1
tools = ["Read", "Grep", "Glob"]
tier_max = 1
$ kgme lint --all
roles/finance/analyst.toml: role [blocking] tier_max = 1: Tier 1 is never a role's to claim (ADR-021, ADR-025 §3)
kgme lint: 368 notes, 1 blocking, 239 advisory, 8 cosmetic
exit 1

# tier_max restored to 2
kgme lint: 368 notes, 0 blocking, 239 advisory, 8 cosmetic
exit 0
```

### 3. `kgme agent list` shows Build (3), Audit (1) and Finance (1)
```
$ kgme agent list
Audit (1)
  audit.auditor            worker   tight  strong   Score a run's trace in the ledger against its role's rubric; answers to Michou, outside every department.
Build (3)
  build.planner            manager  tight  strong   Plan one adopted handoff for the crew as tasks the plan gate parses; dispatch and review, never build.
  build.builder            worker   loose  inherit  Build one crew task inside its Outputs, red first, to a PASS review and one commit by pathspec.
  build.integrator         worker   tight  standard Read a crew run's integration branch, gate and diff, and write the one approval screen.
Finance (1)
  finance.analyst          worker   tight  inherit  One line: what finance.analyst is for.
exit 0

$ kgme agent show build.builder   (the tail)
# allowed at loose: Bash, Edit, Glob, Grep, Read
# model: claude-opus-5-5
# chain: build.builder -> build.planner -> michou
```

### 4. `kgme agent run build.integrator "summarise the last crew run"` starts a session whose ledger events carry the role id
The dry run shows the launch (clone path shortened to `<clone>`):
```
$ kgme agent run build.integrator "summarise the last crew run" --dry-run
claude --setting-sources project,local --settings <clone>/logs/scratch/sessions/01M7PW8M0EZJD0C8H8QFDE28ES/tight.json --permission-mode plan --model claude-opus-5-5 --plugin-dir <clone>/mods/kgme-cockpit --append-system-prompt-file <clone>/logs/scratch/sessions/01M7PW8M0EZJD0C8H8QFDE28ES/role.md summarise the last crew run
```
The prompt file opens `# Role: build.integrator (worker, department build)`, names the chain `build.integrator -> build.planner -> michou`, then carries `# kgme-integrator` (the skill) and `# Atlas slice: kgme/crew_io.py + kgme/approve.py`.

The live run, headless because this shell has no terminal:
```
$ kgme agent run build.integrator "summarise the last crew run" --print
Not logged in · Please run /login
exit 1
```
`claude` started and exited 1 because this session's sandbox hides the Keychain. The three ledger events of that run, from the clone's `logs/ledger/2026-11.jsonl`:
```
{"id": "01M7PW92G9PG1G2MR07FMEVXVS", "run_id": "01M7PW91G86DJK7PKRGRW4HQRE", "actor": "kgme.agent", "kind": "intent", "job": "agent:run", "key": "agent:build.integrator", "parent": null, "summary": "agent build.integrator at tight, model claude-opus-5-5: summarise the last crew run"}
{"id": "01M7PW92GZPQNFBK6Z6K6G8RMW", "run_id": "01M7PW91G86DJK7PKRGRW4HQRE", "actor": "kgme.session", "kind": "note", "job": "session", "key": "session:tight", "summary": "session tight: settings sha256=aa5a6ee46877d48d model=claude-opus-5-5"}
{"id": "01M7PW93JK2HHHRG5M24CT4EQN", "run_id": "01M7PW91G86DJK7PKRGRW4HQRE", "actor": "kgme.agent", "kind": "outcome", "status": "error", "class": "blocking", "job": "agent:run", "key": "agent:build.integrator", "parent": "01M7PW92G9PG1G2MR07FMEVXVS", "summary": "agent build.integrator: exit 1"}
```
The session note's payload carries `"role": "build.integrator"`, `"level": "tight"`, `"headless": true` and the role prompt's sha256. That the session's own hook events nest under the intent through `KGME_LOOP_PARENT` is shown by `test_run_writes_intent_and_outcome_events_carrying_the_role_id` (the child's environment names the intent's id) and by HANDOFF-0063's existing hook tests; no hook event exists in this run because the child never reached a tool call. **Open for Michou:** the interactive run, `uv run --frozen kgme agent run build.integrator "summarise the last crew run"`, in his own terminal, then `kgme ledger read --stream ledger | grep agent:build.integrator`.

### 5. The atlas shows the org chart
```
$ kgme atlas
kgme atlas: 593 nodes; 593 written, 0 unchanged, 0 removed
exit 0
```
`atlas/department/department-build.md` links `role-build.builder`, `role-build.integrator` and `role-build.planner`; `department-audit.md` links `role-audit.auditor`. `role-build.builder` and `role-build.integrator` link `role-build.planner`; `role-build.planner` and `role-audit.auditor` link `michou` (`atlas/head/michou.md`); each role links its `skill-kgme-*` node. The three new kinds (`role`, `department`, `head`) are Obsidian colour groups.

## Gate
- `ruff check .` and `ruff format --check .`: clean.
- `kgme lint` (index, with the staged roles) and `kgme lint --all`: 0 blocking.
- `tests/test_roles.py` and `tests/test_smoke.py`: 40 passed.
- `make check` does not pass in this session, for two reasons that predate this diff. First, `python -P -m kgme.mods` reports `mods/kgme-cockpit: hooks or calls its handoff did not name: ui.render (default matcher key: plugin) [blocking]`, identically on a clone of HEAD `6a4683c` without this diff. Second, the full suite here (`pytest -q tests -m "not agents"`) ends 26 failed, 76 errors, all in 14 files: `test_server.py`, `test_design_precision.py`, `test_loop.py`, `test_loop_codex.py`, `test_cheap*.py`, `test_guard_decisions.py`, `test_adapters.py`, `test_atlas.py`, `test_merge.py`, `test_sync*.py` and `test_workspace.py`. The same 14 files, run on a clone of HEAD with HEAD's own code first on `PYTHONPATH`, end 25 failed, 190 passed, 76 errors, with the same test ids. The one extra here, `test_atlas.py::test_c1_f6_a_relative_project_resolves_against_the_checkout`, makes a folder beside the checkout (`ROOT.parent`), which is writable for a temp clone and refused by this sandbox for `~/Projects/KGME/`. Every one of these needs a local port, the network, or a write outside the repository, which this sandbox refuses. None names a file this diff touches. One failure was this diff's: `test_smoke.py` pins the subcommand set, and it now names `agent`.
- `kgme review --handoff HANDOFF-0071 --dry-run`: resolves the handoff and the staged diff, reviewer `gpt-6-astra`, nothing written. No real cycle ran: `codex exec` cannot read `~/.codex/auth.json` from this sandbox, and a cycle that fails on the environment would still take an AUDIT number.

## Human paths, as diffs for Michou
Both under `logs/scratch/handoff-0071/`, checked with `git apply --check` against the main tree, then applied in the clone where `kgme lint` (with the coherence check) reported 0 blocking.
- `claude-md.diff`: one line in `CLAUDE.md`'s repository map, under `control/`: `roles/               COMMANDS: one file per agent role, its rubric beside it, linted (ADR-025, HANDOFF-0071)`. Until it lands, the coherence check does not recognise `roles/...` paths in documents as this repository's, so it neither checks nor flags them.
- `readers-roles.diff`: the new reader `docs/readers/roles.md` (fields, how a level's tools are derived, the commands, the ledger trail, the org chart, what is declared).
Apply with `git apply logs/scratch/handoff-0071/claude-md.diff logs/scratch/handoff-0071/readers-roles.diff`.

## Residue
- `logs/scratch/handoff-0071/accept/` and `accept-failed-1/` are two partial clone folders from the first attempt, refused halfway by the sandbox; deleting them was refused by the session's permissions. Both are under the gitignored scratch.
- On the first acceptance attempt, `uv run` inside the clone ran the main checkout's code (this session's environment sets `UV_PROJECT` to the main checkout), so `agent new finance analyst` wrote four files into the main tree; they were removed at once (`roles/finance/`, `skills/kgme-finance-analyst/`), and the main tree holds no finance role.

## Review cycle 1 (AUDIT-0173, BLOCK) and its fixes
Cowork ruled as arbiter in the handoff: F1, F2, F4, F5, F6 and F7 accepted as written, F3 ruled narrower. Each fix went red first: 23 of the 53 tests in the split modules failed before any code changed.
- F1: the outcome carries `ref` to its intent as well as `parent`, so `ledger.open_intents("agent:run")` is empty after a run that succeeds and one that fails.
- F2: `kgme agent run` narrows the launch itself. `--tools <role tools>` (right after `claude`, where the variadic flag cannot swallow the task) and `--strict-mcp-config` go on the argv; the run copy of the level's settings keeps only the allow rules of the role's tools and denies every other tool the level, the role's profile or `claude-builder` names; the note's `settings_sha256` is the narrowed copy's. A scoped rule (`Bash(make check)`) and a profile's path or network fences other than `claude-builder`'s at `work` are refused before anything is written. `claude --help` on this machine lists `--tools <tools...>`: "Built-in tools to make available". Residual: a level that loads mods still passes `--plugin-dir`; whether `--strict-mcp-config` also drops a plugin's own MCP servers is unmeasured.
- F3 (narrower): `cheap` is not a role level. Lint blocks `level = "cheap"` and `model = "cheap"` by name, `kgme agent run` refuses it, and `run_cheap_role` is deleted.
- F4: everything after the intent runs under one handler: a preparation or launch failure (`OSError`, `ValueError`, `SubprocessError`) is a `blocking` outcome and exit 2, an interruption a `transient` one and exit 130, anything else is recorded and raised.
- F5: string fields are type-checked first and a wrong-typed one is then judged absent; `parse_roles` keys a role with a non-string `id` by its path.
- F6: the default pass reads the index's blobs (`git cat-file blob :<path>`) for roles and rubrics; `--all` reads the working tree. Levels and profiles stay working-tree reads, as `kgme session` reads them at launch.
- F7: tests split by concern, helpers renamed with effect prefixes (`run_git`, `write_file`, `read_role_findings`, `read_blocking`, `make_run_settings`) and fully annotated; `kgme/roles.py` 276, `roles_io.py` 250, `roles_run.py` 274 lines.
- The pending reader diff `logs/scratch/handoff-0071/readers-roles.diff` is updated to match (no `cheap` level; the launch's narrowing).

Gate after the fixes: `ruff check`, `ruff format --check`, `kgme lint` (0 blocking) clean; the role, smoke, lint, session and atlas-slice suites 125 passed. The full `pytest -m "not agents"` in this sandbox: 885 passed, 25 failed, 76 errors, every one a sandbox refusal in a suite that imports no role module (live `claude`/`codex` calls, `git worktree add`, process-group kills through `ps`, push hooks, Chrome).
