"""`kgme clean`, the pure half: what one target would delete, and what it refuses.

Purpose: turn a listing of filesystem entries into a `CleanPlan` (HANDOFF-0033; Michou's
ruling of 2026-09-14 that bare `rm -rf` stays denied everywhere and agents get a deleter that
reaches only ADR-012's disposable class). A target is a name from `kgme.toml`
`[clean.targets]`, never a path. `plan_clean` refuses a symlink, any path with a `.git` part,
anything under `logs/ledger/`, anything the job's manifest refused, and anything whose
resolved path leaves its root or the repository; a plan holding one refusal deletes nothing
(ADR-016: a blocking finding stops the job). The plan is also written ahead as a payload
(`plan_record`), each path numbered, so an outcome names its path by number when the path
alone would not fit the summary (review F6) and an interrupted run can be reconciled against
what it meant to delete (ADR-013 §4). Listing lives in `kgme/clean_read.py`; deleting in
`kgme/clean_fs.py`; the run and the ledger events in `kgme/clean_io.py`.
Inputs: `Entry` records (path, resolved path, kind, size, device, inode, modification
time), the repository
root, the target's resolved roots, the ledger directory, the manifest's refusals.
Outputs: a `CleanPlan`; the lines that describe it; one-line summaries for the ledger.
Side effects: none.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    """One filesystem entry as found: where it sits, what it resolves to, what it is."""

    path: Path
    resolved: Path
    is_dir: bool
    is_symlink: bool
    size: int
    dev: int = 0
    ino: int = 0
    mtime_ns: int = 0
    is_special: bool = False


@dataclass(frozen=True)
class Refusal:
    """An entry the plan will not touch, and why."""

    entry: Entry
    reason: str


@dataclass(frozen=True)
class CleanPlan:
    """What one target would delete. `dirs` is deepest first, the order they are removed in.
    `kept` are directories that hold a refused entry and so stay."""

    target: str
    files: tuple[Entry, ...]
    dirs: tuple[Entry, ...]
    refused: tuple[Refusal, ...]
    kept: tuple[Entry, ...]

    def total_bytes(self) -> int:
        return sum(entry.size for entry in self.files)

    def empty(self) -> bool:
        return not (self.files or self.dirs or self.refused)


def shown(path: Path, root: Path) -> str:
    """A path as the console and the ledger show it: repo-relative when under the root."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def refusal_reason(
    entry: Entry,
    root: Path,
    allowed_roots: list[Path],
    ledger_dir: Path,
    manifest_refusals: dict[Path, str],
) -> str:
    """Why `entry` may not be deleted, or an empty string. The order is the rule's order."""
    if entry.is_symlink:
        return "a symlink; links are never followed or removed"
    if entry.is_special:
        return "not a regular file or directory (a FIFO, socket, or device)"
    if ".git" in entry.path.parts:
        return "under a .git directory"
    if entry.resolved == ledger_dir or ledger_dir in entry.resolved.parents:
        return f"under {shown(ledger_dir, root)}, never a target (ADR-012)"
    if not entry.resolved.is_relative_to(root):
        return "resolves outside the repository"
    if not any(entry.resolved.is_relative_to(allowed) for allowed in allowed_roots):
        return "resolves outside the target's roots"
    if entry.resolved in manifest_refusals:
        return manifest_refusals[entry.resolved]
    return ""


def plan_clean(
    target: str,
    entries: list[Entry],
    root: Path,
    allowed_roots: list[Path],
    ledger_dir: Path,
    manifest_refusals: dict[Path, str],
) -> CleanPlan:
    """The plan for `target` from a listing: every entry sorted into files, directories
    (deepest first), refusals, and directories kept because a refused entry lies under them."""
    files: list[Entry] = []
    dirs: list[Entry] = []
    refused: list[Refusal] = []
    for entry in entries:
        reason = refusal_reason(entry, root, allowed_roots, ledger_dir, manifest_refusals)
        if reason:
            refused.append(Refusal(entry, reason))
        elif entry.is_dir:
            dirs.append(entry)
        else:
            files.append(entry)
    refused_paths = [refusal.entry.path for refusal in refused]
    kept = [d for d in dirs if any(d.path in path.parents for path in refused_paths)]
    removable = [d for d in dirs if d not in kept]
    return CleanPlan(
        target=target,
        files=tuple(sorted(files, key=lambda e: e.path)),
        dirs=tuple(sorted(removable, key=lambda e: (-len(e.path.parts), e.path))),
        refused=tuple(sorted(refused, key=lambda r: r.entry.path)),
        kept=tuple(sorted(kept, key=lambda e: e.path)),
    )


def keep_holding(plan: CleanPlan, path: Path) -> CleanPlan:
    """The plan with every directory above `path` kept instead of removed: the run's own
    payload lands under `logs/scratch/payloads/`, which the `scratch` target would otherwise
    try to remove while it holds that payload."""
    holding = [d for d in plan.dirs if d.path in path.parents]
    if not holding:
        return plan
    return CleanPlan(
        target=plan.target,
        files=plan.files,
        dirs=tuple(d for d in plan.dirs if d not in holding),
        refused=plan.refused,
        kept=tuple(sorted((*plan.kept, *holding), key=lambda e: e.path)),
    )


def plan_record(plan: CleanPlan, root: Path, key: str, digests: dict[Path, str]) -> dict:
    """The plan as the payload keeps it: every path numbered in deletion order, with the size,
    device, inode, and sha256 prefix the listing saw, so a later run can tell what was meant
    and can record a deletion it finds done with the size and hash the outcome would have."""
    files = [
        {
            "n": i,
            "path": shown(e.path, root),
            "size": e.size,
            "sha256": digests[e.path],
            "dev": e.dev,
            "ino": e.ino,
            "mtime_ns": e.mtime_ns,
        }
        for i, e in enumerate(plan.files, 1)
    ]
    dirs = [
        {"n": i, "path": shown(e.path, root), "dev": e.dev, "ino": e.ino}
        for i, e in enumerate(plan.dirs, len(files) + 1)
    ]
    refused = [{"path": shown(r.entry.path, root), "reason": r.reason} for r in plan.refused]
    return {"target": plan.target, "key": key, "files": files, "dirs": dirs, "refused": refused}


def fit_path(rel: str, budget: int) -> str:
    """`rel` cut from the left to `budget` characters, its end kept, since the end is what
    tells one path from its neighbours; the number beside it is the unambiguous reference."""
    if len(rel) <= budget:
        return rel
    return "…" + rel[-(budget - 1) :]


def fit_summary(head: str, rel: str, tail: str, cap: int, measure: Callable[[str], int]) -> str:
    """`head + path + tail`, the path alone shortened until `measure` of the whole is within
    `cap`; `measure` is the length after the ledger's redaction, which can lengthen a path
    that happens to hold a secret-shaped span (review F6)."""
    budget = cap - len(head) - len(tail)
    while True:
        text = head + fit_path(rel, budget) + tail
        excess = measure(text) - cap
        if excess <= 0 or budget <= 1:
            return text
        budget -= excess


def fit_text(text: str, cap: int, measure: Callable[[str], int]) -> str:
    """`text` cut from the right until `measure` of it is within `cap`: the last guard before
    the ledger on any summary, for one no path-aware fitting shaped (review cycle 3, F6)."""
    while measure(text) > cap and len(text) > 1:
        text = text[: max(1, len(text) - (measure(text) - cap) - 1)] + "…"
    return text


def deleted_summary(
    number: int, size: int, digest: str, rel: str, cap: int, measure: Callable[[str], int]
) -> str:
    """`deleted #n <size> B sha256 <digest> <path>`, the path alone shortened to fit `cap`."""
    return fit_summary(f"deleted #{number} {size} B sha256 {digest} ", rel, "", cap, measure)


def removed_summary(number: int, rel: str, cap: int, measure: Callable[[str], int]) -> str:
    """`removed #n <path>/`, the path alone shortened to fit `cap`."""
    return fit_summary(f"removed #{number} ", rel, "/", cap, measure)


def plan_summary(plan: CleanPlan, mode: str) -> str:
    """The one line the ledger keeps for a plan."""
    return (
        f"clean {plan.target} {mode}: {len(plan.files)} files {plan.total_bytes()} B, "
        f"{len(plan.dirs)} dirs, {len(plan.refused)} refused"
    )


def plan_lines(plan: CleanPlan, root: Path) -> list[str]:
    """The plan for the console: one line per path with its size, refusals with their reasons,
    kept directories, and a total."""
    lines = [f"  {entry.size:>10} B  {shown(entry.path, root)}" for entry in plan.files]
    lines += [f"  {'dir':>10}    {shown(entry.path, root)}/" for entry in plan.dirs]
    lines += [
        f"  {'REFUSED':>10}    {shown(refusal.entry.path, root)}: {refusal.reason}"
        for refusal in plan.refused
    ]
    lines += [
        f"  {'kept':>10}    {shown(entry.path, root)}/ holds a refused entry" for entry in plan.kept
    ]
    lines.append(
        f"kgme clean {plan.target}: {len(plan.files)} files, {plan.total_bytes()} bytes, "
        f"{len(plan.dirs)} directories, {len(plan.refused)} refused"
    )
    return lines
