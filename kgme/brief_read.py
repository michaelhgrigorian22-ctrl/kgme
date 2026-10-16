"""`kgme brief` v1, the reading half of the effects: places, inputs, the previous day, identity.

Purpose: everything the brief job reads before it decides anything (HANDOFF-0034): the
checkout's streams and manifest, the input files after the manifest and the validator have
had their say, the day of the previous brief, and the identity a replaced brief keeps. The
transaction and the run live in `kgme/brief_io.py`.
Inputs: the parsed `kgme.toml`, the checkout to act on, the day, the ledger.
Outputs: a `Places`, `Input` records and refusal lines, a day, an `Identity` with the content
hash last recorded.
Side effects: reads files, the ledger, the clock, and the zone database. Writes nothing.
An input's hash is the sha256 of its bytes, and its text is decoded strictly (review cycle 1
F8); the brief it replaces is read through no link (F1); only a brief written, or an intent
reconciled `ok`, counts as an earlier brief or carries an identity (F4).
"""

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from kgme import brief, clean_fs, events, ledger, lint, paths, policy
from kgme.frontmatter import parse_frontmatter

JOB = "brief"
MANIFEST = Path("jobs") / "brief" / "manifest.toml"
INPUT_ROOTS = ("memory/notes", "memory/agent")


@dataclass(frozen=True)
class Places:
    """Everything one run reads from or writes to, resolved once."""

    base: Path
    dirs: ledger.Dirs
    payloads: Path
    manifest: policy.Manifest
    blocklist: list[Path]
    patterns: list[str]
    tier1: list[Path]

    def allowed(self, operation: str, path: Path) -> policy.Verdict:
        return policy.check(
            self.manifest,
            operation,
            str(path),
            self.base,
            self.blocklist,
            self.patterns,
            self.tier1,
        )


def read_places(settings: dict, base: Path) -> Places:
    """The checkout's streams and payload directory, the job's manifest, the guard's fences."""
    blocklist = settings["hooks"]["blocklist"]
    return Places(
        base=base,
        dirs=ledger.read_base_dirs(settings, base),
        payloads=paths.payloads_dir(settings, base),
        manifest=policy.read_manifest(paths.root() / MANIFEST),
        blocklist=[paths.resolve(p) for p in blocklist if not p.startswith("**/")],
        patterns=[p[3:] for p in blocklist if p.startswith("**/")],
        tier1=paths.tier1_paths(settings, base),
    )


def read_zone(settings: dict) -> ZoneInfo:
    """The zone `due` instants are read in: `kgme.toml` `[brief] timezone` (F9)."""
    return ZoneInfo(settings["brief"]["timezone"])


def read_clock() -> str:
    """Local time with offset, whole seconds: the shape the schema's example shows."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_input_paths(base: Path, date: str) -> tuple[list[Path], list[str]]:
    """Every `.md` under the input roots except the briefs, then the day's daily note and the
    friction log when present, sorted so two runs read in the same order; with them, a
    refusal line for every directory the walk could not read, since a brief missing a
    subtree is incomplete without saying so (review cycle 2 F11)."""
    found: list[Path] = []
    refusals: list[str] = []

    def failed(error: OSError) -> None:
        where = Path(error.filename or base).relative_to(base).as_posix()
        refusals.append(f"{where}: could not be listed: {error.strerror}")

    for root in INPUT_ROOTS:
        top = base / root
        if not top.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(top, onerror=failed, followlinks=False):
            dirnames.sort()
            for name in filenames:
                path = Path(dirpath) / name
                rel = path.relative_to(base).as_posix()
                if name.endswith(".md") and not rel.startswith(brief.BRIEF_DIR + "/"):
                    found.append(path)
    found.sort()
    for rel in (f"{brief.DAILY_DIR}/{date}.md", brief.FRICTION_PATH):
        if (base / rel).exists():
            found.append(base / rel)
    return found, refusals


def read_gated(places: Places, path: Path) -> bytes:
    """The one way the brief job reads a file (Cowork's ruling on review cycle 2 F1): the
    path is resolved and must stay under the checkout, no component below the checkout and
    not the path itself may be a symlink, the manifest must allow the read, and only then
    are the bytes read, as a regular file opened without waiting. `clean_fs.Refused` with
    the reason otherwise, before any byte is read. `tests/test_brief_review.py` fails when a
    brief module reads a file any other way."""
    rel = path.relative_to(places.base).as_posix()
    if not path.resolve().is_relative_to(places.base.resolve()):
        raise clean_fs.Refused(f"{rel} resolves outside the checkout")
    if path.is_symlink():
        raise clean_fs.Refused(f"{rel} is a symlink; nothing is read through one")
    clean_fs.read_no_link_above(path, places.base)
    verdict = places.allowed("read", path)
    if not verdict.allowed:
        raise clean_fs.Refused(f"{rel}: {verdict.reason.replace(str(places.base) + '/', '')}")
    return clean_fs.read_regular_bytes(places.base, path)


def frontmatter_of(text: str, rel: str) -> tuple[dict, str]:
    """`parse_frontmatter`, raising `clean_fs.Refused` by contract on a note it cannot parse
    (no frontmatter block, YAML that does not parse, not a mapping), so a parse failure is
    a classified refusal and never an escape (ruling on cycle 2 F6)."""
    try:
        data, body = parse_frontmatter(text)
    except ValueError as error:
        raise clean_fs.Refused(f"{rel}: {error}") from error
    return {str(key): value for key, value in data.items()}, body


def read_inputs(places: Places, input_paths: list[Path]) -> tuple[list[brief.Input], list[str]]:
    """Each input read through `read_gated` and found nothing blocking by the validator;
    otherwise a refusal line. Ids are checked unique across the run."""
    inputs: list[brief.Input] = []
    refusals: list[str] = []
    ids_seen: dict[str, str] = {}
    for path in input_paths:
        rel = path.relative_to(places.base).as_posix()
        try:
            raw = read_gated(places, path)
        except clean_fs.Refused as refused:
            refusals.append(str(refused))
            continue
        try:
            text = raw.decode("utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            refusals.append(f"{rel}: not valid UTF-8")
            continue
        blocking = [f for f in lint.lint_note(text, rel, ids_seen) if f.cls == "blocking"]
        if blocking:
            refusals.append(f"{rel}: {blocking[0].rule}, {blocking[0].message}")
            continue
        try:
            data, body = frontmatter_of(text, rel)
        except clean_fs.Refused as refused:
            refusals.append(str(refused))
            continue
        digest = hashlib.sha256(raw).hexdigest()
        inputs.append(brief.Input(rel, str(data["id"]), text, digest, data, body))
    return inputs, refusals


def read_written_intents(dirs: ledger.Dirs) -> list[dict]:
    """The brief write intents an `ok` outcome answered: written, or found written on
    reconciliation. An intent that died before writing is not a brief (F4)."""
    return [
        e
        for e in ledger.read_ok_intents(JOB, dirs)
        if (e["key"] or "").startswith("brief:") and brief.parse_identity(e["summary"])
    ]


def read_previous_brief_date(base: Path, date: str, dirs: ledger.Dirs) -> str | None:
    """The day of the latest brief before `date`: from the files under the brief folder and
    from the ledger's written intents, so a brief deleted by `kgme clean briefs` still counts
    and the regenerated brief keeps its friction cutoff."""
    days: set[str] = set()
    folder = base / brief.BRIEF_DIR
    if folder.is_dir():
        days.update(p.stem for p in folder.glob("????-??-??.md") if brief.valid_date(p.stem))
    days.update(e["key"][len("brief:") :] for e in read_written_intents(dirs))
    earlier = [day for day in days if day < date]
    return max(earlier) if earlier else None


def read_identity(
    places: Places, destination: Path, date: str, now: str
) -> tuple[brief.Identity, str | None]:
    """The identity to keep: from the artefact if it exists, read through no link, else from
    the last written intent for this day in the ledger (so a brief deleted by `kgme clean
    briefs` regenerates byte-identical), else new. With it, the content hash last recorded,
    if any. `clean_fs.Refused` when the artefact is a link, unreadable, or has no identity."""
    rel = destination.relative_to(places.base).as_posix()
    if os.path.lexists(destination):
        raw = read_gated(places, destination)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise clean_fs.Refused(f"{rel}: not valid UTF-8") from error
        data, _ = frontmatter_of(text, rel)
        if not all(data.get(field) for field in ("id", "created", "modified")):
            raise clean_fs.Refused(f"{rel} has no id, created, and modified to keep")
        identity = brief.Identity(str(data["id"]), str(data["created"]), str(data["modified"]))
        return identity, brief.content_hash(text)
    recorded = [e for e in read_written_intents(places.dirs) if e["key"] == f"brief:{date}"]
    for event in sorted(recorded, key=lambda e: e["id"], reverse=True):
        parsed = brief.parse_identity(event["summary"])
        if parsed:
            return parsed
    return brief.Identity(events.new_ulid(), now, now), None
