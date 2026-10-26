---
id: READER-SESSIONS
type: note
status: active
created: 2026-10-21T16:00:00-07:00
modified: 2026-10-26T01:25:07-07:00
author: claude-code
source: inferred
sources: ["ADR-022", "ADR-024", "HANDOFF-0047", "HANDOFF-0059", "kgme/session.py", "kgme/session_read.py", "kgme/mods.py"]
tier: 2
---

# Reader: session levels

*Written 2026-10-21 by Claude Code for HANDOFF-0047. The decision is ADR-022.*

## What it is
A session's allowance is a named level, started by one command and recorded in the ledger. `kgme session <level>` builds one `claude` command line and hands the terminal to it. Plain `claude` is unchanged and is not a level.

| Level | Mode | What it allows | For |
|---|---|---|---|
| `tight` | plan | no edits; auto and bypass disabled | reading, planning, review |
| `work` | auto | the sandbox on and admin-required, writing to the repository and the temp folder; the guard as always | the interactive builder |
| `loose` | dontAsk, headless | one handoff: writes only to its `Outputs`, `tests/`, and `logs/scratch/`; a pinned list of tools; no network beyond the model; a turn cap and a spend cap | unattended builders (HANDOFF-0043, 0048) |

`crew`, the mode that plans, dispatches builders in worktrees, and stops at your approval, is HANDOFF-0048.

## How it starts
`kgme session work` runs `claude --setting-sources project,local --settings <run copy> --permission-mode auto --model <builder>`:
- **`--setting-sources project,local`** keeps your user settings, with their broad allows and `auto` default, out of the session; your sign-in is unaffected.
- **The run copy** is the level's template from `control/policy/sessions/`, written into `logs/scratch/sessions/<run>/` with absolute paths filled in.
- **The model** comes from `kgme.toml [models] builder`.

`kgme session loose --handoff HANDOFF-NNNN -- "<prompt>"` adds `-p --permission-prompts none --max-turns` and `--max-budget-usd` from `kgme.toml [sessions]`. It fences the sandbox, the `Edit` allows, and the guard (rule 5) to the same list: the handoff's `Outputs`, `tests/`, and `logs/scratch/`. It starts only from a worktree of this repository outside the main checkout, and with `--setting-sources local` in place of `project,local`: Claude Code merges allow lists across settings files, so the project's own allows would join the pinned list. What `loose` needs from the project it carries from the main checkout's committed files instead: the run copy holds the project's hooks and deny list, and the committed `CLAUDE.md` is passed with `--append-system-prompt-file` (ADR-022, addendum of 2026-10-21). A `loose` builder never stages or commits: `git add` and `git commit` are not on its list, and the loop that started it commits the reviewed diff (HANDOFF-0043). The sandbox alone would not stop it: from a worktree, Claude Code lets sandboxed commands write the repository's shared git directory (all but its hooks and config), a residual recorded for HANDOFF-0048.

Before `claude` starts, one ledger note records the level and the run copy's sha256. Its payload holds the full command line, the template and its sha256, `claude --version`, and the model. `--dry-run` prints the command line and the settings and starts nothing.

## Who changes a level
The templates and `kgme.toml` are human paths: an agent proposes a change as a diff, and you apply it. Widening a level is a weekly-review ruling; narrowing one may be proposed by anyone.

## Mods: the cockpit pane and `/capture`
- **What a level loads.** A `work` session loads two mods from `mods/`, each passed as `--plugin-dir`. A `tight` session loads the pane alone. `loose` and the cheap lane load none, whatever `kgme.toml [mods]` says.
- **The pane** opens beside the chat and shows what `kgme cockpit` serves:
  - the open runs and their states;
  - the last events;
  - an amber line while an intent waits for its outcome;
  - a magenta line while a run is blocked.

  It decides no state, and it binds no key. Start `kgme cockpit` first. Without it, the pane says the server was not reached and keeps the last snapshot. The status line shows the newest run's state.
- **`/capture <kind> <words>`** runs `kgme capture` with your words as typed (one pair of quotes around them is dropped) and prints what it printed. It is the only process a mod starts, and its tool call goes through the hooks and the ledger like any other.
- **What a mod may do** is written in `kgme.toml [mods.allows]`. `make check` validates every mod and blocks one that hooks or calls more (ADR-024).

## One ledger whatever the checkout
The ledger, trace, and test streams resolve from the repository's git common directory, so a session in any worktree of this repository writes to the main checkout's `logs/`. Outside a git repository the hooks refuse, as the guard always has.

## The cheap lane: a cloud model, code only
*Added 2026-10-24 for HANDOFF-0053.*

A model whose provider `kgme.toml [providers]` marks `code` (today `ollama-cloud`, which serves DeepSeek-V4.1-Flash) starts only as `kgme session work --model cheap --red "<command>"`. Every other route refuses it, including `--model cheap` without `--red` and naming it as the default builder. Every token such a session reads leaves the machine for Ollama's servers, so it sees code and documents, never `memory/`, `logs/`, or a Tier 1 path (Michou's ruling, 2026-10-21).

- **The export.** `HEAD` minus `memory/` and `logs/` (bar `memory/templates/`, which the tests read) is extracted into `work/cheap-<run>/` and committed there as its own one-commit repository, so no history of either is reachable from it.
- **The session.** `claude` starts in the export with `ANTHROPIC_BASE_URL` at the local Ollama server and every model slot on the cheap model. Its settings deny `Read` and `Edit` on the brain, the design worktree, `~/Projects/Finance`, and every Tier 1 root, add the same roots to the sandbox's `denyRead`, and allow no Bash network. The prompt is: make the red command exit 0 without editing the test it names, and stop on green, on the turn cap, or when a fix needs a file outside the export.
- **The hooks.** The guard and ledger hooks run the main checkout's code (`python -P`, so the export's own `kgme/` is never imported), so the session cannot edit them and its events land in the main ledger. The guard judges paths against the export, which the launcher names in `KGME_GUARD_ROOT` on the guard's command line alone; the guard honours it only for a folder under `work_dir` outside the main checkout.
- **The fix.** On exit the change comes home as `logs/scratch/cheap/<run>/fix.patch` with the red command's final output, never as a commit. The builder applies it in the real checkout, runs `make check`, and `kgme review` judges it as any diff. The launcher's own run of the red command, which executes the session's code, can write the export, the temporary folders and `/dev`, and never the main checkout, wherever it lives (HANDOFF-0057).

Start and end notes record the provider, model, export tree hash, denied roots, red command, exit reason, turns, and the patch's sha256. Deleting `[models] cheap` turns the lane off.
