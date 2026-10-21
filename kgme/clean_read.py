"""`kgme clean`, the reading half of the effects: the listing, the fences, the recheck.

Purpose: every place the deleter looks at the world before and while it acts (ADR-015, one
named function each): entries by `lstat`, trees walked without following a link and with
every listing and `lstat` error kept (review F4), a target's roots checked for a symlink in
any component (review F1), and the guard's fences for the manifest check. The deletions
themselves, each after one final check against its entry, are in `kgme/clean_fs.py`.
Inputs: paths under the checkout to act on, the target's entries, the parsed `kgme.toml`.
Outputs: `Entry` records, listing errors as `(path, reason)` pairs, resolved roots, fences.
Side effects: `lstat` and directory walks only; nothing is written.
"""

import os
import stat
from pathlib import Path, PurePosixPath

from kgme import paths
from kgme.clean import Entry

PRUNE = (".git", ".venv")


def read_entry(path: Path) -> Entry:
    """One entry by `lstat`: a symlink is reported as such and never followed."""
    status = os.lstat(path)
    is_link = stat.S_ISLNK(status.st_mode)
    is_dir = not is_link and stat.S_ISDIR(status.st_mode)
    is_special = not (is_link or is_dir or stat.S_ISREG(status.st_mode))
    size = 0 if is_dir else status.st_size
    return Entry(
        path,
        path.resolve(),
        is_dir,
        is_link,
        size,
        status.st_dev,
        status.st_ino,
        status.st_mtime_ns,
        is_special,
    )


def read_tree(top: Path) -> tuple[list[Entry], list[tuple[Path, str]]]:
    """Everything under `top`, not `top` itself, symlinks listed but never entered, and every
    directory the walk could not read as an error the plan must refuse on."""
    found: list[Entry] = []
    errors: list[tuple[Path, str]] = []

    def failed(error: OSError) -> None:
        errors.append((Path(error.filename or top), error.strerror or "could not list"))

    for dirpath, dirnames, filenames in os.walk(top, onerror=failed, followlinks=False):
        here = Path(dirpath)
        for name in sorted(dirnames) + sorted(filenames):
            try:
                found.append(read_entry(here / name))
            except OSError as error:
                errors.append((here / name, error.strerror or "could not stat"))
    return found, errors


def read_matches(root: Path, pattern: str) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Entries under `root` whose repo-relative path matches `pattern`; `.git` and `.venv` are
    never entered, so `**/__pycache__` names the repository's caches, not the environment's."""
    matches: list[Path] = []
    errors: list[tuple[Path, str]] = []

    def failed(error: OSError) -> None:
        errors.append((Path(error.filename or root), error.strerror or "could not list"))

    for dirpath, dirnames, filenames in os.walk(root, onerror=failed, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name not in PRUNE)
        for name in dirnames + sorted(filenames):
            path = Path(dirpath) / name
            if PurePosixPath(path.relative_to(root).as_posix()).full_match(pattern):
                matches.append(path)
    return matches, errors


def read_link_in_ancestry(path: Path, root: Path) -> Path | None:
    """The first component of `path` below `root`, `path` itself included, that is a symlink;
    None when there is none. A root reached through a link is a root somewhere else."""
    for ancestor in [*reversed(path.parents), path]:
        if ancestor == root or root not in ancestor.parents:
            continue
        if ancestor.is_symlink():
            return ancestor
    return None


def read_candidates(
    root: Path, target_entries: list[str]
) -> tuple[list[Entry], list[Path], list[tuple[Path, str]]]:
    """Every entry a target names, the resolved roots each must stay under, and the listing
    errors. A root that is a symlink, or sits below one, is listed as that link, which the
    plan refuses, and is not entered."""
    found: list[Entry] = []
    allowed: list[Path] = []
    errors: list[tuple[Path, str]] = []
    for item in target_entries:
        if "*" in item:
            matches, failed = read_matches(root, item)
            errors.extend(failed)
            for match in matches:
                try:
                    entry = read_entry(match)
                except OSError as error:
                    errors.append((match, error.strerror or "could not stat"))
                    continue
                found.append(entry)
                allowed.append(entry.resolved)
                if entry.is_dir:
                    below, failed = read_tree(match)
                    found.extend(below)
                    errors.extend(failed)
            continue
        top = root / item
        try:
            link = read_link_in_ancestry(top, root)
            if link is not None:
                found.append(read_entry(link))
            elif top.is_dir():
                allowed.append(top.resolve())
                below, failed = read_tree(top)
                found.extend(below)
                errors.extend(failed)
        except OSError as error:
            errors.append((top, error.strerror or "could not stat"))
    return once(found), allowed, errors


def once(found: list[Entry]) -> list[Entry]:
    """Each path once, the first listing kept: overlapping roots or glob matches (a cache
    nested in a cache) walk the same entries twice (review cycle 7 F20)."""
    seen: set[Path] = set()
    unique: list[Entry] = []
    for entry in found:
        if entry.path not in seen:
            seen.add(entry.path)
            unique.append(entry)
    return unique


def read_fences(settings: dict, base: Path) -> tuple[list[Path], list[str], list[Path]]:
    """The guard's blocklist roots, its name patterns, and the Tier 1 roots, as the manifest
    check wants them; a manifest narrows and never widens these."""
    blocklist = settings["hooks"]["blocklist"]
    return (
        [paths.resolve(p) for p in blocklist if not p.startswith("**/")],
        [p[3:] for p in blocklist if p.startswith("**/")],
        paths.tier1_paths(settings, base),
    )
