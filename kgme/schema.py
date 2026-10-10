"""Schema v1.3 as data: the tables of `docs/schema-v1.md`, so `kgme/lint.py` reads like the schema.

Purpose: one place for the ten types, their folders, status vocabularies, type-specific
fields, the required and known field sets, and the id families. A change to the schema
document is a change here and nowhere else.
Inputs: none.
Outputs: constants and small pure predicates over strings.
Side effects: none.
"""

import re

TYPES = (
    "daily",
    "note",
    "reminder",
    "task",
    "project",
    "person",
    "source",
    "decision",
    "handoff",
    "report",
)
APPEND_ONLY = ("decision", "handoff", "report")
SOURCES = ("stated", "inferred", "fetched")
AUTHORS = ("human", "claude-code", "codex", "cowork", "kgme")
FROM_VALUES = AUTHORS + ("michou",)

STATUS = {
    "daily": ("open", "closed"),
    "note": ("draft", "active", "archived"),
    "reminder": ("open", "done", "dismissed"),
    "task": ("open", "doing", "done", "dropped"),
    "project": ("active", "paused", "done"),
    "person": ("active", "archived"),
    "source": ("quarantined", "extracted", "discarded", "kept"),
    "decision": ("proposed", "accepted", "superseded"),
    "handoff": ("proposed", "open", "done", "abandoned", "superseded"),
    "report": ("final",),
}

# Repo-relative directories a type may live in. `docs` means the docs root itself, not its
# subtree; every other entry covers the directory and anything under it.
FOLDERS = {
    "daily": ("memory/daily",),
    "note": ("memory/notes", "memory/agent", "memory/inbox", "docs", "docs/plans", "docs/readers"),
    "reminder": ("memory/notes", "memory/agent"),
    "task": ("memory/notes", "memory/agent"),
    "project": ("memory/notes",),
    "person": ("memory/notes",),
    "source": ("memory/agent",),
    "decision": ("docs/adr",),
    "handoff": ("docs/handoff", "docs/handoff/proposed"),
    "report": ("docs/audit", "memory/agent"),
}
HUMAN_FOLDERS = ("memory/notes", "memory/inbox")
MACHINE_FOLDERS = ("memory/agent",)

# Keys that must be present per type; a value may be null where the schema says so.
TYPE_FIELDS = {
    "daily": ("date",),
    "note": (),
    "reminder": ("due", "repeat", "channel"),
    "task": ("due", "project", "priority"),
    "project": ("mode",),
    "person": ("aliases", "context"),
    "source": ("origin", "hash", "fetched", "retention"),
    "decision": ("supersedes",),
    "handoff": ("from", "to"),
    "report": ("handoff", "period"),
}
DATETIME_FIELDS = ("created", "modified", "due", "fetched", "completed", "accepted")
COMMON_FIELDS = ("id", "type", "created", "modified", "status", "tier", "source", "author")
OPTIONAL_FIELDS = ("project", "people", "tags", "origin", "hash", "sources", "supersedes")
NAMED_EXTRAS = (
    "depends_on",
    "plan_ref",
    "superseded_by",
    "audit_ref",
    "accepted_by",
    "version",
    "period",
    "completed",
    "path",
)
KNOWN_FIELDS = frozenset(
    COMMON_FIELDS
    + OPTIONAL_FIELDS
    + NAMED_EXTRAS
    + tuple(field for fields in TYPE_FIELDS.values() for field in fields)
)

ID_FAMILIES = (
    re.compile(r"^\d{8}T\d{6}$"),
    re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$"),
    re.compile(r"^ADR-\d{3}$"),
    re.compile(r"^HANDOFF-\d{4}$"),
    re.compile(r"^AUDIT-\d{4}$"),
    re.compile(r"^CDH-\d{4}$"),
    re.compile(r"^AUDIT-CDH-\d{4}$"),
    re.compile(r"^PLAN-[A-Z0-9-]+$"),
    re.compile(r"^READER-[A-Z0-9-]+$"),
    re.compile(r"^(STATUS|ROADMAP|CORRECTIONS)$"),
)
# The schema's example has whole seconds; fractional seconds are still ISO 8601 with an offset
# and are what the ledger writes, so they are accepted (stated in AUDIT-0022).
DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?[+-]\d{2}:\d{2}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Schema v1.3: reports created before this day are held to the fields that existed when they
# were written; `period`, and `origin` or `sources`, apply from this day on (Michou, 2026-09-20).
PROVENANCE_CUTOFF = "2026-09-14"


def predates_provenance(created: object) -> bool:
    """True for a report created before the day v1.2 widened the schema to `docs/`."""
    return isinstance(created, str) and created[:10] < PROVENANCE_CUTOFF


def folder_allows(note_type: str, rel_parent: str) -> bool:
    """True if a note of `note_type` may live in the repo-relative directory `rel_parent`."""
    for allowed in FOLDERS.get(note_type, ()):
        if allowed == "docs":
            if rel_parent == "docs":
                return True
        elif rel_parent == allowed or rel_parent.startswith(allowed + "/"):
            return True
    return False


def under(rel_parent: str, folders: tuple[str, ...]) -> bool:
    """True if `rel_parent` is one of `folders` or lies under one."""
    return any(rel_parent == f or rel_parent.startswith(f + "/") for f in folders)


def id_family_known(identifier: str) -> bool:
    """True if `identifier` matches one of the named id families."""
    return any(pattern.match(identifier) for pattern in ID_FAMILIES)
