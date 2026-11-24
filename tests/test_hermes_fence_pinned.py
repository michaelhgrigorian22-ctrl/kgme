"""Canary cells for the fence's pinned programs (AUDIT-0178 F10, Cowork's ruling on cycle 3).

Purpose: the programs the fence runs, and the `PATH` its rewritten commands run under, come
from `~/.hermes/hooks/kgme-fence.paths`, which install.sh writes once; never from Hermes's
inherited `PATH`. The child `PATH` is the pinned programs' folders, then
`/usr/bin:/bin:/usr/sbin:/sbin`; a relative or empty entry is never used; a missing,
unreadable or malformed paths file refuses every call (fail closed).
Inputs: a fixture home from `tests/fencetools.py`.
Outputs: pytest assertions.
Side effects: files under `tmp_path`; the module runs as a subprocess.
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from fencetools import PATHS_FILE, PINNED, env_of, inside, make_home, outside, write_pinned

SYSTEM = ["/usr/bin", "/bin", "/usr/sbin", "/sbin"]


@pytest.fixture
def home(tmp_path: Path) -> Path:
    return make_home(tmp_path)


def decoys(home: Path) -> Path:
    """Effect: another environment's programs, in `<home>/decoy`."""
    folder = home / "decoy"
    folder.mkdir()
    for name in PINNED:
        exe = folder / name
        exe.write_text("#!/bin/sh\n")
        exe.chmod(0o755)
    return folder


def rewritten(home: Path, command: str, env: dict) -> tuple[str, list[str]]:
    """Effect: the program a call runs as, and its child `PATH` split into entries."""
    v = inside(home, command, env=env)
    assert v.allow and v.args is not None, v.reason
    words = shlex.split(v.args["command"])
    pairs = [w for w in words[2:] if "=" in w.split("/")[0]]
    path = [p for p in pairs if p.startswith("PATH=")]
    assert len(path) == 1, pairs
    return words[2 + len(pairs)], path[0].removeprefix("PATH=").split(":")


@pytest.mark.blocking
@pytest.mark.parametrize("command", ["git status", "kgme lint", "uv run --frozen --project "
                                     "{brain} kgme lint"])  # fmt: skip
def test_f10_an_alternate_environment_does_not_choose_the_programs(
    home: Path, command: str
) -> None:
    other = decoys(home)
    env = env_of(home, PATH=f"{other}:{home / 'bin'}")
    program, path = rewritten(home, command.format(brain=home / "KGME/brain"), env)
    if command.startswith(("git", "uv")):
        assert program == str(home / "bin" / command.split()[0])
    assert str(other) not in path
    assert path == [str(home / "bin"), *SYSTEM]


@pytest.mark.blocking
@pytest.mark.parametrize("inherited", ["", ":", ".", "bin", ".:bin::relative/dir:",
                                       "bin:{decoy}:."])  # fmt: skip
def test_f10_relative_and_empty_path_entries_are_never_used(home: Path, inherited: str) -> None:
    other = decoys(home)
    env = env_of(home, PATH=inherited.format(decoy=other))
    program, path = rewritten(home, "git status", env)
    assert program == str(home / "bin/git")
    assert all(p.startswith("/") for p in path) and str(other) not in path
    assert path == [str(home / "bin"), *SYSTEM]


@pytest.mark.blocking
def test_f10_the_child_path_is_the_pinned_folders_then_the_system(home: Path) -> None:
    folders = {name: home / f"opt-{name}" for name in ("claude", "codex")}
    for name, folder in folders.items():
        folder.mkdir()
        (folder / name).write_text("#!/bin/sh\n")
        (folder / name).chmod(0o755)
    write_pinned(
        home,
        f"git={home}/bin/git\nuv={home}/bin/uv\n"
        f"claude={folders['claude']}/claude\ncodex={folders['codex']}/codex\n",
    )
    _, path = rewritten(home, "kgme lint", env_of(home))
    assert path == [str(home / "bin"), str(folders["claude"]), str(folders["codex"]), *SYSTEM]


def broken(home: Path) -> list[str]:
    b = home / "bin"
    full = {name: f"{name}={b / name}" for name in PINNED}
    noexec = home / "elsewhere/git"
    noexec.write_text("")
    return [
        "",
        "\n".join(v for k, v in full.items() if k != "codex"),  # one missing
        "\n".join([*full.values(), f"sh={b}/git"]),  # an unknown name
        "\n".join([*full.values(), f"git={b}/git"]),  # a name twice
        "\n".join([*full.values()]).replace(f"git={b}/git", "git=bin/git"),  # relative
        "\n".join([*full.values()]).replace(f"git={b}/git", f"git={b}/../bin/git"),
        "\n".join([*full.values()]).replace(f"git={b}/git", f"git={b}:/x/git"),
        "\n".join([*full.values()]).replace(f"git={b}/git", f"git={b}/missing"),
        "\n".join([*full.values()]).replace(f"git={b}/git", f"git={noexec}"),
        "\n".join([*full.values()]).replace(f"git={b}/git", f"git={b}"),  # a folder
        "\n".join([*full.values()]).replace(f"git={b}/git", f"{b}/git"),  # no name
    ]


@pytest.mark.blocking
@pytest.mark.parametrize("case", range(11))
def test_f10_a_malformed_paths_file_fails_closed(home: Path, case: int) -> None:
    write_pinned(home, broken(home)[case])
    for v in (inside(home, "git status"), outside(home, "ls")):
        assert not v.allow and "kgme-fence.paths" in v.reason, (case, v.reason)


@pytest.mark.blocking
def test_f10_a_missing_or_unreadable_paths_file_fails_closed(home: Path) -> None:
    pinned = home / PATHS_FILE
    pinned.chmod(0)
    try:
        if os.access(pinned, os.R_OK):
            pytest.skip("running as a user who reads a mode-0 file")
        assert not inside(home, "git status").allow
    finally:
        pinned.chmod(0o644)
    pinned.unlink()
    for v in (inside(home, "git status"), outside(home, "ls"), inside(home, "kgme lint")):
        assert not v.allow and "kgme-fence.paths" in v.reason, v.reason


@pytest.mark.blocking
def test_f10_the_hook_ignores_the_path_it_was_started_with(home: Path) -> None:
    other = decoys(home)
    brain = home / "KGME/brain"
    call = {"tool_name": "terminal", "tool_input": {"command": "git status",
            "workdir": str(brain)}, "cwd": str(home / "elsewhere")}  # fmt: skip
    done = subprocess.run(
        [sys.executable, "-I", "-m", "kgme.hermes_fence", "--root", str(home / "KGME"),
         "--home", str(home)],
        input=json.dumps(call), capture_output=True, text=True, check=False,
        env=env_of(home, PATH=f".:{other}"),
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    words = shlex.split(json.loads(done.stdout)["args"]["command"])
    assert str(home / "bin/git") in words and not any(str(other) in w for w in words)
