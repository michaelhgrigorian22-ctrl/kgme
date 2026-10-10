"""Helpers shared by the sync tests (`tests/test_sync.py`, `tests/test_sync_guards.py`).

Purpose: seed a repository holding the working tree's `kgme/`, `tools/`, `kgme.toml`,
`pyproject.toml`, `uv.lock`, and `.gitignore` with a bare `origin` under `tmp_path`, so the
staged code is what the hook runs, through `uv` offline; run git and `kgme sync` against it;
read its ledger; wait for the backgrounded hook.
Inputs: the working tree and the repository's `kgme.toml`.
Outputs: functions and the scrubbed environment every child gets.
Side effects: repositories, a `.venv`, and ledger files under `tmp_path` only.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

from kgme import cli, config, events, ledger, paths, sync_io

ROOT = paths.root()
SETTINGS = config.read_config()
COPIED = ("kgme", "tools", "kgme.toml", "pyproject.toml", "uv.lock", ".gitignore")
# `VIRTUAL_ENV` is scrubbed: pytest runs under `uv run`, and a child `uv run --project` with no
# project under it falls back to the active environment, which is this repository's.
ENV = {
    **{k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")},
    "GIT_AUTHOR_NAME": "kgme-test",
    "GIT_AUTHOR_EMAIL": "test@kgme.local",
    "GIT_COMMITTER_NAME": "kgme-test",
    "GIT_COMMITTER_EMAIL": "test@kgme.local",
    "GIT_TERMINAL_PROMPT": "0",
    "UV_OFFLINE": "1",
}


def run_git(args: list[str], cwd: Path) -> str:
    done = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=ENV
    )
    return done.stdout.strip()


def ledger_event(summary: str = "a hook event") -> dict:
    return events.make_event(
        source="claude-code", actor="claude-code.hook", kind="note", summary=summary
    )


def read_ledger_lines(repo: Path) -> list[dict]:
    dirs = sync_io.read_dirs(SETTINGS, repo)
    return ledger.read(dirs, stream="ledger")


def read_sync_events(repo: Path, kind: str) -> list[dict]:
    return [e for e in read_ledger_lines(repo) if e["kind"] == kind and e["job"] == "sync"]


def write_seed(tmp_path: Path) -> tuple[Path, Path]:
    """A repository holding the working tree's code and one committed ledger event, with a
    bare `origin` it is up to date with. Returns `(repo, bare)`."""
    bare = tmp_path / "origin.git"
    run_git(["init", "--quiet", "--bare", "--initial-branch=main", str(bare)], tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    for name in COPIED:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, repo / name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, repo / name)
    ledger.append(ledger_event("seed"), sync_io.read_dirs(SETTINGS, repo))
    run_git(["init", "--quiet", "--initial-branch=main"], repo)
    run_git(["add", "--all"], repo)
    run_git(["commit", "--quiet", "--message", "seed"], repo)
    run_git(["remote", "add", "origin", str(bare)], repo)
    run_git(["push", "--quiet", "--set-upstream", "origin", "main"], repo)
    return repo, bare


def write_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in ENV.items():
        if name.startswith(("GIT_", "UV_")):
            monkeypatch.setenv(name, value)


def run_sync(repo: Path, *flags: str, monkeypatch: pytest.MonkeyPatch) -> int:
    write_git_env(monkeypatch)
    return cli.main(["sync", "--base", str(repo), *flags])


def write_commit(repo: Path) -> None:
    """One commit the upstream lacks."""
    (repo / "note.txt").write_text("ahead\n")
    run_git(["add", "note.txt"], repo)
    run_git(["commit", "--quiet", "--message", "ahead"], repo)


def read_hook_outcomes(repo: Path, seconds: float = 20.0) -> list[dict]:
    """The sync outcomes once the backgrounded post-commit hook has recorded one, polling for
    up to `seconds`; the list is empty if it never did."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        outcomes = read_sync_events(repo, "outcome")
        if outcomes:
            return outcomes
        time.sleep(0.2)
    return []
