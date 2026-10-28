"""`kgme workspace`: KGME-owned worktrees, one per crew task (HANDOFF-0048 §1, amendment 1).

Purpose: a task's worktree lives under `kgme.toml [crew] root` (`~/Projects/KGME/work/`,
beside `brain/` and `design/`), outside the repository and outside every harness's own
folder, on `crew/<handoff>/<task>` from the integration branch's head (`crew/<handoff>`,
made from `main` when it does not exist yet). Its record, `task.json` (the task's `Outputs`,
acceptance check, harness, model, level, branch, base), lives in the main checkout's
`logs/scratch/workspaces/<name>/`, never in the worktree: the sandbox lets a builder's Bash
write anywhere in its working directory (the residual of 2026-10-21), so a record kept there
would be the builder's to edit. The guard treats the worktree as the repository for its path
checks and the ledger stays the main checkout's (HANDOFF-0047 §3). `quarantine` kills the
task's process group, renames its branch `quarantine/<run>/<task>`, moves the worktree under
`<root>/quarantine/`, removes write permission and appends a `blocking` outcome; `release`
and `remove` are Michou's commands and refuse to run under an agent harness, at any level.
The cheap lane's exports share the root (`cheap-<run>/`) and never a subfolder.
Inputs: the main checkout, the parsed `kgme.toml`, a task, a name, a run id.
Outputs: paths, records, the list of workspaces; `ValueError` naming a refusal.
Side effects: `git worktree add|move|remove`, `git branch -m`, `uv sync --frozen` in a new
worktree; the record file; `chmod`; `killpg`; one ledger event on a quarantine.
"""

import json
import os
import signal
import stat
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from kgme import approve, events, ledger, paths
from kgme.crew import (  # noqa: F401 - the pure names, re-exported (review cycle 1 F17)
    HANDOFF_ID,
    HARNESSES,
    INTEGRATION,
    MAX_WIDTH_DEFAULT,
    PARALLEL_DEFAULT,
    PLAN_CYCLES_DEFAULT,
    TASK_NAME,
    TRUNK,
    Task,
    branch_name,
    integration_branch,
    outputs_text,
    quarantine_branch,
    read_crew,
    split_unit,
    unit,
    workspace_name,
)
from kgme.sync_git import run_git

RECORDS = "workspaces"
QUARANTINE = "quarantine"


# ---------------------------------------------------------------- effects


def read_root(settings: dict, main: Path) -> Path:
    """Effect: the workspace root, `[crew] root`, resolved."""
    return paths.resolve(str(read_crew(settings)["root"]), main).expanduser().resolve()


def read_record_path(settings: dict, main: Path, name: str) -> Path:
    """Effect: where `name`'s record lives, in the main checkout's scratch."""
    return paths.scratch_dir(settings, main) / RECORDS / name / "task.json"


def write_record(settings: dict, main: Path, name: str, record: dict) -> Path:
    """Effect: the record, written whole; returns its path."""
    path = read_record_path(settings, main, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_record(settings: dict, main: Path, name: str) -> dict | None:
    """Effect: `name`'s record, or None when it has none."""
    path = read_record_path(settings, main, name)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def read_is_workspace(path: Path, settings: dict, main: Path) -> bool:
    """Effect: `path` is a KGME workspace: under the root, not the main checkout, and a
    worktree of it."""
    here = path.resolve()
    root = read_root(settings, main)
    if here == main.resolve() or here == root or not here.is_relative_to(root):
        return False
    try:
        return ledger.read_main_checkout(here) == main.resolve()
    except RuntimeError:
        return False


def read_integration_head(main: Path, handoff: str) -> str:
    """Effect: the integration branch's head, made from `main` when the branch is new."""
    branch = integration_branch(handoff)
    found = run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], main, check=False)
    if found.returncode == 0 and found.stdout.strip():
        return found.stdout.strip()
    run_git(["branch", branch, TRUNK], main)
    return run_git(["rev-parse", f"refs/heads/{branch}"], main).stdout.strip()


def run_create(settings: dict, main: Path, task: Task, run: str = "") -> tuple[Path, dict]:
    """Effect: the task's worktree on its branch from the integration head, its environment
    synced, and its record; `ValueError` when either exists already."""
    if task.harness not in HARNESSES:
        raise ValueError(f"unknown harness {task.harness!r}; one of {', '.join(HARNESSES)}")
    from kgme import loop_outputs

    kept = tuple(loop_outputs.parse_outputs(outputs_text(task)))
    if not task.outputs or kept != tuple(task.outputs):
        refused = sorted(set(task.outputs) - set(kept)) or ["(none)"]
        raise ValueError(f"Outputs must be relative paths inside the repository: {refused}")
    name = workspace_name(task.handoff, task.name)
    where = read_root(settings, main) / name
    if where.exists():
        raise ValueError(f"{where} exists; `kgme workspace remove {name}` is Michou's")
    if read_record(settings, main, name) is not None:
        raise ValueError(f"{name} has a record already; remove it first")
    branch = branch_name(task.handoff, task.name)
    base = read_integration_head(main, task.handoff)
    where.parent.mkdir(parents=True, exist_ok=True)
    run_git(["worktree", "add", "-q", "-b", branch, str(where), base], main, timeout=120)
    if (where / "uv.lock").is_file():
        subprocess.run(["uv", "sync", "--frozen", "--quiet"], cwd=where, check=True)
    record = {
        **asdict(task),
        "outputs": list(task.outputs),
        "after": list(task.after),
        "name": task.name,
        "model": task.model or str(read_crew(settings)["model"]),  # resolved once (F9)
        "workspace": str(where),
        "branch": branch,
        "base": base,
        "run": run,
        "created": events.now_iso(),
        "state": "open",
    }
    write_record(settings, main, name, record)
    return where, record


def read_worktrees(main: Path) -> list[tuple[Path, str]]:
    """Effect: every worktree of the repository as (path, branch), from `git worktree list`."""
    listed = run_git(["worktree", "list", "--porcelain"], main).stdout
    found: list[tuple[Path, str]] = []
    path, branch = None, ""
    for line in listed.splitlines() + [""]:
        if line.startswith("worktree "):
            path, branch = Path(line[len("worktree ") :]), ""
        elif line.startswith("branch "):
            branch = line[len("branch ") :].removeprefix("refs/heads/")
        elif not line and path is not None:
            found.append((path, branch))
            path = None
    return found


def read_list(settings: dict, main: Path) -> list[dict]:
    """Effect: the workspaces under the root, each with its branch and its record's state."""
    root = read_root(settings, main)
    rows = []
    for path, branch in read_worktrees(main):
        if not path.resolve().is_relative_to(root) or path.resolve() == main.resolve():
            continue
        record = read_record(settings, main, path.name) or {}
        rows.append({
            "name": path.name, "path": str(path), "branch": branch,
            "state": record.get("state", "no record"), "task": record.get("name"),
        })  # fmt: skip
    return rows


def write_read_only(folder: Path) -> int:
    """Effect: write permission removed from every file and folder under `folder` (symlinks
    left alone); the count touched."""
    touched = 0
    for current, dirs, files in os.walk(folder, topdown=False):
        for name in files + dirs:
            path = Path(current) / name
            if path.is_symlink():
                continue
            mode = path.stat().st_mode
            path.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
            touched += 1
    folder.chmod(folder.stat().st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    return touched + 1


def write_writable(folder: Path) -> None:
    """Effect: the owner's write permission restored under `folder`."""
    folder.chmod(folder.stat().st_mode | stat.S_IWUSR)
    for current, dirs, files in os.walk(folder):
        for name in files + dirs:
            path = Path(current) / name
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)


def kill_recorded_group(record: dict, grace: float = 10.0) -> bool:
    """Effect: SIGTERM to the process group the record names, SIGKILL after `grace`; False
    when none is recorded or alive."""
    from kgme import loop

    pgid = record.get("pgid")
    if not isinstance(pgid, int) or pgid <= 1:
        return False
    alive = any(group == pgid for _, _, group in loop.read_group())
    if not alive:
        return False
    loop.signal_group(pgid, signal.SIGTERM)
    import time

    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        if not any(group == pgid for _, _, group in loop.read_group()):
            return True
        time.sleep(0.1)
    loop.signal_group(pgid, signal.SIGKILL)
    return True


def run_quarantine(
    settings: dict, main: Path, name: str, run: str, reason: str, dirs: ledger.Dirs | None = None
) -> dict:
    """Effect: the task's group killed, its branch renamed, its worktree moved under the
    root's `quarantine/` and made read-only, its record marked, and one `blocking` outcome in
    the ledger; returns the record. `ValueError` for a name with no workspace."""
    root = read_root(settings, main)
    record = read_record(settings, main, name)
    where = root / name
    if record is None or not where.is_dir():
        raise ValueError(f"{name} is not a workspace under {root}")
    killed = kill_recorded_group(record)
    task = str(record.get("name") or name)
    target_branch = quarantine_branch(run, task)
    branch = str(record.get("branch") or "")
    if branch:
        run_git(["branch", "-m", branch, target_branch], main, check=False)
    pen = root / QUARANTINE
    pen.mkdir(parents=True, exist_ok=True)
    moved = pen / name
    run_git(["worktree", "move", str(where), str(moved)], main, timeout=120)
    write_read_only(moved)
    record |= {"state": "quarantined", "quarantine_run": run, "branch": target_branch,
               "workspace": str(moved), "reason": reason, "killed": killed}  # fmt: skip
    write_record(settings, main, name, record)
    handoff = str(record.get("handoff") or "")
    ledger.append(
        events.make_event(
            source="kgme",
            actor="kgme.workspace",
            kind="outcome",
            status="refused",
            class_="blocking",
            job=f"crew:{handoff}",
            key=f"quarantine:{task}",
            run_id=run or None,
            summary=events.clip(
                f"crew {handoff} task {task} quarantined: {reason}; branch "
                f"{target_branch}; worktree read-only under quarantine/"
            ),
        ),  # fmt: skip
        dirs or ledger.read_base_dirs(settings, main),
    )
    return record


def read_michou_only(environ: dict[str, str] | None = None) -> str:
    """Effect: why this command may not run here, or "": `release` and `remove` are Michou's,
    typed in his own terminal, never under an agent harness (HANDOFF-0048 §1)."""
    agent = approve.read_agent(dict(os.environ if environ is None else environ))
    return (
        f"refused: {agent} is set, so an agent harness runs this; it is Michou's" if agent else ""
    )


def run_release(settings: dict, main: Path, name: str) -> Path:
    """Effect (Michou's): a quarantined worktree made writable and moved back under the
    root; its branch keeps its quarantine name, for him to rename or delete."""
    root = read_root(settings, main)
    record = read_record(settings, main, name)
    held = root / QUARANTINE / name
    if record is None or not held.is_dir():
        raise ValueError(f"{name} is not quarantined under {root / QUARANTINE}")
    write_writable(held)
    back = root / name
    run_git(["worktree", "move", str(held), str(back)], main, timeout=120)
    write_record(settings, main, name, record | {"state": "released", "workspace": str(back)})
    return back


def run_remove(settings: dict, main: Path, name: str) -> None:
    """Effect (Michou's): the worktree removed whatever it holds, and its record; the branch
    stays, his to delete."""
    root = read_root(settings, main)
    for where in (root / name, root / QUARANTINE / name):
        if where.is_dir():
            write_writable(where)
            run_git(["worktree", "remove", "--force", str(where)], main, timeout=120)
    run_git(["worktree", "prune"], main, check=False)
    record = read_record_path(settings, main, name)
    if record.is_file():
        record.unlink()


def run_workspace(args, main: Path, settings: dict) -> int:
    """The command: create, list, quarantine, release, remove."""
    try:
        if args.action == "create":
            outputs = tuple(p.strip() for p in (args.outputs or "").split(",") if p.strip())
            task = Task(args.handoff, args.task, outputs, args.acceptance or "",
                        args.harness or read_crew(settings)["harness"],
                        args.model or read_crew(settings)["model"])  # fmt: skip
            where, record = run_create(settings, main, task)
            print(f"{where} on {record['branch']} from {record['base'][:12]}")
            return 0
        if args.action == "list":
            for row in read_list(settings, main):
                print(f"{row['name']}\t{row['branch']}\t{row['state']}\t{row['path']}")
            return 0
        if args.action == "quarantine":
            record = run_quarantine(settings, main, args.name, args.run or events.new_ulid(),
                                    args.reason or "quarantined by hand")  # fmt: skip
            print(f"{args.name}: {record['state']}, branch {record['branch']}")
            return 0
        refused = read_michou_only()
        if refused:
            print(f"kgme workspace {args.action}: {refused}", file=sys.stderr)
            return 2
        if args.action == "release":
            print(run_release(settings, main, args.name))
            return 0
        run_remove(settings, main, args.name)
        print(f"{args.name}: removed")
        return 0
    except (ValueError, subprocess.CalledProcessError, OSError) as error:
        print(f"kgme workspace {args.action}: {error}", file=sys.stderr)
        return 2
