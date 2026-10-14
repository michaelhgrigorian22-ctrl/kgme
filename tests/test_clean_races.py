"""Tests for the deletion step of `kgme clean`, rebuilt on Michou's override of 2026-10-13.

Purpose: an entry swapped for a link or for another entry at the last instant before its
final check is refused there and left as found, and the run stops (HANDOFF-0033 review F1;
the check is one `lstat` and one `realpath` against the plan, no hold, no restore); a file
whose size or modification time changed after the plan is refused by the final check
(F2, within the accepted residual risk the module docstring of `kgme/clean_fs.py` states); a
refusal before any deletion at a path that grows under redaction still fits the ledger, no
outcome can exceed it, and a summary longer raw than redacted fits both ways (F6). The
run's bounds are in `tests/test_clean_bounds.py`.
Inputs: the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files, directories, and ledger lines under `tmp_path` only;
`clean_fs.read_final_check` is wrapped for the duration of one test each.
"""

import os
from pathlib import Path

import pytest
from cleantools import (
    SETTINGS,
    plan_agent,
    read_recorded,
    run_clean,
    write_seed,
)

from kgme import clean, clean_fs, clean_io, events, ledger

BRIEF = "memory/agent/brief/2026-10-01.md"


def run_agent_deletions(base: Path) -> clean_io.CleanResult:
    """The `agent` plan prepared and deleted as `run_clean --yes` would, without the CLI."""
    dirs = ledger.read_base_dirs(SETTINGS, base)
    plan = plan_agent(base)
    digests, problem = clean_io.read_prepared(plan, base)
    assert problem == ""
    return clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", events.new_ulid(), digests
    )


def swap_before_final_check(monkeypatch: pytest.MonkeyPatch, path: Path, swap) -> None:
    """`swap()` runs at the last instant before the final check of `path`: the interval
    after every earlier check and before the one that decides."""
    original = clean_fs.read_final_check
    done = False

    def check_after_swap(checked: Path, entry: clean.Entry) -> None:
        nonlocal done
        if checked == path and not done:
            done = True
            swap()
        original(checked, entry)

    monkeypatch.setattr(clean_fs, "read_final_check", check_after_swap)


@pytest.mark.blocking
def test_a_link_swapped_in_at_the_last_instant_is_refused_and_left(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    target = base / BRIEF

    def swap() -> None:
        target.rename(target.with_suffix(".real"))
        os.symlink(base / "docs" / "keep.md", target)

    swap_before_final_check(monkeypatch, target, swap)
    result = run_agent_deletions(base)
    assert result.deleted_files == 0 and result.refused == 1
    assert (base / "docs" / "keep.md").read_text() == "human\n"
    assert target.is_symlink(), "the planted link is left, not deleted"
    assert target.with_suffix(".real").read_text() == "brief\n"
    assert (base / "memory" / "agent" / "note.md").exists()
    outcome = read_recorded(base, "outcome")[0]
    assert outcome["status"] == "refused"
    assert outcome["summary"] == f"refused #1: is a symlink: {BRIEF}"


@pytest.mark.blocking
def test_another_file_swapped_in_at_the_last_instant_is_refused_and_left(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    target = base / BRIEF

    def swap() -> None:
        target.unlink()
        target.write_text("another\n")

    swap_before_final_check(monkeypatch, target, swap)
    result = run_agent_deletions(base)
    assert result.deleted_files == 0 and result.refused == 1
    assert target.read_text() == "another\n"
    assert [p.name for p in target.parent.iterdir()] == [target.name]
    assert "replaced since the plan" in read_recorded(base, "outcome")[0]["summary"]


@pytest.mark.blocking
def test_a_directory_swapped_for_a_link_at_the_last_instant_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    brief = base / "memory" / "agent" / "brief"

    def swap() -> None:
        brief.rename(brief.with_name("brief.real"))
        os.symlink(base / "docs", brief)

    swap_before_final_check(monkeypatch, brief, swap)
    result = run_agent_deletions(base)
    assert result.deleted_files == 2 and result.removed_dirs == 0 and result.refused == 1
    assert (base / "docs" / "keep.md").exists() and brief.is_symlink()
    assert brief.with_name("brief.real").is_dir()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[2]["status"] == "refused"
    assert outcomes[2]["summary"] == "refused #3: is a symlink: memory/agent/brief"


@pytest.mark.blocking
def test_a_file_rewritten_in_place_after_the_plan_is_refused_by_its_mtime(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    plan = plan_agent(base)
    digests, _ = clean_io.read_prepared(plan, base)
    target = base / BRIEF
    before = os.stat(target)
    with target.open("r+") as handle:
        handle.write("BRIEF\n")
    os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000))
    after = os.stat(target)
    assert (after.st_ino, after.st_size) == (before.st_ino, before.st_size), "same inode, size"
    record = clean.plan_record(plan, base, "clean:agent:t", digests)
    assert record["files"][0]["sha256"] == digests[target], "the payload keeps the planned hash"
    result = clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", events.new_ulid(), digests
    )
    assert result.deleted_files == 0 and result.refused == 1
    assert target.read_text() == "BRIEF\n" and (base / "memory" / "agent" / "note.md").exists()
    outcome = read_recorded(base, "outcome")[0]
    assert outcome["status"] == "refused" and "changed since the plan" in outcome["summary"]


@pytest.mark.blocking
def test_a_file_that_grew_after_the_plan_is_refused_and_the_run_stops(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    plan = plan_agent(base)
    digests, _ = clean_io.read_prepared(plan, base)
    target = base / BRIEF
    with target.open("a") as handle:
        handle.write("more\n")
    result = clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", events.new_ulid(), digests
    )
    assert result.deleted_files == 0 and result.refused == 1
    assert target.read_text() == "brief\nmore\n"
    assert (base / "memory" / "agent" / "note.md").exists(), "later paths untouched"
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["summary"] == f"refused #1: changed since the plan was made: {BRIEF}"
    assert outcomes[-1]["summary"].startswith("closed: stopped at #1; 2 planned paths left")


@pytest.mark.blocking
def test_a_refusal_before_any_deletion_at_a_growing_path_still_fits(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    deep = base / "memory" / "agent"
    for level in range(1, 5):
        deep = deep / f"a-long-directory-name-words-{level}"
    deep.mkdir(parents=True)
    unreadable = deep / "key=x.md"
    unreadable.write_text("dark\n")
    unreadable.chmod(0o000)
    rel = clean.shown(unreadable, base)
    raw = f"{clean_io.BEFORE}#1 Permission denied: {rel}"
    assert len(raw) <= 200 < len(events.redact(raw)), "the fixture must grow past the cap"
    try:
        assert run_clean(base, "agent", "--yes") == 1
    finally:
        unreadable.chmod(0o644)
    assert unreadable.exists() and (base / BRIEF).exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and outcomes[0]["class"] == "blocking"
    assert outcomes[0]["summary"].startswith(clean_io.BEFORE + "#1 ")
    assert "Permission denied" in outcomes[0]["summary"]
    assert "<redacted:" in outcomes[0]["summary"] and len(outcomes[0]["summary"]) <= 200
    assert outcomes[-1]["summary"].startswith("closed: refused, nothing deleted")


@pytest.mark.blocking
def test_no_outcome_summary_can_exceed_the_ledger_cap(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    intent_id = events.new_ulid()
    summary = "error #1: could not delete: " + "words " * 25 + "key=" + "y" * 50
    assert len(summary) > 200
    clean_io.write_outcome(
        dirs, events.new_ulid(), "clean:agent:t", intent_id, summary, "error", "blocking"
    )
    recorded = read_recorded(base, "outcome")[0]["summary"]
    assert len(recorded) <= 200 and recorded.startswith("error #1: could not delete: words ")


@pytest.mark.blocking
def test_a_refusal_longer_raw_than_redacted_fits_both_ways(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    name = "words " * 24 + "key=x " + "z" * 40
    target = base / "memory" / "agent" / name
    target.write_text("a\n")
    plan = plan_agent(base)
    digests, _ = clean_io.read_prepared(plan, base)
    with target.open("r+") as handle:
        handle.write("b\n")
    result = clean_io.run_deletions(
        plan, base, dirs, events.new_ulid(), "clean:agent:t", events.new_ulid(), digests
    )
    assert result.deleted_files == 2 and result.refused == 1
    refusal = [o for o in read_recorded(base, "outcome") if o["status"] == "refused"][0]
    assert "changed since the plan" in refusal["summary"]
    assert len(refusal["summary"]) <= 200 >= len(events.redact(refusal["summary"]))
    assert target.read_text() == "b\n"
