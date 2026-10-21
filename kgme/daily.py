"""`kgme daily`, the pure half: from what the day left behind to the text of its daily note.

Purpose: draft the daily note (HANDOFF-0050) so the habit Michou wanted (today, learned,
problems and solutions, tomorrow, friction) arrives without typing. Five sections from the
template, every line citing what it came from: `Today` from the day's ledger outcomes and its
commits, `Learned` from the day's reports and rulings, `Problems and solutions` from the
day's blocked, refused, and failed outcomes and what cleared them, `Tomorrow` from the open
handoffs and the reminders and tasks due by the end of the next day, `Friction` from the
log's lines dated that day. Those sections are `inferred` and the frontmatter says so; a
closing `Michou` section holds his own words, held by `kgme capture daily` before the draft,
marked `stated`. A day with no ledger event drafts nothing.
Inputs: a `Day` of facts already read and validated, the note's id, the clock, the zone.
Outputs: the note's text, or None.
Side effects: none.
"""

from dataclasses import dataclass
from datetime import date as calendar_date
from datetime import timedelta, tzinfo

from kgme import brief, capture

DRAFTED = "<!-- source: inferred; drafted by kgme daily from {what} -->"
QUIET_JOBS = ("sync", "daily")
SYNC_SUBJECT = "ledger: "  # the subject of every commit `kgme sync` makes (HANDOFF-0040)
MOVES_LISTED = 3
HELD = "held for the draft"  # the outcome of a daily line held until the draft


@dataclass(frozen=True)
class Commit:
    """One commit of the day: short hash, subject, and the handoff files it renamed."""

    sha: str
    subject: str
    moved: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Doc:
    """A handoff or report read from `docs/`: id, path, title, and its frontmatter."""

    id: str
    rel: str
    title: str
    data: dict


@dataclass(frozen=True)
class Day:
    """Everything one draft is built from, already read."""

    date: str
    events: tuple[dict, ...]
    commits: tuple[Commit, ...] | None
    git_note: str
    handoffs: tuple[Doc, ...]
    reports: tuple[Doc, ...]
    items: tuple[brief.Input, ...]
    friction: tuple[str, ...]
    held: tuple[tuple[str, str], ...]
    unread: tuple[str, ...]


def heading_day(date: str) -> str:
    """`Friday 16 October 2026`, the template's `dddd D MMMM YYYY`."""
    day = calendar_date.fromisoformat(date)
    return f"{day.strftime('%A')} {day.day} {day.strftime('%B %Y')}"


def counted(event: dict) -> bool:
    """An event the draft reads: not a tool call, not a push, not the drafter's own."""
    job = event["job"] or ""
    return not job.startswith("tool:") and job not in QUIET_JOBS


def is_problem(event: dict) -> bool:
    """A failed or refused outcome, or a review cycle that blocked."""
    if event["kind"] != "outcome":
        return False
    if event["status"] in ("error", "refused"):
        return True
    return (event["job"] or "").startswith("review:") and " BLOCK" in event["summary"]


def is_solution(event: dict) -> bool:
    """An `ok` outcome that is not a blocked review, or Michou's override of a halt."""
    if event["kind"] == "approval":
        return True
    return event["kind"] == "outcome" and event["status"] == "ok" and not is_problem(event)


def cite(event: dict) -> str:
    return f"{event['summary']} ({event['id']})"


def _moves(moved: tuple[tuple[str, str], ...]) -> list[str]:
    """Each handoff file a commit moved, or, past `MOVES_LISTED`, a count per destination."""
    if len(moved) <= MOVES_LISTED:
        return [f"  - moved {old} → {new}" for old, new in moved]
    folders: dict[str, int] = {}
    for _, new in moved:
        folder = new.rsplit("/", 1)[0] + "/"
        folders[folder] = folders.get(folder, 0) + 1
    return [f"  - moved {count} handoff file(s) to {where}" for where, count in folders.items()]


def _today(day: Day, cited: list[str]) -> list[str]:
    lines = []
    if day.commits is None:
        lines.append(f"- commits not read: {day.git_note}")
    synced = 0
    for commit in day.commits or ():
        if commit.subject.startswith(SYNC_SUBJECT):
            synced += 1
            continue
        lines.append(f"- commit {commit.sha} {commit.subject}")
        cited.append(f"commit {commit.sha}")
        lines.extend(_moves(commit.moved))
    if synced:
        lines.append(f"- {synced} ledger commit(s) by kgme sync")
    for doc in day.handoffs:
        completed = str(doc.data.get("completed") or "")
        if doc.data.get("status") == "done" and completed[:10] == day.date:
            lines.append(f"- {doc.id} done: {doc.title} ({doc.rel})")
            cited.append(doc.id)
    for event in day.events:
        if not counted(event) or event["kind"] not in ("outcome", "note"):
            continue
        if (event["key"] or "").startswith("ruling:") or event["summary"].startswith(HELD):
            continue
        if is_problem(event) or (event["kind"] == "note" and event["source"] != "human"):
            continue
        lines.append(f"- {cite(event)}")
        cited.append(event["id"])
    calls = [
        e for e in day.events if (e["job"] or "").startswith("tool:") and e["kind"] == "intent"
    ]
    if calls:
        sessions = len({e["run_id"] for e in calls})
        lines.append(f"- {len(calls)} agent tool calls in {sessions} session(s), in the ledger")
    return lines or ["- Nothing recorded beyond tool calls."]


def _learned(day: Day, cited: list[str]) -> list[str]:
    lines = []
    for doc in day.reports:
        lines.append(f"- {doc.id}: {doc.title} ({doc.rel})")
        cited.append(doc.id)
    for event in day.events:
        if event["kind"] == "note" and (event["key"] or "").startswith("ruling:"):
            lines.append(f"- {cite(event)}")
            cited.append(event["id"])
    return lines or ["- No report and no ruling today."]


def answers(problem: dict, later: dict) -> bool:
    """Whether `later` clears `problem`, by an explicit relation only (review cycle 1 F5):
    Michou's override of the same review, a later PASS of the same review (a review job is
    one handoff's), or a later `ok` outcome under the same key (a capture's key is its words,
    kind, due, and day). Two unrelated runs of one job never answer each other."""
    if later["id"] <= problem["id"]:
        return False
    if later["kind"] == "approval":
        return later["job"] == problem["job"]
    if not is_solution(later):
        return False
    if (problem["job"] or "").startswith("review:"):
        return later["job"] == problem["job"]
    return problem["key"] is not None and later["key"] == problem["key"]


def _problems(day: Day, cited: list[str]) -> list[str]:
    """Each problem in order, then what cleared it, once for the problems it clears together,
    or `still open` when nothing answered it that day."""
    lines = []
    problems = [e for e in day.events if counted(e) and is_problem(e)]
    answered = [next((e for e in day.events if answers(p, e)), None) for p in problems]
    for index, (problem, cleared) in enumerate(zip(problems, answered, strict=True)):
        lines.append(f"- problem: {cite(problem)}")
        cited.append(problem["id"])
        later = answered[index + 1 :]
        if cleared is not None and any(c is not None and c["id"] == cleared["id"] for c in later):
            continue
        if cleared is None:
            lines.append("  - still open at the end of the day")
        else:
            lines.append(f"- solved: {cite(cleared)}")
            cited.append(cleared["id"])
    for why in day.unread:
        lines.append(f"- not read for this draft: {why}")
    return lines or ["- Nothing blocked, failed, or was refused today."]


def _tomorrow(day: Day, zone: tzinfo, cited: list[str]) -> list[str]:
    lines = []
    for doc in day.handoffs:
        if doc.data.get("status") == "open":
            lines.append(f"- open handoff {doc.id}: {doc.title}")
            cited.append(doc.id)
    by = (calendar_date.fromisoformat(day.date) + timedelta(days=1)).isoformat()
    for item in sorted(day.items, key=brief.sort_key):
        instant = brief.due_instant(item.data.get("due"))
        day_due = instant.astimezone(zone).date().isoformat() if instant else None
        if brief.is_item(item.data) and day_due is not None and day_due <= by:
            lines.append(brief.describe(item, zone))
            cited.append(item.id)
    return lines or ["- No open handoff, and nothing due by the end of tomorrow."]


def _friction(day: Day, cited: list[str]) -> list[str]:
    if day.friction:
        cited.append("FRICTION-LOG")
    return list(day.friction) or ["- No friction captured today."]


def build_daily(day: Day, ident: str, now: str, zone: tzinfo) -> str | None:
    """The whole note, or None for a day with no ledger event."""
    if not [e for e in day.events if e["job"] != "daily"]:
        return None
    cited: list[str] = []
    body = [
        f"# {heading_day(day.date)}",
        "",
        "## Today",
        DRAFTED.format(what="the day's ledger and git log"),
        *_today(day, cited),
        "",
        "## Learned",
        DRAFTED.format(what="the day's reports and rulings"),
        *_learned(day, cited),
        "",
        "## Problems and solutions",
        DRAFTED.format(what="the day's blocked, refused, and failed outcomes"),
        *_problems(day, cited),
        "",
        "## Tomorrow",
        DRAFTED.format(what="the open handoffs and the reminders and tasks due"),
        *_tomorrow(day, zone, cited),
        "",
        "## Friction",
        DRAFTED.format(what="the friction log's lines of the day"),
        *_friction(day, cited),
        "",
        f"## {capture.MICHOU}",
        capture.MICHOU_MARK,
        *[f"- {words}" for _, words in day.held],
    ]
    cited += [event_id for event_id, _ in day.held]
    sources = ", ".join(f'"{s}"' for s in dict.fromkeys(cited)) or '"the day\'s ledger"'
    head = [
        "---",
        f"id: {ident}",
        "type: daily",
        f"date: {day.date}",
        f"created: {now}",
        f"modified: {now}",
        "status: open",
        "tier: 2",
        "source: inferred",
        "author: kgme",
        f"sources: [{sources}]",
        "---",
        "",
    ]
    return "\n".join(head + body) + "\n"
