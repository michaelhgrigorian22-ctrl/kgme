"""`kgme skills install`: the repository's skills linked where every harness reads them
(HANDOFF-0048 §7, amendment 10).

Purpose: each `skills/<name>/` that holds a `SKILL.md` is linked into `~/.claude/skills/`
(the global directory Michou named, 2026-10-16), `~/.agents/skills/` (Codex's user skills;
Codex follows symlinks), and the repository's own `.claude/skills/` and `.agents/skills/`
(relative links, as HANDOFF-0044 made them). A harness that will not follow a link gets a
copy (`--copy DIR`) beside a `.kgme-skill.sha256` marker, and `kgme lint` checks the copy's
hash against the repository's through `read_findings`. The installer refuses to overwrite a
skill of the same name it did not install (anything that is not a link to this repository's
`skills/<name>`), never touches `~/.claude/skills/synced/` (Claude's own skill sync), and
is Michou's command: it refuses to run under an agent harness. The state of
`~/.claude/skills/` is measured at the first run and recorded in the ledger note, not
assumed from 2026-10-16.
Inputs: the repository, the home folder, the parsed `kgme.toml`.
Outputs: what was linked, skipped and refused; lint findings for drifted copies.
Side effects: symlinks and copies; one ledger note per run.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

from kgme import approve, events, ledger, lint

SKILLS = "skills"
MARKER = ".kgme-skill.sha256"
SYNCED = "synced"
HOMES = (Path("~/.claude/skills"), Path("~/.agents/skills"))
LOCAL = (Path(".claude/skills"), Path(".agents/skills"))


def read_skills(base: Path) -> list[Path]:
    """Effect: the skill folders of the repository, those with a `SKILL.md`, sorted."""
    root = base / SKILLS
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def skill_sha256(folder: Path) -> str:
    """Effect: one digest over the skill's files, by relative path and bytes."""
    digest = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.name != MARKER):
        digest.update(path.relative_to(folder).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def read_state(folder: Path) -> list[str]:
    """Effect: what a skills folder holds, one line each (kind and name), measured, so the
    note records the directory as it is."""
    if not folder.is_dir():
        return ["(absent)"]
    rows = []
    for entry in sorted(folder.iterdir()):
        if entry.name.startswith("."):
            continue
        kind = "link" if entry.is_symlink() else "dir" if entry.is_dir() else "file"
        target = f" -> {os.readlink(entry)}" if entry.is_symlink() else ""
        rows.append(f"{kind} {entry.name}{target}")
    return rows or ["(empty)"]


def is_ours(entry: Path, skill: Path) -> bool:
    """Effect: `entry` is a link that resolves to this repository's `skill`."""
    return entry.is_symlink() and entry.resolve() == skill.resolve()


def write_link(target_dir: Path, skill: Path, relative: bool) -> str:
    """Effect: `target_dir/<name>` linked to `skill`; the result word: linked, kept (ours
    already), or refused (something else of that name is there)."""
    entry = target_dir / skill.name
    if entry.name == SYNCED:
        return "refused: synced is Claude's"
    if entry.exists() or entry.is_symlink():
        return "kept" if is_ours(entry, skill) else "refused: not installed by kgme"
    target_dir.mkdir(parents=True, exist_ok=True)
    source = os.path.relpath(skill, target_dir) if relative else str(skill.resolve())
    entry.symlink_to(source)
    return "linked"


def write_copy(target_dir: Path, skill: Path) -> str:
    """Effect: a copy of `skill` in `target_dir` with its marker; refused when something
    of that name is there that carries no marker of ours."""
    entry = target_dir / skill.name
    if entry.exists() and not (entry / MARKER).is_file():
        return "refused: not installed by kgme"
    if entry.exists():
        shutil.rmtree(entry)
    shutil.copytree(skill, entry, ignore=shutil.ignore_patterns("__pycache__"))
    (entry / MARKER).write_text(skill_sha256(skill) + "\n", encoding="utf-8")
    return "copied"


COPIES = Path("logs/scratch/skills/copies.txt")


def read_copies(base: Path) -> tuple[Path, ...]:
    """Effect: the `--copy` destinations earlier installs recorded, one per line."""
    path = base / COPIES
    if not path.is_file():
        return ()
    return tuple(Path(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())


def write_copies(base: Path, copies: tuple[Path, ...]) -> None:
    """Effect: the destinations `kgme lint` will check, kept with the earlier ones."""
    path = base / COPIES
    path.parent.mkdir(parents=True, exist_ok=True)
    known = dict.fromkeys([*read_copies(base), *copies])
    path.write_text("".join(f"{p}\n" for p in known), encoding="utf-8")


def read_findings(base: Path, copies: tuple[Path, ...] = ()) -> list[lint.Finding]:
    """Effect: for `kgme lint`: a copy whose own files no longer hash to the repository's
    skill (either side edited, cycle 1 F15), or whose source is gone, is `blocking`. The
    folders checked: the repository's two local ones, `copies`, and every destination an
    install recorded (`read_copies`)."""
    found: list[lint.Finding] = []
    folders = [base / local for local in LOCAL] + list(copies) + list(read_copies(base))
    for folder in dict.fromkeys(folders):
        if not folder.is_dir():
            continue
        for entry in sorted(folder.iterdir()):
            marker = entry / MARKER
            if entry.is_symlink() or not marker.is_file():
                continue
            source = base / SKILLS / entry.name
            inside = marker.is_relative_to(base)
            where = marker.relative_to(base).as_posix() if inside else str(marker)
            if not source.is_dir():
                found.append(lint.Finding(
                    where, "skill-copy", "blocking",
                    f"copy of a skill the repository no longer holds: {entry.name}",
                ))  # fmt: skip
                continue
            if skill_sha256(entry) != skill_sha256(source):
                found.append(lint.Finding(
                    where, "skill-copy", "blocking", f"skill copy drifted from skills/{entry.name}"
                ))  # fmt: skip
    return found


def run_install(base: Path, settings: dict, home: Path, copies: tuple[Path, ...] = (),
                dirs: ledger.Dirs | None = None, environ: dict | None = None) -> int:  # fmt: skip
    """The command (Michou's): links in the two home folders and the two local ones, copies
    where asked, the state of `~/.claude/skills/` measured first; one ledger note."""
    agent = approve.read_agent(dict(os.environ if environ is None else environ))
    if agent:
        print(
            f"kgme skills install: refused: {agent} is set; it is Michou's command",
            file=sys.stderr,
        )
        return 2
    skills = read_skills(base)
    if not skills:
        print("kgme skills install: no skills/<name>/SKILL.md to install", file=sys.stderr)
        return 2
    measured = read_state(home / ".claude" / "skills")
    results: list[str] = []
    for skill in skills:
        for target in HOMES:
            folder = home / Path(str(target).removeprefix("~/"))
            results.append(f"{folder / skill.name}: {write_link(folder, skill, relative=False)}")
        for target in LOCAL:
            word = write_link(base / target, skill, relative=True)
            results.append(f"{(base / target) / skill.name}: {word}")
        for folder in copies:
            results.append(f"{folder / skill.name}: {write_copy(folder, skill)}")
    if copies:
        write_copies(base, tuple(copies))
    for line in results:
        print(line)
    counts = {
        w: sum(1 for r in results if r.endswith(f": {w}")) for w in ("linked", "kept", "copied")
    }
    refused = sum(1 for r in results if "refused" in r)
    summary = (
        f"skills install: {len(skills)} skills; linked {counts['linked']}, kept {counts['kept']}, "
        f"copied {counts['copied']}, refused {refused}; ~/.claude/skills before: "
        f"{'; '.join(measured)}"
    )
    ledger.append(
        events.make_event(source="human", actor="michou", kind="note", job="skills",
                          key="skills:install", summary=events.clip(summary)),
        dirs or ledger.read_base_dirs(settings, base),
    )  # fmt: skip
    return 1 if refused else 0
