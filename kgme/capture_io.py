"""`kgme capture`, the run: plan one write from Michou's words, then preview or perform it.

Purpose: run one capture (HANDOFF-0050) around the pure `kgme.capture`, the filesystem
effects in `kgme.capture_fs`, and the record in `kgme.capture_record`. A reminder, task, or
note is a new file under `memory/notes/`, published whole under a name that did not exist; a
friction or daily line is added by replacing the file whole (temp, fsync, exchange), every
byte before it kept, so the file is never torn (the arbiter's ruling after AUDIT-0062, F10);
a daily line before the day's note exists is held, verbatim, in the intent's summary and
payload until `kgme daily` drafts the note (creating the note now would stop the draft:
`kgme daily` writes only a note that does not exist). Under the vault lock: open intents are
reconciled, then a capture whose key an `ok` outcome already answered writes nothing and
says so (review cycle 1 F3). One `intent` (with its payload) before the write, one `outcome`
after; a refusal is one intent and one `refused` outcome of class `blocking`, the words in
its summary. `--dry-run` prints what would be written, writes nothing, and appends one
`note` (F7).
Inputs: the kind, the words, the due words, the checkout to act on, the parsed `kgme.toml`,
the clock, whether this is a dry run.
Outputs: an exit code: 0 captured, already captured, or previewed; 1 refused or failed; 2
not a capture. The path and the exact text written on stdout.
Side effects: one new file under `memory/notes/`, or the friction log or the day's note
replaced by itself plus the line; a payload; ledger events in the checkout's own streams;
the lock file.
"""

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from kgme import (
    brief_read,
    capture,
    capture_fs,
    capture_recover,
    clean_fs,
    events,
    ledger,
    lint,
    paths,
    policy,
)
from kgme import capture_record as record
from kgme.capture_record import JOB

MANIFEST = Path("jobs") / "capture" / "manifest.toml"


@dataclass(frozen=True)
class Plan:
    """One capture's write: `new` (the whole text), `replace` (the bytes added, made from
    the file's current bytes), or `hold` (no file); the destination; what the outcome adds."""

    mode: str
    path: Path | None
    build: Callable[[bytes], str]
    detail: str


def read_places(settings: dict, base: Path, manifest: Path = MANIFEST) -> brief_read.Places:
    """The checkout's streams and fences, under a job's own manifest (capture's by default)."""
    blocklist = settings["hooks"]["blocklist"]
    return brief_read.Places(
        base=base,
        dirs=ledger.read_base_dirs(settings, base),
        payloads=paths.payloads_dir(settings, base),
        manifest=policy.read_manifest(paths.root() / manifest),
        blocklist=[paths.resolve(p) for p in blocklist if not p.startswith("**/")],
        patterns=[p[3:] for p in blocklist if p.startswith("**/")],
        tier1=paths.tier1_paths(settings, base),
    )


def read_allowed(places: brief_read.Places, operations: tuple[str, ...], path: Path) -> None:
    """`clean_fs.Refused` unless the manifest allows every operation on `path`."""
    for operation in operations:
        verdict = places.allowed(operation, path)
        if not verdict.allowed:
            raise clean_fs.Refused(verdict.reason.replace(str(places.base) + "/", ""))


def run_capture(
    kind: str,
    words: str,
    due: str | None,
    base: Path,
    settings: dict,
    now: datetime | None = None,
    dry_run: bool = False,
) -> int:
    """One capture inside one failure boundary. Words that are not one line, or a `--due` on
    a kind without one, exit 2 before anything; every later refusal or failure is one
    classified outcome under an intent."""
    try:
        capture.check_words(words)
    except capture.Unreadable as error:
        print(f"kgme capture: {error}", file=sys.stderr)
        return 2
    if due is not None and kind not in capture.DUE_KINDS:
        print(f"kgme capture: --due applies to remind and task, not {kind}", file=sys.stderr)
        return 2
    places = read_places(settings, base)
    now = (now or datetime.now()).astimezone(brief_read.read_zone(settings))
    run_id = events.new_ulid()
    key = record.capture_key(kind, words, due, now.date().isoformat())
    opened: list[str] = []
    lock = None
    try:
        lock = capture_fs.write_lock(base, capture_fs.LOCK_WAIT_SECONDS)
        if lock is None:
            raise clean_fs.Refused("another capture or daily run holds the vault; try again")
        if not dry_run:
            reconciled = capture_recover.write_reconciled_outcomes(places, run_id)
            if reconciled:
                print(f"kgme capture: reconciled {reconciled} open intent(s)")
        done = record.read_done(places, key)
        if done is None and not dry_run:
            done = capture_recover.read_retry(places, key)
        if done is not None:
            print(f"kgme capture: already captured ({done['id']}): {done['summary']}")
            return 0
        plan = read_plan(places, kind, words, due, now)
        if dry_run:
            return run_preview(places, plan, kind, words, run_id, key)
        return run_plan(places, plan, kind, words, now, run_id, key, opened)
    except (clean_fs.Refused, capture.Unreadable) as refused:
        why = f"{refused}; words: {words}"
        if opened:
            return capture_recover.write_settled(places, run_id, opened[0], why)
        return record.write_failure(places, run_id, key, opened, "refused", why)
    except OSError as error:
        why = f"{error.strerror or error}"
        if opened:
            return capture_recover.write_settled(places, run_id, opened[0], why)
        return record.write_failure(places, run_id, key, opened, "error", why)
    except Exception as error:
        why = f"{type(error).__name__}: {error}"
        if opened:
            capture_recover.write_settled(places, run_id, opened[0], why)
        else:
            record.write_failure(places, run_id, key, opened, "error", why)
        raise
    finally:
        if lock is not None:
            os.close(lock)


def read_plan(
    places: brief_read.Places, kind: str, words: str, due: str | None, now: datetime
) -> Plan:
    """What this capture would write and where, validated and allowed, nothing written."""
    if kind in capture.TEMPLATES:
        return read_new_note(places, kind, words, due, now)
    if kind == "friction":
        line = capture.friction_line(words, now)
        path = places.base / capture.FRICTION_PATH
        return read_replace(places, path, lambda existing: capture.lead(existing) + line)
    day = now.date().isoformat()
    path = places.base / capture.DAILY_DIR / f"{day}.md"
    if not os.path.lexists(path):
        summary = f"capture daily held {day}: {words}"
        if len(summary) > events.MAX_SUMMARY_CHARS or events.redact(summary) != summary:
            raise clean_fs.Refused(
                f"no daily note for {day} yet, and these words cannot be held verbatim in the "
                "ledger until the draft (too long, or shaped like a secret); run kgme daily first"
            )
        return Plan(record.HELD, None, lambda _: f"- {words}\n", f"held for the draft of {day}")

    def block(existing: bytes) -> str:
        try:
            text = existing.decode("utf-8")
        except UnicodeDecodeError as error:
            raise clean_fs.Refused(f"{capture.DAILY_DIR}/{day}.md is not valid UTF-8") from error
        return capture.daily_block(words, capture.ends_under_michou(text), existing)

    return read_replace(places, path, block)


def read_new_note(
    places: brief_read.Places, kind: str, words: str, due: str | None, now: datetime
) -> Plan:
    """Resolve the due, render the template, pick a free name, validate, check the manifest."""
    due_text = capture.instant_text(capture.resolve_due(due, now, now.tzinfo)) if due else None
    template_path = places.base / capture.TEMPLATE_DIR / capture.TEMPLATES[kind]
    try:
        template = brief_read.read_gated(places, template_path).decode("utf-8")
    except UnicodeDecodeError as error:
        raise clean_fs.Refused(f"{capture.TEMPLATES[kind]} is not valid UTF-8") from error
    item = capture.render_item(
        kind, words, template, events.new_ulid(), capture.instant_text(now), due_text
    )
    folder = places.base / capture.NOTES_DIR
    destination = folder / f"{item.stem}.md"
    number = 2
    while os.path.lexists(destination):
        destination = folder / f"{item.stem}-{number}.md"
        number += 1
    rel = destination.relative_to(places.base).as_posix()
    blocking = [f for f in lint.lint_note(item.text, rel, {}) if f.cls == "blocking"]
    if blocking:
        raise clean_fs.Refused(f"the note fails the validator: {blocking[0].line()}")
    read_allowed(places, ("write",), destination)
    return Plan("new", destination, lambda _: item.text, f" due {due_text}" if due_text else "")


def read_replace(places: brief_read.Places, path: Path, build: Callable[[bytes], str]) -> Plan:
    rel = path.relative_to(places.base).as_posix()
    if not os.path.lexists(path):
        raise clean_fs.Refused(f"{rel} does not exist; capture adds to it, never creates it")
    read_allowed(places, ("read", "write"), path)
    read_allowed(places, ("read", "write"), path.parent / capture_fs.kept_name(path.name, "0" * 26))
    capture_recover.read_divergent(places, path)
    return Plan("replace", path, build, "")


def run_preview(
    places: brief_read.Places, plan: Plan, kind: str, words: str, run_id: str, key: str
) -> int:
    """`--dry-run`: print the destination and the bytes, write nothing, append one note."""
    existing = b""
    if plan.mode == "replace":
        existing = brief_read.read_gated(places, plan.path)
    text = plan.build(existing)
    where = plan.path.relative_to(places.base).as_posix() if plan.path else "the ledger"
    verb = {"new": "create", "replace": "append to", record.HELD: "hold in"}[plan.mode]
    print(f"kgme capture: dry run; would {verb} {where}{plan.detail}")
    print(text.lstrip("\n"), end="")
    summary = f"capture {kind} dry run: would {verb} {where}: {words}"
    ledger.append(record.job_event("note", run_id, f"{key}:dry-run", summary), places.dirs)
    return 0


def run_plan(
    places: brief_read.Places,
    plan: Plan,
    kind: str,
    words: str,
    now: datetime,
    run_id: str,
    key: str,
    opened: list[str],
) -> int:
    """The payload and intent, the one write, the `ok` outcome, and what was written."""
    rel = plan.path.relative_to(places.base).as_posix() if plan.path else None

    def write_announcement(offset: int, data: bytes, before: bytes | None = None) -> str:
        """The payload and the intent for `data` at `offset`, and for a replace the hashes
        of the file as read and as intended, in the payload and in the `kept` note; its id
        goes in `opened` and is returned."""
        span = "new" if plan.mode == "new" else f"+{offset}:{len(data)}"
        head = f"capture {kind} {rel} {span}" if rel else f"capture daily held {now.date()}"
        facts = {
            "job": JOB,
            "kind": kind,
            "mode": plan.mode,
            "destination": rel,
            "offset": offset,
            "size": len(data),
            "sha256": record.sha256_bytes(data),
            "bytes": data.decode("utf-8"),
            "words": words,
        }
        if before is not None:
            facts["before_sha256"] = record.sha256_bytes(before)
            facts["after_sha256"] = record.sha256_bytes(before + data)
        opened.append(record.write_intent(places, run_id, key, f"{head}: {words}", facts))
        if before is not None:
            record.write_kept_note(places, run_id, opened[0], before, before + data)
        return opened[0]

    if plan.mode == "replace":
        data = capture_fs.write_replaced(places.base, plan.path, plan.build, write_announcement)
    else:
        data = plan.build(b"").encode("utf-8")
        write_announcement(0, data)
        if plan.mode == "new":
            capture_fs.write_new(places.base, plan.path, data.decode("utf-8"))
    text = data.decode("utf-8")
    done = f"captured {kind} {rel}{plan.detail}" if rel else plan.detail
    record.write_outcome(places, run_id, key, opened[0], f"{done}: {text.strip()}")
    verb = {"new": "wrote", "replace": "appended to"}.get(plan.mode)
    print(f"kgme capture: {verb} {rel}{plan.detail}" if verb else f"kgme capture: {plan.detail}")
    print(text.lstrip("\n"), end="")
    return 0
