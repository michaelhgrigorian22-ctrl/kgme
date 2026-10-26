"""Tests for the cockpit's view of the ledger (HANDOFF-0037 §2 and its amendment).

Purpose: the contract between the design and the code. The design's sample events pass the
ledger's own validator; the run lifecycle of `cockpit/render.py` gives, at seven clocks, the
word, quiet note and closing the station prototype's own `lifecycle` and `runClosed` give (the
pinned answers of the station's JavaScript, run over the same file at 51 clocks on 2026-10-25:
267 comparisons, no disagreement); each written rule has its own case; and the view pairs,
nests, collapses and limits as the page needs, with each run's state taken over its history.
Inputs: `docs/design/cockpit-v0/station/sample-events.jsonl`; synthetic events built here.
Outputs: pytest assertions.
Side effects: none.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cockpit import render
from kgme import events

SAMPLE = Path(__file__).parents[1] / "docs" / "design" / "cockpit-v0" / "station"
SAMPLE = SAMPLE / "sample-events.jsonl"
DAY = "2026-10-08T{}.000-07:00"
STATION = [
    ("19:42:30", "c70d687b-55ac-4d55-a22c-8006208d8447", "blocked", "", False),
    ("19:43:30", "01M4F8NR8147T0KJA7TD08P04F", "transient", "", False),
    ("19:41:30", "3f9e21aa-7b02-4c7e-9d1f-2e6a0b5fc0d1", "waiting", "", False),
    ("19:40:30", "c70d687b-55ac-4d55-a22c-8006208d8447", "working", "", False),
    ("19:43:00", "01M4F8PZ2QD0V7H2N0S4T9XK2QD", "working", "", True),
    ("19:46:00", "c70d687b-55ac-4d55-a22c-8006208d8447", "working", "quiet 3m", False),
    ("19:46:00", "01M4F8PZ2QD0V7H2N0S4T9XK2QD", "working", "quiet 3m", True),
]


def read_sample() -> list[dict]:
    return [json.loads(line) for line in SAMPLE.read_text().splitlines() if line.strip()]


def event(n: int, kind: str, minute: float, **fields: object) -> dict:
    """A minimal event `n` of run `r`, at 19:40 plus `minute` minutes."""
    start = datetime.fromisoformat(DAY.format("19:40:00"))
    ts = (start + timedelta(minutes=minute)).isoformat(timespec="milliseconds")
    base = {"id": f"01M4F8G9YGSP1ACEPJRMAH{n:04d}", "ts": ts, "run_id": "r", "kind": kind}
    return {"actor": "kgme.test", "job": "tool:Bash", "class": None, "status": None,
            "ref": None, "parent": None, "summary": "s", "key": None, **base, **fields}  # fmt: skip


def at(minute: float) -> int:
    return render.ts_ms(DAY.format("19:40:00")) + int(minute * 60_000)


@pytest.mark.blocking
def test_the_design_sample_events_pass_the_ledger_validator() -> None:
    """The amendment's contract: what the design draws is what the ledger can hold."""
    sample = read_sample()
    assert len(sample) == 40
    for line in sample:
        events.validate_event(line)


@pytest.mark.blocking
@pytest.mark.parametrize("clock,run_id,word,quiet,closed", STATION)
def test_the_lifecycle_matches_the_station_prototype(
    clock: str, run_id: str, word: str, quiet: str, closed: bool
) -> None:
    now = render.ts_ms(DAY.format(clock))
    seen = [e for e in read_sample() if e["run_id"] == run_id and render.ts_ms(e["ts"]) <= now]
    assert render.lifecycle(seen, now) == (word, quiet)
    assert render.run_closed(seen) is closed


@pytest.mark.blocking
def test_each_written_lifecycle_rule() -> None:
    intent, outcome = event(1, "intent", 0), event(2, "outcome", 0.1, ref=event(1, "x", 0)["id"])
    assert render.lifecycle([intent], at(0.2)) == ("waiting", "")
    assert render.lifecycle([intent, outcome], at(0.2)) == ("working", "")
    blocking = {**outcome, "class": "blocking"}
    assert render.lifecycle([intent, blocking], at(0.2)) == ("blocked", "")
    retry = {**blocking, "summary": "rate limited; retry after 30s"}
    assert render.lifecycle([intent, retry], at(0.2)) == ("transient", "")
    assert render.lifecycle([intent, {**outcome, "class": "transient"}], at(0.2))[0] == "transient"
    halt = event(3, "note", 0.2, **{"class": "blocking"})
    bookkeeping = event(4, "note", 0.3)
    assert render.lifecycle([intent, outcome, halt, bookkeeping], at(0.4)) == ("blocked", "")
    moved = event(5, "approval", 0.5)
    assert render.lifecycle([intent, outcome, halt, moved], at(0.6)) == ("working", "")
    assert render.lifecycle([event(6, "note", 0)], at(0.1)) == ("working", "")


@pytest.mark.blocking
def test_quiet_is_the_median_intent_gap_never_under_three_minutes() -> None:
    """Four intents 5, 7 and 9 minutes apart: the median gap is 7 minutes, so the run is quiet
    only after 7 minutes without an event; with one intent, after three minutes."""
    run = []
    for n, minute in enumerate((0, 5, 12, 21)):
        run += [event(2 * n + 1, "intent", minute), event(2 * n + 2, "outcome", minute + 0.1)]
    assert render.lifecycle(run, at(21.1 + 6.9)) == ("working", "")
    assert render.lifecycle(run, at(21.1 + 7.2)) == ("working", "quiet 7m")
    lone = [event(1, "intent", 0), event(2, "outcome", 0.1)]
    assert render.lifecycle(lone, at(3.0)) == ("working", "")
    assert render.lifecycle(lone, at(3.2)) == ("working", "quiet 3m")


@pytest.mark.blocking
def test_runs_close_by_their_kind() -> None:
    job = event(1, "intent", 0, job="brief")
    done = event(2, "outcome", 1, ref=job["id"], status="ok", job="brief")
    assert render.run_closed([job, done])
    assert not render.run_closed([job, {**done, "status": "error"}])
    hook = event(3, "intent", 0)
    assert not render.run_closed([hook, event(4, "outcome", 1, ref=hook["id"], status="ok")])
    assert render.run_closed([hook, event(5, "note", 2, key="session:end")])


@pytest.mark.blocking
def test_the_view_pairs_nests_collapses_and_limits() -> None:
    root = event(1, "intent", 0)
    answered = event(2, "outcome", 0.1, ref=root["id"], parent=root["id"])
    child = event(3, "intent", 0.2, parent=root["id"])
    read = event(4, "intent", 0.3, parent=root["id"], job="tool:Read")
    view = render.build_view([root, answered, child], [read], at(0.4))
    rows = {row["id"]: row for row in view["events"]}
    assert rows[root["id"]]["outcome_id"] == answered["id"] and not rows[root["id"]]["unmatched"]
    assert rows[child["id"]]["unmatched"] and rows[child["id"]]["depth"] == 1
    assert rows[read["id"]]["stream"] == "trace" and rows[read["id"]]["collapsed"]
    assert not rows[root["id"]]["collapsed"]
    assert view["runs"]["r"]["word"] == "waiting", "the newest operation is an open intent"
    assert view["cursor"] == read["id"]
    later = render.build_view([root, answered, child], [read], at(0.4), since=child["id"])
    assert [row["id"] for row in later["events"]] == [read["id"]]
    assert later["runs"]["r"]["word"] == "waiting", "the state is over the whole history"
    limited = render.build_view([root, answered, child], [read], at(0.4), limit=2)
    assert [row["id"] for row in limited["events"]] == [child["id"], read["id"]]
    empty = render.build_view([root], [], at(0.4), since=root["id"])
    assert empty["events"] == [] and empty["cursor"] == root["id"]
    assert empty["runs"]["r"]["word"] == "waiting", "an open run's state comes with every poll"


@pytest.mark.blocking
def test_a_run_turns_quiet_on_an_unchanged_ledger_polled_with_the_same_cursor() -> None:
    """Review cycle 1 F3: once the last outcome has been returned, the page polls with that
    cursor and gets no new events; the run's state must still move to quiet when the three
    minutes pass, and a closed run drops out."""
    intent, outcome = event(1, "intent", 0), event(2, "outcome", 0.1, ref=event(1, "x", 0)["id"])
    first = render.build_view([intent, outcome], [], at(0.2))
    cursor = first["cursor"]
    before = render.build_view([intent, outcome], [], at(2.0), since=cursor)
    after = render.build_view([intent, outcome], [], at(3.5), since=cursor)
    assert before["events"] == after["events"] == []
    assert before["runs"]["r"]["quiet"] == "" and after["runs"]["r"]["quiet"] == "quiet 3m"
    job = event(3, "intent", 0, job="brief", run_id="j")
    done = event(4, "outcome", 0.1, ref=job["id"], status="ok", job="brief", run_id="j")
    closed = render.build_view([job, done], [], at(5.0), since=done["id"])
    assert closed["runs"] == {}, "a closed run is not refreshed once its events are past"


@pytest.mark.blocking
def test_polling_with_the_cursor_never_skips_an_event() -> None:
    """Review cycle 3 F8: an intent's outcome followed by fifty more events before the next
    poll used to fall outside the newest fifty, so the page never learned the intent closed.
    Polling with the cursor now walks every event in order and reaches the outcome."""
    intent = event(1, "intent", 0)
    first = render.build_view([intent], [], at(0.1))
    assert [row["id"] for row in first["events"]] == [intent["id"]]
    later = [event(2, "outcome", 0.2, ref=intent["id"])]
    later += [event(3 + n, "note", 0.3 + n / 100) for n in range(55)]
    seen, cursor = [], first["cursor"]
    for _ in range(3):
        page = render.build_view([intent, *later], [], at(2), since=cursor, limit=50)
        seen += [row["id"] for row in page["events"]]
        cursor = page["cursor"]
    assert seen == [e["id"] for e in later], "every event, in order, none skipped"
    assert seen[0] == later[0]["id"], "the outcome arrives on the first poll after the intent"


@pytest.mark.blocking
def test_the_first_page_is_the_newest_fifty_of_more() -> None:
    """The acceptance's fifty-event boundary, with more than fifty held."""
    events_ = [event(n, "note", n / 100) for n in range(1, 61)]
    page = render.build_view(events_, [], at(2))
    assert [row["id"] for row in page["events"]] == [e["id"] for e in events_[-50:]]


@pytest.mark.blocking
def test_the_last_fifty_sample_events_in_time_order() -> None:
    sample = read_sample()
    view = render.build_view(sample, [], render.ts_ms(sample[-1]["ts"]))
    shown = [row["ts"] for row in view["events"]]
    assert len(shown) == 40 and shown == sorted(shown, key=render.ts_ms)
    assert set(view["runs"]) == {e["run_id"] for e in sample}
