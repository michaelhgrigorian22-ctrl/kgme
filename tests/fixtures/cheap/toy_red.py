"""The cheap lane's red command (HANDOFF-0053): `uv run --frozen pytest
tests/fixtures/cheap/toy_red.py`. Not named `test_*.py`, so `make check` never collects it;
pytest runs it when the command names it. It fails until `toy.py` is fixed."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("toy", Path(__file__).with_name("toy.py"))
toy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(toy)


@pytest.mark.blocking
def test_add_sums() -> None:
    assert toy.add(2, 3) == 5
