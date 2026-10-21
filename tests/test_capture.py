"""Tests for `kgme capture` (HANDOFF-0050): the acceptance test and what it rests on.

Purpose: a reminder is one new file with a resolved due and one ledger pair, printed; a
friction capture appends exactly one line; a capture into an existing file never changes a
byte before its end; a daily line is held in the ledger until the note exists and appended
under the closing `Michou` heading after; no byte already written is ever changed, and
nothing is created where it must not be or written through a link; an unresolvable,
ambiguous, or passed due is a refusal that records the words; open intents are reconciled;
the brief the next morning lists the reminder and the friction line.
Inputs: the seeded vault of `tests/capturetools.py`.
Outputs: pytest assertions.
Side effects: files, links, and ledger lines under `tmp_path` only.
"""

import fcntl
import os
from datetime import datetime
from pathlib import Path

import pytest
from brieftools import SETTINGS, brief_io_parse
from capturetools import THURSDAY, ZONE, read_job, run_capture, write_vault

from kgme import brief_io, capture, capture_fs, capture_io, capture_record, clean_fs, events, lint

FRICTION = Path("memory/inbox/friction-log.md")


def notes(base: Path) -> set[str]:
    return {p.name for p in (base / "memory" / "notes").glob("*.md")}


@pytest.mark.blocking
def test_a_reminder_is_one_new_file_with_a_resolved_due_and_one_ledger_pair(
    tmp_path: Path, capsys
) -> None:
    base = write_vault(tmp_path)
    before = notes(base)
    assert run_capture(base, "remind", "pay the Backblaze renewal", "friday 9am") == 0
    assert notes(base) - before == {"pay-the-backblaze-renewal.md"}
    path = base / "memory" / "notes" / "pay-the-backblaze-renewal.md"
    text = path.read_text()
    data, body = brief_io_parse(text)
    assert data["due"] == "2026-10-16T09:00:00-07:00"
    assert (data["type"], data["status"], data["source"], data["author"]) == (
        "reminder",
        "open",
        "stated",
        "kgme",
    )
    assert data["repeat"] is None and data["channel"] == "phone"
    assert events.ULID_PATTERN.fullmatch(data["id"])
    assert body.strip() == "# pay the Backblaze renewal"
    assert [f for f in lint.lint_note(text, "memory/notes/x.md", {}) if f.cls == "blocking"] == []
    pair = read_job(base, "capture")
    assert [e["kind"] for e in pair] == ["intent", "outcome"]
    assert pair[1]["status"] == "ok" and pair[1]["ref"] == pair[0]["id"]
    printed = capsys.readouterr().out
    assert "memory/notes/pay-the-backblaze-renewal.md" in printed and text in printed


@pytest.mark.blocking
def test_task_and_note_render_from_their_templates(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "task", "draft chapter 3", "oct 20") == 0
    assert run_capture(base, "task", "read the CPO paper") == 0
    assert run_capture(base, "note", "thesis idea: memory as reconstruction") == 0
    task = brief_io_parse((base / "memory/notes/draft-chapter-3.md").read_text())[0]
    assert task["due"] == "2026-10-20T09:00:00-07:00" and task["priority"] == 2
    assert (
        brief_io_parse((base / "memory/notes/read-the-cpo-paper.md").read_text())[0]["due"] is None
    )
    note = brief_io_parse(
        (base / "memory/notes/thesis-idea-memory-as-reconstruction.md").read_text()
    )
    assert (
        note[0]["type"] == "note" and note[1].strip() == "# thesis idea: memory as reconstruction"
    )


@pytest.mark.blocking
def test_friction_appends_exactly_one_line_and_changes_no_byte_before_the_end(
    tmp_path: Path,
) -> None:
    base = write_vault(tmp_path)
    before = (base / FRICTION).read_bytes()
    assert run_capture(base, "friction", "reviewer out of quota — KGME should know") == 0
    after = (base / FRICTION).read_bytes()
    assert after[: len(before)] == before
    assert (
        after[len(before) :]
        == "- 2026-10-15 14:30 — reviewer out of quota — KGME should know\n".encode()
    )


@pytest.mark.blocking
def test_an_append_to_a_file_without_a_final_newline_starts_its_own_line(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    (base / FRICTION).write_bytes((base / FRICTION).read_bytes().rstrip(b"\n"))
    before = (base / FRICTION).read_bytes()
    assert run_capture(base, "friction", "one more") == 0
    after = (base / FRICTION).read_bytes()
    assert after[: len(before)] == before
    assert after[len(before) :] == "\n- 2026-10-15 14:30 — one more\n".encode()


@pytest.mark.blocking
def test_a_daily_line_lands_under_a_closing_michou_heading(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    daily = base / "memory" / "daily" / "2026-10-15.md"
    daily.write_text("---\nid: 20261015T070000\n---\n\n# Thursday\n\n## Today\n- worked\n")
    before = daily.read_bytes()
    assert run_capture(base, "daily", "finished the costing homework") == 0
    assert run_capture(base, "daily", "thesis reading done") == 0
    after = daily.read_bytes()
    assert after[: len(before)] == before
    added = after[len(before) :].decode()
    assert added == (
        f"\n## Michou\n{capture.MICHOU_MARK}\n- finished the costing homework\n"
        "- thesis reading done\n"
    )


@pytest.mark.blocking
def test_a_daily_line_before_the_note_exists_is_held_in_the_ledger(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "daily", "long day of reviews") == 0
    assert not (base / "memory" / "daily" / "2026-10-15.md").exists()
    intent = read_job(base, "capture", "intent")[-1]
    assert intent["key"].startswith("capture:daily:2026-10-15:")
    assert intent["summary"] == "capture daily held 2026-10-15: long day of reviews"


@pytest.mark.blocking
def test_words_a_summary_would_change_are_refused_rather_than_held(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "daily", "x" * 190) == 1
    assert run_capture(base, "daily", "the api_key: hunter2 was in the log") == 1
    outcomes = read_job(base, "capture", "outcome")
    assert [o["status"] for o in outcomes] == ["refused", "refused"]
    assert all(o["class"] == "blocking" for o in outcomes)


@pytest.mark.blocking
def test_a_taken_name_gets_a_new_file_and_the_old_one_is_untouched(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "note", "same words") == 0
    first = (base / "memory/notes/same-words.md").read_bytes()
    assert run_capture(base, "note", "Same words!") == 0  # other words, the same name
    assert (base / "memory/notes/same-words.md").read_bytes() == first
    assert (base / "memory/notes/same-words-2.md").is_file()


@pytest.mark.blocking
def test_a_missing_friction_log_is_refused_never_created(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    (base / FRICTION).unlink()
    assert run_capture(base, "friction", "something") == 1
    assert not (base / FRICTION).exists()
    outcome = read_job(base, "capture", "outcome")[-1]
    assert outcome["status"] == "refused" and "something" in outcome["summary"]


@pytest.mark.blocking
def test_a_friction_log_that_is_a_link_is_refused_and_its_target_untouched(
    tmp_path: Path,
) -> None:
    base = write_vault(tmp_path)
    target = base / "docs" / "elsewhere.md"
    target.write_text("keep\n")
    (base / FRICTION).unlink()
    (base / FRICTION).symlink_to(target)
    assert run_capture(base, "friction", "something") == 1
    assert target.read_text() == "keep\n"
    assert "symlink" in read_job(base, "capture", "outcome")[-1]["summary"]


@pytest.mark.blocking
def test_a_notes_folder_reached_through_a_link_is_refused(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    real = tmp_path / "outside"
    (base / "memory" / "notes").rename(real)
    (base / "memory" / "notes").symlink_to(real)
    before = {p.name for p in real.iterdir()}
    assert run_capture(base, "note", "through the link") == 1
    assert {p.name for p in real.iterdir()} == before


@pytest.mark.blocking
@pytest.mark.parametrize(
    ("due", "why"),
    [
        ("whenever", "could not read"),
        ("next friday", "ambiguous"),
        ("2026-10-01", "already past"),
        ("2026-02-30", "not a real day"),
    ],
)
def test_an_unreadable_due_is_a_refusal_that_records_the_words(
    tmp_path: Path, capsys, due: str, why: str
) -> None:
    base = write_vault(tmp_path)
    before = notes(base)
    assert run_capture(base, "remind", "call the reader", due) == 1
    assert notes(base) == before
    outcome = read_job(base, "capture", "outcome")[-1]
    assert outcome["status"] == "refused" and why in outcome["summary"]
    assert "call the reader" in outcome["summary"]
    assert why in capsys.readouterr().err


@pytest.mark.blocking
def test_a_reminder_without_a_due_is_refused(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "remind", "call the reader") == 1
    assert "needs --due" in read_job(base, "capture", "outcome")[-1]["summary"]


@pytest.mark.blocking
@pytest.mark.parametrize(
    ("kind", "words", "due"),
    [("friction", "x", "tomorrow"), ("note", "", None), ("task", "two\nlines", None)],
)
def test_usage_errors_exit_2_and_record_nothing(tmp_path: Path, kind, words, due) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, kind, words, due) == 2
    assert read_job(base, "capture") == []


@pytest.mark.blocking
def test_a_held_lock_refuses_the_run(tmp_path: Path, monkeypatch) -> None:
    base = write_vault(tmp_path)
    monkeypatch.setattr(capture_fs, "LOCK_WAIT_SECONDS", 0.0)
    holder = os.open(base / ".git" / capture_fs.LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(holder, fcntl.LOCK_EX)
    try:
        assert run_capture(base, "note", "while held") == 1
    finally:
        os.close(holder)
    assert not (base / "memory/notes/while-held.md").exists()
    assert "holds the vault" in read_job(base, "capture", "outcome")[-1]["summary"]


@pytest.mark.blocking
def test_open_intents_are_settled_by_their_evidence_and_stop_on_doubt(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    places = capture_io.read_places(SETTINGS, base)

    def plant(destination: str, offset: int, data: bytes, payload: bool = True) -> dict:
        whole = (base / destination).read_bytes() if offset else b""
        facts = {
            "mode": "replace" if offset else "new",
            "destination": destination,
            "offset": offset,
            "size": len(data),
            "sha256": capture_record.sha256_bytes(data),
            "bytes": data.decode(),
            "before_sha256": capture_record.sha256_bytes(whole[:offset]),
            "after_sha256": capture_record.sha256_bytes(whole[:offset] + data),
        }
        run_id = events.new_ulid()
        intent_id = capture_record.write_intent(places, run_id, f"k-{run_id}", "planted", facts)
        if not payload:
            ledger_intent = [e for e in read_job(base, "capture") if e["id"] == intent_id][0]
            (base / ledger_intent["payload_ref"]).unlink()
        return {"id": intent_id}

    written = (base / "memory/notes/plain.md").read_bytes()
    friction = (base / FRICTION).read_bytes()
    found = plant("memory/notes/plain.md", 0, written)
    appended = plant(str(FRICTION), len(friction) - 10, friction[-10:])
    lost = plant("memory/notes/gone.md", 0, b"gone\n")
    assert run_capture(base, "note", "next") == 0
    closed = {e["ref"]: e for e in read_job(base, "capture", "outcome")}
    assert closed[found["id"]]["status"] == "ok"
    assert closed[appended["id"]]["status"] == "ok"
    assert (closed[lost["id"]]["status"], closed[lost["id"]]["class"]) == ("error", "transient")
    for planted in (
        plant("memory/notes/plain.md", 0, written + b"more"),
        plant("memory/notes/plain.md", 0, written, payload=False),
    ):
        assert run_capture(base, "note", "stopped") == 1
        closed = {e["ref"]: e for e in read_job(base, "capture", "outcome")}
        assert (closed[planted["id"]]["status"], closed[planted["id"]]["class"]) == (
            "error",
            "blocking",
        )
        assert "repair it by hand" in read_job(base, "capture", "outcome")[-1]["summary"]
    assert not (base / "memory/notes/stopped.md").exists()


@pytest.mark.blocking
def test_due_words_resolve_in_the_configured_zone() -> None:
    def due(words: str, now: datetime = THURSDAY) -> str:
        return capture.instant_text(capture.resolve_due(words, now, ZONE))

    assert due("friday 9am") == "2026-10-16T09:00:00-07:00"
    assert due("thursday 9am") == "2026-10-22T09:00:00-07:00"  # today's 9am has passed
    assert due("thursday 6pm") == "2026-10-15T18:00:00-07:00"
    assert due("tomorrow") == "2026-10-16T09:00:00-07:00"
    assert due("tomorrow at 14:00") == "2026-10-16T14:00:00-07:00"
    assert due("9am") == "2026-10-16T09:00:00-07:00"
    assert due("5pm") == "2026-10-15T17:00:00-07:00"
    assert due("noon") == "2026-10-16T12:00:00-07:00"
    assert due("in 3 days") == "2026-10-18T09:00:00-07:00"
    assert due("in 2 weeks") == "2026-10-29T09:00:00-07:00"
    assert due("20 october 9:30 pm") == "2026-10-20T21:30:00-07:00"
    assert due("nov 3") == "2026-11-03T09:00:00-08:00"  # after the change to standard time
    assert due("jan 5") == "2027-01-05T09:00:00-08:00"
    assert due("2026-12-01 14:00") == "2026-12-01T14:00:00-08:00"
    for words in ("13pm", "25:00", "friday at", "someday"):
        with pytest.raises(capture.Unreadable):
            due(words)


@pytest.mark.blocking
def test_acceptance_the_next_morning_brief_lists_the_reminder_and_the_friction_line(
    tmp_path: Path, capsys
) -> None:
    base = write_vault(tmp_path)
    assert run_capture(base, "remind", "pay the Backblaze renewal", "friday 9am") == 0
    assert run_capture(base, "friction", "renewal almost missed — KGME should remind") == 0
    capsys.readouterr()
    assert brief_io.run_brief("2026-10-16", True, base, SETTINGS) == 0
    text = capsys.readouterr().out
    assert "due today 2026-10-16 09:00  pay the Backblaze renewal" in text
    assert "- 2026-10-15 14:30 — renewal almost missed — KGME should remind" in text


@pytest.mark.blocking
def test_only_the_filesystem_module_opens_a_vault_file_for_writing() -> None:
    """In the run layers, no file is opened, written, or replaced except through
    `kgme.capture_fs` (the lock, the replace, the publish) and `clean_fs.write_payload` (the
    payload, inside `capture_record`); a new note is published by `link`, which never
    replaces, from a temp file created `O_EXCL`; a line is added by exchanging names, never by
    a rename that would discard what it replaces, and the displaced copy is never removed."""
    for module in ("capture_io", "daily_io"):
        source = (Path(capture_io.__file__).parent / f"{module}.py").read_text()
        for call in ("os.open(", "open(", "write_payload(", "os.replace(", "os.rename("):
            assert call not in source.replace("capture_fs.", ""), (module, call)
    fs = Path(capture_fs.__file__).read_text()
    assert "os.link(" in fs and "os.replace(" not in fs and "os.rename(" not in fs
    assert "write_exchanged(" in fs
    # capture deletes nothing (the rulings on cycle 6 F13 and F15): the one unlink is
    # `write_new`'s, of a temp name whose inode the new note keeps, or of its own bytes
    assert fs.count("os.unlink(") == 1 and "os.remove(" not in fs
    assert clean_fs.NEW_FILE_FLAGS & os.O_EXCL
