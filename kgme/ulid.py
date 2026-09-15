"""ULIDs: sortable 26-character ids, monotonic within a process (ADR-019 §5).

Purpose: one id generator for ledger events and agent-written notes (`schema-v1.md`, `id`).
Inputs: the clock and `os.urandom`; an explicit millisecond timestamp for tests.
Outputs: a 26-character Crockford base32 string: 10 characters of time, 16 of randomness.
Side effects: none on disk. The generator keeps the last id it issued so two ids minted in
the same millisecond still sort in issue order; that is the one piece of state in this
module and a lock protects it. No dependency: the ULID spec fits in the lines below.
"""

import os
import threading
import time

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
RANDOM_BITS = 80


def _encode(number: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(ALPHABET[number & 31])
        number >>= 5
    return "".join(reversed(chars))


class Generator:
    """Issues ULIDs that never sort backwards within this process."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_ms = -1
        self._last_random = 0

    def new(self, now_ms: int | None = None) -> str:
        """A fresh ULID. `now_ms` overrides the clock for tests; it must not run backwards."""
        ms = int(time.time() * 1000) if now_ms is None else now_ms
        with self._lock:
            if ms <= self._last_ms:
                ms = self._last_ms
                random = self._last_random + 1
                if random >= 1 << RANDOM_BITS:
                    ms += 1
                    random = int.from_bytes(os.urandom(10), "big")
            else:
                random = int.from_bytes(os.urandom(10), "big")
            self._last_ms, self._last_random = ms, random
        return _encode(ms, 10) + _encode(random, 16)


_default = Generator()


def new_ulid(now_ms: int | None = None) -> str:
    """Module-level convenience over one shared generator, so monotonicity holds process-wide."""
    return _default.new(now_ms)
