"""The cheap lane's acceptance fixture (HANDOFF-0053): a function with one bug, which a cheap
session fixes in its export so `toy_red.py` exits 0. The fix comes home as a patch and is
never committed here."""


def add(a: int, b: int) -> int:
    """The sum of `a` and `b`."""
    return a - b
