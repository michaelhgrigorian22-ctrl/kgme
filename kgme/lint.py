"""The schema validator, pure half: one note's text and path to a list of classed findings.

Purpose: apply `docs/schema-v1.md` to a note (HANDOFF-0031), with the track rules of v1.6
(HANDOFF-0042) when the registered tracks are passed. The tables live in `kgme/schema.py`, the
YAML loading in `kgme/frontmatter.py`; reading files and printing live in `kgme/vault.py` and
`kgme/cli.py`.
Inputs: the note's text, its repo-relative path, the ids seen so far, the registered tracks.
Outputs: `Finding` records, each with an ADR-016 class: the schema's checks are `blocking`,
unknown fields and id-format drift are `advisory`, whitespace is `cosmetic`.
Side effects: none.

Datetimes are judged on the strings the author typed: the loader leaves YAML timestamps
unconstructed, so a missing offset or an impossible day is caught here rather than hidden by
YAML's own construction (Michou's note on HANDOFF-0031).
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePosixPath

from kgme import schema
from kgme.frontmatter import parse_frontmatter

TRAILING_SPACE = re.compile(r"[ \t]+$", re.MULTILINE)
NULLABLE_INSTANTS = {("task", "due")}
# Schema v1.6 (HANDOFF-0042): the folders a record may sit in below its root are the state
# folders and the registered tracks' folders; anything else is blocking.
RECORD_ROOTS = ("docs/handoff", "docs/audit")
STATE_FOLDERS = ("done", "proposed", "archive")
TRACK_KEYS = ("handoff", "audit", "handoff_folder", "audit_folder")


@dataclass(frozen=True)
class Track:
    """A registered track (`kgme.toml [tracks.<name>]`): the id prefixes its handoffs and
    reports carry, and the folders they live in, repo-relative without a trailing `/`."""

    name: str
    handoff: str
    audit: str
    handoff_folder: str
    audit_folder: str


def read_tracks(settings: dict) -> tuple[Track, ...]:
    """Pure: the registered tracks of a parsed `kgme.toml`. A table with none of the four
    registration keys (only `lanes`, say) registers nothing; one with some but not all is a
    ValueError, so a half-written registration is loud rather than silently ignored."""
    found: list[Track] = []
    for name, table in sorted((settings.get("tracks") or {}).items()):
        present = [key for key in TRACK_KEYS if key in table]
        if not present:
            continue
        if len(present) < len(TRACK_KEYS):
            missing = sorted(set(TRACK_KEYS) - set(present))
            raise ValueError(f"kgme.toml [tracks.{name}] is missing {', '.join(missing)}")
        folders = {key: str(table[key]).rstrip("/") for key in ("handoff_folder", "audit_folder")}
        found.append(Track(name, str(table["handoff"]), str(table["audit"]), **folders))
    return tuple(found)


@dataclass(frozen=True)
class Finding:
    """One rule broken in one file. `cls` is the ADR-016 class that decides what happens."""

    path: str
    rule: str
    cls: str
    message: str

    def line(self) -> str:
        """One line, whatever the message contained: a YAML error spans several."""
        return f"{self.path}: {self.rule} [{self.cls}] {' '.join(self.message.split())}"


def _is_instant(value: object) -> bool:
    """A string in the schema's instant shape that names a real moment with an offset."""
    if not isinstance(value, str) or not schema.DATETIME.match(value):
        return False
    try:
        return datetime.fromisoformat(value).tzinfo is not None
    except ValueError:
        return False


def _named(value: object) -> bool:
    """A non-empty string: what `origin` and each entry of `sources` must be."""
    return isinstance(value, str) and value.strip() != ""


def lint_note(
    text: str,
    rel_path: str,
    ids_seen: dict[str, str],
    tracks: tuple[Track, ...] | None = None,
) -> list[Finding]:
    """Every finding for one note. `ids_seen` maps id to the path that first carried it and
    is updated here, so uniqueness is checked across a whole run. With `tracks` (the run
    over the repository passes them), the track rules of schema v1.6 apply too; a caller
    linting one machine-written note passes none."""
    found: list[Finding] = []

    def add(rule: str, cls: str, message: str) -> None:
        found.append(Finding(rel_path, rule, cls, message))

    try:
        data, _ = parse_frontmatter(text)
    except ValueError as error:
        add("frontmatter", "blocking", str(error))
        return found

    odd_keys = [key for key in data if not isinstance(key, str)]
    if odd_keys:
        add(
            "frontmatter",
            "blocking",
            f"key(s) {odd_keys!r} are not strings; YAML reads bare `on`, `yes`, `no`, `off` "
            "as booleans, so quote such a key",
        )
    data = {str(key): value for key, value in data.items()}

    note_type = data.get("type")
    if note_type not in schema.TYPES:
        add("enum", "blocking", f"type `{note_type}` is not one of the ten types")
        note_type = None

    required = ["id", "type", "created", "status", "tier"]
    if note_type != "handoff":
        required += ["source", "author"]
    if note_type not in schema.APPEND_ONLY:
        required.append("modified")
    for field in required:
        if field not in data:
            add("required", "blocking", f"missing `{field}`")
    if note_type == "handoff" and "author" in data:
        add("required", "blocking", "a handoff carries `from`, never `author`")

    if "id" in data:
        identifier = str(data["id"])
        if identifier in ids_seen:
            add(
                "unique-id", "blocking", f"id `{identifier}` already used by {ids_seen[identifier]}"
            )
        else:
            ids_seen[identifier] = rel_path
        if not schema.id_family_known(identifier):
            add("id-format", "advisory", f"id `{identifier}` matches no named id family")

    for field in schema.DATETIME_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if value is None and (note_type, field) in NULLABLE_INSTANTS:
            continue
        if not _is_instant(value):
            why = "null is not allowed here" if value is None else "ISO 8601 with an offset"
            add("datetime", "blocking", f"`{field}` is not an instant ({why})")

    if note_type and "status" in data and data["status"] not in schema.STATUS[note_type]:
        add("enum", "blocking", f"status `{data['status']}` is not in the {note_type} vocabulary")
    if "tier" in data and (type(data["tier"]) is not int or data["tier"] not in (2, 3)):
        add("enum", "blocking", f"tier must be the integer 2 or 3, got {data['tier']!r}")

    source = data.get("source")
    if "source" in data and source not in schema.SOURCES:
        add("enum", "blocking", f"source `{source}` is not stated, inferred, or fetched")
    legacy_report = note_type == "report" and schema.predates_provenance(data.get("created"))
    if source == "fetched" and not legacy_report and not _named(data.get("origin")):
        add("provenance", "blocking", "`source: fetched` requires a non-empty `origin`")
    if source == "inferred" and not legacy_report:
        sources = data.get("sources")
        if not (isinstance(sources, list) and sources and all(_named(s) for s in sources)):
            add("provenance", "blocking", "`source: inferred` requires a list of named `sources`")

    if note_type == "handoff":
        if "from" in data and data["from"] not in schema.FROM_VALUES:
            add("enum", "blocking", f"from `{data['from']}` is not a known actor")
        if data.get("status") == "done" and "completed" not in data:
            add("type-field", "blocking", "a done handoff needs `completed`")
    elif "author" in data and data["author"] not in schema.AUTHORS:
        add("enum", "blocking", f"author `{data['author']}` is not human or a known agent")

    if note_type:
        found.extend(_type_fields(data, note_type, rel_path, legacy_report))
        found.extend(_folder(data, note_type, rel_path))
    if tracks is not None:
        found.extend(_track(data, note_type, rel_path, tracks))

    unknown = sorted(set(data) - schema.KNOWN_FIELDS)
    if unknown:
        add("unknown-field", "advisory", "fields not named in the schema: " + ", ".join(unknown))
    if TRAILING_SPACE.search(text):
        add("whitespace", "cosmetic", "trailing whitespace")
    if text and not text.endswith("\n"):
        add("whitespace", "cosmetic", "no newline at end of file")
    return found


def _type_fields(data: dict, note_type: str, rel_path: str, legacy_report: bool) -> list[Finding]:
    found: list[Finding] = []

    def add(message: str, cls: str = "blocking") -> None:
        found.append(Finding(rel_path, "type-field", cls, message))

    for field in schema.TYPE_FIELDS[note_type]:
        if field == "period" and legacy_report:
            continue
        if field not in data:
            add(f"a {note_type} needs `{field}`")
    if note_type == "daily" and "date" in data and not schema.DATE.match(str(data["date"])):
        add("`date` must be YYYY-MM-DD")
    if note_type == "task" and "priority" in data:
        priority = data["priority"]
        if type(priority) is not int or not 1 <= priority <= 3:
            add(f"priority must be 1, 2, or 3, got {priority!r}")
    if note_type == "project":
        mode = data.get("mode")
        if "mode" in data and mode not in ("contained", "indexed"):
            add(f"mode must be contained or indexed, got {mode!r}")
        if mode == "indexed" and not _named(data.get("path")):
            add("an indexed project needs `path`")
    if note_type == "person" and "aliases" in data and not isinstance(data["aliases"], list):
        add("`aliases` must be a list")
    if note_type == "source" and "retention" in data:
        if data["retention"] not in ("discard", "keep"):
            add(f"retention must be discard or keep, got {data['retention']!r}")
    if note_type == "decision" and isinstance(data.get("supersedes"), list):
        if any(not isinstance(item, str) for item in data["supersedes"]):
            add("`supersedes` entries should be ids", "advisory")
    return found


def _folder(data: dict, note_type: str, rel_path: str) -> list[Finding]:
    found: list[Finding] = []
    path = PurePosixPath(rel_path)
    parent = str(path.parent)
    if not schema.folder_allows(note_type, parent):
        found.append(
            Finding(rel_path, "folder", "blocking", f"a {note_type} may not live in {parent}/")
        )
    if note_type == "daily" and (not schema.DATE.match(path.stem) or path.suffix != ".md"):
        found.append(Finding(rel_path, "folder", "blocking", "a daily note is YYYY-MM-DD.md"))
    author = data.get("author")
    if author == "human" and schema.under(parent, schema.MACHINE_FOLDERS):
        found.append(
            Finding(rel_path, "author-folder", "advisory", "a human note under a machine folder")
        )
    if author in schema.AUTHORS and author != "human":
        if schema.under(parent, schema.HUMAN_FOLDERS):
            found.append(
                Finding(
                    rel_path, "author-folder", "advisory", f"a {author} note under a human folder"
                )
            )
    return found


def _track(
    data: dict, note_type: str | None, rel_path: str, tracks: tuple[Track, ...]
) -> list[Finding]:
    """Schema v1.6: a record below `docs/handoff/` or `docs/audit/` sits in a state folder or
    a registered track's folder, and a handoff or report in a track's folder carries that
    track's id prefix."""
    found: list[Finding] = []
    parts = PurePosixPath(rel_path).parent.parts
    for root in RECORD_ROOTS:
        depth = len(PurePosixPath(root).parts)
        if parts[:depth] != PurePosixPath(root).parts or len(parts) == depth:
            continue
        folder = "/".join(parts[: depth + 1])
        registered = {t.handoff_folder for t in tracks} | {t.audit_folder for t in tracks}
        if parts[depth] not in STATE_FOLDERS and folder not in registered:
            message = f"{folder}/ is neither a state folder nor a registered track's folder"
            found.append(Finding(rel_path, "track-folder", "blocking", message))
    identifier = str(data.get("id", ""))
    parent = str(PurePosixPath(rel_path).parent)
    for track in tracks:
        for kind, folder, prefix in (
            ("handoff", track.handoff_folder, track.handoff),
            ("report", track.audit_folder, track.audit),
        ):
            inside = parent == folder or parent.startswith(folder + "/")
            if note_type == kind and inside and not identifier.startswith(prefix + "-"):
                message = f"a {kind} in {folder}/ carries the {prefix}- prefix, not `{identifier}`"
                found.append(Finding(rel_path, "track-id", "blocking", message))
    return found


def lint_files(
    files: list[tuple[str, str]], tracks: tuple[Track, ...] | None = None
) -> list[Finding]:
    """Findings for many notes, `(rel_path, text)` pairs, with id uniqueness across all of them.

    A note that makes the validator itself raise becomes a blocking finding naming the error,
    so one bad file cannot stop the scan and the failure is still loud (ADR-015)."""
    ids_seen: dict[str, str] = {}
    found: list[Finding] = []
    for rel_path, text in files:
        try:
            found.extend(lint_note(text, rel_path, ids_seen, tracks))
        except Exception as error:  # noqa: BLE001 - reported as a blocking finding, not swallowed
            message = f"validator raised {type(error).__name__}: {error}"
            found.append(Finding(rel_path, "validator", "blocking", message))
    return found


def counts(findings: list[Finding]) -> dict[str, int]:
    """How many findings of each class."""
    return {
        cls: sum(1 for f in findings if f.cls == cls)
        for cls in ("blocking", "transient", "cosmetic", "advisory")
    }
