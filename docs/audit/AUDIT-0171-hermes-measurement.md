---
id: AUDIT-0171
type: report
status: final
handoff: HANDOFF-0073
author: claude-code
source: inferred
sources: ["HANDOFF-0073"]
tier: 2
created: 2026-11-18T00:43:00-08:00
period: 2026-11-18
---

# HANDOFF-0073 §1: what Hermes Agent can enforce (measurement)

*Michou relayed this report to Cowork from the `kgme session tight` run of 2026-11-18 (session note 00:39:54). Cowork recorded it here verbatim on 2026-11-18 at 00:58. Cowork's ruling on it is in HANDOFF-0073, "Rulings at adoption".*

Hermes Agent v0.23.2 (2026.9.24, stable) is installed from git at `~/.hermes/hermes-agent`, commit `ae2a81cc` dated 2026-11-16, with `_config_version: 53`. `~/.hermes` was readable. I read only the relevant parts of `config.yaml` with secret-shaped values masked, and I did not open `.env` or `auth.json`. No files were written.

**One thing to know before §2:** Hermes can run `git commit` in the repo today without asking. The allowlist at `config.yaml:2386-2402` includes `git add *` and `git commit *`, but that doesn't matter much. The allowlist only skips the prompt for commands Hermes already considers dangerous. Any other command runs with no prompt (`tools/approval.py:1441-1446`: no findings means approved).

**(a) Allow commands by pattern and refuse the rest: not through its approval settings, but yes through a hook.**
- The built-in approval system can only list commands to refuse. `approvals.deny` globs (`config.yaml:2403-2407`, enforced at `tools/approval_floors.py:25-44`) block even under `--yolo`, and the modes are only `manual`, `smart` and `off` (`tools/approval_context.py:276`). None of them refuses a command just because it isn't listed.
- The way to get an allowlist is a `pre_tool_call` shell hook under a `hooks:` key in the config (`agent/shell_hooks.py:286`). If the hook script exits with code 2, the tool call is blocked (`agent/shell_hooks.py:5`, `:41-44`), and setting `fail_closed: true` also blocks when the hook itself fails (`:148`). The hook gets the tool name and its arguments as JSON, so a script can allow `kgme …`, the read-only git commands and the read-only views, and block everything else inside `~/Projects/KGME/`.
- The first time each hook runs it needs your consent, stored in `shell-hooks-allowlist.json` (`:39`). Today there is no `hooks:` key in the config and `~/.hermes/hooks/` is empty.

**(b) Turn off file write and edit: yes globally; per folder only by listing where it may write, or with the same hook.**
- **Globally:** remove `file` from `platform_toolsets.cli` (`config.yaml:1461`). `code_execution` must go too. Its own approval text says scripts can "mutate files without passing through terminal command approval" (`tools/approval.py`, `_EXECUTE_CODE_DESCRIPTION` just after `:1478`).
- **Per folder:** the environment variable `HERMES_WRITE_SAFE_ROOT` lists the only folders the file tools may write to (`agent/file_safety.py:330-336`, applied at `:409-411`). Pointing it somewhere outside `~/Projects/KGME` would block writes into the repo. It covers the file tools only, not the terminal. The other option is a `pre_tool_call` hook that checks the path on `write_file` and `patch`.

**(c) Docker with a read-only mount, or another macOS user: both are in the code, but neither is usable today.**
- **Docker:** entries in `docker_volumes` are passed straight to `docker run -v` (`tools/environments/docker.py:857-867`), so `~/Projects/KGME:/workspace:ro` would work. `docker_run_as_host_user` adds `--user` (`docker.py:575-582`).
- Docker isn't installed on this Mac: `docker` isn't on PATH, and there is no OrbStack or Colima.
- A container also can't reach the Keychain item `Claude Code-credentials`, so `kgme` couldn't launch Claude Code from inside it. That breaks dispatch.
- A container with no host folders mounted skips the command guards entirely (`tools/approval.py:1408-1409`).
- **Another macOS user:** the local backend has no option to run as another user (no match in `tools/environments/local.py`). The only route is the SSH backend, with `ssh_host` and `ssh_user` (`tools/terminal_tool_backends.py:55`, required at `:206`), pointed at localhost as a second account. That needs Remote Login turned on and falls under HANDOFF-0038's Tier 1 evaluation.

**(d) Where it reads skills from:**
- `~/.hermes/skills/`, which is also where it creates new skills.
- Any folders listed under `skills.external_dirs` (`agent/skill_utils.py:357`; the example at `config.yaml:1166` is commented out). These are read-only.
- Inside a project, `<git root>/.hermes/skills` and `<git root>/.agents/skills` (`agent/skill_utils.py:517`), but only if that root is listed in `skills.trusted_project_dirs` (`:511-515`). Your config doesn't list it today.
- When names collide, the project copy wins, then local, then the creation folder, then external (`:503`).
- The repo already has `.agents/skills/` holding symlinks. Adding the repo to `trusted_project_dirs` and linking `kgme-conductor` there would be enough for §4.

**(e) Set `KGME_CONDUCTOR=hermes` for every terminal command: yes, though I read this in the code and didn't test it.**
- **Local backend:** terminal commands inherit Hermes's own environment (`tools/environments/local.py:349-352`). Names that look like secrets or start with `HERMES_` are filtered out (`:279-309`; `tools/environments/local_env_policy.py:600`), and `KGME_CONDUCTOR` matches neither. `~/.hermes/.env` is loaded into that environment by `hermes_cli/env_loader.py`, so one line there would do it. The gateway is already running and would need a restart to pick it up.
- **Docker backend:** use `docker_env` (`tools/terminal_tool_backends.py:70`).
- **Fallback:** a `pre_tool_call` hook can also rewrite the command to set the variable.

**What this means for §2:** Hermes can enforce the fence itself, with no Docker and no second user. That takes three changes in your home folder. First, remove `file` and `code_execution` from the CLI toolsets. Second, add a `pre_tool_call` hook with `fail_closed: true` that allows only the listed commands inside `~/Projects/KGME/`. Third, remove `git add *` and `git commit *` from `command_allowlist`.

One limit to state in the audit: the hook runs inside Hermes's own process, so it is weaker than a separate macOS user.

This needs your ruling: if you accept the hook as the fence, §2 can proceed without the Docker-or-second-user choice the handoff reserves for you.