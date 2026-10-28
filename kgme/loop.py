"""`kgme loop --queue`: the unattended mode over a queue of adopted handoffs (HANDOFF-0043).

Purpose: run each handoff of the queue, in the order named, to its close with nobody watching,
as the overnight run of 2026-10-26 did by hand (amendments 13-24). The builder is a fresh
`kgme session loose --handoff <id>` per handoff (amendment 14), started as its own process
group from the workspace it builds in; the loop adds no prompt of its own and never drives the
build step by step. It reads the run back from the ledger, never from the builder's report:
- the halt is ADR-023's measured non-convergence (`halt_reason`, over `kgme.review.loop_state`):
  the run is killed, its packet stands in the ledger, nothing is committed, and the queue goes
  on (amendment 16);
- a finding blocking two consecutive cycles with no settled ruling goes to the arbiter pair
  (`kgme.review_run.run_arbiters`, amendment 20), once per finding;
- a run is stalled when its newest ledger event is older than `--stall-minutes` and no call of
  the session is alive (`is_stalled`, `live_children`): the group is killed, SIGTERM then
  SIGKILL after the grace, a `blocking` outcome "stalled run killed" is written and the run's
  scratch moves to `logs/scratch/loop/quarantine/<run>/` (amendment 17);
- a limit message in the builder's output pauses the queue until the reset it names
  (`reset_time`), or retries on the interval when it names none, then starts the same handoff
  again; a pause is a `transient` note, never a cycle or a strike (amendment 19);
- a compaction in the builder's stream is a note naming the step and the context size the
  stream gives, never a cycle; the cycle's findings and dispositions stay on disk for the
  builder to re-read (amendment 5, Michou's ruling of 2026-10-26).
The run's first intent names the level, the builder's model and both harness versions
(amendment 6); its closing outcome names the commit, the audit ids and the usage the stream
reports (amendment 18). `caffeinate -i -w <pid>` keeps the Mac awake exactly as long as the
loop lives (amendment 21).
Logic (pure, over a run's ledger events or text): `next_handoff`, `is_stalled`,
`live_children`, `reset_time`, `halt_reason`, `settle`, `read_stream`, `closing_screen`.
Effects: `run_loop`, `start_caffeinate`, `start_builder`, `read_group`, `kill_group`.
Inputs: the queue; the workspace; the ledger directories and review places; the builder's
argv per handoff; the stall, poll and grace periods; the clock and sleep.
Outputs: exit code 0 when every handoff closed, 1 otherwise; one closing screen.
Side effects: ledger events; the builder's stream under `<scratch>/loop/<run>/`; payloads;
child processes (the builder's group, `caffeinate`) and their kill; the quarantine move.
"""

import json
import os
import re
import shutil
import signal
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from kgme import events, ledger, review, review_io

POLL_SECONDS = 5.0
GRACE_SECONDS = 10.0
RETRY_WITHOUT_TIME = timedelta(minutes=30)
STALL_MINUTES = 15
# amendment 13: the unattended queue takes Michou's adopted handoffs only (review cycle 1 F11)
AUTHORS = ("michou",)
ARBITER_RETRY = timedelta(minutes=5)
CLASS_ORDER = ("blocking", "transient", "advisory", "cosmetic")  # stricter first, on a tie
# the limit messages the harnesses print. Codex, verbatim in local transcripts: "try again at
# 4:22 PM", "try again at Oct 9th, 2026 12:21 AM". Claude Code's are the documented "resets 6pm"
# form and the older "usage limit reached|<epoch>", not seen on this machine (unverified); an
# unparsed one falls to the interval (Michou's ruling of 2026-10-26)
LIMIT = re.compile(
    r"usage limit|hit your (?:usage |session |weekly )?limit|limit reached|rate.?limit", re.I
)
EPOCH = re.compile(r"limit reached\|(?P<epoch>\d{10})")
AT_DATE = re.compile(
    r"try again at (?P<month>[A-Z][a-z]{2})[a-z]* (?P<day>\d{1,2})(?:st|nd|rd|th)?, "
    r"(?P<year>\d{4}),? (?P<h>\d{1,2}):(?P<m>\d{2}) ?(?P<ap>[AP]M)",
    re.I,
)
AT_TIME = re.compile(
    r"(?:try again at|resets(?: at)?) (?P<h>\d{1,2})(?::(?P<m>\d{2}))? ?(?P<ap>[ap]m)", re.I
)
IN_SPAN = re.compile(r"try again in (?:(?P<h>\d+) hours?)?,? ?(?:(?P<m>\d+) min)?", re.I)
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")


@dataclass
class Run:
    """One handoff's run, as the closing screen shows it."""

    handoff: str
    run: str
    status: str = "open"  # closed | halted | stalled | ended | refused
    reason: str = ""
    commit: str | None = None
    audits: list[str] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    pauses: list[str] = field(default_factory=list)
    compactions: int = 0
    arbitrated: list[str] = field(default_factory=list)
    sessions: list[str] = field(default_factory=list)
    tried: dict = field(default_factory=dict)  # finding -> when the pair was last tried
    arbiter_retry: timedelta = ARBITER_RETRY


# ---------------------------------------------------------------- logic, pure


def next_handoff(queue: list[str], finished: set[str]) -> str | None:
    """Pure: the first handoff of the queue, in the order named, not yet run."""
    return next((h for h in queue if h not in finished), None)


def live_children(rows: list[tuple[int, int, int]], leader: int) -> int:
    """Pure: the processes of `leader`'s group below the session itself. The leader is the
    launcher (`uv run`), its direct child the session (`claude`), and a call the session runs
    sits below that; rows are (pid, ppid, pgid)."""
    return sum(1 for pid, ppid, pgid in rows if pgid == leader and pid != leader and ppid != leader)


def is_stalled(newest: datetime, now: datetime, stall: timedelta, children: int) -> bool:
    """Pure: ledger silence longer than `stall` with no live call (amendment 17); a long
    single call is not a stall while its process lives."""
    return children == 0 and now - newest > stall


def reset_time(text: str, now: datetime) -> datetime | None:
    """Pure: when a limit named in `text` lifts, in `now`'s zone; None when `text` names no
    limit or no time. A clock time already past today is tomorrow's."""
    if not LIMIT.search(text):
        return None
    if match := EPOCH.search(text):
        return datetime.fromtimestamp(int(match["epoch"]), now.tzinfo)
    if match := AT_DATE.search(text):
        month = MONTHS.index(match["month"][:3].lower()) + 1
        hour = int(match["h"]) % 12 + (12 if match["ap"].upper() == "PM" else 0)
        return now.replace(
            year=int(match["year"]), month=month, day=int(match["day"]), hour=hour,
            minute=int(match["m"]), second=0, microsecond=0,
        )  # fmt: skip
    if match := AT_TIME.search(text):
        hour = int(match["h"]) % 12 + (12 if match["ap"].lower() == "pm" else 0)
        at = now.replace(hour=hour, minute=int(match["m"] or 0), second=0, microsecond=0)
        return at if at > now else at + timedelta(days=1)
    if (match := IN_SPAN.search(text)) and (match["h"] or match["m"]):
        return now + timedelta(hours=int(match["h"] or 0), minutes=int(match["m"] or 0))
    return None


def halt_reason(handoff_events: list[dict]) -> str | None:
    """Pure: why this handoff's run must stop, from its review events, else None: a `halt:`
    note already written (by `kgme review` or its gate), or a measure that fired."""
    state = review.loop_state(handoff_events)
    if state.active_halt:
        notes = [e for e in handoff_events if (e["key"] or "").startswith("halt:")]
        return notes[-1]["summary"] if notes else state.reason
    return state.reason if state.halt else None


def settle(rulings: list[dict]) -> dict | None:
    """Pure: one settlement of the arbiters' rulings on a finding. The same class and the
    same recommendation settle it as agreed. Anything else is a split, whether on the class
    or on the option under one class (review cycle 3 F15): it takes the reversible option
    with the smallest blast radius, the stricter class on a tie (ADR-023), and is listed for
    the approval screen; with no reversible option it settles nothing and goes to Michou.
    None when no arbiter ruled."""
    if not rulings:
        return None
    # agreement is the same class and the same recommendation (review cycle 3 F15)
    options = {" ".join(r["option"].lower().split()) for r in rulings}
    if len({r["class"] for r in rulings}) == 1 and len(options) == 1:
        reason = " | ".join(f"{r['arbiter']}: {r['option']}" for r in rulings)
        return {"class": rulings[0]["class"], "reason": f"agreed; {reason}", "split": False,
                "escalate": False}  # fmt: skip
    split = ", ".join(
        f"{r['arbiter']}={r['class']}: {r['option']} (blast {r['blast_radius']}, "
        f"{'reversible' if r['reversible'] else 'one-way'})"
        for r in rulings
    )
    if not any(r["reversible"] for r in rulings):  # review cycle 1 F6
        return {"class": None, "reason": f"split among one-way doors ({split}); Michou's",
                "split": True, "split_text": split, "escalate": True}  # fmt: skip
    chosen = min(
        rulings,
        key=lambda r: (not r["reversible"], r["blast_radius"], CLASS_ORDER.index(r["class"])),
    )
    return {
        "class": chosen["class"],
        "reason": f"split ({split}); took {chosen['arbiter']}: {chosen['option']}",
        "split": True,
        "split_text": split,
        "escalate": False,
    }


def close_status(after: list[dict], commit: str | None, done: bool) -> str:
    """Pure: how a run ended, from its review events after the loop's intent (review cycles 1
    and 2, F3). The newest review cycle must be a PASS whose newest gate before it was green,
    with no red gate or failed review after it; then "closed" when a commit names the handoff
    and the handoff has moved to `done/`, else "ready" (diffs pending). Anything else is
    "ended"."""
    passed, gate = False, None
    for event in after:
        key = event.get("key") or ""
        if key.startswith("loop:"):
            continue
        if key.startswith("gate:"):
            gate = "red" if " red " in f" {event['summary']} " else "green"
            passed = passed and gate == "green"
        elif event["kind"] == "outcome" and event.get("status") == "ok":
            passed = " PASS " in f" {event['summary']} " and gate == "green"
        elif event["kind"] == "outcome":
            passed = False
    if not passed:
        return "ended"
    return "closed" if commit and done else "ready"


def add_usage(total: dict, usage: dict, cost: float | None) -> dict:
    """Pure: one attempt's usage added to the run's (review cycle 1 F10): numbers summed by
    key, the cost summed."""
    summed = dict(total)
    for key, value in usage.items():
        if isinstance(value, int | float) and not isinstance(value, bool):
            summed[key] = summed.get(key, 0) + value
    if cost is not None:
        summed["cost_usd"] = round(summed.get("cost_usd", 0) + cost, 6)
    return summed


def execution_request(handoff: str, path: str, findings: str = "") -> str:
    """Pure: the one line a fresh session is given (review cycle 1 F1), as Michou gives it:
    the handoff and its path; the rest is the committed CLAUDE.md `loose` carries."""
    return (
        f"{handoff} is open and adopted by Michou: {path}. Execute it under CLAUDE.md, to its "
        "close or its report, with nobody watching.\n"
    )


def read_stream(text: str) -> dict:
    """Pure: what the builder's output says: the session id, the usage and cost, the
    compactions with the context size the stream gives, and any limit text. Lines that are
    not JSON are kept as plain text, where a limit message may sit."""
    found: dict = {"session_id": None, "usage": {}, "cost_usd": None, "compactions": [],
                   "plain": [], "last_input_tokens": None}  # fmt: skip
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            if line.strip():
                found["plain"].append(line)
            continue
        if not isinstance(record, dict):
            continue
        kind, sub = record.get("type"), record.get("subtype")
        if kind == "system" and sub == "init":
            found["session_id"] = record.get("session_id")
        elif kind == "system" and sub == "compact_boundary":
            meta = record.get("compact_metadata") or {}
            size = meta.get("pre_tokens", found["last_input_tokens"])
            found["compactions"].append({"trigger": meta.get("trigger"), "context_tokens": size})
        elif kind == "assistant":
            usage = (record.get("message") or {}).get("usage") or {}
            if usage:
                found["last_input_tokens"] = sum(
                    int(usage.get(k) or 0)
                    for k in (
                        "input_tokens",
                        "cache_read_input_tokens",
                        "cache_creation_input_tokens",
                    )
                )
        elif kind == "result":
            found["usage"] = record.get("usage") or {}
            found["cost_usd"] = record.get("total_cost_usd")
            if record.get("is_error") and record.get("result"):
                found["plain"].append(str(record["result"]))
        elif kind in ("error", "turn.failed"):  # Codex's stream (HANDOFF-0048 §2, cycle 1 F6)
            message = record.get("message") or (record.get("error") or {}).get("message") or ""
            if message:
                found["plain"].append(str(message))
    return found


def closing_screen(runs: list[Run]) -> str:
    """Pure: the one screen the loop prints at its end."""
    lines = [f"kgme loop: {len(runs)} handoff(s)"]
    for run in runs:
        usage = run.usage or {}
        tokens = (
            f"in={usage.get('input_tokens', '?')} out={usage.get('output_tokens', '?')} "
            f"cost=${usage.get('cost_usd', '?')}"
        )
        lines.append(
            f"  {run.handoff}: {run.status}{': ' + run.reason if run.reason else ''}; "
            f"commit {run.commit or 'none'}; audits {', '.join(run.audits) or 'none'}; "
            f"usage {tokens}; pauses {len(run.pauses)}; compactions {run.compactions}; "
            f"arbitrated {', '.join(run.arbitrated) or 'none'}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------- effects


def start_caffeinate() -> subprocess.Popen | None:
    """Effect: `caffeinate -i -w <this pid>`, released on exit and on a crash alike."""
    try:
        return subprocess.Popen(
            ["caffeinate", "-i", "-w", str(os.getpid())],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return None


def start_builder(
    argv: list[str], workspace: Path, out: Path, env: dict, request: str = ""
) -> subprocess.Popen:
    """Effect: the builder as its own process group, `request` on its stdin, its output to
    `out`."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "ab") as handle:
        proc = subprocess.Popen(
            argv, cwd=workspace, stdin=subprocess.PIPE, stdout=handle,
            stderr=subprocess.STDOUT, env=env, start_new_session=True,
        )  # fmt: skip
    try:
        proc.stdin.write(request.encode("utf-8"))
        proc.stdin.close()
    except BrokenPipeError:
        pass
    return proc


def read_group() -> list[tuple[int, int, int]]:
    """Effect: every process as (pid, ppid, pgid), from `ps`."""
    done = subprocess.run(
        ["ps", "-A", "-o", "pid=,ppid=,pgid="], capture_output=True, text=True, check=False
    )
    rows = []
    for line in done.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            rows.append((int(parts[0]), int(parts[1]), int(parts[2])))
    return rows


def signal_group(pgid: int, sig: int) -> None:
    """Effect: `sig` to every process of the group; macOS refuses `killpg` with EPERM when a
    member is a zombie, so the members are then signalled one by one."""
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return
    except PermissionError:
        for pid, _, group in read_group():
            if group == pgid:
                try:
                    os.kill(pid, sig)
                except (ProcessLookupError, PermissionError):
                    pass


def kill_group(proc: subprocess.Popen, grace: float) -> None:
    """Effect: SIGTERM to the whole group, SIGKILL after `grace` seconds if any is left."""
    signal_group(proc.pid, signal.SIGTERM)
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        proc.poll()
        if not any(pgid == proc.pid for _, _, pgid in read_group()):
            return
        time.sleep(0.1)
    signal_group(proc.pid, signal.SIGKILL)
    proc.wait()


def read_handoff_ready(handoff_dir: Path, handoff: str) -> str | None:
    """Effect: why `handoff` cannot run, else None: it must be adopted, at the top of the
    handoff folder, `status: open`, from `cowork` or `michou` (CLAUDE.md)."""
    path = review_io.read_handoff_path(handoff_dir, handoff)
    if path is None or path.parent != handoff_dir:
        return f"{handoff} is not an open handoff at the top of {handoff_dir.name}/"
    text = review_io.read_text(path)
    if not re.search(r"^status:\s*open\s*$", text, re.M):
        return f"{handoff} is not status: open"
    if not re.search(rf"^from:\s*({'|'.join(AUTHORS)})\s*$", text, re.M):
        return f"{handoff} is not from {' or '.join(AUTHORS)}"
    return None


def read_versions() -> dict[str, str]:
    """Effect: `claude --version` and `codex --version`, for the run's first intent."""
    found = {}
    for tool in ("claude", "codex"):
        try:
            done = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=30, check=False
            )
            found[tool] = (done.stdout.strip() or done.stderr.strip()).splitlines()[0][:60]
        except (OSError, subprocess.TimeoutExpired, IndexError):
            found[tool] = "not found"
    return found


def read_commit(
    workspace: Path, start: str | None, handoff: str, not_before: datetime | None = None
) -> str | None:
    """Effect: the newest commit since `start` in the workspace whose message names the
    handoff and, with `not_before` (the final PASS), committed no earlier than it (review
    cycle 2 F3, the arbiters' conditions)."""
    if not start:
        return None
    done = subprocess.run(
        ["git", "log", "--format=%h %ct", f"--grep={handoff}", f"{start}..HEAD"],
        cwd=workspace, capture_output=True, text=True, check=False,
    )  # fmt: skip
    floor = int(not_before.timestamp()) if not_before else 0
    for line in done.stdout.splitlines():
        short, _, when = line.partition(" ")
        if when.isdigit() and int(when) >= floor:
            return short
    return None


def read_head(workspace: Path) -> str | None:
    """Effect: the workspace's HEAD, None outside git."""
    done = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=workspace, capture_output=True, text=True, check=False
    )
    return done.stdout.strip() or None


def builder_argv(handoff: str, workspace: Path) -> list[str]:
    """Pure: the fresh loose session for one handoff, its stream as JSON lines."""
    return [
        "uv", "run", "--frozen", "--project", str(workspace), "kgme", "session", "loose",
        "--handoff", handoff, "--", "--output-format", "stream-json", "--verbose",
    ]  # fmt: skip


def _ts(event: dict) -> datetime:
    return datetime.fromisoformat(event["ts"])


def run_loop(
    queue: list[str],
    workspace: Path,
    places: review_io.Places,
    arbiters: list[str],
    arbiter_template: str | None,
    argv_for: Callable[[str, Path], list[str]] = builder_argv,
    stall: timedelta = timedelta(minutes=STALL_MINUTES),
    poll: float = POLL_SECONDS,
    grace: float = GRACE_SECONDS,
    retry: timedelta = RETRY_WITHOUT_TIME,
    now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
    sleep: Callable[[float], None] = time.sleep,
    model: str = "",
    env: dict | None = None,
    run_arbiters: Callable | None = None,
    arbiter_retry: timedelta = ARBITER_RETRY,
    request_for: Callable[..., str] = execution_request,
    parent: str | None = None,
    adapter=None,
    on_process: Callable | None = None,
    after_exit: Callable | None = None,
) -> int:
    """The command: each handoff of the queue to its close, then the closing screen. A queue
    entry `HANDOFF-NNNN:<task>` is one crew task (HANDOFF-0048): its events are keyed by that
    unit, its builder's argv and request come from the task's adapter through `argv_for` and
    `request_for(unit, path, findings)`, and it closes on a PASS and a commit on its branch,
    with no move to `done/` (the crew closes the handoff at approval). `parent` is the crew's
    intent, the parent of the loop's own (cycle 1 F8); `adapter.events` turns a stream into
    ledger events for a harness without hooks and `adapter.close_open` answers what a killed
    builder left open (F7); `on_process(proc or None)` tells the crew the builder's process
    group, for the workspace record (F10); `after_exit(run)` is the supervisor's turn once
    a builder without the reviewer's reach has exited (Codex: stage, gate, review, commit) and
    returns ("again", findings), ("done", "") or ("halted", reason) (F6)."""
    from kgme import review_run

    run_arbiters = run_arbiters or review_run.run_arbiters
    caffeinate = start_caffeinate()
    runs: list[Run] = []
    try:
        finished: set[str] = set()
        while (handoff := next_handoff(queue, finished)) is not None:
            finished.add(handoff)
            run = Run(handoff, events.new_ulid(), arbiter_retry=arbiter_retry)
            runs.append(run)
            _run_one(
                run, workspace, places, arbiters, arbiter_template, argv_for, stall, poll,
                grace, retry, now, sleep, model, env, run_arbiters, request_for, parent,
                adapter, on_process, after_exit,
            )  # fmt: skip
    finally:
        if caffeinate is not None:
            caffeinate.terminate()
            caffeinate.wait()
    print(closing_screen(runs))
    return 0 if all(r.status in ("closed", "ready") for r in runs) else 1


def _loop_event(kind: str, run: Run, parent: str | None, summary: str, **more) -> dict:
    return events.make_event(
        source="kgme", actor="kgme.loop", kind=kind, job=f"review:{run.handoff}",
        key=f"loop:{run.handoff}:{run.run}", parent=parent, run_id=run.run,
        summary=events.clip(summary), **more,
    )  # fmt: skip


def _run_one(
    run: Run,
    workspace,
    places,
    arbiters,
    template,
    argv_for,
    stall,
    poll,
    grace,
    retry,
    now,
    sleep,
    model,
    env,
    run_arbiters,
    request_for=execution_request,
    crew_parent: str | None = None,
    adapter=None,
    on_process=None,
    after_exit=None,
) -> None:
    """One handoff: refuse, or start the builder and supervise it until it closes."""
    dirs = places.dirs
    refused = read_handoff_ready(places.handoff_dir, run.handoff)
    history = review_io.read_handoff_events(run.handoff, dirs)
    if refused is None and review.loop_state(history).active_halt:
        refused = f"{run.handoff} is halted; an override comes first"
    if refused:
        run.status, run.reason = "refused", refused
        ledger.append(
            _loop_event("outcome", run, crew_parent or review_io.first_intent_id(history),
                        f"loop {refused}", status="error", class_="blocking"),
            dirs,
        )  # fmt: skip
        return
    argv = argv_for(run.handoff, workspace)
    handoff_path = review_io.read_handoff_path(places.handoff_dir, run.handoff)
    shown_path = review_io.shown(handoff_path, places.root)
    request = request_for(run.handoff, shown_path)
    versions = read_versions()
    record = {"level": "loose", "handoff": run.handoff, "model": model, "argv": argv,
              "workspace": str(workspace), "versions": versions}  # fmt: skip
    ref, digest = review_io.write_payload(
        places.payloads, f"loop-{run.run}.json", json.dumps(record, indent=2) + "\n", places.root
    )
    intent_id = ledger.append(
        _loop_event(
            "intent",
            run,
            crew_parent or review_io.first_intent_id(history),
            f"loop {run.handoff} level=loose model={model or '?'} claude={versions['claude']} "
            f"codex={versions['codex']}",
            payload_ref=ref,
            payload_sha256=digest,
        ),  # fmt: skip
        dirs,
    )
    parent = review_io.first_intent_id(review_io.read_handoff_events(run.handoff, dirs))
    start_head = read_head(workspace)
    folder = places.scratch / "loop" / run.run
    child_env = {**(env if env is not None else os.environ), "KGME_LOOP_PARENT": parent or ""}
    starts = 0
    while True:  # one pass per builder start; a limit, or a supervisor's fix cycle, starts again
        out = folder / f"builder-{starts}.jsonl"
        starts += 1
        proc = start_builder(argv, workspace, out, child_env, request)
        if on_process is not None:
            on_process(proc)
        ended = _supervise(run, proc, out, places, parent, intent_id, arbiters, template,
                           stall, poll, grace, now, sleep, run_arbiters, adapter)  # fmt: skip
        if on_process is not None:
            on_process(None)
        stream = read_stream(review_io.read_text(out) if out.exists() else "")
        if out.exists():
            run.usage = add_usage(run.usage, stream["usage"], stream["cost_usd"])
        if ended != "exited":
            break
        limit_text = "\n".join(stream["plain"])
        after = [e for e in review_io.read_handoff_events(run.handoff, dirs) if e["id"] > intent_id]
        if LIMIT.search(limit_text) and close_status(after, "-", True) == "ended":
            lifted = reset_time(limit_text, now()) or now() + retry
            run.pauses.append(lifted.isoformat(timespec="seconds"))
            ledger.append(
                _loop_event("note", run, parent,
                            f"loop {run.handoff} paused until {run.pauses[-1]}: the "
                            "harness's limit; not a cycle, not a strike",
                            class_="transient"),
                dirs,
            )  # fmt: skip
            sleep(max(0.0, (lifted - now()).total_seconds()))
            continue
        if after_exit is None:
            break
        verdict, findings = after_exit(run)  # the supervisor's turn (HANDOFF-0048, F6)
        if verdict == "again":
            # a finding that stood two cycles is settled before the next builder starts, and
            # the settled rulings go with the findings (review cycle 2 F6)
            _arbitrate(run, places, arbiters, template, now, run_arbiters)
            request = request_for(
                run.handoff, shown_path, findings + rulings_text(run.handoff, places)
            )
            continue
        if verdict == "halted":
            run.status, run.reason = "halted", findings
        break
    after = [e for e in review_io.read_handoff_events(run.handoff, dirs) if e["id"] > intent_id]
    run.audits = [m["audit"] for e in after if (m := review.AUDIT_TOKEN.search(e["summary"] or ""))]
    passes = [
        e for e in after
        if e["kind"] == "outcome" and e["status"] == "ok" and " PASS " in f" {e['summary']} "
        and not (e["key"] or "").startswith("loop:")
    ]  # fmt: skip
    handoff_id, _, task = run.handoff.partition(":")
    run.commit = read_commit(workspace, start_head, handoff_id, _ts(passes[-1]) if passes else None)
    if run.status == "open":
        finished = review_io.read_handoff_path(places.handoff_dir, run.handoff)
        done = finished is not None and finished.parent == places.handoff_dir / "done"
        done = done or bool(task)  # a task closes on its branch; the crew closes the handoff
        run.status = close_status(after, run.commit, done)
        if run.status == "ready":
            run.reason = "PASS on a green gate, nothing committed: ready, diffs pending"
        elif run.status == "ended":
            run.reason = "the session ended without a final PASS on a green gate"
    status, cls = ("ok", None) if run.status in ("closed", "ready") else ("error", "blocking")
    if run.status == "stalled":
        status = "error"
    usage_ref, usage_digest = review_io.write_payload(
        places.payloads, f"loop-{run.run}-close.json",
        json.dumps({"usage": run.usage, "pauses": run.pauses, "audits": run.audits,
                    "commit": run.commit, "status": run.status}, indent=2) + "\n",
        places.root,
    )  # fmt: skip
    summary = (
        f"loop {run.handoff} {run.status}: commit {run.commit or 'none'}; audits "
        f"{','.join(run.audits) or 'none'}; {run.reason or 'closed'}"
    )
    if run.status == "stalled":
        summary = f"loop {run.handoff}: stalled run killed; {run.reason}"
    ledger.append(
        _loop_event("outcome", run, parent, summary, status=status, class_=cls, ref=intent_id,
                    payload_ref=usage_ref, payload_sha256=usage_digest),
        dirs,
    )  # fmt: skip


def _arbitrate(run, places, arbiters, template, now, run_arbiters, history=None) -> None:
    """Effect: every finding blocking two consecutive cycles with no settled ruling goes to
    the pair, once, retried after the interval when the pair did not settle it (F5)."""
    if history is None:
        history = review_io.read_handoff_events(run.handoff, places.dirs)
    state_now = review.loop_state(history)
    for finding in state_now.to_arbiters:
        if finding in run.arbitrated or not arbiters or template is None:
            continue
        last = run.tried.get(finding)
        if last is not None and now() - last < run.arbiter_retry:
            continue  # pending: the pair is tried again after the interval (F5)
        run.tried[finding] = now()
        if run_arbiters(run.handoff, finding, "", places, arbiters, template) is not None:
            run.arbitrated.append(finding)


def rulings_text(unit_name: str, places) -> str:
    """Effect: the settled rulings of a unit as a builder is given them: one line each, from
    the `ruling:<id>=<class>` notes (class, option, reason); empty when there is none."""
    lines = [
        review_io.read_ruling_text(e, places.root)  # whole, not the clipped summary (F6)
        for e in review_io.read_handoff_events(unit_name, places.dirs)
        if e["kind"] == "note"
        and (e["key"] or "").startswith("ruling:")
        and "@" not in (e["key"] or "")
    ]
    if not lines:
        return ""
    return "\n\nThe arbiter pair's settled rulings, to execute:\n" + "\n".join(
        f"- {ln}" for ln in lines
    )


def _counts(event: dict) -> bool:
    """Pure: an event a halt measure reads: a review cycle, a gate, or a halt note."""
    key = event["key"] or ""
    if key.startswith("loop:"):
        return False
    return key.startswith(("gate:", "halt:")) or (
        event["kind"] == "outcome" and event["status"] == "ok"
    )


def _supervise(
    run,
    proc,
    out,
    places,
    parent,
    intent_id,
    arbiters,
    template,
    stall,
    poll,
    grace,
    now,
    sleep,
    run_arbiters,
    adapter=None,
) -> str:
    """Effect: watch one builder until it exits ("exited"), halts ("halted") or stalls
    ("stalled"); arbitrate and log compactions on the way; with an `adapter`, write the
    stream's events to the ledger as they appear and close what a killed builder left open."""
    dirs = places.dirs
    logged = 0
    state: dict | None = None
    child_run = f"{adapter.name}-{run.run}" if adapter is not None else run.run
    suspect = False  # a stall must hold on two consecutive polls: a call that just ended and
    # the post hook's outcome are a moment apart

    def write_stream_events(text: str) -> None:
        nonlocal state
        if adapter is None:
            return
        new, state = adapter.events(text, child_run, parent, state)
        for event in new:
            ledger.append(event, dirs)

    while True:
        exited = proc.poll() is not None
        text = review_io.read_text(out) if out.exists() else ""
        stream = read_stream(text)
        write_stream_events(text)
        for compaction in stream["compactions"][logged:]:
            run.compactions += 1
            ledger.append(
                _loop_event(
                    "note",
                    run,
                    parent,
                    f"loop {run.handoff} builder compacted ({compaction['trigger'] or '?'}) at "
                    f"{compaction['context_tokens'] or '?'} context tokens; not a cycle; the "
                    "findings and dispositions are on disk under scratch",
                    class_="transient",
                ),  # fmt: skip
                dirs,
            )
        logged = len(stream["compactions"])
        sid = stream["session_id"]
        if sid and sid not in run.sessions:  # the session's own tree, reached by its run id (F4)
            run.sessions.append(sid)
            ledger.append(
                _loop_event("note", run, parent,
                            f"loop {run.handoff} builder session {sid}: its hook events carry "
                            "this run id"),
                dirs,
            )  # fmt: skip
        history = review_io.read_handoff_events(run.handoff, dirs)
        reason = halt_reason(history)
        if reason and any(e["id"] > intent_id and _counts(e) for e in history):
            run.status, run.reason = "halted", reason
            if not exited:
                kill_group(proc, grace)
                if adapter is not None:
                    for event in adapter.close_open(state, child_run, parent):
                        ledger.append(event, dirs)
            state = review.loop_state(history)
            if not state.active_halt:  # a measure fired with no halt note yet: write it
                from kgme import review_run

                review_run.write_halt(run.handoff, state, [], "pair", places, label="loop")
            return "halted"
        _arbitrate(run, places, arbiters, template, now, run_arbiters, history)
        if exited:
            if adapter is not None:
                for event in adapter.close_open(state, child_run, parent):
                    ledger.append(event, dirs)
            return "exited"
        window = [e for e in history if e["id"] >= intent_id]
        if stream["session_id"]:
            window += ledger.read(dirs, run_id=stream["session_id"])
        if adapter is not None:
            window += ledger.read(dirs, run_id=child_run)
        newest = max((_ts(e) for e in window), default=now())
        children = live_children(read_group(), proc.pid)
        stalled = is_stalled(newest, now(), stall, children)
        if stalled and suspect:
            kill_group(proc, grace)
            if adapter is not None:
                for event in adapter.close_open(state, child_run, parent):
                    ledger.append(event, dirs)
            stream = read_stream(review_io.read_text(out) if out.exists() else "")
            run.usage = add_usage(run.usage, stream["usage"], stream["cost_usd"])
            quarantine = places.scratch / "loop" / "quarantine" / run.run
            quarantine.parent.mkdir(parents=True, exist_ok=True)
            source = places.scratch / "loop" / run.run
            if source.exists():
                shutil.move(str(source), str(quarantine))
            run.status = "stalled"
            run.reason = (
                f"no ledger event for {int(stall.total_seconds())} s and no live call; "
                f"scratch in {review_io.shown(quarantine, places.root)}"
            )
            return "stalled"
        suspect = stalled
        sleep(poll)
