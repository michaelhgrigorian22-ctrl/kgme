"""`kgme workspace` (HANDOFF-0048 §1) on a fixture repository under `tmp_path`.

Purpose: `create` makes a worktree under `[crew] root` on `crew/<handoff>/<task>` from the
integration branch's head (made from `main` when new), with its record in the main
checkout's scratch and never in the worktree; a second create of the same task is refused;
`list` names it; a workspace is recognised and the main checkout is not; `quarantine`
renames the branch, moves the worktree under `quarantine/`, makes it read-only, marks the
record and writes one `blocking` outcome; `release` and `remove` refuse under an agent
harness and work for Michou; the names and units are what the loop and the guard read.
Inputs: a temporary git repository as the main checkout; settings pointing `[crew] root`
into `tmp_path`.
Outputs: pytest assertions.
Side effects: repositories, worktrees and files under `tmp_path`.
"""

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from kgme import config, ledger, workspace
from kgme.workspace import Task

GIT = [
    "git",
    "-c",
    "user.name=t",
    "-c",
    "user.email=t@example.invalid",
    "-c",
    "core.hooksPath=/dev/null",
]


def repo(tmp_path: Path) -> tuple[Path, dict]:
    main = tmp_path / "main"
    main.mkdir()
    (main / "kgme.toml").write_text("[paths]\nledger_dir = 'logs/ledger'\n")
    (main / "toy.py").write_text("x = 1\n")
    subprocess.run([*GIT, "init", "-q", "-b", "main"], cwd=main, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=main, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "toy: the base"], cwd=main, check=True)
    settings = json.loads(json.dumps(config.read_config()))
    settings["crew"] = {"root": str(tmp_path / "work"), "parallel": 1}
    return main, settings


def task(**more) -> Task:
    defaults = dict(handoff="HANDOFF-9048", name="parse", outputs=("toy.py",),
                    acceptance="true", harness="claude", model="m")  # fmt: skip
    return Task(**(defaults | more))


@pytest.mark.blocking
def test_create_makes_the_worktree_on_its_branch_from_the_integration_head(tmp_path: Path) -> None:
    main, settings = repo(tmp_path)
    where, record = workspace.run_create(settings, main, task(), run="R1")
    assert where == tmp_path / "work" / "handoff-9048-parse" and where.is_dir()
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=where,
                            capture_output=True, text=True).stdout.strip()  # fmt: skip
    assert branch == "crew/HANDOFF-9048/parse" and record["branch"] == branch
    head = subprocess.run(["git", "rev-parse", "main"], cwd=main, capture_output=True, text=True)
    assert record["base"] == head.stdout.strip(), "the integration branch starts at main"
    integration = subprocess.run(["git", "rev-parse", "crew/HANDOFF-9048/integration"], cwd=main,
                                 capture_output=True, text=True).stdout.strip()  # fmt: skip
    assert integration == record["base"]
    assert workspace.read_record_path(settings, main, where.name).is_file()
    assert not (where / "task.json").exists(), "the record never sits in the worktree"
    assert record["outputs"] == ["toy.py"] and record["state"] == "open" and record["run"] == "R1"
    assert record["model"] == "m", "the task's own model"
    with pytest.raises(ValueError, match="exists"):
        workspace.run_create(settings, main, task())
    with pytest.raises(ValueError, match="harness"):
        workspace.run_create(settings, main, task(name="other", harness="gemini"))
    listed = workspace.read_list(settings, main)
    assert [(r["name"], r["branch"], r["state"]) for r in listed] == [
        ("handoff-9048-parse", "crew/HANDOFF-9048/parse", "open")
    ]
    assert workspace.read_is_workspace(where, settings, main)
    assert not workspace.read_is_workspace(main, settings, main)
    assert not workspace.read_is_workspace(tmp_path / "work", settings, main)
    _, defaulted = workspace.run_create(settings, main, task(name="other", model=""), run="R1")
    assert defaulted["model"] == settings["models"]["builder"], "else [crew] model (cycle 1 F9)"


@pytest.mark.blocking
def test_quarantine_kills_renames_moves_and_locks(tmp_path: Path) -> None:
    main, settings = repo(tmp_path)
    where, record = workspace.run_create(settings, main, task(), run="R1")
    sleeper = subprocess.Popen(["sleep", "60"], start_new_session=True)
    try:
        workspace.write_record(settings, main, where.name, record | {"pgid": sleeper.pid})
        dirs = ledger.Dirs(tmp_path / "ledger", tmp_path / "trace", ("Read",))
        got = workspace.run_quarantine(settings, main, where.name, "R1", "it hung", dirs)
        assert sleeper.wait(timeout=15) != 0, "the recorded group was killed"
        assert got["state"] == "quarantined" and got["branch"] == "quarantine/R1/parse"
        moved = tmp_path / "work" / "quarantine" / "handoff-9048-parse"
        assert moved.is_dir() and not where.exists()
        assert not (moved / "toy.py").stat().st_mode & stat.S_IWUSR, "read-only"
        branches = subprocess.run(["git", "branch", "--list", "quarantine/R1/parse"], cwd=main,
                                  capture_output=True, text=True).stdout  # fmt: skip
        assert "quarantine/R1/parse" in branches
        (event,) = ledger.read(dirs, stream="ledger")
        assert event["class"] == "blocking" and event["status"] == "refused"
        assert event["key"] == "quarantine:parse" and "it hung" in event["summary"]
    finally:
        if sleeper.poll() is None:
            sleeper.kill()


@pytest.mark.blocking
def test_release_and_remove_are_michous(tmp_path: Path, monkeypatch) -> None:
    main, settings = repo(tmp_path)
    where, _ = workspace.run_create(settings, main, task(), run="R1")
    dirs = ledger.Dirs(tmp_path / "ledger", tmp_path / "trace", ("Read",))
    workspace.run_quarantine(settings, main, where.name, "R1", "seeded", dirs)
    assert "CLAUDECODE" in workspace.read_michou_only({"CLAUDECODE": "1"})
    assert workspace.read_michou_only({}) == ""
    back = workspace.run_release(settings, main, where.name)
    assert back == where and (where / "toy.py").stat().st_mode & stat.S_IWUSR
    assert workspace.read_record(settings, main, where.name)["state"] == "released"
    workspace.run_remove(settings, main, where.name)
    assert not where.exists() and workspace.read_record(settings, main, where.name) is None


@pytest.mark.blocking
def test_names_units_and_the_outputs_text() -> None:
    assert workspace.workspace_name("HANDOFF-0048", "route") == "handoff-0048-route"
    assert workspace.unit("HANDOFF-0048", "route") == "HANDOFF-0048:route"
    assert workspace.split_unit("HANDOFF-0048:route") == ("HANDOFF-0048", "route")
    assert workspace.split_unit("HANDOFF-0048") == ("HANDOFF-0048", None)
    assert workspace.outputs_text(task(outputs=("a.py", "b/"))) == "## Outputs\n`a.py`, `b/`\n"
    with pytest.raises(ValueError):
        workspace.workspace_name("HANDOFF-0048", "Bad Name")
    crew = workspace.read_crew({"models": {"builder": "m"}})
    assert (crew["parallel"], crew["harness"], crew["model"]) == (1, "claude", "m")
    assert crew["max_width"] == 3
    assert workspace.read_crew({"crew": {"parallel": 5}})["max_width"] == 5, "never below parallel"
    assert crew["root"].endswith("KGME/work")


@pytest.mark.blocking
def test_the_cli_create_list_and_quarantine_round_trip(tmp_path: Path, capsys) -> None:
    import argparse

    main, settings = repo(tmp_path)
    args = argparse.Namespace(
        action="create", handoff="HANDOFF-9048", task="parse", outputs="toy.py",
        acceptance="true", harness=None, model=None,
    )  # fmt: skip
    assert workspace.run_workspace(args, main, settings) == 0
    assert workspace.run_workspace(argparse.Namespace(action="list"), main, settings) == 0
    assert "handoff-9048-parse\tcrew/HANDOFF-9048/parse\topen" in capsys.readouterr().out
    os.environ.pop("CLAUDECODE", None)
    args = argparse.Namespace(action="quarantine", name="handoff-9048-parse", run="R2", reason="x")
    assert workspace.run_workspace(args, main, settings) == 0
    assert "quarantined" in capsys.readouterr().out
