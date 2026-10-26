"""Tests for what review cycle 1 of HANDOFF-0034 (AUDIT-0051) asked of `kgme brief`: its inputs
(moved out of `tests/test_brief_review.py` by HANDOFF-0060 §3, unchanged).

Purpose: a date that is not a real `YYYY-MM-DD` exits 2 before anything (F7); an input's hash
is its bytes, and invalid UTF-8 is refused (F8); due instants sort and group by time in the
configured zone (F9); an unreadable input directory refuses the run (F11).
Inputs: the seeded vault of `tests/brieftools.py`.
Outputs: pytest assertions.
Side effects: files, modes restored at the end, and ledger lines under `tmp_path` only.
"""

import hashlib
from pathlib import Path

import pytest
from brieftools import BRIEF, DATE, note, read_recorded, run_brief, write_seed

# F7


@pytest.mark.blocking
@pytest.mark.parametrize("date", ["2026-02-30", "tomorrow", "/tmp/x", "../../docs/x", "2026-1-08"])
def test_a_date_that_is_not_a_real_day_exits_2_before_anything(tmp_path: Path, date: str) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base, date=date) == 2
    assert read_recorded(base) == []
    assert sorted(p.name for p in (base / "memory" / "agent" / "brief").iterdir()) == [
        "2026-10-07.md"
    ]


# F8


@pytest.mark.blocking
def test_an_inputs_hash_is_its_bytes_crlf_included(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    crlf = base / "memory" / "notes" / "call-reader.md"
    crlf.write_bytes(crlf.read_bytes().replace(b"\n", b"\r\n"))
    assert run_brief(base) == 0
    digest = hashlib.sha256(crlf.read_bytes()).hexdigest()
    assert f"memory/notes/call-reader.md — sha256 {digest}" in (base / BRIEF).read_text()


@pytest.mark.blocking
def test_an_input_that_is_not_utf8_is_refused(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    bad = base / "memory" / "notes" / "plain.md"
    bad.write_bytes(bad.read_bytes() + b"\xff\xfe\n")
    assert run_brief(base) == 1
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["class"] == "blocking" and "UTF-8" in outcome["summary"]


# F9


@pytest.mark.blocking
def test_due_instants_sort_and_group_by_time_in_the_configured_zone(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    notes = base / "memory" / "notes"
    for name, ident, due in (
        ("paris.md", "20261001T090010", f"{DATE}T17:00:00+02:00"),
        ("pacific.md", "20261001T090011", f"{DATE}T09:00:00-07:00"),
        ("tokyo.md", "20261001T090012", "2026-10-09T03:00:00+09:00"),
    ):
        (notes / name).write_text(
            note("reminder", ident, "open", f"# {name}", due=due, repeat=None, channel="phone")
        )
    assert run_brief(base) == 0
    lines = (base / BRIEF).read_text().splitlines()
    due_today = [line.split("  ")[0:2] for line in lines if line.startswith("- due today ")]
    assert due_today == [
        [f"- due today {DATE} 08:00", "paris.md"],
        [f"- due today {DATE} 09:00", "pacific.md"],
        [f"- due today {DATE} 11:00", "tokyo.md"],
        [f"- due today {DATE} 18:00", "Chapter 2 draft"],
    ], "chronological, and Tokyo's 03:00 on the 9th is 11:00 Pacific on the 8th"


# F11 (cycle 2)


@pytest.mark.blocking
def test_an_unreadable_input_directory_refuses_the_run(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    before = (base / BRIEF).read_bytes()
    hidden = base / "memory" / "notes" / "hidden"
    hidden.mkdir()
    (hidden / "task.md").write_text(
        note("task", "20261001T090020", "open", "# Hidden task", due=None, project=None, priority=1)
    )
    hidden.chmod(0o000)
    try:
        assert run_brief(base) == 1
    finally:
        hidden.chmod(0o755)
    assert (base / BRIEF).read_bytes() == before, "the brief is not replaced by an incomplete one"
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["status"] == "refused" and outcome["class"] == "blocking"
    assert "memory/notes/hidden" in outcome["summary"]
