"""The one writer and the reader for the two event streams (ADR-019 §4).

Purpose: `append` is the only code in KGME that opens a ledger or trace file for writing.
It validates, redacts, re-validates, sizes, routes, and appends under a lock, and it fails
loudly on a short write. `read_page` merges the streams and flags orphans; `read` is the
plain list. `open_intents` finds intents no outcome has closed, for reconciliation on start
(ADR-013 §4).
Inputs: event dicts from `kgme.events`; a `Dirs` naming where the two streams live.
Outputs: event ids; lists of event dicts; a `Page` with its orphans.
Side effects: `append` creates the stream directory if missing and appends one line with
`O_APPEND`, `flock`, a single `os.write`, and `fsync`. `read_default_dirs` and
`read_test_dirs` read `kgme.toml`. `read_page` opens stream files read-only.
"""

import fcntl
import json
import os
from dataclasses import dataclass
from pathlib import Path

from kgme import config, events, paths


@dataclass(frozen=True)
class Dirs:
    """Where the two streams live. Tests pass their own; jobs use `read_default_dirs`."""

    ledger: Path
    trace: Path
    read_only_tools: tuple[str, ...]


@dataclass(frozen=True)
class Page:
    """What a read returns: the events in id order, and those whose `parent` is unknown."""

    events: list[dict]
    orphans: list[dict]


def read_default_dirs(settings: dict | None = None) -> Dirs:
    """The real streams from `kgme.toml`. Reads the config if not given one."""
    settings = settings or config.read_config()
    return Dirs(
        ledger=paths.ledger_dir(settings),
        trace=paths.trace_dir(settings),
        read_only_tools=tuple(settings["hooks"]["read_only_tools"]),
    )


def read_base_dirs(settings: dict, base: Path) -> Dirs:
    """The streams of the checkout at `base`, for a job told which checkout to act on
    (HANDOFF-0033): a test's temporary root gets its own ledger, never this one's."""
    return Dirs(
        ledger=paths.ledger_dir(settings, base),
        trace=paths.trace_dir(settings, base),
        read_only_tools=tuple(settings["hooks"]["read_only_tools"]),
    )


def read_test_dirs(settings: dict | None = None) -> Dirs:
    """The gitignored test streams from `kgme.toml`, so `make check` never dirties the tree."""
    settings = settings or config.read_config()
    return Dirs(
        ledger=paths.ledger_test_dir(settings),
        trace=paths.trace_test_dir(settings),
        read_only_tools=tuple(settings["hooks"]["read_only_tools"]),
    )


def _write_line(path: Path, data: bytes) -> None:
    """Append `data` under an exclusive lock. A short write raises; it is never retried."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        try:
            written = os.write(descriptor, data)
            os.fsync(descriptor)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)
    if written != len(data):
        raise RuntimeError(
            f"short write: {written} of {len(data)} bytes reached {path}; "
            "the last line is torn and must be corrected, never edited (ADR-003)"
        )


def append(event: dict, dirs: Dirs | None = None) -> str:
    """Validate, redact the summary, validate again, route, and append. Returns the event id.

    Raises ValueError before touching disk if the event breaks a rule or exceeds the line cap.
    Redaction can lengthen a summary (each secret becomes a 19-character placeholder). A
    redacted summary over the cap is refused, not clipped: clipping would drop ordinary text
    after the placeholders, and the caller is the one who knows what to shorten.
    """
    dirs = dirs or read_default_dirs()
    events.validate_event(event)
    redacted = dict(event)
    redacted["summary"] = events.redact(event["summary"])
    if len(redacted["summary"]) > events.MAX_SUMMARY_CHARS:
        raise ValueError(
            f"summary is {len(redacted['summary'])} characters after redaction, cap is "
            f"{events.MAX_SUMMARY_CHARS}; shorten it rather than carry that many secret shapes"
        )
    events.validate_event(redacted)
    data = events.serialize(redacted)
    stream = events.stream_for(redacted, list(dirs.read_only_tools))
    stream_dir = dirs.trace if stream == "trace" else dirs.ledger
    _write_line(stream_dir / events.month_file(redacted["ts"]), data)
    return redacted["id"]


def _read_dir(directory: Path) -> list[dict]:
    """Every event in every month file. A malformed line is an error, named by file and line."""
    found: list[dict] = []
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.jsonl")):
        with open(path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    found.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path}:{number} is not a JSON line: {error}") from error
    return found


def read_page(
    dirs: Dirs | None = None,
    since: str | None = None,
    run_id: str | None = None,
    stream: str = "both",
) -> Page:
    """Events in id order from `ledger`, `trace`, or `both`, after `since`, for one run.

    Orphans are judged against everything in the selected streams, before `since` and
    `run_id` narrow the page, so a child whose parent lies before the cursor is not an orphan.
    """
    dirs = dirs or read_default_dirs()
    if stream not in ("both", "ledger", "trace"):
        raise ValueError("stream must be both, ledger, or trace")
    found: list[dict] = []
    if stream in ("both", "ledger"):
        found.extend(_read_dir(dirs.ledger))
    if stream in ("both", "trace"):
        found.extend(_read_dir(dirs.trace))
    found.sort(key=lambda event: event["id"])
    orphan_ids = {event["id"] for event in events.orphans(found)}
    if since is not None:
        found = [event for event in found if event["id"] > since]
    if run_id is not None:
        found = [event for event in found if event["run_id"] == run_id]
    return Page(events=found, orphans=[event for event in found if event["id"] in orphan_ids])


def read(
    dirs: Dirs | None = None,
    since: str | None = None,
    run_id: str | None = None,
    stream: str = "both",
) -> list[dict]:
    """The events of `read_page`, for callers that do not need the orphan list."""
    return read_page(dirs, since, run_id, stream).events


def open_intents(job: str, dirs: Dirs | None = None) -> list[dict]:
    """Intents for `job` that no outcome references. What a job reconciles on start."""
    everything = read(dirs)
    closed = {event["ref"] for event in everything if event["kind"] == "outcome" and event["ref"]}
    return [
        event
        for event in everything
        if event["kind"] == "intent" and event["job"] == job and event["id"] not in closed
    ]
