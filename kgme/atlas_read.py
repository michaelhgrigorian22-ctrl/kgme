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

from kgme import atlas, clean_fs, events, ledger, paths
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
        if not name.startswith(READ_ROOTS) or not (name.endswith(READ_SUFFIXES) or hooks):
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
