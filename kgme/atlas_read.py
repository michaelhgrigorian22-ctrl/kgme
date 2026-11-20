"""The atlas, effects half: read the tracked tree and the listed projects, write `atlas/`.

Purpose: feed `kgme.atlas` and keep its notes on disk (HANDOFF-0051). The tree read is the
commit's: only tracked files (`git ls-files`), each read as a regular file through no link,
so `atlas/` is the same view in `main`, the design worktree, a fresh clone, and a crew
workspace. A project `kgme.toml` `[atlas] projects` lists is read by structure only: its
top-level folder names, the link targets of its `README.md`, and the KGME parts that README
names; never another file's contents. A project at, inside, or around a Tier 1 root is
refused (ADR-002). `write_atlas` writes a note only when its bytes change (a temp file beside
it, then `os.replace`), so a second run on the same tree writes nothing, and removes only a
stale note that carries the generated mark; nothing outside `atlas/` changes. `run_atlas` is
the command: silent in the ledger on success, since the atlas is a regenerable view, and one
`transient` event on failure, so a post-commit run that fails never fails the commit.
Inputs: the checkout, the parsed `kgme.toml`, whether this is a dry run.
Outputs: the sources and projects read; counts written, removed, unchanged; an exit code.
Side effects: reads tracked files, project folders, and READMEs; writes and removes notes
under `atlas/`; on failure, one ledger event.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from kgme import atlas, atlas_slice, clean_fs, events, ledger, paths
from kgme.hooks import guard

READ_ROOTS = ("kgme/", "jobs/", "control/", "tests/", "docs/", "skills/")
READ_SUFFIXES = (".py", ".sh", ".md")
MD_LINK = re.compile(r"\]\(([^)\s]+)\)|\[\[([^\]|#]+)")
KGME_COMMAND = re.compile(r"\bkgme ([a-z]+)\b")


def read_tracked(base: Path) -> list[str]:
    """Effect: every tracked path (`git ls-files`), sorted: the commit's tree."""
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached"], cwd=base, capture_output=True, check=True
    )
    return sorted(filter(None, listed.stdout.decode("utf-8", "surrogateescape").split("\0")))


def read_sources(base: Path, tracked: list[str] | None = None) -> list[atlas.Source]:
    """Effect: every tracked file the atlas reads the text of, in the commit's order."""
    sources: list[atlas.Source] = []
    for name in read_tracked(base) if tracked is None else tracked:
        hooks = name.startswith("control/git-hooks/")
        role = name.startswith("roles/") and name.endswith(".toml")  # the org chart (0071)
        if not (name.startswith(READ_ROOTS) and (name.endswith(READ_SUFFIXES) or hooks) or role):
            continue
        try:
            data = clean_fs.read_regular_bytes(base, base / name)
        except (clean_fs.Refused, OSError):
            continue  # a link or a file gone since the index: not part of the view
        sources.append(atlas.Source(name, data.decode("utf-8", errors="replace")))
    return sources


def read_projects(settings: dict, base: Path) -> list[atlas.Project]:
    """Effect: each listed project by structure only; `clean_fs.Refused` for a Tier 1 one."""
    tier1 = paths.tier1_paths(settings, base)
    projects: list[atlas.Project] = []
    for entry in settings.get("atlas", {}).get("projects", []):
        root = paths.resolve(entry, base).resolve()  # against the checkout, never the cwd (F6)
        if any(guard.is_under_any(root, [t]) or guard.is_under_any(t, [root]) for t in tier1):
            raise clean_fs.Refused(f"{entry} holds Tier 1 data; the atlas never reads it (ADR-002)")
        folders = tuple(
            sorted(
                e.name
                for e in os.scandir(root)
                if e.is_dir(follow_symlinks=False) and not e.name.startswith(".")
            )
        )
        readme = root / "README.md"
        # a regular file reached through no link, or refused: a README never leads elsewhere (F2)
        raw = clean_fs.read_regular_bytes(root, readme) if os.path.lexists(readme) else b""
        text = raw.decode("utf-8", errors="replace")
        links = tuple(sorted({a or b for a, b in MD_LINK.findall(text)}))
        uses = {f"jobs.{c}.run" for c in KGME_COMMAND.findall(text)}
        uses |= {atlas.module_name(p) for p in atlas.TICKED.findall(text) if p.startswith("kgme/")}
        projects.append(atlas.Project(root.name, folders, links, tuple(sorted(uses))))
    return projects


def write_atlas(out: Path, base: Path, notes: dict[str, str]) -> tuple[int, int, int]:
    """Effect: `notes` under `out`, each written only when its bytes change; every other note
    there that carries the generated mark removed. Returns (written, removed, unchanged)."""
    clean_fs.read_no_link_above(out / "x", base)
    if out.is_symlink():
        raise clean_fs.Refused(f"{out.relative_to(base)} is a symlink")
    written = unchanged = removed = 0
    for rel, text in notes.items():
        target = out / rel
        data = text.encode("utf-8")
        clean_fs.read_no_link_above(target, base)  # no link anywhere inside atlas/ (F1)
        if target.is_symlink():
            raise clean_fs.Refused(f"{target.relative_to(base)} is a symlink")
        if target.is_file() and target.read_bytes() == data:
            unchanged += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        clean_fs.read_no_link_above(target, base)
        temp = target.with_name(f".{target.name}.tmp-{events.new_ulid()}")
        temp.write_bytes(data)
        os.replace(temp, target)
        written += 1
    found = [Path(d) / f for d, _, names in os.walk(out, followlinks=False) for f in names]
    for path in sorted(p for p in found if p.suffix == ".md"):
        rel = path.relative_to(out).as_posix()
        if rel in notes or path.is_symlink() or not path.is_file():
            continue
        clean_fs.read_no_link_above(path, base)
        if atlas.MARK in path.read_text(encoding="utf-8", errors="replace").split("\n---", 1)[0]:
            path.unlink()
            removed += 1
    return written, removed, unchanged


def run_atlas(base: Path, settings: dict, dry_run: bool = False) -> int:
    """`kgme atlas`: read, build, write, one line of counts; a failure is one `transient`
    ledger event and exit 1, never a raised error."""
    try:
        tracked = read_tracked(base)
        sources = read_sources(base, tracked)
        nodes = atlas.build_graph(sources, read_projects(settings, base), tracked)
        notes = atlas.render_notes(nodes)
        if dry_run:
            print(f"kgme atlas: dry run; {len(nodes)} nodes, {len(notes)} notes; nothing written")
            return 0
        written, removed, unchanged = write_atlas(base / "atlas", base, notes)
        print(
            f"kgme atlas: {len(nodes)} nodes; {written} written, {unchanged} unchanged, "
            f"{removed} removed"
        )
        return 0
    except (clean_fs.Refused, OSError, subprocess.CalledProcessError, ValueError) as error:
        why = f"atlas not regenerated: {type(error).__name__}: {error}"
        event = events.make_event(
            source="kgme", actor="kgme.atlas", kind="note", job="atlas", key="atlas",
            class_="transient", summary=events.clip(events.redact(why)),
        )  # fmt: skip
        ledger.append(event, ledger.read_base_dirs(settings, base))
        print(f"kgme atlas: {why}", file=sys.stderr)
        return 1


SLICE_BUDGET = 3000  # tokens, until `kgme.toml [atlas] slice_budget` holds one (HANDOFF-0056)


def read_tree(base: Path) -> list[str]:
    """Effect: the tree a slice describes: the tracked files when `base` is a checkout's (or
    worktree's) root; otherwise, an export like the cheap lane's, nested in a checkout or
    not, every regular file under it outside `.git/`, sorted (review cycle 5 F1)."""
    if read_tree_root(base) == base.resolve() and (base / ".git").exists():
        return read_tracked(base)
    found = []
    for folder, dirs, names in os.walk(base, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in names:
            path = Path(folder) / name
            if path.is_file() and not path.is_symlink():
                found.append(path.relative_to(base).as_posix())
    return sorted(found)


def read_excluded(settings: dict, base: Path) -> tuple[str, ...]:
    """Effect: the prefixes no slice names: `memory/`, `logs/`, and each Tier 1 root that
    lies inside `base` (HANDOFF-0056 §1, for every model); `ValueError` for a base that is a
    Tier 1 root or lies inside one (review cycle 1 F1)."""
    inside = []
    root = base.resolve()
    for tier1 in paths.tier1_paths(settings, base):
        resolved = tier1.resolve()
        if root.is_relative_to(resolved):
            raise ValueError(f"{base} is inside a Tier 1 root; no slice is built from it")
        if resolved.is_relative_to(root):
            inside.append(resolved.relative_to(root).as_posix().rstrip("/") + "/")
    return atlas_slice.EXCLUDED + tuple(sorted(inside))


def read_tree_root(base: Path) -> Path:
    """Effect: the root of the tree a slice describes: the checkout (or worktree) that
    contains `base`, so a subdirectory reads its whole checkout with repository-relative
    paths (review cycle 4 F10); a tree that is not one stays as given."""
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=base, capture_output=True, text=True,
        check=False,
    )  # fmt: skip
    return Path(top.stdout.strip()).resolve() if top.returncode == 0 else base.resolve()


def read_permitted(base: Path, around: list[str], excluded: tuple[str, ...]) -> list[str]:
    """Effect: each `--around` argument as a path relative to `base`, normalised (`./`, `..`,
    an absolute path, a link) before it is filtered, seeded, or named; one outside the tree
    or under an excluded prefix is dropped (review cycle 2 F2)."""
    root = base.resolve()
    kept = []
    for given in around:
        path = Path(given)
        resolved = (path if path.is_absolute() else root / path).resolve()
        if not resolved.is_relative_to(root):
            continue
        rel = resolved.relative_to(root).as_posix()  # "." for the root: a folder seed (F9)
        if not atlas_slice.is_excluded(rel, excluded) and rel not in kept:
            kept.append(rel)
    return kept


def read_slice(
    base: Path, settings: dict, handoff: str | None, around: list[str], budget: int | None
) -> atlas_slice.Slice:
    """Effect: the slice of the tree at `base`, built in memory through the same reader and
    builder `kgme atlas` uses; nothing is written. Excluded paths are dropped from the tree
    before any file is opened, and from the arguments before the title is made (review
    cycle 1 F1, F2). `ValueError` for a handoff the tree does not hold, a base in Tier 1, or
    a budget that is not positive or too small."""
    from kgme import loop_outputs

    base = base.resolve()  # the tree as given; the CLI finds a checkout's root (cycle 5 F1)
    excluded = read_excluded(settings, base)  # a Tier 1 base is refused before any read
    tracked = [p for p in read_tree(base) if not atlas_slice.is_excluded(p, excluded)]
    sources = read_sources(base, tracked)
    nodes = atlas.build_graph(sources, [], tracked)
    around = read_permitted(base, around, excluded)
    entries = [a.rstrip("/") + "/" if (base / a).is_dir() else a for a in around]
    if handoff:
        held = [n for n in nodes.values() if n.kind == "handoff" and n.name == handoff]
        if not held:
            raise ValueError(f"{handoff} is not a handoff in {base}")
        text = next(s.text for s in sources if s.path == held[0].file)
        entries = loop_outputs.parse_outputs(text) + entries
    seeds = atlas_slice.read_seeds(entries, nodes)
    edges = atlas_slice.read_edges(sources, nodes)
    built = atlas_slice.build_slice(nodes, seeds, excluded, edges)
    # an omitted budget takes the default; a given one, zero included, is checked (F5)
    limit = budget if budget is not None else settings.get("atlas", {}).get("slice_budget")
    limit = SLICE_BUDGET if limit is None else limit
    title = " + ".join(([handoff] if handoff else []) + list(around))
    return atlas_slice.render_slice(title, built, int(limit))


def run_slice(
    base: Path,
    settings: dict,
    handoff: str | None,
    around: list[str],
    budget: int | None,
    out: Path | None,
    dry_run: bool = False,
) -> int:
    """`kgme atlas --slice ID / --around PATH`: the slice on stdout or in `out`; read-only
    otherwise, and silent in the ledger, as a view is. A dry run builds it, prints its
    size, and writes nothing (review cycle 1 F6)."""
    try:
        built = read_slice(base, settings, handoff, around, budget)
    except (clean_fs.Refused, OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"kgme atlas: no slice: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    if dry_run:
        print(
            f"kgme atlas: dry run; slice of {built.tokens} tokens, {built.cut} cut; nothing written"
        )
        return 0
    if out is None:
        sys.stdout.write(built.text)
    else:
        out.write_text(built.text, encoding="utf-8")
        print(f"kgme atlas: slice of {built.tokens} tokens, {built.cut} cut, written to {out}")
    return 0
