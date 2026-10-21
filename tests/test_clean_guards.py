"""Tests for the guarantees `kgme clean` gained under review of HANDOFF-0033 (AUDIT-0043).

Purpose: a root reached through a symlink in any component is refused and the link's target
untouched, and an entry whose path gained a link, or was replaced, between the plan and its
deletion is refused there and the run stops (F1); a plan is written ahead as a payload, and
an interrupted run is reconciled against it, whether the interruption fell after a recorded
outcome or between an unlink and its outcome (F2); the first failed deletion stops the run
and later paths stay (F3); a directory the listing cannot read refuses the plan (F4); a
refused dry run records blocking outcomes (F5, in `tests/test_clean.py`); a path too long for
the summary keeps its size, hash, and number (F6).
Inputs: the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files, one unreadable directory restored at the end, and ledger lines under
`tmp_path` only.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest
from cleantools import SETTINGS, read_recorded, run_clean, write_seed

from kgme import clean, clean_fs, clean_io, clean_read, events, ledger, paths


@pytest.mark.blocking
def test_a_root_below_a_symlink_is_refused_and_the_link_target_untouched(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "docs" / "brief").mkdir()
    (base / "docs" / "brief" / "human.md").write_text("human\n")
    real = base / "memory" / "agent"
    real.rename(base / "memory" / "agent.real")
    os.symlink(base / "docs", real)
    assert run_clean(base, "briefs", "--yes") == 1
    assert (base / "docs" / "brief" / "human.md").exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert "memory/agent" in outcomes[0]["summary"] and "symlink" in outcomes[0]["summary"]


@pytest.mark.blocking
def test_an_entry_changed_after_the_plan_is_refused_and_the_run_stops(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    entries, allowed, errors = clean_read.read_candidates(base, ["memory/agent"])
    plan = clean.plan_clean("agent", entries, base, allowed, base / "logs" / "ledger", {})
    assert errors == [] and [e.path.name for e in plan.files] == ["2026-10-01.md", "note.md"]
    digests, problem = clean_io.read_prepared(plan, base)
    assert problem == ""
    (base / "docs" / "2026-10-01.md").write_text("human\n")
    (base / "memory" / "agent" / "brief").rename(base / "memory" / "agent" / "brief.real")
    os.symlink(base / "docs", base / "memory" / "agent" / "brief")
    intent_id = events.new_ulid()
    result = clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", intent_id, digests
    )
    assert (base / "docs" / "2026-10-01.md").exists()
    assert (base / "memory" / "agent" / "note.md").exists(), "later paths untouched"
    assert result.deleted_files == 0 and result.refused == 1
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused"
    assert "a component of its path is a symlink" in outcomes[0]["summary"]
    assert outcomes[-1]["summary"].startswith("closed: stopped at #1; 2 planned paths left")
    assert outcomes[-1]["class"] == "blocking"


def plant_interrupted_run(base: Path, deleted: list[str], recorded: list[int]) -> dict:
    """The state a kill leaves: a payload for the `agent` plan, its intent, the files in
    `deleted` gone from disk, and an `ok` outcome for each number in `recorded`."""
    dirs = ledger.read_base_dirs(SETTINGS, base)
    entries, allowed, _ = clean_read.read_candidates(base, ["memory/agent"])
    plan = clean.plan_clean("agent", entries, base, allowed, base / "logs" / "ledger", {})
    key = "clean:agent:2026-10-09T23:00"
    digests, _ = clean_io.read_prepared(plan, base)
    record = clean.plan_record(plan, base, key, digests)
    payloads = paths.payloads_dir(SETTINGS, base)
    text = json.dumps(record) + "\n"
    clean_fs.write_payload(base, payloads / "planted.json", text)
    intent = events.make_event(
        source="kgme",
        actor="kgme.clean",
        kind="intent",
        job="clean",
        key=key,
        summary="clean agent delete: 2 files 11 B, 1 dirs, 0 refused",
        payload_ref="logs/scratch/payloads/planted.json",
        payload_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
    ledger.append(intent, dirs)
    for rel in deleted:
        (base / rel).unlink()
    for number in recorded:
        item = record["files"][number - 1]
        summary = f"deleted #{number} {item['size']} B sha256 {item['sha256']} {item['path']}"
        clean_io.write_outcome(dirs, events.new_ulid(), key, intent["id"], summary, "ok")
    return intent


@pytest.mark.blocking
def test_interruption_after_a_recorded_outcome_is_reconciled_from_the_payload(
    tmp_path: Path,
) -> None:
    base = write_seed(tmp_path)
    intent = plant_interrupted_run(base, ["memory/agent/brief/2026-10-01.md"], [1])
    assert run_clean(base, "agent") == 0
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert len(closing) == 2
    assert closing[-1]["summary"] == (
        "closed: reconciled on start: 0 deleted without an outcome, 2 planned and still present"
    )
    assert closing[-1]["class"] == "transient"
    assert (base / "memory" / "agent" / "note.md").exists(), "reconciliation deletes nothing"


@pytest.mark.blocking
def test_interruption_between_unlink_and_outcome_is_reconciled_from_the_payload(
    tmp_path: Path,
) -> None:
    base = write_seed(tmp_path)
    intent = plant_interrupted_run(
        base, ["memory/agent/brief/2026-10-01.md", "memory/agent/note.md"], [1]
    )
    assert run_clean(base, "agent") == 0
    closing = [e for e in read_recorded(base, "outcome") if e["ref"] == intent["id"]]
    assert [c["summary"].split(" ")[0] for c in closing] == ["deleted", "reconciled", "closed:"]
    assert "absent, deleted before its outcome was written" in closing[1]["summary"]
    assert closing[-1]["summary"].endswith(
        "1 deleted without an outcome, 1 planned and still present"
    )


@pytest.mark.blocking
def test_the_first_failed_deletion_stops_the_run_and_later_paths_stay(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    locked = base / "memory" / "agent" / "brief"
    locked.chmod(0o500)
    try:
        assert run_clean(base, "agent", "--yes") == 1
        assert (base / "memory" / "agent" / "brief" / "2026-10-01.md").exists()
        assert (base / "memory" / "agent" / "note.md").exists(), "later paths untouched"
    finally:
        locked.chmod(0o755)
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "error" and outcomes[0]["class"] == "blocking"
    assert outcomes[0]["summary"].startswith("error #1: could not delete")
    assert outcomes[-1]["summary"].startswith("closed: stopped at #1; 2 planned paths left")


@pytest.mark.blocking
def test_an_unreadable_directory_refuses_the_plan(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dark = base / "memory" / "agent" / "dark"
    dark.mkdir()
    (dark / "x.md").write_text("x\n")
    dark.chmod(0o000)
    try:
        assert run_clean(base, "agent", "--yes") == 1
        assert (base / "memory" / "agent" / "note.md").exists()
    finally:
        dark.chmod(0o755)
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert (
        "could not list" in outcomes[0]["summary"] and "memory/agent/dark" in outcomes[0]["summary"]
    )


@pytest.mark.blocking
def test_a_long_path_keeps_its_size_hash_and_number_in_the_outcome(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    # every segment under 40 characters, so the ledger's secret-shape redaction leaves it alone
    deep = base / "memory" / "agent"
    for level in range(1, 7):
        deep = deep / f"a-long-directory-name-of-words-{level}"
    deep.mkdir(parents=True)
    name = "a-note-with-a-long-path.md"
    (deep / name).write_text("long\n")
    assert run_clean(base, "agent", "--yes") == 0
    outcomes = read_recorded(base, "outcome")
    long = [o for o in outcomes if "…" in o["summary"] and o["summary"].startswith("deleted #")]
    assert len(long) == 1 and len(long[0]["summary"]) <= 200
    assert long[0]["summary"].startswith("deleted #") and " 5 B sha256 " in long[0]["summary"]
    assert long[0]["summary"].endswith(name)
    intents = read_recorded(base, "intent")
    record = json.loads((base / intents[0]["payload_ref"]).read_text())
    number = int(long[0]["summary"].split("#")[1].split(" ")[0])
    assert record["files"][number - 1]["path"].endswith(name)
    assert len(record["files"][number - 1]["path"]) > 200
