"""Ledger events, v1: the shape, its rules, and the transforms that never touch disk (ADR-019).

Purpose: everything about an event that can be decided from the event alone: construction
with defaults, validation against the field set and enums, redaction of the summary, the
stream rule, the month file name, serialization with the size cap, orphan detection.
Vendor-stream parsing lives in `kgme.streams`; writing lives in `kgme.ledger`.
Inputs: dicts and strings.
Outputs: dicts, strings, bytes. Pure, with two named exceptions: `now_iso` reads the clock,
and `make_event` mints ids through `kgme.ulid`, which draws randomness and keeps the last id.
Side effects: none on disk. Nothing here opens a file.
"""

import hashlib
import json
import re
from datetime import datetime

from kgme.ulid import new_ulid

VERSION = 1
MAX_LINE_BYTES = 4096
MAX_SUMMARY_CHARS = 200

FIELDS = (
    "v",
    "id",
    "ts",
    "run_id",
    "source",
    "actor",
    "kind",
    "class",
    "status",
    "job",
    "key",
    "ref",
    "parent",
    "summary",
    "payload_ref",
    "payload_sha256",
)
SOURCES = ("kgme", "claude-code", "codex", "human")
KINDS = ("intent", "outcome", "tool_call", "approval", "correction", "note")
CLASSES = ("blocking", "transient", "cosmetic", "advisory")
STATUSES = ("ok", "error", "refused")
NULLABLE = ("class", "status", "job", "key", "ref", "parent", "payload_ref", "payload_sha256")

TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}$")
# A ULID's first character is 0-7: 128 bits do not reach "8" and above (ADR-019 §5).
ULID_PATTERN = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
PAYLOAD_PREFIX = "logs/scratch/payloads/"

# ADR-008 secret shapes. Each match becomes <redacted:8-hex-of-its-sha256> before disk.
SECRET_PATTERNS = (
    re.compile(r"Bearer\s+\S+"),
    re.compile(r"(?i)\b(?:token|key|password|passwd|secret|api[_-]?key)\s*[=:]\s*\S+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b[A-Za-z0-9_-]{40,}\b"),
    re.compile(r"(?:~|/Users/[^/\s]+)/\.ssh/\S*"),
    re.compile(r"(?:~|/Users/[^/\s]+)/Library/Keychains/\S*"),
    re.compile(r"(?:~|/Users/[^/\s]+)/\.(?:claude|codex)/[^\s]*(?:credentials|auth)[^\s]*"),
    re.compile(r"(?:\S*/)?\.env(?:\.[A-Za-z0-9_-]+)*\b"),
)


def now_iso() -> str:
    """Local time with offset and milliseconds. Never `utcnow()` (corrections.md, entry one)."""
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def make_event(
    *,
    source: str,
    actor: str,
    kind: str,
    summary: str,
    run_id: str | None = None,
    class_: str | None = None,
    status: str | None = None,
    job: str | None = None,
    key: str | None = None,
    ref: str | None = None,
    parent: str | None = None,
    payload_ref: str | None = None,
    payload_sha256: str | None = None,
    ts: str | None = None,
    id: str | None = None,
) -> dict:
    """An event dict in field order, with `v`, `id`, `ts`, and `run_id` defaulted.

    `class_` is the `class` field; Python reserves the bare name. An explicit `ts` is for
    tests and for replaying vendor streams, where the vendor's time is the event's time.
    """
    return {
        "v": VERSION,
        "id": id or new_ulid(),
        "ts": ts or now_iso(),
        "run_id": run_id or new_ulid(),
        "source": source,
        "actor": actor,
        "kind": kind,
        "class": class_,
        "status": status,
        "job": job,
        "key": key,
        "ref": ref,
        "parent": parent,
        "summary": summary,
        "payload_ref": payload_ref,
        "payload_sha256": payload_sha256,
    }


def validate_event(event: dict) -> None:
    """Raise ValueError on the first rule the event breaks. Silence means valid."""
    unknown = set(event) - set(FIELDS)
    if unknown:
        raise ValueError(f"unknown field(s): {sorted(unknown)}")
    missing = set(FIELDS) - set(event)
    if missing:
        raise ValueError(f"missing field(s): {sorted(missing)}")
    if type(event["v"]) is not int or event["v"] != VERSION:
        raise ValueError(f"v must be the integer {VERSION}, got {event['v']!r}")
    for name in ("id", "run_id", "source", "actor", "kind", "summary", "ts"):
        if not isinstance(event[name], str) or not event[name]:
            raise ValueError(f"{name} must be a non-empty string")
    for name in NULLABLE:
        if event[name] is not None and not isinstance(event[name], str):
            raise ValueError(f"{name} must be a string or null")
    if not ULID_PATTERN.fullmatch(event["id"]):
        raise ValueError("id must be a ULID")
    if not TS_PATTERN.fullmatch(event["ts"]) or not _is_real_timestamp(event["ts"]):
        raise ValueError("ts must be a real ISO 8601 instant with milliseconds and an offset")
    for name in ("ref", "parent"):
        if event[name] is not None and not ULID_PATTERN.fullmatch(event[name]):
            raise ValueError(f"{name} must be null or the ULID of another event")
    if event["payload_ref"] is not None and (
        not event["payload_ref"].startswith(PAYLOAD_PREFIX) or ".." in event["payload_ref"]
    ):
        raise ValueError(f"payload_ref must be a repo-relative path under {PAYLOAD_PREFIX}")
    if event["source"] not in SOURCES:
        raise ValueError(f"source must be one of {SOURCES}")
    if event["kind"] not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if event["class"] is not None and event["class"] not in CLASSES:
        raise ValueError(f"class must be null or one of {CLASSES}")
    if event["status"] is not None and event["status"] not in STATUSES:
        raise ValueError(f"status must be null or one of {STATUSES}")
    if event["status"] is not None and event["kind"] != "outcome":
        raise ValueError("status is set only on outcome events")
    if event["kind"] == "outcome" and event["status"] is None:
        raise ValueError("an outcome must carry a status")
    if event["status"] in ("error", "refused") and event["class"] is None:
        raise ValueError("a failed or refused outcome must carry a class (ADR-016)")
    if len(event["summary"]) > MAX_SUMMARY_CHARS:
        raise ValueError(f"summary longer than {MAX_SUMMARY_CHARS} characters")
    if event["payload_sha256"] is not None and not re.fullmatch(
        r"[0-9a-f]{64}", event["payload_sha256"]
    ):
        raise ValueError("payload_sha256 must be 64 hex characters")


def _is_real_timestamp(ts: str) -> bool:
    try:
        datetime.fromisoformat(ts)
    except ValueError:
        return False
    return True


def clip(text: str) -> str:
    """`text` cut to the summary cap with a trailing ellipsis when it was longer."""
    if len(text) <= MAX_SUMMARY_CHARS:
        return text
    return text[: MAX_SUMMARY_CHARS - 1] + "…"


def redact(text: str) -> str:
    """Replace every secret-shaped span with `<redacted:xxxxxxxx>`, 19 characters, sha256 prefix."""

    def replacement(match: re.Match) -> str:
        digest = hashlib.sha256(match.group(0).encode("utf-8")).hexdigest()[:8]
        return f"<redacted:{digest}>"

    for pattern in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def stream_for(event: dict, read_only_tools: list[str]) -> str:
    """`trace` for a read-only tool's intent or outcome, `ledger` for everything else (ADR-019 §2).

    A refused call is consequential whatever the tool, so it always goes to the ledger.
    """
    job = event["job"] or ""
    if not job.startswith("tool:"):
        return "ledger"
    if event["kind"] not in ("intent", "outcome"):
        return "ledger"
    if event["status"] == "refused" or event["class"] == "blocking":
        return "ledger"
    return "trace" if job[len("tool:") :] in read_only_tools else "ledger"


def month_file(ts: str) -> str:
    """`YYYY-MM.jsonl` from the event's own local timestamp (ADR-012 rotation)."""
    return ts[:7] + ".jsonl"


def serialize(event: dict) -> bytes:
    """One compact UTF-8 JSON line in `FIELDS` order, refused if over the cap, never truncated."""
    ordered = {name: event[name] for name in FIELDS}
    line = json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + "\n"
    data = line.encode("utf-8")
    if len(data) > MAX_LINE_BYTES:
        raise ValueError(f"serialized event is {len(data)} bytes, cap is {MAX_LINE_BYTES}")
    return data


TRANSIENT_SIGNS = re.compile(
    r"(?i)rate[ _-]?limit|429|timeout|timed out|overloaded|network|connection|503|502"
)


def classify_failure(text: str) -> str:
    """ADR-016 class for a failure described by `text`: `transient` for the shapes ADR-016
    names (rate limits, timeouts, network, outages), `blocking` for everything else."""
    return "transient" if TRANSIENT_SIGNS.search(text or "") else "blocking"


def orphans(events: list[dict]) -> list[dict]:
    """Events whose `parent` names an id absent from `events`. Accepted on write; flagged here."""
    ids = {event["id"] for event in events}
    return [event for event in events if event["parent"] is not None and event["parent"] not in ids]
