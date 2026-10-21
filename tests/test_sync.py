"""Tests for `kgme sync` (HANDOFF-0040 acceptance).

Purpose: against a bare repository in `tmp_path` as `origin`, never the network: a commit
with the tracked post-commit hook enabled reaches the bare repo by itself, the commit
returning before the push; a staged unrelated file survives a sync still staged and outside
the ledger commit; an unreachable remote is one `transient` outcome and exit 0; a run with
nothing foreign commits nothing; two consecutive runs make one ledger commit; a branch
behind its upstream is refused, never forced; `sync_io.py` and `sync_git.py` cannot spell a
forced push; the SessionEnd script logs a failure and exits 0. The guarantees added by the
review are in `tests/test_sync_guards.py`.
Inputs: the seed repository of `tests/synctools.py`.
Outputs: pytest assertions.
Side effects: repositories, a `.venv`, and ledger files under `tmp_path` only.
"""

import json
import os
import subprocess
import time
from pathlib import Path

import pytest
from synctools import (
    ENV,
    ROOT,
    SETTINGS,
    ledger_event,
    read_hook_outcomes,
    read_ledger_lines,
    run_git,
    run_sync,
    write_seed,
)

from kgme import events, ledger, sync, sync_io


@pytest.mark.blocking
def test_plan_commits_only_when_a_foreign_event_is_new() -> None:
    own = json.dumps({"actor": sync.OWN_ACTOR, "ts": "2026-10-08T20:00:00.000-07:00"})
    hook = json.dumps({"actor": "claude-code.hook", "ts": "2026-10-08T20:01:00.000-07:00"})
    assert sync.plan_sync([own], (0, 0)).commit is False
    plan = sync.plan_sync([own, hook], (0, 2))
    assert plan.commit is True
    assert plan.message == "ledger: 2 events through 2026-10-08T20:01:00.000-07:00"
    assert plan.push is True and plan.ahead == 2 and plan.behind == 0
    assert sync.plan_sync([], (0, 0)).push is False
    assert sync.plan_sync(["not json"], (0, 0)).commit is True


@pytest.mark.blocking
def test_new_ledger_lines_reads_a_diff_and_untracked_files() -> None:
    diff = '--- a/logs/ledger/x.jsonl\n+++ b/logs/ledger/x.jsonl\n@@ -1,0 +2 @@\n+{"a":1}\n'
    assert sync.new_ledger_lines(diff, ['{"b":2}\n\n{"c":3}\n']) == [
        '{"a":1}',
        '{"b":2}',
        '{"c":3}',
    ]
    assert sync.parse_counts("1 3\n") == (1, 3)
    with pytest.raises(ValueError):
        sync.parse_counts("")


@pytest.mark.blocking
def test_commit_with_the_hook_enabled_reaches_origin_by_itself(tmp_path: Path) -> None:
    repo, bare = write_seed(tmp_path)
    run_git(["config", "core.hooksPath", "control/git-hooks"], repo)
    (repo / "note.txt").write_text("hello\n")
    run_git(["add", "note.txt"], repo)
    started = time.monotonic()
    run_git(["commit", "--quiet", "--message", "a commit"], repo)
    returned = time.monotonic() - started
    outcomes = read_hook_outcomes(repo)
    assert returned < 2.0, f"the commit waited {returned:.1f} s for its hook"
    assert run_git(["rev-parse", "HEAD"], repo) == run_git(["rev-parse", "main"], bare)
    assert not (repo / "logs" / "scratch" / "hook-errors.jsonl").exists()
    assert len(outcomes) == 1 and outcomes[0]["status"] == "ok"
    assert "pushed main" in (repo / "logs" / "scratch" / "sync.log").read_text()
    assert "M logs/ledger/" in run_git(["status", "--porcelain", "--", "logs/ledger"], repo)


@pytest.mark.blocking
def test_staged_unrelated_file_survives_and_stays_out_of_the_ledger_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, bare = write_seed(tmp_path)
    ledger.append(ledger_event(), sync_io.read_dirs(SETTINGS, repo))
    (repo / "staged.txt").write_text("staged\n")
    run_git(["add", "staged.txt"], repo)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert run_git(["diff", "--cached", "--name-only"], repo) == "staged.txt"
    committed = run_git(["show", "--name-only", "--format=%s", "HEAD"], repo).splitlines()
    assert committed[0].startswith("ledger: 1 events through ")
    assert [name for name in committed[1:] if name] == [
        "logs/ledger/" + committed[-1].split("/")[-1]
    ]
    assert all(name.startswith("logs/ledger/") for name in committed[1:] if name)
    assert run_git(["rev-parse", "HEAD"], repo) == run_git(["rev-parse", "main"], bare)


@pytest.mark.transient
def test_unreachable_remote_is_one_transient_outcome_and_exit_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _ = write_seed(tmp_path)
    run_git(["remote", "set-url", "origin", str(tmp_path / "does-not-exist.git")], repo)
    (repo / "note.txt").write_text("ahead\n")
    run_git(["add", "note.txt"], repo)
    run_git(["commit", "--quiet", "--message", "ahead"], repo)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    outcomes = [e for e in read_ledger_lines(repo) if e["kind"] == "outcome" and e["job"] == "sync"]
    assert len(outcomes) == 1
    assert outcomes[0]["status"] == "error" and outcomes[0]["class"] == "transient"
    intents = [e for e in read_ledger_lines(repo) if e["kind"] == "intent" and e["job"] == "sync"]
    assert outcomes[0]["ref"] == intents[0]["id"]


@pytest.mark.blocking
def test_a_run_with_nothing_foreign_pushes_and_commits_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, bare = write_seed(tmp_path)
    (repo / "note.txt").write_text("ahead\n")
    run_git(["add", "note.txt"], repo)
    run_git(["commit", "--quiet", "--message", "ahead"], repo)
    own = events.make_event(source="kgme", actor=sync.OWN_ACTOR, kind="note", summary="own")
    ledger.append(own, sync_io.read_dirs(SETTINGS, repo))
    before = run_git(["rev-parse", "HEAD"], repo)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert run_git(["rev-parse", "HEAD"], repo) == before
    assert run_git(["rev-parse", "main"], bare) == before
    assert "M logs/ledger/" in run_git(["status", "--porcelain", "--", "logs/ledger"], repo)


@pytest.mark.blocking
def test_two_consecutive_runs_make_one_ledger_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, bare = write_seed(tmp_path)
    ledger.append(ledger_event(), sync_io.read_dirs(SETTINGS, repo))
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    first = run_git(["rev-parse", "HEAD"], repo)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert run_git(["rev-parse", "HEAD"], repo) == first
    assert run_git(["rev-parse", "main"], bare) == first
    assert run_git(["rev-list", "--count", "HEAD"], repo) == "2"


@pytest.mark.blocking
def test_behind_upstream_is_refused_never_forced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, bare = write_seed(tmp_path)
    other = tmp_path / "other"
    run_git(["clone", "--quiet", str(bare), str(other)], tmp_path)
    (other / "theirs.txt").write_text("theirs\n")
    run_git(["add", "theirs.txt"], other)
    run_git(["commit", "--quiet", "--message", "theirs"], other)
    run_git(["push", "--quiet"], other)
    remote_head = run_git(["rev-parse", "main"], bare)
    (repo / "ours.txt").write_text("ours\n")
    run_git(["add", "ours.txt"], repo)
    run_git(["commit", "--quiet", "--message", "ours"], repo)
    run_git(["fetch", "--quiet"], repo)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert run_git(["rev-parse", "main"], bare) == remote_head
    outcomes = [e for e in read_ledger_lines(repo) if e["kind"] == "outcome" and e["job"] == "sync"]
    assert len(outcomes) == 1
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "transient"


@pytest.mark.blocking
def test_open_push_intent_is_reconciled_on_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _ = write_seed(tmp_path)
    dirs = sync_io.read_dirs(SETTINGS, repo)
    orphan = events.make_event(
        source="kgme",
        actor=sync.OWN_ACTOR,
        kind="intent",
        job="sync",
        key="sync:push:dead",
        summary="push main dead to origin/main: 1 ahead, 0 behind",
    )
    ledger.append(orphan, dirs)
    assert run_sync(repo, monkeypatch=monkeypatch) == 0
    assert ledger.open_intents("sync", dirs) == []
    closing = [e for e in ledger.read(dirs) if e["ref"] == orphan["id"]]
    assert closing[0]["class"] == "transient" and closing[0]["status"] == "error"


@pytest.mark.blocking
def test_sync_io_cannot_spell_a_forced_push() -> None:
    for name in ("sync_io.py", "sync_git.py"):
        text = (ROOT / "kgme" / name).read_text(encoding="utf-8")
        assert "force" not in text
        assert '"-f"' not in text and "--delete" not in text and "+refs" not in text
    hook = (ROOT / "control" / "git-hooks" / "post-commit").read_text(encoding="utf-8")
    assert "kgme sync --base" in hook and "force" not in hook and "--push" not in hook
    assert 'if [ -n "$KGME_SYNC_RUN" ]; then exit 0; fi' in hook
    assert ') >> "$dir/sync.log" 2>&1 &' in hook
    assert os.access(ROOT / "control" / "git-hooks" / "post-commit", os.X_OK)
    assert os.access(ROOT / "control" / "hooks" / "session_end_sync.sh", os.X_OK)


@pytest.mark.blocking
def test_session_end_script_logs_a_failure_and_exits_zero(tmp_path: Path) -> None:
    project = tmp_path / "not-a-project"
    project.mkdir()
    done = subprocess.run(
        [str(ROOT / "control" / "hooks" / "session_end_sync.sh")],
        cwd=project,
        capture_output=True,
        text=True,
        env={**ENV, "CLAUDE_PROJECT_DIR": str(project)},
    )
    assert done.returncode == 0
    errors = project / "logs" / "scratch" / "hook-errors.jsonl"
    deadline = time.monotonic() + 20
    while not errors.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    lines = errors.read_text().splitlines()
    assert len(lines) == 1 and "session_end_sync.sh" in lines[0]


@pytest.mark.blocking
def test_settings_name_the_session_end_hook_and_check_names_setup() -> None:
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"] for entry in settings["hooks"]["SessionEnd"] for h in entry["hooks"]]
    assert commands == ['"$CLAUDE_PROJECT_DIR"/control/hooks/session_end_sync.sh']
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "core.hooksPath control/git-hooks" in makefile
    assert "run: make setup" in makefile


def run_post_commit(tmp_path: Path, branch: str, atlas: bool = False) -> set[str]:
    """The post-commit hook in a throwaway repository on `branch` (holding `kgme/atlas.py`
    when `atlas`), with a stand-in `uv` that logs each `kgme` subcommand it is asked to run;
    the subcommands started."""
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    if atlas:
        (repo / "kgme").mkdir()
        (repo / "kgme" / "atlas.py").write_text("")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(
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
        cwd=repo,
        check=True,
    )
    if branch != "main":
        subprocess.run(["git", "checkout", "-q", "-b", branch], cwd=repo, check=True)
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    mark = tmp_path / "uv-started"
    uv = home / ".local" / "bin" / "uv"
    # the word after `kgme` is the subcommand: `uv run --frozen --project <repo> kgme <sub> ...`
    uv.write_text(
        f'#!/bin/sh\nnext=0\nfor a in "$@"; do [ "$next" = 1 ] && echo "$a" >> {mark}; '
        f'next=0; [ "$a" = kgme ] && next=1; done\n'
    )
    uv.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k != "KGME_SYNC_RUN"}
    env["HOME"] = str(home)
    subprocess.run(
        ["sh", str(ROOT / "control" / "git-hooks" / "post-commit")], cwd=repo, env=env, check=True
    )
    deadline = time.monotonic() + 3
    expected = (1 if atlas else 0) + (1 if branch == "main" else 0)
    while time.monotonic() < deadline and len(read_marks(mark)) < expected:
        time.sleep(0.1)
    time.sleep(0.3)  # anything else the hook would start
    return read_marks(mark)


def read_marks(mark: Path) -> set[str]:
    """Effect: the subcommands the stand-in `uv` logged."""
    return set(mark.read_text().split()) if mark.exists() else set()


@pytest.mark.blocking
def test_the_post_commit_hook_does_nothing_off_main(tmp_path: Path) -> None:
    """HANDOFF-0049 F1 (Cowork's ruling): design pushes are Michou's; the hook pushes main only."""
    assert run_post_commit(tmp_path, "design") == set()


@pytest.mark.blocking
def test_the_post_commit_hook_syncs_on_main(tmp_path: Path) -> None:
    assert run_post_commit(tmp_path, "main") == {"sync"}


@pytest.mark.blocking
def test_c1_f3_the_atlas_is_regenerated_after_every_commit_on_any_branch(tmp_path: Path) -> None:
    """HANDOFF-0051 review cycle 1 F3: the atlas is local and pushes nothing, so it runs on
    every branch; only `main` syncs. A checkout without `kgme/atlas.py` skips it."""
    assert run_post_commit(tmp_path / "d", "design", atlas=True) == {"atlas"}
    assert run_post_commit(tmp_path / "m", "main", atlas=True) == {"sync", "atlas"}
