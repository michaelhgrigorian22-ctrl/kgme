"""Tests for guard rule 5, loop mode's write fence (HANDOFF-0045 §2).

Purpose: under `KGME_LOOP_HANDOFF` the pre-tool guard refuses every file write outside the
handoff's `Outputs`, `tests/`, and `logs/scratch/`, as a `blocking` outcome tied to its
intent; with no readable list for that handoff it refuses every write; reads, Bash, and
interactive sessions are unchanged, and nothing another rule refuses becomes allowed. The
list is parsed once from the handoff's `## Outputs` section by `kgme.loop_outputs`.
Inputs: this handoff's own text; toy handoffs; the gitignored test streams and scratch.
Outputs: pytest assertions.
Side effects: lists under the test scratch's `loop/` folder and lines in the test streams;
the hook entry point runs as a subprocess with `--test-streams`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kgme import clean_fs, config, events, ledger, loop_outputs, paths
from kgme.hooks import guard

ROOT = paths.root()
SETTINGS = config.read_config()
HUMAN = tuple(SETTINGS["hooks"]["human_paths"])
TOY = """---
id: HANDOFF-9045
---

# Toy

## Outputs
`memory/agent/loop-probe.md`, `tests/` (anything), and a paragraph in `docs/readers/review-loop.md`.

## Report
`docs/audit/elsewhere.md`
"""


def decide(tool: str, loop, **tool_input) -> guard.Decision:
    return guard.decide(
        tool, tool_input, ROOT, ROOT, [], [], [], human_paths=HUMAN, loop=loop,
        loop_handoff="HANDOFF-9045",
    )  # fmt: skip


def toy_entries() -> tuple[str, ...]:
    return tuple(loop_outputs.parse_outputs(TOY)) + loop_outputs.ALWAYS


@pytest.mark.blocking
def test_the_outputs_section_is_read_as_a_list_of_paths() -> None:
    text = (ROOT / "docs/handoff/done/2026-10-14-guard-destructive-git.md").read_text()
    assert loop_outputs.parse_outputs(text) == [
        ".claude/settings.json",
        "control/hooks/pre_tool_guard.sh",
        "kgme/canary.py",
        "tests/policy/",
        "tests/test_guard_loop.py",
        "docs/readers/review-loop.md",
        "docs/STATUS.md",
    ]
    assert loop_outputs.parse_outputs(TOY) == [
        "memory/agent/loop-probe.md",
        "tests/",
        "docs/readers/review-loop.md",
    ]
    tricky = "## Outputs\n`/etc/passwd`, `../up.md`, `kgme review`, `KGME_LOOP_HANDOFF`, `~/x.md`\n"
    assert loop_outputs.parse_outputs(tricky) == []
    assert loop_outputs.parse_outputs("# no section\n`a/b.md`\n") == []


@pytest.mark.blocking
def test_loop_mode_refuses_a_write_outside_the_outputs_and_allows_one_inside() -> None:
    loop = toy_entries()
    refused = decide("Write", loop, file_path="docs/charter.md", content="x")
    assert not refused.allowed and "outside HANDOFF-9045's Outputs" in refused.reason
    assert decide("Write", loop, file_path="memory/agent/loop-probe.md", content="x").allowed
    assert decide("Edit", loop, file_path="tests/test_anything.py").allowed
    assert decide("Write", loop, file_path="logs/scratch/loop/x.txt", content="x").allowed
    assert not decide("Write", loop, file_path="memory/agent/other.md", content="x").allowed
    assert not decide("Write", loop, file_path="/tmp/outside.md", content="x").allowed
    assert not decide("NotebookEdit", loop, notebook_path="kgme/x.ipynb").allowed
    # reads and Bash are not this rule's
    assert decide("Read", loop, file_path="docs/charter.md").allowed
    assert decide("Bash", loop, command="ls docs").allowed


@pytest.mark.blocking
def test_loop_mode_never_allows_what_another_rule_refuses() -> None:
    loop = toy_entries()
    human = decide("Edit", loop, file_path="docs/readers/review-loop.md")
    assert not human.allowed and "human-authored" in human.reason


@pytest.mark.blocking
def test_loop_mode_without_its_list_refuses_every_write() -> None:
    reason = "no Outputs list for HANDOFF-9045: missing"
    refused = decide("Write", reason, file_path="memory/agent/loop-probe.md", content="x")
    assert not refused.allowed and "every write is refused" in refused.reason
    assert decide("Read", reason, file_path="docs/charter.md").allowed


@pytest.mark.blocking
def test_interactive_sessions_are_unchanged() -> None:
    assert decide("Write", None, file_path="memory/agent/other.md", content="x").allowed
    assert loop_outputs.read_outputs(Path("/nonexistent"), {}) is None


@pytest.mark.blocking
def test_the_list_is_set_once_and_must_name_its_handoff(tmp_path: Path) -> None:
    run = events.new_ulid()
    scratch = tmp_path / "scratch"
    path, digest = loop_outputs.write_outputs(tmp_path, scratch, "HANDOFF-9045", run, TOY)
    assert path == scratch / "loop" / run / "outputs.txt"
    env = {
        loop_outputs.ENV_HANDOFF: "HANDOFF-9045",
        loop_outputs.ENV_RUN: run,
        loop_outputs.ENV_SHA: digest,
    }
    assert loop_outputs.read_outputs(scratch, env) == toy_entries()
    with pytest.raises(clean_fs.Refused):
        loop_outputs.write_outputs(tmp_path, scratch, "HANDOFF-9045", run, TOY)
    other = {**env, loop_outputs.ENV_HANDOFF: "HANDOFF-0001"}
    assert "is not HANDOFF-0001's" in loop_outputs.read_outputs(scratch, other)
    lost = {**env, loop_outputs.ENV_RUN: events.new_ulid()}
    assert "no Outputs list" in loop_outputs.read_outputs(scratch, lost)
    escape = {**env, loop_outputs.ENV_RUN: "../../etc"}
    assert "not a loop run id" in loop_outputs.read_outputs(scratch, escape)


def run_hook(tool: str, tool_input: dict, env: dict[str, str]) -> subprocess.CompletedProcess:
    """The live entry point, as Claude Code calls it, on the test streams."""
    payload = {
        "session_id": f"loop-{events.new_ulid()}",
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_{events.new_ulid()}",
        "cwd": str(ROOT),
    }
    return subprocess.run(
        [sys.executable, "-m", "kgme.hooks.pre_tool_guard", "--test-streams"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**os.environ, **env},
        timeout=30,
        check=False,
    ), payload


@pytest.mark.blocking
def test_the_live_guard_refuses_the_charter_write_as_a_blocking_outcome() -> None:
    run = events.new_ulid()
    scratch = paths.scratch_test_dir(SETTINGS)
    _, digest = loop_outputs.write_outputs(ROOT, scratch, "HANDOFF-9045", run, TOY)
    env = {
        loop_outputs.ENV_HANDOFF: "HANDOFF-9045",
        loop_outputs.ENV_RUN: run,
        loop_outputs.ENV_SHA: digest,
    }
    done, payload = run_hook("Write", {"file_path": "docs/charter.md", "content": "x"}, env)
    assert done.returncode == 2 and "outside HANDOFF-9045's Outputs" in done.stderr
    found = ledger.read(ledger.read_test_dirs(SETTINGS), run_id=payload["session_id"])
    intent, outcome = (
        [e for e in found if e["kind"] == "intent"],
        [e for e in found if e["kind"] == "outcome"],
    )
    assert outcome and (outcome[0]["status"], outcome[0]["class"]) == ("refused", "blocking")
    assert outcome[0]["ref"] == intent[0]["id"]
    target = {"file_path": "memory/agent/loop-probe.md", "content": "x"}
    allowed, _ = run_hook("Write", target, env)
    assert allowed.returncode == 0, allowed.stderr
    assert not (ROOT / "memory/agent/loop-probe.md").exists(), "the hook decides, never writes"


# Review cycle 1 (AUDIT-0067)


@pytest.mark.blocking
def test_c1_f2_the_builder_cannot_write_its_own_outputs_list(tmp_path: Path) -> None:
    loop = toy_entries()
    run = events.new_ulid()
    for scratch in ("logs/scratch", "logs/scratch-test"):
        listed = f"{scratch}/loop/{run}/outputs.txt"
        refused = guard.decide(
            "Edit", {"file_path": listed}, ROOT, ROOT, [], [], [], human_paths=HUMAN, loop=loop,
            loop_handoff="HANDOFF-9045", loop_dir=ROOT / scratch / "loop",
        )  # fmt: skip
        assert not refused.allowed and "Outputs list" in refused.reason, listed


@pytest.mark.blocking
def test_c1_f2_a_list_changed_after_the_loop_set_it_refuses_every_write(tmp_path: Path) -> None:
    run = events.new_ulid()
    scratch = tmp_path / "scratch"
    path, digest = loop_outputs.write_outputs(tmp_path, scratch, "HANDOFF-9045", run, TOY)
    env = {
        loop_outputs.ENV_HANDOFF: "HANDOFF-9045",
        loop_outputs.ENV_RUN: run,
        loop_outputs.ENV_SHA: digest,
    }
    assert loop_outputs.read_outputs(scratch, env) == toy_entries()
    with path.open("a", encoding="utf-8") as listed:  # a Bash line could do the same
        listed.write("memory/agent/other.md\n")
    changed = loop_outputs.read_outputs(scratch, env)
    assert isinstance(changed, str) and "changed since the loop set it" in changed
    unbound = {k: v for k, v in env.items() if k != loop_outputs.ENV_SHA}
    assert "no digest" in loop_outputs.read_outputs(scratch, unbound)


@pytest.mark.blocking
def test_c1_f1_bash_in_loop_mode_is_the_sandboxs_not_rule_5s() -> None:
    """The arbitration of review cycle 1 F1 (two arbiters, advisory): rule 5 is the
    file-tool half of the fence. Bash, and every program it starts, is fenced by the `loose`
    level's OS sandbox, whose `allowWrite` is the same list (ADR-022; HANDOFF-0047, which
    the loop, HANDOFF-0043, depends on). A change here is a decision, not a regression."""
    loop = toy_entries()
    for command in ("printf x > docs/charter.md", "uv run python -c 'open(\"docs/charter.md\")'"):
        assert decide("Bash", loop, command=command).allowed, command
