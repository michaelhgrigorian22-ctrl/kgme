"""The Claude Code adapter: a task's builder is `kgme session loose` from its workspace.

Purpose: `start` launches `uv run --frozen --project <workspace> kgme session loose --handoff
<handoff> --task <task> -- --output-format stream-json --verbose` as its own process group
in the workspace, the request on its stdin (the one line `kgme.loop.execution_request`
gives a handoff, here naming the task); the level carries the committed `CLAUDE.md`, the
`kgme-builder` skill when Michou has applied it, and the task's `Outputs` as its fence
(HANDOFF-0047, 0056; amendment 11: no `--agent`). Its hooks ledger every call under the
session's id and, since HANDOFF-0063, under the loop's parent, so `events` has nothing to
add. `kill` is the loop's group kill.
Inputs: the task, its workspace, the output path, the environment.
Outputs: the process; an empty event list.
Side effects: one process group; its stream file.
"""

import subprocess
from pathlib import Path

from kgme import loop
from kgme.crew import Task, unit


class ClaudeAdapter:
    name = "claude"

    def argv(self, task: Task, workspace: Path) -> list[str]:
        """Pure: the fresh loose session for one task, its stream as JSON lines."""
        return [
            "uv", "run", "--frozen", "--project", str(workspace), "kgme", "session", "loose",
            "--handoff", task.handoff, "--task", task.name, "--",
            "--output-format", "stream-json", "--verbose",
        ]  # fmt: skip

    def request(self, task: Task, handoff_path: str, findings: str = "") -> str:
        """Pure: the line the session is given on stdin: the task, its handoff, its Outputs
        and its acceptance check; the route (review, then a commit on the task branch by
        pathspec) is the builder skill's and the level's."""
        return (
            f"Task {task.name} of {task.handoff} ({handoff_path}), adopted by Michou, is yours "
            f"in this workspace. Outputs: {', '.join(task.outputs)}. Acceptance check: "
            f"`{task.acceptance}`, red now, green when you are done. {task.description}\n"
            f"Execute it under CLAUDE.md to a PASS review (`kgme review --handoff "
            f"{unit(task.handoff, task.name)}`) and one commit of your Outputs on this branch by "
            "pathspec, with nobody watching.\n"
        )

    def start(
        self, task: Task, workspace: Path, out: Path, env: dict, handoff_path: str = ""
    ) -> subprocess.Popen:
        """Effect: the builder as its own process group."""
        return loop.start_builder(
            self.argv(task, workspace), workspace, out, env, self.request(task, handoff_path)
        )

    def events(
        self, text: str, run: str, parent: str | None, state: dict | None
    ) -> tuple[list[dict], dict]:
        """Pure: nothing: Claude Code's hooks write the ledger themselves."""
        return [], dict(state or {})

    def close_open(self, state: dict | None, run: str, parent: str | None) -> list[dict]:
        """Pure: nothing: the post hooks close what the session opened (HANDOFF-0061)."""
        return []

    def kill(self, proc: subprocess.Popen, grace: float) -> None:
        """Effect: SIGTERM to the group, SIGKILL after `grace`."""
        loop.kill_group(proc, grace)
