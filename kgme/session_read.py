"""`kgme session`, the reads a launch makes (moved out of `kgme/session.py` by HANDOFF-0060 §3,
unchanged).

Purpose: what `kgme.session.read_launch` reads before it builds a level's command line: the
installed `claude --version`, the handoff a run names, the uv environment of a workspace, the
committed `CLAUDE.md` and the prompt a `loose` run carries (the skill, the slice), a committed
file, the main checkout's policy, the workspace a `loose` run starts from, and the mod folders a
level loads.
Inputs: the checkout, the main checkout, the parsed `kgme.toml`, a level, a handoff id.
Outputs: strings, paths, dicts, mod folders; `ValueError` naming what is missing.
Side effects: reads files and git, runs `claude --version`.
"""

import json
import subprocess
from pathlib import Path

from kgme import ledger, mods, paths, review_io
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


def uv_env(workspace: Path) -> dict[str, str]:
    """Pure: the environment a `loose` run's uv needs inside its sandbox: no sync (the
    workspace is synced when it is made) and a cache under its `logs/scratch/`."""
    return {"UV_NO_SYNC": "1", "UV_CACHE_DIR": str(workspace / "logs" / "scratch" / "uv-cache")}


def read_committed_claude_md(main: Path) -> str:
    """Effect: the main checkout's committed `CLAUDE.md` (`git show HEAD:CLAUDE.md`), which a
    `loose` run carries because it loads no project settings and so no project rules (Cowork's
    ruling on F18); `ValueError` when there is none."""
    return read_committed(main, "CLAUDE.md")


SKILL = "skills/kgme-atlas/SKILL.md"


def read_carried_prompt(
    main: Path, workspace: Path, settings: dict, handoff: str | None, around: tuple = ()
) -> tuple[str, dict]:
    """Effect: the one file a `loose` run passes with `--append-system-prompt-file`, in
    order: the main checkout's committed `CLAUDE.md`, the committed `kgme-atlas` skill when
    Michou has applied it, and the handoff's atlas slice built from the workspace
    (HANDOFF-0056 §3); and what the start note records of the last two. A slice that cannot
    be built is left out and its reason recorded: it is an aid, never a reason to refuse."""
    from kgme import atlas_read

    parts = [read_committed_claude_md(main)]
    record: dict = {"carried": ["CLAUDE.md"]}
    try:
        skill = read_committed(main, SKILL)
    except ValueError:
        skill = ""
    if skill:
        parts.append(skill)
        record["carried"].append(SKILL)
        record["skill_sha256"] = sha256_text(skill)
    try:
        built = atlas_read.read_slice(workspace, settings, handoff, list(around), None)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        record["slice_error"] = f"{type(error).__name__}: {error}"[:200]
    else:
        parts.append(built.text)
        record["carried"].append("slice")
        record |= {
            "slice_sha256": sha256_text(built.text),
            "slice_tokens": built.tokens,
            "slice_cut": built.cut,
        }
    return "\n\n".join(p.rstrip("\n") for p in parts) + "\n", record


def read_committed(main: Path, name: str) -> str:
    """Effect: `name` as the main checkout's `HEAD` holds it, or `ValueError` when it has none."""
    done = subprocess.run(
        ["git", "show", f"HEAD:{name}"], cwd=main, capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        raise ValueError(f"{main} has no committed {name} for a level to carry")
    return done.stdout


def read_main_policy(main: Path) -> dict:
    """Effect: the main checkout's committed project settings (`git show
    HEAD:.claude/settings.json`), the policy every level carries: an uncommitted edit in the
    main checkout cannot weaken a launch (review cycle 6 F19, the ADR-022 addendum)."""
    return json.loads(read_committed(main, ".claude/settings.json"))


def read_workspace(base: Path) -> Path:
    """Effect: the working directory a `loose` run may start from, or `ValueError`: a worktree
    of this repository, outside the main checkout, whose `.claude/settings.json` is byte-identical
    to the main checkout's committed one, with no `.claude/settings.local.json` holding allow
    rules or disabling hooks at its root or the main checkout's (Cowork's ruling on F1,
    2026-10-21, on top of the policy the run copy carries)."""
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
    committed = subprocess.run(
        ["git", "show", "HEAD:.claude/settings.json"], cwd=main, capture_output=True, check=False
    )
    project = here / ".claude" / "settings.json"
    held = project.read_bytes() if project.is_file() and not project.is_symlink() else None
    if committed.returncode != 0 or held != committed.stdout:
        raise ValueError(
            f"{project} is not byte-identical to {main}'s committed .claude/settings.json; "
            "loose will not start (Cowork's ruling on F1)"
        )
    for root in (here, main):  # a worktree session reads the main root's local file too
        local = root / ".claude" / "settings.local.json"
        if not local.is_file():
            continue
        try:
            data = json.loads(local.read_text(encoding="utf-8"))
        except ValueError as error:
            raise ValueError(f"{local} does not parse: {error}") from error
        allowed = (data.get("permissions") or {}).get("allow") if isinstance(data, dict) else None
        if allowed or (isinstance(data, dict) and data.get("disableAllHooks")):
            raise ValueError(
                f"{local} holds allow rules or disables hooks; --setting-sources project,local "
                "loads it, so loose will not start"
            )
    return here


def read_mod_dirs(base: Path, level: str, settings: dict) -> tuple[Path, ...]:
    """Effect: the mod folders `kgme.toml [mods]` names for `level` (HANDOFF-0059), each checked
    to be a mod folder under `mods/`, through no symlink and inside the repository
    (`mods.read_mod_problem`); `ValueError` names one that is not."""
    folders = []
    for name in mods.level_mods(level, settings):
        folder = base.resolve() / mods.MODS / name
        problem = mods.read_mod_problem(base.resolve(), folder)
        if problem:
            raise ValueError(f"kgme.toml [mods] {level} names {name}: {problem}")
        folders.append(folder)
    return tuple(folders)
