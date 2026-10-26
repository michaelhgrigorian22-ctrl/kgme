"""`kgme brief`, the kept copies: every copy `kgme capture` kept under `memory/`, judged.

Purpose: a save kept beside a file no later capture touches (a past day's note) was found only
by `kgme clean kept`, which nothing schedules (HANDOFF-0052). The brief is read every morning,
so it finds them: every `.<name>.capture-<intent id>` under `memory/`, read through the brief's
own gate (`brief_read.read_gated`, the manifest's `memory/**/.*.capture-*`), hashed, and judged
by the one rule `kgme capture` and `kgme clean kept` use (`capture_recover.holds_save`) against
the hashes its capture recorded in the ledger. A copy the gate refuses is named, not skipped:
it cannot be shown to be what its capture kept. Nothing is deleted or written.
Inputs: the brief's `Places`.
Outputs: `brief.KeptCopy` records, sorted by path; refusal lines for folders the walk could not
list.
Side effects: lists `memory/`, reads each copy and the ledger.
"""

import fnmatch
import os
from pathlib import Path

from kgme import brief, brief_read, capture_fs, capture_recover, clean_fs
from kgme import capture_record as record

ROOT = "memory"
GLOB = ".*.capture-*"  # the handoff's scope, and the manifest's; an id need not parse
SEP = ".capture-"


def read_kept_copies(places: brief_read.Places) -> tuple[tuple[brief.KeptCopy, ...], list[str]]:
    """Effect: every kept copy under `memory/`, judged, and a refusal line for every folder
    the walk could not list (a brief missing a subtree would say there are none)."""
    base = places.base
    refusals: list[str] = []

    def failed(error: OSError) -> None:
        where = Path(error.filename or base).relative_to(base).as_posix()
        refusals.append(f"{where}: could not be listed for kept copies: {error.strerror}")

    found: list[brief.KeptCopy] = []
    top = base / ROOT
    if not top.is_dir():
        return (), refusals
    for dirpath, dirnames, filenames in os.walk(top, onerror=failed, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            if not fnmatch.fnmatchcase(name, GLOB):
                continue
            # a name whose intent id does not parse is a copy no capture recorded (review
            # cycle 1 F1): named with its file, never skipped
            match = capture_fs.KEPT_NAME.match(name)
            owner, intent_id = (
                (match["name"], match["id"]) if match else (name[1:].rsplit(SEP, 1)[0], None)
            )
            found.append(read_one(places, Path(dirpath) / name, owner, intent_id))
    return tuple(found), refusals


def read_one(
    places: brief_read.Places, path: Path, name: str, intent_id: str | None
) -> brief.KeptCopy:
    """Effect: one copy, read through the gate and judged; a refused read is named."""
    rel = path.relative_to(places.base).as_posix()
    folder = path.parent.relative_to(places.base).as_posix()
    # a name like `..capture-x` names no file (review cycle 2 F3): the copy is still named
    file = f"{folder}/{name}" if name else f"{folder}/?"
    unnamed = "" if name else "; its name names no file"
    try:
        raw = brief_read.read_gated(places, path)
    except (clean_fs.Refused, OSError) as error:
        return brief.KeptCopy(rel, file, 0, True, f"could not be checked: {error}{unnamed}")
    recorded = record.read_kept_hashes(places.dirs, intent_id) if intent_id else None
    holds = capture_recover.holds_save(record.sha256_bytes(raw), recorded)
    why = "no kgme capture recorded it" if holds and recorded is None else ""
    return brief.KeptCopy(rel, file, len(raw), holds, f"{why}{unnamed}")
