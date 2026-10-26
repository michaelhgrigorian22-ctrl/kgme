---
id: AUDIT-0144
type: report
status: final
handoff: HANDOFF-0062
author: claude-code
source: inferred
sources: ["HANDOFF-0062", "control/git-hooks/post-commit", "kgme/mods.py", "tests/test_hook_path.py", "logs/scratch/merge/trial-1d391c743bc6.log"]
tier: 2
created: 2026-10-26T13:31:38-07:00
period: 2026-10-26
---

# HANDOFF-0062: the merge trial finds `claude`

**State: ready, diffs pending.** The fix is one line in a human path. The new test is red on `main` until that line lands, so it ships with the line in one commit for Michou. The handoff closes by observation: the design branch lands after that commit.

## The measurement (§1), first
- **`which -a claude`:**

  ```
  /Users/michaelgrigorian/.nvm/versions/node/v25.9.0/bin/claude
  ```

  One answer: 2.1.310 (Claude Code), a symlink to `../lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`, a native Mach-O arm64 binary. The stale 2.1.111 of the Housekeeping item is no longer on this machine.
- **The hook's view,** `sh -c 'PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"; command -v claude; echo $?'`:

  ```
  1
  ```

  Not found, so the cause is the one the handoff names, not the trial's `env` or `kgme/merge.py`.
- **The binary needs nothing else.** Called by its full path under the hook's line, `claude --version` answers `2.1.310 (Claude Code)` with exit 0, so its folder is all the line lacks; no `node` is needed. Under the same line `uv`, `gh`, `git` and `make` resolve, and `node` and `codex` do not, which nothing on the hook path calls.
- **Reproduced:** `main`'s `python -P -m kgme.mods` under the hook's line prints the trial log's two lines exactly (`logs/scratch/merge/trial-1d391c743bc6.log`, lines 213 and 214): `mods/kgme-capture: claude is not on PATH, so the mod cannot be validated [blocking]`, the same for `kgme-cockpit`, then `kgme mods: 2 mod folders, 2 blocking`.

## The fix (§2), the route chosen
The hook's `PATH` line gains `$HOME/.nvm/versions/node/v25.9.0/bin`, the folder the measurement names: `control/git-hooks/post-commit`, a human path, as `logs/scratch/handoff-0062/post-commit.diff`.
- **The check is not weakened.** The mod step still runs `claude plugin validate` in the trial, and a mod it would refuse still blocks. No route that passes when `claude` is absent was considered.
- **Why not route 2b,** the `kgme.toml [mods]` key: it would fix the mod step alone. The line also lets the trial run the one test that needs the real `claude`: `test_planting_a_tool_call_hook_turns_the_check_red`, skipped under the old line and run under the new.
- **The cost:** the folder carries the Node version, so a Node upgrade through nvm moves `claude`. That is §3's test's case: red in the shell, before a trial.

## The check (§3)
`tests/test_hook_path.py` reads the hook's one `PATH="..."` line from the file, never retyped, expands `$HOME`, and resolves on it every tool the hook path runs:
- the hook's own commands that are no shell builtin: `git`, `uv`, `mkdir` and `date` (`printf`, `trap`, `[`, `exit` and `export` are builtins);
- `make`: the trial's check;
- `gh`: git's credential helper when the hook's sync pushes;
- `claude`: `make check`'s mod step.

The checker is shown to catch a missing tool: for each tool, a copy of the line without every folder that holds it reports the tool missing. A file that sets `PATH` more or fewer than once is refused.

It is `tests/test_hook_path.py` in `logs/scratch/handoff-0062/test_hook_path.diff`, to land with the line. On `main`'s current line it is red, reporting `['claude']`, the trial's failure, in the shell. On the new line it is green.

## Acceptance
- **`sh -c` with the new line finds `claude`:** `/Users/michaelgrigorian/.nvm/versions/node/v25.9.0/bin/claude`, exit 0.
- **The new test** is red with a tool's folder removed from a copy of the line (7 cases, one per tool), red on `main`'s line (`claude`), and green on the new one.
- **A fresh clone of `main` passes `make check` under the hook's environment,** with both diffs applied and `PATH` replaced by the hook's line, as a hook does: lint 0 blocking, `kgme mods: 2 mod folders, 0 blocking`, 697 passed, none skipped (`make-check-hook-path.txt`).
  - **A harsher first attempt** cleared the whole environment with `env -i`, beyond what a hook does. The mod step passed, but two guard tests failed because `TMPDIR` was gone and their temporary files landed in `/private/tmp` (`make-check-hook-env.txt`). That is an artefact of the emulation, not of the line.
- **The design branch level with `main` after one commit:** by observation, after Michou's commit. That closes the handoff.

## Waiting for Michou
1. **`logs/scratch/handoff-0062/post-commit.diff` and `test_hook_path.diff`,** in one commit: the line and its test. The test alone would turn `main` red until the line lands.
2. **`kgme sync` once,** for the merge-trial events since `1d391c7`, as the handoff asks.

## The review
`kgme review` ran in the acceptance clone (`logs/scratch/handoff-0062/clone`), where the line and the test are applied, because on `main` the test is red until the line lands and a red gate is not reviewed. The review's own ledger events stay in that clone.

## Review cycle 1 (AUDIT-0145, BLOCK on F1), fixed
- **F1:** the inventory missed the hook's own `mkdir` and `date`. It now lists every command the hook runs that is no shell builtin, plus what its children run.
  - **Red on the cycle-1 test:** on a copy of the hook whose line lacks `/bin`, it reported nothing missing, so it was green while the hook could no longer run.
  - **Green on the fix:** the fixed test reports `['mkdir', 'date']` (`logs/scratch/handoff-0062/red-c1.txt`).
- **F2 (cosmetic):** the helpers that read the filesystem are `read_where` and `read_missing`, each documented; the pure parser is `parse_path_line`; the module's side effects now say it reads.

## Review cycle 2 (AUDIT-0146): PASS
- **No finding left.** The report and the two review audits are committed on `main`. The line and its test stay in the bundle for Michou: `logs/scratch/handoff-0062/post-commit.diff` and `test_hook_path.diff`, one commit, with the test as reviewed in AUDIT-0146.
- **State:** open, ready, diffs pending. The handoff closes by observation, once the next commit on `main` after Michou's lands the design branch through the hook's trial (or `kgme merge design` by hand). That follow-up names the landing commit and the green trial log.

## Closed by observation, 2026-10-26
- **Michou's `9f94e7c`** (13:50:45) lands the line and `tests/test_hook_path.py`.
- **Its post-commit hook,** running under the new line, landed the design branch: `fa14949` "merge: design 70b3412b00bf (kgme merge)", 13:50:48, the six design commits merged into `main` at `8b4a566`. `design` is level with `main` (`git rev-list --count main..design` is 0).
- **The green trial.** `kgme merge` writes a trial log only for a red trial (`kgme/merge.py`, lines 124–127), so a green one has no `trial-*.log`. Its record is the sync log and the ledger:
  - `logs/scratch/sync.log`, line 455: "merge design 70b3412b00bf (6 commits) into main 8b4a566d2453: merged as fa14949df4a6; make check green on the trial merge";
  - the merge job's intent (13:50:48) and `ok` outcome (13:52:59) in the ledger, key `merge:design:70b3412b00bf3ff9f0b2ac9bfa7edafea1374b55`.

  The last red trial before the fix is `trial-69c6c729cf78.log` (13:45:45), still "claude is not on PATH".
- **A redundant run of mine.** Michou's commit reached my checkout by `git pull`, which runs no hook, and I had not yet seen `fa14949`, so I ran `kgme merge design` by hand under the hook's own `PATH` line. It answered "main holds every design commit; nothing to do" and wrote nothing.
- **`make check` on `main`,** now with `tests/test_hook_path.py`: lint 0 blocking, `kgme mods: 2 mod folders, 0 blocking`, 743 passed.
- **The handoff closes** with `completed:` set to the PASS review's `created` (AUDIT-0146, 2026-10-26T13:42:16-07:00).

