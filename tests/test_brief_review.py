"""Tests for what review cycle 1 of HANDOFF-0034 (AUDIT-0051) asked of `kgme brief`.

Purpose: one test or more per blocking finding, each written and run red before its fix
(the review-loop reader's rule of 2026-10-14). A brief, payload, or payload directory that
is a link refuses the run and nothing outside `memory/agent/brief/` and scratch is read or
written (F1); a payload that is not the evidence its intent recorded, or names another
destination, is closed `blocking` (F2); a dry run leaves an open intent open and appends
exactly one note (F3); an intent that never wrote does not move the friction cutoff (F4);
a short write never leaves a torn brief (F5); read, identity, and replacement failures are
classified outcomes (F6); a date that is not a real `YYYY-MM-DD` exits 2 before anything
(F7); an input's hash is its bytes, and invalid UTF-8 is refused (F8); due instants sort and
group by time in the configured zone (F9).
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
from brieftools import BRIEF, DATE, SETTINGS, note, read_recorded, run_brief, write_seed
from cleantools import OsWith

from kgme import brief, brief_io, clean_fs, events, ledger


def plant_intent(base: Path, date: str, payload_text: str | None, sha: str | None) -> dict:
    """An intent a killed run left: its payload (if any) and the sha256 it recorded."""
    dirs = ledger.read_base_dirs(SETTINGS, base)
    ref = None
    if payload_text is not None:
        target = base / "logs" / "scratch" / "payloads" / f"planted-{date}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload_text)
        ref = target.relative_to(base).as_posix()
    identity = brief.Identity(
        "01K0000000000000000000PLNT", f"{date}T07:00:00-07:00", f"{date}T07:00:00-07:00"
    )
    intent = events.make_event(
        source="kgme",
        actor="kgme.brief",
        kind="intent",
        job="brief",
        key=f"brief:{date}",
        summary=brief.identity_summary(identity, "0" * 16, date),
        payload_ref=ref,
        payload_sha256=sha,
    )
    ledger.append(intent, dirs)
    return intent


def closing(base: Path, intent: dict) -> list[dict]:
    dirs = ledger.read_base_dirs(SETTINGS, base)
    return [e for e in ledger.read(dirs) if e["ref"] == intent["id"]]


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


# Cycle 3: Cowork's ruling on F1 and F6 (one gated reader; one failure boundary)

BRIEF_MODULES = ("brief.py", "brief_read.py", "brief_io.py", "brief_reconcile.py")
READ_CALLS = {"read_text", "read_bytes", "read_regular_bytes", "load", "loads_file"}


@pytest.mark.blocking
def test_no_brief_module_reads_a_file_except_through_the_gate() -> None:
    """Every file read in the brief job is `brief_read.read_gated`, or the ledger's own
    readers; a call that opens or reads a path anywhere else fails this test."""
    import ast

    kgme_dir = Path(brief.__file__).parent
    stray: list[str] = []
    for name in BRIEF_MODULES:
        tree = ast.parse((kgme_dir / name).read_text())
        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            if func.name == "read_gated" or func.name.startswith("write_"):
                continue
            for call in [n for n in ast.walk(func) if isinstance(n, ast.Call)]:
                target = call.func
                called = (
                    target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
                )
                owner = getattr(target.value, "id", "") if isinstance(target, ast.Attribute) else ""
                if called in READ_CALLS or called == "open" or (owner == "os" and called == "read"):
                    where = f"{owner}.{called}" if owner else called
                    stray.append(f"{name}:{call.lineno} {func.name} calls {where}")
    assert stray == [], "\n".join(stray)


@pytest.mark.blocking
def test_a_pending_intent_whose_destination_is_now_forbidden_reads_no_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / read_recorded(base, "intent")[-1]["payload_ref"]).read_text()
    intent = plant_intent(base, DATE, text, hashlib.sha256(text.encode()).hexdigest())
    settings = json.loads(json.dumps(SETTINGS))
    settings["hooks"]["blocklist"] = [*settings["hooks"]["blocklist"], f"**/{DATE}.md"]
    opened: list[Path] = []
    real = clean_fs.read_regular_bytes

    def spy(root: Path, path: Path) -> bytes:
        opened.append(path)
        return real(root, path)

    monkeypatch.setattr(clean_fs, "read_regular_bytes", spy)
    assert brief_io.run_brief(DATE, False, base, settings) == 1
    assert base / BRIEF not in opened, "no byte of a forbidden destination is read"
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"


@pytest.mark.blocking
@pytest.mark.parametrize(
    "damaged", ["# Brief 2026-10-08\n\nno frontmatter\n", "---\nid: [unclosed\n---\n\n# Brief\n"]
)
def test_a_damaged_brief_is_one_intent_and_one_classified_outcome(
    tmp_path: Path, damaged: str
) -> None:
    base = write_seed(tmp_path)
    (base / BRIEF).write_text(damaged)
    assert run_brief(base) == 1
    assert (base / BRIEF).read_text() == damaged, "the existing brief is preserved"
    recorded = read_recorded(base)
    intents = [e for e in recorded if e["kind"] == "intent"]
    outcomes = [e for e in recorded if e["kind"] == "outcome"]
    assert len(intents) == 1 and len(outcomes) == 1
    assert outcomes[0]["ref"] == intents[0]["id"] and outcomes[0]["class"] == "blocking"
