"""Tests for `kgme daily` (HANDOFF-0050): drafted once, from what the day left, citing it.

Purpose: a day with ledger events writes one note whose sections cite the events, commits,
handoffs, reports, and notes they came from, and a second run does nothing; a day with
nothing in the ledger writes nothing and records nothing; a note that exists, Michou's or a
draft, is never touched; daily lines held before the draft land under `Michou`, and lines
captured after it append there; problems are paired with what cleared them; the draft
passes the validator; the day's commits come from `git log` with the handoff files they
moved.
Inputs: the seeded vault of `tests/capturetools.py`; a real `git init` for one test.
Outputs: pytest assertions.
Side effects: files, a git repository, and ledger lines under `tmp_path` only.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

import pytest
from brieftools import SETTINGS, brief_io_parse
from capturetools import read_job, run_capture, run_daily, write_vault

from kgme import capture, daily, events, ledger, lint

TODAY = datetime.now().astimezone().date().isoformat()


def note_path(base: Path, date: str = TODAY) -> Path:
    return base / "memory" / "daily" / f"{date}.md"


def plant(base: Path, **fields) -> dict:
    event = events.make_event(source="kgme", actor="test", **fields)
    ledger.append(event, ledger.read_base_dirs(SETTINGS, base))
    return event


@pytest.mark.blocking
def test_a_day_with_nothing_in_the_ledger_writes_nothing_and_records_nothing(
    tmp_path: Path,
) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_daily(base, TODAY) == 0
    assert not note_path(base).exists()
    assert read_job(base, "daily") == []


@pytest.mark.blocking
def test_a_day_with_events_writes_one_note_citing_them_and_a_second_run_does_nothing(
    tmp_path: Path, capsys
) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "friction", "the reviewer timed out", now=None) == 0
    assert run_capture(base, "remind", "call the reader", "tomorrow 10am", now=None) == 0
    ruling = plant(
        base,
        kind="note",
        job="review:HANDOFF-0899",
        key="ruling:F1=advisory",
        summary="arbiter ruled F1=advisory: style",
    )
    capsys.readouterr()
    assert run_daily(base, TODAY) == 0
    text = note_path(base).read_text()
    assert text in capsys.readouterr().out
    data, body = brief_io_parse(text)
    assert (data["type"], data["date"], data["source"], data["author"]) == (
        "daily",
        TODAY,
        "inferred",
        "kgme",
    )
    captured = [e["id"] for e in read_job(base, "capture", "outcome")]
    for event_id in [*captured, ruling["id"]]:
        assert f"({event_id})" in body and event_id in data["sources"]
    assert "HANDOFF-0899 done: Handoff 0899 — the finished one" in body
    assert "AUDIT-0900: What the finished one taught" in body
    assert "open handoff HANDOFF-0900: Handoff 0900 — the open one" in body
    assert "call the reader" in body.split("## Tomorrow")[1]
    friction = body.split("## Friction")[1].split("## Michou")[0]
    assert "— the reviewer timed out" in friction
    headings = [line for line in body.splitlines() if line.startswith("## ")]
    assert headings == [
        "## Today",
        "## Learned",
        "## Problems and solutions",
        "## Tomorrow",
        "## Friction",
        "## Michou",
    ]
    assert [
        f for f in lint.lint_note(text, f"memory/daily/{TODAY}.md", {}) if f.cls == "blocking"
    ] == []
    pair = read_job(base, "daily")
    assert [e["kind"] for e in pair] == ["intent", "outcome"] and pair[1]["status"] == "ok"
    before = note_path(base).read_bytes()
    assert run_daily(base, TODAY) == 0
    assert note_path(base).read_bytes() == before
    assert read_job(base, "daily") == pair


@pytest.mark.blocking
def test_held_lines_land_under_michou_and_later_ones_append_there(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_capture(base, "daily", "finished the costing homework", now=None) == 0
    assert run_daily(base, TODAY) == 0
    assert run_capture(base, "daily", "thesis reading done", now=None) == 0
    body = note_path(base).read_text().split(f"## {capture.MICHOU}\n")[1]
    assert body == (
        f"{capture.MICHOU_MARK}\n- finished the costing homework\n- thesis reading done\n"
    )


@pytest.mark.blocking
def test_a_note_that_exists_is_never_touched(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    plant(base, kind="note", summary="something happened")
    note_path(base).write_text("mine\n")
    assert run_daily(base, TODAY) == 0
    assert note_path(base).read_text() == "mine\n"
    assert read_job(base, "daily") == []


@pytest.mark.blocking
def test_a_daily_note_that_is_a_link_is_left_alone(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    plant(base, kind="note", summary="something happened")
    target = base / "docs" / "elsewhere.md"
    target.write_text("keep\n")
    note_path(base).symlink_to(target)
    assert run_daily(base, TODAY) == 0
    assert target.read_text() == "keep\n"


@pytest.mark.blocking
def test_a_daily_folder_reached_through_a_link_is_refused(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    plant(base, kind="note", summary="something happened")
    real = tmp_path / "outside"
    (base / "memory" / "daily").rename(real)
    (base / "memory" / "daily").symlink_to(real)
    before = sorted(p.name for p in real.iterdir())
    assert run_daily(base, TODAY) == 1
    assert sorted(p.name for p in real.iterdir()) == before
    assert read_job(base, "daily", "outcome")[-1]["status"] in ("refused", "error")


@pytest.mark.blocking
def test_a_bad_day_exits_2(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    assert run_daily(base, "2026-02-30") == 2
    assert read_job(base, "daily") == []


def day_of(events_: list[dict], **more) -> daily.Day:
    fields = dict(
        date="2026-10-15",
        events=tuple(events_),
        commits=(),
        git_note="",
        handoffs=(),
        reports=(),
        items=(),
        friction=(),
        held=(),
        unread=(),
    )
    fields.update(more)
    return daily.Day(**fields)


def outcome(job: str, summary: str, status: str = "ok", cls: str | None = None) -> dict:
    return events.make_event(
        source="kgme", actor="t", kind="outcome", job=job, summary=summary, status=status,
        class_=cls,
    )  # fmt: skip


@pytest.mark.blocking
def test_problems_are_paired_with_what_cleared_them() -> None:
    blocked = outcome("review:HANDOFF-0900", "review cycle 1 BLOCK blocking=F1")
    passed = outcome("review:HANDOFF-0900", "review cycle 2 PASS blocking=-")
    refused = outcome("capture", "refused: could not read", "refused", "blocking")
    text = daily.build_daily(day_of([blocked, refused, passed]), "01K", "now", None)
    section = text.split("## Problems and solutions")[1].split("## Tomorrow")[0]
    assert f"- problem: review cycle 1 BLOCK blocking=F1 ({blocked['id']})" in section
    assert f"- solved: review cycle 2 PASS blocking=- ({passed['id']})" in section
    assert f"- problem: refused: could not read ({refused['id']})" in section
    assert section.count("  - still open at the end of the day") == 1
    today = text.split("## Today")[1].split("## Learned")[0]
    assert "BLOCK" not in today and "PASS" in today


@pytest.mark.blocking
def test_tool_calls_and_pushes_are_counted_not_listed() -> None:
    call = events.make_event(
        source="claude-code", actor="hook", kind="intent", job="tool:Bash", summary="Bash"
    )
    push = outcome("sync", "pushed main abc")
    commits = (
        daily.Commit("aaa", "ledger: 6 events through x", ()),
        daily.Commit("bbb", "vault: something (HANDOFF-0900)", ()),
        daily.Commit(
            "ccc",
            "tree: moves",
            tuple((f"docs/handoff/{n}.md", f"docs/handoff/done/{n}.md") for n in range(5)),
        ),
    )
    text = daily.build_daily(day_of([call, push], commits=commits), "01K", "now", None)
    today = text.split("## Today")[1].split("## Learned")[0]
    assert "pushed main" not in today and "Bash" not in today
    assert "- 1 agent tool calls in 1 session(s), in the ledger" in today
    assert "- commit bbb vault: something (HANDOFF-0900)" in today
    assert "- 1 ledger commit(s) by kgme sync" in today and "aaa" not in today
    assert "  - moved 5 handoff file(s) to docs/handoff/done/" in today


@pytest.mark.blocking
def test_the_days_commits_and_handoff_moves_come_from_git(tmp_path: Path) -> None:
    base = write_vault(tmp_path, TODAY)
    os.rmdir(base / ".git")
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.invalid",
    }

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=base, env=env, check=True, capture_output=True)

    git("init", "-q")
    git("add", "docs")
    git("commit", "-q", "-m", "seed")
    git("mv", "docs/handoff/open.md", "docs/handoff/done/open.md")
    git("commit", "-q", "-m", "handoff: close 0900")
    plant(base, kind="note", summary="something happened")
    assert run_daily(base, TODAY) == 0
    today = note_path(base).read_text().split("## Today")[1].split("## Learned")[0]
    assert "handoff: close 0900" in today
    assert "  - moved docs/handoff/open.md → docs/handoff/done/open.md" in today
