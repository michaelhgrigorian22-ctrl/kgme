"""Tests for `kgme merge design` (HANDOFF-0055).

Purpose: the acceptance test in a temporary copy of a repository: a design commit inside the
lanes lands on `main` by itself; one outside them is refused with each path and the trial's
result named; a red trial leaves `main` untouched; a staged file makes the merge wait
(`transient`) and the next trigger lands it; the post-commit hook line merges within a minute.
Inputs: `tmp_path`; a fixture repository whose `make check` is a stand-in that reads a file.
Outputs: pytest assertions.
Side effects: repositories, worktrees, and ledger streams under `tmp_path` and the system
temporary folder (the trial's, removed).
"""

import subprocess
import time
from pathlib import Path

import pytest

from kgme import config, ledger, merge, paths

ROOT = paths.root()
SETTINGS = config.read_config()
# a stand-in for `make check`: red when the tree holds RED
MAKEFILE = "check:\n\t@test ! -e RED\n"


def run_git(repo: Path, *argv: str) -> str:
    """Effect: one git command in `repo`, with a fixed identity and no hooks; its stdout."""
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True, text=True,
    )  # fmt: skip
    return done.stdout.strip()


def write_repo(tmp_path: Path) -> Path:
    """Effect: a repository on `main` with a `design` branch at the same commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Makefile").write_text(MAKEFILE)
    (repo / ".gitignore").write_text("logs/\n")
    (repo / "README.md").write_text("fixture\n")
    run_git(repo, "init", "-q", "-b", "main")
    run_git(repo, "config", "user.name", "t")
    run_git(repo, "config", "user.email", "t@localhost")
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", "fixture")
    run_git(repo, "branch", "design")
    return repo.resolve()


def write_commit(repo: Path, branch: str, files: dict[str, str]) -> str:
    """Effect: one commit on `branch` holding `files`; back on `main`; its sha."""
    run_git(repo, "checkout", "-q", branch)
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", f"{branch}: {', '.join(files)}")
    sha = run_git(repo, "rev-parse", "HEAD")
    run_git(repo, "checkout", "-q", "main")
    return sha


def read_wide_settings() -> str:
    """Pure over this repository's kgme.toml: the same settings with the design lanes widened
    to `control/` and `docs/` and the check made trivial, as a branch's own copy might be."""
    import re

    text = (ROOT / "kgme.toml").read_text()
    text = re.sub(r"(?ms)^\[tracks\.design\].*?(?=^\[|\Z)", "", text)
    return text + '\n[tracks.design]\nlanes = ["control/", "docs/"]\ncheck = ["true"]\n'


def read_merge_events(repo: Path) -> list[dict]:
    """Effect: the `merge` events in `repo`'s ledger, in order."""
    return [e for e in ledger.read(ledger.read_base_dirs(SETTINGS, repo)) if e["job"] == "merge"]


@pytest.mark.blocking
def test_lane_paths_holds_folders_and_globs() -> None:
    lanes = merge.DEFAULT_LANES["design"]
    changed = [
        "docs/design/canvas.md",
        "docs/readers/cockpit-design-notes.md",
        "tests/test_design_canvas.py",
        "control/review/design.md",
        "docs/readers/sessions.md",
        "docs/designer.md",
    ]
    assert merge.lane_paths(changed, lanes) == [
        "control/review/design.md", "docs/designer.md", "docs/readers/sessions.md",
    ]  # fmt: skip


@pytest.mark.blocking
def test_is_quiet_names_each_reason() -> None:
    quiet = merge.Checkout("main", "a" * 40, False, False, ())
    assert merge.is_quiet(quiet, "a" * 40) == ""
    assert "not main" in merge.is_quiet(
        merge.Checkout("design", "a" * 40, False, False, ()), "a" * 40
    )
    assert "moved" in merge.is_quiet(quiet, "b" * 40)
    assert "index.lock" in merge.is_quiet(
        merge.Checkout("main", "a" * 40, False, True, ()), "a" * 40
    )
    busy = merge.Checkout("main", "a" * 40, False, False, ("MERGE_HEAD",))
    assert "MERGE_HEAD" in merge.is_quiet(busy, "a" * 40)
    assert "differs" in merge.is_quiet(merge.Checkout("main", "a" * 40, True, False, ()), "a" * 40)


@pytest.mark.blocking
def test_nothing_to_do_writes_nothing(tmp_path: Path) -> None:
    repo = write_repo(tmp_path)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert read_merge_events(repo) == []


@pytest.mark.blocking
def test_a_design_commit_inside_the_lanes_lands_on_main(tmp_path: Path) -> None:
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/canvas.md": "v1\n"})
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""
    assert (
        run_git(repo, "log", "-1", "--format=%s", "main")
        == f"merge: design {sha[:12]} (kgme merge)"
    )
    assert run_git(repo, "rev-list", "--count", "--parents", "-1", "main")  # a merge commit
    assert len(run_git(repo, "log", "-1", "--format=%P", "main").split()) == 2
    found = read_merge_events(repo)
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["status"] == "ok" and found[1]["key"] == f"merge:design:{sha}"
    assert len(run_git(repo, "worktree", "list").splitlines()) == 1, "the trial is removed"


@pytest.mark.blocking
def test_a_design_commit_outside_the_lanes_is_refused_naming_the_path(
    tmp_path: Path, capsys
) -> None:
    repo = write_repo(tmp_path)
    before = run_git(repo, "rev-parse", "main")
    write_commit(repo, "design", {"docs/design/a.md": "x\n", "control/review/design.md": "p\n"})
    assert merge.run_merge(repo, SETTINGS) == 1
    err = capsys.readouterr().err
    assert "control/review/design.md" in err and "trial green" in err
    assert "docs/design/a.md" not in err.split("outside the lanes")[1]
    assert run_git(repo, "rev-parse", "main") == before
    assert read_merge_events(repo)[-1]["status"] == "refused"


@pytest.mark.blocking
def test_a_red_trial_leaves_main_untouched(tmp_path: Path, capsys) -> None:
    repo = write_repo(tmp_path)
    before = run_git(repo, "rev-parse", "main")
    write_commit(repo, "design", {"docs/design/RED.md": "x\n"})
    settings = {**SETTINGS, "tracks": {"design": {"check": ["sh", "-c", "exit 3"]}}}
    assert merge.run_merge(repo, settings) == 1
    assert "trial red" in capsys.readouterr().err
    assert run_git(repo, "rev-parse", "main") == before
    assert read_merge_events(repo)[-1]["status"] == "error"
    assert len(run_git(repo, "worktree", "list").splitlines()) == 1, "the trial is removed"


@pytest.mark.blocking
def test_the_trial_runs_the_tracks_make_check(tmp_path: Path, capsys) -> None:
    """The default check is the trial tree's own `make check`: a tree it finds red stays out."""
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/x.md": "x\n", "RED": ""})
    assert merge.run_merge(repo, SETTINGS) == 1  # RED is outside the lanes too; red comes first
    assert "trial red: make check exited" in capsys.readouterr().err


@pytest.mark.blocking
def test_a_staged_file_makes_the_merge_wait_and_the_next_trigger_lands_it(
    tmp_path: Path, capsys
) -> None:
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/canvas.md": "v2\n"})
    (repo / "README.md").write_text("an edit in progress\n")
    run_git(repo, "add", "README.md")
    before = run_git(repo, "rev-parse", "main")
    assert merge.run_merge(repo, SETTINGS) == 0
    assert "waiting" in capsys.readouterr().err
    assert run_git(repo, "rev-parse", "main") == before
    waited = read_merge_events(repo)[-1]
    assert waited["status"] == "error" and waited["class"] == "transient"
    run_git(repo, "commit", "-q", "-m", "the edit")
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""


@pytest.mark.blocking
def test_a_dry_run_records_and_merges_nothing(tmp_path: Path, capsys) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/canvas.md": "v3\n"})
    before = run_git(repo, "rev-parse", "main")
    assert merge.run_merge(repo, SETTINGS, dry_run=True) == 0
    assert "dry run" in capsys.readouterr().out
    assert run_git(repo, "rev-parse", "main") == before and read_merge_events(repo) == []


@pytest.mark.blocking
def test_from_the_design_worktree_it_merges_in_the_main_checkout(tmp_path: Path) -> None:
    repo = write_repo(tmp_path)
    worktree = tmp_path / "design-worktree"
    run_git(repo, "worktree", "add", "-q", str(worktree), "design")
    (worktree / "docs" / "design").mkdir(parents=True)
    (worktree / "docs" / "design" / "w.md").write_text("w\n")
    run_git(worktree, "add", "-A")
    run_git(worktree, "commit", "-q", "-m", "design: w")
    assert merge.run_merge(worktree.resolve(), SETTINGS) == 0
    assert (repo / "docs" / "design" / "w.md").is_file()
    assert read_merge_events(repo) and not (worktree / "logs").exists(), "one ledger, the main's"


@pytest.mark.blocking
def test_the_post_commit_hook_line_lands_a_design_commit_within_a_minute(tmp_path: Path) -> None:
    """The hook's line, as `control/git-hooks/post-commit` runs it, in the background."""
    repo = write_repo(tmp_path)
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "post-commit").write_text(
        "#!/bin/sh\n"
        'repo="$(git rev-parse --show-toplevel)"\n'
        f'( uv run --frozen --project "{ROOT}" kgme merge design --base "$repo" ) '
        '>> "$repo/merge.log" 2>&1 &\n'
    )
    (hooks / "post-commit").chmod(0o755)
    run_git(repo, "config", "core.hooksPath", str(hooks))
    sha = write_commit(repo, "design", {"docs/design/hooked.md": "h\n"})
    (repo / "notes.txt").write_text("a commit on main\n")
    run_git(repo, "add", "notes.txt")
    run_git(repo, "commit", "-q", "-m", "main: notes")
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        landed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, "main"], cwd=repo, check=False
        )
        if landed.returncode == 0:
            break
        time.sleep(0.5)
    log = (repo / "merge.log").read_text() if (repo / "merge.log").exists() else ""
    assert landed.returncode == 0, log


@pytest.mark.blocking
def test_c1_f1_the_merge_lands_the_tested_commit_not_a_later_one(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 1 F1: a design commit made during the trial is neither checked nor
    lane-validated, so it must not ride in on the branch name."""
    repo = write_repo(tmp_path)
    tested = write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    real = merge.run_trial

    def run_trial_then_advance(*args):
        result = real(*args)
        write_commit(repo, "design", {"control/review/late.md": "late\n"})
        return result

    monkeypatch.setattr(merge, "run_trial", run_trial_then_advance)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "log", "-1", "--format=%P", "main").split()[1] == tested
    assert not (repo / "control" / "review" / "late.md").exists()


@pytest.mark.blocking
def test_c1_f2_a_rename_out_of_a_human_path_is_refused_naming_its_source(
    tmp_path: Path, capsys
) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "main", {"control/review/example.md": "a prompt\n" * 20})
    run_git(repo, "branch", "-f", "design", "main")
    run_git(repo, "checkout", "-q", "design")
    (repo / "docs" / "design").mkdir(parents=True)
    run_git(repo, "mv", "control/review/example.md", "docs/design/example.md")
    run_git(repo, "commit", "-q", "-m", "design: move a prompt")
    run_git(repo, "checkout", "-q", "main")
    assert merge.run_merge(repo, SETTINGS) == 1
    assert "control/review/example.md" in capsys.readouterr().err


@pytest.mark.blocking
def test_c1_f2_a_path_with_spaces_is_named_whole(tmp_path: Path, capsys) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a b.md": "x\n", "control/x y.md": "y\n"})
    assert merge.run_merge(repo, SETTINGS) == 1
    err = capsys.readouterr().err.split("outside the lanes: ")[1]
    assert err.startswith("control/x y.md;")


@pytest.mark.blocking
def test_c1_f3_the_merge_is_pushed_without_another_commit(tmp_path: Path) -> None:
    """A `git merge` fires no post-commit hook, so the run pushes it through `kgme sync`."""
    repo = write_repo(tmp_path)
    bare = tmp_path / "origin.git"
    run_git(tmp_path, "init", "-q", "--bare", "-b", "main", str(bare))
    run_git(repo, "remote", "add", "origin", str(bare))
    run_git(repo, "push", "-q", "-u", "origin", "main")
    write_commit(repo, "design", {"docs/design/pushed.md": "p\n"})
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(bare, "rev-parse", "main") == run_git(repo, "rev-parse", "main")


@pytest.mark.blocking
def test_c1_f4_a_main_commit_during_the_trial_is_retried_and_lands(
    tmp_path: Path, monkeypatch
) -> None:
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    real, calls = merge.run_trial, []

    def run_trial_while_main_moves(*args):
        calls.append(args)
        if len(calls) == 1:
            write_commit(repo, "main", {"notes.txt": "a commit during the trial\n"})
        return real(*args)

    monkeypatch.setattr(merge, "run_trial", run_trial_while_main_moves)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert len(calls) == 2, "a second trial against the moved main"
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""
    assert (repo / "notes.txt").is_file()


@pytest.mark.blocking
def test_c1_f4_a_second_trigger_waits_for_the_holder_instead_of_vanishing(tmp_path: Path) -> None:
    import fcntl
    import os
    import threading

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    lock = merge.read_merge_lock(repo)
    held = os.open(lock, os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(held, fcntl.LOCK_EX)
    threading.Timer(1.0, lambda: os.close(held)).start()  # the holder ends in a second
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""


@pytest.mark.blocking
def test_c1_f5_a_failure_after_the_intent_closes_it(tmp_path: Path, capsys) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    settings = {**SETTINGS, "tracks": {"design": {"check": ["/nonexistent/check"]}}}
    assert merge.run_merge(repo, settings) == 1
    found = read_merge_events(repo)
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["status"] == "error" and "FileNotFoundError" in found[1]["summary"]


@pytest.mark.blocking
def test_c1_f5_an_intent_a_crashed_run_left_open_is_reconciled(tmp_path: Path) -> None:
    from kgme import events

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    dirs = ledger.read_base_dirs(SETTINGS, repo)
    crashed = events.make_event(
        source="kgme", actor="kgme.merge", kind="intent", job="merge",
        key=f"merge:design:{sha}", summary="a run that died",
    )  # fmt: skip
    ledger.append(crashed, dirs)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert ledger.open_intents("merge", dirs) == []
    closing = [e for e in read_merge_events(repo) if e["parent"] == crashed["id"]]
    assert closing and closing[0]["class"] == "transient" and "reconciled" in closing[0]["summary"]


@pytest.mark.blocking
def test_c2_f11_a_check_timeout_is_transient_with_one_outcome(tmp_path: Path, monkeypatch) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    monkeypatch.setattr(merge, "CHECK_TIMEOUT", 0.5)
    settings = {**SETTINGS, "tracks": {"design": {"check": ["sleep", "5"]}}}
    before = run_git(repo, "rev-parse", "main")
    merge.run_merge(repo, settings)
    found = read_merge_events(repo)
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["class"] == "transient" and "TimeoutExpired" in found[1]["summary"]
    assert run_git(repo, "rev-parse", "main") == before


@pytest.mark.blocking
def test_c2_f11_a_git_timeout_is_transient_with_one_outcome(tmp_path: Path, monkeypatch) -> None:
    import subprocess as sp

    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    real = merge.run_git

    def run_git_stalling_on_clone(args, *rest, **more):
        if args[0] == "clone":
            raise sp.TimeoutExpired(["git", *args], 60)
        return real(args, *rest, **more)

    monkeypatch.setattr(merge, "run_git", run_git_stalling_on_clone)
    merge.run_merge(repo, SETTINGS)
    found = read_merge_events(repo)
    assert [e["kind"] for e in found] == ["intent", "outcome"]
    assert found[1]["class"] == "transient" and "TimeoutExpired" in found[1]["summary"]


@pytest.mark.blocking
def test_c2_f5_an_open_intent_whose_commit_already_landed_is_closed_once(tmp_path: Path) -> None:
    """A run that died after its merge and before its outcome: the next run has nothing to
    merge, and still closes the intent, once, as landed."""
    from kgme import events

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.md": "a\n"})
    dirs = ledger.read_base_dirs(SETTINGS, repo)
    died = events.make_event(
        source="kgme", actor="kgme.merge", kind="intent", job="merge",
        key=f"merge:design:{sha}", summary="a run that died after its merge",
    )  # fmt: skip
    ledger.append(died, dirs)
    run_git(repo, "merge", "-q", "--no-ff", "-m", "merged before the crash", sha)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert merge.run_merge(repo, SETTINGS) == 0
    closing = [e for e in read_merge_events(repo) if e["parent"] == died["id"]]
    assert len(closing) == 1 and closing[0]["status"] == "ok" and "on main" in closing[0]["summary"]
    assert ledger.open_intents("merge", dirs) == []


@pytest.mark.blocking
def test_c3_f12_a_branch_kgme_toml_never_governs_a_merge_into_main(tmp_path: Path, capsys) -> None:
    """The CLI reads the main checkout's kgme.toml, whichever checkout starts it."""
    import shutil

    from kgme import cli

    repo = write_repo(tmp_path)
    shutil.copy(ROOT / "kgme.toml", repo / "kgme.toml")  # no [tracks]: the default lanes
    run_git(repo, "add", "kgme.toml")
    run_git(repo, "commit", "-q", "-m", "main's settings")
    run_git(repo, "branch", "-f", "design", "main")
    worktree = tmp_path / "design-worktree"
    run_git(repo, "worktree", "add", "-q", str(worktree), "design")
    wide = read_wide_settings()
    (worktree / "kgme.toml").write_text(wide)  # the branch's own, uncommitted
    (worktree / "control" / "review").mkdir(parents=True)
    (worktree / "control" / "review" / "x.md").write_text("a prompt\n")
    run_git(worktree, "add", "control")
    run_git(worktree, "commit", "-q", "-m", "design: a prompt")
    assert cli.main(["merge", "design", "--base", str(worktree)]) == 1
    assert "control/review/x.md" in capsys.readouterr().err
    assert not (repo / "control" / "review" / "x.md").exists()


@pytest.mark.blocking
def test_c3_f12_the_design_worktree_runs_the_main_checkouts_merge(tmp_path: Path) -> None:
    """The real design path: a design worktree whose own code has no kgme/merge.py, wired to
    the main checkout's hooks by per-worktree config; the applied hook runs the main
    checkout's code, and the commit lands on main (Michou's ask with the applied diffs)."""
    import shutil

    drafted = ROOT / "control" / "git-hooks" / "post-commit"  # the applied hook (Cowork's)
    repo = write_repo(tmp_path)
    run_git(repo, "branch", "-f", "design", "main")  # design predates the code
    shutil.copytree(ROOT / "kgme", repo / "kgme", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("pyproject.toml", "uv.lock", "kgme.toml"):
        shutil.copy(ROOT / name, repo / name)
    (repo / "control" / "git-hooks").mkdir(parents=True)
    shutil.copy(drafted, repo / "control" / "git-hooks" / "post-commit")
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", "main: the code and the hook")
    worktree = tmp_path / "design-worktree"
    run_git(repo, "worktree", "add", "-q", str(worktree), "design")
    assert not (worktree / "kgme" / "merge.py").exists()
    run_git(repo, "config", "extensions.worktreeConfig", "true")
    run_git(worktree, "config", "--worktree", "core.hooksPath", str(repo / "control/git-hooks"))
    (worktree / "docs" / "design").mkdir(parents=True)
    (worktree / "docs" / "design" / "w.svg").write_text("<svg/>\n")
    run_git(worktree, "add", "-A")
    run_git(worktree, "commit", "-q", "-m", "design: w")
    sha = run_git(worktree, "rev-parse", "HEAD")
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        landed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, "main"], cwd=repo, check=False
        )
        if landed.returncode == 0:
            break
        time.sleep(0.5)
    log = worktree / "logs" / "scratch" / "atlas.log"
    assert landed.returncode == 0, log.read_text() if log.exists() else "no hook log"
    # the branch's own kgme.toml widens its lanes to control/: the main checkout's govern (F14)
    (worktree / "kgme.toml").write_text(read_wide_settings())
    (worktree / "control" / "review").mkdir(parents=True)
    (worktree / "control" / "review" / "x.md").write_text("a prompt\n")
    run_git(worktree, "add", "control")
    run_git(worktree, "commit", "-q", "-m", "design: a prompt")
    late = run_git(worktree, "rev-parse", "HEAD")
    deadline = time.monotonic() + 120
    refused = []
    while time.monotonic() < deadline and not refused:
        refused = [
            e for e in read_merge_events(repo)
            if e["kind"] == "outcome" and e["key"] == f"merge:design:{late}"
        ]  # fmt: skip
        time.sleep(0.5)
    assert refused and refused[-1]["status"] == "refused", refused
    assert "control/review/x.md" in refused[-1]["summary"]
    assert not (repo / "control" / "review" / "x.md").exists()


@pytest.mark.blocking
def test_a_head_already_refused_for_its_lanes_is_skipped_without_a_trial(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Cowork's advisory (cycle 3): an out-of-lane design head waits for Michou's hand; each
    later trigger would re-run the trial and write another refusal. It is skipped, silently,
    until the head moves; a dry run still runs the trial."""
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"control/review/x.md": "p\n"})
    assert merge.run_merge(repo, SETTINGS) == 1
    trials = []
    real = merge.run_trial
    monkeypatch.setattr(merge, "run_trial", lambda *a: trials.append(a) or real(*a))
    before = len(read_merge_events(repo))
    assert merge.run_merge(repo, SETTINGS) == 0
    assert "already refused" in capsys.readouterr().out
    assert trials == [] and len(read_merge_events(repo)) == before
    assert merge.run_merge(repo, SETTINGS, dry_run=True) == 1 and len(trials) == 1


@pytest.mark.blocking
def test_c4_f13_a_main_commit_after_the_quiet_check_never_lands_untested(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 4 F13: a commit on main between the quiet check and the landing. The
    untested combination must not land; a fresh trial runs and lands on the new main."""
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    real_checkout, real_trial = merge.read_checkout, merge.run_trial
    raced, trials = [], []

    def read_checkout_then_race(main):
        seen = real_checkout(main)
        if not raced:
            raced.append(write_commit(repo, "main", {"notes.txt": "raced in\n"}))
        return seen

    monkeypatch.setattr(merge, "read_checkout", read_checkout_then_race)
    monkeypatch.setattr(merge, "run_trial", lambda *a: trials.append(a[2]) or real_trial(*a))
    assert merge.run_merge(repo, SETTINGS) == 0
    landed = run_git(repo, "rev-parse", "main")
    first, second = run_git(repo, "log", "-1", "--format=%P", landed).split()
    assert first == raced[0] and second == sha, "the landed merge's first parent is the new main"
    assert trials == [trials[0], raced[0]], "and it was tried on that main"
    assert (repo / "notes.txt").is_file() and (repo / "docs/design/a.svg").is_file()
    assert run_git(repo, "status", "--porcelain") == "", "index and tree match the merge"


@pytest.mark.blocking
def test_c5_f17_an_unfinished_merge_after_the_quiet_check_is_left_alone(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 5 F17: a `--no-commit` merge starts after the outer quiet check, leaving
    HEAD and the index as they were and MERGE_HEAD behind. The landing waits (`transient`)
    and the pending merge is preserved."""
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    run_git(repo, "branch", "side", "main")
    run_git(repo, "checkout", "-q", "side")
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "side: empty")
    run_git(repo, "checkout", "-q", "main")
    before = run_git(repo, "rev-parse", "main")
    real_checkout = merge.read_checkout
    started = []

    def read_checkout_then_start_a_merge(main):
        seen = real_checkout(main)
        if not started:
            started.append(run_git(repo, "merge", "--no-ff", "--no-commit", "side"))
        return seen

    monkeypatch.setattr(merge, "read_checkout", read_checkout_then_start_a_merge)
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "rev-parse", "main") == before, "main untouched"
    assert (repo / ".git" / "MERGE_HEAD").is_file(), "the pending merge is preserved"
    last = read_merge_events(repo)[-1]
    assert last["status"] == "error" and last["class"] == "transient"


@pytest.mark.blocking
def test_c5_f16_a_failure_while_landing_leaves_a_consistent_checkout_and_the_next_run_lands(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 5 F16: the landing fails mid-way (a git timeout). Ref, index, and tree stay
    consistent, the intent is closed, and the next run lands the commit."""
    import subprocess as sp

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    real = merge.run_git

    def run_git_failing_the_landing(args, *rest, **more):
        if "--ff-only" in args:
            raise sp.TimeoutExpired(["git", *args], 60)
        return real(args, *rest, **more)

    monkeypatch.setattr(merge, "run_git", run_git_failing_the_landing)
    before = run_git(repo, "rev-parse", "main")
    merge.run_merge(repo, SETTINGS)
    assert run_git(repo, "rev-parse", "main") == before
    assert run_git(repo, "status", "--porcelain") == "", "index and tree as HEAD"
    # once git is invoked, any failure is blocking with the ref kept (Cowork, cycle 8)
    assert read_merge_events(repo)[-1]["class"] == "blocking"
    assert merge.read_sha(repo, f"{merge.BLOCKED_REFS}{sha[:12]}")
    monkeypatch.setattr(merge, "run_git", real)
    assert merge.run_merge(repo, SETTINGS) == 0, "the checkout is quiet: the latch holds nothing"
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""
    assert run_git(repo, "status", "--porcelain") == ""
    assert run_git(repo, "for-each-ref", merge.BLOCKED_REFS) == "", "the kept ref is cleared"


def run_with_git_hooked(monkeypatch, before_ff) -> None:
    """Effect: `before_ff()` runs just as the landing's `git merge --ff-only` starts, so the
    failure lands inside git's own sequence (the arbiters' ruling on F16 and F18)."""
    real = merge.run_git

    def run_git_hooked(args, *rest, **more):
        if "--ff-only" in args:
            before_ff()
        return real(args, *rest, **more)

    monkeypatch.setattr(merge, "run_git", run_git_hooked)


@pytest.mark.blocking
def test_c6_f16_a_ref_lock_inside_the_landing_is_blocking_named_and_latched(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    before = run_git(repo, "rev-parse", "main")
    lock = repo / ".git" / "refs" / "heads" / "main.lock"
    run_with_git_hooked(monkeypatch, lambda: lock.write_text(""))
    assert merge.run_merge(repo, SETTINGS) == 1
    assert run_git(repo, "rev-parse", "main") == before, "main unmoved"
    last = read_merge_events(repo)[-1]
    assert last["status"] == "error" and last["class"] == "blocking"
    kept = f"{merge.BLOCKED_REFS}{sha[:12]}"
    assert "index" in last["summary"] and kept in last["summary"]
    assert merge.read_sha(repo, kept), "the trial is kept under its own ref"
    count = len(read_merge_events(repo))
    assert merge.run_merge(repo, SETTINGS) == 1, "the next run refuses"
    assert len(read_merge_events(repo)) == count, "and writes nothing"
    assert "refused; a blocked landing is kept" in capsys.readouterr().err
    # Michou's repair, as the outcome names it: the lock gone, the kept trial landed by hand
    lock.unlink()
    run_git(repo, "merge", "--ff-only", "-q", kept)
    assert run_git(repo, "merge-base", "--is-ancestor", sha, "main") == ""
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "status", "--porcelain") == ""


@pytest.mark.blocking
def test_c6_f16_a_stale_ref_lock_is_a_wait_that_touches_nothing(tmp_path: Path) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    (repo / ".git" / "refs" / "heads" / "main.lock").write_text("")
    before = run_git(repo, "rev-parse", "main")
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "rev-parse", "main") == before
    assert run_git(repo, "status", "--porcelain") == ""
    last = read_merge_events(repo)[-1]
    assert last["class"] == "transient" and "main.lock" in last["summary"]


@pytest.mark.blocking
def test_c6_f18_a_branch_switch_inside_the_landing_is_blocking_and_names_the_branch(
    tmp_path: Path, monkeypatch
) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    before = run_git(repo, "rev-parse", "main")
    run_with_git_hooked(monkeypatch, lambda: run_git(repo, "switch", "-q", "-c", "other"))
    assert merge.run_merge(repo, SETTINGS) == 1
    assert run_git(repo, "rev-parse", "main") == before, "main never received it"
    found = read_merge_events(repo)
    assert not [e for e in found if e["status"] == "ok"], "no false ok"
    assert found[-1]["class"] == "blocking" and "other" in found[-1]["summary"]
    count = len(found)
    assert merge.run_merge(repo, SETTINGS) == 1 and len(read_merge_events(repo)) == count


@pytest.mark.blocking
def test_c7_f16_a_timeout_after_a_partial_landing_is_blocking_and_keeps_the_trial(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 7 F16: git installs the trial's index, then the landing times out. The
    post-checks run after the exception too: one blocking outcome, the trial kept."""
    import subprocess as sp

    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    before = run_git(repo, "rev-parse", "main")
    real = merge.run_git
    lock = repo / ".git" / "refs" / "heads" / "main.lock"

    def run_git_landing_partly_then_timing_out(args, *rest, **more):
        if "--ff-only" in args:
            lock.write_text("")
            real(args, *rest, **more)  # git stages the trial's tree, then fails on the lock
            raise sp.TimeoutExpired(["git", *args], 60)
        return real(args, *rest, **more)

    monkeypatch.setattr(merge, "run_git", run_git_landing_partly_then_timing_out)
    assert merge.run_merge(repo, SETTINGS) == 1
    assert run_git(repo, "rev-parse", "main") == before
    closing = [e for e in read_merge_events(repo) if e["kind"] == "outcome"]
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    assert run_git(repo, "for-each-ref", "--format=%(refname)", merge.BLOCKED_REFS)


@pytest.mark.blocking
def test_c7_f19_a_dry_run_and_a_new_design_head_leave_the_kept_trial_alone(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = write_repo(tmp_path)
    write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    lock = repo / ".git" / "refs" / "heads" / "main.lock"
    run_with_git_hooked(monkeypatch, lambda: lock.write_text(""))
    assert merge.run_merge(repo, SETTINGS) == 1
    kept = run_git(repo, "for-each-ref", "--format=%(refname) %(objectname)", merge.BLOCKED_REFS)
    assert kept, "a blocked landing is kept under its own ref"
    merge.run_merge(repo, SETTINGS, dry_run=True)
    write_commit(repo, "design", {"docs/design/b.svg": "<svg/>\n"})
    count = len(read_merge_events(repo))
    assert merge.run_merge(repo, SETTINGS) == 1, "a new design head is refused too"
    assert len(read_merge_events(repo)) == count
    assert (
        run_git(repo, "for-each-ref", "--format=%(refname) %(objectname)", merge.BLOCKED_REFS)
        == kept
    ), "the kept trial is unchanged"
    # the repair the outcome names lands it; the kept ref is cleared once it is on main
    lock.unlink()
    run_git(repo, "merge", "--ff-only", "-q", kept.split()[0])
    monkeypatch.undo()
    assert merge.run_merge(repo, SETTINGS) == 0
    assert run_git(repo, "for-each-ref", "--format=%(refname)", merge.BLOCKED_REFS) == ""
    assert (repo / "docs" / "design" / "b.svg").is_file(), "and the newer head landed"


@pytest.mark.blocking
def test_c8_f16_a_partial_landing_whose_post_check_fails_is_blocking_with_the_ref_kept(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 8 F16, Cowork's fallback: once git is invoked on the main checkout, any
    failure, here the post-check itself, is one blocking outcome with the kept ref."""
    import subprocess as sp

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    lock = repo / ".git" / "refs" / "heads" / "main.lock"
    run_with_git_hooked(monkeypatch, lambda: lock.write_text(""))

    def read_landed_state_timing_out(main):
        raise sp.TimeoutExpired(["git", "symbolic-ref"], 60)

    monkeypatch.setattr(merge, "read_landed_state", read_landed_state_timing_out)
    assert merge.run_merge(repo, SETTINGS) == 1
    closing = [e for e in read_merge_events(repo) if e["kind"] == "outcome"]
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    kept = f"{merge.BLOCKED_REFS}{sha[:12]}"
    assert merge.read_sha(repo, kept), "the recovery ref is intact"
    assert kept in closing[0]["summary"]


@pytest.mark.blocking
def test_c9_f16_a_failed_diagnostic_after_a_wrong_branch_landing_is_still_blocking(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 9 F16: every effect after git is invoked sits inside the blocking
    boundary, the diagnostic reads included."""
    import subprocess as sp

    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    run_with_git_hooked(monkeypatch, lambda: run_git(repo, "switch", "-q", "-c", "other"))
    real_sha, invoked = merge.read_sha, []
    real_landed = merge.read_landed_state

    def read_landed_state_marking(main):
        invoked.append(True)
        return real_landed(main)

    def read_sha_failing_after_the_landing(main, ref):
        if invoked and ref == "other":  # the diagnostic: which commit the switched branch got
            raise sp.TimeoutExpired(["git", "rev-parse", ref], 60)
        return real_sha(main, ref)

    monkeypatch.setattr(merge, "read_landed_state", read_landed_state_marking)
    monkeypatch.setattr(merge, "read_sha", read_sha_failing_after_the_landing)
    synced = []
    monkeypatch.setattr("kgme.sync_io.run_sync", lambda *a: synced.append(a))
    assert merge.run_merge(repo, SETTINGS) == 1
    closing = [e for e in read_merge_events(repo) if e["kind"] == "outcome"]
    kept = f"{merge.BLOCKED_REFS}{sha[:12]}"
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    assert kept in closing[0]["summary"] and synced == []
    monkeypatch.setattr(merge, "read_sha", real_sha)
    assert merge.read_sha(repo, kept), "the recovery ref is intact"


@pytest.mark.blocking
def test_c10_git_output_that_is_not_utf8_after_the_landing_is_blocking(
    tmp_path: Path, monkeypatch
) -> None:
    """Cowork's ruling at cycle 10: `run_git` decodes git's output as text, so output that is
    not UTF-8 raises `UnicodeDecodeError`, a `ValueError`; after git has started on the
    checkout it is one blocking outcome, the kept ref intact, no sync."""
    repo = write_repo(tmp_path)
    sha = write_commit(repo, "design", {"docs/design/a.svg": "<svg/>\n"})
    real = merge.run_git

    def run_git_landing_then_undecodable(args, *rest, **more):
        done = real(args, *rest, **more)
        if "--ff-only" in args:
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
        return done

    monkeypatch.setattr(merge, "run_git", run_git_landing_then_undecodable)
    synced = []
    monkeypatch.setattr("kgme.sync_io.run_sync", lambda *a: synced.append(a))
    assert merge.run_merge(repo, SETTINGS) == 1
    closing = [e for e in read_merge_events(repo) if e["kind"] == "outcome"]
    kept = f"{merge.BLOCKED_REFS}{sha[:12]}"
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    assert kept in closing[0]["summary"] and synced == []
    monkeypatch.setattr(merge, "run_git", real)
    assert merge.read_sha(repo, kept), "the recovery ref is intact"
