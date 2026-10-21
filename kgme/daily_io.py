"""`kgme daily`, the effects: read what the day left behind, then create its note once.

Purpose: draft `memory/daily/<date>.md` (HANDOFF-0050) around the pure `kgme.daily`. Under
the vault lock it shares with `kgme capture`, it closes its own open intents, does nothing
when the note exists (a second run, or a note Michou began himself), does nothing when the
ledger holds no event of the day, and otherwise reads, every file through the brief's one
gated reader under this job's manifest: the day's ledger events, the day's commits by a
bounded read-only `git log` (the ledger carries no commit subject and no handoff move), the
handoffs and the day's reports under `docs/`, the open reminders and tasks, the friction
log, and the daily lines `kgme capture` held for the day. The note is created new, never
through a link and never over a file (`clean_fs.write_payload`), under one `intent` and one
`outcome`; a refusal or failure is one classified outcome under an intent.
Inputs: the day, the checkout to act on, the parsed `kgme.toml`, the clock.
Outputs: an exit code: 0 written or nothing to do, 1 refused or failed, 2 not a day; the
path and the note on stdout.
Side effects: one new file under `memory/daily/`; ledger events; one `git log`; the lock.
"""

import os
import re
import subprocess
import sys
from datetime import date as calendar_date
from datetime import datetime, time, timedelta
from pathlib import Path

from kgme import (
    brief,
    brief_read,
    capture,
    capture_fs,
    capture_io,
    capture_recover,
    clean_fs,
    daily,
    events,
    ledger,
    lint,
)
from kgme import capture_record as record
from kgme.sync_git import run_git

JOB = "daily"
ACTOR = "kgme.daily"
MANIFEST = Path("jobs") / "daily" / "manifest.toml"
HANDOFF_DIRS = ("docs/handoff", "docs/handoff/done")
AUDIT_DIR = "docs/audit"
REVIEW_AUDIT = re.compile(r"^AUDIT-\d+-review-")
HELD_PREFIX = "capture daily held "


def _title(body: str, rel: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return rel


def read_docs(
    places: brief_read.Places, folders: tuple[str, ...], unread: list[str]
) -> list[daily.Doc]:
    """The `.md` files directly in each folder, read through the gate; what cannot be read
    or parsed is named in `unread`, never fatal to the draft."""
    found = []
    for folder in folders:
        top = places.base / folder
        if not top.is_dir():
            continue
        for path in sorted(top.glob("*.md")):
            rel = path.relative_to(places.base).as_posix()
            if path.name == "README.md":
                continue
            try:
                text = brief_read.read_gated(places, path).decode("utf-8")
                data, body = brief_read.frontmatter_of(text, rel)
            except (clean_fs.Refused, UnicodeDecodeError) as error:
                unread.append(f"{rel}: {error}")
                continue
            found.append(daily.Doc(str(data.get("id")), rel, _title(body, rel), data))
    return found


def read_commits(
    places: brief_read.Places, date: str, zone, settings: dict
) -> tuple[tuple[daily.Commit, ...] | None, str]:
    """The day's commits in this checkout, oldest first, with the handoff files each
    renamed; None and why when the manifest refuses git or git cannot answer."""
    verdict = places.allowed("tool", "git")
    if not verdict.allowed:
        return None, verdict.reason
    start = datetime.combine(calendar_date.fromisoformat(date), time(0), tzinfo=zone)
    end = start + timedelta(days=1)
    args = [
        "log",
        "--reverse",
        "-M",
        "--name-status",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
        "--format=%x1e%h%x09%s",
    ]
    try:
        done = run_git(
            args, places.base, check=False, timeout=settings["sync"]["git_timeout_seconds"]
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f"git log did not answer: {error}"
    if done.returncode != 0:
        return None, f"git log exited {done.returncode}: {done.stderr.strip()[:120]}"
    commits = []
    for entry in done.stdout.split("\x1e"):
        lines = [line for line in entry.splitlines() if line.strip()]
        if not lines:
            continue
        sha, _, subject = lines[0].partition("\t")
        moved = []
        for line in lines[1:]:
            parts = line.split("\t")
            if parts[0].startswith("R") and len(parts) == 3 and "docs/handoff/" in parts[1]:
                moved.append((parts[1], parts[2]))
        commits.append(daily.Commit(sha, subject, tuple(moved)))
    return tuple(commits), ""


def read_held(places: brief_read.Places, date: str, unread: list[str]) -> list[tuple[str, str]]:
    """The daily lines `kgme capture` held for `date`, as (intent id, words), in order: the
    words from the payload when it is the evidence its intent bound, from the verbatim
    summary only when the payload is gone (the arbiter's ruling on cycle 2 F2); a payload
    that disagrees is named in `unread`, never overridden."""
    held = []
    prefix = f"{capture_recover.HELD_SUMMARY}{date}: "
    for intent in ledger.read_ok_intents(record.JOB, places.dirs):
        if not capture_recover.is_held(intent) or not intent["summary"].startswith(prefix):
            continue
        data, why = ledger.read_payload(places.base, intent)
        if data is None and why:
            unread.append(f"held line {intent['id']}: {why}")
            continue
        found = record.read_record(places, intent) if data is not None else None
        words = found["words"] if found else intent["summary"][len(prefix) :]
        held.append((intent["id"], words))
    return held


def read_day(places: brief_read.Places, date: str, settings: dict) -> daily.Day:
    """Every fact the draft is built from."""
    zone = brief_read.read_zone(settings)
    day_events = [e for e in ledger.read(places.dirs, stream="ledger") if e["ts"][:10] == date]
    unread: list[str] = []
    commits, git_note = read_commits(places, date, zone, settings)
    handoffs = read_docs(places, HANDOFF_DIRS, unread)
    reports = [
        doc
        for doc in read_docs(places, (AUDIT_DIR,), unread)
        if doc.data.get("type") == "report"
        and str(doc.data.get("created") or "")[:10] == date
        and not REVIEW_AUDIT.match(Path(doc.rel).name)
    ]
    input_paths, unlisted = brief_read.read_input_paths(places.base, date)
    inputs, refusals = brief_read.read_inputs(places, input_paths)
    unread += unlisted + refusals
    friction = next((i for i in inputs if i.rel == brief.FRICTION_PATH), None)
    lines = brief.friction_entries(friction.text, date) if friction else []
    return daily.Day(
        date=date,
        events=tuple(day_events),
        commits=commits,
        git_note=git_note,
        handoffs=tuple(handoffs),
        reports=tuple(reports),
        items=tuple(i for i in inputs if i.data.get("type") in ("reminder", "task")),
        friction=tuple(line for line in lines if line.startswith(f"- {date}")),
        held=tuple(read_held(places, date, unread)),
        unread=tuple(unread),
    )


def run_daily(
    date: str, base: Path, settings: dict, now: datetime | None = None, dry_run: bool = False
) -> int:
    """The run inside one failure boundary, as `kgme capture`'s. Under the vault lock, the
    open intents of both jobs are closed first, so a held line whose capture was interrupted
    is in the draft (review cycle 1 F2)."""
    if not brief.valid_date(date):
        print(f"kgme daily: {date!r} is not a day written YYYY-MM-DD", file=sys.stderr)
        return 2
    places = capture_io.read_places(settings, base, MANIFEST)
    now = (now or datetime.now()).astimezone(brief_read.read_zone(settings))
    run_id = events.new_ulid()
    key = f"daily:{date}"
    opened: list[str] = []
    lock = None
    try:
        lock = capture_fs.write_lock(base, capture_fs.LOCK_WAIT_SECONDS)
        if lock is None:
            raise clean_fs.Refused("another capture or daily run holds the vault; try again")
        if not dry_run:
            reconciled = capture_recover.write_reconciled_outcomes(places, run_id)
            reconciled += capture_recover.write_reconciled_outcomes(places, run_id, JOB, ACTOR)
            if reconciled:
                print(f"kgme daily: reconciled {reconciled} open intent(s)")
        return run_steps(places, settings, date, now, run_id, key, opened, dry_run)
    except clean_fs.Refused as refused:
        return write_failed(places, run_id, key, opened, "refused", str(refused))
    except OSError as error:
        return write_failed(places, run_id, key, opened, "error", f"{error.strerror or error}")
    except Exception as error:
        write_failed(places, run_id, key, opened, "error", f"{type(error).__name__}: {error}")
        raise
    finally:
        if lock is not None:
            os.close(lock)


def write_failed(
    places: brief_read.Places, run_id: str, key: str, opened: list[str], status: str, why: str
) -> int:
    """The failure boundary's record for this job: after the announce, the intent closed by
    what the file holds (`capture_recover.write_settled`); before it, one refused or failed
    outcome (`capture_record.write_failure`)."""
    if opened:
        return capture_recover.write_settled(places, run_id, opened[0], why, JOB, ACTOR)
    return record.write_failure(places, run_id, key, opened, status, why, JOB, ACTOR)


def run_steps(
    places: brief_read.Places,
    settings: dict,
    date: str,
    now: datetime,
    run_id: str,
    key: str,
    opened: list[str],
    dry_run: bool,
) -> int:
    """Nothing when the note exists or the day is empty; else build, validate, and publish
    the note under a payload-bound intent, or print it for a dry run."""
    destination = places.base / capture.DAILY_DIR / f"{date}.md"
    rel = destination.relative_to(places.base).as_posix()
    if os.path.lexists(destination):
        print(f"kgme daily: {rel} exists; nothing to do")
        return 0
    day = read_day(places, date, settings)
    ident = events.new_ulid()
    text = daily.build_daily(day, ident, capture.instant_text(now), now.tzinfo)
    if text is None:
        print(f"kgme daily: no ledger event on {date}; nothing written")
        return 0
    blocking = [f for f in lint.lint_note(text, rel, {}) if f.cls == "blocking"]
    if blocking:
        raise clean_fs.Refused(f"the draft fails the validator: {blocking[0].line()}")
    count = len(day.events)
    if dry_run:
        print(f"kgme daily: dry run; would write {rel}")
        print(text, end="")
        summary = f"daily {date} dry run: would write {rel} from {count} events"
        event = record.job_event("note", run_id, f"{key}:dry-run", summary, job=JOB, actor=ACTOR)
        ledger.append(event, places.dirs)
        return 0
    capture_io.read_allowed(places, ("write",), destination)
    data = text.encode("utf-8")
    facts = {
        "job": JOB,
        "mode": "new",
        "destination": rel,
        "offset": 0,
        "size": len(data),
        "sha256": record.sha256_bytes(data),
        "bytes": text,
    }
    summary = f"daily draft {rel} new: {count} events"
    opened.append(record.write_intent(places, run_id, key, summary, facts, JOB, ACTOR))
    capture_fs.write_new(places.base, destination, text)
    done = f"drafted {rel} id {ident} from {count} events"
    record.write_outcome(places, run_id, key, opened[0], done, job=JOB, actor=ACTOR)
    print(f"kgme daily: wrote {rel}")
    print(text, end="")
    return 0
