"""Tests for concurrent appenders (HANDOFF-0047 §4).

Purpose: eight processes appending 500 events each through `kgme/ledger.py` leave exactly
4,000 whole lines: every line parses, every id is unique, no line is split. The single
writer's `flock` around one `os.write` per event (HANDOFF-0040) is what serialises them.
Inputs: streams under `tmp_path`.
Outputs: pytest assertions.
Side effects: eight child processes; lines under `tmp_path` only.
"""

import json
import multiprocessing
from pathlib import Path

import pytest

from kgme import events, ledger

PROCESSES = 8
EACH = 500


def run_appender(root: str, number: int) -> None:
    """Effect: `EACH` events from appender `number` into the streams under `root`."""
    dirs = ledger.Dirs(Path(root) / "ledger", Path(root) / "trace", ())
    for index in range(EACH):
        summary = f"appender {number} event {index} " + "x" * (number * 7 % 40)
        event = events.make_event(
            source="kgme", actor="kgme.test", kind="note", job="concurrency", summary=summary
        )
        ledger.append(event, dirs)


@pytest.mark.blocking
def test_eight_appenders_leave_exactly_four_thousand_whole_lines(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    workers = [
        context.Process(target=run_appender, args=(str(tmp_path), n)) for n in range(PROCESSES)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=300)
        assert worker.exitcode == 0
    lines = [
        line
        for path in sorted((tmp_path / "ledger").rglob("*.jsonl"))
        for line in path.read_text().splitlines()
    ]
    assert len(lines) == PROCESSES * EACH
    parsed = [json.loads(line) for line in lines]  # a split line would not parse
    assert len({e["id"] for e in parsed}) == PROCESSES * EACH
    seen = {(n, i) for e in parsed for n, i in [map(int, e["summary"].split()[1:4:2])]}
    assert seen == {(n, i) for n in range(PROCESSES) for i in range(EACH)}
