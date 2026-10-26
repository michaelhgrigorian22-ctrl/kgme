"""Helpers for the schema validator's tests (HANDOFF-0031; moved out of `tests/test_lint.py` by
HANDOFF-0060 §3, unchanged).

Purpose: the fixture vault's notes, one inline note, and the rules a list of findings names.
Inputs: `tests/fixtures/vault/`.
Outputs: notes and rule names.
Side effects: none; reads only.
"""

from pathlib import Path

from kgme import lint, vault

FIXTURES = Path(__file__).parent / "fixtures" / "vault"


def fixture_notes(roots: list[Path] | None = None) -> list[tuple[str, str]]:
    return vault.read_notes(
        roots or [FIXTURES / "memory", FIXTURES / "docs"],
        [FIXTURES / "memory" / "templates"],
        (".obsidian",),
        FIXTURES,
    )


def note(**fields: object) -> str:
    """A valid human note under memory/notes with any field overridden or added."""
    base: dict[str, object] = {
        "id": "20260915T120000",
        "type": "note",
        "created": "2026-09-15T12:00:00-07:00",
        "modified": "2026-09-15T12:00:00-07:00",
        "status": "active",
        "tier": 2,
        "source": "stated",
        "author": "human",
    }
    base.update(fields)
    lines = [f"{k}: {'null' if v is None else v}" for k, v in base.items() if v != "__omit__"]
    return "---\n" + "\n".join(lines) + "\n---\nbody\n"


def rules(text: str, rel_path: str = "memory/notes/x.md") -> list[tuple[str, str]]:
    return [(f.rule, f.cls) for f in lint.lint_note(text, rel_path, {})]
