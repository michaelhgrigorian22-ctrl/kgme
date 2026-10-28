"""`kgme approve`: Michou's approval of a thing at a commit, as a ledger event (HANDOFF-0055).

Purpose: make sign-off a separate act from the merge. `kgme approve --what <name> --sha <commit>
[--note "<words>"]` appends one `approval` event, source `human`, actor `michou`, keyed
`approve:<name>:<full sha>`; `kgme approve --show <name>` prints the newest one. It refuses a
commit not on `main`, and refuses to run under an agent harness: Claude Code sets `CLAUDECODE`
and `CLAUDE_CODE_ENTRYPOINT` in the environment of every command it runs, and Codex sets
`CODEX_SANDBOX`, `CODEX_THREAD_ID`, and `CODEX_SESSION_ID` (names read in each, 2026-10-21).
`.claude/settings.json` also denies `Bash(*kgme approve*)`. HANDOFF-0037 builds only from the
newest `canvas` approval's commit.
Inputs: the checkout (any worktree), the parsed `kgme.toml`, the name, the commit, the note.
Outputs: an exit code (0 recorded or shown, 1 none to show, 2 refused); a line on stdout or
stderr.
Side effects: git reads in the main checkout; one ledger event in its streams.
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from kgme import events, ledger
from kgme.merge import TRUNK, read_sha
from kgme.sync_git import run_git

JOB = "approve"
AGENT_MARKERS = (
    "CLAUDECODE",
    "CLAUDE_CODE_ENTRYPOINT",
    "CODEX_SANDBOX",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
)


# a plain name: no `:`, the key's delimiter, so one name never reads as another's (cycle 1 F6)
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def read_agent(environ: dict[str, str]) -> str:
    """Pure: the first agent harness marker set in `environ`, or "" when none is."""
    return next((name for name in AGENT_MARKERS if environ.get(name)), "")


def key_for(what: str, sha: str) -> str:
    """Pure: the approval's key; the full sha lives here, where redaction never reaches."""
    return f"approve:{what}:{sha}"


def run_approve(base: Path, settings: dict, what: str, sha: str, note: str = "") -> int:
    """`kgme approve --what --sha [--note]`: one `approval` event, or a refusal."""
    agent = read_agent(dict(os.environ))
    if agent:
        print(
            f"kgme approve: refused: {agent} is set, so an agent harness runs this; "
            "an approval is Michou's, from his own terminal",
            file=sys.stderr,
        )
        return 2
    if not NAME.match(what):
        print(f"kgme approve: refused: {what!r} is not a plain name (a-z, 0-9, -)", file=sys.stderr)
        return 2
    main = ledger.read_main_checkout(base)
    full = read_sha(main, sha)
    if what == CODE:
        refused = read_code_refusal(main, settings, full)
        if refused:
            print(f"kgme approve: refused: {refused}", file=sys.stderr)
            return 2
    on_trunk = bool(full) and (
        run_git(["merge-base", "--is-ancestor", full, TRUNK], main, check=False).returncode == 0
    )
    if not on_trunk and what != CODE:
        print(f"kgme approve: refused: {sha} is not a commit on {TRUNK}", file=sys.stderr)
        return 2
    words = f"approved {what} at {full[:12]}" + (f": {note}" if note else "")
    event = events.make_event(
        source="human",
        actor="michou",
        kind="approval",
        job=JOB,
        key=key_for(what, full),
        summary=events.clip(events.redact(words)),
    )
    print(ledger.append(event, ledger.read_base_dirs(settings, main)))
    print(f"kgme approve: {words}")
    if what == CODE:
        return write_code_landing(main, settings, full)
    return 0


CODE = "code"


def read_crew_branch(main: Path, full: str) -> str:
    """Effect: the `crew/<handoff>/integration` branch whose head is `full`, or "" (HANDOFF-0048
    amendment 9: an approval of code names an integration branch's head, nothing else)."""
    listed = run_git(
        ["for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/crew/"],
        main,
        check=False,
    ).stdout
    for line in listed.splitlines():
        name, _, sha = line.partition(" ")
        if sha == full and name.endswith("/integration") and name.count("/") == 2:
            return name
    return ""


def read_code_refusal(main: Path, settings: dict, full: str) -> str:
    """Effect: why `full` may not be approved as code, or "": it must be the head of a
    `crew/<handoff>/integration` branch and the crew must have written `awaiting approval`
    naming it, which it does only after the gate was green on it and the integration review
    passed."""
    if not full:
        return "no such commit"
    branch = read_crew_branch(main, full)
    if not branch:
        return f"{full[:12]} is not the head of a crew/<handoff>/integration branch"
    handoff = branch.removeprefix("crew/").removesuffix("/integration")
    waiting = [
        e
        for e in ledger.read(ledger.read_base_dirs(settings, main))
        if e["job"] == f"crew:{handoff}"
        and e["kind"] == "outcome"
        and e["status"] == "ok"
        and "awaiting approval" in (e["summary"] or "")
        and full[:12] in (e["summary"] or "")
    ]
    if not waiting:
        return f"the crew has not written `awaiting approval` for {full[:12]} on {branch}"
    return ""


def write_code_landing(main: Path, settings: dict, full: str) -> int:
    """Effect: `main` fast-forwarded to the approved integration head at a quiet point of
    the main checkout, then pushed through `kgme sync`; a refusal lands nothing."""
    from kgme import merge, sync_io

    checkout = merge.read_checkout(main)
    waiting = merge.is_quiet(checkout, checkout.head)
    if waiting:
        print(
            f"kgme approve: not landed: {waiting}; `git merge --ff-only {full[:12]}` when quiet",
            file=sys.stderr,
        )
        return 1
    done = run_git(["merge", "--ff-only", "--quiet", full], main, check=False)
    if done.returncode != 0 or read_sha(main, "HEAD") != full:
        print(
            f"kgme approve: the fast-forward of {TRUNK} to {full[:12]} did not land: "
            f"{(done.stderr or done.stdout).strip()[:200]}",
            file=sys.stderr,
        )
        return 1
    print(f"kgme approve: {TRUNK} is at {full[:12]}")
    sync_io.run_sync(main, settings)
    return 0


def read_name(key: str | None) -> str:
    """Pure: the name an approval's key holds, or "" when the key is not `approve:<name>:<sha>`."""
    parts = (key or "").split(":")
    return parts[1] if len(parts) == 3 and parts[0] == "approve" else ""


def read_newest(settings: dict, main: Path, what: str) -> dict | None:
    """Effect: the newest `approval` of exactly `what`, by instant, then by event id (cycle 1
    F7: timestamps carry offsets, so their strings do not sort by time), or None."""
    found = [
        e
        for e in ledger.read(ledger.read_base_dirs(settings, main))
        if e["kind"] == "approval" and e["job"] == JOB and read_name(e["key"]) == what
    ]
    return max(found, key=lambda e: (datetime.fromisoformat(e["ts"]), e["id"])) if found else None


def run_show(base: Path, settings: dict, what: str) -> int:
    """`kgme approve --show <name>`: the newest approval's time, commit, and words."""
    newest = read_newest(settings, ledger.read_main_checkout(base), what)
    if newest is None:
        print(f"kgme approve: no approval of {what}", file=sys.stderr)
        return 1
    print(f"{newest['ts']} {newest['key'].split(':', 2)[2]} {newest['summary']}")
    return 0
