"""`kgme agent run <id> "<task>"`: one run of a role, attributable in the ledger (HANDOFF-0071 §3).

Purpose: start the role's level as `kgme session` builds it (`kgme.session.read_launch`), with
the role's model, and its skill and atlas slice carried in one system-prompt file (after the
committed `CLAUDE.md` a `loose` launch already carries), the task as the prompt. The launch
itself is narrowed to the role's tools (AUDIT-0173 F2): `--tools` names them as the only
built-in tools, `--strict-mcp-config` loads no MCP server, and the run copy of the level's
settings keeps only the allow rules of those tools and denies every other tool the level,
the role's profile or `claude-builder` names. A restriction the launch cannot express (a
scoped rule such as `Bash(make check)`, or a profile's path or network fences other than
`claude-builder`'s at `work`) is refused by name before anything is written. Before the
launch, one `agent:run` intent; after it, one outcome that `ref`s it (F1); both keyed
`agent:<role id>`, naming the role in their summaries, and sharing the run id of the session
note `write_start` records, whose payload carries `role` too. Every intent written gets an
outcome (F4): a preparation or launch failure is a `blocking` error (exit 2), an
interruption a `transient` one (exit 130), anything else is recorded and raised. The child's
environment names the intent in `KGME_LOOP_PARENT`, so the session's first hook event nests
under it and every later one under that (HANDOFF-0063's parent link, unchanged). The session
is a child process, never an `exec`, so the outcome is written. A role that fails lint never
runs, judged by the file it was read from, not a path rebuilt from its `id`
(AUDIT-0174 F8). `headless` (`--print`, `claude -p`) is taken only at `tight`, where the level
writes nothing. `cheap` is not a role level in v1 and is refused (F3, ruled narrower). A slice that
cannot be built is left out and its reason recorded, as a `loose` launch does (HANDOFF-0056 §3).
Inputs: the checkout, the parsed `kgme.toml`, the role id, the task, optionally a handoff.
Outputs: the exit code: the session's, 2 when refused or failed, 130 when interrupted.
Side effects: the run copy, the role prompt and payloads under `logs/scratch/`, the intent,
the session note and the outcome in the ledger, and one `claude` child process.
"""

import dataclasses
import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from kgme import clean_fs, events, ledger, paths, roles, roles_io, session

JOB = "agent:run"
PARENT_ENV = "KGME_LOOP_PARENT"
PROMPT_FLAG = "--append-system-prompt-file"


def role_prompt(data: dict, chain: list[str], skill: str, slice_text: str) -> str:
    """Pure: what the role carries into its session: who it is, its chain, its skill, its
    slice."""
    head = (
        f"# Role: {data['id']} ({data['kind']}, department {data['department']})\n\n"
        f"{data['purpose']}\n\nLevel `{data['level']}`, tier ceiling {data['tier_max']}, "
        f"tools {', '.join(data['tools'])}. Escalate: {' -> '.join(chain)}.\n"
    )
    return "\n".join(part for part in (head, skill, slice_text) if part)


def with_role(
    argv: list[str], model: str, prompt_file: Path, task: str, headless: bool
) -> list[str]:
    """Pure: the level's argv with the role's model, its prompt file in place of any carried
    one, `-p` when headless, and the task last."""
    out = list(argv)
    out[out.index("--model") + 1] = model
    if PROMPT_FLAG in out:
        out[out.index(PROMPT_FLAG) + 1] = str(prompt_file)
    else:
        out += [PROMPT_FLAG, str(prompt_file)]
    if headless and "-p" not in out:
        out.append("-p")
    return out + [task]


def narrow(rendered: dict, tools: list[str], universe: frozenset[str]) -> dict:
    """Pure: a level's rendered settings narrowed to the role's `tools` (bare names): an allow
    rule for any other tool dropped, and a deny rule for every tool of `universe` the role does
    not list, merged with the level's own denies (AUDIT-0173 F2)."""
    keep = set(tools)
    permissions = dict(rendered.get("permissions") or {})
    if "allow" in permissions:
        permissions["allow"] = [r for r in permissions["allow"] if roles.tool_name(r) in keep]
    deny = list(permissions.get("deny") or [])
    deny += [name for name in sorted(universe - keep) if name not in deny]
    permissions["deny"] = deny
    return {**rendered, "permissions": permissions}


def launch_refusal(
    data: dict,
    profile: roles.Profile | None,
    level_name: str,
    own_profile: str,
    grant: frozenset[str],
) -> str | None:
    """Pure: why the launch cannot express this role's restriction, or None. `--tools` takes
    bare names, so every tool must pass `roles.tool_problem` against `grant`, the validator
    lint uses (AUDIT-0174 F2); a profile's path or network fences have no rendering at a
    level, unless the profile is the level's own (`claude-builder` at `work`, which the
    project settings the level loads already enforce)."""
    for tool in data.get("tools") or []:
        problem = roles.tool_problem(tool, grant, level_name)
        if problem:
            return problem
    name = data.get("profile")
    own = level_name == "work" and name == own_profile
    if profile is not None and profile.fences and not own:
        return (f"profile `{name}` fences {', '.join(profile.fences)}, which the launch cannot "
                f"render at {level_name}")  # fmt: skip
    return None


def read_slice(base: Path, settings: dict, around: list[str]) -> tuple[str, str | None]:
    """Effect: the role's atlas slice and the reason it is missing, if it is."""
    if not around:
        return "", None
    from kgme import atlas_read

    try:
        return atlas_read.read_slice(base, settings, None, list(around), None).text, None
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        return "", f"{type(error).__name__}: {error}"[:200]


def read_runnable(base: Path, settings: dict, role_id: str) -> tuple[dict | None, str]:
    """Effect: the role if it exists and passes lint, or None and why not."""
    every = roles_io.read_role_files(base)
    if role_id not in every:
        return None, f"no role `{role_id}`"
    rel, data = every[role_id]  # the file it came from selects its findings (AUDIT-0174 F8)
    if data.get("level") in roles.NOT_ROLE_LEVELS:
        return None, roles.NOT_ROLE_LEVELS[str(data.get("level"))]
    broken = [f.line() for f in roles_io.read_findings(base, settings)
              if f.path == rel and f.cls == "blocking"]  # fmt: skip
    if broken:
        return None, "the role fails lint:\n" + "\n".join(broken)
    return data, ""


def write_event(
    dirs: ledger.Dirs, run: str, role_id: str, kind: str, summary: str, **more: object
) -> str:
    """Effect: one `agent:run` event of the role's run; its id."""
    event = events.make_event(
        source="kgme", actor="kgme.agent", kind=kind, job=JOB, key=f"agent:{role_id}",
        run_id=run, summary=events.clip(summary), **more,
    )  # fmt: skip
    return ledger.append(event, dirs)


def read_narrowing(base: Path, settings: dict, data: dict) -> tuple[frozenset[str], str]:
    """Effect: the tool universe the launch denies outside the role's tools, and why the
    launch cannot express the role's restriction ("" when it can) (AUDIT-0173 F2)."""
    profiles = roles_io.read_profiles(base)
    levels = roles_io.read_levels(base, settings, profiles)
    profile = profiles.get(str(data["profile"])) if "profile" in data else None
    level = levels[str(data["level"])]
    grant = roles.allowed(level, profile, str(data["level"]))
    why = launch_refusal(data, profile, str(data["level"]), roles_io.WORK_PROFILE, grant)
    universe = set(level.tools)
    for known in (profile, profiles.get(roles_io.WORK_PROFILE)):
        universe |= set(known.tools or ()) if known else set()
    return frozenset(universe), why or ""


def run_agent(
    base: Path,
    settings: dict,
    role_id: str,
    task: str,
    dirs: ledger.Dirs | None = None,
    run_child: Callable[[list[str], dict], int] | None = None,
    headless: bool = False,
    handoff: str | None = None,
    dry_run: bool = False,
) -> int:
    """The command: check, record the intent, start the session as a child, record the
    outcome. A dry run prints the argv and the role prompt and writes nothing."""
    data, why = read_runnable(base, settings, role_id)
    level = str(data.get("level")) if data else ""
    if data and headless and level != "tight":
        why = f"--print is tight's only; {role_id} runs at {level}"
    if data and task.startswith("-"):
        why = "the task may not start with `-`; it would read as a flag"
    if data and not why:
        universe, why = read_narrowing(base, settings, data)
    if data is None or why:
        print(f"kgme agent: {why}", file=sys.stderr)
        return 2
    dirs = dirs or ledger.read_default_dirs(settings, base)
    model = settings.get("models", {}).get(roles_io.MODEL_KEYS[str(data["model"])])
    run = events.new_ulid()
    try:
        launch, record = session.read_launch(level, handoff, [], base, settings, run)
    except (ValueError, OSError, RuntimeError) as error:
        print(f"kgme agent: {error}", file=sys.stderr)
        return 2
    tools = [str(t) for t in data["tools"]]
    narrowed = narrow(json.loads(launch.settings), tools, universe)
    body = json.dumps(narrowed, indent=2, sort_keys=True) + "\n"
    launch = dataclasses.replace(launch, settings=body)
    main = ledger.read_main_checkout(base)
    skill = (base / "skills" / str(data["skill"]) / "SKILL.md").read_text(encoding="utf-8")
    slice_text, slice_error = read_slice(base, settings, list(data["slice"]))
    chain = roles.chain(role_id, roles_io.read_roles(base))[0]
    prompt = role_prompt(data, chain, skill, slice_text)
    if launch.claude_md:
        prompt = launch.claude_md + "\n" + prompt
    prompt_file = paths.scratch_dir(settings, main) / "sessions" / run / "role.md"
    argv = with_tools(with_role(launch.argv, str(model), prompt_file, task, headless), tools)
    if dry_run:
        print(" ".join(argv))
        print(prompt, end="")
        return 0
    clean_fs.write_payload(main, prompt_file, prompt)
    record |= {
        "argv": argv, "model": model, "role": role_id, "task": task, "headless": headless,
        "tools": tools, "settings_sha256": session.sha256_text(body),
        "role_prompt": prompt_file.relative_to(main).as_posix(),
        "role_prompt_sha256": session.sha256_text(prompt), "slice_error": slice_error,
    }  # fmt: skip
    intent = write_intent(main, settings, dirs, run, role_id, record)
    stage = "preparation"
    try:
        env = session.write_start(record, launch, base, settings, run, dirs)
        inherited = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        child = run_child or (lambda a, e: subprocess.run(a, env=e, check=False).returncode)
        stage = "launch"
        code = child(argv, {**inherited, **env, PARENT_ENV: intent})
    except KeyboardInterrupt:
        write_outcome(dirs, run, role_id, intent, 130, f"interrupted during {stage}", "transient")
        return 130
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        write_outcome(dirs, run, role_id, intent, 2, f"{stage} failed: {describe(error)}")
        return 2
    except BaseException as error:
        write_outcome(dirs, run, role_id, intent, 1, f"{stage} failed: {describe(error)}")
        raise
    write_outcome(dirs, run, role_id, intent, code)
    return code


def with_tools(argv: list[str], tools: list[str]) -> list[str]:
    """Pure: the argv with the role's tools as the only built-in tools and no MCP server but
    those it names (none), right after the executable, where the variadic `--tools` cannot
    swallow the task (AUDIT-0173 F2)."""
    return [argv[0], "--tools", ",".join(tools), "--strict-mcp-config", *argv[1:]]


def describe(error: BaseException) -> str:
    """Pure: an error as `Type: message`, short."""
    return f"{type(error).__name__}: {error}"[:200]


def write_intent(
    main: Path, settings: dict, dirs: ledger.Dirs, run: str, role_id: str, record: dict
) -> str:
    """Effect: the run's payload and its `agent:run` intent; the intent's id."""
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    payload = paths.payloads_dir(settings, main) / f"agent-{run}.json"
    clean_fs.write_payload(main, payload, text)
    summary = f"agent {role_id} at {record['level']}, model {record['model']}: {record['task']}"
    return write_event(
        dirs, run, role_id, "intent", summary,
        payload_ref=payload.relative_to(main).as_posix(), payload_sha256=session.sha256_text(text),
    )  # fmt: skip


def write_outcome(
    dirs: ledger.Dirs,
    run: str,
    role_id: str,
    intent: str,
    code: int,
    failure: str | None = None,
    class_: str = "blocking",
) -> str:
    """Effect: the run's outcome, `ref`ing and nesting under its intent so the intent closes
    (AUDIT-0173 F1): `ok` on exit 0, else an error of `class_`, its summary the exit code or
    the classified `failure` (AUDIT-0173 F4)."""
    failed = {"status": "error", "class_": class_} if code or failure else {"status": "ok"}
    summary = f"agent {role_id}: {failure}" if failure else f"agent {role_id}: exit {code}"
    return write_event(dirs, run, role_id, "outcome", summary,
                       ref=intent, parent=intent, **failed)  # fmt: skip
