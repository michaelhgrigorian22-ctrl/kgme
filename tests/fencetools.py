"""Helpers shared by the Hermes fence suites (`tests/test_hermes_fence*.py`, HANDOFF-0073).

Purpose: a fixture home holding a root (`<home>/KGME`, the stand-in for `~/Projects/KGME`) with
a brain, a work checkout and the brain's `.venv/bin/kgme`; a folder outside it; a `bin` of
stand-in programs, pinned in `<home>/.hermes/hooks/kgme-fence.paths`; and calls to the fence
as Hermes's hook payload carries them (`agent/shell_hooks.py:1-5`, `:87-106`).
Inputs: `tmp_path`.
Outputs: paths, environments, `Verdict`s.
Side effects: files under `tmp_path`.
"""

import json
from pathlib import Path

from kgme import hermes_fence as fence
from kgme.hermes_fence_policy import Verdict

PROGRAMS = ("git", "ls", "cat", "grep", "rg", "uv", "claude", "codex")
PINNED = ("git", "uv", "claude", "codex")
PATHS_FILE = ".hermes/hooks/kgme-fence.paths"


def make_home(tmp_path: Path) -> Path:
    """Effect: the real home: the root is `<home>/KGME`, programs live in `<home>/bin`."""
    base = tmp_path / "KGME"
    for folder in ("brain/kgme", "brain/control", "brain/docs/handoff/proposed", "brain/docs/adr",
                   "brain/docs/readers", "brain/docs/audit", "brain/memory/notes",
                   "brain/.venv/bin", "work/handoff-1/docs/handoff"):  # fmt: skip
        (base / folder).mkdir(parents=True)
    (base / "brain/kgme/cli.py").write_text("")
    (base / "brain/.venv/bin/kgme").write_text("#!/bin/sh\n")
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / "bin").mkdir()
    for name in PROGRAMS:
        exe = tmp_path / "bin" / name
        exe.write_text("#!/bin/sh\n")
        exe.chmod(0o755)
    write_pinned(tmp_path.resolve())
    return tmp_path.resolve()


def write_pinned(home: Path, text: str | None = None) -> Path:
    """Effect: the paths file install.sh writes (AUDIT-0178 F10), pinning `<home>/bin/*` by
    default, or holding `text`."""
    path = home / PATHS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if text is None:
        text = "".join(f"{name}={home / 'bin' / name}\n" for name in PINNED)
    path.write_text(text)
    return path


def case_insensitive(home: Path) -> bool:
    """Effect: the fixture's filesystem treats `kgme` and `KGME` as one folder (macOS's default)."""
    return (home / "kgme").exists()


def env_of(home: Path, **more: str) -> dict:
    return {"HOME": str(home), "PATH": str(home / "bin"), "KGME_CONDUCTOR": "hermes", **more}


def verdict(home: Path, tool: str, args: dict, process: Path | None = None,
            env: dict | None = None) -> Verdict:  # fmt: skip
    """Effect: the fence's verdict on one call, Hermes started in `process` (outside by default)."""
    where = str(process or home / "elsewhere")
    payload = json.dumps({"hook_event_name": "pre_tool_call", "tool_name": tool,
                          "tool_input": args, "cwd": where})  # fmt: skip
    return fence.run_decide(payload, home / "KGME", env or env_of(home), home)


def run(home: Path, command: str, workdir: Path | str | None = None, process: Path | None = None,
        env: dict | None = None) -> Verdict:  # fmt: skip
    """Effect: a terminal call; no `workdir` means Hermes's session directory, unknown."""
    args: dict = {"command": command}
    if workdir is not None:
        args["workdir"] = str(workdir)
    return verdict(home, "terminal", args, process, env)


def outside(home: Path, command: str, **kw) -> Verdict:
    """Effect: a terminal call whose directory the fence knows, outside the root."""
    return run(home, command, workdir=home / "elsewhere", **kw)


def inside(home: Path, command: str, **kw) -> Verdict:
    return run(home, command, workdir=home / "KGME/brain", **kw)


def patch(*ops: str) -> dict:
    return {"mode": "patch", "patch": "*** Begin Patch\n" + "".join(ops) + "*** End Patch\n"}
