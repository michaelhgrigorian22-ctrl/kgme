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
Plain `claude` is unchanged and is not a level.
Inputs: the level, the handoff id, extra `claude` arguments, the parsed `kgme.toml`, the
checkout, the working directory, whether this is a dry run.
Outputs: the argv and environment; an exit code (a launch replaces this process).
Side effects: the run copy, the Outputs list, a payload, one ledger note; `exec` of `claude`.
"""

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from kgme import clean_fs, events, ledger, loop_outputs, paths, review_io
from kgme.frontmatter import parse_frontmatter
from kgme.session_logic import (  # noqa: F401 - the launcher's pure half, re-exported
    AUTHORS,
    EDIT_OUTPUTS,
    EXTRA_FLAGS,
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


@dataclass(frozen=True)
class Launch:
    """What a level starts: the argv, the extra environment, the rendered settings."""

    argv: list[str]
    env: dict[str, str]
    settings: str


def read_claude_version() -> str:
    """Effect: `claude --version`, or `unknown` when it does not answer."""
    try:
        done = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return done.stdout.strip() or "unknown"


def read_handoff(base: Path, settings: dict, handoff: str) -> str:
    """Effect: the text of `handoff` when it is executable: at the top of `docs/handoff/`,
    `status: open`, `from` cowork or michou; `ValueError` naming why it is not (F5)."""
    folder = paths.handoff_dir(settings, base)
    source = review_io.read_handoff_path(folder, handoff)
    if source is None:
        raise ValueError(
            f"{handoff} is not executable: not under docs/handoff/ (a proposal is not a handoff)"
        )
    text = source.read_text(encoding="utf-8")
    try:
        data, _ = parse_frontmatter(text)
    except ValueError as error:
        raise ValueError(f"{handoff} is not executable: {error}") from error
    if source.parent != folder or data.get("status") != "open" or data.get("from") not in AUTHORS:
        where = source.relative_to(base).as_posix()
        raise ValueError(
            f"{handoff} is not executable: {where}, status {data.get('status')}, "
            f"from {data.get('from')} (CLAUDE.md: open, at the top, from cowork or michou)"
        )
    return text


def read_main_policy(main: Path) -> dict:
    """Effect: the main checkout's project settings, the policy every level carries."""
    return json.loads((main / ".claude" / "settings.json").read_text(encoding="utf-8"))


def read_workspace(base: Path) -> Path:
    """Effect: the working directory a `loose` run may start from, or `ValueError`: a worktree
    of this repository, outside the main checkout, that does not disable hooks (F1)."""
    main = ledger.read_main_checkout(base)
    here = Path.cwd().resolve()
    if here.is_relative_to(main):
        raise ValueError(
            "loose runs only from a workspace outside the main checkout (HANDOFF-0048); "
            "the sandbox always lets Bash write to the working directory"
        )
    try:
        theirs = ledger.read_main_checkout(here)
    except RuntimeError:
        theirs = None
    if theirs != main:
        raise ValueError(f"loose runs only from a worktree of {main}; {here} is not one")
    for name in ("settings.json", "settings.local.json"):
        project = here / ".claude" / name
        if project.is_file():
            try:
                data = json.loads(project.read_text(encoding="utf-8"))
            except ValueError as error:
                raise ValueError(f"{project} does not parse: {error}") from error
            if isinstance(data, dict) and data.get("disableAllHooks"):
                raise ValueError(f"{project} sets disableAllHooks; loose will not start there")
    return here


def read_launch(
    level: str, handoff: str | None, extra: list[str], base: Path, settings: dict, run: str
) -> tuple[Launch, dict]:
    """Effect: check the level can start as configured and build what it starts; the launch
    and the record its note carries, or `ValueError` naming what is missing."""
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
    template_path = base / TEMPLATES / f"{level}.json"
    if not template_path.is_file() or template_path.is_symlink():
        raise ValueError(f"{template_path.relative_to(base)} is missing; Michou applies it")
    template_text = template_path.read_text(encoding="utf-8")
    workspace = read_workspace(base) if level == "loose" else base.resolve()
    entries: tuple[str, ...] = ()
    env: dict[str, str] = {}
    if handoff:
        text = read_handoff(base, settings, handoff)
        entries = tuple(loop_outputs.parse_outputs(text)) + loop_outputs.ALWAYS
        env = {loop_outputs.ENV_HANDOFF: handoff, loop_outputs.ENV_RUN: run}
    tmp = Path(tempfile.gettempdir()).resolve()
    rendered = render(json.loads(template_text), workspace, tmp, entries)
    main = ledger.read_main_checkout(base)
    policy_sha = None
    if level == "loose":
        rendered, policy_sha = carry_policy(rendered, read_main_policy(main), main)
    body = json.dumps(rendered, indent=2, sort_keys=True) + "\n"
    copy = paths.scratch_dir(settings, main) / "sessions" / run / f"{level}.json"
    argv = build_argv(level, copy, model, caps, extra)
    record = {
        "level": level,
        "handoff": handoff,
        "workspace": str(workspace),
        "template": template_path.relative_to(base).as_posix(),
        "template_sha256": sha256_text(template_text),
        "settings": copy.relative_to(main).as_posix(),
        "settings_sha256": sha256_text(body),
        "policy_sha256": policy_sha,
        "argv": argv,
        "model": model,
        "claude_version": read_claude_version(),
    }
    return Launch(argv, env, body), record


def write_start(
    record: dict, launch: Launch, base: Path, settings: dict, run: str, dirs: ledger.Dirs
) -> dict[str, str]:
    """Effect: the run copy, the Outputs list for a handoff, the payload, and the start note,
    all in the main checkout; returns the environment the launch adds. Shared with the canary
    cells, so they launch what the launcher launches (review cycle 1 F6)."""
    main = ledger.read_main_checkout(base)
    clean_fs.write_payload(main, main / record["settings"], launch.settings)
    env = dict(launch.env)
    if record["handoff"]:
        text = read_handoff(base, settings, record["handoff"])
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
) -> int:
    """The command: build, record, then replace this process with `claude`. A dry run prints
    the argv and the settings and records one note; nothing else is written."""
    run = events.new_ulid()
    try:
        launch, record = read_launch(level, handoff, extra, base, settings, run)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"kgme session: {error}", file=sys.stderr)
        return 2
    dirs = ledger.read_default_dirs(settings, base)
    if dry_run:
        print(" ".join(launch.argv))
        print(launch.settings, end="")
        digest = record["settings_sha256"][:16]
        summary = f"session {level} dry run: settings sha256={digest} model={record['model']}"
        event = events.make_event(
            source="kgme", actor="kgme.session", kind="note", job="session",
            key=f"session:{level}:dry-run", summary=summary,
        )  # fmt: skip
        ledger.append(event, dirs)
        return 0
    env = write_start(record, launch, base, settings, run, dirs)
    execute(launch.argv[0], launch.argv, {**os.environ, **env})
    return 0
