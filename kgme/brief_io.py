"""`kgme brief` v1, the writing half of the effects: the transaction and the run.

Purpose: run Loop 0 (HANDOFF-0034) around the pure `kgme.brief`, the readers in
`kgme.brief_read`, and reconciliation in `kgme.brief_reconcile`, and write
`memory/agent/brief/<date>.md` as one transaction: `intent` before any write, a temp file
created inside a checked directory descriptor, every byte written and fsynced,
`os.replace` within that descriptor, `outcome` after (review cycle 1 F1, F5). A day that is
not a real `YYYY-MM-DD` exits 2 before anything (F7). Every refusal before the intent is
one `intent` and one `refused` outcome of class `blocking`; a failed write after it is an
`error` outcome of class `blocking` (F6). A dry run reconciles nothing and appends one
`note` (F3).
Inputs: the day, whether this is a dry run, the checkout to act on, the parsed `kgme.toml`.
Outputs: an exit code: 0 written or dry run, 1 refused or failed, 2 not a day; lines on
stdout and stderr.
Side effects: `write_brief` creates and replaces files under the brief folder; `run_brief`
writes the payload through `kgme.clean_fs.write_payload`; `write_*` and `run_brief` append
ledger events to the checkout's own streams.
"""

import json
import os
import sys
from pathlib import Path

from kgme import brief, brief_kept, brief_read, brief_reconcile, clean_fs, events, ledger, lint
from kgme.brief_read import JOB, Places

ACTOR = "kgme.brief"


def write_brief(base: Path, destination: Path, text: str) -> None:
    """The one write: a temp file created inside a descriptor on the brief folder, checked
    after it was opened, every byte written and fsynced, then `os.replace` within that
    descriptor, so the destination holds the previous brief or the whole new one. On any
    failure the temp file is removed and the error raised."""
    clean_fs.read_no_link_above(destination, base)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dir_fd = clean_fs.read_bound_directory(destination.parent, base)
    temp = f".{destination.name}.tmp-{events.new_ulid()}"
    try:
        fd = os.open(temp, clean_fs.NEW_FILE_FLAGS, 0o644, dir_fd=dir_fd)
        try:
            clean_fs.write_whole(fd, text.encode("utf-8"))
        finally:
            os.close(fd)
        os.replace(temp, destination.name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except BaseException:
        try:
            os.unlink(temp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        raise
    finally:
        os.close(dir_fd)


def _event(kind: str, run_id: str, key: str, summary: str, **more) -> dict:
    return events.make_event(
        source="kgme",
        actor=ACTOR,
        kind=kind,
        job=JOB,
        key=key,
        run_id=run_id,
        summary=events.clip(summary),
        **more,
    )


def write_failure(
    places: Places, run_id: str, key: str, date: str, opened: list[str], status: str, why: str
) -> int:
    """The one failure boundary's record (Cowork's ruling on review cycle 2 F6): one outcome
    of class `blocking`, `refused` or `error`, under the run's write intent when one was
    appended, else under one intent appended now. Exactly one intent and one outcome."""
    intent_id = opened[0] if opened else ""
    if not intent_id:
        verb = "refused" if status == "refused" else "failed"
        intent_id = ledger.append(
            _event("intent", run_id, key, f"brief {date} {verb}"), places.dirs
        )
    head = "refused" if status == "refused" else f"brief {date} not written"
    ledger.append(
        _event(
            "outcome",
            run_id,
            key,
            f"{head}: {why}",
            status=status,
            class_="blocking",
            ref=intent_id,
            parent=intent_id,
        ),
        places.dirs,
    )
    print(f"kgme brief: {head}: {why}", file=sys.stderr)
    return 1


def refuse(lines: list[str]) -> clean_fs.Refused:
    """A refusal carrying every reason: each printed, the first in the summary."""
    for line in lines[1:]:
        print(f"kgme brief: also refused: {line}", file=sys.stderr)
    more = f" (+{len(lines) - 1} more)" if len(lines) > 1 else ""
    return clean_fs.Refused(f"{lines[0]}{more}")


def run_brief(date: str, dry_run: bool, base: Path, settings: dict) -> int:
    """The run inside one failure boundary: any refusal or exception after the day is known
    good becomes one classified outcome under an intent (`write_failure`); a refusal or an
    `OSError` exits 1, anything else is recorded and raised, loudly (ADR-015)."""
    refused = ledger.read_worktree_refusal(base)
    if refused:
        print(f"kgme brief: {refused}", file=sys.stderr)
        return 2
    if not brief.valid_date(date):
        print(f"kgme brief: {date!r} is not a day written YYYY-MM-DD", file=sys.stderr)
        return 2
    places = brief_read.read_places(settings, base)
    run_id = events.new_ulid()
    key = f"brief:{date}"
    opened: list[str] = []
    try:
        return run_steps(places, settings, run_id, key, date, dry_run, opened)
    except clean_fs.Refused as refused:
        return write_failure(places, run_id, key, date, opened, "refused", str(refused))
    except OSError as error:
        why = f"{error.strerror or error}"
        return write_failure(places, run_id, key, date, opened, "error", why)
    except Exception as error:
        why = f"{type(error).__name__}: {error}"
        write_failure(places, run_id, key, date, opened, "error", why)
        raise


def run_steps(
    places: Places,
    settings: dict,
    run_id: str,
    key: str,
    date: str,
    dry_run: bool,
    opened: list[str],
) -> int:
    """Reconcile (not on a dry run), read and validate, select, keep the identity, build,
    validate the output, then write once under an intent/outcome pair, or print it for a dry
    run. Every refusal is raised, for the boundary in `run_brief` to record."""
    base = places.base
    now = brief_read.read_clock()
    if dry_run:
        waiting = len(ledger.open_intents(JOB, places.dirs))
        if waiting:
            print(f"kgme brief: {waiting} open intent(s) left for the next real run")
    else:
        reconciled, untrusted = brief_reconcile.write_reconciled_outcomes(places, run_id)
        if reconciled:
            print(f"kgme brief: reconciled {reconciled} open intent(s)")
        if untrusted:
            print(
                f"kgme brief: stopped; {untrusted} open intent(s) left evidence that cannot be "
                "trusted, closed blocking",
                file=sys.stderr,
            )
            return 1
    destination = base / brief.BRIEF_DIR / f"{date}.md"
    rel_dest = destination.relative_to(base).as_posix()
    input_paths, unlisted = brief_read.read_input_paths(base, date)
    inputs, refusals = brief_read.read_inputs(places, input_paths)
    kept, unlisted_kept = brief_kept.read_kept_copies(places)
    refusals = unlisted + refusals + unlisted_kept
    selection = brief.select(inputs, date)
    if not refusals and not selection.inputs():
        refusals.append("no inputs under memory/; seed the vault (HANDOFF-0035)")
    if refusals:
        raise refuse(refusals)
    identity, recorded_body = brief_read.read_identity(places, destination, date, now)
    zone = brief_read.read_zone(settings)
    since = brief_read.read_previous_brief_date(base, date, places.dirs)
    text = brief.build_brief(selection, date, identity, since, zone, kept)
    body = brief.content_hash(text)
    if body != recorded_body:
        identity = brief.Identity(identity.id, identity.created, now)
        text = brief.build_brief(selection, date, identity, since, zone, kept)
        body = brief.content_hash(text)
    invalid = [f for f in lint.lint_note(text, rel_dest, {}) if f.cls == "blocking"]
    if invalid:
        raise refuse([f"built brief fails the validator: {invalid[0].line()}"])
    count = len(selection.inputs())
    if dry_run:
        print(text, end="")
        summary = f"brief {date} dry run: {count} inputs body={body}"
        ledger.append(_event("note", run_id, f"{key}:dry-run", summary), places.dirs)
        return 0
    verdict = places.allowed("write", destination)
    if not verdict.allowed:
        raise refuse([verdict.reason])
    return run_write(places, run_id, key, date, destination, text, identity, body, count, opened)


def run_write(
    places: Places,
    run_id: str,
    key: str,
    date: str,
    destination: Path,
    text: str,
    identity: brief.Identity,
    body: str,
    count: int,
    opened: list[str],
) -> int:
    """The payload, the intent (its id put in `opened`, so a failure after it is recorded
    under it), the write, the `ok` outcome."""
    rel_dest = destination.relative_to(places.base).as_posix()
    full = brief_read.sha256_text(text)
    record = {
        "destination": rel_dest,
        "sha256": full,
        "id": identity.id,
        "created": identity.created,
        "modified": identity.modified,
        "body": body,
    }
    payload_text = json.dumps(record, indent=2) + "\n"
    payload = places.payloads / f"brief-{date}-{run_id}.json"
    try:
        clean_fs.write_payload(places.record, payload, payload_text)
    except clean_fs.Refused as refused:
        raise clean_fs.Refused(f"payload directory: {refused}") from refused
    intent_id = ledger.append(
        _event(
            "intent",
            run_id,
            key,
            brief.identity_summary(identity, body, date),
            payload_ref=payload.relative_to(places.record).as_posix(),
            payload_sha256=brief_read.sha256_text(payload_text),
        ),
        places.dirs,
    )
    opened.append(intent_id)
    write_brief(places.base, destination, text)
    ledger.append(
        _event(
            "outcome",
            run_id,
            key,
            f"brief {date} written {rel_dest} sha256 {full[:16]} inputs {count}",
            status="ok",
            ref=intent_id,
            parent=intent_id,
        ),
        places.dirs,
    )
    print(f"kgme brief: wrote {rel_dest} ({count} inputs)")
    return 0
