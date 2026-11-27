---
id: HANDOFF-0078
type: handoff
created: 2026-11-27T12:50:00-08:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0073]
---

# Proposal 0078: The Desktop fence, measured first, then built in the policy

## Why
- **Hermes Desktop is not fenced** (AUDIT-0180, 2026-11-24, 15:34 to 15:42). In a Desktop chat in a project rooted at brain, after `hermes gateway restart` and with the hook's consent on file, `echo /Users/michaelgrigorian/Projects/KGME/brain/fence-check` ran with exit 0 and no fence message. The CLI refuses the same call: it has no absolute `workdir`, so the fence counts it as inside, and `echo` is not a command the conductor runs there. Desktop shows its tools as `mcp__terminal`, `mcp__write_file`, `mcp__execute_code` and the like, and had two MCP servers that run code (`node_repl`, `computer-use`).
- **Two rules of the fence assume the CLI's names.** `judge` in `kgme/hermes_fence_policy.py` matches tools by their bare names, so `mcp__terminal` would fall to `judge_other`. That rule allows any tool that names no relative path and no path inside the root, so a tool that runs code without naming a path passes, wherever it runs.
- **A missing paths file stops all of Hermes, not only KGME work.** A missing or malformed `~/.hermes/hooks/kgme-fence.paths` refuses every call, outside the repository too (AUDIT-0180, "Narrower than the ruling", score 0.6, listed). The file matters only when the fence rewrites a command, and it rewrites only KGME calls. A Node version switch moves `claude` and `codex` and so triggers it, and the wider the fence reaches, the more it stops.
- Until this lands, KGME work runs in the CLI only (STATUS, "Next", item 0).

## What

### §1 Measure, recorded as an AUDIT before any code
Read the installed Hermes at `~/.hermes/hermes-agent`. Record its version and commit, as AUDIT-0171 did, and cite file and line for every answer. Do not open `.env` or `auth.json`, and mask secret-shaped values in `config.yaml`. Write nothing but the report. Where an answer needs a live run, write the script under `logs/scratch/handoff-0078/`; Michou runs it, as with `install.sh --probes`, and the report quotes his output verbatim.

- **(a) Desktop's path.** Trace a Desktop-sourced call (`mcp__terminal`, `mcp__write_file`, `mcp__execute_code`) from where the Desktop app's request enters Hermes to the tool handler. Answer four questions, each with its evidence:
  1. Does `pre_tool_call` fire on that path at all?
  2. Does the shell hook registered from `hooks:` in `~/.hermes/config.yaml` fire on it?
  3. Does a plugin `pre_tool_call` hook (`ctx.register_hook`) fire on it where the shell hook does not?
  4. Why do the two differ: the profile home, a matcher, consent, a skip flag, or a different dispatcher?

  Record the payload the hook receives on that path: `tool_name` exactly as spelt (with or without `mcp__`), the arguments' key, `cwd`, and whether the session's or the Desktop project's directory reaches the hook anywhere (`cwd`, `extra`, or an argument).
- **(b) The TUI and the gateway.** For each surface (CLI, TUI, the gateway's messaging platforms, cron jobs run under the gateway, Desktop), state whether a call goes through the CLI's hook path: the same dispatcher with the hook not skipped, and shell hooks registered for the same home. Give one table row per surface: shell hook fires, plugin hook fires, the name form the hook sees.
- **(c) Every tool that runs code, per surface.** For each tool record the name the hook sees, the toolset that enables it, whether it is enabled in Michou's configuration today, and how it runs code (shell, Python, Node, a debugger, the GUI). Include the tools that run code indirectly:
  - dispatchers that call other tools by name (`tool_call`, the connectors bridge, `execute_code`'s kernel), with whether each inner call fires its own `pre_tool_call` under its own name;
  - child agents (`delegate_task`);
  - scheduled jobs (`cronjob`);
  - background processes (`process`);
  - the GUI (`computer_use`);
  - browser scripting;
  - every MCP server configured on each surface, Desktop's `node_repl` and `computer-use` among them.

  List the known tools that run no code too, since §2 needs that list.
- **(d) What §2 needs**, as the report's last section: the name forms to normalise, the list of tools that run code, the list of tools that run none, the hook (shell or plugin) that reaches each surface, and whether a base directory reaches the hook on Desktop.

**Leads**, read by the conductor while drafting on 2026-11-27 and not verified; §1 confirms or refutes each:
- `agent/anthropic_adapter.py:548-556` puts every tool name on the Anthropic OAuth wire as `mcp__<name>`. A bare `read_file` becomes `mcp__read_file`, and a native MCP tool `mcp_<server>_<tool>` becomes `mcp__<server>_<tool>`. `normalize_response` reverses the mapping by registry lookup. `:327` also aliases `session_search` to `chat_history_lookup` and `memory` to `context_notes`. In the conductor's own CLI session the model sees `mcp__terminal`, yet the fence judged such a call as `terminal` (it refused one for a `;` on 2026-11-27 at 12:46). So on the CLI the prefix is gone before the hook sees the call, and on Desktop it may not be.
- `tools/mcp_tool_schema.py:157-177`: MCP server tools are registered as `mcp__<server>__<tool>`.
- `agent/tool_executor.py:1761` and `agent/agent_runtime_helpers.py:2116` dispatch with `skip_pre_tool_call_hook=True`. `tests/tools/test_tool_call_bridge_hook_scope.py:7` names a past bug in which the bridge forwarded that flag.
- `agent/shell_hooks.py:51-53` keys a registered shell hook by home, event, matcher and command, "so multiplexed-gateway profiles can register identical triples". The gateway may therefore run Desktop sessions under a home whose configuration has no `hooks:` key.
- `tools/code_kernel.py:301-320`: `execute_code`'s kernel dispatches its tool calls through `handle_function_call`.

**Stop rule.** If §1 finds that no `pre_tool_call` hook, shell or plugin, fires on Desktop's path, §2 is not built. The AUDIT ends with the options (Desktop kept away from KGME projects, a change on Hermes's side, or DEBT's OS-level boundary) and goes to the conductor for a ruling.

### §2 Build from those findings, in `kgme/hermes_fence_policy.py`
The rules live in the policy, which stays pure. The only other code changes are the ones §1 makes necessary, named in Outputs.

1. **Strip an `mcp__` prefix before judging a call.** `judge` first turns `mcp__<name>` into `<name>`, and reverses the OAuth aliases §1 confirms, then judges by the result. An MCP server's tool (`mcp__<server>__<tool>`) still has a `__` in its name after stripping, so it matches no native tool and is judged as unknown (rule 2). Refusal messages give the name as Hermes sent it.
2. **Refuse unknown tools that run code.** `CODE_TOOLS` grows from `("execute_code",)` to §1(c)'s list. A new `PLAIN_TOOLS` holds the known tools that run no code. Any tool on no list (terminal, write, read, code, plain), MCP server tools included, is presumed to run code until it is listed. A tool that runs code, known or presumed, is refused on a KGME call (rule 3).
3. **Calls that name no KGME path still pass,** so non-KGME Desktop work keeps working. One predicate, `kgme_call(call, facts) -> str | None`, returns why a call is a KGME call, and every rule uses it:
   - for the terminal, `why_inside`, as today;
   - for `write_file` and `patch`, a target inside the root, as today;
   - for a tool that runs code: Hermes's process directory is inside; the base directory (if §1 finds one that reaches the hook) is inside or absent; any argument string names the root (`names_root`, after quote removal, in any case), resolves inside, or is a relative path;
   - for a plain tool, `judge_other`, as today.

   A tool that runs code and names no KGME path therefore passes only when the call's base is known to be outside the root. If §1 finds that no base reaches the hook on Desktop, 0073's rule stands: a call with no absolute `workdir` counts as inside. Non-KGME terminal work on Desktop then passes with an absolute `workdir` outside the root, and the report lists that cost.
4. **The paths file (the DEBT item).** A missing paths file refuses only KGME calls. `Facts` gains `unpinned: str | None`, the reason the paths file failed. `judge` checks it after `kgme_call`: on a KGME call it refuses with today's message, and every other call is judged as usual. A file that is unreadable, malformed, or pins a program that is not executable is treated the same as a missing one, so one rule covers every failure. `run_decide` in `kgme/hermes_fence.py` stops returning early and passes the failure into `Facts`, with no programs pinned.
5. **Unchanged:** the inside terminal's allowlist and its rewrite under a clean environment, the write paths, `KGME_REFUSED`, absolute paths for writes, and failing closed on an unreadable payload or any exception.

**Tests.** Write them red first against today's fence and keep the red run under `logs/scratch/`.
- Each native name with the `mcp__` prefix is judged as its bare name: `terminal`, `write_file`, `patch`, `execute_code`, `read_file`.
- AUDIT-0180's Desktop calls, as payloads in the shape §1 records, are refused.
- An `mcp__<server>__<tool>` call that names no path is refused on a KGME call and allowed when its base is known to be outside.
- A terminal call with an absolute `workdir` outside the root that names no KGME path passes under both name forms.
- Every tool on §1(c)'s code list is refused on a KGME call.
- With the paths file missing, malformed, or pinning a non-executable program, a KGME call is refused and names the file, and a non-KGME call is allowed. `test_f10_a_missing_or_unreadable_paths_file_fails_closed` (`tests/test_hermes_fence_pinned.py:125`) and its siblings are rewritten to that rule. This is the one ruled behaviour that changes.
- The other fence tests pass unchanged.

## Outputs
- **§1:** one report under `docs/audit/`, taking the next free AUDIT id in the main checkout (AUDIT-0181 on 2026-11-27), written before any code.
- **§2:** `kgme/hermes_fence_policy.py`; `kgme/hermes_fence.py`, `run_decide` only; `kgme/hermes_fence_parse.py`, only if §1 shows the payload carries a base directory under a key it does not read yet; `tests/test_hermes_fence*.py` and `tests/fencetools.py`; the report under `docs/audit/`.
- **Michou's part,** as files under `logs/scratch/handoff-0078/`:
  - the changes to 0073's `install.sh`;
  - if §1 finds that only a plugin hook reaches Desktop, a thin plugin that runs the same `kgme.hermes_fence` entry point and fails closed, together with its install step;
  - a diff for `docs/DEBT.md` that removes the Desktop line once acceptance passes.

## Acceptance test (under ten minutes)
1. **AUDIT-0180's Desktop test is refused.** In a Desktop chat in a project rooted at brain, after `hermes gateway restart` and the hook's consent, `echo /Users/michaelgrigorian/Projects/KGME/brain/fence-check` is refused with a `kgme-fence:` message. Michou runs it, and the report quotes the transcript.
2. **The four post-landing probes pass** (`install.sh --probes`, (a) to (d)), as in AUDIT-0180's run of 2026-11-24 at 15:15.
3. **`make check` passes.**
4. **Added by the conductor; strike it at adoption if unwanted.** In a Desktop project rooted outside `~/Projects/KGME`, `echo fence-check` runs. If §1 finds that no base reaches the hook, the call carries an absolute `workdir` outside the root.

## Reversibility
Revert the commit, and the fence returns to 0073's rules. If §2 added a plugin, remove it and its configuration entry. The paths file and `install.sh --pin` are untouched.

## Decisions (ADR-023 scores)
| decision | stakes | edge | score | asked |
|---|---|---|---|---|
| An unlisted tool is presumed to run code until §1's list names it | 3 | 0.2 | 0.6 | no; listed |
| With no base visible, a call counts as a KGME call (0073's no-`workdir` rule kept), so non-KGME Desktop terminal work needs an absolute `workdir` unless §1 finds a base | 3 | 0.4 | 1.2 | no; listed |
| The paths-file rule covers a file that is missing, unreadable, malformed, or pins a non-executable program | 2 | 0.2 | 0.4 | no |
| A plugin wrapper, if §1 needs one, ships as Michou's part like `install.sh` | 2 | 0.2 | 0.4 | no |
| Acceptance step 4 added by the conductor | 2 | 0.2 | 0.4 | no; listed |
| `from: claude-code`, because the schema's `from` values have no conductor | 1 | 0.3 | 0.3 | no |

## Needs from Michou
- Adoption: move this file to `docs/handoff/`, set `from: michou` and `status: open`.
- After §1 records the `node_repl` and `computer-use` MCP servers, remove them from Desktop's own configuration yourself (STATUS, "Next", item 0). The builder lists them and never edits them.
- Run the live checks: §1's script if it needs one, the Desktop acceptance steps, and the probes.
