"""Hermes's fence inside `~/Projects/KGME/`: the `pre_tool_call` hook, its effects (HANDOFF-0073).

Purpose: the entry point Hermes's shell hook runs on every tool call (`~/.hermes/hooks/kgme-fence`
runs `python -I -m kgme.hermes_fence`), and the only part of the fence that reads the system.
`kgme.hermes_fence_parse` reads the call, `kgme.hermes_fence_policy` decides, both pure; this
module reads what the policy asks about, once, into `Facts`:
- every path is canonical: resolved through symlinks, then each existing component spelt as it
  is on disk, so a case or Unicode alias on macOS (`projects/kgme` for `Projects/KGME`) is the
  same folder (AUDIT-0177 F8; the installed `os.path.realpath` keeps an alias's spelling);
- a Delete or Move entry keeps its final component, its parent resolved, as Hermes acts on it
  (AUDIT-0177 F9);
- the root and `~` come from the password database, never `$HOME`, since Hermes may give its
  subprocesses a profile home (`hermes_constants.py:821-844`);
- the programs come from `~/.hermes/hooks/kgme-fence.paths` under that home, which install.sh
  writes once, never from Hermes's inherited `PATH`; a missing, unreadable or malformed file,
  or a pinned path that is not an executable file, refuses every call (AUDIT-0178 F10).
Limits, stated in the report: the threat model of `kgme.hermes_fence_policy`; the hook runs in
Hermes's own process, weaker than an OS-level sandbox.
Inputs: the hook's JSON on stdin; the root and the real home from the password database; the
paths file.
Outputs: exit 0 to allow (a `modify` directive on stdout when the call is rewritten), 2 to block
with the reason on stderr.
Side effects: `read_*` resolve paths, list folders, expand globs and read the paths file;
nothing is written.
"""

import glob
import json
import os
import pwd
import shlex
import sys
import unicodedata
from collections.abc import Mapping
from pathlib import Path

from kgme.hermes_fence_parse import GLOB_CHARS, PATHS_FILE, Call, parse, pinned
from kgme.hermes_fence_policy import Facts, Verdict, block, clean_env, judge, wanted

ROOT_UNDER_HOME = Path("Projects/KGME")
BRAIN = "brain"
TRUSTED_KGME = Path(".venv/bin/kgme")
PINNED_UNDER_HOME = Path(".hermes/hooks/kgme-fence.paths")


def fold(name: str) -> str:
    """Pure: a name as a case- and normalisation-insensitive filesystem compares it."""
    return unicodedata.normalize("NFC", name).casefold()


def read_spelling(parent: Path, name: str, listings: dict) -> str:
    """Effect (lists `parent`): `name` as it is spelt on disk in `parent`, when an entry of
    another spelling is the same file (`lstat`, so a final symlink is not followed)."""
    key = str(parent)
    if key not in listings:
        try:
            listings[key] = os.listdir(parent)
        except OSError:
            listings[key] = None
    names = listings[key]
    if not names or name in names:
        return name
    for entry in (e for e in names if fold(e) == fold(name)):
        try:
            if os.path.samestat(os.lstat(parent / entry), os.lstat(parent / name)):
                return entry
        except OSError:
            continue
    return name


def read_canonical(text: str, listings: dict) -> Path:
    """Effect: `text` resolved through symlinks, every existing component spelt as on disk."""
    real = Path(os.path.realpath(text))
    out = Path(real.anchor)
    for name in real.parts[1:]:
        out = out / read_spelling(out, name, listings)
    return out


def read_entry(text: str, listings: dict) -> Path:
    """Effect: the entry a Delete or Move acts on: its parent canonical, its final component
    kept (spelt as on disk), never followed."""
    head, name = os.path.split(text.rstrip("/") or "/")
    if name in ("", ".", ".."):
        return read_canonical(text, listings)
    parent = read_canonical(head or "/", listings)
    return parent / read_spelling(parent, name, listings)


def read_paths(text: str, listings: dict) -> tuple[Path, ...]:
    """Effect: `text` canonical, and its glob matches."""
    found = [text]
    if any(c in text for c in GLOB_CHARS):
        found += glob.glob(text)[:1000]
    return tuple(read_canonical(p, listings) for p in found)


def read_home() -> str:
    """Effect: the real home, from the password database, never `$HOME`."""
    return pwd.getpwuid(os.getuid()).pw_dir


def read_root(environ: Mapping[str, str] | None = None) -> Path:  # noqa: ARG001 - by design
    """Effect: the root, `~/Projects/KGME` under the real home; `environ` is accepted and
    ignored, so no `HOME` can move the fence."""
    return Path(read_home()) / ROOT_UNDER_HOME


def read_pinned(home: str) -> dict[str, str] | str:
    """Effect: the programs install.sh pinned under the real home, each an executable regular
    file; else why every call is refused."""
    try:
        text = (Path(home) / PINNED_UNDER_HOME).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return f"{PATHS_FILE} cannot be read ({type(error).__name__}); run install.sh"
    programs = pinned(text)
    if isinstance(programs, str):
        return programs
    for name, path in programs.items():
        if not (os.path.isfile(path) and os.access(path, os.X_OK)):
            return f"{PATHS_FILE} pins {name} at {path}, which is not an executable file"
    return programs


def read_facts(call: Call, root: Path, environ: Mapping[str, str], home: str,
               programs: Mapping[str, str]) -> Facts:  # fmt: skip
    """Effect: everything the policy needs, read once."""
    listings: dict = {}
    homes = tuple(dict.fromkeys(h for h in (home, environ.get("HOME")) if h))
    real_root = read_canonical(str(root), listings)
    texts, entries = wanted(call, homes)
    return Facts(
        root=real_root,
        homes=homes,
        resolved={text: read_paths(text, listings) for text in texts},
        entries={text: read_entry(text, listings) for text in entries},
        trusted_kgme=read_canonical(str(real_root / BRAIN / TRUSTED_KGME), listings),
        brain=read_canonical(str(real_root / BRAIN), listings),
        programs=programs,
        env=clean_env(environ, home, programs),
    )


def run_decide(text: str, root: Path, environ: Mapping[str, str], home: str | Path) -> Verdict:
    """Effect (through `read_facts`): the verdict on the hook's stdin; an unreadable or
    unrecognised payload is refused (fail closed), naming its keys and never its values, and
    so is every call when the paths file is missing or malformed."""
    try:
        payload = json.loads(text)
    except ValueError:
        return block("the hook payload is not JSON; refusing")
    call = parse(payload)
    if call is None:
        keys = sorted(payload) if isinstance(payload, Mapping) else type(payload).__name__
        return block(f"unrecognised hook payload (keys: {keys}); refusing")
    programs = read_pinned(str(home))
    if isinstance(programs, str):
        return block(f"{programs}; refusing")
    return judge(call, read_facts(call, root, environ, str(home), programs))


def wrapper(python: str) -> str:
    """Pure: the hook script Hermes runs, `~/.hermes/hooks/kgme-fence`: this module under the
    repository's own interpreter, isolated (`-I`), every failure turned into exit 2."""
    quoted = shlex.quote(python)
    return (
        "#!/bin/sh\n"
        "# kgme-fence: Hermes's pre_tool_call hook inside ~/Projects/KGME (HANDOFF-0073).\n"
        "# Written by `python -m kgme.hermes_fence --print-wrapper`; it fails closed.\n"
        f"py={quoted}\n"
        'if [ ! -x "$py" ]; then echo "kgme-fence: $py is missing; refusing" >&2; exit 2; fi\n'
        '"$py" -I -m kgme.hermes_fence\n'
        'if [ "$?" -eq 0 ]; then exit 0; fi\n'
        "exit 2\n"
    )


def run_hook(argv: list[str] | None = None) -> int:
    """Effect: the hook. Read stdin; allow (exit 0, a `modify` directive on stdout when the
    call is rewritten) or block (exit 2, the reason on stderr). Any exception is a refusal.
    `--root` and `--home` are for the tests; the installed wrapper passes neither.
    `--print-wrapper PYTHON` prints the hook script for that interpreter instead."""
    argv = sys.argv[1:] if argv is None else argv
    if "--print-wrapper" in argv:
        print(wrapper(argv[argv.index("--print-wrapper") + 1]), end="")
        return 0
    try:
        home = argv[argv.index("--home") + 1] if "--home" in argv else read_home()
        root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else read_root()
        verdict = run_decide(sys.stdin.read(), root, os.environ, home)
    except Exception as error:  # noqa: BLE001 - fail closed on anything
        verdict = block(f"the fence failed ({type(error).__name__}); refusing")
    if not verdict.allow:
        print(verdict.reason, file=sys.stderr)
        return 2
    if verdict.args is not None:
        print(json.dumps({"action": "modify", "args": dict(verdict.args)}))
    return 0


main = run_hook

if __name__ == "__main__":
    sys.exit(run_hook())
