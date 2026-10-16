"""Helpers shared by the brief tests (`tests/test_brief.py`).

Purpose: seed a vault under `tmp_path` (reminders, tasks, a daily note by Michou's headings,
the friction log, a brief folder, an empty ledger), run the job against it, and read back
what the ledger and the artefact hold.
Inputs: `kgme.toml`.
Outputs: functions and the fixed day the tests brief.
Side effects: `write_seed` creates files under `tmp_path`; `run_brief` runs the job there;
`read_recorded` reads that checkout's ledger.
"""

from pathlib import Path

from kgme import brief_io, config, ledger

SETTINGS = config.read_config()
DATE = "2026-10-08"
BRIEF = Path("memory/agent/brief") / f"{DATE}.md"


def note(kind: str, ident: str, status: str, body: str, **extra: object) -> str:
    fields: dict[str, object] = {
        "id": ident,
        "type": kind,
        "created": "2026-10-01T09:00:00-07:00",
        "modified": "2026-10-01T09:00:00-07:00",
        "status": status,
        "tier": 2,
        "source": "stated",
        "author": "human",
    }
    fields.update(extra)
    lines = [f"{k}: {'null' if v is None else v}" for k, v in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n\n" + body + "\n"


DAILY = f"""---
id: 20261008T070000
type: daily
date: {DATE}
created: {DATE}T07:00:00-07:00
modified: {DATE}T07:00:00-07:00
status: open
tier: 2
source: stated
author: human
---

# Thursday 8 October 2026

## Today
<!-- what happened, any project; one line each is enough -->
- wrote the sync hook

## Learned
- uv falls back to the active environment

## Problems and solutions

## Tomorrow
- seed the vault

## Friction
- 2026-10-08 20:00 — reviewer out of quota — KGME should have known the window
"""

FRICTION = """---
id: FRICTION-LOG
type: note
created: 2026-09-09T19:55:00-07:00
modified: 2026-09-09T19:55:00-07:00
status: active
tier: 2
source: stated
author: human
---

# Friction log

- 2026-10-06 — 10:00 — before the previous brief — nothing
- 2026-10-07 — 10:00 — on the previous brief's day — kept, inclusive
- 2026-10-08 — 10:00 — today — shown
"""


def write_seed(tmp_path: Path, daily: bool = True, items: bool = True) -> Path:
    base = tmp_path / "vault"
    files = {"memory/inbox/friction-log.md": FRICTION}
    if daily:
        files[f"memory/daily/{DATE}.md"] = DAILY
    if items:
        files.update(
            {
                "memory/notes/call-reader.md": note(
                    "reminder",
                    "20261001T090001",
                    "open",
                    "# Call the reader",
                    due="2026-10-07T09:00:00-07:00",
                    repeat=None,
                    channel="phone",
                ),
                "memory/notes/done-reminder.md": note(
                    "reminder",
                    "20261001T090002",
                    "done",
                    "# Already done",
                    due="2026-10-07T09:00:00-07:00",
                    repeat=None,
                    channel="phone",
                ),
                "memory/notes/thesis-chapter.md": note(
                    "task",
                    "20261001T090003",
                    "doing",
                    "# Chapter 2 draft",
                    due=f"{DATE}T18:00:00-07:00",
                    project='"[[thesis]]"',
                    priority=1,
                ),
                "memory/notes/costing-homework.md": note(
                    "task",
                    "20261001T090004",
                    "open",
                    "# Costing homework",
                    due="2026-10-09T09:00:00-07:00",
                    project='"[[school]]"',
                    priority=2,
                ),
                "memory/notes/dropped.md": note(
                    "task",
                    "20261001T090005",
                    "dropped",
                    "# Dropped",
                    due=None,
                    project=None,
                    priority=3,
                ),
                "memory/notes/plain.md": note(
                    "note", "20261001T090006", "active", "# A plain note"
                ),
                "memory/agent/machine-task.md": note(
                    "task",
                    "20261001T090007",
                    "open",
                    "# Machine task",
                    due=None,
                    project=None,
                    priority=3,
                    author="kgme",
                ),
                "memory/agent/brief/2026-10-07.md": note(
                    "note",
                    "01K0000000000000000000PREV",
                    "active",
                    "# Brief 2026-10-07",
                    author="kgme",
                    source="inferred",
                    sources='["FRICTION-LOG"]',
                ),
            }
        )
    for rel, text in files.items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text, encoding="utf-8")
    (base / "memory" / "templates").mkdir()
    (base / "logs" / "ledger").mkdir(parents=True)
    (base / ".git").mkdir()  # `kgme clean` runs only from a checkout root (0033, cycle 3 F9)
    return base


def run_brief(base: Path, *flags: str, date: str = DATE) -> int:
    """`kgme brief` on the seeded vault by the direct call: the commands take no path, so a
    seed is reached only this way (HANDOFF-0033 F9, applied to the brief)."""
    return brief_io.run_brief(date, "--dry-run" in flags, base, SETTINGS)


def read_recorded(base: Path, kind: str | None = None) -> list[dict]:
    found = ledger.read(ledger.read_base_dirs(SETTINGS, base), stream="ledger")
    return [e for e in found if e["job"] == "brief" and (kind is None or e["kind"] == kind)]


def frontmatter(text: str) -> dict:
    data, _ = brief_io_parse(text)
    return data


def brief_io_parse(text: str) -> tuple[dict, str]:
    from kgme.frontmatter import parse_frontmatter

    return parse_frontmatter(text)
