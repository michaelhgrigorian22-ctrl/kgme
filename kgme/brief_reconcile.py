"""`kgme brief` v1, reconciliation on start: the write intents an ended run left open.

Purpose: ADR-013 §4 for the brief (HANDOFF-0034). An intent with no outcome belongs to a run
that ended between its intent and its outcome (`ledger.open_intents`). Its payload says
which destination it meant and the sha256 of the text it meant to write. A payload is
evidence only when `ledger.read_payload`, the verification `kgme clean` shares, finds it a
regular file reached through no link whose bytes hash to the `payload_sha256` the intent
recorded, and it is the JSON a brief writes naming the destination the intent's key names
(review cycle 1 F2). With evidence, the intent is closed `ok` when the
destination holds the intended hash, and `transient` otherwise, since this run rebuilds it.
Without a payload it is closed `transient`. On evidence that cannot be trusted, nothing is
recorded from it, the intent is closed `blocking`, and the run stops. A dry run counts the
open intents and writes nothing (F3).
Inputs: the run's `Places`, the run id.
Outputs: how many intents were closed, and how many of those on untrusted evidence.
Side effects: `read_*` read payloads and destinations; `write_reconciled_outcomes` appends
outcomes to the checkout's own streams.
"""

import hashlib
import json
import os

from kgme import brief, brief_read, clean_fs, events, ledger
from kgme.brief_read import JOB, Places

ACTOR = "kgme.brief"
HEX64 = frozenset("0123456789abcdef")


def well_formed(record: object, expected_destination: str) -> str:
    """Why a payload record is not what a brief writes for this intent, or an empty string."""
    if not isinstance(record, dict):
        return "is not the JSON a brief writes"
    sha = record.get("sha256")
    if not isinstance(sha, str) or len(sha) != 64 or not set(sha) <= HEX64:
        return "carries no sha256 of the text it meant to write"
    if record.get("destination") != expected_destination:
        return f"names another destination than {expected_destination}"
    return ""


def read_intended(places: Places, intent: dict) -> tuple[dict | None, str]:
    """The record an intent's payload holds and an empty string, or None and why it is not
    evidence; (None, "") when the intent left no payload."""
    data, problem = ledger.read_payload(places.base, intent)
    if data is None:
        return None, f"payload {problem}" if problem else ""
    try:
        record = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, f"payload {intent['payload_ref']} is not the JSON a brief writes"
    date = (intent["key"] or "").removeprefix("brief:")
    problem = well_formed(record, f"{brief.BRIEF_DIR}/{date}.md")
    if problem:
        return None, f"payload {intent['payload_ref']} {problem}"
    return record, ""


def read_destination_sha(places: Places, rel: str) -> str | None:
    """The sha256 of the destination as it stands, read through `brief_read.read_gated`, so a
    destination the manifest now forbids is refused before any byte is read; None when
    absent."""
    destination = places.base / rel
    if not os.path.lexists(destination):
        return None
    return hashlib.sha256(brief_read.read_gated(places, destination)).hexdigest()


def write_reconciled_outcomes(places: Places, run_id: str) -> tuple[int, int]:
    """Close every brief intent no outcome answered, as the module docstring states."""
    opened = ledger.open_intents(JOB, places.dirs)
    untrusted = 0
    for intent in opened:
        record, problem = read_intended(places, intent)
        if record is not None:
            try:
                actual = read_destination_sha(places, record["destination"])
            except clean_fs.Refused as refused:
                record, problem = None, f"destination {refused}"
        if problem:
            untrusted += 1
            summary = f"reconciled on start: {problem}; nothing recorded from it"
            status, cls = "error", "blocking"
        elif record is None:
            summary = f"reconciled on start: intent {intent['id']} left no payload; rebuilt"
            status, cls = "error", "transient"
        elif actual == record["sha256"]:
            summary = f"reconciled on start: {record['destination']} present with the intended hash"
            status, cls = "ok", None
        else:
            summary = f"reconciled on start: {record['destination']} not the intended text; rebuilt"
            status, cls = "error", "transient"
        ledger.append(
            events.make_event(
                source="kgme",
                actor=ACTOR,
                kind="outcome",
                job=JOB,
                key=intent["key"],
                run_id=run_id,
                summary=events.clip(summary),
                status=status,
                class_=cls,
                ref=intent["id"],
                parent=intent["id"],
            ),
            places.dirs,
        )
    return len(opened), untrusted
