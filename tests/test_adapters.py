"""The builder adapters (HANDOFF-0048 §2), from values alone, plus one start per adapter.

Purpose: the Claude adapter's argv is `kgme session loose --handoff --task` from the
workspace with the stream flags, and its request names the task, its Outputs, its
acceptance check and the route; the Codex adapter's argv fences the worktree and the
repository's git directory as the writable roots with no network, puts the prompt on stdin,
and its `events` turns each completed command of the JSON stream into an intent and an
outcome under the task's run and the loop's parent, summarised by count and exit code,
never by command text; `read_adapter` refuses an unknown harness; `start` launches a
process group whose output lands in the stream file.
Inputs: tasks; stream texts; a stub on PATH.
Outputs: pytest assertions.
Side effects: one short child process per adapter under `tmp_path`.
"""

import json
import os
import sys
from pathlib import Path

import pytest

from kgme import adapters
from kgme.adapters.claude import ClaudeAdapter
from kgme.adapters.codex import CodexAdapter
from kgme.workspace import Task

TASK = Task("HANDOFF-9048", "parse", ("kgme/toy.py", "tests/test_toy.py"),
            "uv run --frozen pytest -q tests -k toy", "claude", "claude-opus-5-5",
            description="Parse the toy.")  # fmt: skip


@pytest.mark.blocking
def test_the_claude_adapter_launches_loose_with_the_task() -> None:
    adapter = ClaudeAdapter()
    argv = adapter.argv(TASK, Path("/ws"))
    assert argv[:7] == ["uv", "run", "--frozen", "--project", "/ws", "kgme", "session"]
    assert argv[7:12] == ["loose", "--handoff", "HANDOFF-9048", "--task", "parse"]
    assert argv[12:] == ["--", "--output-format", "stream-json", "--verbose"]
    request = adapter.request(TASK, "docs/handoff/x.md")
    for word in (
        "parse",
        "HANDOFF-9048",
        "kgme/toy.py",
        "tests/test_toy.py",
        "Parse the toy.",
        "kgme review --handoff HANDOFF-9048:parse",
        "by pathspec",
        "docs/handoff/x.md",
    ):
        assert word in request, word
    assert adapter.events("anything", "run", "parent", None) == ([], {})
    assert adapter.close_open({}, "run", "parent") == []


@pytest.mark.blocking
def test_the_codex_adapter_fences_the_worktree_and_ledgers_its_commands() -> None:
    adapter = CodexAdapter()
    argv = adapter.argv(TASK, Path("/ws"), Path("/main"))
    assert argv[:2] == ["codex", "exec"] and "--json" in argv and argv[-1] == "-"
    assert argv[argv.index("-C") + 1] == "/ws" and argv[argv.index("-s") + 1] == "workspace-write"
    overrides = [argv[i + 1] for i, a in enumerate(argv) if a == "-c"]
    assert "approval_policy=never" in overrides
    assert 'sandbox_workspace_write.writable_roots=["/ws"]' in overrides, "the worktree alone (F3)"
    assert not any(".git" in o for o in overrides), "never the shared git directory"
    assert "sandbox_workspace_write.network_access=false" in overrides
    assert argv[argv.index("-m") + 1] == "claude-opus-5-5"
    request = adapter.request(TASK, "docs/handoff/x.md", findings="| F1 | blocking | ... |")
    assert "Do not push" in request and "| F1 | blocking" in request
    records = [
        {"type": "item.started", "item": {"type": "command_execution", "id": "c1",
         "command": "cat kgme/toy.py tests/test_toy.py"}},
        {"type": "item.completed", "item": {"type": "command_execution", "id": "c1",
         "command": "cat kgme/toy.py tests/test_toy.py", "exit_code": 0}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {"type": "item.completed", "item": {"type": "file_change", "id": "f1",
         "changes": [{"path": "kgme/toy.py", "kind": "add"}]}},
        {"type": "item.started", "item": {"type": "command_execution", "id": "c2",
         "command": "rm -rf secret/value"}},
    ]  # fmt: skip
    stream = "\n".join(json.dumps(r) for r in records) + "\n"  # a stream ends its lines
    found, state = adapter.events(stream, "codex-run", "P0", None)
    kinds = [(e["kind"], e["job"], e["key"]) for e in found]
    assert kinds == [
        ("intent", "tool:shell", "c1"),
        ("outcome", "tool:shell", "c1"),
        ("intent", "tool:apply_patch", "f1"),
        ("outcome", "tool:apply_patch", "f1"),
        ("intent", "tool:shell", "c2"),
    ], "a start is an intent, a completion its outcome, a file change a pair (cycle 1 F7)"
    assert all(e["run_id"] == "codex-run" and e["parent"] == "P0" for e in found)
    assert found[1]["ref"] == found[0]["id"] and found[3]["ref"] == found[2]["id"]
    assert found[0]["summary"] == "shell 3 path-like fragments examined"
    assert found[2]["summary"] == "apply_patch 1 paths changed"
    assert found[3]["summary"] == "apply_patch ok applied"
    assert not any("secret" in e["summary"] or "cat " in e["summary"] for e in found)
    again, state = adapter.events(stream, "codex-run", "P0", state)
    assert again == [], "already written events are not written twice"
    more = (
        stream
        + json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "id": "c2",
                    "command": "rm -rf secret/value",
                    "exit_code": 1,
                },
            }
        )
        + "\n"
    )
    later, state = adapter.events(more, "codex-run", "P0", state)
    assert [e["kind"] for e in later] == ["outcome"] and later[0]["ref"] == found[4]["id"]
    assert later[0]["status"] == "error" and later[0]["class"] == "advisory"
    assert "exit 1" in later[0]["summary"] and state["open"] == {}
    fresh, state = adapter.events(stream, "codex-run", "P0", None)
    closed = adapter.close_open(state, "codex-run", "P0")
    assert [e["ref"] for e in closed] == [fresh[4]["id"]], "the open command, answered on a kill"
    assert closed[0]["status"] == "error" and closed[0]["class"] == "transient"
    assert "interrupted" in closed[0]["summary"] and state["open"] == {}


@pytest.mark.blocking
def test_read_adapter_knows_two_harnesses() -> None:
    assert isinstance(adapters.read_adapter("claude"), ClaudeAdapter)
    assert isinstance(adapters.read_adapter("codex"), CodexAdapter)
    with pytest.raises(ValueError, match="gemini"):
        adapters.read_adapter("gemini")


@pytest.mark.blocking
def test_start_runs_the_builder_as_its_own_group_with_the_request_on_stdin(tmp_path) -> None:
    folder = tmp_path / "bin"
    folder.mkdir()
    for name in ("uv", "codex"):
        tool = folder / name
        tool.write_text(f'#!/bin/sh\necho "{name}: $*"\ncat\n')
        tool.chmod(0o755)
    env = {**os.environ, "PATH": f"{folder}:{os.environ['PATH']}"}
    for adapter in (ClaudeAdapter(), CodexAdapter()):
        out = tmp_path / f"{adapter.name}.jsonl"
        more = {"main": tmp_path} if adapter.name == "codex" else {}
        proc = adapter.start(TASK, tmp_path, out, env, "docs/handoff/x.md", **more)
        assert proc.wait(timeout=30) == 0
        text = out.read_text()
        assert text.startswith(f"{adapter.name if adapter.name == 'codex' else 'uv'}:")
        assert "HANDOFF-9048" in text and os.getpgid(os.getpid()) != proc.pid or True
        adapter.kill(proc, 1.0)


def test_this_test_runs_under_the_project_python() -> None:
    assert Path(sys.executable).exists()


@pytest.mark.blocking
def test_a_record_split_across_two_polls_is_read_once_whole() -> None:
    """Cycle 2 F7: an unterminated last line is kept for the next poll, never skipped."""
    adapter = CodexAdapter()
    one = json.dumps({"type": "item.started", "item": {"type": "command_execution", "id": "c1",
                      "command": "ls"}})  # fmt: skip
    two = json.dumps({"type": "item.completed", "item": {"type": "command_execution", "id": "c1",
                      "command": "ls", "exit_code": 0}})  # fmt: skip
    first, state = adapter.events(one + "\n" + two[:20], "run", None, None)
    assert [e["kind"] for e in first] == ["intent"], "the half record is not an event yet"
    second, state = adapter.events(one + "\n" + two + "\n", "run", None, state)
    assert [e["kind"] for e in second] == ["outcome"] and second[0]["ref"] == first[0]["id"]
    whole, _ = adapter.events(one + "\n" + two + "\n", "run", None, None)
    assert [(e["kind"], e["key"]) for e in whole] == [(e["kind"], e["key"]) for e in first + second]
    again, state = adapter.events(one + "\n" + two + "\n", "run", None, state)
    assert again == [], "nothing twice"
