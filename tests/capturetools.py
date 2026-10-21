"""Helpers shared by the capture and daily tests (`tests/test_capture.py`, `tests/test_daily.py`).

Purpose: seed a checkout-shaped vault under `tmp_path` (the brief's seed, the real templates,
an open handoff and a done one, a report), run either job against it, and read back what its
ledger holds.
Inputs: `kgme.toml`, `memory/templates/`.
Outputs: functions, the fixed clock the capture tests run at, the zone.
Side effects: `write_vault` creates files under `tmp_path`; `run_capture` and `run_daily` run
the jobs there; `read_job` reads that checkout's ledger.
"""

import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from brieftools import SETTINGS, write_seed

from kgme import capture_io, daily_io, ledger, paths

ZONE = ZoneInfo(SETTINGS["brief"]["timezone"])
THURSDAY = datetime(2026, 10, 15, 14, 30, tzinfo=ZONE)
HANDOFF_OPEN = """---
id: HANDOFF-0900
type: handoff
created: 2026-10-01T09:00:00-07:00
from: michou
to: claude-code
tier: 2
status: open
---

# Handoff 0900 — the open one
"""
HANDOFF_DONE = """---
id: HANDOFF-0899
type: handoff
created: 2026-10-01T09:00:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: {today}T10:00:00-07:00
report: docs/audit/report.md
---

# Handoff 0899 — the finished one
"""
REPORT = """---
id: AUDIT-0900
type: report
status: final
handoff: HANDOFF-0899
author: claude-code
source: stated
tier: 2
created: {today}T10:00:00-07:00
period: {today}
---

# What the finished one taught
"""


def write_vault(tmp_path: Path, today: str = "2026-10-15") -> Path:
    """The brief's seed plus the real templates, two handoffs, and a report of `today`."""
    base = write_seed(tmp_path)
    for template in (paths.root() / "memory" / "templates").glob("*.md"):
        shutil.copy(template, base / "memory" / "templates" / template.name)
    files = {
        "docs/handoff/open.md": HANDOFF_OPEN,
        "docs/handoff/done/done.md": HANDOFF_DONE.format(today=today),
        "docs/audit/report.md": REPORT.format(today=today),
    }
    for rel, text in files.items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text, encoding="utf-8")
    return base


def run_capture(
    base: Path,
    kind: str,
    words: str,
    due: str | None = None,
    now: datetime | None = THURSDAY,
    dry_run: bool = False,
) -> int:
    """`kgme capture` on the seeded vault by the direct call; the command takes no path."""
    return capture_io.run_capture(kind, words, due, base, SETTINGS, now, dry_run)


def run_daily(base: Path, date: str, dry_run: bool = False) -> int:
    return daily_io.run_daily(date, base, SETTINGS, None, dry_run)


def read_job(base: Path, job: str, kind: str | None = None) -> list[dict]:
    found = ledger.read(ledger.read_base_dirs(SETTINGS, base), stream="ledger")
    return [e for e in found if e["job"] == job and (kind is None or e["kind"] == kind)]
