"""Tests for the brief's `Kept copies` section (HANDOFF-0052).

Purpose: the handoff's acceptance test end to end, on copies `kgme capture` really kept:
three copies beside a past day's note and the friction log, one still the file as read, one
the capture's own bytes, one edited after the fact; the brief names the edited one and its
file and counts the other two with their size and the command; `kgme clean kept --yes`
refuses and removes nothing; after the edited copy is deleted by hand it removes the other
two, and the next brief says there are none. Also: a copy no capture recorded and a copy the
gate refuses are named; the brief deletes nothing; the one rule (`holds_save`) at both
digest lengths its callers pass.
Inputs: the seeded vault of `tests/capturetools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only.
"""

from pathlib import Path

import brieftools
import pytest
from capturetools import SETTINGS, run_capture, write_vault

from kgme import brief_io, capture_recover, clean_io
from kgme import capture_record as record

TODAY = "2026-10-15"  # the captures' day (capturetools' THURSDAY)
NEXT = "2026-10-16"  # the brief's: the daily note is a past day's
DAILY = Path("memory/daily") / f"{TODAY}.md"
FRICTION = Path("memory/inbox/friction-log.md")
COUNT_LINE = (
    "- 2 kept copies are still what their capture kept, {size:,} bytes in all: "
    "`kgme clean kept --yes` clears them"
)


def kept(base: Path, beside: Path) -> list[Path]:
    """The copies beside one file, oldest capture first (the intent ids sort by time)."""
    return sorted(
        p for p in (base / beside).parent.iterdir() if p.name.startswith(f".{beside.name}.capture-")
    )


def brief_text(base: Path, capsys) -> str:
    capsys.readouterr()
    assert brief_io.run_brief(NEXT, True, base, SETTINGS) == 0
    return capsys.readouterr().out


def clean_kept(base: Path) -> int:
    return clean_io.run_clean("kept", True, base, SETTINGS, home=base)


@pytest.mark.blocking
def test_the_acceptance_test(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path, TODAY)
    # the day's note exists, so a daily capture replaces it whole and keeps a copy
    (base / DAILY).write_text(
        brieftools.DAILY.replace(brieftools.DATE, TODAY).replace("20261008T", "20261015T")
    )
    assert run_capture(base, "daily", "a line for the day") == 0
    for words in ("the first friction", "the second friction"):
        assert run_capture(base, "friction", words) == 0
    (edited,) = kept(base, DAILY)
    as_kept, as_read = kept(base, FRICTION)
    # the first friction copy is set to that capture's own bytes, which the second capture
    # read as the file; the daily copy is edited after the fact
    as_kept.write_bytes(as_read.read_bytes())
    edited.write_bytes(edited.read_bytes() + b"- a save made in the copy\n")
    text = brief_text(base, capsys)
    section = text.split("## Kept copies\n", 1)[1].split("\n## ", 1)[0]
    assert section.splitlines() == [
        f"- `{edited.relative_to(base).as_posix()}` holds a save `{DAILY.as_posix()}` lacks: "
        "merge it by hand, then delete it",
        COUNT_LINE.format(size=as_kept.stat().st_size + as_read.stat().st_size),
    ]
    assert clean_kept(base) == 1
    assert all(p.exists() for p in (edited, as_kept, as_read))
    edited.unlink()  # merged by hand
    assert clean_kept(base) == 0
    assert kept(base, DAILY) == [] and kept(base, FRICTION) == []
    assert "## Kept copies\nNo kept copies under memory/.\n" in brief_text(base, capsys)


@pytest.mark.blocking
def test_a_copy_no_capture_recorded_is_named(tmp_path: Path, capsys) -> None:
    base = write_vault(tmp_path, TODAY)
    stray = base / "memory" / "inbox" / ".friction-log.md.capture-01M5EMAEG872P34RMNTER7D86P"
    stray.write_text("a copy with no note\n")
    assert (
        "- `memory/inbox/.friction-log.md.capture-01M5EMAEG872P34RMNTER7D86P` holds a save "
        "`memory/inbox/friction-log.md` lacks: merge it by hand, then delete it "
        "(no kgme capture recorded it)"
    ) in brief_text(base, capsys)


@pytest.mark.blocking
def test_a_copy_the_gate_refuses_is_named_and_the_brief_deletes_nothing(
    tmp_path: Path, capsys
) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "friction", "the first friction") == 0
    assert run_capture(base, "friction", "the second friction") == 0
    first, _ = kept(base, FRICTION)
    outside = tmp_path / "outside.md"
    outside.write_text("not the vault's\n")
    first.unlink()
    first.symlink_to(outside)
    before = {
        p: (p.is_symlink(), p.read_bytes()) for p in (base / "memory").rglob("*") if p.is_file()
    }
    text = brief_text(base, capsys)
    assert f"- `{first.relative_to(base).as_posix()}` holds a save" in text
    assert "(could not be checked:" in text
    assert {
        p: (p.is_symlink(), p.read_bytes()) for p in (base / "memory").rglob("*") if p.is_file()
    } == before


@pytest.mark.blocking
def test_the_one_rule_at_both_digest_lengths() -> None:
    before, after = "a" * record.KEPT_DIGITS, "b" * record.KEPT_DIGITS
    for digest in ("a" * 64, "a" * 16, "b" * 64, "b" * 16):  # capture's whole hash, clean's prefix
        assert not capture_recover.holds_save(digest, (before, after))
    for digest in ("c" * 64, "c" * 16, "", "unreadable"):
        assert capture_recover.holds_save(digest, (before, after))
    assert capture_recover.holds_save("a" * 64, None)


@pytest.mark.blocking
def test_review_c1_f1_a_copy_whose_id_does_not_parse_is_named_with_its_file(
    tmp_path: Path, capsys
) -> None:
    """Review cycle 1 F1: discovery took only names whose intent id parses, so this copy,
    alone, read as "No kept copies" while `kgme clean kept` refused it as unrecorded."""
    base = write_vault(tmp_path, TODAY)
    (base / "memory" / "inbox" / ".friction-log.md.capture-orphan").write_text("kept by hand\n")
    text = brief_text(base, capsys)
    assert (
        "- `memory/inbox/.friction-log.md.capture-orphan` holds a save "
        "`memory/inbox/friction-log.md` lacks: merge it by hand, then delete it "
        "(no kgme capture recorded it)"
    ) in text
    assert "No kept copies" not in text


@pytest.mark.blocking
def test_review_c2_f3_a_copy_whose_name_names_no_file_is_named_and_the_brief_renders(
    tmp_path: Path, capsys
) -> None:
    """Review cycle 2 F3: `..capture-orphan` matches the glob, names no file, and raised
    before the gate, so one malformed copy stopped the brief."""
    base = write_vault(tmp_path, TODAY)
    (base / "memory" / "inbox" / "..capture-orphan").write_text("kept by hand\n")
    assert (
        "- `memory/inbox/..capture-orphan` holds a save `memory/inbox/?` lacks: merge it by "
        "hand, then delete it (no kgme capture recorded it; its name names no file)"
    ) in brief_text(base, capsys)
