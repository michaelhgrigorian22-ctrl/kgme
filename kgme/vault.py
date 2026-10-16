"""The vault reader, effects half of the validator: which files to lint, and their text.

Purpose: walk the roots `kgme.toml` `[lint]` names, skip the exempt paths the schema lists,
and hand each note's text to `kgme/lint.py` once, however the roots overlap.
Inputs: root directories, exempt paths, directory names to skip, the repository root.
Outputs: `(repo-relative path, text)` pairs, roots in the given order, sorted within each.
Side effects: reads files. Writes nothing. A root that is not a directory raises
`FileNotFoundError`: a mistyped root must not lint nothing and report success.
`read_coherence_inputs` also reads what `kgme.coherence` checks: the handoffs, the live
documents, every path in the working tree, and, kept apart, the file list of the `design`
branch through one `git ls-tree` (HANDOFF-0049).
"""

import os
import subprocess
from pathlib import Path

from kgme.frontmatter import parse_frontmatter

SKIP_WALK = (".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "node_modules")
LIVE_SINGLE = ("CLAUDE.md", "README.md", "docs/README.md", "docs/STATUS.md")
LIVE_FOLDERS = ("docs/readers", "docs/plans")


def is_exempt(path: Path, exempt: list[Path], skip_dirs: tuple[str, ...]) -> bool:
    """True if `path` is an exempt file, lies under an exempt directory, has a skipped part, or
    is a `README.md`: the index of its folder, not a note (schema v1.4, HANDOFF-0041)."""
    if path.name == "README.md":
        return True
    if any(part in skip_dirs for part in path.parts):
        return True
    for root in exempt:
        if path == root or root in path.parents:
            return True
    return False


def read_notes(
    roots: list[Path], exempt: list[Path], skip_dirs: tuple[str, ...], repo_root: Path
) -> list[tuple[str, str]]:
    """Every `.md` under `roots` minus the exemptions, each file once, as repo-relative path
    and text."""
    notes: list[tuple[str, str]] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            raise FileNotFoundError(f"lint root is not a directory: {root}")
        for path in sorted(root.rglob("*.md")):
            resolved = path.resolve()
            if resolved in seen or is_exempt(path, exempt, skip_dirs):
                continue
            seen.add(resolved)
            try:
                rel = path.relative_to(repo_root).as_posix()
            except ValueError:
                rel = path.as_posix()
            notes.append((rel, path.read_text(encoding="utf-8", errors="replace")))
    return notes


def read_existing_paths(base: Path) -> frozenset[str]:
    """Every repository-relative file and directory in this checkout's working tree."""
    found: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_WALK]
        here = Path(dirpath).relative_to(base).as_posix()
        if here != ".":
            found.add(here)
        for name in filenames:
            found.add(name if here == "." else f"{here}/{name}")
    return frozenset(found)


def read_design_paths(base: Path) -> frozenset[str]:
    """Every file and directory on the `design` branch, kept apart from this checkout's, so a
    path the design track holds resolves only where a document points into its folders
    (review cycle 1 F3); empty when there is no such branch."""
    listed = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "design"],
        cwd=base,
        capture_output=True,
        text=True,
        check=False,
    )
    found: set[str] = set()
    for name in listed.stdout.splitlines() if listed.returncode == 0 else []:
        parts = name.split("/")
        found.update("/".join(parts[: i + 1]) for i in range(len(parts)))
    return frozenset(found)


def read_handoffs(base: Path) -> list[tuple[str, dict, str]]:
    """Every handoff under `docs/handoff/` as `(repo-relative path, frontmatter, body)`; one
    whose frontmatter does not parse is the schema check's finding, not this one's."""
    handoffs: list[tuple[str, dict, str]] = []
    for path in sorted((base / "docs" / "handoff").rglob("*.md")):
        if path.name == "README.md":
            continue
        try:
            data, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        handoffs.append((path.relative_to(base).as_posix(), data, body))
    return handoffs


def read_coherence_inputs(
    base: Path,
) -> tuple[list[tuple[str, dict, str]], list[tuple[str, str]], frozenset[str], str, frozenset[str]]:
    """The handoffs, the live documents (`CLAUDE.md`, the two READMEs, `STATUS.md`, the
    readers, the plans, the open handoffs), this checkout's paths, `CLAUDE.md`'s text, and
    the `design` branch's paths, in the order `kgme.coherence.check_tree` takes them."""
    handoffs = read_handoffs(base)
    rels = [rel for rel in LIVE_SINGLE if (base / rel).is_file()]
    for folder in LIVE_FOLDERS:
        rels += [p.relative_to(base).as_posix() for p in sorted((base / folder).glob("*.md"))]
    rels += [rel for rel, data, _ in handoffs if data.get("status") == "open"]
    documents = [(rel, (base / rel).read_text(encoding="utf-8")) for rel in rels]
    claude = (base / "CLAUDE.md").read_text(encoding="utf-8")
    return handoffs, documents, read_existing_paths(base), claude, read_design_paths(base)
