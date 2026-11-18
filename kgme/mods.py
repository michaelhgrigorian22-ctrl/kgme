"""Mods (HANDOFF-0059, ADR-024): what a level loads, and the check `make check` runs on `mods/`.

Purpose: KGME's own Claude Code mods live under `mods/<name>/`, one folder each. A level loads
the mods `kgme.toml [mods]` names for it, each as `--plugin-dir`; `loose` and `cheap` load
none, whatever the table says (an unattended run draws no UI and gets no process surface it
did not have). `make check` runs `claude plugin validate --json` on every folder under
`mods/` and holds what it lists (the events each module hooks, the `$` nouns it calls) to
`kgme.toml [mods.allows]`, the listing the mod's handoff names: anything more is blocking, and
so is a folder with no entry, a failed validation, or a mod folder when `claude` cannot be run.
The committed policy (hooks, deny list, guard) stays the boundary; no mod replaces it.
Inputs: the parsed `kgme.toml`; the folders under `mods/`; `claude plugin validate --json`.
Outputs: the plugin folders a level passes; findings, one line each, and an exit code.
Side effects: `run_check` runs `claude plugin validate` once per folder. Nothing is written.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from kgme import config

MODS = "mods"
NO_MODS = ("loose", "cheap")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MATCHER = re.compile(r"\{[^}]*\}")
# a note validate writes after a hooked event since 2026-11-17: `(default matcher key: plugin)`
NOTE = re.compile(r"\s*\([^)]*\)")


def level_mods(level: str, settings: dict) -> list[str]:
    """Pure: the mods `kgme.toml [mods]` names for `level`, none for `loose` and `cheap`;
    `ValueError` for a value that is not a list of plain names."""
    if level in NO_MODS:
        return []
    names = settings.get("mods", {}).get(level, [])
    if not isinstance(names, list) or not all(isinstance(n, str) and NAME.match(n) for n in names):
        raise ValueError(f"kgme.toml [mods] {level} must be a list of mod folder names")
    return list(names)


def listing(report: dict) -> set[str]:
    """Pure: what a `claude plugin validate --json` report says the modules hook and call: each
    event name without its matcher or its trailing note (`ui.render`), and each `$` call by
    its noun (`$.ui`)."""
    found: set[str] = set()
    for content in report.get("contents", []):
        for note in content.get("notes", []):
            _, _, hooked = note.partition(" hooks: ")
            if hooked:
                events = NOTE.sub("", MATCHER.sub("", hooked))
                found |= {e.strip() for e in events.split(",") if e.strip()}
            _, _, called = note.partition(" calls: ")
            if called:
                found |= {
                    ".".join(c.strip().split(".")[:2]) for c in called.split(",") if c.strip()
                }
    return found


def errors(report: dict) -> list[str]:
    """Pure: the validation errors of a report, its manifest's and its contents'."""
    parts = [report.get("manifest", {}), *report.get("contents", [])]
    found = [
        e.get("message", str(e)) if isinstance(e, dict) else str(e)
        for p in parts
        for e in p.get("errors", [])
    ]
    return found or ([] if report.get("success") else ["validation failed"])


def check_mod(name: str, report: dict, allows: dict) -> list[str]:
    """Pure: the blocking findings for one mod folder, from its report and `[mods.allows]`."""
    problems = [f"claude plugin validate: {e}" for e in errors(report)]
    allowed = allows.get(name)
    if not isinstance(allowed, list):
        return problems + ["no kgme.toml [mods.allows] entry names what its handoff allows"]
    extra = sorted(listing(report) - set(allowed))
    if extra:
        problems.append(f"hooks or calls its handoff did not name: {', '.join(extra)}")
    return problems


def read_folders(base: Path) -> list[Path]:
    """Effect: the entries under `mods/`, hidden ones skipped; none through a symlinked
    `mods/` (`read_mod_problem` names it)."""
    root = base / MODS
    if root.is_symlink() or not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if not p.name.startswith("."))


def read_mod_problem(base: Path, folder: Path) -> str | None:
    """Effect: why `folder` may not be loaded or validated as a mod, or None. `mods/` and the
    folder are no symlink, the folder is a mod (`.claude-plugin/plugin.json`), and it
    resolves inside the repository (review cycle 1 F1: a symlinked `mods/` passed)."""
    if (base / MODS).is_symlink():
        return f"{MODS}/ is a symlink; no mod is loaded through one"
    if folder.is_symlink():
        return "a symlink; no mod is loaded through one"
    if not (folder / ".claude-plugin" / "plugin.json").is_file():
        return "not a mod folder (no .claude-plugin/plugin.json)"
    if not folder.resolve().is_relative_to(base.resolve()):
        return "resolves outside the repository"
    return None


def read_report(folder: Path, claude: str) -> dict:
    """Effect: `claude plugin validate --json <folder>`, parsed; a report that will not parse
    is a failed one."""
    done = subprocess.run(
        [claude, "plugin", "validate", "--json", str(folder)],
        capture_output=True, text=True, timeout=120, check=False,
    )  # fmt: skip
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"success": False, "manifest": {"errors": [done.stderr.strip() or "no JSON report"]}}


def run_check(base: Path, settings: dict, claude: str | None = None) -> int:
    """The `make check` step: every mod folder validated and held to its allowed listing.
    `claude` is the executable; None looks it up on PATH, and "" means none is installed."""
    folders = read_folders(base)
    claude = shutil.which("claude") if claude is None else claude
    allows = settings.get("mods", {}).get("allows", {})
    found: list[str] = []
    if (base / MODS).is_symlink():
        found.append(f"{MODS}: {read_mod_problem(base, base / MODS)}")
    for folder in folders:
        rel = folder.relative_to(base).as_posix()
        problem = read_mod_problem(base, folder)
        if problem:
            found.append(f"{rel}: {problem}")
        elif not NAME.match(folder.name):
            found.append(f"{rel}: a mod folder's name is lowercase letters, digits and dashes")
        elif not claude:
            found.append(f"{rel}: claude is not on PATH, so the mod cannot be validated")
        else:
            report = read_report(folder, claude)
            found += [f"{rel}: {p}" for p in check_mod(folder.name, report, allows)]
    for line in found:
        print(f"{line} [blocking]")
    print(f"kgme mods: {len(folders)} mod folders, {len(found)} blocking")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(run_check(config.config_path().parent, config.read_config()))
