"""The toolbox checks (ADR-020, HANDOFF-0044 §3): every third-party thing has its row.

Purpose: a third-party package, module, skill, model, harness or API enters KGME through one
row of `docs/toolbox.md`, and these checks keep the row and the tree in step. Every
non-standard-library import in `kgme/` and `cockpit/` names a package row; no `<script src>`
in `cockpit/` names a host (the cockpit loads nothing remote), and a local one points at a
vendored file with a row; every file under `cockpit/static/vendor/` and every vendored skill
has a row whose sha256 is the file's. A row carries a source, a sha and, for a model or an API,
an egress host. A row without a licence is `advisory` under schema 1.7 and `blocking` from 1.8.
Inputs: the registry's text; the repository's Python files, HTML pages and vendored files.
Outputs: `kgme.lint.Finding` records, `blocking` or `advisory`.
Side effects: none; the effects that read the tree are `kgme/toolbox_read.py`.

The registry is one Markdown table; its columns are `name`, `kind`, `for`, `source`,
`licence`, `version`, `held`, `sha256`, `egress`, `used in`, `handoff`. `held` says what the
sha is checked against: a repository path (verified here), `uv.lock` (the lock holds the
hashes; the sha cell says `uv.lock`), a folder ending in `/` (a vendored skill; its sha is
`folder_sha`, over every file in it), `pending: <path> (HANDOFF-NNNN)` (to be vendored by that
handoff; reported, not verified), or `machine: <path>` (a harness or model as installed on
this machine; recorded, not verifiable from a clone). A package row names its import as
`(import <module>)` in the `name` cell.
"""

import hashlib
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import PurePosixPath

from kgme.lint import Finding

REGISTRY = "docs/toolbox.md"
COLUMNS = (
    "name", "kind", "for", "source", "licence", "version", "held", "sha256", "egress",
    "used in", "handoff",
)  # fmt: skip
KINDS = ("package", "module", "skill", "harness", "model", "api", "asset")
NEEDS_EGRESS = ("model", "api")
FIRST_PARTY = frozenset({"kgme", "cockpit", "__future__"})
IMPORT_ROOTS = ("kgme", "cockpit")
VENDOR = "cockpit/static/vendor"
SKILLS = "skills"
SHA = re.compile(r"^[0-9a-f]{64}$")
LOCK_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
IMPORTS = re.compile(r"\(import ([\w., ]+)\)")
PENDING = re.compile(r"^pending: (\S+) \((HANDOFF-\d{4})\)$")
REMOTE = re.compile(r"^([a-z][a-z0-9+.-]*:)?//", re.IGNORECASE)
SCHEMA = "docs/schema-v1.md"
SCHEMA_VERSION = re.compile(r"^version:\s*(\d+)\.(\d+)\s*$", re.MULTILINE)
LICENCE_BLOCKING_FROM = (1, 8)
HOLDS = (VENDOR + "/", SKILLS + "/")


@dataclass(frozen=True)
class Row:
    """One registry row, every cell stripped; `line` is its line in the registry."""

    line: int
    cells: dict[str, str]

    @property
    def name(self) -> str:
        return self.cells["name"]

    @property
    def imports(self) -> tuple[str, ...]:
        found = IMPORTS.search(self.name)
        return tuple(m.strip() for m in found.group(1).split(",")) if found else ()


def parse_rows(text: str) -> tuple[list[Row], list[Finding]]:
    """Pure: the registry's rows, and a blocking finding for a table that is not the one
    the schema names (wrong header, a row with the wrong number of cells)."""
    rows: list[Row] = []
    found: list[Finding] = []
    header_seen = False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not header_seen:
            if tuple(c.lower() for c in cells) != COLUMNS:
                message = f"the table's header must be {' | '.join(COLUMNS)}"
                found.append(Finding(REGISTRY, "toolbox-table", "blocking", message))
                return rows, found
            header_seen = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if len(cells) != len(COLUMNS):
            message = f"line {number}: {len(cells)} cells, the table has {len(COLUMNS)}"
            found.append(Finding(REGISTRY, "toolbox-table", "blocking", message))
            continue
        rows.append(Row(number, dict(zip(COLUMNS, cells, strict=True))))
    if not header_seen:
        found.append(Finding(REGISTRY, "toolbox-table", "blocking", "no registry table"))
    return rows, found


def licence_class(schema_version: tuple[int, int] | None) -> str:
    """Pure: how a missing licence is classed: `advisory` under schema 1.7, `blocking` from
    1.8 (HANDOFF-0044 §3), and `blocking` when the schema's version cannot be read."""
    if schema_version is None or schema_version >= LICENCE_BLOCKING_FROM:
        return "blocking"
    return "advisory"


def check_rows(rows: list[Row], schema_version: tuple[int, int] | None = (1, 7)) -> list[Finding]:
    """Pure: each row has a known kind, a source, a sha the `held` cell can stand behind, an
    egress host where the kind needs one, a licence (classed by `licence_class`), and a
    unique name."""
    found: list[Finding] = []

    def add(row: Row, cls: str, message: str) -> None:
        found.append(
            Finding(REGISTRY, "toolbox-row", cls, f"line {row.line} ({row.name}): {message}")
        )

    seen: set[str] = set()
    for row in rows:
        c = row.cells
        if row.name in seen:
            add(row, "blocking", "a second row with this name")
        seen.add(row.name)
        if c["kind"] not in KINDS:
            add(row, "blocking", f"kind must be one of {', '.join(KINDS)}")
        if not c["source"] or c["source"] == "—":
            add(row, "blocking", "no source")
        if not c["licence"] or c["licence"] == "—":
            add(row, licence_class(schema_version), "no licence (blocking from schema 1.8)")
        if c["held"] == "uv.lock":
            if c["sha256"] != "uv.lock" or c["kind"] != "package":
                add(row, "blocking", "`held: uv.lock` is for a package row whose sha is `uv.lock`")
        elif not SHA.match(c["sha256"]):
            add(row, "blocking", "no sha256 (64 lowercase hex digits) of what we hold")
        if c["kind"] in NEEDS_EGRESS and c["egress"] in ("", "—", "none"):
            add(row, "blocking", f"a {c['kind']} row names the egress host it needs")
    return found


def distribution(row: Row) -> str:
    """Pure: a package row's distribution name, normalised as the lock writes it."""
    return re.sub(r"[-_.]+", "-", row.name.split("(")[0].strip()).lower()


def lock_hashes(entry: dict) -> list[str]:
    """Pure: every artifact hash a `uv.lock` package entry records (its sdist and wheels)."""
    hashes = [entry.get("sdist", {}).get("hash")]
    hashes += [wheel.get("hash") for wheel in entry.get("wheels", [])]
    return [str(h) for h in hashes if h]


def check_lock(rows: list[Row], lock: dict | None) -> list[Finding]:
    """Pure: each `held: uv.lock` row names a package `uv.lock` pins at the row's version,
    with artifact hashes, each `sha256:` and 64 hex digits (review cycles 1 and 2 F3); a
    missing lock is blocking."""
    found: list[Finding] = []
    locked = [row for row in rows if row.cells["held"] == "uv.lock"]
    if locked and lock is None:
        found.append(Finding(REGISTRY, "toolbox-lock", "blocking", "uv.lock is missing"))
        return found
    packages = {p.get("name"): p for p in (lock or {}).get("package", [])}
    for row in locked:
        where, entry = f"line {row.line} ({row.name})", packages.get(distribution(row))
        if entry is None:
            message = f"{where}: uv.lock pins no package `{distribution(row)}`"
        elif entry.get("version") != row.cells["version"]:
            message = (
                f"{where}: uv.lock pins {entry.get('version')}, the row {row.cells['version']}"
            )
        elif not (hashes := lock_hashes(entry)) or not all(LOCK_HASH.match(h) for h in hashes):
            message = f"{where}: uv.lock holds no well-formed sha256 artifact hash for it"
        else:
            continue
        found.append(Finding(REGISTRY, "toolbox-lock", "blocking", message))
    return found


def check_imports(imports: dict[str, set[str]], rows: list[Row]) -> list[Finding]:
    """Pure: every non-standard-library, non-first-party module imported in `imports` (path to
    the modules it imports) is named by a package row's `(import ...)`."""
    covered = {m for row in rows if row.cells["kind"] == "package" for m in row.imports}
    found: list[Finding] = []
    for path, modules in sorted(imports.items()):
        for module in sorted(modules - covered - FIRST_PARTY):
            if module in sys.stdlib_module_names:
                continue
            message = f"imports `{module}`, which no toolbox row names (ADR-020)"
            found.append(Finding(path, "toolbox-import", "blocking", message))
    return found


class ScriptSources(HTMLParser):
    """The exact `src` attribute of every `<script>` in a page; `data-src` and the like are
    other attributes and are not read (review cycle 1 F1)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.sources += [value for name, value in attrs if name == "src" and value is not None]


def script_sources(text: str) -> list[str]:
    """Pure: the `src` of every `<script>` in an HTML page."""
    parser = ScriptSources()
    parser.feed(text)
    parser.close()
    return parser.sources


def check_scripts(pages: dict[str, str], rows: list[Row]) -> list[Finding]:
    """Pure: no `<script src>` in a cockpit page names a host; a local one points at a file
    under `cockpit/static/vendor/` that a row holds."""
    held = {row.cells["held"] for row in rows}
    found: list[Finding] = []
    for path, text in sorted(pages.items()):
        for src in script_sources(text):
            if REMOTE.match(src):
                message = f"`<script src={src}>` names a host; the cockpit loads nothing remote"
                found.append(Finding(path, "toolbox-script", "blocking", message))
                continue
            local = "cockpit/" + src.lstrip("/")
            if not local.startswith(VENDOR + "/") or local not in held:
                message = f"`<script src={src}>` is not a vendored file with a toolbox row"
                found.append(Finding(path, "toolbox-script", "blocking", message))
    return found


def held_problem(place: str) -> str | None:
    """Pure: why a repository path a row holds may not be read, or None. It is relative, has
    no `..`, and lies under `cockpit/static/vendor/` or `skills/`, the only places ADR-020
    vendors into (review cycle 1 F4)."""
    path = PurePosixPath(place)
    if path.is_absolute() or ".." in path.parts or place.startswith("~"):
        return f"{place} is not a relative path inside the repository"
    if not place.startswith(HOLDS):
        return f"{place} is outside {' and '.join(HOLDS)}, where vendored things live"
    return None


def check_held(
    rows: list[Row],
    files: dict[str, str | None],
    vendored: list[str],
    problems: dict[str, str] | None = None,
) -> list[Finding]:
    """Pure: each repository path a row holds exists with the row's sha (`files` maps it to
    the sha read, None when absent); each vendored file (`vendored`) has a row; a pending
    row is reported, not verified; a path in `problems` was refused, never read."""
    found: list[Finding] = []
    held: set[str] = set()
    problems = problems or {}
    for row in rows:
        place, where = row.cells["held"], f"line {row.line} ({row.name})"
        pending = PENDING.match(place)
        if pending:
            message = f"{where}: {pending.group(1)} is to be vendored by {pending.group(2)}"
            found.append(Finding(REGISTRY, "toolbox-pending", "advisory", message))
            continue
        if place == "uv.lock" or place.startswith("machine:"):
            continue
        held.add(place)
        actual = files.get(place)
        if place in problems:
            message = f"{where}: {problems[place]}; not read"
            found.append(Finding(REGISTRY, "toolbox-held", "blocking", message))
        elif actual is None:
            message = f"{where}: {place} is not in the tree"
            found.append(Finding(REGISTRY, "toolbox-held", "blocking", message))
        elif actual != row.cells["sha256"]:
            expected = row.cells["sha256"][:16]
            message = f"{where}: {place} has sha256 {actual[:16]}…, the row {expected}…"
            found.append(Finding(REGISTRY, "toolbox-sha", "blocking", message))
    for path in vendored:
        if path not in held:
            message = "a vendored file no toolbox row holds (ADR-020)"
            found.append(Finding(path, "toolbox-held", "blocking", message))
    return found


def folder_sha(listing: list[tuple[str, str]]) -> str:
    """Pure: one sha256 for a folder, from its files' relative paths and sha256s: the sha256
    of the sorted `<path> <sha>` lines. Any file changed, added or removed changes it."""
    lines = "".join(f"{path} {sha}\n" for path, sha in sorted(listing))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()
