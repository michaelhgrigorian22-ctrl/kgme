"""CDH-0003: hand-placed symbols must retain the approved canonical SVG bodies.

CDH-0007: the active-runs tray (Tray.dc.html) carries a second copy of the
symbols and of board 10's chibi CSS; both are held to the same sources.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs/design/cockpit-v0"
ACTORS = ("builder", "reviewer", "arbiter", "guard", "scribe", "michou", "stranger")
BOARDS = ("Sprites.dc.html", "Tray.dc.html")


def normalize(body: str) -> str:
    """Strip outer whitespace and indentation between tags only.

    Text, attributes, path data, style declarations and attribute order stay exact.
    The SVG root is deliberately excluded: its viewport and material roles are
    applied to each native specimen, while its children live once in a symbol.
    """
    return re.sub(r">\s+<", "><", body.strip())


def chibi_css(board: str) -> str:
    """Board 10's shared chibi stylesheet: from its opening comment to the last keyframes."""
    start = board.index("/* Only the SVG body is copied into each symbol.")
    end = board.index("@keyframes chibi-halo{")
    end = board.index("\n", end) + 1
    return board[start:end]


@pytest.mark.parametrize("board_name", BOARDS)
@pytest.mark.parametrize("actor", ACTORS)
def test_native_symbol_matches_canonical_svg(board_name: str, actor: str) -> None:
    board = (DESIGN / board_name).read_text()
    svg = (DESIGN / "chibi" / f"{actor}.svg").read_text()
    root = re.fullmatch(r"\s*<svg\b[^>]*>(.*)</svg>\s*", svg, re.DOTALL)
    assert root is not None, f"{actor}: expected one canonical SVG root"
    symbols = re.findall(
        rf'<symbol\b[^>]*\bid="chibi-{actor}"[^>]*>(.*?)</symbol>',
        board,
        re.DOTALL,
    )
    assert len(symbols) == 1, f"{board_name} {actor}: expected exactly one native symbol"
    assert normalize(symbols[0]) == normalize(root.group(1))


@pytest.mark.parametrize("board_name", BOARDS)
@pytest.mark.parametrize("actor", ACTORS)
def test_native_sticker_materials_match_canonical_root(board_name: str, actor: str) -> None:
    """Root palettes are outside the body comparison but must not silently drift."""
    board = (DESIGN / board_name).read_text()
    svg = (DESIGN / "chibi" / f"{actor}.svg").read_text()
    root_style = re.search(r'<svg\b[^>]*\bstyle="([^"]+)"', svg)
    board_style = re.search(rf"\.actor-{actor}\{{([^}}]+)\}}", board)
    assert root_style is not None and board_style is not None
    assert board_style.group(1) == root_style.group(1)


def test_tray_chibi_css_matches_sprites() -> None:
    """The tray's copy of the chibi stylesheet is board 10's, byte for byte."""
    sprites = chibi_css((DESIGN / "Sprites.dc.html").read_text())
    tray = chibi_css((DESIGN / "Tray.dc.html").read_text())
    assert sprites.count("@keyframes") == 15
    assert tray == sprites


def test_tray_portrait_crops_match_canonical_svgs() -> None:
    """The tray's head crops are the data-portrait values of the canonical SVGs."""
    tray = (DESIGN / "Tray.dc.html").read_text()
    for actor in ACTORS:
        svg = (DESIGN / "chibi" / f"{actor}.svg").read_text()
        portrait = re.search(r'\bdata-portrait="([^"]+)"', svg)
        assert portrait is not None, f"{actor}: canonical SVG declares no data-portrait"
        assert f"{actor}: '{portrait.group(1)}'" in tray, (
            f"{actor}: tray crop differs from data-portrait"
        )
