"""The vault reader, effects half of the validator: which files to lint, and their text.

Purpose: walk the roots `kgme.toml` `[lint]` names, skip the exempt paths the schema lists,
and hand each note's text to `kgme/lint.py` once, however the roots overlap.
Inputs: root directories, exempt paths, directory names to skip, the repository root.
Outputs: `(repo-relative path, text)` pairs, roots in the given order, sorted within each.
Side effects: reads files. Writes nothing. A root that is not a directory raises
`FileNotFoundError`: a mistyped root must not lint nothing and report success.
"""

from pathlib import Path


def is_exempt(path: Path, exempt: list[Path], skip_dirs: tuple[str, ...]) -> bool:
    """True if `path` is an exempt file, lies under an exempt directory, or has a skipped part."""
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
