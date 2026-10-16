"""Tests for the guarantees `kgme sync` gained under review of HANDOFF-0040 (AUDIT-0036 to
AUDIT-0040) and Michou's simplification of 2026-10-09.

Purpose: one run owns the push, so a sync with the hook enabled and an unreachable remote
attempts it once (F1); a stalled push is killed with its helpers inside the configured bound
and is one `transient` outcome (F2); a ledger setting wider than the literal pathspec
`logs/ledger` is refused before any effect (F3); a run that finds the sync lock held waits
for the holder and then runs the whole job, a commit's hook pushing its commit, neither
repeating a push the holder just attempted; a wait that runs out is one `transient` note and
nothing else, since every run does the same work (F4, F8, closed by Michou's word).
Inputs: the seed repository of `tests/synctools.py`.
Outputs: pytest assertions.
Side effects: repositories and ledger files under `tmp_path` only; one `sleep` the stalled
push starts, killed by the run under test; threads that hold the lock for seconds.
"""

import copy
import fcntl
import os
import subprocess
import threading
import time
from pathlib import Path

import pytest
from synctools import (
    SETTINGS,
    ledger_event,
    read_hook_outcomes,
    read_sync_events,
    run_git,
    run_sync,
    write_commit,
    write_git_env,
    write_seed,
)

from kgme import events, ledger, sync, sync_git, sync_io


@pytest.mark.blocking
def test_full_sync_with_the_hook_enabled_attempts_the_push_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _ = write_seed(tmp_path)
    run_git(["config", "core.hooksPath", "control/git-hooks"], repo)
    run_git(["remote", "set-url", "origin", str(tmp_path / "does-not-exist.git")], repo)
    ledger.append(ledger_event(), sync_io.read_dirs(SETTINGS, repo))
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert run_git(["rev-list", "--count", "HEAD"], repo) == "2"
    assert run_git(["rev-list", "--count", "@{u}..HEAD"], repo) == "1"
    assert not (repo / "logs" / "scratch" / "hook-errors.jsonl").exists()
    intents = read_sync_events(repo, "intent")
    outcomes = read_sync_events(repo, "outcome")
    assert len(intents) == 1 and len(outcomes) == 1
    assert outcomes[0]["class"] == "transient" and outcomes[0]["ref"] == intents[0]["id"]


@pytest.mark.transient
def test_stalled_push_is_killed_with_its_helpers_and_is_one_transient_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _ = write_seed(tmp_path)
    stall = tmp_path / "stall.sh"
    stall.write_text("#!/bin/sh\nsleep 30\n")
    stall.chmod(0o755)
    run_git(["config", "protocol.ext.allow", "always"], repo)
    run_git(["remote", "set-url", "origin", f"ext::{stall} %S"], repo)
    write_commit(repo)
    settings = copy.deepcopy(SETTINGS)
    settings["sync"]["git_timeout_seconds"] = 2
    write_git_env(monkeypatch)
    started = time.monotonic()
    assert sync_io.run_sync(repo, settings) == 0
    assert time.monotonic() - started < 15
    outcomes = read_sync_events(repo, "outcome")
    assert len(outcomes) == 1 and outcomes[0]["class"] == "transient"
    assert "no answer from the remote in 2 s; killed" in outcomes[0]["summary"]
    for _ in range(20):
        alive = subprocess.run(["pgrep", "-f", str(stall)], capture_output=True, text=True)
        if alive.returncode != 0:
            break
        time.sleep(0.1)
    assert alive.returncode != 0, f"helpers survived the kill: {alive.stdout}"


@pytest.mark.blocking
def test_a_ledger_setting_wider_than_the_literal_pathspec_is_refused_before_any_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    repo, bare = write_seed(tmp_path)
    ledger.append(ledger_event(), sync_io.read_dirs(SETTINGS, repo))
    (repo / "staged.txt").write_text("staged\n")
    run_git(["add", "staged.txt"], repo)
    settings = copy.deepcopy(SETTINGS)
    settings["paths"]["ledger_dir"] = "."
    write_git_env(monkeypatch)
    assert sync_io.run_sync(repo, settings) == 2
    assert "commits 'logs/ledger' and nothing else" in capsys.readouterr().err
    assert run_git(["rev-list", "--count", "HEAD"], repo) == "1"
    assert run_git(["diff", "--cached", "--name-only"], repo) == "staged.txt"
    assert not (repo / ".git" / sync_git.LOCK_NAME).exists()
    assert read_sync_events(repo, "intent") == [] and read_sync_events(repo, "note") == []
    assert sync_git.LEDGER_REL == "logs/ledger"


def run_holder(repo: Path, seconds: float) -> threading.Thread:
    """A thread that holds the sync lock for `seconds`, as a run in flight would."""
    held = os.open(repo / ".git" / sync_git.LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def release() -> None:
        time.sleep(seconds)
        os.close(held)

    thread = threading.Thread(target=release)
    thread.start()
    return thread


@pytest.mark.blocking
def test_a_sync_arriving_during_a_push_waits_then_commits_and_pushes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    repo, bare = write_seed(tmp_path)
    ledger.append(ledger_event(), sync_io.read_dirs(SETTINGS, repo))
    holder = run_holder(repo, 0.6)
    started = time.monotonic()
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    holder.join()
    assert time.monotonic() - started >= 0.5
    assert "waited for the run that held the lock" in capsys.readouterr().out
    assert run_git(["rev-list", "--count", "HEAD"], repo) == "2"
    assert run_git(["rev-parse", "main"], bare) == run_git(["rev-parse", "HEAD"], repo)
    assert len(read_sync_events(repo, "outcome")) == 1


@pytest.mark.blocking
def test_a_commit_arriving_during_a_push_is_pushed_by_its_own_hook(tmp_path: Path) -> None:
    repo, bare = write_seed(tmp_path)
    run_git(["config", "core.hooksPath", "control/git-hooks"], repo)
    holder = run_holder(repo, 0.6)
    write_commit(repo)
    holder.join()
    outcomes = read_hook_outcomes(repo)
    assert run_git(["rev-parse", "main"], bare) == run_git(["rev-parse", "HEAD"], repo)
    assert not (repo / "logs" / "scratch" / "hook-errors.jsonl").exists()
    assert len(outcomes) == 1 and outcomes[0]["status"] == "ok"


@pytest.mark.blocking
def test_a_waiting_run_does_not_repeat_the_push_the_holder_just_attempted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    repo, bare = write_seed(tmp_path)
    run_git(["remote", "set-url", "origin", str(tmp_path / "does-not-exist.git")], repo)
    write_commit(repo)
    head = run_git(["rev-parse", "--short", "HEAD"], repo)
    dirs = sync_io.read_dirs(SETTINGS, repo)
    write_git_env(monkeypatch)
    result: list[int] = []
    contender = threading.Thread(target=lambda: result.append(sync_io.run_sync(repo, SETTINGS)))
    held = os.open(repo / ".git" / sync_git.LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
    contender.start()
    time.sleep(0.3)
    attempt = events.make_event(
        source="kgme",
        actor=sync.OWN_ACTOR,
        kind="outcome",
        job="sync",
        key=f"sync:push:{head}",
        summary="push failed, exit 128: no such directory; the next trigger retries",
        status="error",
        class_="transient",
    )
    ledger.append(attempt, dirs)
    time.sleep(0.3)
    os.close(held)
    contender.join()
    assert result == [0]
    assert f"attempted the push of {head}; not again" in capsys.readouterr().out
    assert read_sync_events(repo, "intent") == []
    assert read_sync_events(repo, "outcome") == [attempt]
    assert run_git(["rev-list", "--count", "HEAD"], repo) == "2"


@pytest.mark.transient
def test_a_wait_that_runs_out_is_one_transient_note_and_nothing_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    repo, bare = write_seed(tmp_path)
    write_commit(repo)
    before = run_git(["rev-parse", "main"], bare)
    settings = copy.deepcopy(SETTINGS)
    settings["sync"]["git_timeout_seconds"] = 1
    write_git_env(monkeypatch)
    holder = run_holder(repo, 2.0)
    assert sync_io.run_sync(repo, settings) == 0
    holder.join()
    assert "the holder or the next trigger does the same work" in capsys.readouterr().err
    assert run_git(["rev-parse", "main"], bare) == before
    assert read_sync_events(repo, "intent") == []
    notes = read_sync_events(repo, "note")
    assert len(notes) == 1 and notes[0]["class"] == "transient" and notes[0]["key"] == "sync:lock"
