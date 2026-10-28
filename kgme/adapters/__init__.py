"""The builder adapters (HANDOFF-0048 §2): one interface, any model as builder.

Purpose: `kgme loop` and `kgme crew` start a task's builder through an adapter and never
through a harness's own command line: `start(task, workspace, out, env)` launches the builder
as its own process group with its output streamed to `out`; `events(text, run, parent)`
turns what the stream says into ledger events for the harness that has no hook layer
(Codex), and nothing for the one whose hooks ledger every call (Claude Code); `kill(proc,
grace)` ends the group. `kgme.adapters.claude` is `kgme session loose --handoff <id> --task
<task>` from the workspace; `kgme.adapters.codex` is `codex exec --json` with the worktree as
its only writable root. An adapter builds at `loose` only after its conformance cells pass
(`tests/policy/test_agents_adapters.py`).
Inputs: a task, its workspace, the main checkout.
Outputs: argv lists, requests, events.
Side effects: `start` spawns; `kill` signals.
"""

from kgme.adapters.claude import ClaudeAdapter
from kgme.adapters.codex import CodexAdapter

ADAPTERS = {"claude": ClaudeAdapter, "codex": CodexAdapter}


def read_adapter(harness: str):
    """Pure: the adapter class of a harness name; `ValueError` for an unknown one."""
    if harness not in ADAPTERS:
        raise ValueError(f"no adapter for harness {harness!r}; one of {', '.join(ADAPTERS)}")
    return ADAPTERS[harness]()
