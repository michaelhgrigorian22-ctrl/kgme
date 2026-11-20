"""Tests for `kgme agent new|list|show` and the atlas's org chart (HANDOFF-0071 §3, §5).

Purpose: `new` writes a lint-clean role, rubric and stub skill and says what is missing,
never over an existing file; `list` groups by department with counts; `show` prints the
chain; the atlas draws roles, `escalates_to` edges and departments.
Inputs: fixture checkouts from `tests/roletools.py`.
Outputs: pytest assertions.
Side effects: repositories under `tmp_path`.
"""

import inspect
import tomllib
from pathlib import Path

import pytest
from roletools import SETTINGS, SKILL, read_blocking, role_text, write_repo

from kgme import atlas, roles_io


@pytest.mark.blocking
def test_new_writes_a_lint_clean_role_and_says_what_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = write_repo(tmp_path)
    assert roles_io.run_new(base, SETTINGS, "finance", "analyst") == 0
    out = capsys.readouterr().out
    assert "skills/kgme-finance-analyst/SKILL.md" in out and "missing" in out
    assert (base / "roles/finance/analyst.toml").is_file()
    assert (base / "roles/finance/rubrics/analyst.md").is_file()
    data = tomllib.loads((base / "roles/finance/analyst.toml").read_text())
    assert data["id"] == "finance.analyst" and data["skill"] == "kgme-finance-analyst"
    assert read_blocking(base) == []
    assert roles_io.run_new(base, SETTINGS, "finance", "analyst") == 2  # never overwrites
    assert roles_io.run_new(base, SETTINGS, "templates", "x") == 2  # a reserved folder
    assert roles_io.run_new(base, SETTINGS, "Finance", "x") == 2  # kebab-case only


@pytest.mark.blocking
def test_list_groups_by_department_with_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    base = write_repo(
        tmp_path,
        {
            "build/a": role_text("build", "a", kind="manager"),
            "build/b": role_text("build", "b", escalates_to="build.a"),
            "finance/analyst": role_text("finance", "analyst"),
        },
    )
    assert roles_io.run_list(base) == 0
    out = capsys.readouterr().out
    assert "Build (2)" in out and "Finance (1)" in out and "build.b" in out
    assert roles_io.run_show(base, SETTINGS, "build.b") == 0
    shown = capsys.readouterr().out
    assert "build.b -> build.a -> michou" in shown
    assert roles_io.run_show(base, SETTINGS, "build.zz") == 2


@pytest.mark.blocking
def test_the_atlas_draws_the_org_chart() -> None:
    sources = [
        atlas.Source("roles/build/planner.toml", role_text("build", "planner", kind="manager")),
        atlas.Source("roles/build/builder.toml", role_text("build", "builder",
                                                           escalates_to="build.planner")),
        atlas.Source("roles/templates/role.toml", "id = \"{department}.{role}\"\n"),
        atlas.Source("skills/kgme-fixture/SKILL.md", SKILL.format(name="kgme-fixture")),
    ]  # fmt: skip
    nodes = atlas.build_graph(sources, [], [s.path for s in sources])
    assert nodes["role-build.builder"].kind == "role"
    assert "role-build.planner" in nodes["role-build.builder"].links
    assert "michou" in nodes["role-build.planner"].links
    assert {"role-build.planner", "role-build.builder"} <= nodes["department-build"].links
    assert "skill-kgme-fixture" in nodes["role-build.builder"].links
    assert not any("templates" in name for name in nodes)


@pytest.mark.blocking
def test_the_new_public_helpers_are_fully_annotated() -> None:
    from kgme import cli_parser

    for function in (atlas.add_role, atlas.link_role, cli_parser.add_agent):
        unannotated = [name for name, p in inspect.signature(function).parameters.items()
                       if p.annotation is inspect.Parameter.empty]  # fmt: skip
        assert unannotated == [], (function.__name__, unannotated)
