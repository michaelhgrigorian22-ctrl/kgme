"""Tests for what review cycle 5 of HANDOFF-0033 (AUDIT-0047) asked of the rebuilt deleter.

Purpose: the payload directory swapped for a link after its last ancestry check, before or
after it is opened, cannot carry the payload out of the repository's scratch (F8); a payload
altered or replaced by a link before reconciliation is not evidence, its plan is closed
`blocking`, and the run stops before planning (F14); a run that cannot take
`kgme-clean.lock` does nothing, so it cannot close a live run's intent (F15); a FIFO under
a target refuses the plan, and hashing one never waits on it (F16).
Inputs: the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files, directories, a FIFO, a lock, and ledger lines under `tmp_path` only;
`clean_fs.read_bound_directory` and `clean_fs.os` are patched for one test each.
"""

import json
import os
from pathlib import Path

import pytest
from cleantools import OsWith, plant_interrupted_run, read_recorded, run_clean, write_seed

from kgme import clean, clean_fs

BRIEF = "memory/agent/brief/2026-10-01.md"


def swap_payloads_for_docs(base: Path) -> None:
    payloads = base / "logs" / "scratch" / "payloads"
    payloads.rename(payloads.with_name("payloads.real"))
    os.symlink(base / "docs", payloads)


@pytest.mark.blocking
def test_a_payload_directory_swapped_before_it_is_opened_refuses_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    original = clean_fs.read_bound_directory

    def swap_then_bind(directory: Path, root: Path) -> int:
        swap_payloads_for_docs(base)
        return original(directory, root)

    monkeypatch.setattr(clean_fs, "read_bound_directory", swap_then_bind)
    assert run_clean(base, "agent", "--yes") == 1
    assert sorted(p.name for p in (base / "docs").iterdir()) == ["keep.md"]
    assert (base / BRIEF).exists() and (base / "memory" / "agent" / "note.md").exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and "payload directory" in outcomes[0]["summary"]
    assert outcomes[-1]["summary"].startswith("closed: refused, nothing deleted")


@pytest.mark.blocking
def test_a_payload_directory_swapped_after_it_is_opened_keeps_the_payload_inside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    swapped = False

    def swap_then_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if "dir_fd" in kwargs and not swapped:
            swapped = True
            swap_payloads_for_docs(base)
        return os.open(path, flags, *args, **kwargs)

    monkeypatch.setattr(clean_fs, "os", OsWith(open=swap_then_open))
    run_clean(base, "agent", "--yes")
    assert swapped
    assert sorted(p.name for p in (base / "docs").iterdir()) == ["keep.md"]
    real = base / "logs" / "scratch" / "payloads.real"
    assert any(p.name.startswith("clean-agent-") for p in real.iterdir()), "landed where bound"


@pytest.mark.blocking
def test_an_altered_payload_is_not_evidence_and_stops_the_run(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent, record = plant_interrupted_run(base, [BRIEF], [])
    payload = base / intent["payload_ref"]
    record["files"][1]["path"] = "memory/agent/invented.md"
    payload.write_text(json.dumps(record) + "\n")
    assert run_clean(base, "agent", "--yes") == 1
    assert (base / "memory" / "agent" / "note.md").exists(), "nothing planned or deleted"
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    assert "does not match the hash its intent recorded" in closing[0]["summary"]
    assert not any("invented" in e["summary"] for e in read_recorded(base))
    assert len(read_recorded(base, "intent")) == 1, "no new plan after the stop"


@pytest.mark.blocking
def test_a_payload_replaced_by_a_link_is_not_evidence(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent, _ = plant_interrupted_run(base, [BRIEF], [])
    payload = base / intent["payload_ref"]
    copy = tmp_path / "elsewhere.json"
    copy.write_bytes(payload.read_bytes())
    payload.unlink()
    os.symlink(copy, payload)
    assert run_clean(base, "agent") == 1
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert len(closing) == 1 and closing[0]["class"] == "blocking"
    assert "could not be read" in closing[0]["summary"] or "symlink" in closing[0]["summary"]


@pytest.mark.blocking
def test_a_run_that_cannot_take_the_lock_does_nothing(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent, _ = plant_interrupted_run(base, [BRIEF], [])
    held = clean_fs.write_lock(base)
    assert held is not None
    try:
        assert run_clean(base, "agent") == 1
        assert run_clean(base, "agent", "--yes") == 1
    finally:
        os.close(held)
    assert not [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]], "open"
    assert len(read_recorded(base, "note")) == 0
    assert (base / "memory" / "agent" / "note.md").exists()
    assert run_clean(base, "agent") == 0, "once the holder is gone the plan is reconciled"
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert closing[-1]["summary"].startswith("closed: reconciled on start")


@pytest.mark.blocking
def test_a_fifo_under_a_target_refuses_the_plan(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    fifo = base / "logs" / "scratch" / "pipe"
    os.mkfifo(fifo)
    assert run_clean(base, "scratch", "--yes") == 1
    assert fifo.exists() and (base / "logs" / "scratch" / "review.patch").exists()
    outcomes = read_recorded(base, "outcome")
    assert any("not a regular file or directory" in o["summary"] for o in outcomes)
    assert outcomes[-1]["summary"].startswith("closed: refused, nothing deleted")


@pytest.mark.blocking
def test_hashing_a_fifo_is_refused_without_waiting(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    fifo = base / "memory" / "agent" / "pipe"
    os.mkfifo(fifo)
    status = os.lstat(fifo)
    as_planned = clean.Entry(fifo, fifo, False, False, 0, status.st_dev, status.st_ino)
    with pytest.raises(clean_fs.Refused, match="not a regular file"):
        clean_fs.read_digest(fifo, as_planned)
