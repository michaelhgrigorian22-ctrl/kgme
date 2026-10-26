"""Tests for how `kgme capture` adds a line to an existing vault file (HANDOFF-0050).

Purpose: the whole-file replace the arbiter's ruling after AUDIT-0062 asked for (F10), and the
kept copy the arbiter's ruling on F13 and F15 (option A) and Cowork's refinement asked for:
the file is replaced whole by an exchange of names, so it is never torn; an interruption
before the exchange leaves it byte-identical; a save made by an editor during the capture is
kept; capture deletes nothing, so the copy the exchange displaced stays, named with the
intent id, and only `kgme clean kept` removes it, when its bytes are still the ones the
capture recorded. Each test ran red before its fix (the review-loop reader's rule).
Inputs: the seeded vault of `tests/capturetools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only; `kgme.capture_fs` calls are
patched for the interruption and concurrent-writer tests.
"""

import os
import subprocess
from pathlib import Path

import pytest
from brieftools import SETTINGS
from capturetools import read_job, run_capture, write_vault
from clocktools import FROZEN, freeze

from kgme import capture_fs, clean_fs, clean_io, paths

TODAY = FROZEN.date().isoformat()


@pytest.fixture(autouse=True)
def frozen(monkeypatch) -> None:
    """Every test reads one clock, frozen at `FROZEN` (HANDOFF-0060 §1): "today" here and in
    the code are the same day, whenever the run starts or ends."""
    freeze(monkeypatch)


FRICTION = Path("memory/inbox/friction-log.md")


def exchange_name() -> str:
    """The exchange of names in `kgme.capture_fs`, by its name before and after F16."""
    return "write_exchanged" if hasattr(capture_fs, "write_exchanged") else "swap_names"


def kept_copies(base: Path) -> list[Path]:
    return sorted(p for p in (base / FRICTION).parent.iterdir() if ".capture-" in p.name)


def clean_kept(base: Path) -> int:
    return clean_io.run_clean("kept", True, base, SETTINGS, home=base)


def saved_once_then(base: Path, publish, then=None):
    """An exchange that, on its first call, is preceded by an editor's completed save, and on
    its second call does `then` instead when given."""
    calls = []

    def call(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            with (base / FRICTION).open("ab") as log:
                log.write(b"- Michou saved this first\n")
        elif then is not None:
            return then(*args, **kwargs)
        return publish(*args, **kwargs)

    return call


# Cycle 5 (the arbiter's ruling after AUDIT-0062, F10: remove the mechanism)


@pytest.mark.blocking
@pytest.mark.parametrize("kind", ["friction", "daily"])
def test_c5_an_interruption_before_the_exchange_leaves_the_file_byte_identical(
    tmp_path: Path, monkeypatch, kind: str
) -> None:
    base = write_vault(tmp_path, TODAY)
    target = FRICTION if kind == "friction" else Path("memory/daily") / f"{TODAY}.md"
    if kind == "daily":
        (base / target).write_text("---\nid: 20261015T070000\n---\n\n# Today\n\n- worked\n")
    before = (base / target).read_bytes()

    def interrupted(*args, **kwargs) -> None:
        raise KeyboardInterrupt

    with monkeypatch.context() as patch:
        patch.setattr(capture_fs, exchange_name(), interrupted)
        try:
            run_capture(base, kind, "cut short", now=None)
        except KeyboardInterrupt:
            pass
    assert (base / target).read_bytes() == before
    assert run_capture(base, kind, "cut short", now=None) == 0
    after = (base / target).read_bytes()
    assert after.startswith(before) and after.count(b"cut short") == 1
    assert clean_kept(base) == 0  # the interrupted copy held only the capture's own bytes


@pytest.mark.blocking
def test_c5_an_edit_made_during_the_capture_is_kept_and_nothing_is_replaced(
    tmp_path: Path, monkeypatch
) -> None:
    base = write_vault(tmp_path)
    whole = clean_fs.write_whole

    def edited_meanwhile(fd: int, data: bytes) -> None:
        if not data.startswith(b"{"):  # the kept copy, not a payload
            with (base / FRICTION).open("ab") as log:
                log.write(b"- Michou typed this in Obsidian\n")
        whole(fd, data)

    with monkeypatch.context() as patch:
        patch.setattr(clean_fs, "write_whole", edited_meanwhile)
        assert run_capture(base, "friction", "said during an edit") == 1
    text = (base / FRICTION).read_text()
    assert text.endswith("- Michou typed this in Obsidian\n") and "said during" not in text
    summary = read_job(base, "capture", "outcome")[-1]["summary"]
    assert "changed while the capture was made" in summary
    assert clean_kept(base) == 0


# Cycle 6 (AUDIT-0063)


@pytest.mark.blocking
def test_c6_f13_a_save_after_the_last_check_is_kept_and_nothing_is_replaced(
    tmp_path: Path, monkeypatch
) -> None:
    """The editor saves in place at the last moment: after every check, as the new file is
    put in place."""
    base = write_vault(tmp_path)
    name = exchange_name()
    with monkeypatch.context() as patch:
        patch.setattr(capture_fs, name, saved_once_then(base, getattr(capture_fs, name)))
        assert run_capture(base, "friction", "said at the last moment") == 1
    text = (base / FRICTION).read_text()
    assert text.endswith("- Michou saved this first\n")
    assert "said at the last moment" not in text
    assert clean_kept(base) == 0


@pytest.mark.blocking
def test_c6_f13_a_save_on_each_side_of_the_exchange_keeps_both_files(
    tmp_path: Path, monkeypatch
) -> None:
    base = write_vault(tmp_path)
    name = exchange_name()
    exchange = getattr(capture_fs, name)

    def saved_each_time(*args, **kwargs):
        with (base / FRICTION).open("ab") as log:
            log.write(b"- a save\n")
        return exchange(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(capture_fs, name, saved_each_time)
        assert run_capture(base, "friction", "said between saves") == 1
    kept = kept_copies(base)
    assert len(kept) == 1 and kept[0].name in read_job(base, "capture", "outcome")[-1]["summary"]
    assert (base / FRICTION).read_text().endswith("- a save\n")
    assert kept[0].read_text().endswith("— said between saves\n- a save\n")
    assert clean_kept(base) == 1 and kept[0].exists()


# Cycle 7 (AUDIT-0064; the arbiter's ruling on F13 and F15, option A, with Cowork's refinement)


@pytest.mark.blocking
def test_c7_f13_a_write_through_a_descriptor_held_across_the_capture_is_kept(
    tmp_path: Path,
) -> None:
    base = write_vault(tmp_path)
    held = os.open(base / FRICTION, os.O_WRONLY | os.O_APPEND)
    try:
        assert run_capture(base, "friction", "said while a save was in flight") == 0
        os.write(held, b"- the save in flight\n")
    finally:
        os.close(held)
    kept = kept_copies(base)
    assert len(kept) == 1 and kept[0].read_bytes().endswith(b"- the save in flight\n")
    assert clean_kept(base) == 1
    assert kept[0].read_bytes().endswith(b"- the save in flight\n")
    assert kept[0].name in read_job(base, "clean", "outcome")[0]["summary"]
    assert run_capture(base, "friction", "said after the save") == 1
    assert kept[0].name in read_job(base, "capture", "outcome")[-1]["summary"]
    assert b"said after the save" not in (base / FRICTION).read_bytes()


@pytest.mark.blocking
def test_c7_f15_a_failed_check_after_the_exchange_keeps_the_save_and_fails(
    tmp_path: Path, monkeypatch
) -> None:
    base = write_vault(tmp_path)
    name = exchange_name()

    def unreadable(*args, **kwargs):
        raise OSError(5, "read failed after the exchange")

    with monkeypatch.context() as patch:
        patch.setattr(capture_fs, name, saved_once_then(base, getattr(capture_fs, name)))
        patch.setattr(capture_fs, "read_name", unreadable)
        assert run_capture(base, "friction", "said as the check failed") != 0
    everything = b"".join(p.read_bytes() for p in [base / FRICTION, *kept_copies(base)])
    assert b"- Michou saved this first\n" in everything
    assert read_job(base, "capture", "outcome")[-1]["status"] != "ok"


@pytest.mark.blocking
def test_c7_f15_a_failed_rollback_keeps_the_save_and_fails(tmp_path: Path, monkeypatch) -> None:
    base = write_vault(tmp_path)
    name = exchange_name()

    def stuck(*args, **kwargs):
        raise OSError(5, "the exchange back failed")

    with monkeypatch.context() as patch:
        patch.setattr(capture_fs, name, saved_once_then(base, getattr(capture_fs, name), stuck))
        assert run_capture(base, "friction", "said as the rollback failed") != 0
    everything = b"".join(p.read_bytes() for p in [base / FRICTION, *kept_copies(base)])
    assert b"- Michou saved this first\n" in everything
    assert read_job(base, "capture", "outcome")[-1]["status"] != "ok"


@pytest.mark.blocking
def test_c7_a_kept_copy_still_as_read_is_removed_by_kgme_clean_kept(tmp_path: Path) -> None:
    base = write_vault(tmp_path)
    before = (base / FRICTION).read_bytes()
    assert run_capture(base, "friction", "said cleanly") == 0
    kept = kept_copies(base)
    intent = [e for e in read_job(base, "capture", "intent") if e["payload_ref"]][-1]
    assert [p.name for p in kept] == [f".friction-log.md.capture-{intent['id']}"]
    assert kept[0].read_bytes() == before
    assert clean_kept(base) == 0
    assert kept_copies(base) == []


@pytest.mark.blocking
def test_c7_git_ignores_a_kept_copy() -> None:
    name = "memory/inbox/.friction-log.md.capture-01M5EMAEG872P34RMNTER7D86P"
    found = subprocess.run(["git", "check-ignore", "-q", name], cwd=paths.root(), check=False)
    assert found.returncode == 0
