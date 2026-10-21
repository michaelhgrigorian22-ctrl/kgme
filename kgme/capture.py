"""`kgme capture`, the pure half: from Michou's words to the exact bytes one capture writes.

Purpose: capture by talking (HANDOFF-0050). A reminder, task, or note is a new file rendered
from its template in `memory/templates/` with his words as the title, `source: stated`,
`author: kgme`, a ULID `id` (schema v1.5: an agent writes a ULID); a friction entry is one
line in the log's own format; a daily line goes under a closing `## Michou` heading. A `due`
is read from plain words in the configured zone and written ISO 8601 with its offset; what
cannot be read, or is ambiguous, or has passed, is refused with what was not understood.
Inputs: the kind, the words, the due words, the clock as an aware datetime, the zone, the
template's text, the tail of the file an append lands on.
Outputs: strings: the note text, the filename stem, the line or block to append; a datetime;
`Unreadable` with the reason.
Side effects: none.
"""

import re
from dataclasses import dataclass
from datetime import date as calendar_date
from datetime import datetime, time, timedelta, tzinfo

KINDS = ("remind", "task", "friction", "note", "daily")
TEMPLATES = {"remind": "reminder.md", "task": "task.md", "note": "note.md"}
DUE_KINDS = ("remind", "task")
NOTES_DIR = "memory/notes"
DAILY_DIR = "memory/daily"
FRICTION_PATH = "memory/inbox/friction-log.md"
TEMPLATE_DIR = "memory/templates"
MICHOU = "Michou"
MICHOU_MARK = "<!-- source: stated; Michou's words, verbatim, by kgme capture daily -->"
DEFAULT_TIME = time(9, 0)  # the reminder template's own default
SLUG_WORDS = 8
SLUG_CHARS = 60
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)
CLOCK = re.compile(r"^(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s*(?P<ampm>am|pm)?$")
IN_DAYS = re.compile(r"^in (?P<n>\d{1,3}) (?P<unit>days?|weeks?)$")
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LAST_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
CONTROL = re.compile(r"[\x00-\x1f\x7f]")


class Unreadable(ValueError):
    """Words a capture cannot turn into what it writes; the message says what and why."""


@dataclass(frozen=True)
class Item:
    """A new note: the filename stem it wants and its whole text."""

    stem: str
    text: str


def check_words(words: str) -> str:
    """His words, unchanged, or `Unreadable`: a capture is one non-empty line, since a line
    break would split a friction entry or a list item in two."""
    if not words.strip():
        raise Unreadable("nothing to capture: the words are empty")
    if CONTROL.search(words):
        raise Unreadable("the words hold a line break or a control character; capture one line")
    return words


def _weekday(word: str) -> int | None:
    for index, name in enumerate(WEEKDAYS):
        if word == name or (len(word) >= 3 and name.startswith(word)):
            return index
    return None


def _month(word: str) -> int | None:
    for index, name in enumerate(MONTHS, start=1):
        if word == name or (len(word) >= 3 and name.startswith(word)):
            return index
    return None


def _clock(text: str) -> time | None:
    """`9am`, `9:30 pm`, `14:00`, `noon`, `midnight`; None when `text` is not a time."""
    if text == "noon":
        return time(12, 0)
    if text == "midnight":
        return time(0, 0)
    match = CLOCK.match(text)
    if not match or (match["m"] is None and match["ampm"] is None):
        return None
    hour, minute = int(match["h"]), int(match["m"] or 0)
    if match["ampm"]:
        if not 1 <= hour <= 12:
            return None
        hour = hour % 12 + (12 if match["ampm"] == "pm" else 0)
    if hour > 23 or minute > 59:
        return None
    return time(hour, minute)


def _split_clock(words: str) -> tuple[str, time | None]:
    """The day words and the time at their end (`friday 9am`, `tomorrow at 14:00`)."""
    parts = words.split(" ")
    for cut in (2, 1):
        found = _clock(" ".join(parts[-cut:])) if len(parts) >= cut else None
        if found is not None:
            day = parts[:-cut]
            return " ".join(day[:-1] if day[-1:] == ["at"] else day), found
    return words, None


def _day(words: str, today: calendar_date) -> tuple[calendar_date | None, bool]:
    """The day the words name, and whether a weekday was named (so a passed time today
    moves it a week on); `Unreadable` for words that name no day or name it ambiguously."""
    if words in ("", "today"):
        return (today if words else None), False
    if words == "tomorrow":
        return today + timedelta(days=1), False
    if words.startswith("next ") or words.startswith("this "):
        raise Unreadable(
            f"'{words}' is ambiguous (this week's or the next?); name the day or a date"
        )
    weekday = _weekday(words)
    if weekday is not None:
        return today + timedelta(days=(weekday - today.weekday()) % 7), True
    if ISO_DAY.match(words):
        try:
            return calendar_date.fromisoformat(words), False
        except ValueError as error:
            raise Unreadable(f"'{words}' is not a real day") from error
    match = IN_DAYS.match(words)
    if match:
        unit = 7 if match["unit"].startswith("week") else 1
        return today + timedelta(days=int(match["n"]) * unit), False
    parts = words.replace(",", " ").split()
    if len(parts) == 2:
        month, day_text = _month(parts[0]), parts[1]
        if month is None:
            month, day_text = _month(parts[1]), parts[0]
        if month is not None and day_text.isdigit():
            try:
                found = calendar_date(today.year, month, int(day_text))
            except ValueError as error:
                raise Unreadable(f"'{words}' is not a real day") from error
            if found < today:
                found = found.replace(year=today.year + 1)
            return found, False
    raise Unreadable(f"could not read a day in '{words}'")


def resolve_due(words: str, now: datetime, zone: tzinfo) -> datetime:
    """The instant `words` name, read in `zone`: a day (today, tomorrow, a weekday, a date,
    `oct 20`, `in 3 days`) and an optional time (`9am`, `14:00`; 09:00 when none). A time
    alone is its next occurrence; a weekday is the next one, today only while its time is
    ahead. `Unreadable` for anything else, for an ambiguous day, and for an instant passed."""
    text = " ".join(words.lower().replace(",", " ").split())
    if not text:
        raise Unreadable("--due is empty")
    local = now.astimezone(zone)
    day_words, clock = _split_clock(text)
    day, weekday = _day(day_words, local.date())
    if day is None:
        if clock is None:
            raise Unreadable(f"could not read a day or a time in '{words}'")
        due = datetime.combine(local.date(), clock, tzinfo=zone)
        tomorrow = local.date() + timedelta(days=1)
        return due if due > local else datetime.combine(tomorrow, clock, tzinfo=zone)
    due = datetime.combine(day, clock or DEFAULT_TIME, tzinfo=zone)
    if weekday and due <= local:
        due = datetime.combine(day + timedelta(days=7), clock or DEFAULT_TIME, tzinfo=zone)
    if due <= local:
        raise Unreadable(f"'{words}' is {due.isoformat(timespec='minutes')}, already past")
    return due


def instant_text(moment: datetime) -> str:
    """ISO 8601 with its offset, whole seconds: the shape the schema's example shows."""
    return moment.isoformat(timespec="seconds")


def slug(words: str) -> str:
    """A kebab-case filename stem from the first words, ASCII letters and digits only;
    empty when nothing of the words survives."""
    found = re.findall(r"[a-z0-9]+", words.lower())[:SLUG_WORDS]
    stem = "-".join(found)
    if len(stem) > SLUG_CHARS:
        stem = stem[:SLUG_CHARS].rsplit("-", 1)[0]
    return stem


def render_item(
    kind: str, words: str, template: str, ident: str, now: str, due: str | None
) -> Item:
    """The new note from its template: the frontmatter keys in the template's order, with
    `id`, `created`, `modified`, `source`, `author`, and `due` set and every other value the
    template's own; the title placeholder replaced by his words. `Unreadable` when the
    template has no frontmatter, a placeholder survives, or a reminder has no due."""
    if kind == "remind" and due is None:
        raise Unreadable("a reminder needs --due")
    head, sep, body = template.partition("\n---\n")
    if not template.startswith("---\n") or not sep:
        raise Unreadable(f"the {TEMPLATES[kind]} template has no frontmatter block")
    values = {
        "id": ident,
        "created": now,
        "modified": now,
        "source": "stated",
        "author": "kgme",
    }
    if kind in DUE_KINDS:
        values["due"] = due if due is not None else "null"
    lines = []
    for line in head.removeprefix("---\n").splitlines():
        key, colon, _ = line.partition(":")
        lines.append(f"{key}: {values[key]}" if colon and key in values else line)
    text = "---\n" + "\n".join(lines) + "\n---\n" + body.replace("{{title}}", words)
    if "{{" in text.replace(words, ""):
        raise Unreadable(f"the {TEMPLATES[kind]} template holds a placeholder kgme cannot fill")
    if not text.endswith("\n"):
        text += "\n"
    return Item(slug(words) or f"{kind}-{ident.lower()}", text)


def friction_line(words: str, now: datetime) -> str:
    """One entry in the log's stated format, `- YYYY-MM-DD HH:MM — what happened — ...`,
    his words as they came; the separator is his to add."""
    return f"- {now.strftime('%Y-%m-%d %H:%M')} — {words}\n"


def lead(tail: bytes) -> str:
    """A newline when the file does not end with one, so an append starts its own line."""
    return "" if not tail or tail.endswith(b"\n") else "\n"


def ends_under_michou(text: str) -> bool:
    """Whether the last `##` heading of a daily note is the closing `Michou` one."""
    headings = LAST_HEADING.findall(text)
    return bool(headings) and headings[-1] == MICHOU


def daily_block(words: str, under_michou: bool, tail: bytes) -> str:
    """What one `capture daily` appends: the line, after the closing heading when the note
    does not end under it already."""
    head = "" if under_michou else f"\n## {MICHOU}\n{MICHOU_MARK}\n"
    return lead(tail) + head + f"- {words}\n"
