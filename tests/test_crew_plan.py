"""The plan and its gate (HANDOFF-0048 §3): parsing, the refusals, readiness, the order.

Purpose: `kgme.crew` from values alone: a plan parses into tasks; the gate refuses a task
without `Outputs` or an acceptance check, overlapping `Outputs` with no edge, a cycle, a
human or blocklisted path, and a width over the cap, and lets a sound plan through; a
revised plan passes; the same plan hashes the same; ready tasks follow the edges and wait
behind a stopped one; the integration order is the plan's.
Inputs: plan texts.
Outputs: pytest assertions.
Side effects: none.
"""

import pytest

from kgme import config, crew

SETTINGS = config.read_config()
HUMAN = tuple(SETTINGS["hooks"]["human_paths"])
PATTERNS = [p[3:] for p in SETTINGS["hooks"]["blocklist"] if p.startswith("**/")]
TIER1 = tuple(SETTINGS["paths"]["tier1_paths"])

PLAN = """# Plan: HANDOFF-9048

## Task: parse
outputs: `kgme/toy_parse.py`, `tests/test_toy_parse.py`
acceptance: `uv run --frozen pytest -q tests -k toy_parse`
harness: claude
model: claude-opus-5-5
after:
Parse the toy's lines.

## Task: render
outputs: `kgme/toy_render.py`
acceptance: `uv run --frozen pytest -q tests -k toy_render`
harness: codex
model: gpt-6-astra
after:
Render them.

## Task: wire
outputs: `kgme/toy_wire.py`
acceptance: `uv run --frozen pytest -q tests -k toy_wire`
harness: claude
model:
after: parse
Wire the parser in.
"""


CREW = {"harness": "claude", "model": "claude-opus-5-5"}


def gate(text: str, parallel: int = 1) -> list[str]:
    """The gate as the crew runs it: harness and model resolved first (cycle 3 F18)."""
    tasks = [
        crew.resolve_task(t, CREW, "claude-builder", "gpt-6-astra") for t in crew.parse_plan(text)
    ]
    return crew.check_plan(tasks, parallel, HUMAN, PATTERNS, TIER1)


@pytest.mark.blocking
def test_a_plan_parses_into_tasks_in_order() -> None:
    tasks = crew.parse_plan(PLAN)
    assert [t.name for t in tasks] == ["parse", "render", "wire"]
    assert tasks[0].handoff == "HANDOFF-9048"
    assert tasks[0].outputs == ("kgme/toy_parse.py", "tests/test_toy_parse.py")
    assert tasks[0].acceptance == "uv run --frozen pytest -q tests -k toy_parse"
    assert tasks[1].harness == "codex" and tasks[1].model == "gpt-6-astra"
    assert tasks[2].after == ("parse",) and tasks[2].description == "Wire the parser in."


@pytest.mark.blocking
def test_the_gate_refuses_overlap_without_an_edge_then_passes_the_revision() -> None:
    overlapping = PLAN.replace("outputs: `kgme/toy_render.py`", "outputs: `kgme/toy_parse.py`")
    refusals = gate(overlapping, parallel=3)
    assert any("Outputs overlap" in r and "parse and render" in r for r in refusals)
    revised = overlapping.replace("after:\nRender them.", "after: parse\nRender them.")
    assert gate(revised, parallel=3) == []


@pytest.mark.blocking
@pytest.mark.parametrize(
    "change, expected",
    [
        (("outputs: `kgme/toy_render.py`", "outputs:"), "render: no Outputs"),
        (("acceptance: `uv run --frozen pytest -q tests -k toy_render`", "acceptance:"),
         "render: no acceptance check"),
        (("outputs: `kgme/toy_render.py`", "outputs: `kgme.toml`"), "kgme.toml is a human path"),
        (("outputs: `kgme/toy_render.py`", "outputs: `docs/adr/ADR-099.md`"), "is a human path"),
        (("outputs: `kgme/toy_render.py`", "outputs: `kgme/secrets.env`"), "is blocklisted"),
        (("harness: codex", "harness: gemini"), "harness 'gemini'"),
        (("after: parse\nWire", "after: nowhere\nWire"), "which the plan does not name"),
    ],
)  # fmt: skip
def test_the_gate_refuses_what_section_3_names(change: tuple[str, str], expected: str) -> None:
    refusals = gate(PLAN.replace(*change), parallel=3)
    assert any(expected in r for r in refusals), refusals


@pytest.mark.blocking
def test_the_gate_refuses_a_cycle_and_a_width_over_the_cap() -> None:
    cyclic = PLAN.replace("after:\nParse the toy's lines.", "after: wire\nParse the toy's lines.")
    assert any("cycle" in r for r in gate(cyclic, parallel=3))
    assert any("width 2 exceeds the cap 1" in r for r in gate(PLAN, parallel=1))
    assert gate(PLAN, parallel=2) == []
    assert gate("# Plan: HANDOFF-9048\n") == ["the plan names no task"]


@pytest.mark.blocking
def test_tier1_paths_are_refused_from_the_configured_list() -> None:
    private = TIER1[0]
    planned = PLAN.replace("outputs: `kgme/toy_render.py`", f"outputs: `{private}/x.md`")
    assert any("Tier 1" in r or "human" in r or "blocklisted" in r for r in gate(planned, 3))


@pytest.mark.blocking
def test_ready_tasks_follow_the_edges_and_wait_behind_a_stopped_one() -> None:
    tasks = crew.parse_plan(PLAN)
    assert [t.name for t in crew.ready_tasks(tasks, set(), set())] == ["parse", "render"]
    assert [t.name for t in crew.ready_tasks(tasks, {"parse"}, set())] == ["render", "wire"]
    assert [t.name for t in crew.ready_tasks(tasks, set(), {"parse"})] == ["render"], (
        "wire waits behind its stopped dependency"
    )
    assert crew.ready_tasks(tasks, {"parse", "render", "wire"}, set()) == []


@pytest.mark.blocking
def test_the_order_is_the_plans_and_the_hash_ignores_spacing() -> None:
    tasks = crew.parse_plan(PLAN)
    assert crew.integration_order(tasks) == ["parse", "render", "wire"]
    assert crew.plan_sha(PLAN) == crew.plan_sha(PLAN.replace("\n\n", "\n\n\n").replace("  ", " "))
    assert crew.plan_sha(PLAN) != crew.plan_sha(PLAN.replace("Wire", "Join"))
    assert crew.depths(tasks) == {"parse": 0, "render": 0, "wire": 1}


@pytest.mark.blocking
def test_outputs_outside_the_repository_are_left_out_of_a_plan_and_refused_at_create(
    tmp_path,
) -> None:
    """Cycle 1 F4: an absolute path, a `..` segment or a `~` never reach the sandbox's write
    list: the plan parser drops them (so the gate refuses the task for having no Outputs or
    overlapping ones), and `kgme workspace create` refuses a task that carries one."""
    from kgme import workspace
    from kgme.crew import Task

    planned = PLAN.replace(
        "outputs: `kgme/toy_render.py`", "outputs: `/etc/passwd`, `../outside.py`, `~/x.py`"
    )
    tasks = crew.parse_plan(planned)
    assert tasks[1].outputs == (), "nothing escaping is kept"
    assert any("render: no Outputs" in r for r in gate(planned, 3))
    sneaky = PLAN.replace(
        "outputs: `kgme/toy_render.py`", "outputs: `kgme/../../x.py`, `kgme/ok.py`"
    )
    assert crew.parse_plan(sneaky)[1].outputs == ("kgme/ok.py",)
    settings = {"crew": {"root": str(tmp_path / "work")}, "models": {"builder": "m"}}
    bad = Task("HANDOFF-9048", "t", ("/etc/passwd",), "true")
    with pytest.raises(ValueError, match="relative paths inside the repository"):
        workspace.run_create(settings, tmp_path, bad)
    dotted = Task("HANDOFF-9048", "t", ("kgme/a.py", "../b.py"), "true")
    with pytest.raises(ValueError, match=r"\.\./b\.py"):
        workspace.run_create(settings, tmp_path, dotted)


@pytest.mark.blocking
def test_harness_and_model_are_resolved_together() -> None:
    """Cycle 2 F18: a blank harness is `[crew] harness`, a blank model the crew's when it
    runs under the harness, else the builder's; a Codex model never survives a move to Claude."""
    from kgme.crew import Task, resolve_task

    crew_claude = {"harness": "claude", "model": "claude-opus-5-5"}
    blank = Task("HANDOFF-9048", "t", ("a.py",), "true", "", "")
    got = resolve_task(blank, crew_claude, "claude-builder")
    assert (got.harness, got.model) == ("claude", "claude-opus-5-5")
    codex_blank = Task("HANDOFF-9048", "t", ("a.py",), "true", "codex", "")
    got = resolve_task(codex_blank, crew_claude, "claude-builder", "gpt-6-astra")
    assert (got.harness, got.model) == ("codex", "gpt-6-astra"), "Codex's own default (cycle 3)"
    unfit = resolve_task(codex_blank, crew_claude, "claude-builder", "")
    assert unfit.model == "", "nothing fits: blank, for the gate to refuse"
    assert any(
        "no model runs under harness codex" in r
        for r in crew.check_plan([unfit], 3, HUMAN, PATTERNS, TIER1)
    )
    wrong = Task("HANDOFF-9048", "t", ("a.py",), "true", "codex", "claude-opus-5-5")
    assert any(
        "does not run under codex" in r for r in crew.check_plan([wrong], 3, HUMAN, PATTERNS, TIER1)
    )
    got = resolve_task(codex_blank, {"harness": "codex", "model": "gpt-6-astra"}, "claude-builder")
    assert got.model == "gpt-6-astra", "the crew's model when it runs under the harness"
    moved = resolve_task(Task("HANDOFF-9048", "t", ("a.py",), "true", "claude", "gpt-6-astra"),
                         crew_claude, "claude-builder")  # fmt: skip
    assert moved.model == "claude-opus-5-5", "a Codex model dropped on the way to Claude"
    plan = crew.parse_plan(PLAN.replace("harness: claude\nmodel: claude-opus-5-5\nafter:\nParse",
                                        "after:\nParse"))  # fmt: skip
    assert plan[0].harness == "" and plan[0].model == "", "the parser leaves blanks to resolve"


@pytest.mark.blocking
def test_check_plan_on_the_command_line_resolves_as_the_crew_does(tmp_path, capsys) -> None:
    """Cycle 3 F18: `kgme crew check-plan FILE` resolves a blank harness and model before the
    gate, so a plan the crew's planner may write is not refused at the command line."""
    import argparse

    from kgme import crew_io

    plan = tmp_path / "plan.md"
    plan.write_text(PLAN.replace("harness: claude\nmodel: claude-opus-5-5\nafter:\nParse",
                                 "after:\nParse"))  # fmt: skip
    settings = {**SETTINGS, "crew": {"root": str(tmp_path), "parallel": 2, "max_width": 3}}
    args = argparse.Namespace(action="check-plan", plan=str(plan), handoff=None, stall_minutes=15)
    assert crew_io.run_crew_command(args, tmp_path, settings) == 0, capsys.readouterr().out
    assert "green" in capsys.readouterr().out
