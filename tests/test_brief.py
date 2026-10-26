"""Tests for `kgme brief` v1 (HANDOFF-0034: the four ADR-015 job tests, each with its
ADR-016 class, plus the dry run and the rendering rules).

Purpose: on a seeded vault under `tmp_path`: two runs give one artefact with the same id,
`created`, and bytes; an intent left open is reconciled against the intended hash; a planted
forbidden input is refused with a `blocking` outcome and no artefact; the artefact deleted
with `kgme clean briefs --yes` regenerates byte-identical from the ledger and `memory/`;
`--dry-run` writes no file and exactly one `note`; the daily note is read by its headings;
missing inputs and empty sections are stated; the output passes the validator; `modified`
moves only when the content does; the job folder's `run.py` runs the same job.
Inputs: `kgme.toml`, `jobs/brief/manifest.toml`, the seeded vault of `tests/brieftools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only.
"""

import hashlib
import sys
from pathlib import Path

import pytest
from brieftools import (
    BRIEF,
    DATE,
    SETTINGS,
    frontmatter,
    note,
    read_recorded,
    run_brief,
    write_seed,
)

from kgme import brief, brief_io, clean_io, cli, config, events, ledger, lint, paths

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jobs" / "brief"))
import run as brief_run  # noqa: E402 - the job folder's entry point, not a package


@pytest.mark.blocking
def test_selection_sorts_by_due_then_priority_then_id_and_skips_closed(tmp_path: Path) -> None:
    from kgme import brief_read

    base = write_seed(tmp_path)
    input_paths, unlisted = brief_read.read_input_paths(base, DATE)
    inputs, refusals = brief_read.read_inputs(brief_read.read_places(SETTINGS, base), input_paths)
    assert unlisted == [] and refusals == []
    selection = brief.select(inputs, DATE)
    assert [i.id for i in selection.items] == [
        "20261001T090001",
        "20261001T090003",
        "20261001T090004",
        "20261001T090007",
    ]
    assert selection.daily is not None and selection.friction is not None
    assert "01K0000000000000000000PREV" not in [i.id for i in selection.inputs()]
    assert selection.inputs() == sorted(selection.inputs(), key=lambda i: i.id)


@pytest.mark.blocking
def test_run_twice_gives_one_artefact_with_the_same_id_created_and_bytes(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    first = (base / BRIEF).read_text(encoding="utf-8")
    assert run_brief(base) == 0
    second = (base / BRIEF).read_text(encoding="utf-8")
    assert first == second
    data = frontmatter(second)
    assert data["author"] == "kgme" and data["source"] == "inferred"
    assert sorted(p.name for p in (base / "memory/agent/brief").iterdir()) == [
        "2026-10-07.md",
        f"{DATE}.md",
    ]
    intents, outcomes = read_recorded(base, "intent"), read_recorded(base, "outcome")
    assert len(intents) == 2 and [o["status"] for o in outcomes] == ["ok", "ok"]
    assert all(o["ref"] == i["id"] for o, i in zip(outcomes, intents, strict=True))
    assert all(i["payload_ref"].startswith("logs/scratch/payloads/") for i in intents)
    assert ledger.open_intents("brief", ledger.read_base_dirs(SETTINGS, base)) == []


@pytest.mark.blocking
def test_body_renders_every_section_from_the_seeded_vault(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / BRIEF).read_text(encoding="utf-8")
    body = text.split("---\n", 2)[2]
    sections = [line for line in body.splitlines() if line.startswith("## ")]
    assert sections == [
        "## Due and overdue",
        "## Today",
        "## Open tasks",
        "## Friction since last brief",
        "## Kept copies",
        "## Inputs",
    ]
    assert "## Kept copies\nNo kept copies under memory/.\n" in body  # HANDOFF-0052
    assert "- overdue 2026-10-07 09:00  Call the reader  (reminder 20261001T090001)" in body
    assert (
        "- due today 2026-10-08 18:00  Chapter 2 draft  "
        "(task 20261001T090003, priority 1, doing, [[thesis]])"
    ) in body
    assert "Already done" not in body and "Dropped" not in body and "A plain note" not in body
    assert "Today:\n- wrote the sync hook\nLearned:\n- uv falls back" in body
    assert "Tomorrow:\n- seed the vault" in body
    assert "Problems and solutions:" not in body, "an empty daily section is not rendered"
    assert "- no due date  Machine task  (task 20261001T090007, priority 3, open)" in body
    assert "Since 2026-10-07, the previous brief:" in body
    assert "on the previous brief's day" in body and "before the previous brief" not in body
    assert "From the daily note's Friction section:\n- 2026-10-08 20:00" in body
    inputs = [line for line in body.splitlines() if line.startswith("- ") and " — sha256 " in line]
    assert len(inputs) == 6 and all(len(line.rsplit(" ", 1)[-1]) == 64 for line in inputs)


@pytest.mark.blocking
def test_missing_daily_note_and_empty_sections_are_stated(tmp_path: Path) -> None:
    base = write_seed(tmp_path, daily=False, items=False)
    assert run_brief(base) == 0
    text = (base / BRIEF).read_text(encoding="utf-8")
    assert f"No daily note for {DATE}" in text
    assert "Nothing due today and nothing overdue." in text
    assert "No open tasks." in text
    assert "All entries, no previous brief:" in text
    assert 'sources: ["FRICTION-LOG"]' in text


@pytest.mark.blocking
def test_empty_vault_is_refused_not_written(tmp_path: Path) -> None:
    base = tmp_path / "empty"
    (base / "memory" / "notes").mkdir(parents=True)
    (base / "logs" / "ledger").mkdir(parents=True)
    assert run_brief(base) == 1
    assert not (base / BRIEF).exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[0]["status"] == "refused" and "seed the vault" in outcomes[0]["summary"]


@pytest.mark.blocking
def test_open_intent_is_reconciled_against_the_intended_hash(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    dirs = ledger.read_base_dirs(SETTINGS, base)
    written = read_recorded(base, "intent")[-1]
    payload_text = (base / written["payload_ref"]).read_text()
    for name, destination_present in (("match", True), ("gone", False)):
        payload_path = base / "logs" / "scratch" / "payloads" / f"orphan-{name}.json"
        payload_path.write_text(payload_text)
        if not destination_present:
            (base / BRIEF).unlink()
        orphan = events.make_event(
            source="kgme",
            actor="kgme.brief",
            kind="intent",
            job="brief",
            key=f"brief:{DATE}",
            summary=f"orphan {name}",
            payload_ref=payload_path.relative_to(base).as_posix(),
            payload_sha256=hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
        )
        ledger.append(orphan, dirs)
        assert run_brief(base) == 0
        closing = [e for e in ledger.read(dirs) if e["ref"] == orphan["id"]]
        assert len(closing) == 1
        if destination_present:
            assert closing[0]["status"] == "ok" and "intended hash" in closing[0]["summary"]
        else:
            assert closing[0]["status"] == "error" and closing[0]["class"] == "transient"
            assert (base / BRIEF).exists(), "this run rebuilt it"
    assert ledger.open_intents("brief", dirs) == []


@pytest.mark.blocking
def test_planted_forbidden_inputs_are_refused_and_nothing_is_written(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "memory/notes/broken.md").write_text(
        note("bogus", "20261001T090009", "open", "# Not a type")
    )
    assert run_brief(base) == 1
    assert not (base / BRIEF).exists()
    outcomes = read_recorded(base, "outcome")
    assert outcomes[-1]["status"] == "refused" and outcomes[-1]["class"] == "blocking"
    assert "broken.md" in outcomes[-1]["summary"]
    (base / "memory/notes/broken.md").unlink()
    secret = base / "memory" / "private" / "positions.md"
    secret.parent.mkdir(parents=True)
    secret.write_text(note("note", "20261001T090010", "active", "# Tier 1"))
    (base / "memory" / "notes" / "leak.md").symlink_to(secret)
    assert run_brief(base) == 1
    assert not (base / BRIEF).exists()
    summary = read_recorded(base, "outcome")[-1]["summary"]
    assert "leak.md is a symlink" in summary, "refused at the gate, before the manifest is asked"


@pytest.mark.blocking
def test_clean_briefs_then_regenerate_byte_identical(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    (base / "memory/agent/brief/2026-10-07.md").unlink()
    assert run_brief(base, date="2026-10-07") == 0
    assert run_brief(base) == 0
    original = (base / BRIEF).read_bytes()
    assert clean_io.run_clean("briefs", True, base, config.read_config(), home=base) == 0
    assert not (base / BRIEF).exists() and not (base / "memory/agent/brief/2026-10-07.md").exists()
    assert run_brief(base) == 0
    assert (base / BRIEF).read_bytes() == original, (
        "identity and modified come back from the ledger"
    )


@pytest.mark.blocking
def test_dry_run_prints_writes_nothing_and_appends_one_note(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base, "--dry-run") == 0
    out = capsys.readouterr().out
    assert out.startswith("---\nid: ") and f"# Brief {DATE}" in out
    assert not (base / BRIEF).exists()
    assert len(read_recorded(base)) == 1 and read_recorded(base)[0]["kind"] == "note"
    assert (
        not list((base / "logs" / "scratch").rglob("*"))
        if (base / "logs/scratch").exists()
        else True
    )


@pytest.mark.blocking
def test_output_passes_the_validator_and_names_every_input(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / BRIEF).read_text(encoding="utf-8")
    findings = lint.lint_note(text, BRIEF.as_posix(), {})
    assert [f for f in findings if f.cls == "blocking"] == []
    data = frontmatter(text)
    assert data["sources"] == [
        "20261001T090001",
        "20261001T090003",
        "20261001T090004",
        "20261001T090007",
        "20261008T070000",
        "FRICTION-LOG",
    ]


@pytest.mark.blocking
def test_modified_moves_only_when_the_content_moves(tmp_path: Path) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    before = frontmatter((base / BRIEF).read_text())
    task = base / "memory/notes/costing-homework.md"
    task.write_text(task.read_text().replace("priority: 2", "priority: 1"))
    assert run_brief(base) == 0
    after = frontmatter((base / BRIEF).read_text())
    assert (after["id"], after["created"]) == (before["id"], before["created"])
    assert after["modified"] >= before["modified"]
    assert "priority 1, open" in (base / BRIEF).read_text()


@pytest.mark.blocking
def test_both_entry_points_run_this_repository_and_take_no_path(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    seen: list[tuple] = []

    def record(date: str, dry_run: bool, base: Path, settings: dict) -> int:
        seen.append((date, dry_run, base))
        return 0

    monkeypatch.setattr(brief_io, "run_brief", record)
    assert brief_run.main(["--date", DATE, "--dry-run"]) == 0
    assert cli.main(["brief", "--date", DATE]) == 0
    assert seen == [(DATE, True, paths.root()), (DATE, False, paths.root())]
    with pytest.raises(SystemExit):
        brief_run.main(["--base", "x"])
    assert "unrecognized arguments: --base" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        cli.main(["brief", "--base", "x"])
    assert "unrecognized arguments: --base" in capsys.readouterr().err
