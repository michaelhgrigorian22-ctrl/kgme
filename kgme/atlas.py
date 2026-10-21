"""The atlas, pure half: KGME's parts and how they connect, as notes Obsidian draws (HANDOFF-0051).

Purpose: one short generated note per node, each linking its neighbours with `[[...]]`, so
Obsidian's graph is a lens on the repository and nothing more. Nodes: each top-level folder
(linked to what it contains); each module in `kgme/`, `jobs/`, and `control/` (linked to the
modules it imports, read with `ast` and never executed, to the tests that import it, and to
the ADRs its text cites); each test; each ADR (linked to the ADRs it supersedes or cites and
to the handoffs that cite it); each handoff (`depends_on`, `plan_ref`, the files of its
`Outputs`, its `report`, the ADRs it cites); each row of the phase plan; each reader (the
folders and modules it names); each audit (its handoff, the ADRs it cites); each skill; and,
opt-in, each project `kgme.toml` `[atlas] projects` lists. Each note opens with one line saying
what the node is and links the real file: a Markdown document as `[[docs/...]]`, code as a
plain relative link. Frontmatter `kind:` gives the graph's colour groups. The output is a
function of its inputs alone: no clock, no machine state, sorted throughout, so a second run
on the same tree writes identical bytes.
Inputs: `Source` records (path and text) the effects half read from the tracked tree, and
`Project` records.
Outputs: `Node` records; the notes as `{atlas-relative path: text}`.
Side effects: none. Reading the tree and writing `atlas/` is `kgme.atlas_read`.
"""

import ast
import re
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

from kgme.frontmatter import parse_frontmatter

MARK = "generated: kgme atlas"
CODE_ROOTS = ("kgme", "jobs", "control")
ADR_ID = re.compile(r"\bADR-(\d{3})\b")
HANDOFF_ID = re.compile(r"\bHANDOFF-(\d{4})\b")
TICKED = re.compile(r"`([^`\s]+)`")
BRACES = re.compile(r"\{([^{}]+)\}")
SHELL_MODULE = re.compile(r"\bkgme(?:\.[a-z_]+)+")
PLAN_ROW = re.compile(r"^\|\s*(\d+[a-z]?)\s*\|(.*)$", re.M)
PLAN_REF = re.compile(r"PLAN-PHASE-1 step (\d+[a-z]?)")


@dataclass(frozen=True)
class Source:
    """One tracked file the atlas reads: its repository-relative path and text."""

    path: str
    text: str


@dataclass(frozen=True)
class Project:
    """A project outside KGME, by structure only: its name, folder names, README link
    targets, and the KGME parts its README names."""

    name: str
    folders: tuple[str, ...]
    readme_links: tuple[str, ...]
    uses: tuple[str, ...]


@dataclass
class Node:
    """One note: its name (unique, the `[[...]]` target), kind, opening line, the real file
    it stands for, and the names it links."""

    name: str
    kind: str
    line: str
    file: str = ""
    links: set[str] = field(default_factory=set)


def module_name(path: str) -> str:
    """`kgme/hooks/guard.py` → `kgme.hooks.guard`; a shell script keeps its suffix."""
    pure = PurePosixPath(path)
    stem = pure.with_suffix("") if pure.suffix == ".py" else pure
    return ".".join(stem.parts)


def read_imports(text: str) -> set[str]:
    """Pure: the dotted names a Python source imports, parsed and never executed. `from a
    import b` gives `a` and `a.b`, so a module imported from its package is found."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


def expand(token: str) -> list[str]:
    """Pure: `a/{b,c}.md` → `a/b.md`, `a/c.md`; one level of braces."""
    match = BRACES.search(token)
    if not match:
        return [token]
    return [token[: match.start()] + part + token[match.end() :] for part in match[1].split(",")]


def read_doc_links(text: str) -> dict[str, set[str]]:
    """Pure: what a document names: `adrs` and `handoffs` by id anywhere, `paths` in backticks
    (braces expanded), and `outputs`, the paths of its `## Outputs` section."""
    outputs = re.search(r"^## Outputs[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    ticked = lambda body: {p.rstrip("/.,;:") for t in TICKED.findall(body) for p in expand(t)}  # noqa: E731
    return {
        "adrs": {f"ADR-{n}" for n in ADR_ID.findall(text)},
        "handoffs": {f"HANDOFF-{n}" for n in HANDOFF_ID.findall(text)},
        "paths": ticked(text),
        "outputs": ticked(outputs[1]) if outputs else set(),
    }


def match_paths(tokens: set[str], files: dict[str, str]) -> set[str]:
    """Pure: the node names whose file a token names, exactly or as a glob (`kgme/brief*.py`)."""
    return {
        name
        for token in tokens
        for path, name in files.items()
        if path == token or ("*" in token and fnmatchcase(path, token))
    }


def build_graph(
    sources: list[Source], projects: list[Project] = (), tracked: list[str] = ()
) -> dict[str, Node]:
    """Pure: every node and link of the atlas, from the tracked files read, every tracked
    path (for the folders and the files an `Outputs` names), and the projects."""
    nodes: dict[str, Node] = {}
    files: dict[str, str] = {}  # repository path -> node name

    def add(name: str, kind: str, line: str, file: str = "") -> Node:
        node = nodes.setdefault(name, Node(name, kind, line, file))
        if file:
            files[file] = name
        return node

    texts = {s.path: s.text for s in sources}
    for path in sorted(tracked):  # every top-level folder, whatever it holds (review F4)
        if "/" in path:
            top = path.split("/", 1)[0]
            add(f"folder-{top}", "folder", f"The top-level folder `{top}/`.")
    for path in sorted(texts):
        top = path.split("/", 1)[0]
        if "/" in path:
            add(f"folder-{top}", "folder", f"The top-level folder `{top}/`.")
        if top in CODE_ROOTS and path.endswith((".py", ".sh")):
            kind = "job" if top == "jobs" else "module"
            add(module_name(path), kind, f"Code: `{path}`.", path)
        elif (
            top == "tests" and path.endswith(".py") and PurePosixPath(path).name.startswith("test")
        ):
            add(module_name(path), "test", f"Tests: `{path}`.", path)
        elif top == "skills" and path.endswith("SKILL.md"):
            add(f"skill-{PurePosixPath(path).parent.name}", "skill", f"Skill: `{path}`.", path)
        elif path.startswith("docs/") and path.endswith(".md"):
            add_document(path, texts[path], add)
    named = set().union(
        *(read_doc_links(texts[p])["outputs"] for p in texts if p.startswith("docs/handoff/"))
    )
    for path in sorted(set(tracked) - set(files)):  # an existing file an Outputs names (F5)
        if any(path == t or ("*" in t and fnmatchcase(path, t)) for t in named):
            add(path.replace("/", "."), "file", f"File: {file_line(path)}", path)
            if "/" in path:  # a root file (`.gitignore`) sits in no folder
                nodes[f"folder-{path.split('/', 1)[0]}"].links.add(path.replace("/", "."))
    for path, text in sorted(texts.items()):
        name = files.get(path)
        if name is None:
            continue
        node = nodes[name]
        top = path.split("/", 1)[0]
        nodes[f"folder-{top}"].links.add(name)
        if path.endswith(".py"):
            imported = {i for i in read_imports(text) if i in nodes}
            node.links |= imported
            if node.kind == "test":
                for module in imported:
                    nodes[module].links.add(name)
        elif path.endswith(".sh"):
            node.links |= {m for m in SHELL_MODULE.findall(text) if m in nodes}
        link_document(node, text, nodes, files)
    for handoff in [n for n in nodes.values() if n.kind == "handoff"]:
        for adr in [link for link in handoff.links if nodes[link].kind == "adr"]:
            nodes[adr].links.add(handoff.name)  # the handoffs that cite an ADR
    for project in projects:
        node = add(f"project-{project.name}", "project", f"Project `{project.name}`, outside KGME.")
        node.links |= {u for u in project.uses if u in nodes}
    return nodes


def file_line(path: str) -> str:
    """Pure: a Markdown file as a wikilink (it is inside the vault); any other named in
    backticks, its relative link added when the note is rendered."""
    return f"[[{path[:-3]}]]." if path.endswith(".md") else f"`{path}`."


def add_document(path: str, text: str, add) -> None:
    """Pure: the node a document under `docs/` is, and, for the phase plan, one per row."""
    try:
        data, _ = parse_frontmatter(text)
    except ValueError:
        data = {}
    ident = str(data.get("id") or "")
    if path.startswith("docs/adr/") and ident.startswith("ADR-"):
        add(ident, "adr", f"Decision {ident}: [[{path[:-3]}]].", path)
    elif path.startswith("docs/handoff/") and ident.startswith("HANDOFF-"):
        add(ident, "handoff", f"Handoff {ident} ({data.get('status')}): [[{path[:-3]}]].", path)
    elif path.startswith("docs/audit/") and ident.startswith("AUDIT-"):
        add(ident, "audit", f"Report {ident}: [[{path[:-3]}]].", path)
    elif path.startswith("docs/readers/"):
        name = f"reader-{PurePosixPath(path).stem}"
        add(name, "reader", f"Reader: [[{path[:-3]}]].", path)
    elif path.startswith("docs/plans/"):
        for step, rest in PLAN_ROW.findall(text):
            row = add(f"plan-step-{step}", "plan", f"Plan row {step}: [[{path[:-3]}]].")
            row.links |= {f"HANDOFF-{n}" for n in re.findall(r"\b(\d{4})\b", rest)}


def link_document(node: Node, text: str, nodes: dict[str, Node], files: dict[str, str]) -> None:
    """Pure: a node's links read from its text, by kind, and the links back they imply."""
    named = read_doc_links(text)
    if node.kind in ("module", "job", "adr", "audit"):
        node.links |= {a for a in named["adrs"] if a in nodes and a != node.name}
    if node.kind == "handoff":
        data, _ = safe_frontmatter(text)
        node.links |= {str(d) for d in data.get("depends_on") or [] if str(d) in nodes}
        step = PLAN_REF.search(str(data.get("plan_ref") or ""))
        if step and f"plan-step-{step[1]}" in nodes:
            node.links.add(f"plan-step-{step[1]}")
        report = files.get(str(data.get("report") or ""))
        if report:
            node.links.add(report)
        node.links |= match_paths(named["outputs"], files)
        node.links |= {a for a in named["adrs"] if a in nodes}
    if node.kind == "audit":
        data, _ = safe_frontmatter(text)
        if str(data.get("handoff")) in nodes:
            node.links.add(str(data["handoff"]))
    if node.kind == "reader":
        node.links |= match_paths(named["paths"], files)
        node.links |= {f"folder-{p.split('/', 1)[0]}" for p in named["paths"]} & set(nodes)
    node.links.discard(node.name)


def safe_frontmatter(text: str) -> tuple[dict, str]:
    try:
        return parse_frontmatter(text)
    except ValueError:
        return {}, text


def render_notes(nodes: dict[str, Node]) -> dict[str, str]:
    """Pure: each node's note, `{atlas-relative path: text}`: frontmatter `kind` and the
    generated mark, a title, the opening line (code links its file relatively, so it opens in
    the editor), and the links, sorted."""
    notes: dict[str, str] = {}
    for name in sorted(nodes):
        node = nodes[name]
        line = node.line
        if node.file and not node.file.endswith(".md"):
            line += f" [{node.file}](../../{node.file})"
        links = "".join(f"- [[{link}]]\n" for link in sorted(node.links))
        notes[f"{node.kind}/{name}.md"] = (
            f"---\nkind: {node.kind}\n{MARK}\n---\n\n# {name}\n\n{line}\n"
            + (f"\n## Links\n{links}" if links else "")
        )
    return notes
