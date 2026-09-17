"""The pure half of the pre-tool guard: which paths a call touches, and whether any is forbidden.

Purpose: decide, from the hook payload and the configuration alone, whether a tool call may
proceed. Everything that checks a file exists, reads a script, or writes an event lives in
`pre_tool_guard`.
Inputs: the hook payload dict; the `[hooks]` and `[paths]` sections of `kgme.toml`; the repo
root; for Bash, the fragments of any script the line would execute, read by the entry point
only after the line itself has been allowed.
Outputs: a `Decision` with the resolved candidate paths and, if refused, the reason.
Side effects: none that change anything. `Path.resolve()` consults the filesystem to follow
symlinks; it creates, reads, and writes nothing. Nothing here tests whether a file exists.

What this guard is and is not (HANDOFF-0028, ADR-013 §2, the F2 arbitration of 2026-09-15):
it is the enforcement layer that sees resolved paths, beside the settings deny list. For Bash
it scans every fragment of the command line, heredoc bodies and inline code included, and the
text of any script file the line executes, so that `python -c "open('.env')"` and
`uv run script.py` are caught when they name a forbidden file directly. A script the line only
copies, greps, or lists is not executed and is not scanned; a script that follows a runner word
anywhere in its command segment is. A `cd` inside the line, a glob the shell expands later, or
a name built at runtime are the recorded residual; the canary tests (HANDOFF-0032) measure it
and the OS-level boundary (HANDOFF-0038) closes it.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

PATH_KEYS = ("file_path", "path", "notebook_path", "directory")
FILE_TOOLS = ("Read", "Edit", "Write", "NotebookEdit", "MultiEdit", "Glob", "Grep", "LS")
SCRIPT_SUFFIXES = (".py", ".sh", ".zsh", ".bash")
RUNNERS = ("python", "python3", "sh", "bash", "zsh", "source", ".", "run", "exec", "nohup")
FRAGMENT_SPLIT = re.compile(r"[\s;|&()<>`'\"{}\[\],=:]+")
SEGMENT_SPLIT = re.compile(r"(?:\|\||&&|[;|\n])")
REDIRECTION_PREFIX = re.compile(r"^[0-9]*[<>&|]+")


@dataclass(frozen=True)
class Decision:
    """`allowed` with the candidate paths examined, or refused with a one-line `reason`."""

    allowed: bool
    paths: tuple[Path, ...]
    reason: str


def fragments(text: str) -> list[str]:
    """Every path-like fragment of a command line or script text.

    Splitting on whitespace, shell operators, quotes, brackets, `=` and `:` isolates a filename
    wherever it sits: `cat .env;`, `--file=.env`, `open('.env')`, `<<EOF … .env … EOF`. A
    fragment that is empty, a flag, or a redirection prefix is dropped. `$HOME` and `~` expand.
    """
    found: list[str] = []
    for raw in FRAGMENT_SPLIT.split(text):
        fragment = REDIRECTION_PREFIX.sub("", raw)
        if not fragment or fragment.startswith("-"):
            continue
        found.append(os.path.expandvars(fragment))
    return found


def expand_home(fragment: str) -> Path:
    """`~` and `~user` expanded when the shell would expand them; otherwise the literal path.

    A tilde word that names no user (`~330` in a table, `~nosuchuser/x`) stays literal and is
    resolved against the working directory like any other word. `expanduser` raises on it,
    and a guard that raises fails closed and refuses the call (learned 2026-09-17).
    """
    path = Path(fragment)
    try:
        return path.expanduser()
    except RuntimeError:
        return path


def resolve_all(fragment_list: list[str], cwd: Path) -> tuple[Path, ...]:
    """Each fragment as an absolute path against `cwd`, symlinks followed."""
    resolved = []
    for fragment in fragment_list:
        path = expand_home(fragment)
        absolute = path if path.is_absolute() else cwd / path
        resolved.append(absolute.resolve())
    return tuple(resolved)


def candidate_paths(tool_name: str, tool_input: dict, cwd: Path) -> tuple[Path, ...]:
    """Every path a call names, resolved. Bash: every fragment; file tools: the named keys."""
    if tool_name == "Bash":
        return resolve_all(fragments(str(tool_input.get("command", ""))), cwd)
    named = []
    for key in PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            named.append(value)
    return resolve_all(named, cwd)


def script_candidates(tool_name: str, tool_input: dict, cwd: Path) -> tuple[Path, ...]:
    """Script-suffixed words a Bash line would execute, resolved; existence is not checked here.

    A word counts as executed when it stands first on the line or when a runner word
    (`python`, `sh`, `bash`, `source`, `run`, …) precedes it anywhere in the same command
    segment, so `uv run python -X dev job.py` is caught while `cp a.py b.py` and
    `grep x tests/test_y.py` are not. Segments are split on `;`, `|`, `&&`, `||`, newlines.
    """
    if tool_name != "Bash":
        return ()
    found: list[Path] = []
    for segment in SEGMENT_SPLIT.split(str(tool_input.get("command", ""))):
        seen_runner = False
        for index, word in enumerate(fragments(segment)):
            if Path(word).name in RUNNERS:
                seen_runner = True
            executed = index == 0 or seen_runner
            path = expand_home(word)
            absolute = (path if path.is_absolute() else cwd / path).resolve()
            if executed and absolute.suffix in SCRIPT_SUFFIXES and absolute not in found:
                found.append(absolute)
    return tuple(found)


def _under(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def is_under_any(path: Path, roots: list[Path]) -> bool:
    """True if `path` is one of `roots` or lies under one."""
    return any(_under(path, root) for root in roots)


def _name_matches(part: str, pattern: str) -> bool:
    """`.env` matches `.env` and `.env.local`; `*.env` matches `planted.env` and `prod.env.bak`."""
    if pattern.startswith("*."):
        suffix = pattern[1:]
        return part.endswith(suffix) or (suffix + ".") in part
    return part == pattern or part.startswith(pattern + ".")


def is_blocklisted(path: Path, blocklist: list[Path], name_patterns: list[str]) -> bool:
    """True if `path` is, or is under, a blocklisted root, or any part matches a name pattern."""
    if any(_under(path, root) for root in blocklist):
        return True
    return any(
        any(_name_matches(part, pattern) for part in path.parts) for pattern in name_patterns
    )


def decide(
    tool_name: str,
    tool_input: dict,
    cwd: Path,
    repo_root: Path,
    blocklist: list[Path],
    name_patterns: list[str],
    allow_outside: list[Path],
    extra_paths: tuple[Path, ...] = (),
    uninspectable: tuple[Path, ...] = (),
) -> Decision:
    """The rule (HANDOFF-0028, ADR-013 §2):

    1. Any tool naming a blocklisted path, on the line or inside a script it runs, is refused.
    2. A file tool naming a path outside the repository is refused unless the path is under
       a root in `allow_outside`. A Bash line that executes a script the guard could not
       inspect (outside the allowed roots, or unreadable) is refused for the same reason.
    3. Everything else is allowed; the settings file still decides whether to ask.
    """
    paths = candidate_paths(tool_name, tool_input, cwd) + tuple(extra_paths)
    for path in paths:
        if is_blocklisted(path, blocklist, name_patterns):
            return Decision(False, paths, f"refused: {tool_name} names a blocklisted path {path}")
    if tool_name in FILE_TOOLS:
        for path in paths:
            if not _under(path, repo_root) and not is_under_any(path, allow_outside):
                return Decision(
                    False, paths, f"refused: {tool_name} names a path outside the repository {path}"
                )
    for script in uninspectable:
        return Decision(
            False, paths, f"refused: Bash runs a script the guard cannot inspect {script}"
        )
    return Decision(True, paths, "")
