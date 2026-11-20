"""Tests for the role pass of `kgme lint` (HANDOFF-0071 §2, ADR-025 §2-4).

Purpose: every rule of a role is blocking: fields and their types, skill, level (never
`cheap` in v1), profile, tools within the level, tier ceiling and never Tier 1, an escalation
chain that reaches `michou` in at most three hops, a rubric of three to six dimensions with the
standing `intent` and `context` gates; one malformed role never crashes the pass; the default
pass reads the index's blobs and `--all` the working tree's; the declared roles pass.
Inputs: fixture checkouts from `tests/roletools.py`; this repository's own `roles/`.
Outputs: pytest assertions.
Side effects: repositories under `tmp_path`.
"""

from pathlib import Path

import pytest
from roletools import (
    ROOT,
    RUBRIC,
    read_blocking,
    read_role_findings,
    role_text,
    run_git,
    write_file,
    write_repo,
)

from kgme import cli, roles, roles_io

# --- the declared roles ------------------------------------------------------------------


@pytest.mark.blocking
def test_the_declared_roles_pass_lint_and_list_by_department() -> None:
    assert [f.line() for f in read_role_findings(ROOT) if f.cls == "blocking"] == []
    declared = roles_io.read_roles(ROOT)
    by_department: dict[str, list[str]] = {}
    for role in declared.values():
        by_department.setdefault(role["department"], []).append(role["id"])
    assert sorted(by_department["build"]) == ["build.builder", "build.integrator", "build.planner"]
    assert by_department["audit"] == ["audit.auditor"]
    assert declared["build.planner"]["kind"] == "manager"
    assert declared["build.builder"]["skill"] == "kgme-builder"
    assert declared["build.integrator"]["skill"] == "kgme-integrator"


# --- each rule ---------------------------------------------------------------------------


@pytest.mark.blocking
def test_a_clean_role_passes(tmp_path: Path) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst")})
    assert read_blocking(base) == []


@pytest.mark.blocking
@pytest.mark.parametrize(
    "fields,needle",
    [
        ({"purpose": None}, "missing `purpose`"),
        ({"skill": "kgme-absent"}, "skill `kgme-absent`"),
        ({"level": "wide"}, "level `wide`"),
        ({"profile": "absent"}, "profile `absent`"),
        ({"model": "huge"}, "model `huge`"),
        ({"kind": "boss"}, "kind `boss`"),
        ({"tools": ["Read", "Bash"]}, "`Bash` is not allowed at tight"),
        ({"level": "loose", "tools": ["Read", "WebFetch"]}, "`WebFetch` is not allowed at loose"),
        ({"tier_max": 1}, "Tier 1"),
        ({"level": "cheap", "tools": ["Read"], "tier_max": 3}, "`cheap` is not a role level"),
        ({"model": "cheap"}, "model `cheap` is the cheap lane's"),
        ({"escalates_to": "finance.nobody"}, "does not resolve"),
        ({"rubric": "roles/finance/rubrics/absent.md"}, "rubric"),
        ({"id": "finance.other"}, "id `finance.other`"),
    ],
)
def test_each_broken_rule_is_blocking(tmp_path: Path, fields: dict, needle: str) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst", **fields)})
    lines = read_blocking(base)
    assert any(needle in line for line in lines), lines


@pytest.mark.blocking
def test_a_profile_narrows_the_level_and_never_widens_it(tmp_path: Path) -> None:
    narrowed = role_text("finance", "analyst", level="work", profile="claude-builder")
    assert read_blocking(write_repo(tmp_path / "a", {"finance/analyst": narrowed})) == []
    codex = role_text("finance", "analyst", level="work", profile="codex-builder")
    lines = read_blocking(write_repo(tmp_path / "b", {"finance/analyst": codex}))
    assert any("`Read` is not allowed at work" in line for line in lines), lines


@pytest.mark.blocking
def test_the_chain_reaches_michou_in_three_hops_without_a_cycle(tmp_path: Path) -> None:
    chain = {
        "build/a": role_text("build", "a", escalates_to="build.b"),
        "build/b": role_text("build", "b", escalates_to="build.c"),
        "build/c": role_text("build", "c", escalates_to="michou"),
    }
    assert read_blocking(write_repo(tmp_path / "ok", chain)) == []
    long = {**chain, "build/c": role_text("build", "c", escalates_to="build.d")}
    long["build/d"] = role_text("build", "d", escalates_to="michou")
    assert any("hops" in line for line in read_blocking(write_repo(tmp_path / "long", long)))
    loop = {**chain, "build/c": role_text("build", "c", escalates_to="build.a")}
    assert any("cycle" in line for line in read_blocking(write_repo(tmp_path / "loop", loop)))


@pytest.mark.blocking
def test_one_manager_per_department(tmp_path: Path) -> None:
    two = {
        "build/a": role_text("build", "a", kind="manager"),
        "build/b": role_text("build", "b", kind="manager"),
    }
    assert any("one manager" in line for line in read_blocking(write_repo(tmp_path, two)))


@pytest.mark.blocking
@pytest.mark.parametrize(
    "body,needle",
    [
        ("- `intent` (gate): a.\n- `context` (gate): b.\n", "three to six"),
        ("".join(f"- `d{i}` (gate): x.\n" for i in range(7)), "three to six"),
        ("- `intent`: a.\n- `context` (gate): b.\n- `x`: c.\n", "`intent` gate"),
        ("- `intent` (gate): a.\n- `x`: b.\n- `y`: c.\n", "`context` gate"),
    ],
)
def test_the_rubric_shape_is_blocking(tmp_path: Path, body: str, needle: str) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst")})
    write_file(base, "roles/finance/rubrics/analyst.md", "# Rubric\n\n## Dimensions\n" + body)
    assert any(needle in line for line in read_blocking(base)), read_blocking(base)


# --- malformed roles (AUDIT-0173 F5) -----------------------------------------------------


@pytest.mark.blocking
@pytest.mark.parametrize(
    "fields,needle",
    [
        ({"id": []}, "`id` is a string"),
        ({"kind": []}, "`kind` is a string"),
        ({"level": 3}, "`level` is a string"),
        ({"escalates_to": ["michou"]}, "`escalates_to` is a string"),
        ({"rubric": 3}, "`rubric` is a string"),
        ({"profile": []}, "`profile` is a string"),
        ({"tier_max": "2"}, "tier_max must be 2 or 3"),
    ],
)
def test_a_malformed_role_is_findings_never_a_crash(
    tmp_path: Path, fields: dict, needle: str
) -> None:
    roles_ = {
        "finance/analyst": role_text("finance", "analyst", **fields),
        "finance/other": role_text("finance", "other", tools=["Bash"]),
    }
    lines = read_blocking(write_repo(tmp_path, roles_))
    assert any(needle in line for line in lines), lines
    assert any("roles/finance/other.toml" in line and "`Bash`" in line for line in lines), lines


@pytest.mark.blocking
def test_a_role_escalating_to_a_malformed_one_still_reports(tmp_path: Path) -> None:
    roles_ = {
        "build/a": role_text("build", "a", escalates_to="build.b"),
        "build/b": role_text("build", "b", escalates_to=[]),
    }
    lines = read_blocking(write_repo(tmp_path, roles_))
    assert any("`escalates_to` is a string" in line for line in lines), lines


# --- a tool is one complete bare name (AUDIT-0174 F2) ------------------------------------


@pytest.mark.blocking
@pytest.mark.parametrize(
    "tool",
    ["Read,NotebookEdit", "Read NotebookEdit", "Read;Bash", " Read", "Read\n", "", "Bash(x *)"],
)
def test_a_tool_that_is_not_one_bare_name_is_blocking(tmp_path: Path, tool: str) -> None:
    role = role_text("finance", "analyst", level="work", tools=["Read", tool])
    lines = read_blocking(write_repo(tmp_path, {"finance/analyst": role}))
    assert any("is not one bare tool name" in line for line in lines), lines


@pytest.mark.blocking
def test_lint_and_launch_share_one_tool_validator() -> None:
    grant = frozenset({"Read", "Grep"})
    for tool in ("Read,NotebookEdit", "Bash(make check)", "Read", "Bash", 3):
        verdict = roles.tool_problem(tool, grant, "work")
        assert (verdict is None) == (tool == "Read"), (tool, verdict)


# --- index by default, the tree under --all (AUDIT-0173 F6) -------------------------------


@pytest.mark.blocking
def test_lint_reads_the_index_by_default_and_the_tree_under_all(tmp_path: Path) -> None:
    base = write_repo(tmp_path)
    write_file(base, "roles/finance/analyst.toml", role_text("finance", "analyst", tier_max=1))
    write_file(base, "roles/finance/rubrics/analyst.md", RUBRIC.format(id="finance.analyst"))
    assert read_blocking(base, index=True) == []
    assert any("Tier 1" in line for line in read_blocking(base, index=False))
    assert cli.main(["lint", "--base", str(base), "--all"]) == 1
    assert cli.main(["lint", "--base", str(base)]) == 0


@pytest.mark.blocking
def test_a_staged_role_is_judged_on_its_staged_copy(tmp_path: Path) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst")})
    write_file(base, "roles/finance/analyst.toml", role_text("finance", "analyst", tier_max=1))
    run_git(base, "add", "roles/finance/analyst.toml")
    write_file(base, "roles/finance/analyst.toml", role_text("finance", "analyst"))  # repaired
    assert any("Tier 1" in line for line in read_blocking(base, index=True))
    assert read_blocking(base, index=False) == []


@pytest.mark.blocking
def test_a_staged_rubric_is_judged_on_its_staged_copy(tmp_path: Path) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst")})
    rubric = "roles/finance/rubrics/analyst.md"
    write_file(base, rubric, "# Rubric\n\n## Dimensions\n- `intent` (gate): a.\n")
    run_git(base, "add", rubric)
    write_file(base, rubric, RUBRIC.format(id="finance.analyst"))  # repaired, unstaged
    assert any("three to six" in line for line in read_blocking(base, index=True))
    assert read_blocking(base, index=False) == []


@pytest.mark.blocking
def test_a_working_tree_deletion_does_not_hide_a_staged_role(tmp_path: Path) -> None:
    base = write_repo(tmp_path)
    write_file(base, "roles/finance/analyst.toml", role_text("finance", "analyst", tier_max=1))
    write_file(base, "roles/finance/rubrics/analyst.md", RUBRIC.format(id="finance.analyst"))
    run_git(base, "add", "roles")
    (base / "roles/finance/analyst.toml").unlink()
    assert any("Tier 1" in line for line in read_blocking(base, index=True))
    assert read_blocking(base, index=False) == []


@pytest.mark.blocking
def test_a_staged_deletion_of_a_rubric_is_blocking_in_the_index(tmp_path: Path) -> None:
    base = write_repo(tmp_path, {"finance/analyst": role_text("finance", "analyst")})
    run_git(base, "rm", "-q", "--cached", "roles/finance/rubrics/analyst.md")
    assert any("rubric" in line for line in read_blocking(base, index=True))
    assert read_blocking(base, index=False) == []


# --- the pure half -----------------------------------------------------------------------


@pytest.mark.blocking
def test_allowed_tools_are_derived_from_the_level() -> None:
    template = {"permissions": {"allow": ["Read", "Edit(/{repo}/**)", "Bash(make check)"]}}
    assert roles.allowed_from_template(template) == frozenset({"Read", "Edit", "Bash"})
    denied = {"permissions": {"allow": ["Read", "WebFetch"], "deny": ["WebFetch"]}}
    assert roles.allowed_from_template(denied) == frozenset({"Read"})
    assert roles.CEILINGS == {"tight": 2, "work": 2, "loose": 2}
