"""`kgme clean`, reconciliation on start: the plans an interrupted run left unclosed.

Purpose: ADR-013 §4 for the deleter (HANDOFF-0033). Every plan ends with one `closed:`
outcome; an intent without one belongs to a run that died. With its payload, each planned
path is checked: one an outcome already names, by number, is settled; one absent without an
outcome was deleted before its outcome was written and gets one now, with the size and hash
the payload kept; one still present was not reached and is left for the next plan. Without a
payload nothing can be told, and the plan is closed `transient`. A payload is evidence only
when `ledger.read_payload`, shared with `kgme brief`, finds it a regular file reached
through no link whose bytes hash to the `payload_sha256` the intent recorded, and its
structure is the one `plan_record` writes; otherwise nothing is recorded from it, the plan
is closed `blocking`, and the run stops (review cycle 5 F14). The run holds
`kgme-clean.lock` while it reconciles, so an open intent belongs to a run that has ended
(F15).
Inputs: the checkout, its ledger streams, the run id.
Outputs: how many plans were closed, and how many on evidence that could not be trusted.
Side effects: `read_*` read the ledger and the payloads and stat planned paths;
`write_reconciled_outcomes` appends outcomes to the checkout's own streams.
"""

import json
import os
import re
from pathlib import Path

from kgme import events, ledger
from kgme.clean import fit_summary, fit_text

JOB = "clean"
CLOSE = "closed: "
CAP = events.MAX_SUMMARY_CHARS
NUMBER = re.compile(r"^(?:deleted|removed|refused|error|reconciled) #(\d+)\b")


def _measure(text: str) -> int:
    return max(len(text), len(events.redact(text)))


def read_unclosed_intents(dirs: ledger.Dirs) -> list[dict]:
    """Clean intents no `closed:` outcome answered: a plan a run did not finish recording."""
    everything = ledger.read(dirs, stream="ledger")
    closed = {
        e["ref"]
        for e in everything
        if e["kind"] == "outcome" and e["ref"] and e["summary"].startswith(CLOSE)
    }
    return [
        e for e in everything if e["kind"] == "intent" and e["job"] == JOB and e["id"] not in closed
    ]


def read_numbers_recorded(dirs: ledger.Dirs, intent_id: str) -> set[int]:
    """The plan numbers an outcome under `intent_id` already names, whatever its verb."""
    found: set[int] = set()
    for event in ledger.read(dirs, stream="ledger"):
        if event["kind"] == "outcome" and event["ref"] == intent_id:
            match = NUMBER.match(event["summary"])
            if match:
                found.add(int(match.group(1)))
    return found


def write_reconciled_outcomes(base: Path, dirs: ledger.Dirs, run_id: str) -> tuple[int, int]:
    """Close every plan an interrupted run left open (ADR-013 §4). With its payload, each
    planned path is checked: one an outcome already names is settled; one absent without an
    outcome was deleted before its outcome was written and gets one now, with the size and
    hash the payload kept; one still present was not reached and is left for the next plan.
    Without a payload nothing can be told. The plan is then closed as `transient`, and the
    run goes on to plan afresh. A payload that is not the evidence the intent recorded closes
    its plan `blocking`. Returns how many plans were closed, and how many of those blocking."""
    opened = read_unclosed_intents(dirs)
    untrusted = 0
    for intent in opened:
        key, intent_id = intent["key"], intent["id"]
        recorded = read_numbers_recorded(dirs, intent_id)
        data, problem = ledger.read_payload(ledger.read_record_root(base), intent)
        if data is None and not problem:
            summary = f"{CLOSE}reconciled on start: intent {intent_id} left no payload to check"
            write_recovery_outcome(dirs, run_id, key, intent_id, summary, "error", "transient")
            continue
        record, problem = read_plan(data) if data is not None else (None, problem)
        if record is None:
            untrusted += 1
            summary = (
                f"{CLOSE}reconciled on start: payload of {intent_id}: {problem}; "
                "nothing recorded from it"
            )
            write_recovery_outcome(dirs, run_id, key, intent_id, summary, "error", "blocking")
            continue
        unrecorded = present = 0
        for item in [*record["files"], *record["dirs"]]:
            if item["n"] in recorded:
                continue
            if read_present(base, item):
                present += 1
                continue
            unrecorded += 1
            if "sha256" in item:
                head = f"reconciled #{item['n']}: absent, deleted before its outcome was written; "
                head += f"{item['size']} B sha256 {item['sha256']} "
            else:
                head = f"reconciled #{item['n']}: absent, removed before its outcome was written; "
            summary = fit_summary(head, item["path"], "", CAP, _measure)
            write_recovery_outcome(dirs, run_id, key, intent_id, summary, "ok")
        summary = (
            f"{CLOSE}reconciled on start: {unrecorded} deleted without an outcome, "
            f"{present} planned and still present"
        )
        write_recovery_outcome(dirs, run_id, key, intent_id, summary, "error", "transient")
    return len(opened), untrusted


def read_plan(data: bytes) -> tuple[dict | None, str]:
    """The plan in a payload's verified bytes (`ledger.read_payload`), or None and why the
    bytes are not one: not JSON, or not the structure `plan_record` writes."""
    try:
        record = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "is not the JSON a plan writes"
    if not well_formed(record):
        return None, "is not the structure a plan writes"
    return record, ""


def well_formed(record: object) -> bool:
    """Whether `record` has the shape `plan_record` writes: lists of numbered paths, files
    with a size and a sha256 prefix."""
    if not isinstance(record, dict):
        return False
    files, dirs = record.get("files"), record.get("dirs")
    if not isinstance(files, list) or not isinstance(dirs, list):
        return False
    for item in [*files, *dirs]:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get("n"), int) or not isinstance(item.get("path"), str):
            return False
    for item in files:
        if not isinstance(item.get("size"), int) or not isinstance(item.get("sha256"), str):
            return False
    return True


def read_present(base: Path, item: dict) -> bool:
    """Whether a planned name is still there, by `lstat`, a link included; a path that cannot
    be stat for any reason but absence counts as present: not reached, left for the next plan
    to refuse."""
    try:
        os.lstat(base / item["path"])
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return True


def write_recovery_outcome(
    dirs: ledger.Dirs,
    run_id: str,
    key: str,
    intent_id: str,
    summary: str,
    status: str,
    cls: str | None = None,
) -> str:
    """One outcome a reconciliation writes under the open plan's intent, fitted to the cap."""
    event = events.make_event(
        source="kgme",
        actor="kgme.clean",
        kind="outcome",
        job=JOB,
        key=key,
        run_id=run_id,
        summary=fit_text(summary, CAP, _measure),
        status=status,
        class_=cls,
        ref=intent_id,
        parent=intent_id,
    )
    return ledger.append(event, dirs)
