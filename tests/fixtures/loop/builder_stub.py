"""The toy builder of HANDOFF-0043's acceptance test: a fresh session, scripted.

Purpose: stand in for `kgme session loose --handoff <toy>` under `kgme loop`, doing what a
builder does and writing what its hooks would: a stream-json `init` line with a session id,
tool events under that id, `gate:` notes from the toy's own suite, review cycles through the
real `kgme.review_run.run_cycle` against the fake `codex`, a commit on PASS and a `result`
line with usage. The scenario is the first argument:
- `close`: red gate, green gate with the seed, review BLOCK, the seed removed, review PASS,
  commit, the handoff moved to `done/`;
- `unfixable`: the seed stays (the dispute), two BLOCK cycles; it waits for the arbiters'
  settled ruling, executes it, and blocks again; then keeps working until killed;
- `silent`: the init line, then silence in its own process, no child;
- `busy`: the init line, then one long call in a child process, then exit;
- `limited`: on its first start, the harness's limit message (the second argument) and exit;
  on the next start, `close`.
Inputs: argv (scenario, limit text); the environment: `TOY_DIR` (the workspace, a git repo),
`TOY_PLACES` (a JSON file with the review places), `TOY_HANDOFF`, `KGME_LOOP_PARENT`.
Outputs: stream-json lines on stdout; exit 0.
Side effects: files and commits in the workspace; events in the test streams; audits and
payloads under the test places.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from kgme import events, ledger, review_io, review_run

TOY = Path(os.environ["TOY_DIR"])
HANDOFF = os.environ["TOY_HANDOFF"]
SESSION = f"toy-session-{events.new_ulid()}"
MODULE = TOY / f"toy_{HANDOFF.lower().replace('-', '_')}.py"


def read_places() -> review_io.Places:
    raw = json.loads(Path(os.environ["TOY_PLACES"]).read_text())
    dirs = ledger.Dirs(Path(raw["ledger"]), Path(raw["trace"]), tuple(raw["read_only_tools"]))
    return review_io.Places(
        dirs, Path(raw["audit_dir"]), Path(raw["scratch"]), Path(raw["payloads"]),
        Path(raw["handoff_dir"]), Path(raw["prompt_path"]), Path(raw["root"]),
    )  # fmt: skip


PLACES = read_places()


def say(record: dict) -> None:
    print(json.dumps(record), flush=True)


def tool(summary: str) -> None:
    """The pair of events a hook writes for one call, under this session's id."""
    common = {"source": "claude-code", "actor": "claude-code.hook", "run_id": SESSION,
              "job": "tool:Bash", "parent": os.environ.get("KGME_LOOP_PARENT") or None}  # fmt: skip
    key = events.new_ulid()
    intent = ledger.append(
        events.make_event(kind="intent", key=key, summary=summary, **common), PLACES.dirs
    )
    ledger.append(
        events.make_event(kind="outcome", status="ok", key=key, ref=intent, summary=summary,
                          **common),
        PLACES.dirs,
    )  # fmt: skip


def write(body: str) -> None:
    tool(f"Edit {MODULE.name}")
    MODULE.write_text(body)


def gate() -> int:
    """The toy's own suite as the gate, recorded as `kgme review`'s gate is."""
    tool("Bash pytest")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(TOY),
         "-c", os.devnull, str(TOY / "test_toy.py")],
        cwd=TOY, capture_output=True, text=True, env={**os.environ, "TOY_MODULE": MODULE.stem},
    )  # fmt: skip
    review_run.write_gate(HANDOFF, done.returncode, done.stdout + done.stderr, PLACES, "pair")
    return done.returncode


def review(dispositions: str) -> int:
    tool("Bash kgme review")
    # its own module only: the toys of one queue share a workspace, and a halted run's work
    # stays there uncommitted (a real queue gives each handoff its own, HANDOFF-0048)
    subprocess.run(["git", "add", MODULE.name], cwd=TOY, check=True)
    patch = subprocess.run(
        ["git", "diff", "--cached", "--", MODULE.name],
        cwd=TOY,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return review_run.run_cycle(HANDOFF, "fake", dispositions, patch, PLACES, False, backoff=())


def commit_and_close() -> None:
    tool("Bash git commit")
    subprocess.run(
        ["git", "commit", "-q", "-m", f"toy: add ({HANDOFF})", "--", MODULE.name],
        cwd=TOY,
        check=True,
    )
    for path in PLACES.handoff_dir.glob("*.md"):
        text = path.read_text()
        if f"id: {HANDOFF}\n" in text:
            (PLACES.handoff_dir / "done").mkdir(exist_ok=True)
            path.rename(PLACES.handoff_dir / "done" / path.name)
            target = PLACES.handoff_dir / "done" / path.name
            target.write_text(text.replace("status: open", "status: done"))


def close() -> None:
    write("def add(a, b):\n    return a - b\n")
    assert gate() != 0
    write("def add(a, b):\n    return a + b  # SEED\n")
    assert gate() == 0
    assert review("") == 1
    write("def add(a, b):\n    return a + b\n")
    assert gate() == 0
    assert review("F1 fixed: the seed is removed.") == 0
    commit_and_close()


def unfixable() -> None:
    write("def add(a, b):\n    return a + b  # SEED\n")
    assert gate() == 0
    assert review("") == 1
    write("def add(a, b):\n    return a + b  # SEED: required\n")
    assert gate() == 0
    assert review("F1 disputed: the seed is required by the toy's brief.") == 1
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:  # the loop sends F1 to the arbiters
        history = review_io.read_handoff_events(HANDOFF, PLACES.dirs)
        if any((e["key"] or "").startswith("ruling:F1=") for e in history):
            break
        tool("Bash waiting for the ruling")
        time.sleep(0.2)
    write("def add(a, b):\n    return a + b  # SEED: the ruling executed, the seed kept\n")
    assert gate() == 0
    review("F1: ruling executed; the seed cannot go.")
    while True:  # keeps working until the loop stops it
        tool("Bash still working")
        time.sleep(0.2)


def main() -> int:
    scenario = sys.argv[1]
    say({"type": "system", "subtype": "init", "session_id": SESSION})
    tool("Bash start")
    if scenario == "limited":
        marker = TOY / f".{HANDOFF}-limited"
        if not marker.exists():
            marker.write_text("1")
            say({"type": "result", "is_error": False, "usage": {"input_tokens": 100,
                 "output_tokens": 10}, "total_cost_usd": 0.05})  # fmt: skip
            print(sys.argv[2], flush=True)
            return 1
        scenario = "close"
    if scenario == "close":
        close()
    elif scenario == "unfixable":
        unfixable()
    elif scenario == "silent":
        time.sleep(120)
    elif scenario == "busy":
        subprocess.run(["sleep", "8"], check=True)
        tool("Bash sleep 8")  # the post hook's outcome, the instant the call ends
    say({"type": "system", "subtype": "compact_boundary",
         "compact_metadata": {"trigger": "auto", "pre_tokens": 150000}})  # fmt: skip
    say({"type": "result", "is_error": False, "usage": {"input_tokens": 1200,
         "output_tokens": 340}, "total_cost_usd": 0.42})  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
