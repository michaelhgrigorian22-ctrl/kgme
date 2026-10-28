"""A Codex task through the common loop (HANDOFF-0048 amendment 6; review cycle 1 F6, F7,
F8, F10), with the toy codex as both builder and reviewer.

Purpose: `kgme.crew_io.run_task_in_loop` runs a Codex task through `kgme.loop.run_loop` with
the Codex adapter: the loop's intent sits under the crew's intent and the builder's stream
events under the loop's (F8, F7); the builder's process group is in the workspace record
while it runs and cleared after (F10); the supervisor stages, gates, reviews and commits by
pathspec once the builder exits, and a BLOCK sends the findings back to a fresh builder
(F6); the task closes with its commit on the task branch.
Inputs: a fixture repository as the main checkout, the toy codex on PATH.
Outputs: pytest assertions.
Side effects: repositories, worktrees and files under `tmp_path`; events in the test streams.
"""

import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

from kgme import config, crew_io, events, ledger, paths, review_io, workspace
from kgme.crew import Task

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


def bin_with_fake_codex(tmp_path: Path) -> str:
    folder = tmp_path / "bin"
    folder.mkdir(exist_ok=True)
    tool = folder / "codex"
    tool.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FIXTURES / "fake_codex.py"}" "$@"\n')
    tool.chmod(0o755)
    return f"{folder}:{os.environ['PATH']}"


def fixture_main(tmp_path: Path, handoff: str) -> tuple[Path, dict, review_io.Places]:
    main = tmp_path / "main"
    (main / "docs" / "handoff").mkdir(parents=True)
    (main / "kgme").mkdir()
    (main / "kgme" / "__init__.py").write_text("")
    (main / "Makefile").write_text("check:\n\t@true\n")
    (main / "AGENTS.md").write_text("# toy constitution\n")
    (main / "docs" / "handoff" / "toy.md").write_text(
        f"---\nid: {handoff}\ntype: handoff\ncreated: 2026-10-27T20:00:00-07:00\nfrom: michou\n"
        f"to: claude-code\ntier: 2\nstatus: open\n---\n\n# {handoff}\n\n## Outputs\n"
        "`kgme/toy_codex.py`\n"
    )
    subprocess.run([*GIT, "init", "-q", "-b", "main"], cwd=main, check=True)
    subprocess.run([*GIT, "add", "-A"], cwd=main, check=True)
    subprocess.run([*GIT, "commit", "-q", "-m", "toy: the base"], cwd=main, check=True)
    settings = json.loads(json.dumps(config.read_config()))
    settings["crew"] = {"root": str(tmp_path / "work"), "parallel": 1, "harness": "codex",
                        "model": "toy-codex"}  # fmt: skip
    settings["models"]["arbiters"] = ["claude-toy-arbiter", "claude-toy-other"]
    places = review_io.Places(
        dirs=ledger.read_test_dirs(settings), audit_dir=tmp_path / "audit",
        scratch=tmp_path / "scratch", payloads=main / "logs" / "scratch" / "payloads",
        handoff_dir=main / "docs" / "handoff", prompt_path=ROOT / "control/review/prompt.md",
        root=main,
    )  # fmt: skip
    places.audit_dir.mkdir()
    return main, settings, places


@pytest.mark.blocking
def test_a_codex_task_builds_through_the_loop_under_the_crews_intent(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    handoff = f"HANDOFF-T{os.getpid()}X"
    main, settings, places = fixture_main(tmp_path, handoff)
    task = Task(handoff, "codex-toy", ("kgme/toy_codex.py",), "true", "codex", "toy-codex",
                description="Build add. SEED")  # fmt: skip
    ws, record = workspace.run_create(settings, main, task, run="R1")
    crew_intent = ledger.append(
        events.make_event(source="kgme", actor="kgme.crew", kind="intent", job=f"crew:{handoff}",
                          key=f"crew:{handoff}:R1", summary="crew toy"),
        places.dirs,
    )  # fmt: skip
    seen_pgids: list = []
    original = crew_io.write_process

    def spy(settings_, main_, name, proc):
        seen_pgids.append(proc.pid if proc is not None else None)
        original(settings_, main_, name, proc)

    monkeypatch.setattr(crew_io, "write_process", spy)
    result = crew_io.run_task_in_loop(
        main, settings, places, task, ws, "R1", crew_intent, [], None, timedelta(seconds=60),
        reviewer="toy-reviewer",  # the toy codex; a real Codex task's reviewer is a Claude model
    )  # fmt: skip
    assert result["status"] == "closed", result
    unit_events = review_io.read_handoff_events(f"{handoff}:codex-toy", places.dirs)
    loop_intent = [e for e in unit_events if (e["key"] or "").startswith("loop:")][0]
    assert loop_intent["kind"] == "intent", loop_intent
    assert loop_intent["parent"] == crew_intent, "under the crew's intent (F8)"
    verdicts = [
        e["summary"]
        for e in unit_events
        if e["kind"] == "outcome"
        and e["status"] == "ok"
        and not (e["key"] or "").startswith("loop:")
    ]
    assert len(verdicts) == 2 and " BLOCK " in verdicts[0] and " PASS " in verdicts[1], (
        "the seed blocks once, the fresh builder fixes it (F6)"
    )
    gates = [e for e in unit_events if (e["key"] or "").startswith("gate:")]
    assert len(gates) == 2 and all("green" in g["summary"] for g in gates)
    stream = ledger.read(places.dirs, run_id=f"codex-{loop_intent['run_id']}")
    assert stream, "the builder's commands are in the ledger (F7)"
    assert all(e["parent"] == loop_intent["id"] for e in stream), "under the loop's intent"
    kinds = {(e["kind"], e["job"]) for e in stream}
    assert kinds >= {
        ("intent", "tool:shell"),
        ("outcome", "tool:shell"),
        ("intent", "tool:apply_patch"),
    }
    groups = [p for p in seen_pgids if p is not None]
    assert len(groups) == 2 and all(isinstance(p, int) for p in groups), "one group per start"
    assert seen_pgids == [groups[0], None, groups[1], None], "recorded, then cleared (F10)"
    assert (workspace.read_record(settings, main, ws.name) or {}).get("pgid") is None, "cleared"
    log = subprocess.run(["git", "log", "-1", "--format=%s", "--name-only"], cwd=ws,
                         capture_output=True, text=True).stdout.split()  # fmt: skip
    assert log == ["crew:", "codex-toy", f"({handoff})", "kgme/toy_codex.py"], "by pathspec"
    assert "SEED" not in (ws / "kgme" / "toy_codex.py").read_text()


@pytest.mark.blocking
def test_a_persistent_blocker_goes_to_the_arbiters_and_the_ruling_reaches_the_next_builder(
    tmp_path, monkeypatch
) -> None:
    """Cycle 2 F6 (the arbiters' ruling): on `again`, a finding that stood two cycles is
    settled before the next Codex builder starts, and its settled ruling (class, option,
    reason) is in that builder's request beside the findings; the downgraded finding then
    passes and the task closes."""
    monkeypatch.setenv("PATH", bin_with_fake_codex(tmp_path))
    handoff = f"HANDOFF-T{os.getpid()}Y"
    main, settings, places = fixture_main(tmp_path, handoff)
    task = Task(handoff, "codex-stuck", ("kgme/toy_codex.py",), "true", "codex", "toy-codex",
                description="Build add. SEED KEEP SEED")  # fmt: skip
    ws, _ = workspace.run_create(settings, main, task, run="R2")
    crew_intent = ledger.append(
        events.make_event(source="kgme", actor="kgme.crew", kind="intent", job=f"crew:{handoff}",
                          key=f"crew:{handoff}:R2", summary="crew toy"),
        places.dirs,
    )  # fmt: skip
    asked: list[tuple[str, str]] = []
    # a split over the writer's cap whose chosen option is the second (cycle 4, under F6):
    # the builder's request carries it whole from the note's payload
    chosen = "keep the seed, it is required by the acceptance check"
    reason = (
        "split (claude-opus-5-5=advisory: remove the seed and let the task fail "
        "(blast 2, reversible); claude-fable-5-1=advisory: "
        + chosen
        + " (blast 1, reversible)); took claude-fable-5-1: "
        + chosen
    )
    assert len(reason) > 200

    def arbiters(unit_name, finding, argument, places_, models, template):
        asked.append((unit_name, finding))
        review_io.write_ruling(unit_name, finding, "advisory", reason, "pair", places_)
        return {"class": "advisory"}

    monkeypatch.setattr(crew_io.loop, "ARBITER_RETRY", timedelta(seconds=0))
    import kgme.loop as loop_module

    original = loop_module.run_loop

    def run_loop_with_stub(*args, **kwargs):
        kwargs["run_arbiters"] = arbiters
        kwargs["arbiter_retry"] = timedelta(seconds=0)
        return original(*args, **kwargs)

    monkeypatch.setattr(crew_io.loop, "run_loop", run_loop_with_stub)
    result = crew_io.run_task_in_loop(
        main, settings, places, task, ws, "R2", crew_intent, ["arbiter-one", "arbiter-two"],
        "brief $FINDING", timedelta(seconds=60), reviewer="toy-reviewer",
    )  # fmt: skip
    assert result["status"] == "closed", result
    assert asked == [(f"{handoff}:codex-stuck", "F1")], "once, after two blocking cycles"
    last_prompt = (ws / "logs" / "scratch" / "last-prompt.txt").read_text()
    assert "settled rulings" in last_prompt and "ruled F1=advisory" in last_prompt, last_prompt[
        -600:
    ]
    assert reason in last_prompt, "the whole ruling, past the summary's cap (cycle 4 F21)"
    assert "| F1 | blocking" in last_prompt, "the findings table travels with the ruling"
    stuck = review_io.read_handoff_events(f"{handoff}:codex-stuck", places.dirs)
    verdicts = [
        e["summary"]
        for e in stuck
        if e["kind"] == "outcome"
        and e["status"] == "ok"
        and not (e["key"] or "").startswith("loop:")
    ]
    assert [" BLOCK " in v for v in verdicts] == [True, True, False], verdicts
