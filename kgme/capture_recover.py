"""`kgme capture` and `kgme daily`, recovery: what an uncertain write left, and what to do.

Purpose: one classifier for every write whose result the ledger does not settle (review
cycle 2 F2, F3; the arbiter's ruling after AUDIT-0062, F10: every write is whole, so there
is no fragment to find). After its announce, an open intent or an `error` outcome says
nothing about the bytes; the file does. `read_state` compares the file's bytes with what the
intent's payload recorded: `done` (a new note holds exactly its bytes; a replaced file
hashes to its intended bytes and its kept copy, if still there, to the bytes it was read
as), `absent` (no new note; a replaced file still hashes to the bytes it was read as and its
kept copy, if any, to the capture's own), `conflict` (anything else: a kept copy that
changed holds a save the file lacks; the rulings on cycle 6 F13 and F15), `unknown` (the
payload is gone or is not the evidence its intent bound). A held daily line is `done` from
its key and its verbatim summary alone. Reconciliation on start closes `done` `ok` and
`absent` `transient`, and stops the run on `conflict` or `unknown`, naming the file. A
failure after the announce is classified before its intent is closed. A retry checks the
earlier attempts under its key: an `ok` answer is "already captured" without reading bytes
(Michou edits these files), any other attempt is classified. Before a line is added to a
file, every kept copy beside it is checked against the hashes its capture recorded, and the
capture refuses, naming the copy, while one differs (Fable's amendment to the same ruling):
the file lacks a save that copy holds.
Inputs: a `brief_read.Places`, intents, their records, the run id.
Outputs: states, counts, refusals.
Side effects: `write_*` append ledger events; `read_*` read the ledger, payloads, and gated
files.
"""

import os
import sys
from pathlib import Path

from kgme import brief_read, capture_fs, clean_fs, ledger
from kgme import capture_record as record
from kgme.capture_record import JOB

HELD_SUMMARY = "capture daily held "


def is_held(intent: dict) -> bool:
    """A daily line held until the draft: its words are its summary, verbatim by construction."""
    key, summary = intent["key"] or "", intent["summary"]
    return key.startswith("capture:daily:") and summary.startswith(HELD_SUMMARY)


def read_state(places: brief_read.Places, intent: dict) -> tuple[str, dict | None]:
    """`done`, `absent`, `conflict`, or `unknown`, and the intent's record when it has one."""
    if is_held(intent):
        return "done", record.read_record(places, intent)
    found = record.read_record(places, intent)
    if found is None or found.get("mode") not in ("new", "replace"):
        return "unknown", found
    path = places.base / found["destination"]
    if not os.path.lexists(path):
        return ("absent" if found["mode"] == "new" else "conflict"), found
    try:
        raw = brief_read.read_gated(places, path)
    except clean_fs.Refused:
        return "conflict", found
    if found["mode"] == "new":
        return ("done" if raw == found["bytes"].encode("utf-8") else "conflict"), found
    digest = record.sha256_bytes(raw)
    kept = read_kept_digest(places, path, intent["id"])
    before, after = found.get("before_sha256") or "", found.get("after_sha256") or ""
    if digest == after and kept in (None, before):
        return "done", found
    if digest == before and kept in (None, after):
        return "absent", found
    return "conflict", found


def read_kept_digest(places: brief_read.Places, path: Path, intent_id: str) -> str | None:
    """The sha256 of the copy the replace under `intent_id` kept beside `path`, None when
    there is none, `unreadable` when it cannot be read through the gate."""
    kept = path.parent / capture_fs.kept_name(path.name, intent_id)
    if not os.path.lexists(kept):
        return None
    try:
        return record.sha256_bytes(brief_read.read_gated(places, kept))
    except clean_fs.Refused:
        return "unreadable"


def read_divergent(places: brief_read.Places, path: Path) -> None:
    """`clean_fs.Refused`, naming it, while a copy kept beside `path` no longer hashes to
    either value its capture recorded, or has no record: `path` lacks what it holds."""
    rel = path.relative_to(places.base).as_posix()
    for name in sorted(os.listdir(path.parent)):
        match = capture_fs.KEPT_NAME.match(name)
        if match is None or match["name"] != path.name:
            continue
        recorded = record.read_kept_hashes(places.dirs, match["id"])
        digest = read_kept_digest(places, path, match["id"]) or ""
        if recorded is None or digest[: record.KEPT_DIGITS] not in recorded:
            raise clean_fs.Refused(
                f"{name} beside {rel} holds what {rel} lacks; merge it by hand, then delete it"
            )


def write_closed(
    places: brief_read.Places,
    run_id: str,
    intent: dict,
    state: str,
    why: str,
    job: str = JOB,
    actor: str = record.ACTOR,
) -> None:
    """Close `intent` by its state: `ok` when done, `transient` when absent, `blocking`
    otherwise, the state and `why` in the summary."""
    status, cls = ("ok", None) if state == "done" else ("error", "transient")
    if state not in ("done", "absent"):
        cls = "blocking"
    event = record.job_event(
        "outcome",
        run_id,
        intent["key"] or "",
        f"{why}: {state}",
        job=job,
        actor=actor,
        status=status,
        class_=cls,
        ref=intent["id"],
        parent=intent["id"],
    )
    ledger.append(event, places.dirs)


def write_reconciled_outcomes(
    places: brief_read.Places, run_id: str, job: str = JOB, actor: str = record.ACTOR
) -> int:
    """Close every open intent of `job` by what its file holds; `clean_fs.Refused` after
    closing one that is `conflict` or `unknown`."""
    count = 0
    for intent in ledger.open_intents(job, places.dirs):
        count += 1
        if intent["payload_ref"] is None and not is_held(intent):
            # a refusal's own intent: nothing was announced, nothing written
            write_closed(places, run_id, intent, "absent", "reconciled", job, actor)
            continue
        state, found = read_state(places, intent)
        write_closed(places, run_id, intent, state, "reconciled", job, actor)
        if state in ("conflict", "unknown"):
            where = (found or {}).get("destination") or intent["summary"]
            raise clean_fs.Refused(f"an earlier write to {where} is {state}; repair it by hand")
    return count


def write_settled(
    places: brief_read.Places,
    run_id: str,
    intent_id: str,
    why: str,
    job: str = JOB,
    actor: str = record.ACTOR,
) -> int:
    """The failure boundary after an announce: the intent is closed by what its file holds
    (`ok` when the bytes landed, so a retry is "already captured"), and the exit code is 0
    only then."""
    intent = next(e for e in ledger.read(places.dirs, stream="ledger") if e["id"] == intent_id)
    state, _ = read_state(places, intent)
    write_closed(places, run_id, intent, state, f"failed after the announce ({why})", job, actor)
    if state == "done":
        print(f"kgme {job}: written, then failed: {why}", file=sys.stderr)
        return 0
    print(f"kgme {job}: failed: {why} ({state})", file=sys.stderr)
    return 1


def read_attempts(places: brief_read.Places, key: str) -> list[dict]:
    """The write intents under `key` no `ok` outcome answered (refusals carry no payload)."""
    answered = {e["id"] for e in ledger.read_ok_intents(JOB, places.dirs)}
    return [
        e
        for e in ledger.read(places.dirs, stream="ledger")
        if e["job"] == JOB
        and e["kind"] == "intent"
        and e["key"] == key
        and e["payload_ref"] is not None
        and e["id"] not in answered
    ]


def read_retry(places: brief_read.Places, key: str) -> dict | None:
    """What earlier attempts under `key` settle: the attempt found done (the capture is
    made), None when every one is absent; `clean_fs.Refused` on `conflict` or `unknown`."""
    for intent in read_attempts(places, key):
        state, found = read_state(places, intent)
        if state == "done":
            return intent
        if state in ("conflict", "unknown"):
            where = (found or {}).get("destination") or intent["summary"]
            raise clean_fs.Refused(f"an earlier attempt at {where} is {state}; check it by hand")
    return None
