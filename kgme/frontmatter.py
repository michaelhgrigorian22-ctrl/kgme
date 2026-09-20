"""Frontmatter as the author wrote it: the block between the `---` fences, loaded strictly.

Purpose: the one YAML entry point of the validator (HANDOFF-0031). `yaml.safe_load` would
construct timestamps into objects and keep the last of two equal keys; both hide what the
schema has to judge, so this loader leaves instants as strings and refuses a duplicated key.
Inputs: a note's text.
Outputs: the frontmatter mapping and the body, or a ValueError naming what is wrong.
Side effects: none.

Before anything is constructed, the composed node tree is walked and a key that appears twice
in one mapping, bare, quoted, in flow style, spelled through an alias, or inside a merge
source, is refused where YAML would silently keep the last value. A note's own key may still
override a merged one, which is what a merge is for.
"""

import re

import yaml

FRONTMATTER = re.compile(r"\A---\r?\n(?P<block>.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
TIMESTAMP_TAG = "tag:yaml.org,2002:timestamp"
MERGE_TAG = "tag:yaml.org,2002:merge"


class _Loader(yaml.SafeLoader):
    """`SafeLoader` that keeps timestamps as the strings the author typed."""


_Loader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag != TIMESTAMP_TAG]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(block: str) -> object:
    """`yaml.safe_load` with instants kept as text and a duplicated key refused wherever it sits.

    The check walks the composed node tree before construction, so it sees every mapping as
    written: a merge source (`<<`) is checked as a mapping of its own, and a note's own key may
    still override a merged one, which is what a merge is for. Raises a `yaml.YAMLError`.
    """
    loader = _Loader(block)
    try:
        node = loader.get_single_node()
        if node is None:
            return None
        _refuse_duplicates(loader, node)
        return loader.construct_document(node)
    finally:
        loader.dispose()


def _refuse_duplicates(loader: yaml.SafeLoader, node: yaml.Node) -> None:
    """Raise if any mapping under `node` names the same constructed key twice."""
    if isinstance(node, yaml.SequenceNode):
        for item in node.value:
            _refuse_duplicates(loader, item)
        return
    if not isinstance(node, yaml.MappingNode):
        return
    seen: list[object] = []
    for key_node, value_node in node.value:
        if key_node.tag == MERGE_TAG:
            sources = (
                value_node.value if isinstance(value_node, yaml.SequenceNode) else [value_node]
            )
            for source in sources:
                _refuse_duplicates(loader, source)
            continue
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        seen.append(key)
        _refuse_duplicates(loader, value_node)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """The YAML block between the opening and closing `---`, and the body; None if absent."""
    match = FRONTMATTER.match(text)
    if not match:
        return None
    return match["block"], text[match.end() :]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """The frontmatter as a dict and the body. Raises ValueError with the reason."""
    parts = split_frontmatter(text)
    if parts is None:
        raise ValueError("no frontmatter block")
    block, body = parts
    try:
        data = load_yaml(block)
    except yaml.YAMLError as error:
        raise ValueError(f"frontmatter is not valid YAML: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data, body
