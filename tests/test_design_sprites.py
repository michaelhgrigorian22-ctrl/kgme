"""CDH-0003: hand-placed symbols must retain the approved canonical SVG bodies."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs/design/cockpit-v0"
ACTORS = ("builder", "reviewer", "arbiter", "guard", "scribe", "michou", "stranger")


def normalize(body: str) -> str:
    """Strip outer whitespace and indentation between tags only.

    Text, attributes, path data, style declarations and attribute order stay exact.
    The SVG root is deliberately excluded: its viewport and material roles are
    applied to each native specimen, while its children live once in a symbol.
    """
    return re.sub(r">\s+<", "><", body.strip())


@pytest.mark.parametrize("actor", ACTORS)
def test_native_symbol_matches_canonical_svg(actor: str) -> None:
    board = (DESIGN / "Sprites.dc.html").read_text()
    svg = (DESIGN / "chibi" / f"{actor}.svg").read_text()
    root = re.fullmatch(r"\s*<svg\b[^>]*>(.*)</svg>\s*", svg, re.DOTALL)
    assert root is not None, f"{actor}: expected one canonical SVG root"
    symbols = re.findall(
        rf'<symbol\b[^>]*\bid="chibi-{actor}"[^>]*>(.*?)</symbol>',
        board,
        re.DOTALL,
    )
    assert len(symbols) == 1, f"{actor}: expected exactly one native symbol"
    assert normalize(symbols[0]) == normalize(root.group(1))


@pytest.mark.parametrize("actor", ACTORS)
def test_native_sticker_materials_match_canonical_root(actor: str) -> None:
    """Root palettes are outside the body comparison but must not silently drift."""
    board = (DESIGN / "Sprites.dc.html").read_text()
    svg = (DESIGN / "chibi" / f"{actor}.svg").read_text()
    root_style = re.search(r'<svg\b[^>]*\bstyle="([^"]+)"', svg)
    board_style = re.search(rf"\.actor-{actor}\{{([^}}]+)\}}", board)
    assert root_style is not None and board_style is not None
    assert board_style.group(1) == root_style.group(1)
