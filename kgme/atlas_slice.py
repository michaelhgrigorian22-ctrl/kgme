"""Atlas slices, pure half: a task's neighbourhood as plain text under a budget (HANDOFF-0056).

Purpose: give any model the part of the atlas a task touches, without the whole map or a
first hour of exploring. Seeds are the files a handoff's `Outputs` names and any `--around`
paths (a folder seed takes the nodes under it); the slice is the seeds plus one step out,
ranked: the seeds themselves, the tests that import them, their importers, what they
import, then the readers, ADRs, and handoffs that name them, each rank sorted by path. It
is rendered as plain text, one block per node: its path, the line the atlas writes about
it, and its neighbours by path; truncated at a token budget (characters / 4), ending with a
line naming how many nodes were cut and from which ranks. A slice never names a path under
an excluded prefix (`memory/`, `logs/`, and the Tier 1 roots inside the tree, for every
model), whatever tree it was built from. The output is a function of its inputs alone.
Inputs: the atlas's `Node` records (`kgme.atlas.build_graph`), the seed entries, the
excluded prefixes, the budget.
Outputs: `Slice` records; the rendered text, its token estimate, and the number cut.
Side effects: none. Reading the tree is `kgme.atlas_read.run_slice`.
"""

import re
from dataclasses import dataclass
from fnmatch import fnmatchcase

from kgme.atlas import TICKED, Node, Source, expand, read_imports

RANKS = ("seed", "test", "importer", "import", "document")
CODE_KINDS = ("module", "job")
DOCUMENT_KINDS = ("reader", "adr", "handoff")
EXCLUDED = ("memory/", "logs/")
CHARS_PER_TOKEN = 4
LIST_CAP = 12  # a neighbour's lists, so one block cannot take the budget; a seed's are whole
WIKILINK = re.compile(r"\[\[([^\]|#]+)\]\]")


@dataclass(frozen=True)
class Entry:
    """One node of a slice, the rank that brought it in, and its rendered block."""

    rank: str
    path: str
    block: str


@dataclass(frozen=True)
class Edges:
    """The directed relations a slice ranks by: what each code or test node imports, read
    from its source (the atlas's links are undirected, and link a module back to its
    tests), and the files each document names (review cycle 2 F3, cycle 1 F4)."""

    imports: dict[str, set[str]]
    names: dict[str, set[str]]


@dataclass(frozen=True)
class Slice:
    """A rendered slice: its text, the token estimate of that text, and the nodes cut."""

    text: str
    tokens: int
    cut: int


def label(node: Node) -> str:
    """Pure: the path a node stands for: its file, a folder's `top/`, else its name."""
    if node.file:
        return node.file
    if node.kind == "folder":
        return node.name.removeprefix("folder-") + "/"
    return node.name


def is_excluded(path: str, excluded: tuple[str, ...]) -> bool:
    """Pure: whether `path` is under an excluded prefix (each ends in `/`)."""
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in excluded)


def read_seeds(entries: list[str], nodes: dict[str, Node]) -> list[str]:
    """Pure: the names of the nodes the seed entries name: the files named outright (a
    brace pattern expanded, a glob matched) first, sorted by path; then the nodes a folder
    entry (`dir/`) takes, sorted by path, so a named file is never cut for a folder's."""
    entries = [e for entry in entries for e in expand(entry)]
    named, under = set(), set()
    for node in nodes.values():
        path = node.file
        if not path:
            continue
        for entry in entries:
            if entry.endswith("/"):
                if entry == "./" or path.startswith(entry):  # `./`: the root, every node
                    under.add(node.name)
            elif fnmatchcase(path, entry) if ("*" in entry or "?" in entry) else path == entry:
                named.add(node.name)
    by_path = lambda names: sorted(names, key=lambda n: label(nodes[n]))  # noqa: E731
    return by_path(named) + by_path(under - named)


def read_document_refs(sources: list[Source], nodes: dict[str, Node]) -> dict[str, set[str]]:
    """Pure: for each reader, ADR, and handoff, the nodes whose files its text names in
    backticks anywhere (a brace pattern expanded), not only its `Outputs`; the atlas's own
    links do not carry these (review cycle 1 F4)."""
    files = {n.file: n.name for n in nodes.values() if n.file}
    refs: dict[str, set[str]] = {}
    for source in sources:
        name = files.get(source.path)
        if name is None or nodes[name].kind not in DOCUMENT_KINDS:
            continue
        named = {t for token in TICKED.findall(source.text) for t in expand(token)}
        targets = {files[t] for t in named if t in files and t != source.path}
        if targets:
            refs[name] = targets
    return refs


def read_edges(sources: list[Source], nodes: dict[str, Node]) -> Edges:
    """Pure: the slice's directed relations: each Python source's imports (parsed as the
    atlas parses them, never executed) that are nodes, tests included; a shell script's
    atlas links (the modules it runs); and each document's named files."""
    files = {n.file: n.name for n in nodes.values() if n.file}
    imports: dict[str, set[str]] = {}
    for source in sources:
        name = files.get(source.path)
        if name is None or nodes[name].kind not in (*CODE_KINDS, "test"):
            continue
        if source.path.endswith(".py"):
            found = {i for i in read_imports(source.text) if i in nodes and i != name}
        else:
            found = {link for link in nodes[name].links if nodes[link].kind in CODE_KINDS}
        imports[name] = {i for i in found if nodes[i].kind in (*CODE_KINDS, "test")}
    return Edges(imports, read_document_refs(sources, nodes))


def read_link_edges(nodes: dict[str, Node]) -> Edges:
    """Pure: edges from the atlas's links alone, for a graph with no sources: a code or test
    node's links to code nodes (a module's links to tests are back-links)."""
    return Edges(
        {
            n.name: {link for link in n.links if link in nodes and nodes[link].kind in CODE_KINDS}
            for n in nodes.values()
            if n.kind in (*CODE_KINDS, "test")
        },
        {},
    )


def read_neighbours(
    name: str, nodes: dict[str, Node], edges: Edges | None = None
) -> dict[str, list[str]]:
    """Pure: a node's neighbours one step out, by rank, as node names: the tests and the code
    that import it and what it imports, from the directed edges; the documents that link it
    or name it, and the ADRs it cites."""
    node = nodes[name]
    edges = edges or read_link_edges(nodes)
    importing = [n for n, targets in edges.imports.items() if name in targets and n != name]
    tests = [n for n in importing if nodes[n].kind == "test"]
    importers = [n for n in importing if nodes[n].kind in CODE_KINDS]
    if node.kind in DOCUMENT_KINDS:
        imports = [t for t in edges.names.get(name, ()) if t in nodes]  # the files it names
    else:
        imports = list(edges.imports.get(name, ()))
    pointing = [n for n in nodes.values() if name in n.links and n.name != name]
    documents = [n.name for n in pointing if n.kind in DOCUMENT_KINDS]
    documents += [d for d, targets in edges.names.items() if name in targets and d != name]
    documents += [link for link in node.links if link in nodes and nodes[link].kind == "adr"]
    by_path = lambda names: sorted(set(names), key=lambda n: label(nodes[n]))  # noqa: E731
    return {
        "test": by_path(tests),
        "importer": by_path(importers),
        "import": by_path(imports),
        "document": by_path(documents),
    }


def plain(line: str) -> str:
    """Pure: an atlas line with its wikilinks as paths: `[[docs/x]]` becomes `docs/x.md`."""
    return WIKILINK.sub(lambda m: f"{m[1]}.md", line)


def build_slice(
    nodes: dict[str, Node],
    seeds: list[str],
    excluded: tuple[str, ...],
    edges: Edges | None = None,
) -> list[Entry]:
    """Pure: the slice's entries in order: every seed, then each rank's neighbours of the
    seeds, each node once at its first rank, each rank sorted by path, excluded paths
    dropped everywhere, neighbour lists included."""
    allowed = {n for n in nodes if not is_excluded(label(nodes[n]), excluded)}
    seeds = [s for s in seeds if s in allowed]
    placed: dict[str, str] = {s: "seed" for s in seeds}
    around = {s: read_neighbours(s, nodes, edges) for s in seeds}
    for rank in RANKS[1:]:
        found = {n for s in seeds for n in around[s][rank] if n in allowed}
        for name in sorted(found - set(placed), key=lambda n: label(nodes[n])):
            placed[name] = rank
    # the seeds in their own order (named files, then a folder's), then each rank by path
    return [
        Entry(rank, label(nodes[name]), render_block(name, rank, nodes, allowed, edges))
        for name, rank in placed.items()
    ]


def render_block(
    name: str,
    rank: str,
    nodes: dict[str, Node],
    allowed: set[str],
    edges: Edges | None = None,
) -> str:
    """Pure: one node's block: its path and rank, the atlas's line, its neighbours by path."""
    node = nodes[name]
    lines = [f"## {label(node)} ({rank})", plain(node.line)]
    code = node.kind in (*CODE_KINDS, "test")
    titles = {
        "test": "tests",
        "importer": "imported by",
        "import": "imports" if code else "names",  # for a document, the code it names
        "document": "named by",
    }
    for key, names in read_neighbours(name, nodes, edges).items():
        shown = [label(nodes[n]) for n in names if n in allowed]
        if rank != "seed" and len(shown) > LIST_CAP:  # a seed's lists are whole
            shown = shown[:LIST_CAP] + [f"+{len(shown) - LIST_CAP} more"]
        if shown:
            lines.append(f"{titles[key]}: {', '.join(shown)}")
    return "\n".join(lines) + "\n"


def estimate(text: str) -> int:
    """Pure: the token estimate of `text`: characters / 4, rounded up."""
    return -(-len(text) // CHARS_PER_TOKEN)


def render_slice(title: str, entries: list[Entry], budget: int) -> Slice:
    """Pure: the slice as text, whole blocks only, the header and the last line counted, the
    whole within `budget` tokens; when anything is cut, the last line names how many nodes
    and from which ranks. `ValueError` for a budget that is not positive or cannot hold the
    header and the last line (review cycle 1 F5)."""
    if budget <= 0:
        raise ValueError(f"a slice budget must be a positive number of tokens, not {budget}")
    head = f"# Atlas slice: {title}\n\n"
    every = len(entries)
    worst = (  # the longest last line this slice could need
        f"Cut at the budget of {budget} tokens: {every} nodes ("
        + ", ".join(f"{r} {every}" for r in RANKS)
        + f").\nComplete: {every} nodes within {budget} tokens.\n"
    )
    floor = estimate(head) + estimate(worst)
    if budget < floor:
        raise ValueError(
            f"a slice budget of {budget} tokens cannot hold its header and last line ({floor})"
        )
    kept, cut = [], []
    used = floor
    for entry in entries:
        cost = estimate(entry.block + "\n")
        if cut or used + cost > budget:
            cut.append(entry)
            continue
        kept.append(entry.block)
        used += cost
    if cut:
        ranks = {r: sum(1 for e in cut if e.rank == r) for r in RANKS}
        named = ", ".join(f"{r} {n}" for r, n in ranks.items() if n)
        tail = f"Cut at the budget of {budget} tokens: {len(cut)} nodes ({named}).\n"
    else:
        tail = f"Complete: {len(kept)} nodes within {budget} tokens.\n"
    text = head + "\n".join(kept) + ("\n" if kept else "") + tail
    return Slice(text, estimate(text), len(cut))
