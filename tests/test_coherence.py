"""Tests for the coherence checks of `kgme lint` and the handoff folders (HANDOFF-0049).

Purpose: each check in `kgme/coherence.py` finds what it should and nothing else: a handoff
in the wrong folder for its status, a finished handoff without an existing report, a
backticked repository path that resolves nowhere (with the `Outputs` of open and proposed
handoffs and the absent-by-design paths excused), a map folder that neither exists nor is
marked later. On the real tree, nothing outside the open handoffs is incoherent, every
finished handoff's report exists, and `kgme review` still finds HANDOFF-0034 under `done/`.
Inputs: literal fixtures; the repository's own tree for the last tests.
Outputs: pytest assertions.
Side effects: reads the repository's files and runs `git ls-files` and `git ls-tree` on it;
the HANDOFF-0054 tests also create repositories under `tmp_path`, commit fixtures there,
clone this repository there with no hard links, stage into the clone what this checkout has
staged, and fetch its design ref. Nothing in this repository is written.

The Tier 1 path is assembled at run time: the live guard scans the text of a test file named
on a command line, and refuses the run for the literal (lesson of 2026-09-15).
"""

import datetime
from pathlib import Path

import pytest

from kgme import coherence, config, paths, review_io, vault

ROOT = paths.root()
TIER1 = "memory/" + "private"


COMPLETED = "coherence-completed"  # advisory by design, HANDOFF-0060 §4


def rules(found) -> list[tuple[str, str]]:
    return [(f.path, f.rule) for f in found]


@pytest.mark.advisory
def test_a_handoff_must_sit_in_the_folder_its_status_names() -> None:
    handoffs = [
        ("docs/handoff/a.md", {"status": "open"}, ""),
        ("docs/handoff/b.md", {"status": "done", "report": "docs/audit/r.md"}, ""),
        ("docs/handoff/done/c.md", {"status": "done", "report": "docs/audit/r.md"}, ""),
        ("docs/handoff/proposed/d.md", {"status": "proposed"}, ""),
        ("docs/handoff/archive/e.md", {"status": "superseded"}, ""),
        ("docs/handoff/archive/f.md", {"status": "open"}, ""),
        ("docs/handoff/proposed/track/g.md", {"status": "open"}, ""),
    ]
    found = coherence.check_handoffs(handoffs, frozenset({"docs/audit/r.md"}))
    assert rules(found) == [
        ("docs/handoff/b.md", "coherence-folder"),
        ("docs/handoff/archive/f.md", "coherence-folder"),
    ], "a design track's own folder is not judged by these four"
    assert all(f.cls == "advisory" for f in found)


@pytest.mark.advisory
def test_a_finished_handoff_names_a_report_that_exists() -> None:
    handoffs = [
        ("docs/handoff/done/a.md", {"status": "done"}, ""),
        ("docs/handoff/done/b.md", {"status": "done", "report": "docs/audit/gone.md"}, ""),
        ("docs/handoff/done/c.md", {"status": "done", "report": "docs/audit/here.md"}, ""),
    ]
    found = coherence.check_handoffs(handoffs, frozenset({"docs/audit/here.md"}))
    assert rules(found) == [
        ("docs/handoff/done/a.md", "coherence-report"),
        ("docs/handoff/done/b.md", "coherence-report"),
    ]


@pytest.mark.advisory
def test_backticked_paths_resolve_unless_promised_or_absent_by_design() -> None:
    text = (
        f"Read `docs/STATUS.md`, `kgme/gone.py`, `kgme/later.py`, `{TIER1}/x.md`, "
        "`docs/adr/ADR-NNN-*.md`, `~/.zshrc`, `make check`, `kgme/lint.py:42`, `control/`."
    )
    handoffs = [
        ("docs/handoff/proposed/p.md", {"status": "proposed"}, "## Outputs\n`kgme/later.py`\n"),
        ("docs/handoff/done/q.md", {"status": "done"}, "## Outputs\n`kgme/gone.py`\n"),
    ]
    existing = frozenset({"docs", "kgme", "memory", "control", "docs/STATUS.md", "kgme/lint.py"})
    declared = frozenset({"docs", "kgme", "memory", "control"})
    found = coherence.check_paths(
        [("README.md", text)],
        existing,
        coherence.excused_paths(handoffs),
        declared=declared,
    )
    assert [f.message for f in found] == ["`kgme/gone.py` does not resolve"], (
        "a finished handoff's outputs excuse nothing"
    )


@pytest.mark.advisory
def test_each_map_folder_exists_or_is_marked_later() -> None:
    claude = (
        "## Repository map\n\n```\nkgme/   the package\nrouter/   llm.py (later)\n"
        "ghost/   nothing\n  nested/   ignored\n```\n"
    )
    found = coherence.check_map(claude, frozenset({"kgme"}))
    assert [f.message for f in found] == [
        "map lists `ghost/`, which neither exists nor is marked later"
    ]


@pytest.mark.advisory
def test_the_whole_tree_is_coherent() -> None:
    """Review cycle 1 F6: the full scope, open handoffs included, with no exclusion."""
    found = coherence.check_tree(*vault.read_coherence_inputs(ROOT))
    assert [f.line() for f in found if f.rule != COMPLETED] == []
    # `completed:` against the PASS review is advisory by design: history differs (HANDOFF-0060 §4)
    assert {f.cls for f in found if f.rule == COMPLETED} <= {"advisory"}


@pytest.mark.advisory
def test_every_finished_handoff_report_exists_on_the_real_tree() -> None:
    finished = sorted((ROOT / "docs" / "handoff" / "done").glob("*.md"))
    assert len(finished) >= 27
    reports = {
        rel: data.get("report")
        for rel, data, _ in vault.read_handoffs(ROOT)
        if rel.startswith("docs/handoff/done/")
    }
    assert len(reports) == len(finished)
    assert [rel for rel, report in reports.items() if not (ROOT / str(report)).is_file()] == []


@pytest.mark.blocking
def test_review_finds_a_handoff_by_id_wherever_it_sits(tmp_path: Path) -> None:
    assert review_io.read_handoff_path(ROOT / "docs" / "handoff", "HANDOFF-0034") == (
        ROOT / "docs" / "handoff" / "done" / "2026-09-14-kgme-brief-v1.md"
    )
    for folder in ("proposed", "archive"):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "x.md").write_text("---\nid: HANDOFF-9999\n---\n")
    assert review_io.read_handoff_path(tmp_path, "HANDOFF-9999") is None


# Review cycle 1 of HANDOFF-0049 (AUDIT-0055)


@pytest.mark.blocking
def test_the_local_tree_does_not_borrow_the_design_branch() -> None:
    """F3: a path that exists only on `design` is not present in this checkout."""
    only_on_design = "tools/git-hooks/post-commit"
    assert not (ROOT / only_on_design).exists()
    assert only_on_design not in vault.read_existing_paths(ROOT)


@pytest.mark.blocking
@pytest.mark.parametrize(
    "token", [".claude/settings.json", "uv.lock", "tools/hooks/pre_tool_guard.sh", "router/llm.py"]
)
def test_any_repository_path_is_recognised_and_checked(token: str) -> None:
    """F4: hidden paths, root files, and obsolete roots are paths too."""
    assert coherence.repository_path(token) == token
    declared = frozenset({"router"})
    found = coherence.check_paths(
        [("README.md", f"see `{token}`")], frozenset(), frozenset(), declared=declared
    )
    assert [f.message for f in found] == [f"`{token}` does not resolve"]


@pytest.mark.blocking
def test_coherence_findings_are_advisory_the_day_before_the_configured_date() -> None:
    """F5 (Cowork's ruling): the date lives in `kgme.toml` `[coherence] blocking_from`."""
    start = config.read_config()["coherence"]["blocking_from"]
    day_before = datetime.date.fromisoformat(start) - datetime.timedelta(days=1)
    assert coherence.finding_class(day_before, start) == "advisory"


@pytest.mark.blocking
def test_coherence_findings_are_blocking_from_the_configured_date() -> None:
    start = config.read_config()["coherence"]["blocking_from"]
    assert start == "2026-10-23"
    assert coherence.finding_class(datetime.date.fromisoformat(start), start) == "blocking"
    handoffs = [("docs/handoff/x.md", {"status": "done"}, "")]
    late = coherence.check_tree(handoffs, [], frozenset(), "", cls="blocking")
    assert late and all(f.cls == "blocking" for f in late)


# The arbiter's ruling on HANDOFF-0049 review cycle 2 F4: recognition by declared root

MAP = (
    "## Repository map\n\n```\nREADME.md   the front door\ndocs/   the documents\n"
    "  handoff/   open handoffs\n    done/   finished\nkgme/   the package\n"
    "router/   llm.py (later)\n```\n"
)


def path_findings(document: str, text: str, existing: set[str]) -> list[str]:
    found = coherence.check_tree([], [(document, text)], frozenset(existing), MAP)
    return [f.message for f in found if f.rule == "coherence-path"]


@pytest.mark.blocking
def test_a_retired_root_named_alone_is_checked() -> None:
    assert path_findings("README.md", "see `tools/`", {"docs", "kgme"}) == [
        "`tools` does not resolve"
    ]


@pytest.mark.blocking
@pytest.mark.parametrize("existing", [{"docs", "docs/handoff"}, {"docs"}])
def test_a_document_relative_folder_is_checked_when_it_is_gone(existing: set[str]) -> None:
    assert path_findings("docs/README.md", "see `handoff/done/`", existing) == [
        "`handoff/done` does not resolve"
    ]


@pytest.mark.blocking
def test_a_hidden_root_is_checked_even_when_it_is_gone() -> None:
    assert path_findings("README.md", "see `.claude/settings.json`", {"docs"}) == [
        "`.claude/settings.json` does not resolve"
    ]


@pytest.mark.blocking
def test_names_outside_the_declared_roots_are_not_this_repositorys() -> None:
    external = (
        "`michaelhgrigorian22-ctrl/kgme`, `mattpocock/skills`, `Active/MODELING_CONVENTIONS_V2.md`"
    )
    assert path_findings("README.md", external, {"docs", "kgme"}) == []
    assert path_findings("docs/readers/obsidian.md", "`templates/daily`", {"docs"}) == []


# HANDOFF-0054: the check resolves against the commit, not the machine


def run_git(repo: Path, *argv: str) -> None:
    """Effect: one git command in `repo`, quiet, with a fixed identity."""
    import subprocess

    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True,
    )  # fmt: skip


def read_git(repo: Path, *argv: str) -> bytes:
    """Effect: one git command's output in `repo`."""
    import subprocess

    return subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True).stdout


def write_staged_into(clone: Path) -> None:
    """Effect: what this checkout has staged, blob by blob from its index, staged in `clone`,
    so the clone holds what the next commit will: nothing outside git enters."""
    added = read_git(
        ROOT, "diff", "--cached", "--no-renames", "--name-only", "-z", "--diff-filter=ACM"
    )
    gone = read_git(
        ROOT, "diff", "--cached", "--no-renames", "--name-only", "-z", "--diff-filter=D"
    )
    for name in filter(None, added.decode().split("\0")):
        target = clone / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(read_git(ROOT, "show", f":{name}"))
        run_git(clone, "add", "--", name)
    for name in filter(None, gone.decode().split("\0")):
        run_git(clone, "rm", "-q", "--", name)


@pytest.mark.blocking
def test_the_whole_tree_is_coherent_in_a_fresh_clone(tmp_path: Path) -> None:
    """The red command of HANDOFF-0054, in-process: the committed tree and the staged change,
    cloned with no hard links, hold none of the paths this machine's runs created."""
    clone = tmp_path / "clone"
    run_git(tmp_path, "clone", "-q", "--no-hardlinks", str(ROOT), str(clone))
    write_staged_into(clone)
    for ref in vault.DESIGN_REFS:  # a clone of a clone has no `origin/design` of its own
        if read_git(ROOT, "branch", "-a", "--list", ref, f"remotes/{ref}").strip():
            run_git(clone, "fetch", "-q", str(ROOT), f"+{ref}:refs/remotes/origin/design")
            break
    found = coherence.check_tree(*vault.read_coherence_inputs(clone))
    assert [f.line() for f in found if f.rule != COMPLETED] == []


@pytest.mark.blocking
def test_a_path_under_a_clean_target_resolves_with_its_root_absent() -> None:
    text = (
        "Read `logs/scratch/review.patch`, `logs/trace`, `kgme/__pycache__/x.pyc`, "
        "and `logs/gone.md`."
    )
    found = coherence.check_paths(
        [("docs/readers/x.md", text)],
        frozenset({"docs", "kgme", "logs"}),
        frozenset(),
        declared=frozenset({"docs", "kgme", "logs"}),
        regenerable=("logs/scratch", "logs/trace", "**/__pycache__"),
    )
    assert [f.message for f in found] == ["`logs/gone.md` does not resolve"]


@pytest.mark.blocking
def test_existing_paths_are_the_index_not_the_working_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    run_git(repo, "init", "-q", "-b", "main")
    (repo / "docs" / "tracked.md").write_text("x\n")
    run_git(repo, "add", "docs/tracked.md")
    run_git(repo, "commit", "-q", "-m", "one")
    (repo / "docs" / "staged.md").write_text("x\n")
    run_git(repo, "add", "docs/staged.md")
    (repo / "docs" / "untracked.md").write_text("x\n")
    (repo / "attachments").mkdir()
    (repo / "attachments" / ".DS_Store").write_text("x")
    existing = vault.read_existing_paths(repo)
    assert {"docs", "docs/tracked.md", "docs/staged.md"} <= existing
    assert "docs/untracked.md" not in existing, "a file only this machine has does not resolve"
    assert "attachments" not in existing, "a folder that holds no tracked file does not resolve"


@pytest.mark.blocking
def test_the_design_paths_fall_back_to_the_remote_branch(tmp_path: Path) -> None:
    origin = tmp_path / "origin"
    origin.mkdir()
    run_git(origin, "init", "-q", "-b", "main")
    (origin / "a.md").write_text("x\n")
    run_git(origin, "add", "a.md")
    run_git(origin, "commit", "-q", "-m", "main")
    run_git(origin, "checkout", "-q", "-b", "design")
    (origin / "docs" / "design").mkdir(parents=True)
    (origin / "docs" / "design" / "only-here.md").write_text("x\n")
    run_git(origin, "add", "docs")
    run_git(origin, "commit", "-q", "-m", "design")
    run_git(origin, "checkout", "-q", "main")
    clone = tmp_path / "clone"
    run_git(tmp_path, "clone", "-q", str(origin), str(clone))
    assert "docs/design/only-here.md" in vault.read_design_paths(clone)


# Review cycle 1 of HANDOFF-0054 (AUDIT-0070)


@pytest.mark.blocking
def test_c1_f1_a_document_relative_path_under_a_clean_target_resolves() -> None:
    text = "See `generated/result.md` and `handwritten/note.md`."
    found = coherence.check_paths(
        [("docs/README.md", text)],
        frozenset({"docs", "docs/generated", "docs/handwritten"}),
        frozenset(),
        declared=frozenset({"docs", "docs/generated", "docs/handwritten"}),
        regenerable=("docs/generated",),
    )
    assert [f.message for f in found] == ["`handwritten/note.md` does not resolve"]
