"""`kgme session`, the pure half: a level's command line and its settings (HANDOFF-0047).

Purpose: what `kgme.session` launches, computed from values alone (ADR-015; review cycle 2 F8):
the levels and their permission modes, the template's placeholders made absolute
(`render`), the extra arguments a level takes (`check_extra`), the command line
(`build_argv`), and the main checkout's policy carried into the run copy (`carry_policy`,
review cycle 2 F1, two arbiters, option C). Nothing here reads or writes.
Inputs: templates and policies as dicts, resolved paths, the model, the caps, extra arguments.
Outputs: dicts, argv lists, sha256 digests; `ValueError` for an argument a level refuses.
Side effects: none.
"""

import hashlib
import json
import os
from pathlib import Path

LEVELS = {"tight": "plan", "work": "auto", "loose": "dontAsk"}
TEMPLATES = Path("control") / "policy" / "sessions"
OUTPUTS = "{outputs}"
EDIT_OUTPUTS = "Edit({outputs})"
# HANDOFF-0048 amendment 2: a loose builder in a KGME workspace stages and commits by pathspec,
# one rule per Outputs entry (review cycle 1 F2): `git add -- <path>` exactly, and
# `git commit --only <path> -m ...`, the path before the message so a prefix rule pins it; a
# folder entry takes the folder's prefix. `git add -A`, `git commit -a`, a bare `git commit`
# and every other git write match no rule and are refused by the level's dontAsk mode.
GIT_ADD_OUTPUTS = "Bash(git add {outputs})"
GIT_COMMIT_OUTPUTS = "Bash(git commit {outputs})"
PLACEHOLDERS = (OUTPUTS, EDIT_OUTPUTS, GIT_ADD_OUTPUTS, GIT_COMMIT_OUTPUTS)
# The only extra arguments a level takes, with how many values each: output shape, never
# permission, settings, model, workspace, or caps (review cycle 1 F2).
EXTRA_FLAGS = {"--verbose": 0, "--output-format": 1, "--input-format": 1}
AUTHORS = ("cowork", "michou")
PROJECT_DIR = "$CLAUDE_PROJECT_DIR"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(
    template: dict, repo: Path, tmp: Path, entries: tuple[str, ...] = (), main: Path | None = None
) -> dict:
    """Pure: the template with its placeholders filled from the resolved `repo`, `tmp` and
    `main` (the main checkout, whose code a workspace's `kgme review` runs; HANDOFF-0048
    amendment 2) the caller gives (review cycle 1 F8). An `{outputs}` or `Edit({outputs})`
    element with no entries (no handoff) is refused: a level that confines writes must know
    where."""

    def value(item):
        if isinstance(item, dict):
            return {key: value(v) for key, v in item.items()}
        if isinstance(item, list):
            out: list = []
            for element in item:
                if element not in PLACEHOLDERS:
                    out.append(value(element))
                    continue
                if not entries:
                    raise ValueError("this level confines writes to a handoff's Outputs")
                for entry in entries:
                    path = os.path.normpath(repo / entry.rstrip("/"))
                    folder = entry.endswith("/") or not Path(entry).suffix
                    relative = os.path.normpath(entry.rstrip("/"))
                    if element == OUTPUTS:
                        out.append(path)
                    elif element == EDIT_OUTPUTS:
                        out.append(f"Edit(/{path}/**)" if folder else f"Edit(/{path})")
                    else:
                        out.extend(git_rules(element, (relative, path), folder))
            return out
        if isinstance(item, str):
            filled = item.replace("{repo}", str(repo)).replace("{tmp}", str(tmp))
            return filled.replace("{main}", str(main if main is not None else repo))
        return item

    return value(template)


def git_rules(element: str, forms: tuple[str, ...], folder: bool) -> list[str]:
    """Pure: the `git add` or `git commit` rules of one Outputs entry, in each of `forms`
    (the path as written and absolute): a file is named exactly, a folder by its prefix."""
    rules = []
    for form in forms:
        if element == GIT_ADD_OUTPUTS:
            rules.append(f"Bash(git add -- {form}/*)" if folder else f"Bash(git add -- {form})")
        else:
            tail = f"{form}/*" if folder else f"{form} -m *"
            rules.append(f"Bash(git commit --only {tail})")
    return rules


def check_extra(extra: list[str]) -> None:
    """Pure: `ValueError` for any extra argument outside `EXTRA_FLAGS` (or its value)."""
    index = 0
    while index < len(extra):
        word = extra[index]
        if word.startswith("-"):
            name = word.split("=", 1)[0]
            if name not in EXTRA_FLAGS:
                raise ValueError(f"{name} is not allowed after a level; it could widen it")
            index += 0 if "=" in word else EXTRA_FLAGS[name]
        index += 1


def build_argv(
    level: str,
    settings_file: Path,
    model: str,
    caps: dict,
    extra: list[str],
    claude_md: Path | None = None,
    plugin_dirs: tuple[Path, ...] = (),
) -> list[str]:
    """Pure: the `claude` command line of `level`. `loose` loads no project settings
    (`--setting-sources local`, ADR-022 addendum of 2026-10-21: the project's allows would merge
    into its pinned list), takes the committed `CLAUDE.md` as `claude_md`, and adds the headless
    hard stops; `tight` and `work` keep `project,local`. Each of `plugin_dirs` is a mod the
    level loads (`--plugin-dir`, HANDOFF-0059); `loose` takes none (ADR-024)."""
    if level == "loose" and plugin_dirs:
        raise ValueError("loose loads no mod (ADR-024)")
    sources = "local" if level == "loose" else "project,local"
    argv = ["claude", "--setting-sources", sources, "--settings", str(settings_file)]
    argv += ["--permission-mode", LEVELS[level], "--model", model]
    if level == "loose":
        argv += ["-p", "--permission-prompts", "none", "--max-turns", str(caps["max_turns"])]
        argv += ["--max-budget-usd", str(caps["max_budget_usd"])]
    if claude_md is not None:
        argv += ["--append-system-prompt-file", str(claude_md)]
    for folder in plugin_dirs:
        argv += ["--plugin-dir", str(folder)]
    return argv + list(extra)


def carry_policy(rendered: dict, policy: dict, main: Path) -> tuple[dict, str]:
    """Pure: `rendered` with the main checkout's policy carried in: its hooks, each command's
    `$CLAUDE_PROJECT_DIR` made the main checkout's absolute path, and its deny rules after the
    level's own, once each; `disableAllHooks` false. Returns it and the carried policy's sha256."""

    def pinned(hook: dict) -> dict:
        command = str(hook.get("command", "")).replace(f'"{PROJECT_DIR}"', str(main))
        return {**hook, "command": command.replace(PROJECT_DIR, str(main))}

    hooks = {
        event: [{**group, "hooks": [pinned(h) for h in group.get("hooks", [])]} for group in groups]
        for event, groups in (policy.get("hooks") or {}).items()
    }
    deny = list(dict.fromkeys(
        [*(rendered.get("permissions") or {}).get("deny", []),
         *(policy.get("permissions") or {}).get("deny", [])]
    ))  # fmt: skip
    carried = {**rendered, "hooks": hooks, "disableAllHooks": False}
    carried["permissions"] = {**(rendered.get("permissions") or {}), "deny": deny}
    digest = sha256_text(json.dumps({"hooks": hooks, "deny": deny}, sort_keys=True))
    return carried, digest
