"""The toy handoff's suite: one test, red until `add` adds (HANDOFF-0043 acceptance)."""

import importlib
import os


def test_add() -> None:
    assert importlib.import_module(os.environ["TOY_MODULE"]).add(2, 2) == 4
