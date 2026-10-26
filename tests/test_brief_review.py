"""Tests for what review cycle 1 of HANDOFF-0034 (AUDIT-0051) asked of `kgme brief`: the run.

Purpose: one test or more per blocking finding, each written and run red before its fix
(the review-loop reader's rule of 2026-10-14). A brief, payload, or payload directory that
is a link refuses the run and nothing outside `memory/agent/brief/` and scratch is read or
written (F1); a payload that is not the evidence its intent recorded, or names another
destination, is closed `blocking` (F2); a dry run leaves an open intent open and appends
exactly one note (F3); an intent that never wrote does not move the friction cutoff (F4);
a short write never leaves a torn brief (F5); read, identity, and replacement failures are
classified outcomes (F6). The inputs' findings (F7 to F9, F11) are in
`tests/test_brief_review_inputs.py`, cycle 3's gate in `tests/test_brief_review_gate.py`
(split by HANDOFF-0060 §3, moves only).
Inputs: the seeded vault of `tests/brieftools.py`.
Outputs: pytest assertions.
Side effects: files, links, modes restored at the end, and ledger lines under `tmp_path`
only; the `os` that `kgme.brief_io` and `kgme.clean_fs` see is patched for two tests.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest
from briefreviewtools import closing, plant_intent
from brieftools import BRIEF, DATE, SETTINGS, note, read_recorded, run_brief, write_seed
from cleantools import OsWith

from kgme import brief_io, clean_fs, ledger

# F1


@pytest.mark.blocking
def test_a_brief_that_is_a_link_is_refused_and_its_target_untouched(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    outside = base / "docs" / "secret.md"
    outside.parent.mkdir()
    outside.write_text(note("note", "SECRET", "active", "# Secret", author="human"))
    before = outside.read_bytes()
    (base / BRIEF).symlink_to(outside)
    assert run_brief(base) == 1
    assert outside.read_bytes() == before and (base / BRIEF).is_symlink()
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["status"] == "refused" and outcome["class"] == "blocking"
    assert "symlink" in outcome["summary"]


@pytest.mark.blocking
def test_a_linked_payload_directory_refuses_the_write(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "docs").mkdir()
    (base / "logs" / "scratch").mkdir(parents=True, exist_ok=True)
    (base / "logs" / "scratch" / "payloads").symlink_to(base / "docs")
    assert run_brief(base) == 1
    assert list((base / "docs").iterdir()) == []
    assert not (base / BRIEF).exists()
    assert read_recorded(base, "outcome")[-1]["class"] == "blocking"


@pytest.mark.blocking
def test_a_recovery_payload_that_is_a_link_is_not_read(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / read_recorded(base, "intent")[-1]["payload_ref"]).read_text()
    intent = plant_intent(base, DATE, text, hashlib.sha256(text.encode()).hexdigest())
    planted = base / intent["payload_ref"]
    outside = tmp_path / "outside.json"
    outside.write_text(text)
    planted.unlink()
    planted.symlink_to(outside)
    assert run_brief(base) == 1
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"
    assert "symlink" in closed[0]["summary"]


# F2


@pytest.mark.blocking
def test_an_altered_payload_closes_its_intent_blocking(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / read_recorded(base, "intent")[-1]["payload_ref"]).read_text()
    altered = json.loads(text)
    altered["sha256"] = "f" * 64
    intent = plant_intent(
        base, DATE, json.dumps(altered), hashlib.sha256(text.encode()).hexdigest()
    )
    assert run_brief(base) == 1
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"
    assert "hash" in closed[0]["summary"]


@pytest.mark.blocking
def test_a_payload_naming_another_destination_closes_its_intent_blocking(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    record = json.loads((base / read_recorded(base, "intent")[-1]["payload_ref"]).read_text())
    record["destination"] = "docs/elsewhere.md"
    text = json.dumps(record)
    intent = plant_intent(base, DATE, text, hashlib.sha256(text.encode()).hexdigest())
    assert run_brief(base) == 1
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"
    assert "destination" in closed[0]["summary"]


@pytest.mark.blocking
def test_a_malformed_payload_closes_its_intent_blocking(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    text = "not json"
    intent = plant_intent(base, DATE, text, hashlib.sha256(text.encode()).hexdigest())
    assert run_brief(base) == 1
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"


# F3


@pytest.mark.blocking
def test_a_dry_run_leaves_an_open_intent_open_and_appends_one_note(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent = plant_intent(base, "2026-10-01", None, None)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    before = len(ledger.read(dirs))
    assert run_brief(base, "--dry-run") == 0
    after = ledger.read(dirs)
    assert len(after) == before + 1 and after[-1]["kind"] == "note"
    assert closing(base, intent) == []


# F4


@pytest.mark.blocking
def test_an_intent_that_never_wrote_does_not_move_the_friction_cutoff(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "memory" / "agent" / "brief" / "2026-10-07.md").unlink()
    plant_intent(base, "2026-10-07", None, None)
    assert run_brief(base) == 0
    text = (base / BRIEF).read_text()
    assert "before the previous brief" in text, "no brief was written on 2026-10-07"


# F5


@pytest.mark.blocking
def test_a_short_write_never_leaves_a_torn_brief(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    real_write = os.write

    def seven_bytes(fd: int, data) -> int:
        return real_write(fd, bytes(data[:7]))

    monkeypatch.setattr(brief_io, "os", OsWith(write=seven_bytes))
    monkeypatch.setattr(clean_fs, "os", OsWith(write=seven_bytes))
    assert run_brief(base) == 0
    monkeypatch.undo()
    written = (base / BRIEF).read_bytes()
    recorded = read_recorded(base, "outcome")[-1]["summary"]
    assert hashlib.sha256(written).hexdigest()[:16] in recorded
    assert written.endswith(b"\n") and b"## Inputs" in written


# F6


@pytest.mark.blocking
def test_an_unreadable_input_is_a_classified_refusal(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dark = base / "memory" / "notes" / "plain.md"
    dark.chmod(0o000)
    try:
        assert run_brief(base) == 1
    finally:
        dark.chmod(0o644)
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["status"] == "refused" and outcome["class"] == "blocking"
    assert "plain.md" in outcome["summary"]


@pytest.mark.blocking
def test_a_brief_without_its_identity_is_a_classified_refusal(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / BRIEF).write_text("---\nid: X\ntype: note\n---\n\n# Brief\n")
    assert run_brief(base) == 1
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["status"] == "refused" and outcome["class"] == "blocking"


@pytest.mark.blocking
def test_a_failed_replacement_closes_its_intent_as_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)

    def no_replace(*args, **kwargs) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(brief_io, "os", OsWith(replace=no_replace))
    assert run_brief(base) == 1
    monkeypatch.undo()
    dirs = ledger.read_base_dirs(SETTINGS, base)
    assert ledger.open_intents("brief", dirs) == []
    outcome = read_recorded(base, "outcome")[-1]
    assert outcome["status"] == "error" and outcome["class"] == "blocking"
    assert not (base / BRIEF).exists()
    assert not any(p.name.startswith(".") for p in (base / BRIEF).parent.iterdir())
