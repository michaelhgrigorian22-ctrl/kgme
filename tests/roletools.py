"""Helpers shared by the role registry tests (`tests/test_roles_*.py`, HANDOFF-0071).

Purpose: a committed fixture checkout holding this repository's level templates, profiles and
role templates, one skill, and the roles a test names, each with a rubric; the role pass run
over it; settings for a launch whose `claude` is replaced by a recorder.
Inputs: `tmp_path`; this repository's `control/policy/` and `roles/templates/`.
Outputs: paths, role texts, findings, settings.
Side effects: repositories under `tmp_path`; nothing is launched.
"""

import json
import shutil
import subprocess
from pathlib import Path

from kgme import config, lint, paths, roles_io

ROOT = paths.root()
SETTINGS = config.read_config()
RUBRIC = (
    "# Rubric: {id}\n\n## Dimensions\n"
    "- `intent` (gate): the end matches the goal the run stated first.\n"
    "- `context` (gate): the run read what the task needed before acting.\n"
    "- `outputs`: the run wrote only where it was told.\n"
)
SKILL = "---\nname: {name}\ndescription: a fixture skill.\n---\n\n# {name}\n"


def run_git(repo: Path, *argv: str) -> None:
    """Effect: one git command in `repo`, as a throwaway identity; raises on failure."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True,
    )  # fmt: skip


def role_text(department: str, name: str, **fields: object) -> str:
    """Pure: a lint-clean `tight` role's TOML with `fields` overriding; a None field is left out."""
    data: dict[str, object] = {
        "id": f"{department}.{name}",
        "department": department,
        "purpose": "A fixture role.",
        "kind": "worker",
        "skill": "kgme-fixture",
        "model": "inherit",
        "level": "tight",
        "slice": [],
        "tools": ["Read", "Grep"],
        "tier_max": 2,
        "escalates_to": "michou",
        "rubric": f"roles/{department}/rubrics/{name}.md",
        **fields,
    }
    lines = [f"{key} = {json.dumps(value)}" for key, value in data.items() if value is not None]
    return "\n".join(lines) + "\n"


def write_file(base: Path, rel: str, text: str) -> None:
    """Effect: `text` at `base/rel`, its folders made."""
    (base / rel).parent.mkdir(parents=True, exist_ok=True)
    (base / rel).write_text(text)


def write_repo(tmp_path: Path, roles_: dict[str, str] | None = None) -> Path:
    """Effect: a committed checkout with the level templates, the profiles, the role
    templates, one skill, and `roles_` ({"dept/name": toml text}) each with a rubric; its
    resolved path."""
    base = tmp_path / "repo"
    for folder in ("control/policy/sessions", "control/policy/profiles", "roles/templates"):
        shutil.copytree(ROOT / folder, base / folder)
    write_file(base, "skills/kgme-fixture/SKILL.md", SKILL.format(name="kgme-fixture"))
    for key, text in (roles_ or {}).items():
        department, name = key.split("/")
        write_file(base, f"roles/{department}/{name}.toml", text)
        write_file(base, f"roles/{department}/rubrics/{name}.md", RUBRIC.format(id=key))
    for empty in ("memory", "docs"):  # the lint roots `kgme lint --base` walks
        (base / empty).mkdir()
    run_git(base, "init", "-q", "-b", "main")
    run_git(base, "add", "-A")
    run_git(base, "commit", "-q", "-m", "fixture")
    return base.resolve()


def read_role_findings(base: Path, index: bool = False) -> list[lint.Finding]:
    """Effect: the role pass over `base`: the index's roles when `index`, else the tree's."""
    return roles_io.read_findings(base, SETTINGS, index=index)


def read_blocking(base: Path, index: bool = False) -> list[str]:
    """Effect: the role pass's blocking findings over `base`, as lines."""
    return [f.line() for f in read_role_findings(base, index) if f.cls == "blocking"]


def make_run_settings() -> dict:
    """Pure: this repository's settings with a fixed builder model and no mods."""
    return {**SETTINGS, "models": {**SETTINGS["models"], "builder": "claude-opus-5-5"}, "mods": {}}
