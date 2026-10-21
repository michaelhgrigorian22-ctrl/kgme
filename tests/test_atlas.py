"""Tests for `kgme atlas` (HANDOFF-0051): Obsidian's lens on how KGME's parts connect.

Purpose: imports are read without running anything; each kind of node links what the handoff
says it links; the notes are a function of the tree alone, so a second run writes nothing;
only notes the atlas generated are ever removed, and nothing outside `atlas/` is touched; a
listed project is read by structure only and a Tier 1 one is refused; a failure is one
`transient` ledger event; `atlas/` is ignored by git. On the real tree, the acceptance links
hold: HANDOFF-0034 to `kgme/brief*.py` and its report, `kgme/ledger.py` from the modules
that import it, ADR-023 to ADR-016, and ADR-019 reached through the ledger module that cites
it.
Inputs: literal fixtures; this repository's tracked tree.
Outputs: pytest assertions.
Side effects: files under `tmp_path`; one `git init` there; reads this repository.
"""

import os
import subprocess
from pathlib import Path

import pytest

from kgme import atlas, atlas_read, clean_fs, config, ledger, paths

ROOT = paths.root()
SETTINGS = config.read_config()
S = atlas.Source


def fixture_tree() -> list[atlas.Source]:
    return [
        S("kgme/ledger.py", '"""The ledger (ADR-019)."""\nimport json\n'),
        S("kgme/brief.py", "from kgme import ledger\nfrom kgme.hooks import guard\n"),
        S("kgme/hooks/guard.py", "import os\n"),
        S("control/hooks/pre_tool_guard.sh", "uv run python -m kgme.hooks.guard\n"),
        S("tests/test_brief.py", "from kgme import brief\n"),
        S("docs/adr/ADR-019-ledger.md", "---\nid: ADR-019\nsupersedes: null\n---\n# ADR-019\n"),
        S("docs/adr/ADR-016-classes.md", "---\nid: ADR-016\n---\n# ADR-016\n"),
        S("docs/adr/ADR-023-loops.md", "---\nid: ADR-023\n---\n# ADR-023 (amends ADR-016)\n"),
        S(
            "docs/handoff/done/brief.md",
            "---\nid: HANDOFF-0034\nstatus: done\nreport: docs/audit/loop.md\n"
            "depends_on: [HANDOFF-0026]\nplan_ref: PLAN-PHASE-1 step 9\n---\n"
            "Per ADR-016.\n\n## Outputs\n`kgme/brief*.py`, `tests/{test_brief}.py`\n\n"
            "## Report\nx\n",
        ),
        S("docs/handoff/done/ledger.md", "---\nid: HANDOFF-0026\nstatus: done\n---\n# x\n"),
        S("docs/audit/loop.md", "---\nid: AUDIT-0035\nhandoff: HANDOFF-0034\n---\n# Report\n"),
        S(
            "docs/readers/review.md",
            "---\nid: READER-X\n---\nSee `kgme/brief.py` and `control/`.\n",
        ),
        S("docs/plans/phase.md", "| 9 | **Loop 0.** brief | 0034 | done |\n"),
    ]


@pytest.mark.blocking
def test_imports_are_read_without_running_anything() -> None:
    text = (
        "import os, kgme.ledger\nfrom kgme import paths, events\nfrom . import x\n"
        "raise SystemExit\n"
    )
    assert atlas.read_imports(text) == {
        "os", "kgme.ledger", "kgme", "kgme.paths", "kgme.events",
    }  # fmt: skip
    assert atlas.read_imports("def (:") == set()
    assert atlas.expand("jobs/brief/{job.md,run.py}") == ["jobs/brief/job.md", "jobs/brief/run.py"]


@pytest.mark.blocking
def test_each_kind_of_node_links_what_the_handoff_names() -> None:
    nodes = atlas.build_graph(fixture_tree())

    def links(name: str) -> set[str]:
        return nodes[name].links

    assert {"kgme.ledger", "kgme.hooks.guard", "tests.test_brief"} <= links("kgme.brief")
    assert "ADR-019" in links("kgme.ledger"), "code links the decisions its text cites"
    assert links("control.hooks.pre_tool_guard.sh") == {"kgme.hooks.guard"}
    assert links("HANDOFF-0034") >= {
        "kgme.brief", "tests.test_brief", "AUDIT-0035", "HANDOFF-0026", "plan-step-9", "ADR-016"
    }  # fmt: skip
    assert "HANDOFF-0034" in links("ADR-016"), "an ADR links the handoffs that cite it"
    assert "ADR-016" in links("ADR-023")
    assert "HANDOFF-0034" in links("AUDIT-0035") and "HANDOFF-0034" in links("plan-step-9")
    assert {"kgme.brief", "folder-control"} <= links("reader-review")
    assert {"kgme.ledger", "kgme.brief"} <= links("folder-kgme")
    kinds = {n.kind for n in nodes.values()}
    assert kinds == {"folder", "module", "test", "adr", "handoff", "audit", "reader", "plan"}


@pytest.mark.blocking
def test_notes_are_a_function_of_the_tree_and_open_on_their_file() -> None:
    notes = atlas.render_notes(atlas.build_graph(fixture_tree()))
    assert notes == atlas.render_notes(atlas.build_graph(list(reversed(fixture_tree()))))
    ledger_note = notes["module/kgme.ledger.md"]
    assert ledger_note.startswith(f"---\nkind: module\n{atlas.MARK}\n---\n")
    assert (
        "[kgme/ledger.py](../../kgme/ledger.py)" in ledger_note and "- [[ADR-019]]" in ledger_note
    )
    assert "[[docs/handoff/done/brief]]" in notes["handoff/HANDOFF-0034.md"]


@pytest.mark.blocking
def test_a_second_run_writes_nothing_and_only_generated_notes_go(tmp_path: Path) -> None:
    out = tmp_path / "atlas"
    notes = atlas.render_notes(atlas.build_graph(fixture_tree()))
    assert atlas_read.write_atlas(out, tmp_path, notes) == (len(notes), 0, 0)
    stamps = {p: p.stat().st_mtime_ns for p in out.rglob("*.md")}
    assert atlas_read.write_atlas(out, tmp_path, notes) == (0, 0, len(notes))
    assert {p: p.stat().st_mtime_ns for p in out.rglob("*.md")} == stamps
    stale, mine = out / "module" / "kgme.gone.md", out / "module" / "michou.md"
    stale.write_text(f"---\nkind: module\n{atlas.MARK}\n---\n# kgme.gone\n")
    mine.write_text("---\nkind: module\n---\n# written by hand\n")
    assert atlas_read.write_atlas(out, tmp_path, notes) == (0, 1, len(notes))
    assert not stale.exists() and mine.exists()
    assert not [p for p in out.rglob("*") if ".tmp-" in p.name]


@pytest.mark.blocking
def test_an_atlas_reached_through_a_link_is_refused(tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    base = tmp_path / "repo"
    base.mkdir()
    (base / "atlas").symlink_to(elsewhere)
    with pytest.raises(clean_fs.Refused):
        atlas_read.write_atlas(base / "atlas", base, {"module/x.md": "x"})
    assert list(elsewhere.iterdir()) == []


@pytest.mark.blocking
def test_a_project_is_read_by_structure_and_tier_1_is_refused(tmp_path: Path) -> None:
    project = tmp_path / "thesis"
    (project / "notes").mkdir(parents=True)
    (project / "secret.txt").write_text("never read")
    (project / "README.md").write_text(
        "Run `kgme brief`; see [plan](docs/plan.md) and `kgme/ledger.py`."
    )
    settings = {**SETTINGS, "atlas": {"projects": [str(project)]}}
    [read] = atlas_read.read_projects(settings, ROOT)
    assert (read.name, read.folders, read.readme_links) == ("thesis", ("notes",), ("docs/plan.md",))
    assert read.uses == ("jobs.brief.run", "kgme.ledger")
    tier1 = str(paths.tier1_paths(SETTINGS, ROOT)[0])
    for listed in (tier1, str(Path(tier1).parent)):
        with pytest.raises(clean_fs.Refused):
            atlas_read.read_projects({**SETTINGS, "atlas": {"projects": [listed]}}, ROOT)


@pytest.mark.blocking
def test_a_failure_is_one_transient_event_and_exit_1(tmp_path: Path, capsys) -> None:
    base = tmp_path / "not-a-checkout"
    base.mkdir()
    assert atlas_read.run_atlas(base, SETTINGS) == 1
    found = ledger.read(ledger.read_base_dirs(SETTINGS, base))
    assert [(e["kind"], e["class"], e["job"]) for e in found] == [("note", "transient", "atlas")]
    assert "atlas not regenerated" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_real_tree_holds_the_acceptance_links() -> None:
    nodes = atlas.build_graph(atlas_read.read_sources(ROOT))
    assert {"kgme.brief", "kgme.brief_io", "AUDIT-0035"} <= nodes["HANDOFF-0034"].links
    assert "kgme.ledger" in nodes["kgme.brief_io"].links
    assert "ADR-019" in nodes["kgme.ledger"].links
    assert "ADR-016" in nodes["ADR-023"].links
    importers = [n for n in nodes.values() if "kgme.ledger" in n.links and n.kind == "module"]
    assert len(importers) >= 10


@pytest.mark.blocking
def test_the_atlas_is_ignored_by_git() -> None:
    found = subprocess.run(
        ["git", "check-ignore", "-q", "atlas/module/kgme.ledger.md"], cwd=ROOT, check=False
    )
    assert found.returncode == 0
    assert os.path.exists(ROOT / ".obsidian" / "graph.json")


# Review cycle 1 (AUDIT-0073)


@pytest.mark.blocking
def test_c1_f1_a_link_inside_the_atlas_is_refused_and_nothing_outside_changes(
    tmp_path: Path,
) -> None:
    base = tmp_path / "repo"
    (base / "atlas").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "x.md").write_text(f"---\n{atlas.MARK}\n---\nkept\n")
    (base / "atlas" / "module").symlink_to(elsewhere)
    with pytest.raises(clean_fs.Refused):
        atlas_read.write_atlas(base / "atlas", base, {"module/x.md": "replaced"})
    assert [p.name for p in elsewhere.iterdir()] == ["x.md"]
    assert (elsewhere / "x.md").read_text().endswith("kept\n")


@pytest.mark.blocking
def test_c1_f2_a_readme_that_is_a_link_is_never_followed(tmp_path: Path) -> None:
    protected = tmp_path / "protected.md"
    protected.write_text("[secret](never-read.md) `kgme/ledger.py`")
    project = tmp_path / "thesis"
    project.mkdir()
    (project / "README.md").symlink_to(protected)
    with pytest.raises(clean_fs.Refused):
        atlas_read.read_projects({**SETTINGS, "atlas": {"projects": [str(project)]}}, ROOT)


@pytest.mark.blocking
def test_c1_f4_every_tracked_top_level_folder_is_a_node() -> None:
    nodes = atlas.build_graph(
        fixture_tree(), tracked=["memory/notes/a.md", "logs/ledger/2026-10.jsonl", "cockpit/x.js"]
    )
    assert {"folder-memory", "folder-logs", "folder-cockpit"} <= set(nodes)
    real = atlas.build_graph(atlas_read.read_sources(ROOT), tracked=atlas_read.read_tracked(ROOT))
    assert {"folder-memory", "folder-logs", "folder-docs", "folder-kgme"} <= set(real)


@pytest.mark.blocking
def test_c1_f5_every_existing_file_an_outputs_names_is_linked() -> None:
    nodes = atlas.build_graph(atlas_read.read_sources(ROOT), tracked=atlas_read.read_tracked(ROOT))
    named = {
        "jobs.brief.job.md",
        "memory.templates.reminder.md",
        "memory.templates.task.md",
        "memory.templates.daily.md",
    }
    assert named <= nodes["HANDOFF-0034"].links
    assert nodes["memory.templates.daily.md"].kind == "file"
    assert "[[memory/templates/daily]]" in nodes["memory.templates.daily.md"].line


@pytest.mark.blocking
def test_c1_f6_a_relative_project_resolves_against_the_checkout(tmp_path: Path) -> None:
    project = ROOT.parent / f"atlas-probe-{tmp_path.name}"
    project.mkdir()
    try:
        settings = {**SETTINGS, "atlas": {"projects": [f"../{project.name}"]}}
        here = os.getcwd()
        try:
            os.chdir(tmp_path)
            from_tmp = atlas_read.read_projects(settings, ROOT)
        finally:
            os.chdir(here)
        assert from_tmp == atlas_read.read_projects(settings, ROOT)
        assert [p.name for p in from_tmp] == [project.name]
    finally:
        project.rmdir()
