"""CDH-0032: static headroom and stacking checks for the eleven design boards.

This is a conservative palette contract, not a replacement for the Chromium and
Safari composited-pixel acceptance pass. Every declared normal text colour is
checked against every text surface present in that board, including focus and
hover tints. Colours in JS-generated style strings are included. New colours or
surfaces require classification here instead of silently escaping the gate.

The station is deliberately outside this change's static headroom contract:
CDH-0032 requires it to remain byte-identical and checks its painted contrast
separately. Artwork paint, empty swatches and disabled controls are not text.
"""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import pytest

DESIGN = Path(__file__).resolve().parents[1] / "docs/design/cockpit-v0"
BOARDS = tuple(sorted(path.name for path in DESIGN.glob("*.dc.html")))
TEXT_SURFACES = {
    "#0a0c10",  # ground
    "#11151c",  # panel
    "#0e1a22",  # focused row / active key
    "#0f141b",  # hovered row
    "#1c0f16",  # blocking focus
    "#1a150c",  # pending focus
    "#0e1218",  # key frame
    "#171c22",  # disconnect band
    "#161c24",  # future buffer
}
TEXT_COLOURS = {"#cfe6ef", "#7a8d9b", "#39d0ff", "#ff3d7f", "#ffb02e", "#4de38a", "#a3b0b8"}
DISABLED = "#3a4650"
INVERSE = "#0a0c10"
# These backgrounds are bars, rules or empty palette samples, never text surfaces.
GRAPHIC_BACKGROUNDS = {"#141b22", "#1e2a33", "#6f8290"} | TEXT_COLOURS
OVERLAYS = {"frame", "scan", "vig", "tx", "ty", "sweep", "flood", "static"}
COLOUR = re.compile(r"(?<![-\w])color\s*:\s*(#[\da-f]{3,8}|[a-z][\w()-]*)", re.I)
BACKGROUND = re.compile(r"(?<![-\w])background(?:-color)?\s*:\s*(#[\da-f]{3,8})", re.I)
VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def clean(source: str) -> str:
    return re.sub(r"/\*.*?\*/", "", source, flags=re.S)


def declarations(body: str) -> dict[str, str]:
    return {
        match.group(1).strip(): match.group(2).strip()
        for match in re.finditer(r"(?:^|;)\s*([\w-]+)\s*:\s*([^;]+)", body)
    }


def rules(source: str) -> list[tuple[str, dict[str, str]]]:
    result = []
    for style in re.findall(r"<style\b[^>]*>(.*?)</style>", clean(source), re.S):
        for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", style):
            for selector in rule.group(1).split(","):
                result.append((selector.strip(), declarations(rule.group(2))))
    return result


def luminance(colour: str) -> float:
    channels = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return sum(
        value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True)
    )


def contrast(foreground: str, background: str) -> float:
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    parent: "Node | None" = None
    text: str = ""
    children: list["Node"] = field(default_factory=list)

    def ancestors(self):
        node = self
        while node is not None:
            yield node
            node = node.parent

    def disabled(self) -> bool:
        return any(
            (
                node.tag in {"button", "input", "select", "textarea", "fieldset"}
                and "disabled" in node.attrs
            )
            or node.attrs.get("aria-disabled") == "true"
            for node in self.ancestors()
        )

    def all_text(self) -> str:
        return self.text + "".join(child.all_text() for child in self.children)


class Markup(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {})
        self.current = self.root
        self.nodes: list[Node] = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.current)
        self.current.children.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for node in self.current.ancestors():
            if node.tag == tag:
                self.current = node.parent or self.root
                break

    def handle_data(self, data):
        self.current.text += data


def simple_selector_matches(node: Node, selector: str) -> bool:
    """Match the graphic rules' simple descendant selectors, failing closed.

    Literal class tokens are checked here. Runtime-generated classes and cascade
    effects remain part of the required browser sweep. Complex future graphic
    selectors need explicit proof; this deliberately does not implement CSS.
    """
    tokens = selector.split()
    assert tokens and all(re.fullmatch(r"[\w.#-]+", token) for token in tokens), (
        selector,
        "Graphic background selector needs a static text-free proof",
    )

    def matches(candidate: Node, token: str) -> bool:
        tag = re.match(r"^[\w-]+", token)
        if tag and candidate.tag != tag.group():
            return False
        identifiers = re.findall(r"#([\w-]+)", token)
        if identifiers and candidate.attrs.get("id") not in identifiers:
            return False
        classes = candidate.attrs.get("class") or ""
        required = set(re.findall(r"\.([\w-]+)", token))
        return required <= set(classes.split())

    if not matches(node, tokens[-1]):
        return False
    ancestor = node.parent
    for token in reversed(tokens[:-1]):
        while ancestor is not None and not matches(ancestor, token):
            ancestor = ancestor.parent
        if ancestor is None:
            return False
        ancestor = ancestor.parent
    return True


def assert_graphic_is_text_free_or_inverse(board: str, node: Node, background: str) -> None:
    """A bright swatch or dark rule is not a blanket contrast exemption."""
    if node.text.strip():
        foreground = declarations(node.attrs.get("style") or "").get("color", "").lower()
        assert foreground == INVERSE and contrast(foreground, background) >= 4.8, (
            board,
            node.tag,
            node.attrs,
            "Text on a graphic background needs explicit verified inverse colour",
        )
    for child in node.children:
        assert_graphic_is_text_free_or_inverse(board, child, background)


@pytest.mark.parametrize("board", BOARDS)
def test_every_declared_text_token_has_rendering_headroom(board):
    source = clean((DESIGN / board).read_text())
    colours = {colour.lower() for colour in COLOUR.findall(source)}
    assert colours <= TEXT_COLOURS | {DISABLED, INVERSE, "inherit"}, (
        board,
        "Unclassified text token",
        colours - TEXT_COLOURS - {DISABLED, INVERSE, "inherit"},
    )
    backgrounds = {colour.lower() for colour in BACKGROUND.findall(source)}
    assert backgrounds <= TEXT_SURFACES | GRAPHIC_BACKGROUNDS, (
        board,
        "Unclassified background",
        backgrounds - TEXT_SURFACES - GRAPHIC_BACKGROUNDS,
    )
    surfaces = backgrounds & TEXT_SURFACES
    assert {"#0a0c10", "#11151c"} <= surfaces, (board, "Missing ground or panel coverage")
    for foreground in colours & TEXT_COLOURS:
        for background in surfaces:
            assert contrast(foreground, background) >= 4.8, (
                board,
                foreground,
                background,
                contrast(foreground, background),
            )


@pytest.mark.parametrize("board", BOARDS)
def test_graphic_backgrounds_cannot_be_reused_as_unchecked_text_surfaces(board):
    source = (DESIGN / board).read_text()
    markup = Markup(source)
    for node in markup.nodes:
        props = declarations(node.attrs.get("style") or "")
        background = props.get("background-color", props.get("background", "")).lower()
        if background in GRAPHIC_BACKGROUNDS:
            assert_graphic_is_text_free_or_inverse(board, node, background)
    for selector, props in rules(source):
        background = props.get("background-color", props.get("background", "")).lower()
        if background not in GRAPHIC_BACKGROUNDS:
            continue
        for node in markup.nodes:
            if simple_selector_matches(node, selector):
                assert_graphic_is_text_free_or_inverse(board, node, background)


@pytest.mark.parametrize("board", BOARDS)
def test_disabled_grey_and_inverse_text_have_only_their_intended_uses(board):
    source = (DESIGN / board).read_text()
    # A low-contrast rule may not be inherited by ordinary text. All current
    # disabled specimens declare grey inline, where their ancestry is provable.
    for selector, props in rules(source):
        colour = props.get("color", "").lower().replace("!important", "").strip()
        assert colour not in {DISABLED, INVERSE}, (board, selector, colour)
    seen_special = {DISABLED: 0, INVERSE: 0}
    for node in Markup(source).nodes:
        props = declarations(node.attrs.get("style") or "")
        colour = props.get("color", "").lower()
        if colour == DISABLED:
            assert node.disabled(), (board, node.tag, node.attrs, "Grey text is not disabled")
            seen_special[DISABLED] += 1
        if colour == INVERSE:
            background = props.get("background-color", props.get("background", "")).lower()
            assert background in TEXT_COLOURS, (
                board,
                node.attrs,
                "Inverse text needs its own surface",
            )
            assert contrast(colour, background) >= 4.8
            seen_special[INVERSE] += 1
    # Also catches a new grey/dark colour in a JS-generated style string that
    # cannot be proven disabled or paired by the source markup above.
    for colour, count in seen_special.items():
        assert sum(value.lower() == colour for value in COLOUR.findall(clean(source))) == count, (
            board,
            colour,
            "A special colour escaped its verified inline usage",
        )


@pytest.mark.parametrize("board", BOARDS)
def test_surface_overlays_stay_below_every_text_layer(board):
    source = (DESIGN / board).read_text()
    css = rules(source)
    markup = Markup(source)
    hud = any("hud" in (node.attrs.get("class") or "").split() for node in markup.nodes)
    hud_props = {}
    panel_props = {}
    for selector, props in css:
        if selector == ".hud":
            hud_props.update(props)
        if selector == ".pnl":
            panel_props.update(props)
    if hud:
        assert hud_props.get("isolation") == "isolate", (
            board,
            "Negative decoration needs an isolated ground",
        )
    for node in markup.nodes:
        if not hud:
            break  # Component miniatures use backgrounds, not screen overlays.
        classes = set((node.attrs.get("class") or "").split())
        for overlay in classes & OVERLAYS:
            assert not node.all_text().strip(), (board, overlay, "Decoration contains text")
            layer = None
            for selector, props in css:
                if re.search(rf"(?:^|[ >])\.{overlay}$", selector) and "z-index" in props:
                    layer = props["z-index"]
            inline = declarations(node.attrs.get("style") or "")
            layer = inline.get("z-index", layer)
            assert layer is not None and int(layer.replace("!important", "").strip()) < 0, (
                board,
                overlay,
                layer,
                "Decoration must be below the auto/0 text plane",
            )
    for selector, props in css:
        layer = props.get("z-index", "auto").replace("!important", "").strip()
        if layer == "auto" or int(layer) >= 0:
            continue
        if "::before" in selector or "::after" in selector:
            # Corner brackets must remain empty decoration, never generated words.
            content = next(
                (
                    candidate["content"]
                    for target, candidate in css
                    if target == selector and "content" in candidate
                ),
                None,
            )
            assert content in {'""', "''"}, (
                board,
                selector,
                "Negative pseudo-element carries text",
            )
            assert panel_props.get("isolation") == "isolate", (
                board,
                selector,
                "Corner decoration needs an isolated panel ground",
            )
        else:
            assert any(re.search(rf"(?:^|[ >])\.{overlay}$", selector) for overlay in OVERLAYS), (
                board,
                selector,
                "A text-bearing layer was put below the text plane",
            )
    for node in markup.nodes:
        if not node.text.strip() or node.tag in {"script", "style", "title"}:
            continue
        for ancestor in node.ancestors():
            layer = declarations(ancestor.attrs.get("style") or "").get("z-index", "auto")
            assert layer == "auto" or int(layer) >= 0, (
                board,
                ancestor.attrs,
                "Text inherits a negative layer",
            )
