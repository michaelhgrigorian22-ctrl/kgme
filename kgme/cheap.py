"""The cheap lane: a code-only export, the session that grinds a red command in it, the fix home
as a diff (HANDOFF-0053).

Purpose: let a model whose provider's data class is `code` (Ollama's cloud) fix a failing
command without ever seeing `memory/`, `logs/`, or a Tier 1 path. The main checkout's `HEAD`
is exported minus `memory/` and `logs/` (bar `memory/templates/`, which the tests read and
which holds no personal content) into a folder under `work/`, initialised as its own
one-commit repository, so no object store holding `memory/` is reachable from it. The
session runs there; on exit the change is `git diff` against that one commit, written to
`logs/scratch/cheap/<run>/fix.patch` in the main checkout with the red command's final
output; the builder or the loop applies it in the real checkout and `kgme review` judges it.
The cheap model never touches the main checkout, `main`, or a push.
Inputs: the main checkout, the parsed `kgme.toml`, the run id, the red command.
Outputs: the export's path and tree hash; the patch's sha256 and the red command's status.
Side effects: `git archive` reads of the main checkout; files and a repository under
`work/cheap-<run>/`; `uv sync` there; the red command run there under `sandbox-exec`, since
it runs the session's code; the patch and the red output under `logs/scratch/`.
"""

import hashlib
import io
import re
import shlex
import subprocess
import tarfile
from pathlib import Path

from kgme import paths

PROVIDER_DEFAULT = "anthropic"
CODE = "code"
EXCLUDED = ("memory", "logs")
KEPT = ("memory/templates",)  # read by the tests; templates, no personal content
WORK_DIR = "~/Projects/KGME/work"
RED_TIMEOUT = 900
SHELL_SYNTAX = ";&|<>`$\n"
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
IDENTITY = ("-c", "user.name=kgme", "-c", "user.email=kgme@localhost")


def read_model(settings: dict, key: str) -> tuple[str, str, str]:
    """Pure: a `[models]` key's model id, its provider (`[models] <key>_provider`, else
    Anthropic), and that provider's data class (`[providers]`); `ValueError` when unset."""
    models = settings.get("models", {})
    model = models.get(key)
    if not model:
        raise ValueError(f"kgme.toml [models] {key} is not set")
    provider = models.get(f"{key}_provider", PROVIDER_DEFAULT)
    data_class = settings.get("providers", {}).get(provider)
    if not data_class:
        raise ValueError(f"kgme.toml [providers] {provider} has no data class")
    return model, provider, data_class


def read_red_argv(red: str) -> list[str]:
    """Pure: the red command as an argument list, never a shell string (ADR-015, review F3);
    `ValueError` for an empty command or shell syntax (separators, pipes, redirects,
    substitution, expansion), which an argument list would silently change."""
    if any(c in red for c in SHELL_SYNTAX):
        raise ValueError(f"the red command may not use shell syntax ({SHELL_SYNTAX!r}): {red}")
    argv = shlex.split(red)
    if not argv:
        raise ValueError("the red command is empty")
    return argv


def read_red_files(red: str) -> list[str]:
    """Pure: the repository-relative test files a red command names (`tests/...py`, a `::`
    node id cut to its file), in order, once each; they seed the carried slice and are the
    files the session may not edit."""
    found: list[str] = []
    for word in shlex.split(red):
        path = word.split("::", 1)[0]
        if path.startswith("tests/") and path.endswith(".py") and path not in found:
            found.append(path)
    return found


def build_prompt(red: str) -> str:
    """Pure: the session's instruction (HANDOFF-0053 §2)."""
    named = ", ".join(f"`{f}`" for f in read_red_files(red)) or "the tests it runs"
    return (
        f"Make `{red}` exit 0 without editing {named}. Work only in this directory. Stop as "
        "soon as it exits 0, when you reach the turn cap, or when a fix needs a file outside "
        "this directory; then say which."
    )


def read_work_dir(settings: dict, main: Path) -> Path:
    """Effect: the folder exports go in: `kgme.toml [paths] work_dir`, else
    `~/Projects/KGME/work`."""
    return paths.resolve(settings.get("paths", {}).get("work_dir", WORK_DIR), main)


def read_archive(main: Path, pathspecs: list[str]) -> bytes:
    """Effect: `git archive` of the main checkout's `HEAD` for `pathspecs`, as tar bytes."""
    done = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD", "--", *pathspecs],
        cwd=main,
        capture_output=True,
        check=True,
    )
    return done.stdout


def write_export(main: Path, settings: dict, run: str) -> tuple[Path, str]:
    """Effect: `HEAD` minus `memory/` and `logs/`, plus `memory/templates/`, extracted into
    `work/cheap-<run>/` and committed there as a fresh one-commit repository on `main`, its
    environment synced; returns the export and its tree hash. `FileExistsError` if the folder
    is already there."""
    export = read_work_dir(settings, main) / f"cheap-{run}"
    export.mkdir(parents=True, exist_ok=False)
    excludes = [f":(exclude){e}" for e in EXCLUDED]
    tracked = subprocess.run(
        ["git", "ls-tree", "-d", "--name-only", "HEAD", *KEPT], cwd=main, capture_output=True,
        text=True, check=True,
    ).stdout.split()  # fmt: skip
    for spec in ([".", *excludes], tracked):
        if not spec:
            continue
        with tarfile.open(fileobj=io.BytesIO(read_archive(main, spec))) as archive:
            archive.extractall(export, filter="data")
    git = ["git", *IDENTITY, "-c", "core.hooksPath=/dev/null"]
    subprocess.run([*git, "init", "-q", "-b", "main"], cwd=export, check=True)
    subprocess.run([*git, "add", "-A"], cwd=export, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "cheap lane export"], cwd=export, check=True)
    if (export / "uv.lock").is_file():  # the session runs `uv run` with no sync (uv_env)
        subprocess.run(["uv", "sync", "--frozen", "--quiet"], cwd=export, check=True)
    tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=export, capture_output=True, text=True, check=True
    ).stdout.strip()
    return export, tree


def quote_sbpl(path: Path) -> str:
    """Pure: `path` as a Seatbelt string literal."""
    return '"' + str(path).replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_name_regex(glob: str) -> str:
    """Pure: a blocklist name glob (`.env`, `.env.*`, `*.env`) as a Seatbelt regex matching
    a file of that name in any folder."""
    return "^.*/" + re.escape(glob).replace(r"\*", "[^/]*") + "$"


def build_red_profile(export: Path, mains: list[Path], denied: list[Path], names: list[str]) -> str:
    """Pure: the Seatbelt profile the launcher's own run of the red command runs under. That
    run executes code the session wrote, so it gets the session's fence (review F1): no
    network, no read under a denied root or of a file a name pattern covers (cycle 2 F1),
    writes only to the export, the temporary folders, and `/dev`, and never to a main
    checkout, wherever it lives (HANDOFF-0057): `mains` are the main checkout the launch is
    for and the checkout this code runs from, the same folder in use and two in a merge
    trial's clone, which sits under the temporary folders. In Seatbelt a later rule wins, so
    the writes are: deny all; allow the temporary folders and `/dev`; deny each main
    checkout; allow the export last, so an export under a checkout stays writable."""
    temporary = [Path("/private/tmp"), Path("/private/var/folders"), Path("/dev")]
    allowed = " ".join(f"(subpath {quote_sbpl(p)})" for p in temporary)
    checkouts = " ".join(f"(subpath {quote_sbpl(m)})" for m in dict.fromkeys(mains))
    refused = [f"(subpath {quote_sbpl(r)})" for r in denied]
    refused += [f'(regex #"{build_name_regex(n)}")' for n in names]
    return (
        "(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n"
        f"(allow file-write* {allowed})\n(deny file-write* {checkouts})\n"
        f"(allow file-write* (subpath {quote_sbpl(export)}))\n"
        f"(deny file-read* {' '.join(refused)})\n"
    )


def write_fix(
    export: Path, main: Path, settings: dict, run: str, red: str, denied: list[Path]
) -> dict:
    """Effect: the session's change as `fix.patch` (every file, new ones included, against
    the export's one commit) and the red command's final output, run under
    `build_red_profile`, under the main checkout's `logs/scratch/cheap/<run>/`; returns the
    patch's sha256, its size, the red command's exit status, and the two paths, relative to
    the main checkout."""
    out = paths.scratch_dir(settings, main) / "cheap" / run
    out.mkdir(parents=True, exist_ok=True)
    git = ["git", *IDENTITY, "-c", "core.hooksPath=/dev/null"]
    # whatever a session leaves under memory/ or logs/ stays out of the fix (found live)
    kept = ["--", ".", *(f":(exclude){e}" for e in EXCLUDED)]
    subprocess.run([*git, "add", "-A", *kept], cwd=export, check=True)
    patch = subprocess.run(
        [*git, "diff", "--cached", "--binary", "HEAD", *kept], cwd=export, capture_output=True,
        check=True,
    ).stdout  # fmt: skip
    (out / "fix.patch").write_bytes(patch)
    import os

    from kgme import session

    mains = [main.resolve(), paths.root().resolve()]
    profile = build_red_profile(export.resolve(), mains, denied, read_denied_names(settings))
    argv = [SANDBOX_EXEC, "-p", profile, *read_red_argv(red)]
    try:
        ran = subprocess.run(
            argv, cwd=export, capture_output=True, text=True, timeout=RED_TIMEOUT,
            env=os.environ | session.uv_env(export),
        )  # fmt: skip
        status, output = ran.returncode, ran.stdout + ran.stderr
    except subprocess.TimeoutExpired:
        status, output = -1, f"the red command ran past {RED_TIMEOUT}s"
    (out / "red.txt").write_text(f"$ {red}\nexit {status}\n\n{output}", encoding="utf-8")
    return {
        "patch": (out / "fix.patch").relative_to(main).as_posix(),
        "patch_sha256": hashlib.sha256(patch).hexdigest(),
        "patch_bytes": len(patch),
        "red_output": (out / "red.txt").relative_to(main).as_posix(),
        "red_status": status,
    }


TEMPLATE = "cheap.json"
OLLAMA_URL = "http://localhost:11434"
# every model slot Claude Code uses, pinned to the one model (code.claude.com docs, model-config
# and env-vars, read 2026-10-22; ANTHROPIC_SMALL_FAST_MODEL is deprecated for the haiku slot)
MODEL_SLOTS = (
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_FABLE_MODEL",
    "CLAUDE_CODE_SUBAGENT_MODEL",
)
QUIET = {  # no traffic to Anthropic but the session's own, and no pre-release request fields
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
    "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1",
}
HOOK = (  # the main checkout's code, failing closed as control/hooks/pre_tool_guard.sh does;
    # `-P`: without it `python -m` puts the export first on sys.path, so the export's own
    # `kgme` ran and wrote the export's ledger (found live, 2026-10-22)
    '{pin}uv run --frozen --project "{main}" python -P -m kgme.hooks.{module}; code=$?; '
    '[ "$code" -eq 0 ] && exit 0; {tail}'
)
# the export the guard judges paths against, set on the guard's command line alone: the main
# checkout's code then took the main checkout as its repository and refused every edit in the
# export (found live, 2026-10-22); `kgme.hooks.common.read_guard_root` honours it
GUARD_ROOT_ENV = "KGME_GUARD_ROOT"


def read_denied_roots(settings: dict, main: Path) -> list[Path]:
    """Effect: the folders a cheap session may not read: the brain (the main checkout), the
    design worktree, `~/Projects/Finance`, every Tier 1 root (HANDOFF-0053 §2), and the
    agents' own homes, `~/.claude` (every project's memory and transcripts, the global
    instructions) and `~/.codex`, which the guard's `allow_outside` otherwise opens to the
    file tools (review F2), and the guard's absolute blocklist entries (`~/.ssh`, the
    Keychains, the credential files), which the permission rules alone left readable to a
    script that builds the path (review cycle 2 F1)."""
    home = Path.home()
    kgme = home / "Projects" / "KGME"
    roots = [main, kgme / "brain", kgme / "design", home / "Projects" / "Finance"]
    roots += [home / ".claude", home / ".codex"]
    roots += paths.tier1_paths(settings, main)
    blocklist = settings.get("hooks", {}).get("blocklist", [])
    roots += [Path(p).expanduser() for p in blocklist if p.startswith("~/") or p.startswith("/")]
    return sorted({r.resolve() for r in roots})


def read_denied_names(settings: dict) -> list[str]:
    """Pure: the guard's name patterns (`[hooks] blocklist` entries `**/<glob>`: the `.env`
    files), which hold under every folder."""
    return [p[3:] for p in settings.get("hooks", {}).get("blocklist", []) if p.startswith("**/")]


def build_env(model: str, settings: dict) -> dict[str, str]:
    """Pure: the environment a cheap session starts with: Ollama's Anthropic endpoint, its
    placeholder token (Ollama's own, no secret), no Anthropic key, every slot on `model`."""
    url = settings.get("providers", {}).get("ollama_url", OLLAMA_URL)
    env = {"ANTHROPIC_BASE_URL": url, "ANTHROPIC_AUTH_TOKEN": "ollama", "ANTHROPIC_API_KEY": ""}
    return env | {slot: model for slot in MODEL_SLOTS} | QUIET


def build_policy(
    rendered: dict,
    main: Path,
    denied: list[Path],
    main_deny: list[str],
    export: Path | None,
    names: list[str],
) -> dict:
    """Pure: the cheap session's settings: the rendered template, the main checkout's deny
    rules, `Read` and `Edit` denied on every denied root and the sandbox's `denyRead` on the
    same (the permission rule covers the file tools and recognised Bash file commands; only
    the sandbox stops any subprocess), the guard's name patterns as `~/**/<name>` wildcard
    denies in `denyRead`, so a script that builds a `.env` path at run time is refused too
    (review cycle 3 F8; the wildcard form is the sandbox's documented one), and the guard and
    ledger hooks run from the main checkout's code so their records land in its ledger, never
    the export's; the guard judges paths against `export` (none on a dry run)."""
    roots = [str(r) for r in denied]
    deny = list(dict.fromkeys([
        *(rendered.get("permissions") or {}).get("deny", []), *main_deny,
        *(f"Read(/{r}/**)" for r in roots), *(f"Edit(/{r}/**)" for r in roots),
    ]))  # fmt: skip
    sandbox = dict(rendered.get("sandbox") or {})
    filesystem = dict(sandbox.get("filesystem") or {})
    wildcards = [f"~/**/{n}" for n in names]
    filesystem["denyRead"] = list(
        dict.fromkeys([*filesystem.get("denyRead", []), *roots, *wildcards])
    )
    sandbox["filesystem"] = filesystem
    pin = f'{GUARD_ROOT_ENV}="{export}" ' if export else ""
    guard = HOOK.format(pin=pin, main=main, module="pre_tool_guard", tail="exit 2")
    ledger_hook = HOOK.format(pin="", main=main, module="post_tool_ledger", tail="exit 0")
    hooks = {
        "PreToolUse": [{"matcher": "", "hooks": [{"type": "command", "command": guard}]}],
        "PostToolUse": [{"matcher": "", "hooks": [{"type": "command", "command": ledger_hook}]}],
    }
    permissions = {**(rendered.get("permissions") or {}), "deny": deny}
    return {**rendered, "permissions": permissions, "sandbox": sandbox, "hooks": hooks,
            "disableAllHooks": False}  # fmt: skip


def read_cheap_launch(
    key: str, red: str, base: Path, settings: dict, run: str, export: Path | None
) -> tuple:
    """Effect: what a cheap session starts with, built against `export` (the main checkout
    when a dry run has none): the launch (argv, environment, settings, carried prompt) and
    the record its start note carries. `ValueError` naming what is missing."""
    import json
    import tempfile

    from kgme import ledger, session
    from kgme.session_logic import render

    model, provider, data_class = read_model(settings, key)
    read_red_argv(red)
    main = ledger.read_main_checkout(base)
    template_path = main / session.TEMPLATES / TEMPLATE
    if not template_path.is_file() or template_path.is_symlink():
        raise ValueError(f"{template_path.relative_to(main)} is missing; Michou applies it")
    caps = settings.get("sessions", {})
    if "max_turns" not in caps:
        raise ValueError("kgme.toml [sessions] max_turns is not set")
    where = export or main
    template_text = template_path.read_text(encoding="utf-8")
    rendered = render(json.loads(template_text), where, Path(tempfile.gettempdir()).resolve())
    denied = read_denied_roots(settings, main)
    main_deny = (session.read_main_policy(main).get("permissions") or {}).get("deny", [])
    policy = build_policy(rendered, main, denied, main_deny, export, read_denied_names(settings))
    body = json.dumps(policy, indent=2, sort_keys=True)
    body += "\n"
    copy = paths.scratch_dir(settings, main) / "sessions" / run / TEMPLATE
    carried_text, carried = session.read_carried_prompt(
        main, where, settings, None, tuple(read_red_files(red))
    )
    claude_path = copy.with_name("CLAUDE.md")
    argv = [
        "claude", "--setting-sources", "local", "--settings", str(copy), "--model", model,
        "-p", "--permission-prompts", "none", "--max-turns", str(caps["max_turns"]),
        "--output-format", "json", "--append-system-prompt-file", str(claude_path),
        build_prompt(red),
    ]  # fmt: skip
    env = build_env(model, settings) | session.uv_env(where)
    record = {
        "level": "work",
        "lane": "cheap",
        "handoff": None,
        "model_key": key,
        "model": model,
        "provider": provider,
        "data_class": data_class,
        "red": red,
        "red_files": read_red_files(red),
        "export": str(export) if export else None,
        "denied_roots": [str(r) for r in denied],
        "template": template_path.relative_to(main).as_posix(),
        "template_sha256": session.sha256_text(template_text),
        "settings": copy.relative_to(main).as_posix(),
        "settings_sha256": session.sha256_text(body),
        "claude_md": claude_path.relative_to(main).as_posix(),
        "claude_md_sha256": session.sha256_text(carried_text),
        **carried,
        "env": dict(sorted(env.items())),
        "argv": argv,
        "claude_version": session.read_claude_version(),
    }
    return session.Launch(argv, env, body, carried_text), record


def read_session_result(stdout: str) -> tuple[str, int | None]:
    """Pure: the exit reason and turn count from `claude -p --output-format json`."""
    import json

    try:
        result = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else {}
    except (json.JSONDecodeError, IndexError):
        return "unreadable output", None
    return str(result.get("subtype") or result.get("type") or "unknown"), result.get("num_turns")


def run_cheap(
    key: str,
    red: str,
    base: Path,
    settings: dict,
    dry_run: bool = False,
    run_claude=subprocess.run,
) -> int:
    """`kgme session work --model <key> --red "<command>"`: export, start note, the session in
    the export, the fix and the red command's final output, end note. A dry run prints the
    launch built against the main checkout and writes one note, no export. Exit 0 when the
    red command ends green, 1 when it does not, 2 when the launch is refused or, after the
    start note, the launch or the patch fails; the end note is written either way."""
    import json
    import os
    import sys

    from kgme import events, ledger, session

    run = events.new_ulid()
    dirs = ledger.read_default_dirs(settings, base)
    try:
        if dry_run:
            launch, record = read_cheap_launch(key, red, base, settings, run, None)
            print(" ".join(launch.argv))
            print(launch.settings, end="")
            print(f"--- carried: {', '.join(record['carried'])} ---")
            print(launch.claude_md, end="")
            summary = f"session work cheap dry run: model={record['model']} red={red}"
            ledger.append(events.make_event(
                source="kgme", actor="kgme.session", kind="note", job="session",
                key="session:work:cheap:dry-run", summary=events.clip(summary),
            ), dirs)  # fmt: skip
            return 0
        read_red_argv(red)
        main = ledger.read_main_checkout(base)
        export, tree = write_export(main, settings, run)
        launch, record = read_cheap_launch(key, red, base, settings, run, export)
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"kgme session: {error}", file=sys.stderr)
        return 2
    record["export_tree"] = tree
    env = session.write_start(record, launch, base, settings, run, dirs)
    # from here every way out writes the end note (review F4)
    out = paths.scratch_dir(settings, main) / "cheap" / run
    failed = None
    try:
        done = run_claude(
            launch.argv, cwd=export, env={**os.environ, **env}, capture_output=True, text=True
        )
        reason, turns, exit_code = *read_session_result(done.stdout or ""), done.returncode
        out.mkdir(parents=True, exist_ok=True)
        (out / "session.json").write_text(done.stdout or "", encoding="utf-8")
    except (OSError, subprocess.SubprocessError) as error:
        reason, turns, exit_code = f"launch failed: {type(error).__name__}: {error}", None, None
        failed = reason
    denied = [Path(r) for r in record["denied_roots"]]
    try:
        fix = write_fix(export, main, settings, run, red, denied)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        fix = dict.fromkeys(("patch", "patch_sha256", "patch_bytes", "red_output", "red_status"))
        failed = f"patch failed: {type(error).__name__}: {error}"
        reason = f"{reason}; {failed}"
    end = {"exit_code": exit_code, "exit_reason": reason, "turns": turns, **fix}
    payload_text = json.dumps(end, indent=2, sort_keys=True) + "\n"
    payload = paths.payloads_dir(settings, main) / f"session-{run}-end.json"
    from kgme import clean_fs

    clean_fs.write_payload(main, payload, payload_text)
    summary = (
        f"session work cheap end: {reason}, {turns} turns, patch sha256="
        f"{(fix['patch_sha256'] or 'none')[:16]}, red exit {fix['red_status']}"
    )
    ledger.append(events.make_event(
        source="kgme", actor="kgme.session", kind="note", job="session",
        key="session:work:cheap:end", run_id=run, summary=events.clip(summary),
        payload_ref=payload.relative_to(main).as_posix(),
        payload_sha256=session.sha256_text(payload_text),
    ), dirs)  # fmt: skip
    if failed:
        print(f"kgme session: {summary}", file=sys.stderr)
        return 2
    print(f"kgme session: {summary}; the fix is {fix['patch']}")
    return 0 if fix["red_status"] == 0 else 1
