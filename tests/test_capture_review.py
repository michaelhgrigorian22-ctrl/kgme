"""Tests for what review cycle 1 of HANDOFF-0050 (AUDIT-0059) asked of capture and daily.

Purpose: one test or more per blocking finding, each written and run red before its fix (the
review-loop reader's rule of 2026-10-14). An interrupted daily publication leaves no partial
note and the next run drafts it (F1); a held line whose capture was interrupted reaches the
draft (F2); a capture retried after it wrote, or run twice, writes once (F3); reconciliation
does not depend on a summary the redactor can change (F4); a problem is solved only by an
outcome that answers it (F5); the morning brief reads the evening's draft (F6); both jobs
take `--dry-run` and change nothing with it (F7); every written byte is reconstructable
from the ledger and its payload, words longer than a summary included (F8). Cycles 5 to 7,
how a line is added to an existing file, are in `tests/test_capture_replace.py`.
Inputs: the seeded vault of `tests/capturetools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only; `os`-level writes are patched
for the interruption tests.
"""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from brieftools import SETTINGS
from capturetools import read_job, run_capture, run_daily, write_vault
from cleantools import OsWith
from clocktools import FROZEN, freeze

from kgme import brief_io, capture_fs, clean_fs, cli, daily, events, ledger

TODAY = FROZEN.date().isoformat()


@pytest.fixture(autouse=True)
def frozen(monkeypatch) -> None:
    """Every test reads one clock, frozen at `FROZEN` (HANDOFF-0060 §1): "today" here and in
    the code are the same day, whenever the run starts or ends."""
    freeze(monkeypatch)


FRICTION = Path("memory/inbox/friction-log.md")


def drop_last_outcome(base: Path) -> dict:
    """What a run killed after its write and before its outcome leaves: its outcome removed
    from the test ledger (the real ledger is never edited; this one is a fixture)."""
    month = ledger.read_base_dirs(SETTINGS, base).ledger
    path = sorted(month.glob("*.jsonl"))[-1]
    lines = path.read_text().splitlines(keepends=True)
    last = max(i for i, line in enumerate(lines) if json.loads(line)["kind"] == "outcome")
    dropped = json.loads(lines.pop(last))
    path.write_text("".join(lines))
    return dropped


def interrupt_after_half(monkeypatch) -> None:
    """`write_whole` writes half of a note's bytes, then the process is interrupted; other
    writes (a payload) go through whole."""
    whole = clean_fs.write_whole

    def half(fd: int, data: bytes) -> None:
        import os

        if not data.startswith(b"---\n"):
            return whole(fd, data)
        os.write(fd, data[: len(data) // 2])
        raise KeyboardInterrupt

    monkeypatch.setattr(clean_fs, "write_whole", half)


# F1


@pytest.mark.blocking
def test_an_interrupted_daily_publication_leaves_no_partial_note(
    tmp_path: Path, monkeypatch
) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "friction", "something happened", now=None) == 0
    destination = base / "memory" / "daily" / f"{TODAY}.md"
    with monkeypatch.context() as patch:
        interrupt_after_half(patch)
        with pytest.raises(KeyboardInterrupt):
            run_daily(base, TODAY)
    assert not destination.exists(), "an interrupted publication leaves no note behind"
    assert run_daily(base, TODAY) == 0
    assert destination.read_text().rstrip().endswith(daily.capture.MICHOU_MARK)


# F2


@pytest.mark.blocking
def test_a_held_line_whose_capture_was_interrupted_reaches_the_draft(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "daily", "finished the costing homework", now=None) == 0
    drop_last_outcome(base)
    assert run_daily(base, TODAY) == 0
    note = (base / "memory" / "daily" / f"{TODAY}.md").read_text()
    assert "- finished the costing homework" in note


# F3


@pytest.mark.blocking
def test_a_capture_retried_after_it_wrote_writes_once(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    before = sorted((base / "memory/notes").iterdir())
    assert run_capture(base, "note", "call the reader") == 0
    drop_last_outcome(base)
    assert run_capture(base, "note", "call the reader") == 0
    after = sorted((base / "memory/notes").iterdir())
    assert len(after) == len(before) + 1
    friction = (base / FRICTION).read_bytes()
    assert run_capture(base, "friction", "quota again") == 0
    drop_last_outcome(base)
    assert run_capture(base, "friction", "quota again") == 0
    assert (base / FRICTION).read_bytes().count(b"quota again") == 1
    assert (base / FRICTION).read_bytes().startswith(friction)


@pytest.mark.blocking
def test_a_duplicate_run_writes_once(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "remind", "call the reader", "friday 9am") == 0
    assert run_capture(base, "remind", "call the reader", "friday 9am") == 0
    assert len(list((base / "memory/notes").glob("call-the-reader*.md"))) == 1
    assert "already captured" in capsys.readouterr().out


# F4


@pytest.mark.blocking
def test_reconciliation_does_not_depend_on_a_redacted_summary(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    long_word = "a" * 45  # a stem the redactor would replace in a summary
    assert run_capture(base, "note", long_word) == 0
    intent_id = drop_last_outcome(base)["ref"]
    assert run_capture(base, "note", "something else") == 0
    closing = [e for e in read_job(base, "capture", "outcome") if e["ref"] == intent_id]
    assert [e["status"] for e in closing] == ["ok"]


# F5


@pytest.mark.blocking
def test_an_unrelated_success_does_not_solve_a_problem() -> None:
    refused = events.make_event(
        source="kgme", actor="t", kind="outcome", job="capture", key="capture:remind:aaa",
        summary="refused: could not read", status="refused", class_="blocking",
    )  # fmt: skip
    unrelated = events.make_event(
        source="kgme", actor="t", kind="outcome", job="capture", key="capture:friction:bbb",
        summary="captured friction", status="ok",
    )  # fmt: skip
    day = daily.Day(TODAY, (refused, unrelated), (), "", (), (), (), (), (), ())
    text = daily.build_daily(day, "01K", "now", None)
    section = text.split("## Problems and solutions")[1].split("## Tomorrow")[0]
    assert "solved" not in section
    assert "still open" in section


# F6


@pytest.mark.blocking
def test_the_morning_brief_reads_the_evening_draft(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "daily", "a line for the evening", now=None) == 0
    assert run_daily(base, TODAY) == 0
    tomorrow = (date.fromisoformat(TODAY) + timedelta(days=1)).isoformat()
    capsys.readouterr()
    assert brief_io.run_brief(tomorrow, True, base, SETTINGS) == 0
    text = capsys.readouterr().out
    assert f"memory/daily/{TODAY}.md" in text and "a line for the evening" in text


# F7


@pytest.mark.blocking
def test_both_jobs_take_dry_run_and_change_nothing(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path, TODAY)
    for kind, words in (("note", "dry note"), ("friction", "dry friction")):
        args = cli.build_parser().parse_args(["capture", kind, words, "--dry-run"])
        assert args.dry_run
    assert cli.build_parser().parse_args(["daily", "--dry-run"]).dry_run
    files = {p: p.read_bytes() for p in (base / "memory").rglob("*") if p.is_file()}
    assert run_capture(base, "note", "dry note", now=None, dry_run=True) == 0
    assert run_capture(base, "friction", "dry friction", now=None, dry_run=True) == 0
    assert run_daily(base, TODAY, dry_run=True) == 0
    assert {p: p.read_bytes() for p in (base / "memory").rglob("*") if p.is_file()} == files
    out = capsys.readouterr().out
    assert "# dry note" in out and "dry friction" in out and "## Michou" in out
    assert [e["kind"] for e in read_job(base, "capture")] == ["note", "note"]
    assert [e["kind"] for e in read_job(base, "daily")] == ["note"]


# F8


@pytest.mark.blocking
def test_every_written_byte_is_reconstructable_from_the_ledger(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    words = "a thought much longer than any summary can hold " * 6
    assert run_capture(base, "note", words.strip(), now=None) == 0
    assert run_capture(base, "friction", "the reviewer timed out", now=None) == 0
    assert run_daily(base, TODAY) == 0
    for job in ("capture", "daily"):
        for intent in read_job(base, job, "intent"):
            data, why = ledger.read_payload(base, intent)
            assert data is not None and why == "", intent["summary"]
            record = json.loads(data)
            written = (base / record["destination"]).read_bytes()
            start = record.get("offset", 0)
            assert written[start : start + record["size"]] == record["bytes"].encode("utf-8")
    first = json.loads(ledger.read_payload(base, read_job(base, "capture", "intent")[0])[0])
    assert first["words"] == words.strip()


# Cycle 2 (AUDIT-0060)


def fail_fsync_after_write(monkeypatch) -> None:
    """In `kgme.capture_fs` only, the bytes land (the append is written, the new note is
    linked) and then `fsync` raises, so the run closes its intent `error`; the ledger's own
    fsync is untouched."""

    def fsync(fd: int) -> None:
        raise OSError(5, "fsync failed after the write")

    monkeypatch.setattr(capture_fs, "os", OsWith(fsync=fsync))


@pytest.mark.blocking
def test_c2_f2_a_held_line_survives_its_payload_being_cleaned(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "daily", "finished the costing homework", now=None) == 0
    dropped = drop_last_outcome(base)
    intent = [e for e in read_job(base, "capture", "intent") if e["id"] == dropped["ref"]][0]
    (base / intent["payload_ref"]).unlink()
    assert run_daily(base, TODAY) == 0
    note = (base / "memory" / "daily" / f"{TODAY}.md").read_text()
    assert "- finished the costing homework" in note


@pytest.mark.blocking
@pytest.mark.parametrize("kind", ["note", "friction"])
def test_c2_f3_a_failure_after_the_bytes_landed_is_settled_by_them(
    tmp_path: Path, monkeypatch, capsys, kind: str
) -> None:
    """The arbiter's ruling: classified before it is closed, so the intent is `ok` and a
    retry writes nothing."""
    base = write_vault(tmp_path)
    friction = (base / FRICTION).read_bytes()
    notes_before = sorted(p.name for p in (base / "memory/notes").iterdir())
    with monkeypatch.context() as patch:
        fail_fsync_after_write(patch)
        assert run_capture(base, kind, "said once") == 0
    assert "written, then failed" in capsys.readouterr().err
    assert read_job(base, "capture", "outcome")[-1]["status"] == "ok"
    assert run_capture(base, kind, "said once") == 0
    assert "already captured" in capsys.readouterr().out
    if kind == "friction":
        assert (base / FRICTION).read_bytes().count(b"said once") == 1
        assert (base / FRICTION).read_bytes().startswith(friction)
    else:
        assert len(sorted(p.name for p in (base / "memory/notes").iterdir())) == (
            len(notes_before) + 1
        )


@pytest.mark.blocking
def test_c2_f3_an_attempt_closed_in_error_whose_bytes_landed_is_not_replayed(
    tmp_path: Path, capsys
) -> None:
    """A ledger written before the ruling, or by any path that closed an intent `error`
    after its bytes landed: the retry reads the file, not the outcome."""
    base = write_vault(tmp_path)
    assert run_capture(base, "friction", "said once") == 0
    dropped = drop_last_outcome(base)
    error = events.make_event(
        source="kgme", actor="kgme.capture", kind="outcome", job="capture", key=dropped["key"],
        summary="failed: fsync", status="error", class_="blocking", ref=dropped["ref"],
        parent=dropped["ref"],
    )  # fmt: skip
    ledger.append(error, ledger.read_base_dirs(SETTINGS, base))
    capsys.readouterr()
    assert run_capture(base, "friction", "said once") == 0
    assert "already captured" in capsys.readouterr().out
    assert (base / FRICTION).read_bytes().count(b"said once") == 1


@pytest.mark.blocking
def test_c2_an_ok_capture_edited_above_is_still_already_captured(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "friction", "said once") == 0
    text = (base / FRICTION).read_text()
    (base / FRICTION).write_text(text.replace("# Friction log", "# Friction log, edited"))
    capsys.readouterr()
    assert run_capture(base, "friction", "said once") == 0
    assert "already captured" in capsys.readouterr().out
    assert (base / FRICTION).read_text().count("said once") == 1
