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
Side effects: one process tree; its stream file.
"""

import subprocess
from pathlib import Path

from kgme import loop
from kgme.crew import Task, unit
from kgme.session_logic import is_folder


class ClaudeAdapter:
    name = "claude"

    def argv(self, task: Task, workspace: Path) -> list[str]:
        """Pure: the fresh loose session for one task, its stream as JSON lines."""
        return [
            "uv", "run", "--frozen", "--project", str(workspace), "kgme", "session", "loose",
            "--handoff", task.handoff, "--task", task.name, "--",
            "--output-format", "stream-json", "--verbose",
        ]  # fmt: skip

    def request(self, task: Task, handoff_path: str, findings: str = "", main: str = "") -> str:
        """Pure: the line the session is given on stdin: the task, its handoff, its Outputs,
        its acceptance check and the route's exact commands, since the level's pinned list
        matches these forms and no other (the toy crew of 2026-10-28: a builder was refused
        `git add` with two paths and a review without `--project`, and stopped there); a
        folder Output takes its prefix rules' forms, a path under it (cycle 6 F24);
        `findings` is unused, a Claude builder reviews within its session."""
        project = f" --project {main}" if main else ""
        paths = [f"{p.rstrip('/')}/<file>" if is_folder(p) else p for p in task.outputs]
        adds = ", ".join(f"`git add -- {p}`" for p in paths)
        message = f'-m "crew: {task.name} ({task.handoff})"'
        commits = ", ".join(f"`git commit --only {p} {message}`" for p in paths)
        return (
            f"Task {task.name} of {task.handoff} ({handoff_path}), adopted by Michou, is yours "
            f"in this workspace. Outputs: {', '.join(task.outputs)}. Acceptance check: "
            f"`{task.acceptance}`, red now, green when you are done. {task.description}\n"
            f"Execute it under CLAUDE.md with nobody watching, by these exact commands, the "
            f"only git and review forms this level allows, one path per call and a file under "
            f"a folder Output by its own path (a `git add` or `git commit` naming two paths, a "
            f"bare commit and a review without `--project` are refused): build inside the "
            f"Outputs and get `make check` green; stage with {adds}; review with `uv run "
            f"--frozen{project} kgme review --handoff {unit(task.handoff, task.name)}`, and on "
            f"a BLOCK fix what blocks, write `logs/scratch/dispositions.md` and review again "
            f"with `--dispositions logs/scratch/dispositions.md`; on PASS commit once per path, "
            f"by pathspec, with {commits}; then stop.\n"
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
