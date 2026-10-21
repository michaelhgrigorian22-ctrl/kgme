"""Tests for `kgme clean` (HANDOFF-0033 acceptance and the four ADR-015 job tests).

Purpose: on a seeded temporary checkout, a dry run lists exactly the seeded files and deletes
none; `--yes` deletes them with one outcome per path and one close; a symlink planted under a
target is refused with a blocking outcome and its target is untouched, under `--yes` and
under the default dry run alike; an unknown target exits 2 with the list; `ledger` is not a
target; the ledger directory, `.git` parts, and paths resolving outside their root are
refused in the plan; the manifest's blocklist refuses a dotenv file; globs never enter
`.venv`; a second run is a no-op; an intent without a payload is reconciled on start. The
guarantees the review added are in `tests/test_clean_guards.py`.
Inputs: `kgme.toml`, `jobs/clean/manifest.toml`, the seeded tree of `tests/cleantools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only.
"""

import os
from pathlib import Path

import pytest
from cleantools import DOTENV, SETTINGS, entry, read_recorded, run_clean, write_seed

from kgme import clean, cli, events, ledger


@pytest.mark.blocking
def test_dry_run_lists_exactly_the_seeded_files_and_deletes_none(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "agent") == 0
    out = capsys.readouterr().out
    assert "memory/agent/brief/2026-10-01.md" in out and "memory/agent/note.md" in out
    assert "docs/keep.md" not in out
    assert out.count(" B  ") == 2
    assert (base / "memory/agent/note.md").exists()
    assert (base / "memory/agent/brief/2026-10-01.md").exists()
    assert len(read_recorded(base, "note")) == 1 and read_recorded(base, "intent") == []
    assert run_clean(base, "agent", "--dry-run") == 0


@pytest.mark.blocking
def test_yes_deletes_files_then_directories_with_one_outcome_per_path(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "agent", "--yes") == 0
    assert not (base / "memory/agent/note.md").exists()
    assert not (base / "memory/agent/brief").exists()
    assert (base / "memory/agent").is_dir()
    assert (base / "docs/keep.md").exists()
    intents = read_recorded(base, "intent")
    outcomes = read_recorded(base, "outcome")
    assert len(intents) == 1 and intents[0]["key"].startswith("clean:agent:")
    assert [o["status"] for o in outcomes] == ["ok", "ok", "ok", "ok"]
    assert all(o["ref"] == intents[0]["id"] for o in outcomes)
    deleted = [o["summary"] for o in outcomes if o["summary"].startswith("deleted ")]
    assert len(deleted) == 2 and all(" B sha256 " in s for s in deleted)
    assert outcomes[-2]["summary"] == "removed #3 memory/agent/brief/"
    assert outcomes[-1]["summary"] == "closed: deleted 2 files 11 B, removed 1 dirs"
    assert intents[0]["payload_ref"].startswith("logs/scratch/payloads/clean-agent-")
    assert (base / intents[0]["payload_ref"]).exists()


@pytest.mark.blocking
def test_symlink_under_a_target_is_refused_and_its_target_untouched(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    base = write_seed(tmp_path)
    os.symlink(base / "docs", base / "memory" / "agent" / "x")
    for flags in (("--yes",), ()):
        assert run_clean(base, "agent", *flags) == 1
        assert (base / "docs" / "keep.md").exists()
        assert (base / "memory" / "agent" / "x").is_symlink()
        assert (base / "memory" / "agent" / "note.md").exists(), "a refused plan deletes nothing"
        assert "REFUSED" in capsys.readouterr().out
    outcomes = read_recorded(base, "outcome")
    assert [o["status"] for o in outcomes] == ["refused"] * 4
    assert all(o["class"] == "blocking" for o in outcomes)
    assert "memory/agent/x" in outcomes[0]["summary"] and "symlink" in outcomes[0]["summary"]
    assert outcomes[1]["summary"].startswith("closed: refused, nothing deleted")
    assert read_recorded(base, "note") == [] and len(read_recorded(base, "intent")) == 2


@pytest.mark.blocking
def test_a_root_that_is_itself_a_symlink_is_refused(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "logs" / "trace").symlink_to(base / "docs")
    assert run_clean(base, "trace", "--yes") == 1
    assert (base / "docs" / "keep.md").exists()


@pytest.mark.blocking
def test_unknown_targets_exit_2_with_the_list(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "docs/") == 2
    assert run_clean(base, "ledger") == 2
    assert run_clean(base, "memory/agent") == 2
    err = capsys.readouterr().err
    assert "briefs" in err and "ledger-test" in err
    assert cli.main(["clean"]) == 2
    assert run_clean(base, "agent", "--yes", "--dry-run") == 2
    assert read_recorded(base) == []


@pytest.mark.blocking
def test_plan_refuses_the_ledger_git_parts_and_paths_outside_their_root(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    ledger_dir = base / "logs" / "ledger"
    root = base / "logs" / "scratch"
    outside = tmp_path / "elsewhere.txt"
    outside.write_text("x\n")
    entries = [
        entry(ledger_dir / "2026-10.jsonl", base),
        entry(base / ".git" / "objects" / "ab", base),
        entry(outside, base),
        entry(base / "docs" / "keep.md", base),
        entry(base / "logs" / "scratch" / "review.patch", base),
        entry(base / "logs" / "scratch" / "payloads", base, is_dir=True),
        entry(base / "logs" / "scratch" / "payloads" / "a.json", base),
    ]
    plan = clean.plan_clean("scratch", entries, base, [root], ledger_dir, {})
    reasons = {clean.shown(r.entry.path, base): r.reason for r in plan.refused}
    assert "never a target" in reasons["logs/ledger/2026-10.jsonl"]
    assert ".git" in reasons[".git/objects/ab"]
    assert "outside the repository" in reasons[str(outside)]
    assert "outside the target's roots" in reasons["docs/keep.md"]
    assert [clean.shown(e.path, base) for e in plan.files] == [
        "logs/scratch/payloads/a.json",
        "logs/scratch/review.patch",
    ]
    assert [clean.shown(e.path, base) for e in plan.dirs] == ["logs/scratch/payloads"]
    manifest_said = {entries[4].resolved: "refused: by manifest"}
    plan = clean.plan_clean("scratch", entries[4:], base, [root], ledger_dir, manifest_said)
    assert plan.refused[0].reason == "refused: by manifest"


@pytest.mark.blocking
def test_manifest_blocklist_refuses_a_dotenv_file_and_the_plan_with_it(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "logs" / "scratch" / DOTENV).write_text("SECRET=1\n")
    assert run_clean(base, "scratch", "--yes") == 1
    assert (base / "logs" / "scratch" / "review.patch").exists()
    outcomes = read_recorded(base, "outcome")
    assert len(outcomes) == 2 and outcomes[0]["status"] == "refused"
    assert "blocklisted" in outcomes[0]["summary"]


@pytest.mark.blocking
def test_caches_glob_deletes_matches_whole_and_never_enters_venv(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "caches", "--yes") == 0
    assert not (base / "kgme" / "__pycache__").exists()
    assert (base / ".venv" / "lib" / "__pycache__" / "x.pyc").exists()
    summaries = [o["summary"] for o in read_recorded(base, "outcome")]
    digest = summaries[0].split(" sha256 ")[1].split(" ")[0]
    assert summaries == [
        f"deleted #1 4 B sha256 {digest} kgme/__pycache__/m.pyc",
        "removed #2 kgme/__pycache__/",
        "closed: deleted 1 files 4 B, removed 1 dirs",
    ]


@pytest.mark.blocking
def test_nested_cache_matches_plan_each_path_once(tmp_path: Path) -> None:
    """Review cycle 7 F20: `**/__pycache__` matches both `pkg/__pycache__` and the cache
    nested inside it, and each walk reaches the same file; the plan holds it once."""
    base = write_seed(tmp_path)
    nested = base / "pkg" / "__pycache__" / "nested" / "__pycache__"
    nested.mkdir(parents=True)
    (nested / "x.pyc").write_text("x\n")
    assert run_clean(base, "caches", "--yes") == 0
    assert not (base / "pkg" / "__pycache__").exists()
    summaries = [o["summary"] for o in read_recorded(base, "outcome")]
    paths = [s.rsplit(" ", 1)[1] for s in summaries if not s.startswith("closed:")]
    assert len(paths) == len(set(paths)), "every planned path once"
    assert sum(1 for p in paths if p.endswith("nested/__pycache__/x.pyc")) == 1
    assert summaries[-1] == "closed: deleted 2 files 6 B, removed 4 dirs"


@pytest.mark.blocking
def test_venv_contents_go_and_the_directory_stays(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "venv", "--yes") == 0
    assert (base / ".venv").is_dir() and list((base / ".venv").iterdir()) == []


@pytest.mark.blocking
def test_ledger_test_target_covers_both_test_streams(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "ledger-test", "--yes") == 0
    assert list((base / "logs" / "ledger-test").iterdir()) == []
    assert list((base / "logs" / "trace-test").iterdir()) == []
    assert (base / "logs" / "ledger").is_dir()


@pytest.mark.blocking
def test_second_run_is_a_no_op_with_a_note_and_no_open_intent(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_clean(base, "briefs", "--yes") == 0
    assert run_clean(base, "briefs", "--yes") == 0
    assert len(read_recorded(base, "intent")) == 1
    notes = [n for n in read_recorded(base, "note") if n["key"] == "clean:briefs:empty"]
    assert len(notes) == 1
    assert ledger.open_intents("clean", ledger.read_base_dirs(SETTINGS, base)) == []


@pytest.mark.blocking
def test_intent_without_a_payload_is_reconciled_on_start(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    dirs = ledger.read_base_dirs(SETTINGS, base)
    orphan = events.make_event(
        source="kgme",
        actor="kgme.clean",
        kind="intent",
        job="clean",
        key="clean:agent:2026-10-08T19:00",
        summary="clean agent delete: 2 files 10 B, 1 dirs, 0 refused",
    )
    ledger.append(orphan, dirs)
    assert run_clean(base, "agent") == 0
    closing = [e for e in ledger.read(dirs) if e["ref"] == orphan["id"]]
    assert len(closing) == 1
    assert closing[0]["status"] == "error" and closing[0]["class"] == "transient"
    assert (
        closing[0]["summary"].startswith("closed: reconciled on start")
        and "no payload" in closing[0]["summary"]
    )
    assert ledger.open_intents("clean", dirs) == []
