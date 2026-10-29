"""The Codex adapter: a task's builder is `codex exec --json` with the worktree as its only
writable root (HANDOFF-0048 §2, amendment 3).

Purpose: `start` launches `codex exec --json -C <workspace> -s workspace-write` under the
`codex-builder` profile of HANDOFF-0042 written out as overrides (`approval_policy=never`,
the worktree as the one writable root, no network), as its own process group, the request
on stdin. The repository's shared git directory is not writable (review cycle 1 F3): it
holds `main` and the integration refs, so the supervisor stages, gates, reviews and commits
for a Codex task (`kgme.crew_io.run_codex_cycle`, through `kgme.loop`'s `after_exit`).
Codex has no hook layer, so `events` turns its JSON stream into ledger events under the
task's run id and the loop's parent (cycle 1 F7): a started command or file change is an
intent, its completion the outcome that answers it, and `close_open` answers what a killed
builder left open with an `interrupted` outcome; a summary carries the count of path-like
fragments or changed paths and the exit code, never a command's text (ADR-019 §4; the raw
stream is the payload). The reviewer of a Codex-built task is a Claude model through
`claude -p`, read-only (`kgme.review_io.reviewer_argv`), so the vendors differ.
Inputs: the task, its workspace, the main checkout, the stream text, the events state.
Outputs: argv, the request, events and the state they leave.
Side effects: one process group; its stream file.
"""

import json
import subprocess
from pathlib import Path

from kgme import events, loop
from kgme.crew import Task, unit
from kgme.hooks import guard

KINDS = {"command_execution": "tool:shell", "file_change": "tool:apply_patch"}


class CodexAdapter:
    name = "codex"

    def argv(self, task: Task, workspace: Path, main: Path | None = None) -> list[str]:
        """Pure: `codex exec --json` fenced to the workspace alone; the prompt on stdin (`-`)."""
        writable = json.dumps([str(workspace)])
        argv = [
            "codex", "exec", "--json", "--skip-git-repo-check", "-C", str(workspace),
            "-s", "workspace-write", "-c", "approval_policy=never",
            "-c", f"sandbox_workspace_write.writable_roots={writable}",
            "-c", "sandbox_workspace_write.network_access=false",
        ]  # fmt: skip
        if task.model:
            argv += ["-m", task.model]
        return argv + ["-"]

    def request(self, task: Task, handoff_path: str, findings: str = "", main: str = "") -> str:
        """Pure: the builder's instruction: the task, its Outputs, its acceptance check, and
        on a fix cycle the findings to answer; it builds and writes its dispositions; the
        supervisor stages, gates, reviews and commits (git is read-only for it, F3)."""
        text = (
            f"You are the builder of task {task.name} of {task.handoff} ({handoff_path}) in KGME, "
            f"in this worktree on branch crew/{task.handoff}/{task.name}. Read AGENTS.md first. "
            f"Write only these Outputs: {', '.join(task.outputs)} (and tests/, logs/scratch/). "
            f"Acceptance check: `{task.acceptance}`, red now, green when you are done. "
            f"{task.description}\nWhen done, stop: the supervisor stages your Outputs, gates, "
            "reviews and commits (git is read-only for you here). Do not push, run the reviewer, "
            "or touch any other path. Write logs/scratch/dispositions.md: one line per finding "
            "you answered, or 'first cycle'.\n"
        )
        if findings:
            text += f"\nFindings of the previous cycle, to fix or dispute:\n{findings}\n"
        return text

    def start(
        self,
        task: Task,
        workspace: Path,
        out: Path,
        env: dict,
        handoff_path: str = "",
        main: Path | None = None,
        findings: str = "",
    ) -> subprocess.Popen:
        """Effect: the builder as its own process group."""
        clean = {k: v for k, v in env.items() if not k.startswith("CLAUDE")}
        return loop.start_builder(
            self.argv(task, workspace, main), workspace, out, clean,
            self.request(task, handoff_path, findings),
        )  # fmt: skip

    def events(
        self, text: str, run: str, parent: str | None, state: dict | None
    ) -> tuple[list[dict], dict]:
        """Pure: the ledger events for the stream lines after those `state` already read, and
        the new state: a started command or file change is an intent keyed by its item id, a
        completion the outcome answering it (an intent first when no start was seen)."""
        state = dict(state or {"lines": 0, "open": {}, "done": []})
        found: list[dict] = []
        # a record is complete only with its newline: an unfinished last line is left for the
        # next poll, never skipped (review cycle 2 F7)
        complete = text if text.endswith("\n") else text[: text.rfind("\n") + 1]
        lines = complete.splitlines()
        for line in lines[state["lines"] :]:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict):
                continue
            item = record.get("item") or {}
            job = KINDS.get(str(item.get("type", "")))
            if not job or record.get("type") not in ("item.started", "item.completed"):
                continue
            key = str(item.get("id") or f"{job}:{len(state['done']) + len(state['open']) + 1}")
            if record["type"] == "item.started" and key not in state["open"]:
                intent = self._intent(item, job, key, run, parent)
                state["open"][key] = intent["id"]
                found.append(intent)
                continue
            if record["type"] == "item.completed":
                if key in state["done"]:
                    continue
                ref = state["open"].pop(key, None)
                if ref is None:
                    intent = self._intent(item, job, key, run, parent)
                    found.append(intent)
                    ref = intent["id"]
                found.append(self._outcome(item, job, key, run, parent, ref))
                state["done"].append(key)
        state["lines"] = len(lines)
        return found, state

    def close_open(self, state: dict | None, run: str, parent: str | None) -> list[dict]:
        """Pure: an `interrupted` outcome for every intent still open when the builder ended."""
        found = []
        for key, ref in dict((state or {}).get("open", {})).items():
            found.append(
                events.make_event(
                    source="codex",
                    actor="codex.exec",
                    kind="outcome",
                    run_id=run,
                    parent=parent,
                    job="tool:shell",
                    key=key,
                    ref=ref,
                    status="error",
                    class_="transient",
                    summary="interrupted: the builder ended before the call did",
                )  # fmt: skip
            )
        if state is not None:
            state["open"] = {}
        return found

    def kill(self, proc: subprocess.Popen, grace: float) -> None:
        """Effect: SIGTERM to the group, SIGKILL after `grace`."""
        loop.kill_group(proc, grace)

    @staticmethod
    def _summary(item: dict, job: str) -> str:
        if job == "tool:apply_patch":
            return f"apply_patch {len(item.get('changes') or [])} paths changed"
        count = len(guard.fragments(str(item.get("command", ""))))
        return f"shell {count} path-like fragments examined"

    def _intent(self, item: dict, job: str, key: str, run: str, parent: str | None) -> dict:
        return events.make_event(
            source="codex", actor="codex.exec", kind="intent", run_id=run, parent=parent,
            job=job, key=key, summary=self._summary(item, job),
        )  # fmt: skip

    def _outcome(
        self, item: dict, job: str, key: str, run: str, parent: str | None, ref: str
    ) -> dict:
        code = item.get("exit_code")
        failed = job == "tool:shell" and code not in (0, None)
        status = "error" if failed else "ok"
        word = f"exit {code}" if job == "tool:shell" else "applied"
        return events.make_event(
            source="codex", actor="codex.exec", kind="outcome", run_id=run, parent=parent,
            job=job, key=key, ref=ref, status=status, class_="advisory" if failed else None,
            summary=f"{job.removeprefix('tool:')} {status} {word}",
        )  # fmt: skip


def review_unit(task: Task) -> str:
    """Pure: the review unit a Codex task's cycles are keyed by."""
    return unit(task.handoff, task.name)
