"""Tests for the cycle of `kgme review` (HANDOFF-0029 acceptance) through a fake `codex`.

Purpose: one round trip that writes the audit and binds the outcome to the diff hash, the
dry run that writes nothing, the second cycle that needs dispositions and shows the prior
table the ledger names, bounded retries on tooling failures with no open intent left behind,
rulings recorded once and applied, and a halt that is persisted, enforced, and overridden.
Inputs: a fake `codex` on PATH that records its argv; a temporary directory per test.
Outputs: pytest assertions.
Side effects: files under `tmp_path` and under `logs/scratch/payloads/test/`; events in the
test streams; never a file under `docs/audit/`.
"""

import os
from pathlib import Path

import pytest

from kgme import config, ledger, paths, review_io, review_run
from tests.test_review import SAMPLE

ROOT = paths.root()
ONLY_F2 = SAMPLE.replace("| F3 | blocking, unresolved | `c.py:9` | Still open. | Fix it. |\n", "")


def fake_codex(tmp_path: Path, body: str, exit_code: int = 0) -> str:
    """A `codex` on PATH that records its argv and writes `body` to the `-o` file."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "codex"
    script.write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$@" > "{tmp_path}/argv.txt"\n'
        "out=''\n"
        'while [ $# -gt 0 ]; do if [ "$1" = "-o" ]; then out="$2"; shift; fi; shift; done\n'
        f"cat > \"$out\" <<'REVIEW'\n{body}\nREVIEW\n"
        f"exit {exit_code}\n"
    )
    script.chmod(0o755)
    return f"{bin_dir}:{os.environ['PATH']}"


def places_for(tmp_path: Path, handoff: str) -> review_io.Places:
    """Test places: test streams, a temp audit dir, a temp handoff dir holding one handoff."""
    settings = config.read_config()
    handoff_dir = tmp_path / "handoff"
    handoff_dir.mkdir()
    (handoff_dir / "toy.md").write_text(
        f"---\nid: {handoff}\ntype: handoff\n---\n\n# Toy\n\n## What\nA toy.\n\n"
        "## Acceptance test\nNone.\n"
    )
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()
    return review_io.Places(
        dirs=ledger.read_test_dirs(settings),
        audit_dir=audit_dir,
        scratch=tmp_path / "scratch",
        payloads=paths.payloads_dir(settings) / "test" / f"{os.getpid()}-{tmp_path.name}",
        handoff_dir=handoff_dir,
        prompt_path=paths.review_prompt(settings),
        root=ROOT,
    )


def cycle(handoff: str, places: review_io.Places, dispositions: str = "", patch: str = "diff\n"):
    return review_run.run_cycle(handoff, "fake", dispositions, patch, places, False, backoff=())


def recorded(handoff: str, places: review_io.Places) -> list[dict]:
    return review_io.read_handoff_events(handoff, places.dirs)


@pytest.mark.blocking
def test_round_trip_writes_the_audit_and_binds_the_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, SAMPLE))
    handoff = f"HANDOFF-T{os.getpid()}A"
    places = places_for(tmp_path, handoff)
    patch = "diff --git a/toy.py b/toy.py\n+print('toy')\n"
    assert cycle(handoff, places, patch=patch) == 1
    written = list(places.audit_dir.glob("AUDIT-*-review-*-cycle-1.md"))
    assert len(written) == 1
    text = written[0].read_text()
    assert "open_blocking: [F2, F3]" in text and "verdict: BLOCK" in text
    assert "| F2 | blocking |" in text and "| F12 | advisory |" in text
    assert "--json" in (tmp_path / "argv.txt").read_text()
    sha = review_io.sha256_text(patch)
    events_seen = recorded(handoff, places)
    # F12 had no class, so one reclassification note sits between the intent and the outcome.
    assert [e["kind"] for e in events_seen] == ["intent", "note", "outcome"]
    intent, outcome = events_seen[0], events_seen[-1]
    assert outcome["ref"] == intent["id"]
    assert intent["key"] == f"review:{handoff}:{sha[:16]}" and sha[:16] in outcome["summary"]
    assert outcome["class"] == "blocking" and "blocking=F2,F3" in outcome["summary"]
    assert (ROOT / outcome["payload_ref"]).exists()
    assert (places.scratch / "review.sha").read_text().strip() == sha[:16]


@pytest.mark.blocking
def test_dry_run_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, SAMPLE))
    handoff = f"HANDOFF-T{os.getpid()}D"
    places = places_for(tmp_path, handoff)
    assert review_run.run_cycle(handoff, "fake", "", "diff\n", places, True) == 0
    assert not places.scratch.exists() and not list(places.audit_dir.iterdir())
    assert recorded(handoff, places) == [] and not (tmp_path / "argv.txt").exists()
    assert "nothing written" in capsys.readouterr().out


@pytest.mark.blocking
def test_cycle_two_needs_dispositions_and_shows_the_prior_table_the_ledger_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, SAMPLE))
    handoff = f"HANDOFF-T{os.getpid()}P"
    places = places_for(tmp_path, handoff)
    assert cycle(handoff, places, patch="diff one\n") == 1
    assert cycle(handoff, places, patch="diff two\n") == 2
    assert "needs --dispositions" in capsys.readouterr().out
    assert review_run.run_cycle(handoff, "fake", "F2 fixed.", "diff two\n", places, True) == 0
    prompt = capsys.readouterr().out
    assert "| F2 | blocking |" in prompt and "F2 fixed." in prompt and "cycle 2" in prompt
    # After an override the strike window restarts but the labels keep counting; the prior
    # table is the audit the ledger names, cycle 3 here, not a guess from cycle numbers (F5).
    assert cycle(handoff, places, "d", "diff two\n") == 1
    assert review_io.write_override(handoff, "restart", places)
    assert cycle(handoff, places, "d", "diff three\n") == 1
    latest = sorted(places.audit_dir.glob("*cycle-3.md"))[-1]
    assert review_run.run_cycle(handoff, "fake", "again", "diff four\n", places, True) == 0
    prompt = capsys.readouterr().out
    table = latest.read_text().partition("## Findings")[2].partition("## Verdict")[0]
    assert table.strip()[:60] in prompt


@pytest.mark.blocking
def test_prior_table_keeps_every_row_when_a_cell_quotes_a_header(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    quoting = (
        "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
        "| F1 | blocking | a.py:1 | splits at `## Verdict` and drops rows. | Use sections. |\n"
        "| F2 | advisory | b.py:2 | The row after the quoted header. | Keep it. |\n"
        "\n## Verdict\n\nBLOCK: 1 open.\n\n## Notes\n\nnone\n"
    )
    monkeypatch.setenv("PATH", fake_codex(tmp_path, quoting))
    handoff = f"HANDOFF-T{os.getpid()}Q"
    places = places_for(tmp_path, handoff)
    assert cycle(handoff, places) == 1
    assert review_run.run_cycle(handoff, "fake", "F1 fixed.", "diff two\n", places, True) == 0
    prompt = capsys.readouterr().out
    assert "| F1 | blocking |" in prompt and "| F2 | advisory |" in prompt, (
        "both rows reach cycle 2"
    )
    assert "The row after the quoted header." in prompt


@pytest.mark.blocking
def test_tooling_failures_retry_within_bounds_and_close_the_intent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, "HTTP 429 Too Many Requests"))
    handoff = f"HANDOFF-T{os.getpid()}R"
    places = places_for(tmp_path, handoff)
    assert cycle(handoff, places) == 1
    events_seen = recorded(handoff, places)
    kinds = [(e["kind"], e["status"], e["class"]) for e in events_seen]
    assert kinds[0] == ("intent", None, None)
    assert kinds[1:4] == [("outcome", "error", "transient")] * 3
    assert kinds[4] == ("outcome", "error", "blocking") and "exhausted" in events_seen[4]["summary"]
    assert all(e["ref"] == events_seen[0]["id"] for e in events_seen[1:])
    assert not [e for e in ledger.open_intents(f"review:{handoff}", places.dirs)]
    assert not list(places.audit_dir.iterdir())
    broken = (
        "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
        "| F1 | blocking | x |\n\n## Verdict\n\nBLOCK"
    )
    monkeypatch.setenv("PATH", fake_codex(tmp_path, broken))
    assert cycle(handoff, places) == 1
    assert "malformed" in recorded(handoff, places)[-2]["summary"]
    monkeypatch.setenv("PATH", fake_codex(tmp_path, "## Findings\n\nincomplete; cannot PASS\n"))
    assert cycle(handoff, places) == 1
    assert "no findings table" in recorded(handoff, places)[-2]["summary"]


@pytest.mark.blocking
def test_a_ruling_changes_the_verdict_survives_an_override_and_is_recorded_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, ONLY_F2))
    handoff = f"HANDOFF-T{os.getpid()}U"
    places = places_for(tmp_path, handoff)
    assert cycle(handoff, places) == 1
    assert review_io.write_ruling(handoff, "F2", "advisory", "residual", "opus", places)
    assert review_io.write_ruling(handoff, "F2", "blocking", "again", "opus", places) is None
    assert cycle(handoff, places, "F2 ruled.") == 0
    latest = sorted(places.audit_dir.glob("*cycle-2.md"))[-1].read_text()
    assert "verdict: PASS" in latest and "| F2 | advisory |" in latest
    assert review_io.write_override(handoff, "fresh start", places)
    assert cycle(handoff, places, "d") == 0, "the ruling still applies after the override"


@pytest.mark.blocking
def test_a_halt_is_persisted_and_enforced_until_an_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.setenv("PATH", fake_codex(tmp_path, ONLY_F2))
    handoff = f"HANDOFF-T{os.getpid()}H"
    places = places_for(tmp_path, handoff)
    # the same diff reviewed twice is measure (b) of HANDOFF-0043 amendment 16
    assert [cycle(handoff, places, "d" if c > 1 else "") for c in (1, 2)] == [1, 3]
    out = capsys.readouterr().out
    assert "ESCALATION" in out and "If you do nothing" in out and "arbiter opus" in out
    assert "was reviewed before" in out
    halt = [e for e in recorded(handoff, places) if (e["key"] or "").startswith("halt:")][-1]
    assert "If you do nothing" in (ROOT / halt["payload_ref"]).read_text()
    latest = sorted(places.audit_dir.glob("*cycle-2.md"))[-1].read_text()
    assert "## Escalation" in latest
    (tmp_path / "argv.txt").unlink()
    assert cycle(handoff, places, "d") == 3
    assert not (tmp_path / "argv.txt").exists(), "the reviewer must not run while halted"
    assert review_io.write_override(handoff, "understood", places)
    assert cycle(handoff, places, "d") == 1
    assert (tmp_path / "argv.txt").exists()


@pytest.mark.blocking
def test_a_task_review_carries_the_tasks_contract_before_the_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """HANDOFF-0048, cycle 2 F20: a crew task's review is judged against the task's own
    Outputs, acceptance check and description, put before the prompt; a handoff's review
    carries none."""
    from kgme import crew_io
    from kgme.crew import Task

    handoff = f"HANDOFF-T{os.getpid()}K"
    places = places_for(tmp_path, handoff)
    check = "uv run --frozen pytest -q tests -k toy_parse"
    task = Task(handoff, "parse", ("kgme/toy_parse.py",), check, "claude", "claude-opus-5-5",
                description="Parse the toy's lines.")  # fmt: skip
    contract = crew_io.task_contract(task)
    assert "one task of its crew's plan, not the whole handoff" in contract
    assert "kgme/toy_parse.py" in contract and "Parse the toy's lines." in contract
    code = review_run.run_cycle(
        f"{handoff}:parse", "toy", "", "+x\n", places, True, contract=contract
    )
    assert code == 0
    out = capsys.readouterr().out
    assert out.index("one task of its crew's plan") < out.index("You are the reviewer"), "first"
    review_run.run_cycle(handoff, "toy", "", "+x\n", places, True)
    assert "one task of its crew's plan" not in capsys.readouterr().out


@pytest.mark.blocking
def test_a_settled_ruling_reaches_a_builder_whole_not_clipped(tmp_path: Path) -> None:
    """HANDOFF-0048, cycle 3 F6: a settled ruling's summary is clipped to the writer's cap,
    so the whole ruling (a split's every option, the chosen one) travels as its payload and
    `loop.rulings_text` gives a builder the whole text."""
    from kgme import loop

    handoff = f"HANDOFF-T{os.getpid()}L"
    places = places_for(tmp_path, handoff)
    places.payloads.mkdir(parents=True, exist_ok=True)
    reason = (
        "split (claude-opus-5-5=blocking: "
        + "settle every finding before the restart " * 5
        + "(blast 2, reversible), claude-fable-5-1=blocking: "
        + "carry the rulings whole " * 6
        + "(blast 2, reversible)); took claude-opus-5-5: "
        + "the chosen option, in full " * 4
    )
    assert len(reason) > 400
    note_id = review_io.write_ruling(handoff, "F6", "blocking", reason, "pair", places)
    (note,) = [e for e in recorded(handoff, places) if e["id"] == note_id]
    assert len(note["summary"]) <= 200 and note["payload_ref"], "clipped, with its payload"
    text = loop.rulings_text(handoff, places)
    assert reason in text and "to execute" in text, text[-300:]
