"""Hermes's fence, what it reads of a tool call (HANDOFF-0073 §2): the shell words, the patch.

Purpose: turn the hook's payload into a `Call`, a terminal command into shell words, and a V4A
patch into the paths it touches, each tagged with how Hermes resolves it. Facts from the
installed Hermes, read at `~/.hermes/hermes-agent`:
- the payload is `{hook_event_name, tool_name, tool_input, session_id, cwd, extra}`, `cwd`
  being Hermes's *process* directory (`agent/shell_hooks.py:1-5`, `:87-106`);
- `patch` applies the V4A grammar of `tools/patch_parser.py:51-57` (applied at
  `tools/file_operations.py:1687`); Delete and both ends of a Move act on the entry itself, a
  final symlink kept, while Update and Add write through it (`tools/file_tools.py:166-171`;
  `tools/file_operations.py:1322-1324`, `:1363`).
It also reads the paths file install.sh writes, `~/.hermes/hooks/kgme-fence.paths`, one
`name=/absolute/path` line per pinned program (`pinned`; AUDIT-0178 F10).
Inputs: strings and mappings. Outputs: `Call`, `Word`s, path texts, `Target`s, pinned paths.
Side effects: none; everything here is pure.
"""

import posixpath
import re
import string
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

NAME_KEYS = ("tool_name", "tool", "name")
ARG_KEYS = ("tool_input", "args", "arguments", "input", "tool_args")
PLAIN = frozenset(string.ascii_letters + string.digits + "_-./:,@%+^")
OPERATORS = frozenset(";&|<>()")
GLOB_CHARS = "*?["
# Read on the flattened text (`flat`): quotes and backslashes gone, case folded.
DIRECTORY_CHANGE = re.compile(
    r"(?<![\w./-])(?:cd|pushd|popd|source|eval)(?![\w./-])|(?:^|[\s;&|(])\.(?=\s)"
)
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# The programs install.sh pins (AUDIT-0178 F10), in the order their folders go on the child PATH.
PINNED = ("git", "uv", "claude", "codex")
PATHS_FILE = "~/.hermes/hooks/kgme-fence.paths"
# Hermes's V4A grammar, verbatim from tools/patch_parser.py:51-57.
PATCH_BEGIN = re.compile(r"^\*\*\*\s*Begin\s+Patch\s*$")
PATCH_END = re.compile(r"^\*\*\*\s*End\s+Patch\s*$")
PATCH_UPDATE = re.compile(r"\*\*\*\s*Update\s+File:\s*(.+)")
PATCH_ADD = re.compile(r"\*\*\*\s*Add\s+File:\s*(.+)")
PATCH_DELETE = re.compile(r"\*\*\*\s*Delete\s+File:\s*(.+)")
PATCH_MOVE = re.compile(r"\*\*\*\s*Move\s+File:\s*(.+?)\s*->\s*(.+)")
# Which operations act on the entry itself (True) rather than through a final symlink.
PATCH_OPS = ((PATCH_UPDATE, False), (PATCH_ADD, False), (PATCH_DELETE, True), (PATCH_MOVE, True))


@dataclass(frozen=True)
class Call:
    """One tool call: its name, its arguments, and Hermes's process directory."""

    name: str
    args: Mapping
    process_dir: str | None


@dataclass(frozen=True)
class Target:
    """A path a write tool names, and whether Hermes acts on the entry itself (Delete, Move)."""

    text: str
    entry: bool = False


@dataclass(frozen=True)
class Word:
    """One shell word with its quotes removed, or an operator; what in it the shell would
    expand (`$`, a backtick), an unquoted leading `~/`, and any other unquoted character the
    fence does not take literally (globs, braces, escapes, a comment, `~user`)."""

    text: str
    op: bool = False
    expands: bool = False
    tilde: bool = False
    marks: frozenset[str] = frozenset()


def parse(payload: object) -> Call | None:
    """Pure: the call in the hook's payload, or None when it has no shape the fence knows."""
    if not isinstance(payload, Mapping):
        return None
    name = next((payload[k] for k in NAME_KEYS if isinstance(payload.get(k), str)), None)
    if not name:
        return None
    args = next((payload[k] for k in ARG_KEYS if isinstance(payload.get(k), Mapping)), {})
    cwd = payload.get("cwd")
    return Call(name, args, cwd if isinstance(cwd, str) and cwd.startswith("/") else None)


def lex(command: str) -> list[Word] | str:
    """Pure: the command as words and operators, or why it does not lex (an open quote).
    Single quotes are literal; in double quotes `$` and a backtick expand and `\\` escapes;
    unquoted, `;&|<>()` and newlines are operators."""
    words: list[Word] = []
    text: list[str] | None = None
    flags: dict = {}

    def flush() -> None:
        nonlocal text
        if text is not None:
            words.append(Word("".join(text), expands=flags.get("expands", False),
                              tilde=flags.get("tilde", False),
                              marks=frozenset(flags.get("marks", ()))))  # fmt: skip
        text = None

    def mark(char: str) -> None:
        flags.setdefault("marks", set()).add(char)

    i, n = 0, len(command)
    while i < n:
        ch = command[i]
        if ch in " \t":
            flush()
            i += 1
            continue
        if ch in "\n\r" or ch in OPERATORS:
            flush()
            j = i + 1
            while ch in OPERATORS and j < n and command[j] in OPERATORS:
                j += 1
            words.append(Word(command[i:j], op=True))
            i = j
            continue
        if text is None:
            text, flags = [], {}
        if ch == "'":
            end = command.find("'", i + 1)
            if end < 0:
                return "an open single quote"
            text.append(command[i + 1 : end])
            i = end + 1
        elif ch == '"':
            j = i + 1
            while j < n and command[j] != '"':
                if command[j] in "$`":
                    flags["expands"] = True
                if command[j] == "\\":
                    mark("\\")
                    j += 1
                j += 1
            if j >= n:
                return "an open double quote"
            text.append(command[i + 1 : j])
            i = j + 1
        elif ch == "\\":
            mark("\\")
            text.append(command[i + 1 : i + 2])
            i += 2
        else:
            if ch in "$`":
                flags["expands"] = True
            elif ch == "~" and not text and command[i + 1 : i + 2] in ("/", "", " ", "\t"):
                flags["tilde"] = True
            elif ch == "~" and (not text or text[-1][-1:] in "=:"):
                mark("~")
            elif ch in "=#" and not text:
                mark(ch)
            elif ch not in PLAIN and ch not in "=#~":
                mark(ch)
            text.append(ch)
            i += 1
    flush()
    return words


def flat(text: str) -> str:
    """Pure: the text as the outside checks read it: every quote and backslash removed (so
    `c''d`, `"cd"` and `\\cd` all read `cd`), Unicode composed, case folded, and `//` and `/./`
    collapsed. It over-reads by design, and only ever adds a refusal."""
    text = unicodedata.normalize("NFC", re.sub(r"['\"\\]", "", text)).casefold()
    return re.sub(r"/(?:\.?/)+", "/", text)


def simple_problem(words: list[Word]) -> str | None:
    """Pure: why the words are not one simple command the fence takes literally, or None."""
    if not words:
        return "an empty command"
    op = next((w.text for w in words if w.op), None)
    if op is not None:
        shown = "a newline" if op in "\n\r" else f"`{op}`"
        return f"{shown} is refused: no ;, &&, ||, |, &, redirection, subshell or second line"
    if any(w.expands for w in words):
        return "`$`, backticks and substitution are refused"
    marks = sorted({m for w in words for m in w.marks})
    if marks:
        return (f"unquoted {' '.join(marks)} is refused: no globs, braces, escapes, comments "
                "or ~user; quote a literal pattern")  # fmt: skip
    return None


def home_texts(text: str, homes: tuple[str, ...]) -> list[str]:
    """Pure: `~` or `~/…` under every home it may mean."""
    return [h + text[1:] for h in homes]


def absolute_texts(text: str, homes: tuple[str, ...]) -> list[str] | None:
    """Pure: the absolute texts a file tool's path may name, or None when it is relative
    (its base, the session directory, is unknown) or `~user`."""
    if text.startswith("/"):
        return [text]
    if text == "~" or text.startswith("~/"):
        return home_texts(text, homes)
    return None


def terminal_texts(words: list[Word], base: str | None, homes: tuple[str, ...]) -> list[str]:
    """Pure: every absolute text the words may name: each word and each `=` value, `~` under
    every home, relative ones joined to `base` when it is known."""
    out: list[str] = []
    for word in words:
        if word.op or not word.text:
            continue
        values = [word.text] + ([word.text.split("=", 1)[1]] if "=" in word.text else [])
        for value in filter(None, values):
            if value.startswith("/"):
                out.append(value)
                continue
            if value == "~" or value.startswith("~/"):
                out += home_texts(value, homes)
            if base is not None:
                out.append(f"{base.rstrip('/')}/{value}")
    return out


def terminal_base(args: Mapping) -> str | None:
    """Pure: the terminal's directory when the fence knows it: an absolute `workdir`."""
    workdir = args.get("workdir")
    return workdir if isinstance(workdir, str) and workdir.startswith("/") else None


def patch_targets(text: str) -> list[Target] | str:
    """Pure: every path a V4A patch names, both ends of a move, read with Hermes's own markers
    on every line (inside the Begin/End range or not), each tagged as Hermes resolves it; or
    why the patch is refused: a `***` line that is none of Begin, End, Update, Add, Delete or
    Move."""
    targets: list[Target] = []
    for line in (ln.removesuffix("\r") for ln in text.split("\n")):
        if PATCH_BEGIN.match(line) or PATCH_END.match(line):
            continue
        found = next(((m, entry) for rx, entry in PATCH_OPS if (m := rx.match(line))), None)
        if found:
            match, entry = found
            targets += [Target(g.strip(), entry) for g in match.groups()]
        elif line.startswith("***"):
            return f"the patch has an operation the fence does not know: `{line[:60]}`"
    return targets


def write_targets(name: str, args: Mapping) -> list[Target] | str:
    """Pure: the paths a write tool's arguments name (`path`, and every path of a `patch`
    argument), or why the patch is refused."""
    targets = [Target(str(args[k])) for k in ("path", "file_path") if isinstance(args.get(k), str)]
    text = args.get("patch")
    if name == "patch" and isinstance(text, str):
        found = patch_targets(text)
        if isinstance(found, str):
            return found
        targets += found
    return targets


def strings(value: object) -> list[str]:
    """Pure: every string inside an argument value, nested lists and dicts included."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        return [s for v in value.values() for s in strings(v)]
    if isinstance(value, (list, tuple)):
        return [s for v in value for s in strings(v)]
    return []


def path_like(text: str) -> bool:
    """Pure: a string another tool may use as a path: one word, not a URL, with a slash or a
    leading `~` or `.`."""
    if not text or len(text) > 4096 or any(c.isspace() for c in text) or "://" in text:
        return False
    return "/" in text or text.startswith(("~", "."))


def pinned(text: str) -> dict[str, str] | str:
    """Pure: the paths file's `name=/absolute/path` lines (blank lines and `#` comments
    skipped) as a mapping holding every name of `PINNED` once and nothing else, each path
    absolute, normalised and free of `:` (it becomes a PATH entry); else why it is refused."""
    found: dict[str, str] = {}
    for line in (raw.strip() for raw in text.splitlines()):
        if not line or line.startswith("#"):
            continue
        name, sep, path = line.partition("=")
        if not sep or name not in PINNED:
            return f"{PATHS_FILE} has a line that is not `name=path` for one of {', '.join(PINNED)}"
        if name in found:
            return f"{PATHS_FILE} names {name} twice"
        if not path.startswith("/") or posixpath.normpath(path) != path or ":" in path:
            return f"{PATHS_FILE} pins {name} at a path that is not absolute and plain"
        found[name] = path
    missing = [name for name in PINNED if name not in found]
    if missing:
        return f"{PATHS_FILE} does not pin {', '.join(missing)}"
    return found
