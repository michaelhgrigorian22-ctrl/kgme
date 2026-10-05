"""Helpers shared by the hook tests (`tests/test_guard_decisions.py`, `tests/test_hooks.py`).

Purpose: run a hook entry point as Claude Code would, build a hook payload, decide a call with
the real lists from `kgme.toml`, and plant a probe script in the test scratch directory.
Inputs: the repository's `kgme.toml`.
Outputs: functions and the lists the guard reads.
Side effects: `run_hook` spawns a subprocess writing to the test streams; `probe_script` writes
under the gitignored test scratch directory.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from kgme import config, paths
from kgme.hooks import guard

ROOT = paths.root()
SETTINGS = config.read_config()
BLOCKLIST = [paths.resolve(p) for p in SETTINGS["hooks"]["blocklist"] if not p.startswith("**/")]
PATTERNS = [p[3:] for p in SETTINGS["hooks"]["blocklist"] if p.startswith("**/")]
TEST_SCRATCH = paths.scratch_test_dir(SETTINGS)


def run_hook(module: str, payload: object) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", module, "--test-streams"],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )


def payload(tool: str, session: str, **tool_input: object) -> dict:
    digest = hashlib.sha256(json.dumps([tool, tool_input], sort_keys=True).encode()).hexdigest()
    return {
        "session_id": session,
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": f"toolu_{digest[:12]}",
        "cwd": str(ROOT),
        "hook_event_name": "PreToolUse",
    }


def decide(tool: str, tool_input: dict, **overrides: object) -> guard.Decision:
    kwargs: dict = dict(
        cwd=ROOT, repo_root=ROOT, blocklist=BLOCKLIST, name_patterns=PATTERNS, allow_outside=[]
    )
    kwargs.update(overrides)
    return guard.decide(tool, tool_input, **kwargs)


def probe_script(name: str, text: str) -> Path:
    target = TEST_SCRATCH / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    return target
