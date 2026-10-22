"""Tests for `kgme approve` (HANDOFF-0055).

Purpose: an approval is Michou's act on a commit on `main`: refused under any agent harness
marker and for a commit not on `main`; from a terminal with no marker it records one
`approval` event naming the full commit, and `--show` prints the newest.
Inputs: `tmp_path`; a fixture repository with a commit on `main` and one only on `design`.
Outputs: pytest assertions.
Side effects: a repository and its ledger streams under `tmp_path`.
"""

import subprocess
from pathlib import Path

import pytest

from kgme import approve, config, ledger

SETTINGS = config.read_config()


def run_git(repo: Path, *argv: str) -> str:
    """Effect: one git command in `repo`, with a fixed identity; its stdout."""
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True, text=True,
    )  # fmt: skip
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    base = tmp_path / "repo"
    base.mkdir()
    (base / ".gitignore").write_text("logs/\n")
    run_git(base, "init", "-q", "-b", "main")
    run_git(base, "add", "-A")
    run_git(base, "commit", "-q", "-m", "canvas v1")
    run_git(base, "checkout", "-q", "-b", "design")
    run_git(base, "commit", "-q", "--allow-empty", "-m", "design only")
    run_git(base, "checkout", "-q", "main")
    return base.resolve()


@pytest.fixture
def terminal(monkeypatch) -> None:
    """Michou's terminal: no agent harness marker set."""
    for name in approve.AGENT_MARKERS:
        monkeypatch.delenv(name, raising=False)


def read_approvals(repo: Path) -> list[dict]:
    """Effect: the `approval` events in `repo`'s ledger, in order."""
    found = ledger.read(ledger.read_base_dirs(SETTINGS, repo))
    return [e for e in found if e["kind"] == "approval"]


@pytest.mark.blocking
@pytest.mark.parametrize("marker", approve.AGENT_MARKERS)
def test_under_an_agent_harness_it_is_refused(
    repo: Path, terminal, monkeypatch, capsys, marker: str
) -> None:
    monkeypatch.setenv(marker, "1")
    sha = run_git(repo, "rev-parse", "main")
    assert approve.run_approve(repo, SETTINGS, "canvas", sha) == 2
    assert marker in capsys.readouterr().err
    assert read_approvals(repo) == []


@pytest.mark.blocking
def test_this_session_is_an_agent_harness() -> None:
    """Run from Claude Code (as `make check` is here), the real environment is refused."""
    import os

    if not approve.read_agent(dict(os.environ)):
        pytest.skip("not run under an agent harness")
    assert approve.read_agent(dict(os.environ)) in approve.AGENT_MARKERS


@pytest.mark.blocking
def test_a_commit_not_on_main_is_refused(repo: Path, terminal, capsys) -> None:
    only_design = run_git(repo, "rev-parse", "design")
    assert approve.run_approve(repo, SETTINGS, "canvas", only_design) == 2
    assert "not a commit on main" in capsys.readouterr().err
    assert approve.run_approve(repo, SETTINGS, "canvas", "0" * 40) == 2
    assert read_approvals(repo) == []


@pytest.mark.blocking
def test_from_a_terminal_it_records_and_show_prints_the_newest(
    repo: Path, terminal, capsys
) -> None:
    first = run_git(repo, "rev-parse", "main")
    assert approve.run_approve(repo, SETTINGS, "canvas", first[:10], "the v1 canvas") == 0
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "canvas v2")
    second = run_git(repo, "rev-parse", "main")
    assert approve.run_approve(repo, SETTINGS, "canvas", second) == 0
    [one, two] = read_approvals(repo)
    assert one["source"] == "human" and one["actor"] == "michou" and one["job"] == "approve"
    assert one["key"] == f"approve:canvas:{first}", "the full sha, resolved from a prefix"
    assert "the v1 canvas" in one["summary"]
    capsys.readouterr()
    assert approve.run_show(repo, SETTINGS, "canvas") == 0
    assert capsys.readouterr().out.split()[1] == second
    assert approve.run_show(repo, SETTINGS, "tokens") == 1


@pytest.mark.blocking
def test_c1_f6_a_name_with_a_delimiter_is_refused_and_names_match_whole(
    repo: Path, terminal, capsys
) -> None:
    sha = run_git(repo, "rev-parse", "main")
    assert approve.run_approve(repo, SETTINGS, "canvas:draft", sha) == 2
    assert approve.run_approve(repo, SETTINGS, "canvas-draft", sha) == 0
    capsys.readouterr()
    assert approve.run_show(repo, SETTINGS, "canvas") == 1, "canvas-draft is not canvas"


@pytest.mark.blocking
def test_c1_f7_the_newest_is_by_instant_then_by_id(repo: Path) -> None:
    from kgme import events

    dirs = ledger.read_base_dirs(SETTINGS, repo)

    def write_approval(ts: str, sha: str, id_: str) -> None:
        ledger.append(events.make_event(
            source="human", actor="michou", kind="approval", job="approve",
            key=f"approve:canvas:{sha}", summary="approved", ts=ts, id=id_,
        ), dirs)  # fmt: skip

    write_approval("2026-10-21T01:50:00.000-07:00", "a" * 40, "01M5GW00000000000000000001")
    write_approval("2026-10-21T01:10:00.000-08:00", "b" * 40, "01M5GW00000000000000000002")
    assert approve.read_newest(SETTINGS, repo, "canvas")["key"].endswith("b" * 40)
    write_approval("2026-10-21T01:10:00.000-08:00", "c" * 40, "01M5GW00000000000000000003")
    assert approve.read_newest(SETTINGS, repo, "canvas")["key"].endswith("c" * 40)
