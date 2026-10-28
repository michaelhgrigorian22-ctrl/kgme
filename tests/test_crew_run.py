"""`kgme crew` end to end on a toy handoff, with the planner, the tasks and the merge gate as
stubs and the review through the real `kgme.review_run.run_cycle` against the toy reviewer
(HANDOFF-0048, the amended acceptance test's crew half, mechanical parts).

Purpose: the first plan has two overlapping Outputs and is refused by the plan gate, revised
by the planner, reviewed (the toy reviewer blocks on a seeded line), revised once more and
passes, with no human input; dispatch at width 1 builds the tasks in plan order, each in
its own workspace under the root; a task the stub halts is quarantined with its worktree
read-only and its dependent waits, independent tasks go on; the rest integrate on
`crew/<handoff>/integration`, the crew stops at `awaiting approval` naming the commit, and
`kgme approve --what code --sha <that commit>` from Michou's terminal fast-forwards `main`;
a merge-gate refusal quarantines too. The live halves (real builders, the scanner's fake
key, the zero-width character on a branch, a hanging builder) are `tests/policy` cells and
the merge-gate unit tests.
Inputs: a fixture repository as the main checkout; the toy reviewer on PATH.
Outputs: pytest assertions.
Side effects: repositories, worktrees, trial clones and files under `tmp_path`; events in
the test streams.
"""

import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from kgme import approve, config, crew_io, events, ledger, paths, review_io, workspace

ROOT = paths.root()
FIXTURES = ROOT / "tests" / "fixtures" / "loop"
GIT = [
    "git",
    "-c",
    "user.name=t",
    "-c",
    "user.email=t@example.invalid",
    "-c",
    "core.hooksPath=/dev/null",
]
HANDOFF = "HANDOFF-9050"  # the template id; each test takes its own unit (`unit_id`)
HANDOFF_TEXT = f"""---
id: {HANDOFF}
type: handoff
created: 2026-10-27T20:00:00-07:00
from: michou
to: claude-code
tier: 2
status: open
---

# {HANDOFF}: the toy crew

## What
Three toy modules.

## Outputs
`kgme/toy_a.py`, `kgme/toy_b.py`, `kgme/toy_c.py`

## Acceptance test
Each module imports.
"""
PLAN_OVERLAP = f"""# Plan: {HANDOFF}

## Task: a
outputs: `kgme/toy_a.py`
acceptance: `true`
harness: claude
model: claude-toy
after:
Module a.

## Task: b
outputs: `kgme/toy_a.py`
acceptance: `true`
harness: claude
model: claude-toy
after:
Module b, wrongly on a's file.

## Task: c
outputs: `kgme/toy_c.py`
acceptance: `true`
harness: claude
model: claude-toy
after: a
Module c after a.
"""
FIELDS = "acceptance: `true`\nharness: claude\nmodel: claude-toy\nafter:\n"
PLAN_SEEDED = PLAN_OVERLAP.replace(
    f"outputs: `kgme/toy_a.py`\n{FIELDS}Module b",
    f"outputs: `kgme/toy_b.py`\n{FIELDS}Module b SEED",
)
assert PLAN_SEEDED != PLAN_OVERLAP
PLAN_GOOD = (
    PLAN_SEEDED.replace("Module b SEED", "Module b")
    + "\n## Dispositions\nF1: fixed, the seed is gone.\n"
)


def unit_id(tag: str) -> str:
    """One handoff id per test process and test: the test streams keep every run's events,
    and a unit's loop state is read over all of them (as `tests/test_loop.py` does)."""
    return f"HANDOFF-T{os.getpid()}{tag}"


def bin_with_fake_codex(tmp_path: Path) -> str:
    folder = tmp_path / "bin"
    folder.mkdir(exist_ok=True)
    tool = folder / "codex"
    tool.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FIXTURES / "fake_codex.py"}" "$@"\n')
    tool.chmod(0o755)
    return f"{folder}:{os.environ['PATH']}"


def fixture_main(tmp_path: Path, handoff: str = HANDOFF) -> tuple[Path, dict, review_io.Places]:
    main = tmp_path / "main"
    (main / "docs" / "handoff").mkdir(parents=True)
    (main / "kgme").mkdir()
    (main / "kgme" / "__init__.py").write_text("")
    (main / "Makefile").write_text("check:\n\t@true\n")
    text = HANDOFF_TEXT.replace(HANDOFF, handoff)
    (main / "docs" / "handoff" / "toy.md").write_text(text)
    (main / "control" / "review").mkdir(parents=True)
    (main / "control" / "review" / "plan-prompt.md").write_text(
        "Review the plan of $HANDOFF at $PATCH_PATH (sha $SHA), cycle $CYCLE.\n"
        "$PRIOR_FINDINGS\n$DISPOSITIONS\n"
    )
    subprocess.run([*GIT, "init", "-q", "-b", "main"], cwd=main, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=main, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "toy: the base"], cwd=main, check=True)
    settings = json.loads(json.dumps(config.read_config()))
    settings["crew"] = {
        "root": str(tmp_path / "work"),
        "parallel": 1,
        "max_plan_cycles": 5,
        "harness": "claude",
        "model": "claude-toy",
    }
    settings["models"]["reviewer"] = "toy-reviewer"
    places = review_io.Places(
        dirs=ledger.read_test_dirs(settings),
        audit_dir=tmp_path / "audit",
        scratch=tmp_path / "scratch",
        payloads=main / "logs" / "scratch" / "payloads",
        handoff_dir=main / "docs" / "handoff",
        prompt_path=ROOT / "control/review/prompt.md",
        root=main,
    )
    places.audit_dir.mkdir()
    return main, settings, places


def stub_task(outcomes: dict[str, str]):
    """A builder stub per task: writes the task's module on its branch and commits it, or
    ends as `outcomes` says ("halted", "stalled")."""

    def run_task(main, settings, places, task, ws, run, parent, arbiters, template, stall):
        if outcomes.get(task.name, "closed") != "closed":
            return {
                "status": outcomes[task.name],
                "reason": f"{task.name} {outcomes[task.name]} (stub)",
                "audits": [],
                "cycles": 1,
            }
        for path in task.outputs:
            (ws / path).write_text(f"# {task.name}\n")
        subprocess.run([*GIT, "add", "--", *task.outputs], cwd=ws, check=True)
        subprocess.run(
            [
                *GIT,
                "commit",
                "-q",
                "-m",
                f"crew: {task.name} ({task.handoff})",
                "--",
                *task.outputs,
            ],
            cwd=ws,
            check=True,
        )
        return {"status": "closed", "reason": "PASS (stub)", "audits": ["AUDIT-0001"], "cycles": 1}

    return run_task


def stub_gate(refuse: dict[str, list[str]] | None = None):
    def merge_gate(main, settings, task, record, scratch):
        if refuse and task.name in refuse:
            return refuse[task.name], "", []
        return crew_io.run_merge_gate(main, settings, task, record, scratch)

    return merge_gate


@pytest.mark.blocking
def test_the_toy_crew_plans_builds_quarantines_integrates_and_awaits_approval(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("A")
    main, settings, places = fixture_main(tmp_path, h)
    plans = iter([p.replace(HANDOFF, h) for p in (PLAN_OVERLAP, PLAN_SEEDED, PLAN_GOOD)])
    asked: list[str] = []

    def planner(request: str, cycle: int) -> str:
        asked.append(request)
        return next(plans)

    code = crew_io.run_crew(
        h,
        main,
        settings,
        places,
        [],
        None,
        planner=planner,
        run_task=stub_task({"c": "halted"}),
        merge_gate=stub_gate(),
        stall=timedelta(seconds=5),
    )
    screen = capsys.readouterr().out
    assert code == 0, screen
    assert len(asked) == 3
    assert "Outputs overlap" in asked[1] and "The previous plan" in asked[1], "the gate's refusals"
    assert "| F1 | blocking" in asked[2] and "Dispositions" in asked[2], "the reviewer's findings"
    plan_events = review_io.read_handoff_events(f"{h}:plan", places.dirs)
    verdicts = [e["summary"] for e in plan_events if e["kind"] == "outcome" and e["status"] == "ok"]
    assert len(verdicts) == 2 and " BLOCK " in verdicts[0] and " PASS " in verdicts[1]
    crew_events = [e for e in ledger.read(places.dirs, stream="ledger") if e["job"] == f"crew:{h}"]
    keys = [e["key"] for e in crew_events]
    assert keys[0].startswith(f"crew:{h}:") and crew_events[0]["kind"] == "intent"
    assert "plan:1" in keys and "plan:3" in keys
    starts = [k for k in keys if k.endswith(":start")]
    assert starts == ["task:a:start", "task:b:start", "task:c:start"], "width 1, plan order"
    assert "task:a:integrated" in keys and "task:b:integrated" in keys
    assert "quarantine:c" in keys
    root = tmp_path / "work"
    pen = root / workspace.QUARANTINE / workspace.workspace_name(h, "c")
    assert pen.is_dir() and not os.access(pen, os.W_OK), "c's worktree is read-only in quarantine"
    assert (root / workspace.workspace_name(h, "a")).is_dir()
    head = subprocess.run(
        ["git", "rev-parse", workspace.integration_branch(h)],
        cwd=main,
        capture_output=True,
        text=True,
    ).stdout.strip()
    closing = crew_events[-1]
    assert closing["kind"] == "outcome" and closing["status"] == "ok"
    assert "awaiting approval" in closing["summary"] and head[:12] in closing["summary"]
    tree = subprocess.run(
        ["git", "ls-tree", "--name-only", "-r", head], cwd=main, capture_output=True, text=True
    ).stdout.split()
    assert "kgme/toy_a.py" in tree and "kgme/toy_b.py" in tree and "kgme/toy_c.py" not in tree
    assert "awaiting approval" in screen and "quarantined c" in screen
    integration = review_io.read_handoff_events(f"{h}:integration", places.dirs)
    assert any(" PASS " in e["summary"] for e in integration if e["kind"] == "outcome")
    # Michou's approval, from his own terminal, fast-forwards main
    for marker in approve.AGENT_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    monkeypatch.setattr(
        approve,
        "read_sha",
        lambda m, ref: subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
            cwd=m,
            capture_output=True,
            text=True,
        ).stdout.strip(),
    )
    monkeypatch.setattr(approve.ledger, "read_base_dirs", lambda s, m: places.dirs)
    monkeypatch.setattr("kgme.sync_io.run_sync", lambda m, s: 0)
    wrong = subprocess.run(["git", "rev-parse", "main"], cwd=main, capture_output=True, text=True)
    assert approve.run_approve(main, settings, "code", wrong.stdout.strip()) == 2, "not a crew head"
    assert approve.run_approve(main, settings, "code", head[:12]) == 0
    landed = subprocess.run(["git", "rev-parse", "main"], cwd=main, capture_output=True, text=True)
    assert landed.stdout.strip() == head
    approvals = [
        e for e in ledger.read(places.dirs) if e["kind"] == "approval" and e["job"] == "approve"
    ]
    assert approvals and approvals[-1]["key"] == f"approve:code:{head}"


@pytest.mark.blocking
def test_a_merge_gate_refusal_quarantines_and_a_stopped_plan_dispatches_nothing(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("B")
    main, settings, places = fixture_main(tmp_path, h)
    plans = iter([PLAN_GOOD.replace("Module b", "Module b SEED").replace(HANDOFF, h),
                  PLAN_GOOD.replace(HANDOFF, h)])  # fmt: skip
    code = crew_io.run_crew(
        h,
        main,
        settings,
        places,
        [],
        None,
        planner=lambda r, c: next(plans),
        run_task=stub_task({}),
        merge_gate=stub_gate({"a": ["kgme/toy_a.py carries U+200B (zero width space)"]}),
    )
    screen = capsys.readouterr().out
    assert code == 0, screen
    keys = [e["key"] for e in ledger.read(places.dirs, stream="ledger") if e["job"] == f"crew:{h}"]
    assert "quarantine:a" in keys and "task:b:integrated" in keys
    assert "task:c:start" not in keys, "c waits behind its quarantined dependency"
    assert "U+200B" in screen
    # a plan that never passes dispatches nothing
    monkeypatch.setattr(events, "new_ulid", events.new_ulid)
    h3 = unit_id("D")
    (main / "docs" / "handoff" / "toy.md").write_text(HANDOFF_TEXT.replace(HANDOFF, h3))
    subprocess.run([*GIT, "commit", "-q", "-am", "toy: the third"], cwd=main, check=True)
    stuck = iter([PLAN_OVERLAP.replace(HANDOFF, h3)] * 5)
    code = crew_io.run_crew(
        h3,
        main,
        settings,
        places,
        [],
        None,
        planner=lambda r, c: next(stuck),
        run_task=stub_task({}),
        merge_gate=stub_gate(),
    )
    assert code == 1
    assert "plan stopped" in capsys.readouterr().out


@pytest.mark.blocking
def test_a_settled_ruling_reaches_the_planner_and_the_same_plan_may_return(
    tmp_path, monkeypatch
) -> None:
    """Cycle 1 F5: a finding blocking two cycles goes to the arbiters (a stub here); the
    settled ruling is in the planner's next request, and a plan seen before is accepted again
    once a ruling landed, where it passes with the finding downgraded."""
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("E")
    main, settings, places = fixture_main(tmp_path, h)
    seeded_a = PLAN_GOOD.replace("Module b", "Module b SEED").replace(HANDOFF, h)
    seeded_b = seeded_a.replace("Module a.", "Module a, first.")
    plans = iter([seeded_a, seeded_b, seeded_b])
    asked: list[str] = []
    rulings: list[tuple[str, str]] = []

    def planner(request: str, cycle: int) -> str:
        asked.append(request)
        return next(plans)

    def arbitrate(unit_name, finding, argument, places_, models, template):
        rulings.append((unit_name, finding))
        review_io.write_ruling(
            unit_name, finding, "advisory", "the seed is fine here", "pair", places_
        )
        return {"class": "advisory"}

    plan_places_dirs = places.dirs
    code = crew_io.run_crew(
        h, main, settings, places, ["arbiter-one", "arbiter-two"], "brief $FINDING",
        planner=planner, run_task=stub_task({}), merge_gate=stub_gate(), arbitrate=arbitrate,
    )  # fmt: skip
    assert code == 0, asked[-1][-400:]
    assert rulings == [(f"{h}:plan", "F1")], "sent once, after two blocking cycles"
    assert "ruled F1=advisory" in asked[2] and "settled rulings" in asked[2]
    verdicts = [
        e["summary"] for e in review_io.read_handoff_events(f"{h}:plan", plan_places_dirs)
        if e["kind"] == "outcome" and e["status"] == "ok"
    ]  # fmt: skip
    assert [" BLOCK " in v for v in verdicts] == [True, True, False], verdicts


@pytest.mark.blocking
def test_integration_reruns_every_tasks_check_and_the_review_reads_the_candidate_tree(
    tmp_path, monkeypatch, capsys
) -> None:
    """Cycle 1 F11 and F12: at integration every integrated task's acceptance check runs again
    on the integration head, so a later task that breaks an earlier oracle stops the crew
    before `awaiting approval`; and the integration review runs in a checkout of the exact
    candidate, not the main checkout's tree."""
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("F")
    main, settings, places = fixture_main(tmp_path, h)
    plan = PLAN_GOOD.replace(HANDOFF, h)
    # task b's oracle: a must not exist. Task a (first) creates it, b's check passes on b's
    # branch only because b is built from the integration head before... no: b is built after
    # a integrates, so its check is red at the gate and b is quarantined; then a stands alone.
    # The regression case instead: task a's oracle is "toy_b.py absent", a integrates first,
    # then b integrates and breaks a's oracle; integration must see it.
    plan = plan.replace(
        "## Task: a\noutputs: `kgme/toy_a.py`\nacceptance: `true`",
        "## Task: a\noutputs: `kgme/toy_a.py`\nacceptance: `test ! -f kgme/toy_b.py`",
    )
    seen_trees: list[tuple[str, bool]] = []
    real_cycle = crew_io.review_run.run_cycle

    def spy_cycle(unit_name, model, dispositions, patch, places_, dry_run, **more):
        if unit_name.endswith(":integration"):
            where = places_.workspace
            seen_trees.append((str(where), bool(where and (where / "kgme" / "toy_a.py").is_file())))
        return real_cycle(unit_name, model, dispositions, patch, places_, dry_run, **more)

    monkeypatch.setattr(crew_io.review_run, "run_cycle", spy_cycle)
    code = crew_io.run_crew(
        h, main, settings, places, [], None, planner=lambda r, c: plan,
        run_task=stub_task({"c": "halted"}), merge_gate=stub_gate(),
    )  # fmt: skip
    screen = capsys.readouterr().out
    assert code == 1 and "integration not green" in screen, screen
    assert seen_trees == [], "a red integration gate is not reviewed"
    keys = [e["key"] for e in ledger.read(places.dirs, stream="ledger") if e["job"] == f"crew:{h}"]
    assert "task:a:integrated" in keys and "task:b:integrated" in keys, "each passed its own gate"
    # the same crew with a's oracle satisfied reviews the candidate tree itself
    h2 = unit_id("G")
    (main / "docs" / "handoff" / "toy.md").write_text(HANDOFF_TEXT.replace(HANDOFF, h2))
    subprocess.run([*GIT, "commit", "-q", "-am", "toy: the next"], cwd=main, check=True)
    code = crew_io.run_crew(
        h2, main, settings, places, [], None, planner=lambda r, c: PLAN_GOOD.replace(HANDOFF, h2),
        run_task=stub_task({"c": "halted"}), merge_gate=stub_gate(),
    )  # fmt: skip
    assert code == 0, capsys.readouterr().out
    assert len(seen_trees) == 1 and seen_trees[0][1], (
        "the reviewer's tree held the candidate's files"
    )
    assert str(main) not in seen_trees[0][0], "not the main checkout"
    assert not Path(seen_trees[0][0]).exists(), "the candidate checkout is gone afterwards"


@pytest.mark.blocking
def test_a_gate_that_cannot_run_quarantines_the_task_and_the_crew_goes_on(
    tmp_path, monkeypatch, capsys
) -> None:
    """Cycle 1 F13: a task whose acceptance command names a missing executable is refused at
    the merge gate as a classified refusal, quarantined, and the independent task goes on."""
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("H")
    main, settings, places = fixture_main(tmp_path, h)
    plan = PLAN_GOOD.replace(HANDOFF, h).replace(
        "## Task: a\noutputs: `kgme/toy_a.py`\nacceptance: `true`",
        "## Task: a\noutputs: `kgme/toy_a.py`\nacceptance: `no-such-oracle-binary --check`",
    )
    code = crew_io.run_crew(
        h, main, settings, places, [], None, planner=lambda r, c: plan,
        run_task=stub_task({}), merge_gate=stub_gate(),
    )  # fmt: skip
    screen = capsys.readouterr().out
    assert code == 0, screen
    keys = [e["key"] for e in ledger.read(places.dirs, stream="ledger") if e["job"] == f"crew:{h}"]
    assert "quarantine:a" in keys and "task:b:integrated" in keys
    assert "task:c:start" not in keys, "c waits behind a"
    assert "acceptance check is red" in screen
    root = tmp_path / "work"
    assert (root / workspace.QUARANTINE / workspace.workspace_name(h, "a")).is_dir()


@pytest.mark.blocking
def test_an_uncommitted_write_outside_the_outputs_is_refused_at_the_gate(
    tmp_path, monkeypatch, capsys
) -> None:
    """Cycle 2 F19: a builder that leaves a stray write in its workspace (a tracked file
    edited, an untracked file added, outside its Outputs) is refused at the merge gate and
    quarantined, whatever its branch carries."""
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    h = unit_id("J")
    main, settings, places = fixture_main(tmp_path, h)
    plan = PLAN_GOOD.replace(HANDOFF, h)
    builder = stub_task({})

    def straying(main_, settings_, places_, task, ws, run, parent, arbiters, template, stall):
        result = builder(
            main_, settings_, places_, task, ws, run, parent, arbiters, template, stall
        )
        if task.name == "a":
            (ws / "Makefile").write_text("check:\n\t@false\n")  # a tracked file, edited
            (ws / "kgme" / "extra.py").write_text("x = 1\n")  # untracked, outside the Outputs
        return result

    code = crew_io.run_crew(
        h, main, settings, places, [], None, planner=lambda r, c: plan, run_task=straying,
        merge_gate=stub_gate(),
    )  # fmt: skip
    screen = capsys.readouterr().out
    assert code == 0, screen
    keys = [e["key"] for e in ledger.read(places.dirs, stream="ledger") if e["job"] == f"crew:{h}"]
    assert "quarantine:a" in keys and "task:b:integrated" in keys
    assert "an uncommitted write outside the Outputs in the workspace: Makefile" in screen
    assert "kgme/extra.py" in screen
    assert "scanner: the built-in rules" in screen, "the gate names the scanner that ran (F14)"
