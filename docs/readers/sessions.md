---
id: READER-SESSIONS
type: note
status: active
created: 2026-10-21T16:00:00-07:00
modified: 2026-10-21T16:00:00-07:00
author: claude-code
source: inferred
sources: ["ADR-022", "HANDOFF-0047", "kgme/session.py"]
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

`kgme session loose --handoff HANDOFF-NNNN -- "<prompt>"` adds `-p --permission-prompts none --max-turns` and `--max-budget-usd` from `kgme.toml [sessions]`. It fences the sandbox, the `Edit` allows, and the guard (rule 5) to the same list: the handoff's `Outputs`, `tests/`, and `logs/scratch/`. A `loose` builder never stages or commits: `.git/` is outside its sandbox, and the loop that started it commits the reviewed diff (HANDOFF-0043).

Before `claude` starts, one ledger note records the level and the run copy's sha256. Its payload holds the full command line, the template and its sha256, `claude --version`, and the model. `--dry-run` prints the command line and the settings and starts nothing.

## Who changes a level
The templates and `kgme.toml` are human paths: an agent proposes a change as a diff, and you apply it. Widening a level is a weekly-review ruling; narrowing one may be proposed by anyone.

## One ledger whatever the checkout
The ledger, trace, and test streams resolve from the repository's git common directory, so a session in any worktree of this repository writes to the main checkout's `logs/`. Outside a git repository the hooks refuse, as the guard always has.
