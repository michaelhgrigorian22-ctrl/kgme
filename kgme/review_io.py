"""`kgme review`, the effects primitives: the diff, the gate, the reviewer, files, events.

Purpose: every place the review loop touches the world, one named function each (ADR-015),
so `kgme.review_run` can orchestrate a cycle without opening a file or a process itself.
Inputs: the repository root and the places `kgme.toml` names; prompts and texts.
Outputs: strings, paths, event lists, a `Places`.
Side effects: `read_*` open files or run read-only commands; `write_*` create or append files;
`run_*` start subprocesses as argument lists, never through a shell.
"""

import hashlib
import os
import re
import string
import subprocess
from dataclasses import dataclass
from pathlib import Path

from kgme import config, events, ledger, paths, review_parse

AUDIT_ID = re.compile(r"^id:\s*AUDIT-(\d{4})", re.MULTILINE)
REVIEWER_TIMEOUT_SECONDS = 600


@dataclass(frozen=True)
class Places:
    """Everything a cycle writes to or reads from, resolved once from `kgme.toml`."""

    dirs: ledger.Dirs
    audit_dir: Path
    scratch: Path
    payloads: Path
    handoff_dir: Path
    prompt_path: Path
    root: Path
    # the tree under review when it is not the main checkout: a KGME workspace under
    # `[crew] root` (HANDOFF-0048 amendment 2); the diff, the gate and the reviewer's cwd are
    # its, the ledger, the audits and the scratch stay the main checkout's
    workspace: Path | None = None

    @property
    def tree(self) -> Path:
        """The checkout the diff and the gate are read from."""
        return self.workspace or self.root


def read_places(test_streams: bool, workspace: Path | None = None) -> Places:
    """The real places, or the gitignored test streams and test scratch under `--test-streams`;
    `workspace` when the review is of a KGME workspace's staged diff."""
    settings = config.read_config()
    # review runs in the main checkout only (0047 review cycle 3 F12), so this is the record
    # root; the workspace, when there is one, is the tree under review (HANDOFF-0048)
    root = paths.root()
    handoff_dir = paths.handoff_dir(settings)
    if test_streams:
        scratch = paths.scratch_test_dir(settings)
        dirs = ledger.read_test_dirs(settings)
        audit_dir, payloads = scratch / "audit", paths.payloads_dir(settings, root) / "test"
        # a toy handoff under the test scratch, so a live route cell (HANDOFF-0048) reviews
        # a handoff that never enters docs/handoff/, a human path
        if (scratch / "handoff").is_dir():
            handoff_dir = scratch / "handoff"
    else:
        scratch = paths.scratch_dir(settings)
        dirs = ledger.read_default_dirs(settings)
        audit_dir, payloads = paths.audit_dir(settings), paths.payloads_dir(settings, root)
    return Places(
        dirs,
        audit_dir,
        scratch,
        payloads,
        handoff_dir,
        paths.review_prompt(settings),
        root,
        workspace,
    )


def read_staged_patch(root: Path) -> str:
    """`git diff --staged`, the diff the loop binds to."""
    done = subprocess.run(
        ["git", "diff", "--staged"], capture_output=True, text=True, cwd=root, check=True
    )
    return done.stdout


def sha256_text(text: str) -> str:
    """Hex digest of a string, the identity of a reviewed diff."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path: Path, text: str) -> None:
    """Create or replace one text file, parents included."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(path: Path) -> str:
    """One text file, decoding errors replaced."""
    return path.read_text(encoding="utf-8", errors="replace")


# what a gate must not inherit from the session that runs it: a loose builder's loop-mode
# fence and test-stream routing would reach the hook tests, and another checkout's
# virtual environment would be ignored with a warning on every uv call (HANDOFF-0048, the
# live route of 2026-10-27: 21 red tests in a workspace, 6 of them the suite's own worktree
# assumptions, the rest the inherited KGME_LOOP_* and KGME_TEST_STREAMS)
GATE_STRIPS = (
    "KGME_LOOP", "KGME_TEST_STREAMS", "KGME_GUARD_ROOT", "VIRTUAL_ENV", "UV_NO_SYNC",
    "UV_CACHE_DIR", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT",
)  # fmt: skip


def gate_env(environ: dict[str, str]) -> dict[str, str]:
    """Pure: the gate's environment: `environ` without the variables a session carries."""
    return {k: v for k, v in environ.items() if not k.startswith(GATE_STRIPS)}


def run_make_check(root: Path) -> tuple[int, str]:
    """The gate, in `root` (the tree under review), in a clean environment. A red gate is
    not reviewed."""
    done = subprocess.run(
        ["make", "check"], capture_output=True, text=True, cwd=root, env=gate_env(dict(os.environ))
    )
    return done.returncode, done.stdout[-2000:] + done.stderr[-2000:]


CLAUDE_REVIEWER_TURNS = 40


def reviewer_argv(model: str, prompt: str, out_path: Path) -> tuple[list[str], str | None]:
    """Pure: the reviewer's read-only run and what goes on its stdin: a `claude-` model
    through `claude -p` with the read-only tools alone, the prompt on stdin (HANDOFF-0048
    amendment 3: a Claude reviewer for a Codex-built task); any other model through
    `codex exec --json -s read-only` with the prompt as its argument and stdin closed, as
    always."""
    if not model.startswith("claude-"):
        argv = ["codex", "exec", "--json", "-s", "read-only", "-m", model, "-o", str(out_path)]
        return argv + [prompt], None
    argv = ["claude", "-p", "--model", model, "--permission-mode", "dontAsk"]
    argv += ["--max-turns", str(CLAUDE_REVIEWER_TURNS), "--tools", "Read,Grep,Glob"]
    argv += ["--output-format", "text"]
    return argv, prompt


def run_reviewer(
    prompt: str, model: str, root: Path, out_path: Path, stream_path: Path
) -> tuple[int, str, str]:
    """The reviewer, read-only, hard timeout (reviewer-hang lesson), in `root` (the tree
    under review).

    Returns the exit code, the reviewer's last message, and stderr. 124 is the timeout, 127
    means the harness is not on PATH. Codex's JSON Lines stream lands in `stream_path` for
    the payload; a Claude reviewer's text is its reply, and the stream file holds it too.
    """
    write_text(stream_path, "")
    if out_path.exists():
        out_path.unlink()
    argv, on_stdin = reviewer_argv(model, prompt, out_path)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "KGME_LOOP"))}
    try:
        done = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL if on_stdin is None else None,
            input=on_stdin,
            capture_output=True,
            text=True,
            cwd=root,
            env=env,
            timeout=REVIEWER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError:
        return 127, "", f"{argv[0]} not found"
    write_text(stream_path, done.stdout)
    if on_stdin is not None:
        return done.returncode, done.stdout, done.stderr
    text = read_text(out_path) if out_path.exists() else ""
    return done.returncode, text, done.stderr


NOT_ADOPTED = ("proposed", "archive")


def read_handoff_path(handoff_dir: Path, handoff_id: str) -> Path | None:
    """The adopted handoff file whose frontmatter carries `id: <handoff_id>`, else None: open
    at the top of `docs/handoff/` or finished under `done/` (HANDOFF-0049), never a proposal
    or an archived one. A review unit `HANDOFF-NNNN:<task>` (a crew task, a plan, an
    integration; HANDOFF-0048) names its handoff before the colon."""
    handoff_id = handoff_id.partition(":")[0]
    pattern = re.compile(rf"^id:\s*{re.escape(handoff_id)}\s*$", re.MULTILINE)
    for path in sorted(handoff_dir.rglob("*.md")):
        if path.relative_to(handoff_dir).parts[0] in NOT_ADOPTED:
            continue
        if pattern.search(read_text(path)):
            return path
    return None


def read_next_audit_number(audit_dir: Path) -> int:
    """One more than the highest AUDIT-NNNN id in the directory."""
    highest = 0
    for path in audit_dir.glob("*.md"):
        match = AUDIT_ID.search(read_text(path))
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def read_audit_table(audit_dir: Path, audit_id: str) -> str:
    """The Findings table of the audit file carrying `audit_id`, empty if there is none."""
    pattern = re.compile(rf"^id:\s*{re.escape(audit_id)}\s*$", re.MULTILINE)
    for path in audit_dir.glob("*.md"):
        text = read_text(path)
        if pattern.search(text):
            return (review_parse.section(text, "Findings") or "").strip()
    return ""


def render_prompt(template: str, fields: dict[str, str]) -> str:
    """`$NAME` placeholders substituted; unknown ones left alone, braces untouched."""
    return string.Template(template).safe_substitute(fields)


def write_payload(payloads_dir: Path, name: str, text: str, root: Path) -> tuple[str, str]:
    """A disposable payload file under scratch; returns its repo-relative path and sha256."""
    target = payloads_dir / name
    write_text(target, text)
    return str(target.relative_to(root)), sha256_text(text)


def shown(path: Path, root: Path) -> str:
    """A path as the prompt and the console show it: repo-relative when under the root."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_handoff_events(handoff: str, dirs: ledger.Dirs) -> list[dict]:
    """Every ledger event of one handoff's review loop, in id order."""
    return [e for e in ledger.read(dirs, stream="ledger") if e["job"] == f"review:{handoff}"]


def first_intent_id(handoff_events: list[dict]) -> str | None:
    """The root of the loop's tree: its first intent, else None."""
    intents = [e for e in handoff_events if e["kind"] == "intent"]
    return intents[0]["id"] if intents else None


def write_ruling(
    handoff: str, finding_id: str, cls: str, reason: str, arbiter: str, places: Places
) -> str | None:
    """The arbiter's ruling on one finding, once. A second ruling on the same finding is refused."""
    history = read_handoff_events(handoff, places.dirs)
    already = any(
        (e["key"] or "").startswith(f"ruling:{finding_id}=") for e in history if e["kind"] == "note"
    )
    if already:
        return None
    # the summary is clipped to the writer's cap; the whole ruling (the option and the reason,
    # a split's every option) goes with it as a payload, which a builder's next request reads
    # (HANDOFF-0048 review cycle 3 F6)
    text = f"arbiter {arbiter} ruled {finding_id}={cls}: {reason}"
    payload_ref, digest = write_payload(
        places.payloads, f"ruling-{handoff}-{finding_id}-settled-{events.new_ulid()}.txt",
        text + "\n", places.root,
    )  # fmt: skip
    return ledger.append(
        events.make_event(
            source="kgme",
            actor=f"arbiter.{arbiter}",
            kind="note",
            job=f"review:{handoff}",
            key=f"ruling:{finding_id}={cls}",
            parent=first_intent_id(history),
            summary=events.clip(text),
            payload_ref=payload_ref,
            payload_sha256=digest,
        ),
        places.dirs,
    )


def read_ruling_text(event: dict, root: Path) -> str:
    """Effect: a settled ruling whole: its payload when the note has one and it is intact,
    else its (clipped) summary."""
    if event.get("payload_ref"):
        path = root / str(event["payload_ref"])
        try:
            text = read_text(path)
        except OSError:
            return str(event.get("summary") or "")
        if sha256_text(text) == event.get("payload_sha256"):
            return text.rstrip("\n")
    return str(event.get("summary") or "")


def write_override(handoff: str, reason: str, places: Places) -> str:
    """Michou's override of a halt: an `approval` clearing the strike history, not rulings."""
    history = read_handoff_events(handoff, places.dirs)
    return ledger.append(
        events.make_event(
            source="human",
            actor="michou",
            kind="approval",
            job=f"review:{handoff}",
            key=f"override:{handoff}",
            parent=first_intent_id(history),
            summary=events.clip(f"override review halt {handoff}: {reason}"),
        ),
        places.dirs,
    )
