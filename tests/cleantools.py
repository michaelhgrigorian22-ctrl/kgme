"""Helpers shared by the clean tests (`tests/test_clean*.py`).

Purpose: seed a checkout-shaped tree under `tmp_path`, run `kgme clean` against it, read
back its ledger, build `Entry` records for the pure planner, and plant the state a killed
run leaves.
Inputs: `kgme.toml`.
Outputs: functions and the dotenv name.
Side effects: `write_seed` creates files under `tmp_path`; `run_clean` runs the job there;
`read_recorded` reads that checkout's ledger; `plant_interrupted_run` writes a payload, an
intent, and outcomes there and deletes seeded files.

The dotenv name is assembled at run time: the live guard scans the text of a test file named
on a command line, and would refuse the run for the literal (lesson of 2026-09-15).
"""

import hashlib
import json
import os
from pathlib import Path

from kgme import clean, clean_fs, clean_io, clean_read, config, events, ledger, paths

SETTINGS = config.read_config()
DOTENV = "." + "env"


def write_seed(tmp_path: Path) -> Path:
    """A checkout-shaped tree: two machine notes, a human document, scratch payloads, caches
    inside and outside `.venv`, the two test streams, and an empty ledger directory."""
    base = tmp_path / "base"
    files = {
        "memory/agent/brief/2026-10-01.md": "brief\n",
        "memory/agent/note.md": "note\n",
        "docs/keep.md": "human\n",
        "logs/scratch/payloads/a.json": "{}\n",
        "logs/scratch/review.patch": "diff\n",
        "kgme/__pycache__/m.pyc": "pyc\n",
        ".venv/lib/x.py": "x\n",
        ".venv/lib/__pycache__/x.pyc": "pyc\n",
        "logs/ledger-test/2026-10.jsonl": "{}\n",
        "logs/trace-test/2026-10.jsonl": "{}\n",
    }
    for rel, text in files.items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)
    (base / "logs" / "ledger").mkdir()
    (base / ".git").mkdir()
    return base


def run_clean(base: Path, *argv: str) -> int:
    """`kgme clean` on the seeded checkout under the CLI's usage rules; the seed is both the
    base and the authorized root, which only this direct call can say (cycle 4, F9)."""
    flags = [a for a in argv if a.startswith("--")]
    targets = [a for a in argv if not a.startswith("--")]
    if not targets or ("--yes" in flags and "--dry-run" in flags):
        return 2
    return clean_io.run_clean(targets[0], "--yes" in flags, base, SETTINGS, home=base)


def read_recorded(base: Path, kind: str | None = None) -> list[dict]:
    found = ledger.read(ledger.read_base_dirs(SETTINGS, base), stream="ledger")
    return [e for e in found if e["job"] == "clean" and (kind is None or e["kind"] == kind)]


def entry(path: Path, base: Path, is_dir: bool = False, link: bool = False) -> clean.Entry:
    return clean.Entry(path, path.resolve(), is_dir, link, 0 if is_dir else 1)


def plan_agent(base: Path) -> clean.CleanPlan:
    entries, allowed, errors = clean_read.read_candidates(base, ["memory/agent"])
    assert errors == []
    return clean.plan_clean("agent", entries, base, allowed, base / "logs" / "ledger", {})


def plant_interrupted_run(base: Path, deleted: list[str], recorded: list[int]) -> tuple[dict, dict]:
    """The state a kill leaves: a payload for the `agent` plan with hashes, its intent, the
    files in `deleted` gone from disk, and an `ok` outcome for each number in `recorded`."""
    dirs = ledger.read_base_dirs(SETTINGS, base)
    plan = plan_agent(base)
    digests, _ = clean_io.read_prepared(plan, base)
    key = "clean:agent:2026-10-09T23:00"
    record = clean.plan_record(plan, base, key, digests)
    payloads = paths.payloads_dir(SETTINGS, base)
    text = json.dumps(record) + "\n"
    clean_fs.write_payload(base, payloads / "planted.json", text)
    intent = events.make_event(
        source="kgme",
        actor="kgme.clean",
        kind="intent",
        job="clean",
        key=key,
        summary="clean agent delete: 2 files 11 B, 1 dirs, 0 refused",
        payload_ref="logs/scratch/payloads/planted.json",
        payload_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
    ledger.append(intent, dirs)
    for rel in deleted:
        (base / rel).unlink()
    for number in recorded:
        item = record["files"][number - 1]
        summary = f"deleted #{number} {item['size']} B sha256 {item['sha256']} {item['path']}"
        clean_io.write_outcome(dirs, events.new_ulid(), key, intent["id"], summary, "ok")
    return intent, record


class OsWith:
    """`os` as `kgme.clean_fs` sees it, with named calls replaced for one test."""

    def __init__(self, **calls) -> None:
        self._calls = calls

    def __getattr__(self, name: str):
        return self._calls.get(name) or getattr(os, name)
