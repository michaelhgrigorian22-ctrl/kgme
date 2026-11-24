"""Hermes's fence, the policy (HANDOFF-0073 §2): the verdict on one tool call, from `Facts`.

Purpose: the conductor (Opus through Hermes Agent) dispatches only through `kgme`. The fence
allows only what it fully understands and refuses the rest inside `~/Projects/KGME` (Cowork's
rulings on review cycles 1 and 2). Threat model (the cycle-2 ruling): the fence makes
accidental and casual writes by the conductor into KGME impossible and every dispatch
attributable; it is not a security boundary against a deliberately adversarial shell, which
only an OS-level sandbox gives. The rules:
- inside, the terminal runs one simple command, no operator, redirection, substitution,
  expansion or `cd`: the brain's own `kgme …` (never `approve`, `merge` or `skills install`,
  Michou's own acts), or `git status|log|diff|show` bare, no options and no paths; it runs
  rewritten, by the absolute path install.sh pinned in `~/.hermes/hooks/kgme-fence.paths`,
  under a clean environment whose `PATH` is the pinned programs' folders then the system's,
  never Hermes's inherited `PATH` (AUDIT-0178 F10), through Hermes's `modify` directive
  (`agent/shell_hooks.py:651-653`, merged at `hermes_cli/plugins.py:1162-1166`), because the
  terminal re-exports the session's variables (`tools/environments/base_session_env.py:198-242`);
- a terminal call is inside when Hermes's process directory is, when it has no absolute
  `workdir` (the session directory never reaches the hook, `tools/terminal_tool.py:256`), when
  the `workdir` is, or, outside, when its text read after quote removal and case-folding
  (`flat`) changes directory or names the root, when it does not lex, when it expands a
  variable, a substitution or a brace, or when it names a path that resolves inside;
- `execute_code` is refused everywhere; `write_file` and `patch` write inside only under
  `<checkout>/docs/handoff|adr|readers/` and `<checkout>/docs/STATUS.md`, every path absolute;
  Delete and Move are judged on the entry itself;
- any other tool naming a path inside the root must be a read tool (`READ_TOOLS`).
Inputs: a `Call` and the `Facts` the effects read (`kgme.hermes_fence.read_facts`), every path
in them canonical (symlinks resolved, components spelt as on disk).
Outputs: `Verdict`s. Side effects: none; everything here is pure.
"""

import shlex
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from kgme.hermes_fence_parse import (
    ASSIGNMENT,
    DIRECTORY_CHANGE,
    PINNED,
    Call,
    Target,
    absolute_texts,
    flat,
    home_texts,
    lex,
    path_like,
    simple_problem,
    strings,
    terminal_base,
    terminal_texts,
    write_targets,
)

ENV = "/usr/bin/env"
TERMINAL_TOOLS = ("terminal",)
WRITE_TOOLS = ("write_file", "patch")
CODE_TOOLS = ("execute_code",)
# Tools that only read; any tool not named here that names a path in the repo is refused.
READ_TOOLS = ("read_file", "search_files", "skill_view", "skills_list")
GIT_READS = ("status", "log", "diff", "show")
SYSTEM_PATH = ("/usr/bin", "/bin", "/usr/sbin", "/sbin")
KGME_REFUSED = {
    "approve": "`kgme approve` is Michou's approval, never the conductor's",
    "merge": "`kgme merge` lands on main, which is Michou's approval",
    "skills": "`kgme skills install` is Michou's command",
}
# What a rewritten command keeps of Hermes's own environment; HOME is the real home and PATH
# is built from the pinned programs (`child_path`), never inherited.
CLEAN_ENV = ("USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE", "TERM",
             "SSH_AUTH_SOCK", "KGME_CONDUCTOR")  # fmt: skip
GIT_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
UV_ENV = {"UV_NO_CONFIG": "1"}
WRITABLE_DIRS = ("handoff", "adr", "readers")
ROOT_NAME = "projects/kgme"


@dataclass(frozen=True)
class Verdict:
    """Allow or block, and why; `args`, when set, are the call's arguments as rewritten."""

    allow: bool
    reason: str = ""
    args: Mapping | None = None


ALLOW = Verdict(True)


@dataclass(frozen=True)
class Facts:
    """What the effects read, so the policy reads nothing: the root, the homes `~` may mean
    (the real one first), every path text resolved (glob matches included), every Delete and
    Move entry with its final component kept, the brain and its trusted `kgme`, the pinned
    programs (every name of `PINNED`), the clean env. Every path is canonical."""

    root: Path
    homes: tuple[str, ...]
    resolved: Mapping[str, tuple[Path, ...]]
    entries: Mapping[str, Path]
    trusted_kgme: Path
    brain: Path
    programs: Mapping[str, str]
    env: Mapping[str, str]


def block(reason: str) -> Verdict:
    """Pure: a refusal, its reason prefixed so Hermes's transcript names the fence."""
    return Verdict(False, f"kgme-fence: {reason}")


def within(path: Path, root: Path) -> bool:
    """Pure: `path` is `root` or under it (both canonical)."""
    return path == root or root in path.parents


def child_path(programs: Mapping[str, str]) -> str:
    """Pure: the `PATH` a rewritten command runs under: the pinned programs' folders in
    `PINNED` order, then `SYSTEM_PATH`, each once; every entry absolute by construction."""
    folders = [programs[name].rsplit("/", 1)[0] or "/" for name in PINNED if name in programs]
    return ":".join(dict.fromkeys([*folders, *SYSTEM_PATH]))


def clean_env(environ: Mapping[str, str], home: str, programs: Mapping[str, str]) -> dict[str, str]:
    """Pure: the environment a rewritten command runs under: the real home, the child `PATH`
    from the pinned programs, and the few variables of Hermes's own environment a program
    needs (`CLEAN_ENV`)."""
    kept = {k: environ[k] for k in CLEAN_ENV if k in environ}
    return {"HOME": home, "PATH": child_path(programs), **kept}


def wanted(call: Call, homes: tuple[str, ...]) -> tuple[set[str], set[str]]:
    """Pure: the absolute path texts the policy will look up for this call: those to resolve
    fully, and the Delete and Move entries."""
    texts: set[str] = set()
    entries: set[str] = set()
    if call.process_dir:
        texts.add(call.process_dir)
    if call.name in TERMINAL_TOOLS:
        base = terminal_base(call.args)
        if base:
            texts.add(base)
        words = lex(str(call.args.get("command", "")))
        if not isinstance(words, str):
            texts.update(terminal_texts(words, base, homes))
    elif call.name in WRITE_TOOLS:
        targets = write_targets(call.name, call.args)
        for target in targets if isinstance(targets, list) else []:
            (entries if target.entry else texts).update(absolute_texts(target.text, homes) or [])
    elif call.name not in READ_TOOLS:
        for text in filter(path_like, strings(call.args)):
            texts.update(absolute_texts(text, homes) or [])
    return texts, entries


def lands_inside(text: str, facts: Facts) -> bool:
    """Pure: the text resolves inside the root; a text nobody resolved counts as inside."""
    paths = facts.resolved.get(text)
    return paths is None or any(within(p, facts.root) for p in paths)


def names_root(text: str, facts: Facts) -> bool:
    """Pure: the flattened text names the root outright, in any case."""
    return ROOT_NAME in text or flat(str(facts.root)) in text


def why_inside(call: Call, facts: Facts) -> str | None:
    """Pure: why a terminal call counts as inside the root, or None when it is outside."""
    command = str(call.args.get("command", ""))
    base = terminal_base(call.args)
    if call.process_dir and lands_inside(call.process_dir, facts):
        return "Hermes was started inside ~/Projects/KGME"
    if base is None:
        return ("it has no absolute `workdir`; Hermes's session directory never reaches the "
                "hook, so it may run inside ~/Projects/KGME")  # fmt: skip
    if lands_inside(base, facts):
        return "its `workdir` is inside ~/Projects/KGME"
    text = flat(command)
    if DIRECTORY_CHANGE.search(text):
        return "it changes directory (read after quote removal), so its paths have no known base"
    if names_root(text, facts):
        return "it names ~/Projects/KGME (read after quote removal, in any case)"
    words = lex(command)
    if isinstance(words, str):
        return f"it does not lex ({words}), so where it acts is uncertain"
    if any(w.expands or "{" in w.marks for w in words):
        return "it expands a variable, a substitution or a brace the fence cannot see"
    if any(lands_inside(t, facts) for t in terminal_texts(words, base, facts.homes)):
        return "it names a path inside ~/Projects/KGME"
    return None


def kgme_plan(argv: list[str], facts: Facts) -> tuple[list[str], dict] | str | None:
    """Pure: when `argv` dispatches, the argv that runs the brain's own `kgme` and its extra
    env, or why it is refused; None when it is not a dispatch."""
    name, trusted = argv[0], str(facts.trusted_kgme)
    if name == "kgme":
        plan, rest, extra = [trusted], argv[1:], {}
    elif name.startswith("/") and facts.resolved.get(name, (None,))[0] == facts.trusted_kgme:
        plan, rest, extra = [trusted], argv[1:], {}
    elif name == "uv":
        project = argv[4] if len(argv) > 4 else ""
        brain = facts.resolved.get(project, (None,))[0] if project.startswith("/") else None
        if (
            argv[1:4] != ["run", "--frozen", "--project"]
            or argv[5:6] != ["kgme"]
            or (brain != facts.brain)
        ):
            return (
                f"dispatch through uv is exactly `uv run --frozen --project {facts.brain} kgme …`"
            )
        plan = [facts.programs["uv"], "run", "--frozen", "--project", str(facts.brain), "kgme"]
        rest, extra = argv[6:], UV_ENV
    elif name.rsplit("/", 1)[-1] == "kgme":
        return f"only the brain's own kgme dispatches ({trusted}, or `kgme`); not {name}"
    else:
        return None
    sub = next((a for a in rest if not a.startswith("-")), "")
    if sub == "skills" and "install" not in rest:
        return plan + rest, extra
    if sub in KGME_REFUSED:
        return KGME_REFUSED[sub]
    return plan + rest, extra


def command_plan(argv: list[str], facts: Facts) -> tuple[list[str], dict] | str:
    """Pure: the argv and extra env one simple command runs as, or why it is refused."""
    name = argv[0]
    if ASSIGNMENT.match(name):
        return f"a leading variable assignment (`{name}`) is refused"
    if name == "cd":
        return "`cd` is refused; name the folder as the terminal's absolute `workdir`"
    dispatch = kgme_plan(argv, facts)
    if dispatch is not None:
        return dispatch
    if name != "git":
        return (f"`{name}` is not one the conductor runs in ~/Projects/KGME: it runs kgme … and "
                "bare git status|log|diff|show; read files with read_file")  # fmt: skip
    if len(argv) != 2 or argv[1] not in GIT_READS:
        return ("git here is bare git status, log, diff or show, no options and no paths; "
                "a richer view is a read-only kgme subcommand; Michou runs git writes")  # fmt: skip
    return [facts.programs["git"], argv[1]], GIT_ENV


def judge_strict(call: Call, facts: Facts, why: str) -> Verdict:
    """Pure: an inside terminal call: one simple allowlisted command, rewritten to run by
    absolute path under a clean environment."""
    words = lex(str(call.args.get("command", "")))
    problem = words if isinstance(words, str) else simple_problem(words)
    if problem:
        return block(f"{problem} ({why})")
    argv = [home_texts(w.text, facts.homes)[0] if w.tilde else w.text for w in words]
    plan = command_plan(argv, facts)
    if isinstance(plan, str):
        return block(f"{plan} ({why})")
    program_argv, extra = plan
    env = {**facts.env, **extra}
    command = shlex.join([ENV, "-i", *(f"{k}={v}" for k, v in env.items()), *program_argv])
    return Verdict(True, "", {**call.args, "command": command})


def judge_terminal(call: Call, facts: Facts) -> Verdict:
    """Pure: the terminal rule."""
    if not isinstance(call.args.get("command"), str):
        return block("the terminal call names no command")
    why = why_inside(call, facts)
    return ALLOW if why is None else judge_strict(call, facts, why)


def writable(path: Path, root: Path) -> bool:
    """Pure: a path the conductor may write as architect: `<checkout>/docs/handoff|adr|readers/…`
    or `<checkout>/docs/STATUS.md`, `<checkout>` one folder under the root."""
    parts = path.relative_to(root).parts
    if len(parts) < 3 or parts[1] != "docs":
        return False
    return parts[2:] == ("STATUS.md",) or (len(parts) >= 4 and parts[2] in WRITABLE_DIRS)


def target_paths(target: Target, text: str, facts: Facts) -> tuple[Path | None, ...]:
    """Pure: where a write lands: the entry itself for Delete and Move, else the text resolved;
    None when nobody resolved it."""
    if target.entry:
        return (facts.entries.get(text),)
    return tuple(facts.resolved.get(text) or (None,))


def judge_write(call: Call, facts: Facts) -> Verdict:
    """Pure: `write_file` and `patch`: every target absolute, and inside only the architect's."""
    targets = write_targets(call.name, call.args)
    if isinstance(targets, str):
        return block(targets)
    if not targets:
        return block(f"{call.name} names no path the fence can check")
    for target in targets:
        texts = absolute_texts(target.text, facts.homes)
        if texts is None:
            return block(f"{call.name} needs an absolute path: `{target.text}` would resolve "
                         "against the session directory, which never reaches the hook")  # fmt: skip
        for path in (p for text in texts for p in target_paths(target, text, facts)):
            if path is None:
                return block(f"{call.name}: `{target.text}` was not resolved; refusing")
            if within(path, facts.root) and not writable(path, facts.root):
                return block(f"{call.name} may write in the repo only under docs/handoff/, "
                             f"docs/adr/, docs/readers/, docs/STATUS.md; not {path}")  # fmt: skip
    return ALLOW


def judge_other(call: Call, facts: Facts) -> Verdict:
    """Pure: a tool the fence does not know: refused when it names a relative path or one
    inside the root."""
    for text in filter(path_like, strings(call.args)):
        texts = absolute_texts(text, facts.homes)
        if texts is None:
            return block(f"`{call.name}` names a relative path (`{text[:80]}`) whose base the "
                         "fence cannot see; use an absolute path")  # fmt: skip
        if any(lands_inside(t, facts) for t in texts):
            return block(f"`{call.name}` names a path in ~/Projects/KGME and is not a read tool")
    return ALLOW


def judge(call: Call, facts: Facts) -> Verdict:
    """Pure: the verdict on one tool call."""
    if call.name in TERMINAL_TOOLS:
        return judge_terminal(call, facts)
    if call.name in CODE_TOOLS:
        return block("execute_code is refused: it runs in Hermes's session directory, which "
                     "never reaches the hook; dispatch through kgme")  # fmt: skip
    if call.name in WRITE_TOOLS:
        return judge_write(call, facts)
    if call.name in READ_TOOLS:
        return ALLOW
    return judge_other(call, facts)
