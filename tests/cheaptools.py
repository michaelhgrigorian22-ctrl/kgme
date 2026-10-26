"""Helpers for the cheap lane's tests (HANDOFF-0053; moved out of `tests/test_cheap.py` by
HANDOFF-0060 §3, unchanged).

Purpose: the fixture checkout with the cheap template, the stand-in for `claude`, the session
notes, one git command's output, and the real guard run in a folder.
Inputs: `tmp_path`; this checkout's code.
Outputs: paths, settings, notes, text, completed processes.
Side effects: repositories under `tmp_path`; `run_guard_in` runs the guard on the test streams.
"""

import json
import subprocess
from pathlib import Path

from sessiontools import run_git, write_checkout

from kgme import cheap, ledger, paths, session

ROOT = paths.root()


DRAFT = ROOT / "logs" / "scratch" / "handoff-0053" / "cheap.json"


APPLIED = ROOT / session.TEMPLATES / cheap.TEMPLATE


RED = "python3 tests/test_toy.py"


TOY_TEST = (
    "import sys\nfrom pathlib import Path\n"
    "sys.exit(0 if 'a + b' in Path('kgme/toy.py').read_text() else 1)\n"
)


def write_cheap_checkout(tmp_path: Path) -> tuple[Path, dict]:
    """Effect: the fixture checkout plus the cheap template, a toy bug and its red test,
    private `memory/` and `logs/` files and templates; settings with the cheap lane on."""
    base, settings = write_checkout(tmp_path)
    template = APPLIED if APPLIED.is_file() else DRAFT
    (base / session.TEMPLATES / cheap.TEMPLATE).write_text(template.read_text())
    files = {
        "kgme/toy.py": "def add(a, b):\n    return a - b\n",
        "tests/test_toy.py": TOY_TEST,
        "memory/notes/private.md": "private\n",
        "memory/templates/daily.md": "# Daily\n",
        "logs/ledger/2026-10.jsonl": "",
        ".gitignore": "logs/scratch/\nlogs/ledger-test/\n.venv/\n",
    }
    for rel, text in files.items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)
    run_git(base, "add", "-A")
    run_git(base, "commit", "-q", "-m", "the cheap fixture")
    settings = {
        **settings,
        "models": {
            **settings["models"],
            "cheap": "toy-model:cloud",
            "cheap_provider": "ollama-cloud",
        },
        "providers": {"anthropic": "tier2", "ollama-cloud": "code"},
        "paths": {**settings["paths"], "work_dir": str(tmp_path / "work")},
    }
    return base, settings


def run_fixing(argv, cwd, env, **_):
    """A stand-in `claude`: fixes the toy in the export it is started in, as a session would."""
    (Path(cwd) / "kgme" / "toy.py").write_text("def add(a, b):\n    return a + b\n")
    reply = {"type": "result", "subtype": "success", "num_turns": 3, "result": "green"}
    return subprocess.CompletedProcess(argv, 0, json.dumps(reply), "")


def read_session_notes(base: Path, settings: dict) -> list[dict]:
    """Effect: the session notes in the fixture's ledger."""
    return [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]


def run_out(repo: Path, *argv: str) -> str:
    """Effect: one git command's stdout in `repo`."""
    return subprocess.run(
        ["git", *argv], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def run_guard_in(root: Path, tool: str, **tool_input: object) -> subprocess.CompletedProcess:
    """Effect: this checkout's real pre-tool guard, on the test streams, with
    `KGME_GUARD_ROOT` set to `root` and the call's `cwd` there."""
    import os
    import sys

    from hooktools import payload

    call = payload(tool, f"hooktest-cheap-{os.getpid()}", **tool_input) | {"cwd": str(root)}
    return subprocess.run(
        [sys.executable, "-P", "-m", "kgme.hooks.pre_tool_guard", "--test-streams"],
        input=json.dumps(call), capture_output=True, text=True, cwd=root, timeout=60,
        env=os.environ | {cheap.GUARD_ROOT_ENV: str(root)},
    )  # fmt: skip
