"""Tests for the writer and reader (HANDOFF-0026 acceptance).

Purpose: prove the ADR-019 §4 append contract: validation before disk, redaction, the size
cap, stream routing by rule, month rotation by the event's own timestamp, concurrent appends
without interleaving, merged reads, orphan flagging, and open-intent reconciliation.
Inputs: a temporary directory per test; four subprocesses for the concurrency test.
Outputs: pytest assertions.
Side effects: files under pytest's `tmp_path` only. One test writes to the configured
`logs/ledger-test/` and `logs/trace-test/` to prove they are gitignored, then checks that
`git status` shows nothing under `logs/`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kgme import config, events, ledger, paths

READ_ONLY = ("Read", "Grep", "Glob", "LS", "TodoRead")


def dirs_in(tmp_path: Path) -> ledger.Dirs:
    return ledger.Dirs(
        ledger=tmp_path / "ledger", trace=tmp_path / "trace", read_only_tools=READ_ONLY
    )


def event(**overrides: object) -> dict:
    fields: dict = dict(source="kgme", actor="kgme.test", kind="note", summary="hello")
    fields.update(overrides)
    return events.make_event(**fields)


@pytest.mark.blocking
def test_append_writes_one_valid_line_to_the_month_file(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    identifier = ledger.append(event(ts="2026-09-14T10:00:00.000-07:00"), dirs)
    lines = (dirs.ledger / "2026-09.jsonl").read_text().splitlines()
    assert len(lines) == 1
    stored = json.loads(lines[0])
    assert stored["id"] == identifier
    assert list(stored) == list(events.FIELDS)
    events.validate_event(stored)


@pytest.mark.blocking
def test_invalid_event_never_reaches_disk(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    bad = event()
    bad["kind"] = "wish"
    with pytest.raises(ValueError):
        ledger.append(bad, dirs)
    assert not dirs.ledger.exists()


@pytest.mark.blocking
def test_oversized_line_is_refused_not_truncated(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    with pytest.raises(ValueError, match="cap"):
        ledger.append(event(key="x" * 5000), dirs)
    assert not dirs.ledger.exists()


@pytest.mark.blocking
def test_summary_is_redacted_before_disk(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ledger.append(event(summary="curl -H token=abc123DEF456ghi789 https://example.test"), dirs)
    raw = next(dirs.ledger.glob("*.jsonl")).read_text()
    assert "abc123DEF456ghi789" not in raw
    assert "<redacted:" in raw


@pytest.mark.blocking
def test_read_only_tool_pairs_go_to_trace_and_others_to_ledger(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    read_intent = ledger.append(
        event(kind="intent", job="tool:Read", summary="Read kgme/paths.py"), dirs
    )
    ledger.append(
        event(kind="outcome", status="ok", job="tool:Read", ref=read_intent, summary="ok"), dirs
    )
    edit_intent = ledger.append(
        event(kind="intent", job="tool:Edit", summary="Edit kgme/cli.py"), dirs
    )
    ledger.append(
        event(kind="outcome", status="ok", job="tool:Edit", ref=edit_intent, summary="ok"), dirs
    )
    assert len(ledger.read(dirs, stream="trace")) == 2
    assert len(ledger.read(dirs, stream="ledger")) == 2
    assert {e["job"] for e in ledger.read(dirs, stream="trace")} == {"tool:Read"}
    assert {e["job"] for e in ledger.read(dirs, stream="ledger")} == {"tool:Edit"}


@pytest.mark.blocking
def test_refused_read_only_call_goes_to_the_ledger(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ledger.append(
        event(
            kind="outcome", status="refused", class_="blocking", job="tool:Read", summary="refused"
        ),
        dirs,
    )
    assert len(ledger.read(dirs, stream="ledger")) == 1
    assert len(ledger.read(dirs, stream="trace")) == 0


@pytest.mark.blocking
def test_read_both_merges_in_id_order_and_since_filters(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ids = [
        ledger.append(event(kind="intent", job=job, summary=job), dirs)
        for job in ("tool:Read", "x", "tool:Grep", "y")
    ]
    merged = [e["id"] for e in ledger.read(dirs)]
    assert merged == sorted(ids)
    assert [e["id"] for e in ledger.read(dirs, since=ids[1])] == sorted(ids)[2:]


@pytest.mark.blocking
def test_orphan_parent_is_accepted_and_flagged_by_read_page(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    root = ledger.append(event(kind="intent", job="brief", summary="run"), dirs)
    child = ledger.append(event(parent=root, summary="child"), dirs)
    ledger.append(event(parent="01ARZ3NDEKTSV4RRFFQ69G5FAV", summary="orphan"), dirs)
    page = ledger.read_page(dirs)
    assert len(page.events) == 3
    assert [e["summary"] for e in page.orphans] == ["orphan"]
    after_root = ledger.read_page(dirs, since=root)
    assert [e["id"] for e in after_root.events][0] == child
    assert [e["summary"] for e in after_root.orphans] == ["orphan"]
    assert ledger.read_page(dirs, run_id="nope").orphans == []
    other_run = ledger.append(
        event(parent=root, run_id="run-b", summary="child in another run"), dirs
    )
    page_b = ledger.read_page(dirs, run_id="run-b")
    assert [e["id"] for e in page_b.events] == [other_run]
    assert page_b.orphans == []


@pytest.mark.blocking
def test_bare_dot_env_is_redacted_at_the_writer(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ledger.append(event(summary="cat .env and .env.local then source ./app/.env.production"), dirs)
    raw = next(dirs.ledger.glob("*.jsonl")).read_text()
    assert ".env" not in raw
    assert raw.count("<redacted:") == 3


@pytest.mark.blocking
def test_redaction_that_lengthens_a_summary_past_the_cap_is_refused_not_clipped(
    tmp_path: Path,
) -> None:
    dirs = dirs_in(tmp_path)
    summary = " ".join(["token=a"] * 11) + " action refused"
    assert len(summary) < 200 < len(events.redact(summary))
    with pytest.raises(ValueError, match="after redaction"):
        ledger.append(event(summary=summary), dirs)
    assert not dirs.ledger.exists()
    short = "token=a action refused"
    ledger.append(event(summary=short), dirs)
    stored = json.loads(next(dirs.ledger.glob("*.jsonl")).read_text())
    assert stored["summary"].endswith(" action refused") and "token=a" not in stored["summary"]


@pytest.mark.blocking
def test_short_write_raises_and_is_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dirs = dirs_in(tmp_path)
    real_write = os.write
    calls: list[int] = []

    def short_write(descriptor: int, data: bytes) -> int:
        calls.append(len(data))
        return real_write(descriptor, data[: len(data) // 2])

    monkeypatch.setattr(os, "write", short_write)
    with pytest.raises(RuntimeError, match="short write"):
        ledger.append(event(summary="torn"), dirs)
    assert len(calls) == 1


@pytest.mark.blocking
def test_malformed_line_is_named_on_read(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ledger.append(event(summary="fine"), dirs)
    path = next(dirs.ledger.glob("*.jsonl"))
    path.write_text(path.read_text() + "{not json\n")
    with pytest.raises(ValueError, match=":2 is not a JSON line"):
        ledger.read(dirs)


@pytest.mark.blocking
def test_serialized_order_is_the_field_order_whatever_the_input_order(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    scrambled = dict(reversed(list(event().items())))
    ledger.append(scrambled, dirs)
    stored = json.loads(next(dirs.ledger.glob("*.jsonl")).read_text())
    assert list(stored) == list(events.FIELDS)


@pytest.mark.blocking
def test_month_rotation_uses_each_events_own_timestamp(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    ledger.append(event(ts="2026-09-30T23:59:59.900-07:00", summary="before midnight"), dirs)
    ledger.append(event(ts="2026-10-01T00:00:00.100-07:00", summary="after midnight"), dirs)
    assert sorted(p.name for p in dirs.ledger.glob("*.jsonl")) == ["2026-09.jsonl", "2026-10.jsonl"]


@pytest.mark.blocking
def test_open_intents_returns_only_the_unclosed_one(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    closed = ledger.append(event(kind="intent", job="x", key="x:1", summary="closed"), dirs)
    ledger.append(event(kind="outcome", status="ok", job="x", ref=closed, summary="done"), dirs)
    open_id = ledger.append(event(kind="intent", job="x", key="x:2", summary="open"), dirs)
    ledger.append(event(kind="intent", job="other", summary="other job"), dirs)
    assert [e["id"] for e in ledger.open_intents("x", dirs)] == [open_id]


WORKER = """
import sys
from pathlib import Path
from kgme import events, ledger
dirs = ledger.Dirs(ledger=Path(sys.argv[1]), trace=Path(sys.argv[2]), read_only_tools=())
for i in range(250):
    summary = f"{sys.argv[3]}-{i}"
    made = events.make_event(source="kgme", actor="kgme.test", kind="note", summary=summary)
    ledger.append(made, dirs)
"""


@pytest.mark.blocking
def test_four_processes_appending_concurrently_do_not_interleave(tmp_path: Path) -> None:
    dirs = dirs_in(tmp_path)
    procs = [
        subprocess.Popen([sys.executable, "-c", WORKER, str(dirs.ledger), str(dirs.trace), f"w{n}"])
        for n in range(4)
    ]
    assert all(p.wait(timeout=120) == 0 for p in procs)
    lines = [line for p in dirs.ledger.glob("*.jsonl") for line in p.read_text().splitlines()]
    assert len(lines) == 1000
    parsed = [json.loads(line) for line in lines]
    assert len({e["id"] for e in parsed}) == 1000
    for e in parsed:
        events.validate_event(e)


@pytest.mark.blocking
def test_configured_test_streams_leave_git_status_unchanged() -> None:
    def porcelain() -> str:
        return subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=paths.root(),
            check=True,
        ).stdout

    before = porcelain()
    dirs = ledger.read_test_dirs(config.read_config())
    ledger.append(event(summary="gitignore probe"), dirs)
    ledger.append(event(kind="intent", job="tool:Read", summary="trace probe"), dirs)
    assert (dirs.ledger / "2026-09.jsonl").exists() or any(dirs.ledger.glob("*.jsonl"))
    assert porcelain() == before
