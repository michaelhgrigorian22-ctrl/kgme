"""`kgme capture` and `kgme daily`, the record: events, payloads, reconciliation, retries.

Purpose: what the two jobs write to and read from the ledger (HANDOFF-0050). Every write is
announced by an `intent` whose payload (under `logs/scratch/payloads/`, bound by sha256 in
the intent and read back only through `ledger.read_payload`) holds the destination, the
mode (`new`, `replace`, `hold`), the offset and size, the exact bytes added, for a replace
the hashes of the whole file as read and as intended, and the words: what a
reconciliation checks and what the output is reconstructed from, never the summary the
redactor may change (review cycle 1 F4, F8); what an unsettled intent left is read by
`kgme.capture_recover`. A capture
carries an idempotency key (kind, words, due words, day); an `ok` answer under the same key
means a retry writes nothing (F3). A replace also leaves a `kept` note naming its intent and
the sha256 prefixes (32 hex digits, which the redactor leaves alone) of the file as read
and as intended: the durable record, since payloads are
disposable, that a kept copy is checked against (the rulings on cycle 6 F13 and F15).
Inputs: a `brief_read.Places`, the run id, keys, summaries, records.
Outputs: event dicts and ids; records; counts; whether evidence was found.
Side effects: `write_intent` writes one payload and appends one intent; `write_kept_note`
appends one note; `write_outcome` and
`write_failure` append outcomes (and an intent); `read_*` read the ledger and payloads.
"""

import hashlib
import json
import re
import sys

from kgme import brief_read, clean_fs, events, ledger

JOB = "capture"
ACTOR = "kgme.capture"
HELD = "hold"
KEPT = "capture:kept:"
KEPT_DIGITS = 32  # under the redactor's 40-character token rule; clean compares its 16
KEPT_SUMMARY = re.compile(
    r"^kept copy of \S+: before (?P<before>[0-9a-f]{32}) after (?P<after>[0-9a-f]{32})$"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture_key(kind: str, words: str, due: str | None, day: str) -> str:
    """The idempotency key: the same words, kind, due words, and day are the same capture."""
    digest = sha256_bytes("\0".join((kind, words, due or "", day)).encode("utf-8"))[:16]
    return f"capture:{kind}:{day}:{digest}"


def job_event(
    kind: str, run_id: str, key: str, summary: str, job: str = JOB, actor: str = ACTOR, **more
) -> dict:
    """An event of `job`, its summary redacted before it is clipped: the ledger redacts again,
    and a placeholder longer than what it replaced must not push a clipped summary past the
    cap."""
    return events.make_event(
        source="kgme",
        actor=actor,
        kind=kind,
        job=job,
        key=key,
        run_id=run_id,
        summary=events.clip(events.redact(summary)),
        **more,
    )


def write_intent(
    places: brief_read.Places,
    run_id: str,
    key: str,
    summary: str,
    record: dict,
    job: str = JOB,
    actor: str = ACTOR,
) -> str:
    """The payload, written new and whole, then the intent that binds it by hash."""
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    payload = places.payloads / f"{job}-{run_id}-{events.new_ulid()}.json"
    try:
        clean_fs.write_payload(places.record, payload, text)
    except clean_fs.Refused as refused:
        raise clean_fs.Refused(f"payload directory: {refused}") from refused
    intent = job_event(
        "intent",
        run_id,
        key,
        summary,
        job=job,
        actor=actor,
        payload_ref=payload.relative_to(places.record).as_posix(),
        payload_sha256=sha256_bytes(text.encode("utf-8")),
    )
    return ledger.append(intent, places.dirs)


def write_outcome(
    places: brief_read.Places, run_id: str, key: str, intent_id: str, summary: str, **more
) -> None:
    """The `ok` outcome answering `intent_id`."""
    event = job_event(
        "outcome", run_id, key, summary, status="ok", ref=intent_id, parent=intent_id, **more
    )
    ledger.append(event, places.dirs)


def read_record(places: brief_read.Places, intent: dict) -> dict | None:
    """The record an intent's payload holds, when the payload is the evidence it bound."""
    data, _ = ledger.read_payload(places.record, intent)
    if data is None:
        return None
    try:
        record = json.loads(data)
    except ValueError:
        return None
    return record if isinstance(record, dict) else None


def read_done(places: brief_read.Places, key: str) -> dict | None:
    """The latest intent under `key` an `ok` outcome answered, if any: the capture is done."""
    done = [e for e in ledger.read_ok_intents(JOB, places.dirs) if e["key"] == key]
    return done[-1] if done else None


def write_failure(
    places: brief_read.Places,
    run_id: str,
    key: str,
    opened: list[str],
    status: str,
    why: str,
    job: str = JOB,
    actor: str = ACTOR,
) -> int:
    """One outcome of class `blocking` under the run's intent, or under one appended now."""
    intent_id = opened[0] if opened else ""
    if not intent_id:
        intent = job_event("intent", run_id, key, f"{job} refused", job=job, actor=actor)
        intent_id = ledger.append(intent, places.dirs)
    head = "refused" if status == "refused" else "failed"
    ledger.append(
        job_event(
            "outcome",
            run_id,
            key,
            f"{head}: {why}",
            job=job,
            actor=actor,
            status=status,
            class_="blocking",
            ref=intent_id,
            parent=intent_id,
        ),
        places.dirs,
    )
    print(f"kgme {job}: {head}: {why}", file=sys.stderr)
    return 1


def write_kept_note(
    places: brief_read.Places, run_id: str, intent_id: str, before: bytes, after: bytes
) -> None:
    """The record a kept copy is checked against: the hashes of the file as read and as
    intended, under the intent's id, before the copy exists."""
    was, will = sha256_bytes(before)[:KEPT_DIGITS], sha256_bytes(after)[:KEPT_DIGITS]
    summary = f"kept copy of {intent_id}: before {was} after {will}"
    event = job_event(
        "note", run_id, f"{KEPT}{intent_id}", summary, ref=intent_id, parent=intent_id
    )
    ledger.append(event, places.dirs)


def read_kept_hashes(dirs: ledger.Dirs, intent_id: str) -> tuple[str, str] | None:
    """The `before` and `after` sha256 prefixes a capture recorded for the copy it keeps under
    `intent_id`, from its own note only; None when there is none."""
    for event in ledger.read(dirs, stream="ledger"):
        if (event["kind"], event["job"], event["actor"], event["key"]) != (
            "note",
            JOB,
            ACTOR,
            f"{KEPT}{intent_id}",
        ):
            continue
        match = KEPT_SUMMARY.match(event["summary"])
        if match:
            return match["before"], match["after"]
    return None
