"""Shared pytest setup.

Purpose: a suite run from under a conductor (a `kgme` command Hermes started, HANDOFF-0073)
inherits `KGME_CONDUCTOR`, which marks the summaries the event writers produce; every test
starts without it, and the tests of the mark set it themselves.
Inputs: the process environment.
Outputs: none.
Side effects: `KGME_CONDUCTOR` unset for each test, restored after it.
"""

import pytest


@pytest.fixture(autouse=True)
def _no_conductor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KGME_CONDUCTOR", raising=False)
