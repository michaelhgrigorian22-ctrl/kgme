"""Tests for the bounds of a `kgme clean` run after review cycles 3 and 4 of HANDOFF-0033.

Purpose: the command takes no path and acts on this repository's root, a seeded checkout is
reached only by the direct call the tests make, and a base inside or above the authorized
root is refused before anything (F9); the payload is written whole or the run is refused
before any deletion (F10).
Inputs: the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files, directories with their modes restored at the end, and ledger lines
under `tmp_path` only; `clean_fs.os` and `clean_io.run_clean` are patched for one test each.
"""

import errno
import os
from pathlib import Path

import pytest
from cleantools import SETTINGS, OsWith, read_recorded, run_clean, write_seed

from kgme import clean_fs, clean_io, cli, paths

BRIEF = "memory/agent/brief/2026-10-01.md"


@pytest.mark.blocking
def test_the_command_takes_no_path_and_a_seed_is_reached_only_directly(
    tmp_path: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    inside = base / "docs"
    (inside / "memory" / "agent").mkdir(parents=True)
    (inside / "memory" / "agent" / "x.md").write_text("x\n")
    assert clean_io.run_clean("agent", True, inside, SETTINGS, home=base) == 2
    assert "not a git checkout" in capsys.readouterr().err
    (inside / ".git").mkdir()
    assert clean_io.run_clean("agent", True, inside, SETTINGS, home=base) == 2
    assert "inside or above this repository" in capsys.readouterr().err
    (tmp_path / ".git").mkdir()
    assert clean_io.run_clean("agent", True, tmp_path, SETTINGS, home=base) == 2
    assert "inside or above this repository" in capsys.readouterr().err
    assert (inside / "memory" / "agent" / "x.md").exists() and read_recorded(base) == []
    assert clean_io.run_clean("agent", False, base, SETTINGS, home=base) == 0, "the root runs"
    seen: dict = {}

    def record(target, delete, base_, settings, home=None) -> int:
        seen.update(target=target, base=base_, home=home)
        return 0

    monkeypatch.setattr(clean_io, "run_clean", record)
    assert cli.main(["clean", "agent"]) == 0
    assert seen == {"target": "agent", "base": paths.root(), "home": None}
    with pytest.raises(SystemExit):
        cli.main(["clean", "agent", "--base", str(base)])
    assert "unrecognized arguments: --base" in capsys.readouterr().err


@pytest.mark.blocking
def test_a_short_write_is_completed_before_any_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    calls: list[int] = []

    def seven_bytes_at_a_time(fd: int, data) -> int:
        calls.append(fd)
        return os.write(fd, bytes(data[:7]))

    monkeypatch.setattr(clean_fs, "os", OsWith(write=seven_bytes_at_a_time))
    assert run_clean(base, "agent", "--yes") == 0
    assert len(calls) > 10, "the payload took many short writes"
    intent = read_recorded(base, "intent")[0]
    text = (base / intent["payload_ref"]).read_text()
    assert text.endswith("}\n") and "memory/agent/note.md" in text
    assert not (base / BRIEF).exists()


@pytest.mark.blocking
def test_a_failed_payload_write_refuses_the_run_before_any_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    calls: list[int] = []

    def full_after_one(fd: int, data) -> int:
        calls.append(fd)
        if len(calls) > 1:
            raise OSError(errno.ENOSPC, "No space left on device")
        return os.write(fd, bytes(data[:7]))

    monkeypatch.setattr(clean_fs, "os", OsWith(write=full_after_one))
    assert run_clean(base, "agent", "--yes") == 1
    assert (base / BRIEF).exists() and (base / "memory" / "agent" / "note.md").exists()
    assert [p.name for p in (base / "logs" / "scratch" / "payloads").iterdir()] == ["a.json"]
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert "could not be written whole: No space left on device" in outcomes[0]["summary"]
    assert outcomes[-1]["summary"].startswith("closed: refused, nothing deleted")
    assert read_recorded(base, "intent")[0]["payload_ref"] is None
