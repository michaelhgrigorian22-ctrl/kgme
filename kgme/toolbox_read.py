"""The toolbox checks' effects (ADR-020, HANDOFF-0044 §3): what they read from the tree.

Purpose: the half of `kgme/toolbox.py` that touches the disk, kept apart as ADR-015 asks
(review cycle 2 F7). It reads the registry, the schema's version, `uv.lock`, the imports of
`kgme/` and `cockpit/`, the cockpit's pages and the vendored files, and hands them to the
pure checks. A held path is refused before it is read when any component of it is a symlink
or it resolves outside the repository.
Inputs: a checkout's root.
Outputs: `kgme.lint.Finding` records.
Side effects: reads files; writes nothing.
"""

import ast
import hashlib
import tomllib
from pathlib import Path

from kgme.lint import Finding
from kgme.toolbox import (
    IMPORT_ROOTS,
    PENDING,
    REGISTRY,
    SCHEMA,
    SCHEMA_VERSION,
    SKILLS,
    VENDOR,
    Row,
    check_held,
    check_imports,
    check_lock,
    check_rows,
    check_scripts,
    folder_sha,
    held_problem,
    parse_rows,
)


def read_folder_sha(folder: Path) -> str | None:
    """Effect: `folder_sha` of a folder in the tree, None when it is not there. The caller
    has refused a folder holding a symlink (`read_link_problem`)."""
    if not folder.is_dir():
        return None
    files = [p for p in sorted(folder.rglob("*")) if p.is_file()]
    listing = [
        (p.relative_to(folder).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
        for p in files
    ]
    return folder_sha(listing)


def read_discovered(base: Path, root: str, pattern: str) -> tuple[list[Path], list[Finding]]:
    """Effect: the files matching `pattern` under `root` that may be read, and a blocking
    finding for each that may not: it is or passes through a symlink, or resolves outside
    the repository (`read_link_problem`). Nothing refused is read (review cycle 3 F8)."""
    readable: list[Path] = []
    refused: list[Finding] = []
    for path in sorted((base / root).rglob(pattern)):
        problem = read_link_problem(base, path)
        if problem:
            rel = path.relative_to(base).as_posix()
            message = f"{problem}; not read by the toolbox checks"
            refused.append(Finding(rel, "toolbox-link", "blocking", message))
        else:
            readable.append(path)
    return readable, refused


def read_imports(base: Path) -> tuple[dict[str, set[str]], list[Finding]]:
    """Effect: the top-level modules each Python file under `kgme/` and `cockpit/` imports
    (absolute imports only), from its syntax tree, and the files refused unread."""
    found: dict[str, set[str]] = {}
    refused: list[Finding] = []
    for root in IMPORT_ROOTS:
        paths, links = read_discovered(base, root, "*.py")
        refused += links
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            modules: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    modules.add(node.module.split(".")[0])
            found[path.relative_to(base).as_posix()] = modules
    return found, refused


def read_vendored(base: Path) -> list[str]:
    """Effect: every file under `cockpit/static/vendor/`, and every folder under `skills/`
    that is not KGME's own (`skills/kgme-*` are KGME's), as `skills/<name>/`."""
    found: list[str] = []
    vendor = base / VENDOR
    if vendor.is_dir():
        found += [p.relative_to(base).as_posix() for p in sorted(vendor.rglob("*")) if p.is_file()]
    skills = base / SKILLS
    if skills.is_dir():
        found += [
            f"{SKILLS}/{p.name}/"
            for p in sorted(skills.iterdir())
            if p.is_dir() and not p.name.startswith("kgme-")
        ]
    return found


def read_link_problem(base: Path, path: Path) -> str | None:
    """Effect: why `path` (a file or a folder and everything in it) may not be read: a
    component on the way to it is a symlink (review cycle 2 F4: `skills/alias -> memory/notes`
    made `skills/alias/x.md` look local), it is or holds a symlink, or it resolves outside
    the repository; None when it may. Nothing is read before this answers."""
    root = base.resolve()
    step = base
    for part in path.relative_to(base).parts:
        step = step / part
        if step.is_symlink():
            return f"{step.relative_to(base).as_posix()} is a symlink"
    members = [path, *(sorted(path.rglob("*")) if path.is_dir() else [])]
    for member in members:
        if member.is_symlink():
            return f"{member.relative_to(base).as_posix()} is a symlink"
        if not member.resolve().is_relative_to(root):
            return f"{member.relative_to(base).as_posix()} resolves outside the repository"
    return None


def read_held(base: Path, rows: list[Row]) -> tuple[dict[str, str | None], dict[str, str]]:
    """Effect: the sha256 of each repository path a row holds (None when it is not there),
    and the paths refused before any read, with why (review cycle 1 F4)."""
    shas: dict[str, str | None] = {}
    problems: dict[str, str] = {}
    for row in rows:
        place = row.cells["held"]
        if place == "uv.lock" or place.startswith("machine:") or PENDING.match(place):
            continue
        refused = held_problem(place)
        path = base / place
        if refused is None:
            refused = read_link_problem(base, path)
        if refused:
            problems[place] = refused
            continue
        if place.endswith("/"):
            shas[place] = read_folder_sha(path)
        else:
            shas[place] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return shas, problems


def read_lock(base: Path) -> dict | None:
    """Effect: `uv.lock`, parsed, or None when it is not there."""
    lock = base / "uv.lock"
    return tomllib.loads(lock.read_text(encoding="utf-8")) if lock.is_file() else None


def read_schema_version(base: Path) -> tuple[int, int] | None:
    """Effect: the schema's `version` (`1.7` as (1, 7)), or None when it cannot be read."""
    schema = base / SCHEMA
    found = SCHEMA_VERSION.search(schema.read_text(encoding="utf-8")) if schema.is_file() else None
    return (int(found.group(1)), int(found.group(2))) if found else None


def read_findings(base: Path) -> list[Finding]:
    """Effect: every toolbox finding for the checkout at `base`; a missing registry is one
    blocking finding."""
    registry = base / REGISTRY
    if not registry.is_file():
        return [Finding(REGISTRY, "toolbox-table", "blocking", "the registry is missing (ADR-020)")]
    rows, found = parse_rows(registry.read_text(encoding="utf-8"))
    found += check_rows(rows, read_schema_version(base))
    found += check_lock(rows, read_lock(base))
    imports, refused = read_imports(base)
    found += refused + check_imports(imports, rows)
    html, refused = read_discovered(base, "cockpit", "*.html")
    found += refused
    pages = {p.relative_to(base).as_posix(): p.read_text(encoding="utf-8") for p in html}
    found += check_scripts(pages, rows)
    shas, problems = read_held(base, rows)
    found += check_held(rows, shas, read_vendored(base), problems)
    return found
