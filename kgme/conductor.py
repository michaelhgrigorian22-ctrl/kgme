"""Which conductor started a run: `KGME_CONDUCTOR` on the events `kgme` writes (HANDOFF-0073 §3).

Purpose: Hermes's terminal sets `KGME_CONDUCTOR=hermes`; the `session`, `loop`, `crew` and
`agent:run` events a `kgme` command writes under it carry `[conductor: hermes]` at the end of
their summary, so `grep 'conductor: hermes'` over the ledger finds every run Hermes started.
ADR-019's field set is closed, so the mark rides in the summary (clipped so the mark itself
always survives the 200-character cap), and in the run's payload record where one is written
(`conductor`). A value that is not a short kebab-case name is ignored, never written: the
variable is attribution, not a channel into the ledger.
Inputs: a summary; the environment (`os.environ` unless one is given).
Outputs: the summary with its mark; the conductor's name or None.
Side effects: none; `name` and `tag` read the process environment when none is passed.
"""

import os
import re
from collections.abc import Mapping

from kgme.events import MAX_SUMMARY_CHARS

ENV = "KGME_CONDUCTOR"
NAME = re.compile(r"^[a-z][a-z0-9-]{0,31}$")


def name(environ: Mapping[str, str] | None = None) -> str | None:
    """The conductor named in the environment, or None when unset or not a kebab-case name."""
    value = (os.environ if environ is None else environ).get(ENV, "").strip()
    return value if NAME.fullmatch(value) else None


def mark(conductor: str) -> str:
    """Pure: the mark a summary carries."""
    return f" [conductor: {conductor}]"


def tag(summary: str, environ: Mapping[str, str] | None = None) -> str:
    """`summary` with the conductor's mark when one is set, cut so the whole line stays within
    the cap and the mark is never the part cut off; unchanged when no conductor is set."""
    conductor = name(environ)
    if conductor is None:
        return summary
    suffix = mark(conductor)
    room = MAX_SUMMARY_CHARS - len(suffix)
    body = summary if len(summary) <= room else summary[: room - 1] + "…"
    return body + suffix


def record(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """The payload field for a run's record: `{"conductor": name}`, or empty when unset."""
    conductor = name(environ)
    return {"conductor": conductor} if conductor else {}
