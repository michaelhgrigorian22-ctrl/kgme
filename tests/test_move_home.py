"""Tests for `control/move-home.sh`'s refusals, before it moves anything (HANDOFF-0049 F2).

Purpose: the script refuses while a `claude` or `codex` process has its working directory in
the repository, and also when it cannot tell, because process enumeration failed: an
unknown state is never taken for an idle one. `--check` runs every precondition and stops
before the first mutation, so these tests move nothing.
Inputs: a throwaway `$HOME` holding a one-commit repository at `Projects/Automate`, and
stand-in `pgrep` and `lsof` scripts on `$PATH` that report idle, busy, or failure.
Outputs: pytest assertions.
Side effects: files under `tmp_path` only; the script runs as a subprocess with that `$HOME`.
"""

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "control" / "move-home.sh"


def make_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    repo = home / "Projects" / "Automate"
    repo.mkdir(parents=True)
    for argv in (
        ["git", "init", "-q", "-b", "main"],
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "x",
        ],
    ):
        subprocess.run(argv, cwd=repo, check=True)
    return home


def stand_in(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text("#!/bin/sh\n" + body + "\n")
    path.chmod(0o755)


def run_check(tmp_path: Path, pgrep: str, lsof: str) -> subprocess.CompletedProcess:
    home = make_home(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stand_in(bin_dir, "pgrep", pgrep)
    stand_in(bin_dir, "lsof", lsof.replace("HOME_DIR", str(home)))
    env = {**os.environ, "HOME": str(home), "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    return subprocess.run(
        ["sh", str(SCRIPT), "--check"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def untouched(tmp_path: Path) -> bool:
    return (tmp_path / "home" / "Projects" / "Automate" / ".git").is_dir() and not (
        tmp_path / "home" / "Projects" / "KGME"
    ).exists()


@pytest.mark.blocking
def test_idle_passes_the_check_and_moves_nothing(tmp_path: Path) -> None:
    done = run_check(tmp_path, pgrep="exit 1", lsof="exit 0")
    assert done.returncode == 0, done.stderr
    assert "no claude or codex process" in done.stdout
    assert untouched(tmp_path)


@pytest.mark.blocking
def test_a_busy_process_inside_the_repository_refuses(tmp_path: Path) -> None:
    done = run_check(
        tmp_path,
        pgrep="echo 4242; exit 0",
        lsof="echo p4242; echo fcwd; echo nHOME_DIR/Projects/Automate/kgme; exit 0",
    )
    assert done.returncode == 1 and "refused" in done.stderr and "4242" in done.stderr
    assert untouched(tmp_path)


@pytest.mark.blocking
def test_a_failed_process_enumeration_refuses(tmp_path: Path) -> None:
    done = run_check(tmp_path, pgrep='echo "pgrep: broken" >&2; exit 3', lsof="exit 0")
    assert done.returncode == 1 and "could not list" in done.stderr
    assert untouched(tmp_path)


@pytest.mark.blocking
def test_a_failed_working_directory_lookup_refuses(tmp_path: Path) -> None:
    done = run_check(tmp_path, pgrep="echo 4242; exit 0", lsof='echo "lsof: denied" >&2; exit 1')
    assert done.returncode == 1 and "could not read the working directory" in done.stderr
    assert untouched(tmp_path)
