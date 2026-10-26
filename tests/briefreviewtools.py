"""Helpers for the brief's review-cycle tests (HANDOFF-0034; moved out of
`tests/test_brief_review.py` by HANDOFF-0060 §3, unchanged).

Purpose: plant an open intent with its payload, and read the outcome that closed one.
Inputs: the seeded vault of `tests/brieftools.py`.
Outputs: events and ids.
Side effects: ledger lines and payloads under `tmp_path`.
"""

from pathlib import Path

from brieftools import SETTINGS

from kgme import brief, events, ledger


def plant_intent(base: Path, date: str, payload_text: str | None, sha: str | None) -> dict:
    """An intent a killed run left: its payload (if any) and the sha256 it recorded."""
    dirs = ledger.read_base_dirs(SETTINGS, base)
    ref = None
    if payload_text is not None:
        target = base / "logs" / "scratch" / "payloads" / f"planted-{date}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload_text)
        ref = target.relative_to(base).as_posix()
    identity = brief.Identity(
        "01K0000000000000000000PLNT", f"{date}T07:00:00-07:00", f"{date}T07:00:00-07:00"
    )
    intent = events.make_event(
        source="kgme",
        actor="kgme.brief",
        kind="intent",
        job="brief",
        key=f"brief:{date}",
        summary=brief.identity_summary(identity, "0" * 16, date),
        payload_ref=ref,
        payload_sha256=sha,
    )
    ledger.append(intent, dirs)
    return intent


def closing(base: Path, intent: dict) -> list[dict]:
    dirs = ledger.read_base_dirs(SETTINGS, base)
    return [e for e in ledger.read(dirs) if e["ref"] == intent["id"]]
