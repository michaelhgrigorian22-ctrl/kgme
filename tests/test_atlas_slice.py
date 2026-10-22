"""Tests for atlas slices (HANDOFF-0056).

Purpose: the acceptance test. On a temporary clone of this repository: a slice of
HANDOFF-0047 names `kgme/session.py`, the tests that import it, and its importers, within the
default budget, names nothing under `memory/` or `logs/`, and is byte-identical on a second
run; `--budget 500` truncates and says what was cut; `--around kgme/ledger.py` lists its
importers and tests; a worktree on another branch gets its own tree's slice; a tree that is
not a checkout (the cheap lane's shape) builds, and a Tier 1 root inside it is dropped.
Inputs: `tmp_path`; this repository's committed tree, cloned.
Outputs: pytest assertions.
Side effects: clones, worktrees, and files under `tmp_path`.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from kgme import atlas, atlas_read, atlas_slice, cli, config, paths

ROOT = paths.root()
SETTINGS = config.read_config()


def run_git(repo: Path, *argv: str) -> str:
    """Effect: one git command in `repo`, with a fixed identity; its stdout."""
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True, text=True,
    )  # fmt: skip
    return done.stdout.strip()


@pytest.fixture(scope="module")
def clone(tmp_path_factory) -> Path:
    """Effect: a clone of this repository's committed tree."""
    where = tmp_path_factory.mktemp("slice") / "clone"
    subprocess.run(["git", "clone", "-q", "--shared", str(ROOT), str(where)], check=True)
    return where


def read_text(base: Path, handoff=None, around=(), budget=None) -> str:
    """Effect: a slice's text, as `kgme atlas --slice/--around` prints it."""
    return atlas_read.read_slice(base, SETTINGS, handoff, list(around), budget).text


def read_seed_list(text: str, path: str, title: str) -> list[str]:
    """Pure: one list of a seed's block, as paths."""
    block = text.split(f"## {path} (seed)\n", 1)[1].split("\n## ", 1)[0]
    line = next(ln for ln in block.splitlines() if ln.startswith(f"{title}: "))
    return [p.strip() for p in line.split(": ", 1)[1].split(",")]


def read_paths(text: str) -> list[str]:
    """Pure: every path a slice's headings and lists name."""
    found = []
    for line in text.splitlines():
        if line.startswith("## "):
            found.append(line[3:].rsplit(" (", 1)[0])
        elif ": " in line and not line.startswith(("Code", "Tests", "Reader", "Decision")):
            found += [p.strip() for p in line.split(": ", 1)[1].split(",")]
    return found


@pytest.mark.blocking
def test_a_handoff_slice_names_its_files_tests_and_importers(clone: Path) -> None:
    text = read_text(clone, "HANDOFF-0047")
    block = text.split("## kgme/session.py (seed)\n", 1)[1].split("\n## ", 1)[0]
    assert "tests/test_session.py" in block.split("tests: ", 1)[1].splitlines()[0]
    assert "kgme/cli.py" in block.split("imported by: ", 1)[1].splitlines()[0]
    assert atlas_slice.estimate(text) <= atlas_read.SLICE_BUDGET


@pytest.mark.blocking
def test_a_slice_names_nothing_under_memory_or_logs(clone: Path) -> None:
    for text in (read_text(clone, "HANDOFF-0047"), read_text(clone, around=["kgme/ledger.py"])):
        named = read_paths(text)
        assert named and not [p for p in named if p.startswith(("memory/", "logs/"))], named


@pytest.mark.blocking
def test_a_slice_is_deterministic(clone: Path, capsys) -> None:
    assert cli.main(["atlas", "--slice", "HANDOFF-0047", "--base", str(clone)]) == 0
    first = capsys.readouterr().out
    assert cli.main(["atlas", "--slice", "HANDOFF-0047", "--base", str(clone)]) == 0
    assert capsys.readouterr().out == first


@pytest.mark.blocking
def test_a_small_budget_truncates_and_names_what_was_cut(clone: Path) -> None:
    text = read_text(clone, "HANDOFF-0047", budget=500)
    assert atlas_slice.estimate(text) <= 500
    assert text.rstrip().splitlines()[-1].startswith("Cut at the budget of 500 tokens: ")


@pytest.mark.blocking
def test_around_a_module_lists_its_importers_and_tests(clone: Path) -> None:
    text = read_text(clone, around=["kgme/ledger.py"])
    assert "kgme/hooks/common.py" in read_seed_list(text, "kgme/ledger.py", "imported by")
    assert "tests/test_ledger_concurrency.py" in read_seed_list(text, "kgme/ledger.py", "tests")


@pytest.mark.blocking
def test_a_worktree_on_another_branch_gets_its_own_trees_slice(clone: Path, tmp_path) -> None:
    other = tmp_path / "other"
    run_git(clone, "worktree", "add", "-q", "-b", "slice-branch", str(other))
    (other / "kgme" / "only_here.py").write_text(
        '"""Only on this branch."""\nfrom kgme import ledger\n'
    )
    run_git(other, "add", "kgme/only_here.py")
    run_git(other, "commit", "-q", "-m", "a module only on this branch")
    mine = read_seed_list(
        read_text(other, around=["kgme/ledger.py"]), "kgme/ledger.py", "imported by"
    )
    main = read_seed_list(
        read_text(clone, around=["kgme/ledger.py"]), "kgme/ledger.py", "imported by"
    )
    assert "kgme/only_here.py" in mine and "kgme/only_here.py" not in main


@pytest.mark.blocking
def test_a_tree_that_is_not_a_checkout_builds_and_drops_a_tier1_root(tmp_path: Path) -> None:
    export = tmp_path / "export"
    for rel in ("kgme/ledger.py", "kgme/events.py", "tests/test_ledger_concurrency.py"):
        (export / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, export / rel)
    # inside a folder the atlas reads, where it would otherwise be named
    (export / "kgme" / "secret").mkdir()
    (export / "kgme" / "secret" / "notes.py").write_text("from kgme import ledger\n")
    tier1 = [str(export / "kgme" / "secret")]
    settings = {**SETTINGS, "paths": {**SETTINGS["paths"], "tier1_paths": tier1}}
    text = atlas_read.read_slice(export, settings, None, ["kgme/ledger.py"], None).text
    named = read_paths(text)
    assert "kgme/ledger.py" in named and "tests/test_ledger_concurrency.py" in named
    assert not [p for p in named if p.startswith(("kgme/secret/", "memory/", "logs/"))], named
    plain = atlas_read.read_slice(export, SETTINGS, None, ["kgme/ledger.py"], None).text
    assert "kgme/secret/notes.py" in plain, "without the Tier 1 root, the file is named"


@pytest.mark.blocking
def test_an_unknown_handoff_is_refused(clone: Path, capsys) -> None:
    assert cli.main(["atlas", "--slice", "HANDOFF-9999", "--base", str(clone)]) == 2
    assert "HANDOFF-9999 is not a handoff" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_pure_half_ranks_seeds_then_neighbours_and_filters() -> None:
    nodes = {
        "kgme.a": atlas.Node("kgme.a", "module", "Code: `kgme/a.py`.", "kgme/a.py", {"kgme.b"}),
        "kgme.b": atlas.Node("kgme.b", "module", "Code: `kgme/b.py`.", "kgme/b.py"),
        "kgme.c": atlas.Node("kgme.c", "module", "Code: `kgme/c.py`.", "kgme/c.py", {"kgme.a"}),
        "tests.test_a": atlas.Node("tests.test_a", "test", "Tests.", "tests/test_a.py", {"kgme.a"}),
        "logs.x": atlas.Node("logs.x", "module", "Code.", "logs/x.py", {"kgme.a"}),
    }
    nodes["kgme.a"].links.add("tests.test_a")
    entries = atlas_slice.build_slice(nodes, ["kgme.a"], atlas_slice.EXCLUDED)
    assert [(e.rank, e.path) for e in entries] == [
        ("seed", "kgme/a.py"), ("test", "tests/test_a.py"), ("importer", "kgme/c.py"),
        ("import", "kgme/b.py"),
    ]  # fmt: skip
    assert all("logs/" not in e.block for e in entries)


@pytest.mark.blocking
def test_c1_f1_excluded_files_are_never_opened_and_a_base_in_tier1_is_refused(
    tmp_path: Path, monkeypatch
) -> None:
    from kgme import clean_fs

    export = tmp_path / "export"
    (export / "kgme" / "secret").mkdir(parents=True)
    (export / "memory").mkdir()
    shutil.copy(ROOT / "kgme/ledger.py", export / "kgme/ledger.py")
    (export / "kgme" / "secret" / "notes.py").write_text("from kgme import ledger\n")
    (export / "memory" / "note.md").write_text("private\n")
    tier1 = [str(export / "kgme" / "secret")]
    settings = {**SETTINGS, "paths": {**SETTINGS["paths"], "tier1_paths": tier1}}
    opened = []
    real = clean_fs.read_regular_bytes
    monkeypatch.setattr(
        clean_fs, "read_regular_bytes", lambda base, path: opened.append(path) or real(base, path)
    )
    atlas_read.read_slice(export, settings, None, ["kgme/ledger.py"], None)
    assert opened and not [p for p in opened if "secret" in str(p) or "memory" in str(p)], opened
    for inside in (export / "kgme" / "secret", export / "kgme" / "secret" / "deeper"):
        inside.mkdir(exist_ok=True)
        with pytest.raises(ValueError, match="Tier 1"):
            atlas_read.read_slice(inside, settings, None, ["x.py"], None)


@pytest.mark.blocking
def test_c1_f2_the_title_never_names_an_excluded_path(clone: Path) -> None:
    text = read_text(clone, around=["memory/example.md", "kgme/ledger.py"])
    assert "memory/" not in text and "logs/" not in text
    assert text.startswith("# Atlas slice: kgme/ledger.py\n")


@pytest.mark.blocking
def test_c1_f3_a_tests_dependencies_are_imports_not_importers(clone: Path) -> None:
    text = read_text(clone, around=["tests/test_ledger_concurrency.py"])
    block = text.split("## tests/test_ledger_concurrency.py (seed)\n", 1)[1].split("\n## ", 1)[0]
    assert "imported by:" not in block, block
    assert "kgme/ledger.py" in read_seed_list(text, "tests/test_ledger_concurrency.py", "imports")
    assert "## kgme/ledger.py (import)" in text


@pytest.mark.blocking
def test_c1_f4_documents_naming_a_file_anywhere_reach_its_slice() -> None:
    sources = [
        atlas.Source("kgme/review.py", '"""Review."""\n'),
        atlas.Source(
            "docs/adr/ADR-0X1-x.md",
            "---\nid: ADR-001\n---\n\nThe loop lives in `kgme/review.py`.\n",
        ),
        atlas.Source(
            "docs/handoff/h.md",
            "---\nid: HANDOFF-0001\nstatus: open\n---\n\n## Why\nSee `kgme/review.py`.\n\n"
            "## Outputs\n`kgme/other.py`\n",
        ),
    ]
    nodes = atlas.build_graph(sources, [], [s.path for s in sources])
    edges = atlas_slice.read_edges(sources, nodes)
    entries = atlas_slice.build_slice(nodes, ["kgme.review"], atlas_slice.EXCLUDED, edges)
    named = [(e.rank, e.path) for e in entries if e.rank == "document"]
    assert ("document", "docs/adr/ADR-0X1-x.md") in named
    assert ("document", "docs/handoff/h.md") in named


@pytest.mark.blocking
@pytest.mark.parametrize("budget", [0, -5, 1, 20])
def test_c1_f5_a_budget_too_small_or_not_positive_is_refused(clone: Path, budget: int) -> None:
    with pytest.raises(ValueError, match="budget"):
        read_text(clone, "HANDOFF-0047", budget=budget)


@pytest.mark.blocking
def test_c1_f5_the_whole_text_fits_the_budget(clone: Path) -> None:
    for budget in (60, 120, 500, 3000):
        text = read_text(clone, "HANDOFF-0047", budget=budget)
        assert atlas_slice.estimate(text) <= budget, (budget, atlas_slice.estimate(text))


@pytest.mark.blocking
def test_c1_f6_a_dry_run_writes_nothing(clone: Path, tmp_path: Path) -> None:
    out = tmp_path / "existing.txt"
    out.write_bytes(b"kept\n")
    args = ["atlas", "--around", "kgme/ledger.py", "--base", str(clone), "--dry-run"]
    assert cli.main([*args, "--out", str(out)]) == 0
    assert out.read_bytes() == b"kept\n"


@pytest.mark.blocking
def test_c1_f7_files_named_outright_come_before_a_folders_nodes() -> None:
    nodes = {
        "kgme.z": atlas.Node("kgme.z", "module", "Code.", "kgme/z.py"),
        "reader-a": atlas.Node("reader-a", "reader", "Reader.", "docs/readers/a.md"),
    }
    seeds = atlas_slice.read_seeds(["docs/readers/", "kgme/z.py"], nodes)
    assert seeds == ["kgme.z", "reader-a"], "the named file first, though it sorts later"


@pytest.mark.blocking
def test_c2_f2_equivalent_spellings_of_an_excluded_path_never_appear(clone: Path) -> None:
    spellings = ["././memory/example.md", "kgme/../memory/example.md", str(clone / "logs" / "x.md")]
    text = read_text(clone, around=[*spellings, "kgme/ledger.py"])
    assert "memory" not in text.split("\n", 1)[0] and "logs" not in text.split("\n", 1)[0]
    assert not [p for p in read_paths(text) if p.startswith(("memory/", "logs/"))]
    assert text.startswith("# Atlas slice: kgme/ledger.py\n")
    outside = read_text(clone, around=["../elsewhere.py", "kgme/ledger.py"])
    assert "elsewhere" not in outside


@pytest.mark.blocking
def test_c2_f3_a_test_importing_a_test_is_kept_at_both_ends(clone: Path) -> None:
    runner = read_text(clone, around=["tests/test_review_run.py"])
    assert "tests/test_review.py" in read_seed_list(runner, "tests/test_review_run.py", "imports")
    imported = read_text(clone, around=["tests/test_review.py"])
    assert "tests/test_review_run.py" in read_seed_list(imported, "tests/test_review.py", "tests")


@pytest.mark.blocking
@pytest.mark.parametrize("spelling", [".", "./", "ABSOLUTE"])
def test_c3_f9_the_root_folder_is_a_seed_of_every_permitted_node(
    clone: Path, spelling: str
) -> None:
    given = str(clone) if spelling == "ABSOLUTE" else spelling
    text = read_text(clone, around=[given], budget=1000)
    assert text.split("\n## ", 1)[1].split("\n", 1)[0].endswith("(seed)"), text[:300]
    last = text.rstrip().splitlines()[-1]
    assert last.startswith("Cut at the budget of 1000 tokens: ") and "seed " in last, last
    assert atlas_slice.estimate(text) <= 1000
    assert not [p for p in read_paths(text) if p.startswith(("memory/", "logs/"))]


@pytest.mark.blocking
def test_c4_f10_from_a_subdirectory_the_base_is_the_containing_checkout(
    clone: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(clone / "kgme")
    assert cli.main(["atlas", "--slice", "HANDOFF-0047"]) == 0
    assert "## kgme/session.py (seed)" in capsys.readouterr().out
    assert cli.main(["atlas", "--around", ".", "--budget", "1000"]) == 0
    here = capsys.readouterr().out
    seeds = [ln for ln in here.splitlines() if ln.endswith("(seed)")]
    assert seeds and all(ln.startswith("## kgme/") for ln in seeds), seeds[:3]
    assert cli.main(["atlas", "--around", "ledger.py"]) == 0
    assert "## kgme/ledger.py (seed)" in capsys.readouterr().out


@pytest.mark.blocking
def test_c5_f1_a_tier1_base_inside_a_checkout_is_refused(clone: Path, capsys) -> None:
    secret = clone / "kgme" / "hooks"
    settings = {**SETTINGS, "paths": {**SETTINGS["paths"], "tier1_paths": [str(secret)]}}
    with pytest.raises(ValueError, match="Tier 1"):
        atlas_read.read_slice(secret, settings, None, ["guard.py"], None)


@pytest.mark.blocking
def test_c5_f1_an_export_nested_in_a_checkout_is_its_own_tree(clone: Path) -> None:
    export = clone / "exported"
    (export / "kgme").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "kgme/ledger.py", export / "kgme/ledger.py")
    shutil.copy(ROOT / "kgme/events.py", export / "kgme/events.py")
    try:
        text = read_text(export, around=["kgme/ledger.py"])
        named = read_paths(text)
        assert "kgme/ledger.py" in named and "kgme/events.py" in named
        assert "kgme/session.py" not in named, "the export, not the checkout around it"
    finally:
        shutil.rmtree(export)
