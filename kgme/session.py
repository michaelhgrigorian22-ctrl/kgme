"""`kgme session <level>`: a session's allowance as a named level, one launcher line (ADR-022).

Purpose: build the `claude` command line of a level, record it, and hand the terminal to it
(HANDOFF-0047). Each level is a settings template under `control/policy/sessions/`, a human
path Michou applies, rendered at launch into a per-run copy under the main checkout's
`logs/scratch/sessions/<run>/` with absolute paths: `{repo}` the folder the session works in,
`{tmp}` the per-user temp directory, an element `{outputs}` the handoff's `Outputs` plus
`tests/` and `logs/scratch/` in that folder (the list `kgme.loop_outputs` parses, the one guard
rule 5 also reads), and an element `Edit({outputs})` one `Edit(//<path>)` rule per entry. The
command is `claude --setting-sources project,local --settings <copy> --permission-mode
<mode> --model <kgme.toml [models] builder>`, plus for `loose` `-p --permission-prompts none
--max-turns N --max-budget-usd B` from `[sessions]`, plus extra arguments only from a short
list that cannot widen a level (review cycle 1 F2). Before it starts, one ledger `note`
(`job: session`), in the main checkout's ledger, records the level and the copy's sha256 in its
summary, and in its payload, in the main checkout too (F3), the template and its sha256, the
full argv, `claude --version`, the model, the handoff, and the workspace.
`loose` runs one executable handoff: at the top of `docs/handoff/`, `status: open`, from
`cowork` or `michou` (F5, CLAUDE.md). It starts only from a worktree of this repository outside
the main checkout: the live cell of 2026-10-21 showed the sandbox letting a Bash line write to
the working directory outside `allowWrite`, a recorded residual, so a `loose` builder runs only
from a workspace (HANDOFF-0048; Michou, 2026-10-21). Claude Code reads project settings from
its working directory, which a builder may have touched, so the run copy carries the main
checkout's policy itself: its hooks, the commands naming the main checkout's scripts by
absolute path, and its deny list, merged with the level's; deny rules merge across scopes and
cannot be overridden, so the workspace's settings can add rules but never remove the guard or a
deny. A workspace that sets `disableAllHooks` is refused, and the note records the carried
policy's sha256 (review cycle 2 F1, two arbiters, option C). Residual: the guard script runs
the workspace's own `kgme/hooks/` code, through `uv run --project "$CLAUDE_PROJECT_DIR"`.
`loose` sets the loop-mode variables, so the guard fences the same Outputs the sandbox does.
The cheap route (HANDOFF-0053): `work --model <key> --red <command>`, with a model whose
provider has the data class `code`, runs only through `kgme.cheap` (a code-only export,
`run_cheap`), never as a level; `read_route` decides it from the configuration alone. A level
that loads mods (HANDOFF-0059, ADR-024) passes `--plugin-dir` for each mod `kgme.toml [mods]`
names for it and names the checkout as `UV_PROJECT`. The reads the launch makes are in
`kgme.session_read` (HANDOFF-0060 §3, moved unchanged).
Plain `claude` is unchanged and is not a level.
Inputs: the level, the handoff id, extra `claude` arguments, the parsed `kgme.toml`, the
checkout, the working directory, whether this is a dry run.
Outputs: the argv and environment; an exit code (a launch replaces this process).
Side effects: the run copy, the Outputs list, a payload, one ledger note; `exec` of `claude`.
"""

import json
import os
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from kgme import clean_fs, events, ledger, loop_outputs, paths
from kgme.session_logic import (  # noqa: F401 - the launcher's pure half, re-exported
    AUTHORS,
    EDIT_OUTPUTS,
    EXTRA_FLAGS,
    GIT_ADD_OUTPUTS,
    GIT_COMMIT_OUTPUTS,
    LEVELS,
    OUTPUTS,
    PROJECT_DIR,
    TEMPLATES,
    build_argv,
    carry_policy,
    check_extra,
    render,
    sha256_text,
)
from kgme.session_read import (  # noqa: F401 - the launch's reads, re-exported (HANDOFF-0060 §3)
    SKILL,
    read_carried_prompt,
    read_claude_version,
    read_committed_claude_md,
    read_handoff,
    read_main_policy,
    read_mod_dirs,
    read_workspace,
    uv_env,
)

BASH_TIMEOUTS = {"BASH_DEFAULT_TIMEOUT_MS": "1500000", "BASH_MAX_TIMEOUT_MS": "1800000"}


@dataclass(frozen=True)
class Launch:
    """What a level starts: the argv, the extra environment, the rendered settings."""

    argv: list[str]
    env: dict[str, str]
    settings: str
    claude_md: str = ""  # the committed CLAUDE.md a `loose` run carries (F18)


def read_route(
    level: str,
    handoff: str | None,
    extra: list[str],
    settings: dict,
    model_key: str | None,
    red: str | None,
) -> str:
    """Pure over the config: "cheap" for `work --model <key> --red <command>` where the key's
    provider has the data class `code`, else the level's own route; `ValueError` for any
    other use of a `code` model, or of `--model` and `--red` (HANDOFF-0053 §1: a `code`
    model is launched only through the cheap lane)."""
    from kgme import cheap

    provider = settings.get("models", {}).get("builder_provider", cheap.PROVIDER_DEFAULT)
    builder_class = settings.get("providers", {}).get(provider)  # None before [providers]
    if builder_class == cheap.CODE:
        raise ValueError("[models] builder is a code-class model; it runs only through --red")
    if model_key is None:
        if red is not None:
            raise ValueError("--red is the cheap lane's: it needs --model <key>")
        return level
    data_class = cheap.read_model(settings, model_key)[2]
    if data_class != cheap.CODE:
        raise ValueError(
            f"--model {model_key} is not a code-class model; --model is the cheap lane's"
        )
    if level != "work" or handoff or extra:
        raise ValueError(
            f"--model {model_key} runs only as `kgme session work --model {model_key} --red ...`"
        )
    if not red:
        raise ValueError(f'--model {model_key} needs --red "<command>": the command it makes green')
    return "cheap"


def read_launch(
    level: str,
    handoff: str | None,
    extra: list[str],
    base: Path,
    settings: dict,
    run: str,
    task: str | None = None,
) -> tuple[Launch, dict]:
    """Effect: check the level can start as configured and build what it starts; the launch
    and the record its note carries, or `ValueError` naming what is missing. With `task`
    (HANDOFF-0048), a `loose` run builds one task of the handoff from the task's own
    workspace: its fence is the task's `Outputs` from the record `kgme workspace create`
    wrote in the main checkout, and the handoff is still read for its adoption."""
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}; levels: {', '.join(LEVELS)}")
    check_extra(extra)
    model = settings.get("models", {}).get("builder")
    if not model:
        raise ValueError("kgme.toml [models] builder is not set")
    caps = settings.get("sessions", {})
    if level == "loose" and not {"max_turns", "max_budget_usd"} <= set(caps):
        raise ValueError("kgme.toml [sessions] max_turns and max_budget_usd are not set")
    if level == "loose" and not handoff:
        raise ValueError("loose runs one handoff: --handoff HANDOFF-NNNN")
    if task and (level != "loose" or not handoff):
        raise ValueError("--task is loose's, with --handoff: one task of a crew handoff")
    template_path = base / TEMPLATES / f"{level}.json"
    if not template_path.is_file() or template_path.is_symlink():
        raise ValueError(f"{template_path.relative_to(base)} is missing; Michou applies it")
    template_text = template_path.read_text(encoding="utf-8")
    workspace = read_workspace(base) if level == "loose" else base.resolve()
    main = ledger.read_main_checkout(base)
    entries: tuple[str, ...] = ()
    env: dict[str, str] = {}
    task_record: dict | None = None
    if handoff:
        text = read_handoff(base, settings, handoff)
        entries = tuple(loop_outputs.parse_outputs(text)) + loop_outputs.ALWAYS
        env = {loop_outputs.ENV_HANDOFF: handoff, loop_outputs.ENV_RUN: run}
    if task:
        task_record = read_task_record(main, settings, handoff, task, workspace)
        entries = tuple(task_record["outputs"]) + loop_outputs.ALWAYS
    if level == "loose":
        # measured live (2026-10-21): uv opens its cache at start, and ~/.cache/uv is outside the
        # sandbox's writes, so the pinned `uv run --frozen pytest` failed; the cache goes inside
        # the fence and uv uses the workspace's synced environment as it is
        env |= uv_env(workspace)
        # `make check` and a review cycle run as one Bash call and take minutes; Claude Code's
        # default Bash timeout is two, so an unattended builder would lose its gate (HANDOFF-0048)
        env |= BASH_TIMEOUTS
    tmp = Path(tempfile.gettempdir()).resolve()
    rendered = render(json.loads(template_text), workspace, tmp, entries, main)
    policy_sha = None
    if level == "loose":
        rendered, policy_sha = carry_policy(rendered, read_main_policy(main), main)
    body = json.dumps(rendered, indent=2, sort_keys=True) + "\n"
    copy = paths.scratch_dir(settings, main) / "sessions" / run / f"{level}.json"
    claude_md, claude_path, carried = "", None, {}
    if level == "loose":
        claude_md, carried = read_carried_prompt(main, workspace, settings, handoff)
        claude_path = copy.with_name("CLAUDE.md")
    if task_record and task_record.get("model"):  # the task's model, resolved at create (F9)
        model = str(task_record["model"])
    plugin_dirs = read_mod_dirs(base, level, settings)
    if plugin_dirs:
        # the project `/capture`'s `uv run --frozen kgme capture` runs in: the checkout this
        # level launched from, wherever the terminal stands (review cycle 1 F2)
        env |= {"UV_PROJECT": str(base.resolve())}
    argv = build_argv(level, copy, model, caps, extra, claude_path, plugin_dirs)
    record = {
        "level": level,
        "mods": [folder.name for folder in plugin_dirs],
        "handoff": handoff,
        "task": task,
        "task_outputs": list(task_record["outputs"]) if task_record else None,
        "workspace": str(workspace),
        "template": template_path.relative_to(base).as_posix(),
        "template_sha256": sha256_text(template_text),
        "settings": copy.relative_to(main).as_posix(),
        "settings_sha256": sha256_text(body),
        "policy_sha256": policy_sha,
        "claude_md": claude_path.relative_to(main).as_posix() if claude_path else None,
        "claude_md_sha256": sha256_text(claude_md) if claude_path else None,
        **carried,
        "env": dict(sorted(env.items())),
        "argv": argv,
        "model": model,
        "claude_version": read_claude_version(),
    }
    return Launch(argv, env, body, claude_md), record


def read_task_record(main: Path, settings: dict, handoff: str, task: str, workspace: Path) -> dict:
    """Effect: the record of `task` of `handoff` (`kgme workspace create` wrote it in the
    main checkout's scratch), checked to name this workspace; `ValueError` otherwise."""
    from kgme import workspace as ws

    name = ws.workspace_name(handoff, task)
    record = ws.read_record(settings, main, name)
    if record is None:
        raise ValueError(f"no record for task {task} of {handoff}: `kgme workspace create` first")
    if Path(str(record.get("workspace", ""))).resolve() != workspace.resolve():
        raise ValueError(f"task {task}'s workspace is {record.get('workspace')}, not {workspace}")
    if record.get("state") != "open" or not record.get("outputs"):
        raise ValueError(f"task {task} is {record.get('state')} or names no Outputs")
    from kgme.sync_git import run_git

    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], workspace, check=False).stdout.strip()
    if branch != record.get("branch"):
        raise ValueError(f"the workspace is on {branch!r}, not the task's {record.get('branch')!r}")
    return record


def write_start(
    record: dict, launch: Launch, base: Path, settings: dict, run: str, dirs: ledger.Dirs
) -> dict[str, str]:
    """Effect: the run copy, the Outputs list for a handoff, the payload, and the start note,
    all in the main checkout; returns the environment the launch adds. Shared with the canary
    cells, so they launch what the launcher launches (review cycle 1 F6)."""
    main = ledger.read_main_checkout(base)
    clean_fs.write_payload(main, main / record["settings"], launch.settings)
    if record.get("claude_md"):
        clean_fs.write_payload(main, main / record["claude_md"], launch.claude_md)
    env = dict(launch.env)
    if record["handoff"]:
        text = read_handoff(base, settings, record["handoff"])
        if record.get("task_outputs"):  # the task's fence, not the handoff's (HANDOFF-0048)
            text = "## Outputs\n" + ", ".join(f"`{p}`" for p in record["task_outputs"]) + "\n"
        scratch = paths.scratch_dir(settings, main)
        _, digest = loop_outputs.write_outputs(main, scratch, record["handoff"], run, text)
        env[loop_outputs.ENV_SHA] = digest
    write_note(record, main, settings, run, dirs)
    return env


def write_note(record: dict, main: Path, settings: dict, run: str, dirs: ledger.Dirs) -> str:
    """Effect: the start note, its payload the record, both in the main checkout; the note's
    id. The canary cells write the same note for the run copy they launch (F6)."""
    payload_text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    payload = paths.payloads_dir(settings, main) / f"session-{run}.json"
    clean_fs.write_payload(main, payload, payload_text)
    summary = (
        f"session {record['level']}: settings sha256={record['settings_sha256'][:16]} "
        f"model={record['model']}"
    )
    event = events.make_event(
        source="kgme", actor="kgme.session", kind="note", job="session",
        key=f"session:{record['level']}", run_id=run, summary=summary,
        payload_ref=payload.relative_to(main).as_posix(), payload_sha256=sha256_text(payload_text),
    )  # fmt: skip
    return ledger.append(event, dirs)


def run_session(
    level: str,
    handoff: str | None,
    extra: list[str],
    base: Path,
    settings: dict,
    dry_run: bool = False,
    execute: Callable[[str, list[str], dict], None] = os.execvpe,
    model_key: str | None = None,
    red: str | None = None,
    run_claude: Callable | None = None,
    task: str | None = None,
) -> int:
    """The command: build, record, then replace this process with `claude`. A dry run prints
    the argv, the settings, and any carried file, and records one note; nothing else is
    written."""
    try:
        route = read_route(level, handoff, extra, settings, model_key, red)
    except ValueError as error:
        print(f"kgme session: {error}", file=sys.stderr)
        return 2
    if route == "cheap":  # the one route a `code` provider's model runs by (HANDOFF-0053)
        from kgme import cheap

        more = {"run_claude": run_claude} if run_claude else {}
        return cheap.run_cheap(model_key, red, base, settings, dry_run, **more)
    run = events.new_ulid()
    try:
        launch, record = read_launch(level, handoff, extra, base, settings, run, task)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"kgme session: {error}", file=sys.stderr)
        return 2
    dirs = ledger.read_default_dirs(settings, base)
    if dry_run:
        print(" ".join(launch.argv))
        print(launch.settings, end="")
        if launch.claude_md:  # the carried file, in order (HANDOFF-0056 §3)
            print(f"--- carried: {', '.join(record['carried'])} ---")
            print(launch.claude_md, end="")
        digest = record["settings_sha256"][:16]
        summary = f"session {level} dry run: settings sha256={digest} model={record['model']}"
        if record.get("slice_sha256"):
            summary += f" slice sha256={record['slice_sha256'][:16]}"
        event = events.make_event(
            source="kgme", actor="kgme.session", kind="note", job="session",
            key=f"session:{level}:dry-run", summary=summary,
        )  # fmt: skip
        ledger.append(event, dirs)
        return 0
    env = write_start(record, launch, base, settings, run, dirs)
    # another checkout's active environment would be ignored with a warning on every uv call
    # in the session (seen on the live route of 2026-10-27, HANDOFF-0048)
    inherited = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    execute(launch.argv[0], launch.argv, {**inherited, **env})
    return 0
