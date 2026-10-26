"""Helpers shared by the `kgme session` tests (`tests/test_session.py`, `test_session_policy.py`).

Purpose: a committed fixture checkout with the level templates, project settings that run the
guard, and handoffs; a worktree of it outside it, as KGME's workspaces are; one launch with
`claude` replaced by a recorder.
Inputs: `tmp_path`; this repository's applied templates (or the drafts before they were).
Outputs: paths, settings, the recorded launch.
Side effects: repositories and worktrees under `tmp_path`; nothing is launched.
"""

import json
import shutil
import subprocess
from pathlib import Path

from kgme import config, paths, session

ROOT = paths.root()
SETTINGS = config.read_config()
DRAFTS = ROOT / "logs" / "scratch" / "handoff-0047"
APPLIED = ROOT / session.TEMPLATES
TOY = (
    "---\nid: HANDOFF-9047\nstatus: open\nfrom: michou\n---\n\n"
    "## Outputs\n`kgme/toy.py`, `docs/audit/toy.md`\n"
)
GUARDED = {"hooks": {"PreToolUse": [{"matcher": "", "hooks": [
    {"type": "command", "command": '"$CLAUDE_PROJECT_DIR"/control/hooks/pre_tool_guard.sh'}
]}]}}  # fmt: skip


def run_git(repo: Path, *argv: str) -> None:
    """Effect: one quiet git command in `repo`, with a fixed identity."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True,
    )  # fmt: skip


def write_checkout(tmp_path: Path, handoffs: dict | None = None) -> tuple[Path, dict]:
    """Effect: a committed git checkout with the three templates, project settings that run
    the guard, and handoffs (the toy by default); settings with the model and the caps."""
    base = tmp_path / "repo"
    (base / session.TEMPLATES).mkdir(parents=True)
    source = APPLIED if (APPLIED / "loose.json").is_file() else DRAFTS
    for level in session.LEVELS:
        shutil.copy(source / f"{level}.json", base / session.TEMPLATES / f"{level}.json")
    (base / "CLAUDE.md").write_text("# Fixture constitution\n")  # a loose run carries it (F18)
    (base / ".claude").mkdir()
    (base / ".claude" / "settings.json").write_text(json.dumps(GUARDED))
    for rel, text in (handoffs or {"docs/handoff/toy.md": TOY}).items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)
    run_git(base, "init", "-q", "-b", "main")
    run_git(base, "add", "-A")
    run_git(base, "commit", "-q", "-m", "fixture")
    settings = {
        **SETTINGS,
        "models": {**SETTINGS["models"], "builder": "claude-opus-5-5"},
        "sessions": {"max_turns": 60, "max_budget_usd": 15},
        "mods": {},  # a fixture checkout holds no mod folder; a test that loads one sets it
    }
    return base.resolve(), settings


def write_workspace(base: Path, tmp_path: Path) -> Path:
    """Effect: a worktree of `base` outside it, as KGME's workspaces are (HANDOFF-0048)."""
    workspace = tmp_path / "workspace"
    run_git(base, "worktree", "add", "-q", "--detach", str(workspace))
    return workspace.resolve()


def launched(base: Path, settings: dict, level: str, handoff=None, extra=()) -> tuple:
    calls = []
    code = session.run_session(
        level, handoff, list(extra), base, settings, execute=lambda *a: calls.append(a)
    )
    return code, calls
