"""Loop mode's write fence: the paths a handoff's `Outputs` names, as a list (HANDOFF-0045 §2).

Purpose: when `kgme review --loop` (HANDOFF-0043) runs a builder with nobody watching, the
builder may write only inside its handoff's `Outputs`, plus `tests/` and `logs/scratch/`. The
loop parses the `## Outputs` section once per run into `<scratch>/loop/<run>/outputs.txt`
(`write_outputs`), and sets `KGME_LOOP_HANDOFF`, `KGME_LOOP_RUN`, and the list's sha256 in
`KGME_LOOP_OUTPUTS_SHA256` for the builder's process; the pre-tool guard reads that list
(`read_outputs`), never the prose, and only while it still hashes to that digest. The
builder cannot change the environment its hooks run in, so a list it edited, by any tool,
refuses every write; the guard also refuses a file write under the list's folder (review
cycle 1 F2). A path counts
when it appears in backticks in the section, without spaces, naming a file (`a/b.py`, `x.md`)
or a folder (`tests/policy/`). The list never widens anything: the guard's other rules still
apply inside it. When `KGME_LOOP_HANDOFF` is set and the list cannot be read, has no header,
names another handoff, has no digest, or no longer matches it, `read_outputs` says why, and
the guard refuses every write.
Inputs: the handoff's text and id, the scratch directory, the run id; the environment.
Outputs: the list's path and sha256; the entries, or the reason there are none.
Side effects: `write_outputs` creates the list, whole and new; `read_outputs` reads it.
"""

import hashlib
import os
import re
from pathlib import Path, PurePosixPath

from kgme import clean_fs

ENV_HANDOFF = "KGME_LOOP_HANDOFF"
ENV_RUN = "KGME_LOOP_RUN"
ENV_SHA = "KGME_LOOP_OUTPUTS_SHA256"
ALWAYS = ("tests/", "logs/scratch/")
RUN_ID = re.compile(r"^[0-9A-Za-z_-]{1,64}$")
HANDOFF_ID = re.compile(r"^HANDOFF-[0-9A-Za-z-]{1,40}$")
SECTION = re.compile(r"^## Outputs[ \t]*\n(?P<body>.*?)(?=^## |\Z)", re.M | re.S)
TICKED = re.compile(r"`([^`\s]+)`")
FILE_NAME = re.compile(r"^[\w.-]*\w\.\w+$")


def parse_outputs(text: str) -> list[str]:
    """Pure: the repository-relative paths the `## Outputs` section names, in order, once
    each; a folder keeps its trailing `/`. Anything absolute, above the repository, or not
    shaped like a path is left out."""
    match = SECTION.search(text)
    if match is None:
        return []
    found: list[str] = []
    for token in TICKED.findall(match["body"]):
        entry = token.removeprefix("./")
        parts = PurePosixPath(entry.rstrip("/")).parts
        if not parts or entry.startswith(("/", "~", "-")) or ".." in parts:
            continue
        if "/" not in entry and not FILE_NAME.match(entry):
            continue
        if entry not in found:
            found.append(entry)
    return found


def outputs_path(scratch: Path, run: str) -> Path:
    """Where the list for `run` lives; `ValueError` for a run id that could leave the folder."""
    if not RUN_ID.match(run):
        raise ValueError(f"not a loop run id: {run!r}")
    return scratch / "loop" / run / "outputs.txt"


def write_outputs(
    root: Path, scratch: Path, handoff_id: str, run: str, text: str
) -> tuple[Path, str]:
    """Effect: the list for `run`, its first line `# <handoff id>`, then one path per line.
    Created new and whole; an existing list is refused, so a run's fence is set once. Returns
    its path and the sha256 the loop puts in `KGME_LOOP_OUTPUTS_SHA256`."""
    if not HANDOFF_ID.match(handoff_id):
        raise ValueError(f"not a handoff id: {handoff_id!r}")
    path = outputs_path(scratch, run)
    body = "\n".join([f"# {handoff_id}", *parse_outputs(text)]) + "\n"
    clean_fs.write_payload(root, path, body)
    return path, hashlib.sha256(body.encode("utf-8")).hexdigest()


def read_outputs(
    scratch: Path, environ: dict[str, str] | None = None
) -> tuple[str, ...] | str | None:
    """Effect: None outside loop mode; in it, the entries the guard allows (the list plus
    `ALWAYS`), or the reason every write must be refused."""
    env = os.environ if environ is None else environ
    handoff = env.get(ENV_HANDOFF, "")
    if not handoff:
        return None
    digest = env.get(ENV_SHA, "")
    if not digest:
        return f"no digest for {handoff}'s Outputs list ({ENV_SHA} is not set)"
    try:
        path = outputs_path(scratch, env.get(ENV_RUN, ""))
        data = path.read_bytes()
        lines = data.decode("utf-8").splitlines()
    except (ValueError, OSError, UnicodeDecodeError) as error:
        return f"no Outputs list for {handoff}: {error}"
    if hashlib.sha256(data).hexdigest() != digest:
        return f"the Outputs list at {path} changed since the loop set it"
    if not lines or lines[0] != f"# {handoff}":
        return f"the Outputs list at {path} is not {handoff}'s"
    return tuple(line for line in lines[1:] if line.strip()) + ALWAYS


def is_inside(rel: PurePosixPath, entries: tuple[str, ...]) -> bool:
    """Pure: `rel` is an entry, or under a folder entry (one ending in `/`, or any entry it
    sits below)."""
    for entry in entries:
        named = PurePosixPath(entry.rstrip("/"))
        if rel == named or named in rel.parents:
            return True
    return False
