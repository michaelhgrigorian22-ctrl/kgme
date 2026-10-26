"""Tests for Cowork's ruling on review cycle 3 of HANDOFF-0034, F1 and F6: the one read gate
(moved out of `tests/test_brief_review.py` by HANDOFF-0060 §3, unchanged).

Purpose: no brief module reads a file except through `brief_read.read_gated`; a pending intent
whose destination is now forbidden reads no bytes; a damaged brief is one intent and one
classified outcome.
Inputs: the brief modules' source; the seeded vault of `tests/brieftools.py`.
Outputs: pytest assertions.
Side effects: files and ledger lines under `tmp_path` only.
"""

import hashlib
import json
from pathlib import Path

import pytest
from briefreviewtools import closing, plant_intent
from brieftools import BRIEF, DATE, SETTINGS, read_recorded, run_brief, write_seed

from kgme import brief, brief_io, clean_fs

# Cycle 3: Cowork's ruling on F1 and F6 (one gated reader; one failure boundary)

BRIEF_MODULES = ("brief.py", "brief_read.py", "brief_io.py", "brief_reconcile.py")


READ_CALLS = {"read_text", "read_bytes", "read_regular_bytes", "load", "loads_file"}


@pytest.mark.blocking
def test_no_brief_module_reads_a_file_except_through_the_gate() -> None:
    """Every file read in the brief job is `brief_read.read_gated`, or the ledger's own
    readers; a call that opens or reads a path anywhere else fails this test."""
    import ast

    kgme_dir = Path(brief.__file__).parent
    stray: list[str] = []
    for name in BRIEF_MODULES:
        tree = ast.parse((kgme_dir / name).read_text())
        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            if func.name == "read_gated" or func.name.startswith("write_"):
                continue
            for call in [n for n in ast.walk(func) if isinstance(n, ast.Call)]:
                target = call.func
                called = (
                    target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
                )
                owner = getattr(target.value, "id", "") if isinstance(target, ast.Attribute) else ""
                if called in READ_CALLS or called == "open" or (owner == "os" and called == "read"):
                    where = f"{owner}.{called}" if owner else called
                    stray.append(f"{name}:{call.lineno} {func.name} calls {where}")
    assert stray == [], "\n".join(stray)


@pytest.mark.blocking
def test_a_pending_intent_whose_destination_is_now_forbidden_reads_no_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_seed(tmp_path)
    assert run_brief(base) == 0
    text = (base / read_recorded(base, "intent")[-1]["payload_ref"]).read_text()
    intent = plant_intent(base, DATE, text, hashlib.sha256(text.encode()).hexdigest())
    settings = json.loads(json.dumps(SETTINGS))
    settings["hooks"]["blocklist"] = [*settings["hooks"]["blocklist"], f"**/{DATE}.md"]
    opened: list[Path] = []
    real = clean_fs.read_regular_bytes

    def spy(root: Path, path: Path) -> bytes:
        opened.append(path)
        return real(root, path)

    monkeypatch.setattr(clean_fs, "read_regular_bytes", spy)
    assert brief_io.run_brief(DATE, False, base, settings) == 1
    assert base / BRIEF not in opened, "no byte of a forbidden destination is read"
    closed = closing(base, intent)
    assert len(closed) == 1 and closed[0]["class"] == "blocking"


@pytest.mark.blocking
@pytest.mark.parametrize(
    "damaged", ["# Brief 2026-10-08\n\nno frontmatter\n", "---\nid: [unclosed\n---\n\n# Brief\n"]
)
def test_a_damaged_brief_is_one_intent_and_one_classified_outcome(
    tmp_path: Path, damaged: str
) -> None:
    base = write_seed(tmp_path)
    (base / BRIEF).write_text(damaged)
    assert run_brief(base) == 1
    assert (base / BRIEF).read_text() == damaged, "the existing brief is preserved"
    recorded = read_recorded(base)
    intents = [e for e in recorded if e["kind"] == "intent"]
    outcomes = [e for e in recorded if e["kind"] == "outcome"]
    assert len(intents) == 1 and len(outcomes) == 1
    assert outcomes[0]["ref"] == intents[0]["id"] and outcomes[0]["class"] == "blocking"
