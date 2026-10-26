"""Tests for what `kgme lint` reads by default (HANDOFF-0042; moved out of `tests/test_lint.py`
by HANDOFF-0060 §3, unchanged).

Purpose: the default lints the commit and counts the untracked files it skips; the command
line counts them and `--all` reports them.
Inputs: git repositories under `tmp_path`.
Outputs: pytest assertions.
Side effects: git repositories under `tmp_path`.
"""

from pathlib import Path

import pytest
from linttools import note
from test_lint_tracks import TRACK, record

from kgme import cli, lint, vault


def write_repo(tmp_path: Path) -> Path:
    """Effect: a git repository with the lint roots, one valid committed note, and the
    planted cases of HANDOFF-0042's acceptance test staged or left untracked."""
    import subprocess

    repo = tmp_path / "repo"
    for rel, text in {
        "memory/notes/kept.md": note(),
        "docs/handoff/stray/planted.md": record("handoff", "HANDOFF-0098"),
        "docs/handoff/cockpit-design/wrong-prefix.md": record("handoff", "HANDOFF-0097"),
    }.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]
    subprocess.run([*git, "init", "-q"], cwd=repo, check=True)
    subprocess.run([*git, "add", "-A"], cwd=repo, check=True)
    (repo / "docs" / "untracked.md").write_text("no frontmatter here\n")
    return repo


@pytest.mark.blocking
def test_the_default_lints_the_commit_and_counts_the_untracked_it_skips(tmp_path: Path) -> None:
    """HANDOFF-0042 §2: staged files are the commit's and are linted; an untracked file is
    skipped and counted; `--all` walks it."""
    repo = write_repo(tmp_path)
    roots, exempt = [repo / "memory", repo / "docs"], [repo / "memory" / "templates"]
    notes, skipped = vault.read_commit_notes(roots, exempt, (), repo)
    assert skipped == 1 and "docs/untracked.md" not in [rel for rel, _ in notes]
    found = [(f.path, f.rule) for f in lint.lint_files(notes, (TRACK,)) if f.cls == "blocking"]
    assert ("docs/handoff/stray/planted.md", "track-folder") in found
    assert ("docs/handoff/cockpit-design/wrong-prefix.md", "track-id") in found
    walked = vault.read_notes(roots, exempt, (), repo)
    assert "docs/untracked.md" in [rel for rel, _ in walked]
    outside, none_skipped = vault.read_commit_notes([tmp_path / "repo" / "docs"], [], (), tmp_path)
    assert none_skipped == 0 and len(outside) == 3, "no index outside a work tree: the walk"


@pytest.mark.blocking
def test_the_cli_counts_the_untracked_and_all_reports_it(tmp_path: Path, capsys) -> None:
    import subprocess

    repo = tmp_path / "repo"
    (repo / "memory" / "notes").mkdir(parents=True)
    (repo / "memory" / "notes" / "kept.md").write_text(note())
    (repo / "docs").mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    (repo / "docs" / "untracked.md").write_text("no frontmatter here\n")
    assert cli.main(["lint", "--base", str(repo)]) == 0
    last = capsys.readouterr().out.splitlines()[-1]
    assert "1 untracked skipped; `--all` walks them" in last, last
    assert cli.main(["lint", "--base", str(repo), "--all"]) == 1
    out = capsys.readouterr().out
    assert "docs/untracked.md: frontmatter [blocking]" in out and "untracked skipped" not in out
