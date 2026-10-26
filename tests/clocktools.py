"""A clock the test controls (HANDOFF-0060 §1): every wall-clock read in `kgme`, frozen at once.

Purpose: a test that takes "today" at import and compares it with a value the code takes
later fails when a run crosses midnight. `freeze` pins every place `kgme` reads the wall
clock (the event timestamp, the ULID time, `kgme capture`'s and `kgme daily`'s `now`, the
brief's clock) to one instant, so "today" in the test and in the code are the same day by
construction. `FROZEN` is one second before midnight in the vault's zone, the moment the
failure needed; `git_dates` dates a test's commits from the same instant.
Inputs: pytest's `monkeypatch`; an aware instant.
Outputs: the instant; environment entries for git.
Side effects: patches module attributes for the duration of one test.
"""

from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from brieftools import SETTINGS

from kgme import brief_read, capture_io, daily_io, events, ulid

ZONE = ZoneInfo(SETTINGS["brief"]["timezone"])
FROZEN = datetime(2026, 10, 22, 23, 59, 59, tzinfo=ZONE)
CLOCKED = (events, capture_io, daily_io, brief_read)


def freeze(monkeypatch, at: datetime = FROZEN) -> datetime:
    """Effect: every wall-clock read in `kgme` answers `at` for the rest of the test."""

    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return at.astimezone(tz) if tz is not None else at

    for module in CLOCKED:
        monkeypatch.setattr(module, "datetime", Frozen)
    monkeypatch.setattr(ulid, "time", SimpleNamespace(time=lambda: at.timestamp()))
    return at


def git_dates(at: datetime = FROZEN) -> dict[str, str]:
    """The environment that dates a git commit at `at`, author and committer."""
    stamp = at.isoformat()
    return {"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
