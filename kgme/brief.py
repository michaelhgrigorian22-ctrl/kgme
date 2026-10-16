"""`kgme brief` v1, the pure half: from validated inputs to the text of one day's brief.

Purpose: Loop 0 (HANDOFF-0034), model-free. Given the notes read from the vault, select
what the brief is about (open reminders, open and doing tasks, the day's daily note, the
friction log), sort them deterministically (due, then priority, then id), and render the
artefact: frontmatter per `docs/schema-v1.md` (`note`, `inferred`, `sources` naming every
input) and the five sections `Due and overdue`, `Today`, `Open tasks`, `Friction since last
brief`, `Inputs`. A missing daily note and an empty section are stated, never omitted.
Inputs: `Input` records (repo-relative path, id, text, sha256 of the file's bytes,
frontmatter, body), the day, an `Identity` (id, created, modified) to keep across
replacements, the previous brief's day, and the zone in which due instants are read
(`kgme.toml` `[brief] timezone`).
Outputs: strings; a `Selection`; a content hash that ignores `modified`.
Side effects: none.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime, tzinfo
from datetime import date as calendar_date

DAILY_DIR = "memory/daily"
FRICTION_PATH = "memory/inbox/friction-log.md"
BRIEF_DIR = "memory/agent/brief"
HEADING = re.compile(r"^##\s+(.+?)\s*$")
FRICTION_LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2})")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
IDENTITY = re.compile(r"id=(?P<id>\S+) created=(?P<created>\S+) modified=(?P<modified>\S+)")
BODY_HASH = re.compile(r"body=(?P<body>[0-9a-f]{16})")
NO_DUE = "9999-99-99"
DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True)
class Input:
    """One note the brief may draw on, as read and validated."""

    rel: str
    id: str
    text: str
    sha256: str
    data: dict
    body: str


@dataclass(frozen=True)
class Identity:
    """What a replaced brief keeps: its id and `created`; `modified` moves only when the
    content does, so a brief rebuilt from the same inputs is byte-identical."""

    id: str
    created: str
    modified: str


@dataclass(frozen=True)
class Selection:
    """The inputs the brief is about, in deterministic order."""

    items: tuple[Input, ...]
    daily: Input | None
    friction: Input | None

    def inputs(self) -> list[Input]:
        found = list(self.items)
        found += [i for i in (self.daily, self.friction) if i is not None]
        return sorted(found, key=lambda i: i.id)


def is_item(data: dict) -> bool:
    """An open reminder, or an open or doing task."""
    kind, status = data.get("type"), data.get("status")
    return (kind == "reminder" and status == "open") or (
        kind == "task" and status in ("open", "doing")
    )


def valid_date(text: str) -> bool:
    """Whether `text` is a real day written `YYYY-MM-DD`, and nothing else: it becomes a
    path, a heading, and a ledger key (review cycle 1 F7)."""
    if not DAY.fullmatch(text):
        return False
    try:
        return calendar_date.fromisoformat(text).isoformat() == text
    except ValueError:
        return False


def due_instant(due: object) -> datetime | None:
    """The instant a `due` value names, or None when there is none or it carries no offset."""
    if not isinstance(due, str):
        return None
    try:
        instant = datetime.fromisoformat(due)
    except ValueError:
        return None
    return instant if instant.tzinfo is not None else None


def sort_key(item: Input) -> tuple[str, int, str]:
    """Due first, by the instant in UTC so offsets compare correctly (none last), then
    priority (a reminder sorts as 0), then id (review cycle 1 F9)."""
    instant = due_instant(item.data.get("due"))
    priority = item.data.get("priority", 0) if item.data.get("type") == "task" else 0
    due = instant.astimezone(UTC).isoformat() if instant else NO_DUE
    return (due, int(priority), item.id)


def select(inputs: list[Input], date: str) -> Selection:
    """Items sorted; the day's daily note and the friction log by path; briefs never."""
    items = [i for i in inputs if not i.rel.startswith(BRIEF_DIR + "/") and is_item(i.data)]
    daily = next((i for i in inputs if i.rel == f"{DAILY_DIR}/{date}.md"), None)
    friction = next((i for i in inputs if i.rel == FRICTION_PATH), None)
    return Selection(tuple(sorted(items, key=sort_key)), daily, friction)


def title_of(item: Input) -> str:
    """The first `#` heading, else the first non-empty body line, else the file's stem."""
    for line in item.body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    for line in item.body.splitlines():
        if line.strip():
            return line.strip()
    return item.rel.rsplit("/", 1)[-1].removesuffix(".md")


def when(due: object, zone: tzinfo) -> str:
    """`2026-10-09 09:00`, the instant as read in the brief's zone, or `no due date`."""
    instant = due_instant(due)
    if instant is None:
        return "no due date"
    return instant.astimezone(zone).strftime("%Y-%m-%d %H:%M")


def describe(item: Input, zone: tzinfo) -> str:
    """One line for an item: when, title, then type, id, priority, status, project."""
    data = item.data
    tail = [f"{data.get('type')} {item.id}"]
    if data.get("type") == "task":
        tail.append(f"priority {data.get('priority')}")
        tail.append(str(data.get("status")))
    if data.get("project"):
        tail.append(str(data["project"]))
    return f"- {when(data.get('due'), zone)}  {title_of(item)}  ({', '.join(tail)})"


def sections(body: str) -> list[tuple[str, list[str]]]:
    """A daily note's `##` sections in order, each with its non-empty lines, comments removed."""
    found: list[tuple[str, list[str]]] = []
    for line in COMMENT.sub("", body).splitlines():
        heading = HEADING.match(line)
        if heading:
            found.append((heading.group(1), []))
        elif found and line.strip():
            found[-1][1].append(line.rstrip())
    return found


def friction_entries(text: str, since: str | None) -> list[str]:
    """Dated entries of the friction log on or after `since`; all of them without a cutoff.
    Inclusive on purpose: repeating a line is harmless, dropping one is not."""
    entries = []
    for line in text.splitlines():
        match = FRICTION_LINE.match(line)
        if match and (since is None or match.group(1) >= since):
            entries.append(line.rstrip())
    return entries


def _due_section(items: tuple[Input, ...], date: str, zone: tzinfo) -> list[str]:
    """Overdue and due-today items, the day each falls on read in the brief's zone."""
    lines = []
    for item in items:
        instant = due_instant(item.data.get("due"))
        day = instant.astimezone(zone).date().isoformat() if instant else None
        if day is not None and day < date:
            lines.append("- overdue " + describe(item, zone)[2:])
        elif day == date:
            lines.append("- due today " + describe(item, zone)[2:])
    return lines or ["Nothing due today and nothing overdue."]


def _today_section(daily: Input | None, date: str) -> list[str]:
    if daily is None:
        return [f"No daily note for {date} (expected {DAILY_DIR}/{date}.md)."]
    lines = [f"From {daily.rel}:"]
    shown = 0
    for heading, content in sections(daily.body):
        if heading.lower() == "friction" or not content:
            continue
        lines.append(f"{heading}:")
        lines.extend(content)
        shown += 1
    if shown == 0:
        lines.append("Daily note present, its sections empty.")
    return lines


def _tasks_section(items: tuple[Input, ...], zone: tzinfo) -> list[str]:
    lines = [describe(i, zone) for i in items if i.data.get("type") == "task"]
    return lines or ["No open tasks."]


def _friction_section(selection: Selection, since: str | None) -> list[str]:
    lines = [f"Since {since}, the previous brief:" if since else "All entries, no previous brief:"]
    count = 0
    if selection.friction is not None:
        entries = friction_entries(selection.friction.text, since)
        lines.extend(entries)
        count += len(entries)
    else:
        lines.append(f"No friction log at {FRICTION_PATH}.")
    if selection.daily is not None:
        for heading, content in sections(selection.daily.body):
            if heading.lower() == "friction" and content:
                lines.append("From the daily note's Friction section:")
                lines.extend(content)
                count += len(content)
    if count == 0:
        lines.append("No friction recorded.")
    return lines


def _inputs_section(selection: Selection) -> list[str]:
    return [f"- {i.id} — {i.rel} — sha256 {i.sha256}" for i in selection.inputs()]


def build_brief(
    selection: Selection, date: str, identity: Identity, since: str | None, zone: tzinfo
) -> str:
    """The whole artefact, frontmatter and body, deterministic for the same inputs and zone."""
    sources = ", ".join(f'"{i.id}"' for i in selection.inputs())
    head = [
        "---",
        f"id: {identity.id}",
        "type: note",
        f"created: {identity.created}",
        f"modified: {identity.modified}",
        "status: active",
        "tier: 2",
        "source: inferred",
        "author: kgme",
        f"sources: [{sources}]",
        "---",
        "",
        f"# Brief {date}",
        "",
        "## Due and overdue",
        *_due_section(selection.items, date, zone),
        "",
        "## Today",
        *_today_section(selection.daily, date),
        "",
        "## Open tasks",
        *_tasks_section(selection.items, zone),
        "",
        "## Friction since last brief",
        *_friction_section(selection, since),
        "",
        "## Inputs",
        *_inputs_section(selection),
    ]
    return "\n".join(head) + "\n"


def content_hash(text: str) -> str:
    """Sixteen hex of the sha256 of `text` with its `modified:` line blanked: the identity
    of the content, which decides whether `modified` moves."""
    stable = re.sub(r"^modified: .*$", "modified: -", text, count=1, flags=re.MULTILINE)
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]


def identity_summary(identity: Identity, body: str, date: str) -> str:
    """The intent summary the next run can read an identity back from, scratch or no scratch."""
    return (
        f"brief {date} id={identity.id} created={identity.created} "
        f"modified={identity.modified} body={body}"
    )


def parse_identity(summary: str) -> tuple[Identity, str] | None:
    """The identity and body hash a previous intent summary recorded, else None."""
    match, body = IDENTITY.search(summary), BODY_HASH.search(summary)
    if not match or not body:
        return None
    return Identity(match["id"], match["created"], match["modified"]), body["body"]
