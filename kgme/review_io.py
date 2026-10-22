"""`kgme review`, the effects primitives: the diff, the gate, the reviewer, files, events.

Purpose: every place the review loop touches the world, one named function each (ADR-015),
so `kgme.review_run` can orchestrate a cycle without opening a file or a process itself.
Inputs: the repository root and the places `kgme.toml` names; prompts and texts.
Outputs: strings, paths, event lists, a `Places`.
Side effects: `read_*` open files or run read-only commands; `write_*` create or append files;
`run_*` start subprocesses as argument lists, never through a shell.
"""

import hashlib
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


def read_places(test_streams: bool) -> Places:
    """The real places, or the gitignored test streams and test scratch under `--test-streams`."""
    settings = config.read_config()
    # review runs in the main checkout only (0047 review cycle 3 F12), so this is the record
    # root as well as the workspace
    root = paths.root()
    if test_streams:
        scratch = paths.scratch_test_dir(settings)
        dirs = ledger.read_test_dirs(settings)
        audit_dir, payloads = scratch / "audit", paths.payloads_dir(settings, root) / "test"
    else:
        scratch = paths.scratch_dir(settings)
        dirs = ledger.read_default_dirs(settings)
        audit_dir, payloads = paths.audit_dir(settings), paths.payloads_dir(settings, root)
    return Places(
        dirs,
        audit_dir,
        scratch,
        payloads,
        paths.handoff_dir(settings),
        paths.review_prompt(settings),
        root,
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


def run_make_check(root: Path) -> tuple[int, str]:
    """The gate. A red gate is not reviewed."""
    done = subprocess.run(["make", "check"], capture_output=True, text=True, cwd=root)
    return done.returncode, done.stdout[-2000:] + done.stderr[-2000:]


def run_reviewer(
    prompt: str, model: str, root: Path, out_path: Path, stream_path: Path
) -> tuple[int, str, str]:
    """`codex exec --json`, read-only, stdin closed, hard timeout (reviewer-hang lesson).

    Returns the exit code, the reviewer's last message, and stderr. 124 is the timeout, 127
    means no `codex` on PATH. The JSON Lines stream lands in `stream_path` for the payload.
    """
    write_text(stream_path, "")
    if out_path.exists():
        out_path.unlink()
    argv = ["codex", "exec", "--json", "-s", "read-only", "-m", model, "-o", str(out_path), prompt]
    try:
        done = subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            cwd=root,
            timeout=REVIEWER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError:
        return 127, "", "codex not found"
    write_text(stream_path, done.stdout)
    text = read_text(out_path) if out_path.exists() else ""
    return done.returncode, text, done.stderr


NOT_ADOPTED = ("proposed", "archive")


def read_handoff_path(handoff_dir: Path, handoff_id: str) -> Path | None:
    """The adopted handoff file whose frontmatter carries `id: <handoff_id>`, else None: open
    at the top of `docs/handoff/` or finished under `done/` (HANDOFF-0049), never a proposal
    or an archived one."""
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
    return ledger.append(
        events.make_event(
            source="kgme",
            actor=f"arbiter.{arbiter}",
            kind="note",
            job=f"review:{handoff}",
            key=f"ruling:{finding_id}={cls}",
            parent=first_intent_id(history),
            summary=events.clip(f"arbiter {arbiter} ruled {finding_id}={cls}: {reason}"),
        ),
        places.dirs,
    )


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
