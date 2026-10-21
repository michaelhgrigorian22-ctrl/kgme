"""Coherence checks, pure half: does the tree say what its documents say (HANDOFF-0049 item 7).

Purpose: four checks `kgme lint` runs over the whole repository, beside the schema's checks.
A handoff's folder matches its `status` (`open` at the top of `docs/handoff/`, `done` under
`done/`, `proposed` under `proposed/`, `abandoned` and `superseded` under `archive/`); a
finished handoff's `report` exists; every backticked repository path in the live documents
resolves in the commit, the index's paths and the folders above them (a path inside the
design track's own folders may resolve on the `design` branch instead), except the `Outputs`
of open and proposed handoffs, the paths at or under a `kgme.toml` `[clean.targets]` entry
(regenerated, so absent by design), and the other paths absent by design; and each top-level
folder in `CLAUDE.md`'s map exists or is marked later. What resolves is a function of the
commit, never of what this machine's runs created (HANDOFF-0054).
A token is recognised as this repository's path by declared root, never by existence (the
arbiter's ruling on review cycle 2 F4): its first segment is a top-level folder the map in
`CLAUDE.md` declares (marked later or not), the hidden `.claude`, or the retired `tools`;
or it sits under a folder the map declares beneath the document's own folder; or it is a
root file. It is then resolved from the document's folder and from the root, and the
exemptions apply last (F3, F4). Findings are `advisory` until `kgme.toml` `[coherence]
blocking_from`, then `blocking` (F5; schema v1.5).
Inputs: the handoffs as `(repo-relative path, frontmatter, body)`, the live documents as
`(repo-relative path, text)`, the index's paths, the text of `CLAUDE.md`, the paths on the
`design` branch, the clean targets, the class and the day.
Outputs: `Finding` records from `kgme.lint`.
Side effects: none. Reading the tree is `kgme.vault.read_coherence_inputs`.
"""

import datetime
import re
from pathlib import PurePosixPath

from kgme.lint import Finding

CLASS = "advisory"
DESIGN_AREAS = ("docs/design", "docs/handoff/cockpit-design", "docs/audit/cockpit-design")
# Roots that existed and were renamed: a path under one is stale, never someone else's.
RETIRED_ROOTS = ("tools",)
# A hidden root the map does not draw, declared here so its paths are checked even if it goes.
HIDDEN_ROOTS = frozenset({".claude"})
MAP_ENTRY = re.compile(r"^( *)([A-Za-z.][\w.-]*)/(?:\s|$)")
HANDOFF_ROOT = "docs/handoff"
FOLDER_STATUS = {
    "": ("open",),
    "done": ("done",),
    "proposed": ("proposed",),
    "archive": ("abandoned", "superseded"),
}
ROOT_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "kgme.toml",
    "Makefile",
    "pyproject.toml",
    "uv.lock",
    ".gitignore",
    ".python-version",
)
PATH_TOKEN = re.compile(r"^\.?[A-Za-z0-9_][\w.@-]*(/[\w.@-]+)*$")
# Absent by design: Tier 1 lives in its own repository (ADR-002); the design review folder
# exists only once Michou exports images into it himself (HANDOFF-0042 item 4); project
# skills live in `.claude/skills/` once the first one is written.
ABSENT_BY_DESIGN = ("memory/private", "docs/design/cockpit-v0/review", ".claude/skills")
NOT_A_PATH = re.compile(r"[\s*<>{}…|]|\.\.\.|NNN|YYYY|-DD\b|\bMM\b")
BACKTICKED = re.compile(r"`([^`\n]+)`")
MAP_LINE = re.compile(r"^([A-Za-z][\w.-]*)/\s")


def handoff_folder(rel: str) -> str | None:
    """`""`, `done`, `proposed` or `archive` for a handoff directly in one of the four state
    folders; None for anything deeper (a design track's own folder, HANDOFF-0042)."""
    parts = rel.split("/")
    if parts[:2] != ["docs", "handoff"]:
        return None
    if len(parts) == 3:
        return ""
    if len(parts) == 4 and parts[2] in FOLDER_STATUS:
        return parts[2]
    return None


def check_handoffs(
    handoffs: list[tuple[str, dict, str]], existing: frozenset[str], cls: str = CLASS
) -> list[Finding]:
    """A handoff's folder matches its status; a finished one names a report that exists."""
    found: list[Finding] = []
    for rel, data, _ in handoffs:
        folder = handoff_folder(rel)
        if folder is None:
            continue
        status = data.get("status")
        if status not in FOLDER_STATUS[folder]:
            where = f"{HANDOFF_ROOT}/{folder}/" if folder else f"{HANDOFF_ROOT}/"
            message = f"status {status!r} does not belong in {where}"
            found.append(Finding(rel, "coherence-folder", cls, message))
        if status == "done":
            report = data.get("report")
            if not report:
                found.append(Finding(rel, "coherence-report", cls, "done without `report`"))
            elif str(report) not in existing:
                message = f"`report` {report} does not exist"
                found.append(Finding(rel, "coherence-report", cls, message))
    return found


def outputs_section(body: str) -> str:
    """The text of a handoff's `## Outputs` section, empty when it has none."""
    match = re.search(r"^## Outputs\s*$(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def finding_class(today: datetime.date, blocking_from: str | None) -> str:
    """`advisory` before the configured day, `blocking` from it on; `advisory` when unset."""
    if not blocking_from:
        return CLASS
    return "blocking" if today >= datetime.date.fromisoformat(blocking_from) else CLASS


def repository_path(token: str) -> str | None:
    """The path a backticked token is shaped as, or None: a command, a pattern, a placeholder,
    a home, absolute or parent path, a URL, or a bare word that is neither a root file nor a
    folder written with its trailing `/` (`tools/`). Whether it is this repository's is
    decided by declared root in `check_paths`, never here and never by existence (F4)."""
    if NOT_A_PATH.search(token):
        return None
    shaped = token.split(":", 1)[0].rstrip(".,;")
    path = shaped.rstrip("/")
    if not path or not PATH_TOKEN.match(path):
        return None
    if "/" not in path and path not in ROOT_FILES and not shaped.endswith("/"):
        return None
    return path


def declared_folders(claude_text: str) -> frozenset[str]:
    """Every folder `CLAUDE.md`'s repository map declares, top-level and nested, existing or
    marked later, as repository-relative paths (`docs`, `docs/handoff`, `docs/handoff/done`)."""
    match = re.search(r"^## Repository map\s*$.*?```\n(.*?)```", claude_text, re.M | re.S)
    found: set[str] = set()
    stack: list[tuple[int, str]] = []
    for line in match.group(1).splitlines() if match else []:
        entry = MAP_ENTRY.match(line)
        if not entry:
            continue
        indent, name = len(entry.group(1)), entry.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, name))
        found.add("/".join(part for _, part in stack))
    return frozenset(found)


def recognised(path: str, document: str, declared: frozenset[str]) -> bool:
    """Whether `path` is this repository's, by declared root (the arbiter's ruling, F4)."""
    if path in ROOT_FILES:
        return True
    first = path.split("/", 1)[0]
    top = frozenset(d for d in declared if "/" not in d) | HIDDEN_ROOTS | frozenset(RETIRED_ROOTS)
    folder = document.rsplit("/", 1)[0] if "/" in document else ""
    return first in top or (bool(folder) and f"{folder}/{first}" in declared)


def candidates(path: str, document: str) -> list[str]:
    """Pure: `path` from the root, and from the document's folder when it has one."""
    folder = document.rsplit("/", 1)[0] if "/" in document else ""
    return [path, f"{folder}/{path}"] if folder else [path]


def resolves(path: str, document: str, existing: frozenset[str], design: frozenset[str]) -> bool:
    """`path` exists from the root or from the document's folder in this checkout, or, inside
    the design track's own folders only, on the `design` branch (F3)."""
    candidates_ = candidates(path, document)
    if any(candidate in existing for candidate in candidates_):
        return True
    return any(
        candidate in design and any(in_area(candidate, area) for area in DESIGN_AREAS)
        for candidate in candidates_
    )


def in_area(path: str, area: str) -> bool:
    """True if `path` is the folder `area` or lies under it."""
    return path == area or path.startswith(area + "/")


def later_roots(claude_text: str) -> frozenset[str]:
    """The top-level folders `CLAUDE.md`'s map marks `(later`: paths under them are promised."""
    match = re.search(r"^## Repository map\s*$.*?```\n(.*?)```", claude_text, re.M | re.S)
    lines = match.group(1).splitlines() if match else []
    marked = [MAP_LINE.match(line) for line in lines if "(later" in line]
    return frozenset(m.group(1) for m in marked if m)


def excused_paths(handoffs: list[tuple[str, dict, str]]) -> frozenset[str]:
    """The paths open and proposed handoffs promise as outputs: not built yet, by design."""
    promised: set[str] = set()
    for _, data, body in handoffs:
        if data.get("status") in ("open", "proposed"):
            for token in BACKTICKED.findall(outputs_section(body)):
                path = repository_path(token)
                if path:
                    promised.add(path)
    return frozenset(promised)


def is_regenerable(path: str, entries: tuple[str, ...]) -> bool:
    """Pure: `path` is at or under a clean target: a root, or a folder some leading part of
    the path matches as a glob (`**/__pycache__`)."""
    parts = path.split("/")
    for entry in entries:
        if "*" in entry:
            prefixes = ("/".join(parts[: i + 1]) for i in range(len(parts)))
            if any(PurePosixPath(prefix).full_match(entry) for prefix in prefixes):
                return True
        elif path == entry or path.startswith(entry + "/"):
            return True
    return False


def check_paths(
    documents: list[tuple[str, str]],
    existing: frozenset[str],
    excused: frozenset[str],
    design: frozenset[str] = frozenset(),
    cls: str = CLASS,
    later: frozenset[str] = frozenset(),
    declared: frozenset[str] = frozenset(),
    regenerable: tuple[str, ...] = (),
) -> list[Finding]:
    """Every backticked path that is this repository's resolves. A token is recognised by
    declared root (`recognised`), never by what exists now, so a declared root that is gone
    is still checked and another project's or a remote's name is not; it is then resolved;
    the exemptions apply last: the `Outputs` open and proposed handoffs promise, roots the
    map marks later, the paths at or under a clean target (regenerated, so absent by design,
    HANDOFF-0054), and the other paths absent by design."""
    found: list[Finding] = []
    for rel, text in documents:
        seen: set[str] = set()
        for token in BACKTICKED.findall(text):
            path = repository_path(token)
            if path is None or path in seen or not recognised(path, rel, declared):
                continue
            if resolves(path, rel, existing, design):
                continue
            if path in excused or path.split("/", 1)[0] in later:
                continue
            # either reading of the token, from the root or the document's folder (review
            # cycle 1 F1 of HANDOFF-0054)
            if any(is_regenerable(c, regenerable) for c in candidates(path, rel)):
                continue
            if any(path == a or path.startswith(a + "/") for a in ABSENT_BY_DESIGN):
                continue
            seen.add(path)
            found.append(Finding(rel, "coherence-path", cls, f"`{path}` does not resolve"))
    return found


def check_map(claude_text: str, existing: frozenset[str], cls: str = CLASS) -> list[Finding]:
    """Each top-level folder in `CLAUDE.md`'s repository map exists or is marked later."""
    match = re.search(r"^## Repository map\s*$.*?```\n(.*?)```", claude_text, re.M | re.S)
    if not match:
        return [Finding("CLAUDE.md", "coherence-map", cls, "no repository map found")]
    found: list[Finding] = []
    for line in match.group(1).splitlines():
        folder = MAP_LINE.match(line)
        if folder and folder.group(1) not in existing and "(later" not in line:
            message = f"map lists `{folder.group(1)}/`, which neither exists nor is marked later"
            found.append(Finding("CLAUDE.md", "coherence-map", cls, message))
    return found


def check_tree(
    handoffs: list[tuple[str, dict, str]],
    documents: list[tuple[str, str]],
    existing: frozenset[str],
    claude_text: str,
    design: frozenset[str] = frozenset(),
    regenerable: tuple[str, ...] = (),
    cls: str = CLASS,
) -> list[Finding]:
    """All four checks, in the order the module docstring states, each finding of `cls`."""
    return [
        *check_handoffs(handoffs, existing, cls),
        *check_paths(
            documents,
            existing,
            excused_paths(handoffs),
            design,
            cls,
            later_roots(claude_text),
            declared_folders(claude_text),
            regenerable,
        ),
        *check_map(claude_text, existing, cls),
    ]
