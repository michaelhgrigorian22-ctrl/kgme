"""Tests for the guarantees `kgme clean` gained in review cycle 2 of HANDOFF-0033 (AUDIT-0044).

Purpose: a link planted in a component of a planned path before its deletion is refused
there, because the final check asks that the path still resolve where the plan resolved it
(F1, rebuilt on Michou's override of 2026-10-13); a reconciled deletion carries the size and
hash the payload kept, and a reconciliation interrupted before its close is not repeated
(F2); a directory whose names can be listed but whose children cannot be stat'ed, and a root
that cannot be read, refuse the plan (F4); a summary that grows under the ledger's redaction
still fits, measured before anything is deleted (F6); a payload directory that is a link
refuses the run before any deletion (F8).
Inputs: the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files, directories with their modes restored at the end, and ledger lines
under `tmp_path` only.
"""

import os
from pathlib import Path

import pytest
from cleantools import (
    SETTINGS,
    plan_agent,
    plant_interrupted_run,
    read_recorded,
    run_clean,
    write_seed,
)

from kgme import clean, clean_fs, clean_io, events, ledger


@pytest.mark.blocking
def test_a_link_planted_after_the_last_check_cannot_redirect_the_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    plan = plan_agent(base)
    digests, problem = clean_io.read_prepared(plan, base)
    assert problem == ""
    (base / "docs" / "2026-10-01.md").write_text("human\n")
    original = clean_fs.read_final_check

    def swap_then_check(path: Path, entry: clean.Entry) -> None:
        brief = base / "memory" / "agent" / "brief"
        if not brief.is_symlink():
            brief.rename(base / "memory" / "agent" / "brief.real")
            os.symlink(base / "docs", brief)
        original(path, entry)

    monkeypatch.setattr(clean_fs, "read_final_check", swap_then_check)
    intent_id = events.new_ulid()
    result = clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", intent_id, digests
    )
    assert (base / "docs" / "2026-10-01.md").exists()
    assert (base / "memory" / "agent" / "brief.real" / "2026-10-01.md").exists()
    assert (base / "memory" / "agent" / "note.md").exists()
    assert result.deleted_files == 0 and result.refused == 1
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused"
    assert "a component of its path is a symlink" in outcomes[0]["summary"]
    assert outcomes[-1]["summary"].startswith("closed: stopped at #1; 2 planned paths left")


@pytest.mark.blocking
def test_a_file_replaced_after_the_last_check_is_refused_by_its_inode(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    plan = plan_agent(base)
    first = plan.files[0]
    first.path.unlink()
    first.path.write_text("another file under the same name\n")
    with pytest.raises(clean_fs.Refused, match="replaced since the plan"):
        clean_fs.run_unlink(first.path, first)
    assert first.path.read_text() == "another file under the same name\n", "left, not deleted"
    assert [p.name for p in first.path.parent.iterdir()] == [first.path.name]


@pytest.mark.blocking
def test_a_reconciled_deletion_carries_the_payloads_size_and_hash(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent, record = plant_interrupted_run(
        base, ["memory/agent/brief/2026-10-01.md", "memory/agent/note.md"], [1]
    )
    assert run_clean(base, "agent") == 0
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    item = record["files"][1]
    assert closing[1]["summary"] == (
        f"reconciled #2: absent, deleted before its outcome was written; "
        f"{item['size']} B sha256 {item['sha256']} {item['path']}"
    )
    assert len(item["sha256"]) == 16 and closing[1]["status"] == "ok"


@pytest.mark.blocking
def test_a_reconciliation_interrupted_before_its_close_is_not_repeated(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    intent, record = plant_interrupted_run(
        base, ["memory/agent/brief/2026-10-01.md", "memory/agent/note.md"], [1]
    )
    dirs = ledger.read_base_dirs(SETTINGS, base)
    item = record["files"][1]
    summary = (
        f"reconciled #2: absent, deleted before its outcome was written; "
        f"{item['size']} B sha256 {item['sha256']} {item['path']}"
    )
    clean_io.write_outcome(dirs, events.new_ulid(), intent["key"], intent["id"], summary, "ok")
    assert run_clean(base, "agent") == 0
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert [c["summary"].split(" ")[0] for c in closing] == ["deleted", "reconciled", "closed:"]
    assert closing[-1]["summary"].endswith(
        "0 deleted without an outcome, 1 planned and still present"
    )


@pytest.mark.blocking
def test_a_directory_whose_children_cannot_be_stat_refuses_the_plan(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dim = base / "memory" / "agent" / "dim"
    dim.mkdir()
    (dim / "x.md").write_text("x\n")
    dim.chmod(0o400)
    try:
        assert run_clean(base, "agent", "--yes") == 1
        assert (base / "memory" / "agent" / "note.md").exists()
    finally:
        dim.chmod(0o755)
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert "could not list" in outcomes[0]["summary"] and "dim/x.md" in outcomes[0]["summary"]


@pytest.mark.blocking
def test_an_unreadable_root_refuses_the_plan(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    root = base / "memory" / "agent"
    root.chmod(0o000)
    try:
        assert run_clean(base, "agent", "--yes") == 1
    finally:
        root.chmod(0o755)
    assert (root / "note.md").exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and "could not list" in outcomes[0]["summary"]


@pytest.mark.blocking
def test_a_summary_that_grows_under_redaction_still_fits(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    deep = base / "memory" / "agent"
    for level in range(1, 5):
        deep = deep / f"a-long-directory-name-of-words-{level}"
    deep.mkdir(parents=True)
    name = "key=x.md"
    (deep / name).write_text("grows\n")
    rel = clean.shown(deep / name, base)
    plain = f"deleted #1 6 B sha256 {'0' * 16} {rel}"
    assert len(plain) <= 200 < len(events.redact(plain)), "the fixture must grow past the cap"
    assert run_clean(base, "agent", "--yes") == 0
    grown = [o for o in read_recorded(base, "outcome") if "<redacted:" in o["summary"]]
    assert len(grown) == 1 and len(grown[0]["summary"]) <= 200
    assert grown[0]["summary"].startswith("deleted #") and " 6 B sha256 " in grown[0]["summary"]
    assert not (deep / name).exists()


@pytest.mark.blocking
def test_a_linked_payload_directory_refuses_the_run_before_any_deletion(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    payloads = base / "logs" / "scratch" / "payloads"
    for child in payloads.iterdir():
        child.unlink()
    payloads.rmdir()
    os.symlink(base / "docs", payloads)
    assert run_clean(base, "agent", "--yes") == 1
    assert (base / "memory" / "agent" / "note.md").exists()
    assert sorted(p.name for p in (base / "docs").iterdir()) == ["keep.md"]
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert "payload directory" in outcomes[0]["summary"] and "symlink" in outcomes[0]["summary"]
    assert outcomes[-1]["summary"].startswith("closed: refused, nothing deleted")
