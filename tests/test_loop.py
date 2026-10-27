"""Tests for `kgme loop` (HANDOFF-0043, the amended acceptance test of 2026-10-26).

Purpose: the supervisor end to end on the toy handoff, with the builder, the reviewer and the
arbiter pair as stubs (`tests/fixtures/loop/`): the toy closes without a keystroke along build,
red gate, build, green gate, review BLOCK, build, review PASS, commit, every event classed and
one tree under the first intent, and the closing screen names the commit, the audits and the
usage; the unfixable toy goes to two agreeing arbiters after two cycles, the ruling is executed,
the root cause returns and the run halts with no commit while a second toy in the queue closes;
splitting arbiters are settled by blast radius and the split is listed; a silent builder past
the stall is killed with its group and quarantined, a busy one is not; a limit with a time
pauses until it, one without retries on the interval, neither a strike; `caffeinate` holds the
loop's pid and is gone at its end. Then the pure logic, case by case.
Inputs: the fixtures; a temporary git workspace and handoff folder per test.
Outputs: pytest assertions.
Side effects: files under `tmp_path`; events in the test streams; payloads under
`logs/scratch/payloads/test/`; child processes, all reaped.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from kgme import config, events, ledger, loop, paths, review, review_io, review_run

ROOT = paths.root()
FIXTURES = Path(__file__).parent / "fixtures" / "loop"
MODELS = ["claude-opus-5-5", "claude-fable-5-1"]
TEMPLATE = (
    "Arbitrate $HANDOFF.\nFinding: $FINDING\nBuilder: $BUILDER_ARGUMENT\nDiff:\n$DIFF\n"
    'Reply with one JSON object: {"class", "option", "reversible", "blast_radius", "reason"}.\n'
)
LIMIT_AT = (
    "You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro) or try "
    "again at 4:22 PM."
)


def bin_with(tmp_path: Path) -> str:
    """A PATH whose `codex` and `claude` are the fixtures."""
    folder = tmp_path / "bin"
    folder.mkdir(exist_ok=True)
    for name, script in (("codex", "fake_codex.py"), ("claude", "fake_claude.py")):
        tool = folder / name
        tool.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{FIXTURES / script}" "$@"\n')
        tool.chmod(0o755)
    return f"{folder}:{os.environ['PATH']}"


def toy(tmp_path: Path, handoffs: list[str]) -> tuple[Path, review_io.Places, Path]:
    """The workspace (a git repo holding the toy suite), the places, and the places file."""
    settings = config.read_config()
    workspace, handoff_dir = tmp_path / "workspace", tmp_path / "handoff"
    workspace.mkdir()
    handoff_dir.mkdir()
    shutil.copy(FIXTURES / "toy_suite.py", workspace / "test_toy.py")
    git = ["git", "-c", "user.name=toy", "-c", "user.email=toy@example.invalid"]
    subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "toy"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "config", "user.email", "toy@example.invalid"], cwd=workspace, check=True
    )
    subprocess.run(["git", "add", "-A"], cwd=workspace, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "toy: the suite"], cwd=workspace, check=True)
    template = (FIXTURES / "toy-handoff.md").read_text()
    for handoff in handoffs:
        (handoff_dir / f"{handoff.lower()}.md").write_text(template.replace("$ID", handoff))
    places = review_io.Places(
        dirs=ledger.read_test_dirs(settings),
        audit_dir=tmp_path / "audit",
        scratch=tmp_path / "scratch",
        payloads=paths.payloads_dir(settings) / "test" / f"{os.getpid()}-{tmp_path.name}",
        handoff_dir=handoff_dir,
        prompt_path=paths.review_prompt(settings),
        root=ROOT,
    )
    places.audit_dir.mkdir()
    raw = {
        "ledger": str(places.dirs.ledger), "trace": str(places.dirs.trace),
        "read_only_tools": list(places.dirs.read_only_tools), "audit_dir": str(places.audit_dir),
        "scratch": str(places.scratch), "payloads": str(places.payloads),
        "handoff_dir": str(handoff_dir), "prompt_path": str(places.prompt_path), "root": str(ROOT),
    }  # fmt: skip
    places_file = tmp_path / "places.json"
    places_file.write_text(json.dumps(raw))
    return workspace, places, places_file


def stub(scenarios: dict[str, list[str]], places_file: Path, workspace: Path):
    """The builder argv per handoff: `sh` as the launcher, the stub as the session beneath it."""

    def argv_for(handoff: str, _workspace: Path) -> list[str]:
        words = " ".join(shlex.quote(w) for w in scenarios[handoff])
        line = (
            f"TOY_HANDOFF={handoff} TOY_DIR={shlex.quote(str(workspace))} "
            f"TOY_PLACES={shlex.quote(str(places_file))} {shlex.quote(sys.executable)} "
            f"{shlex.quote(str(FIXTURES / 'builder_stub.py'))} {words}; exit $?"
        )
        return ["/bin/sh", "-c", line]

    return argv_for


def handoff_id(tmp_path: Path, tag: str) -> str:
    return f"HANDOFF-T{os.getpid()}{tag}{tmp_path.name[-6:].replace('_', '')}"


def seed(
    places: review_io.Places, handoff: str, patch: str, dispositions: str = "", ok: bool = True
) -> Path:
    """A review attempt as `run_cycle` leaves it: its intent, its bundle (patch, dispositions,
    the findings table with F1) and its outcome, successful or not. Returns the bundle."""
    sha = review_io.sha256_text(patch)[:16]
    common = {"source": "kgme", "actor": "kgme.review", "job": f"review:{handoff}",
              "key": f"review:{handoff}:{sha}"}  # fmt: skip
    intent = ledger.append(
        events.make_event(kind="intent", summary=f"review:{handoff} sha={sha}", **common),
        places.dirs,
    )
    folder = review_run.write_evidence(places, handoff, intent, patch, dispositions)
    if ok:
        review_run.write_findings(
            places, handoff, intent,
            "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
            "| F1 | blocking | toy.py:2 | The seed is in the diff. | Remove it. |\n\n"
            "## Verdict\n\nBLOCK\n",
        )  # fmt: skip
    summary = (
        f"review:{handoff} cycle 1 BLOCK sha={sha} blocking=F1 transient=0 cosmetic=0 "
        "advisory=0 audit=AUDIT-0001"
        if ok else f"review:{handoff} cycle 2 attempt 1/3 reviewer timed out; not counted"
    )  # fmt: skip
    ledger.append(
        events.make_event(kind="outcome", status="ok" if ok else "error",
                          class_="blocking" if ok else "transient", ref=intent, summary=summary,
                          **common),
        places.dirs,
    )  # fmt: skip
    return folder


def recorded(handoff: str, places: review_io.Places) -> list[dict]:
    return review_io.read_handoff_events(handoff, places.dirs)


def run(queue, workspace, places, argv_for, **more) -> int:
    defaults = {"stall": timedelta(seconds=60), "poll": 0.1, "grace": 1.0, "model": "toy"}
    return loop.run_loop(queue, workspace, places, MODELS, TEMPLATE, argv_for, **(defaults | more))


@pytest.mark.blocking
def test_the_toy_closes_without_a_keystroke(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("PATH", bin_with(tmp_path))
    monkeypatch.setenv("ARBITER_LOG", str(tmp_path / "arbiters.jsonl"))
    handoff = handoff_id(tmp_path, "C")
    workspace, places, places_file = toy(tmp_path, [handoff])
    argv_for = stub({handoff: ["close"]}, places_file, workspace)
    assert run([handoff], workspace, places, argv_for) == 0
    seen = recorded(handoff, places)
    steps = []
    for e in seen:
        key = e["key"] or ""
        if key.startswith("gate:"):
            steps.append("gate " + ("green" if "green" in e["summary"] else "red"))
        elif key.startswith("loop:") and e["kind"] != "note":  # the compaction, checked below
            steps.append(f"loop {e['kind']}")
        elif e["kind"] == "outcome":
            steps.append("review " + ("PASS" if " PASS " in e["summary"] else "BLOCK"))
    assert steps == [
        "loop intent", "gate red", "gate green", "review BLOCK", "gate green", "review PASS",
        "loop outcome",
    ]  # fmt: skip
    first = seen[0]
    assert first["kind"] == "intent" and "level=loose" in first["summary"]
    assert "claude=" in first["summary"] and "codex=" in first["summary"]
    assert all(e["parent"] == first["id"] for e in seen[1:]), "one tree under the first intent"
    (stream,) = (places.scratch / "loop").glob("*/builder-0.jsonl")
    sid = loop.read_stream(stream.read_text())["session_id"]
    calls = ledger.read(places.dirs, run_id=sid)
    assert calls and all(e["parent"] == first["id"] for e in calls), "the session's calls too"
    assert all(e["class"] for e in seen if e["status"] == "error"), "every failure classed"
    closing = seen[-1]
    assert closing["status"] == "ok" and closing["ref"] == first["id"]
    commit = subprocess.run(
        ["git", "log", "-1", "--format=%h %s"], cwd=workspace, capture_output=True, text=True
    ).stdout.split()
    assert commit[1:] == ["toy:", "add", f"({handoff})"]
    screen = capsys.readouterr().out
    audits = [a for a in review.AUDIT_TOKEN.findall(" ".join(e["summary"] for e in seen))]
    assert f"{handoff}: closed" in screen and f"commit {commit[0]}" in screen
    assert all(a in screen for a in audits) and len(set(audits)) == 2
    assert "in=1200 out=340 cost=$0.42" in screen and "compactions 1" in screen
    usage = json.loads((ROOT / closing["payload_ref"]).read_text())["usage"]
    assert usage == {"input_tokens": 1200, "output_tokens": 340, "cost_usd": 0.42}
    linked = [e for e in seen if f"builder session {sid}" in (e["summary"] or "")]
    assert len(linked) == 1 and linked[0]["parent"] == first["id"], "the session, named (F4)"
    compacted = [e for e in seen if "compacted" in (e["summary"] or "")]
    assert len(compacted) == 1 and "150000 context tokens" in compacted[0]["summary"]
    assert review.loop_state(seen).cycles == 2, "a compaction is not a cycle"
    assert (places.handoff_dir / "done" / f"{handoff.lower()}.md").exists()


@pytest.mark.blocking
def test_an_unfixable_seed_goes_to_the_arbiters_halts_and_the_queue_goes_on(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("PATH", bin_with(tmp_path))
    monkeypatch.setenv("ARBITER_LOG", str(tmp_path / "arbiters.jsonl"))
    monkeypatch.setenv("ARBITER_MODE", "agree")
    stuck, second = handoff_id(tmp_path, "U"), handoff_id(tmp_path, "V")
    workspace, places, places_file = toy(tmp_path, [stuck, second])
    argv_for = stub({stuck: ["unfixable"], second: ["close"]}, places_file, workspace)
    assert run([stuck, second], workspace, places, argv_for) == 1
    seen = recorded(stuck, places)
    rulings = [e for e in seen if (e["key"] or "").startswith("ruling:F1")]
    assert sorted(e["key"] for e in rulings) == [
        "ruling:F1=blocking",
        "ruling:F1@claude-fable-5-1=blocking",
        "ruling:F1@claude-opus-5-5=blocking",
    ]
    for each in (e for e in rulings if "@" in e["key"]):
        payload = json.loads((ROOT / each["payload_ref"]).read_text())
        brief = (
            Path(payload["brief"])
            if Path(payload["brief"]).is_absolute()
            else ROOT / payload["brief"]
        )
        assert payload["brief_sha256"] == review_io.sha256_text(brief.read_text())
        assert "F1 disputed" in brief.read_text() and "SEED" in brief.read_text()
    calls = [json.loads(line) for line in (tmp_path / "arbiters.jsonl").read_text().splitlines()]
    assert (
        sorted(c["model"] for c in calls) == sorted(MODELS) and calls[0]["pid"] != calls[1]["pid"]
    )
    assert all("F1 disputed" in c["brief"] for c in calls), "the brief reaches each arbiter"
    halt = [e for e in seen if (e["key"] or "").startswith("halt:")]
    assert halt and "F1 blocked again after its ruling was executed" in halt[-1]["summary"]
    closing = [e for e in seen if (e["key"] or "").startswith("loop:")][-1]
    assert closing["status"] == "error" and closing["class"] == "blocking"
    assert "halted" in closing["summary"] and "commit none" in closing["summary"]
    log = subprocess.run(["git", "log", "--format=%s"], cwd=workspace, capture_output=True,
                         text=True).stdout  # fmt: skip
    assert stuck not in log and f"({second})" in log, "no commit on a halt; the next one closes"
    screen = capsys.readouterr().out
    assert f"{stuck}: halted" in screen and f"{second}: closed" in screen
    assert "arbitrated F1" in screen


@pytest.mark.blocking
def test_splitting_arbiters_are_settled_by_blast_radius_and_the_split_is_listed(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("PATH", bin_with(tmp_path))
    monkeypatch.setenv("ARBITER_LOG", str(tmp_path / "arbiters.jsonl"))
    monkeypatch.setenv("ARBITER_MODE", "split")
    handoff = handoff_id(tmp_path, "S")
    _, places, _ = toy(tmp_path, [handoff])
    seed(places, handoff, "+    return a + b  # SEED\n", "F1 disputed.")
    settled = review_run.run_arbiters(handoff, "F1", "F1 disputed.", places, MODELS, TEMPLATE)
    assert settled["class"] == "advisory" and settled["split"]
    keys = [e["key"] for e in recorded(handoff, places)]
    assert "ruling:F1=advisory" in keys and "split:F1" in keys
    split = [e for e in recorded(handoff, places) if e["key"] == "split:F1"][0]
    assert "approval screen" in split["summary"] and split["class"] == "advisory"
    assert review_run.run_arbiters(handoff, "F1", "", places, MODELS, TEMPLATE) is None, "once"


@pytest.mark.blocking
@pytest.mark.parametrize("scenario,status", [("silent", "stalled"), ("busy", "ended")])
def test_a_silent_builder_is_killed_with_its_group_and_a_busy_one_is_not(
    tmp_path: Path, monkeypatch, scenario: str, status: str
) -> None:
    monkeypatch.setenv("PATH", bin_with(tmp_path))
    handoff = handoff_id(tmp_path, scenario[0].upper())
    workspace, places, places_file = toy(tmp_path, [handoff])
    started: list[subprocess.Popen] = []
    real_start = loop.start_builder

    def keep(*args, **kwargs):
        started.append(real_start(*args, **kwargs))
        return started[-1]

    monkeypatch.setattr(loop, "start_builder", keep)
    argv_for = stub({handoff: [scenario]}, places_file, workspace)
    assert run([handoff], workspace, places, argv_for, stall=timedelta(seconds=4)) == 1
    closing = [e for e in recorded(handoff, places) if (e["key"] or "").startswith("loop:")][-1]
    leader = started[0].pid
    assert not [row for row in loop.read_group() if row[2] == leader], "the whole group is gone"
    quarantine = places.scratch / "loop" / "quarantine"
    if status == "stalled":
        assert "stalled run killed" in closing["summary"] and closing["class"] == "blocking"
        assert started[0].returncode is not None and started[0].returncode < 0, "killed"
        assert len(list(quarantine.iterdir())) == 1
    else:
        assert "stalled" not in closing["summary"] and started[0].returncode == 0
        assert "without a final PASS" in closing["summary"] and not quarantine.exists()


@pytest.mark.blocking
@pytest.mark.parametrize("message", [LIMIT_AT, "Claude AI usage limit reached; no time given"])
def test_a_limit_pauses_until_its_reset_or_the_interval_and_is_no_strike(
    tmp_path: Path, monkeypatch, message: str
) -> None:
    monkeypatch.setenv("PATH", bin_with(tmp_path))
    handoff = handoff_id(tmp_path, "L")
    workspace, places, places_file = toy(tmp_path, [handoff])
    slept: list[float] = []

    def sleep(seconds: float) -> None:
        if seconds > 5:
            slept.append(seconds)  # the pause, recorded rather than waited
        else:
            import time

            time.sleep(seconds)

    argv_for = stub({handoff: ["limited", message]}, places_file, workspace)
    clock = datetime.now().astimezone()
    assert run([handoff], workspace, places, argv_for, sleep=sleep) == 0
    seen = recorded(handoff, places)
    pauses = [e for e in seen if "paused until" in (e["summary"] or "")]
    assert len(pauses) == 1 and pauses[0]["class"] == "transient" and len(slept) == 1
    if "4:22 PM" in message:
        assert "T16:22:00" in pauses[0]["summary"]
        lifted = loop.reset_time(message, clock)
        assert abs(slept[0] - (lifted - clock).total_seconds()) < 60
    else:
        assert abs(slept[0] - 1800) < 60, "no time named: the 30-minute interval"
    state = review.loop_state(seen)
    assert state.cycles == 2 and not state.halt, "a pause is no cycle and no strike"
    closing = [e for e in seen if (e["key"] or "").startswith("loop:") and e["kind"] == "outcome"]
    usage = json.loads((ROOT / closing[-1]["payload_ref"]).read_text())["usage"]
    assert usage == {"input_tokens": 1300, "output_tokens": 350, "cost_usd": 0.47}, "both tries"


@pytest.mark.blocking
def test_caffeinate_holds_the_loops_pid_and_is_gone_at_its_end(tmp_path: Path, monkeypatch):
    if shutil.which("caffeinate") is None:
        pytest.skip("caffeinate is macOS's")
    seen: list[subprocess.Popen] = []
    real = loop.start_caffeinate

    def keep():
        seen.append(real())
        return seen[-1]

    monkeypatch.setattr(loop, "start_caffeinate", keep)
    handoff = handoff_id(tmp_path, "K")
    workspace, places, _ = toy(tmp_path, [])  # no handoff file: refused, quickly
    assert run([handoff], workspace, places, lambda h, w: ["true"]) == 1
    assert seen[0].args == ["caffeinate", "-i", "-w", str(os.getpid())]
    assert seen[0].poll() is not None, "released when the loop ends"
    refused = [e for e in recorded(handoff, places) if (e["key"] or "").startswith("loop:")]
    assert refused[-1]["class"] == "blocking" and "not an open handoff" in refused[-1]["summary"]


# ---------------------------------------------------------------- the pure logic


@pytest.mark.blocking
def test_reset_time_reads_the_harnesses_limit_messages() -> None:
    now = datetime(2026, 10, 26, 18, 0, tzinfo=datetime.now().astimezone().tzinfo)
    assert loop.reset_time("try again at 4:22 PM, usage limit", now) == now.replace(
        day=27, hour=16, minute=22
    ), "past today is tomorrow"
    assert loop.reset_time(
        "You've hit your usage limit. ... try again at Oct 9th, 2026 12:21 AM.", now
    ) == now.replace(month=10, day=9, hour=0, minute=21)
    assert loop.reset_time("5-hour limit reached ∙ resets 9pm", now) == now.replace(hour=21)
    epoch = int((now + timedelta(hours=2)).timestamp())
    assert loop.reset_time(f"Claude AI usage limit reached|{epoch}", now) == now + timedelta(
        hours=2
    )
    assert loop.reset_time("rate limit: try again in 1 hour 5 minutes", now) == now + timedelta(
        hours=1, minutes=5
    )
    assert loop.reset_time("usage limit reached", now) is None, "no time: the interval"
    assert loop.reset_time("try again at 4:22 PM", now) is None, "no limit named"


@pytest.mark.blocking
def test_stall_needs_silence_and_no_live_call() -> None:
    now = datetime.now().astimezone()
    old = now - timedelta(minutes=16)
    stall = timedelta(minutes=15)
    assert loop.is_stalled(old, now, stall, 0)
    assert not loop.is_stalled(old, now, stall, 1), "a long call is not a stall"
    assert not loop.is_stalled(now - timedelta(minutes=14), now, stall, 0)
    rows = [(10, 1, 10), (11, 10, 10), (12, 11, 10), (13, 12, 10), (20, 1, 20)]
    assert loop.live_children(rows, 10) == 2, "the launcher and the session are not calls"
    assert loop.live_children(rows[:2], 10) == 0


@pytest.mark.blocking
def test_settle_agrees_or_takes_the_smallest_reversible_blast_radius() -> None:
    def ruling(arbiter, cls, blast, reversible=True):
        return {"arbiter": arbiter, "class": cls, "option": f"{arbiter} option",
                "blast_radius": blast, "reversible": reversible, "reason": ""}  # fmt: skip

    agreed = loop.settle(
        [ruling("a", "blocking", 3), ruling("b", "blocking", 1) | {"option": "a option"}]
    )
    assert agreed["class"] == "blocking" and not agreed["split"]
    split = loop.settle([ruling("a", "blocking", 3), ruling("b", "advisory", 1)])
    assert split["class"] == "advisory" and split["split"] and "took b" in split["reason"]
    one_way = loop.settle([ruling("a", "blocking", 3), ruling("b", "advisory", 1, False)])
    assert one_way["class"] == "blocking", "a one-way door loses to any reversible option"
    tie = loop.settle([ruling("a", "advisory", 2), ruling("b", "blocking", 2)])
    assert tie["class"] == "blocking", "on a tie, the stricter class"
    assert loop.settle([]) is None


@pytest.mark.blocking
def test_next_handoff_keeps_the_queue_order_and_read_stream_reads_the_builder() -> None:
    assert loop.next_handoff(["B", "A"], set()) == "B"
    assert loop.next_handoff(["B", "A"], {"B"}) == "A"
    assert loop.next_handoff(["B"], {"B"}) is None
    text = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "s1"}),
        json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 10,
                    "cache_read_input_tokens": 90000}}}),
        json.dumps({"type": "system", "subtype": "compact_boundary", "compact_metadata": {}}),
        "Claude AI usage limit reached|1761523200",
        json.dumps({"type": "result", "usage": {"output_tokens": 5}, "total_cost_usd": 0.1}),
    ])  # fmt: skip
    found = loop.read_stream(text)
    assert found["session_id"] == "s1" and found["cost_usd"] == 0.1
    assert found["compactions"] == [{"trigger": None, "context_tokens": 90010}]
    assert found["plain"] == ["Claude AI usage limit reached|1761523200"]


# ---------------------------------------------------------------- review cycle 1 (AUDIT-0148)


@pytest.mark.blocking
def test_f1_the_session_gets_its_execution_request_and_the_argv_is_kgmes(tmp_path: Path) -> None:
    from kgme import cli

    argv = loop.builder_argv("HANDOFF-0099", tmp_path)
    parsed = cli.build_parser().parse_args(argv[argv.index("kgme") + 1 :])
    assert (parsed.command, parsed.level, parsed.handoff) == ("session", "loose", "HANDOFF-0099")
    assert parsed.extra == ["--output-format", "stream-json", "--verbose"]
    request = loop.execution_request("HANDOFF-0099", "docs/handoff/x.md")
    assert "HANDOFF-0099" in request and "docs/handoff/x.md" in request
    out = tmp_path / "out.txt"
    proc = loop.start_builder(["/bin/sh", "-c", "cat; exit $?"], tmp_path, out, dict(os.environ),
                              request)  # fmt: skip
    assert proc.wait(timeout=10) == 0 and out.read_text() == request, "the request on stdin"


@pytest.mark.blocking
def test_f3_a_run_closes_only_on_a_final_pass_with_a_commit() -> None:
    def ev(kind, key, summary, status=None):
        return {"kind": kind, "key": key, "summary": summary, "status": status}

    passed = ev("outcome", "review:H:a", "review:H cycle 2 PASS sha=a", "ok")
    green = ev("note", "gate:H:2", "review:H gate green failing=0")
    red = ev("note", "gate:H:3", "review:H gate red failing=2")
    failed = ev("outcome", "review:H:b", "review:H cycle 3 attempt 1/3 timed out", "error")
    ok = [green, passed]
    assert loop.close_status(ok, "abc1234", True) == "closed"
    assert loop.close_status(ok, None, True) == "ready", "PASS, nothing committed: diffs pending"
    assert loop.close_status(ok, "abc1234", False) == "ready", "a commit, the handoff still open"
    assert loop.close_status([*ok, red], "abc1234", True) == "ended", "a red gate after the PASS"
    assert loop.close_status([*ok, failed], "abc1234", True) == "ended", "a failed review after"
    assert loop.close_status([green, red, passed], "abc1234", True) == "ended", (
        "cycle 2 F3: a PASS after a red gate with no green gate between is no close"
    )
    assert loop.close_status([], "abc1234", True) == "ended"


@pytest.mark.blocking
def test_f6_a_split_among_one_way_doors_goes_to_michou() -> None:
    a = {"arbiter": "a", "class": "blocking", "option": "x", "blast_radius": 2,
         "reversible": False, "reason": ""}  # fmt: skip
    b = a | {"arbiter": "b", "class": "advisory", "blast_radius": 1}
    settled = loop.settle([a, b])
    assert settled["escalate"] and settled["class"] is None and "one-way" in settled["reason"]
    assert loop.settle([a, a | {"arbiter": "b"}])["escalate"] is False, "agreement settles"


@pytest.mark.blocking
@pytest.mark.parametrize(
    "reply",
    [
        '{"class": "advisory"}',
        '{"class": "advisory", "option": "x", "reversible": "false", "blast_radius": 1, '
        '"reason": "r"}',
        '{"class": "advisory", "option": "x", "reversible": true, "blast_radius": 9, '
        '"reason": "r"}',
        '{"class": "advisory", "option": "x", "reversible": true, "blast_radius": "two", '
        '"reason": "r"}',
        '{"class": "advisory", "option": "", "reversible": true, "blast_radius": 1, "reason": "r"}',
    ],
)
def test_f7_a_malformed_ruling_is_rejected_not_settled(reply: str) -> None:
    assert review_run.parse_ruling(f"reasoning\n{reply}") is None
    good = (
        '{"class": "advisory", "option": "x", "reversible": false, "blast_radius": 5, '
        '"reason": "r"}'
    )
    assert review_run.parse_ruling(good)["reversible"] is False


@pytest.mark.blocking
@pytest.mark.parametrize("failing", [1, 2])
def test_f5_the_pair_needs_two_valid_rulings_and_a_failure_stays_pending(
    tmp_path: Path, failing: int
) -> None:
    handoff = handoff_id(tmp_path, "P")
    _, places, _ = toy(tmp_path, [handoff])
    seed(places, handoff, "+    return a + b  # SEED\n", "F1 disputed.")
    good = (
        'ok\n{"class": "blocking", "option": "remove it", "reversible": true, '
        '"blast_radius": 1, "reason": "r"}'
    )

    def run_one(model, brief, scratch):
        return "claude -p", "" if MODELS.index(model) < failing else good

    assert review_run.run_arbiters(handoff, "F1", "", places, MODELS, TEMPLATE, run_one) is None
    keys = [e["key"] for e in recorded(handoff, places)]
    assert not [k for k in keys if k.startswith("ruling:F1=")], "nothing settles on one ruling"
    assert sum(k.startswith("arbiter-failed:F1") for k in keys) == failing
    retried = review_run.run_arbiters(
        handoff, "F1", "", places, MODELS, TEMPLATE, lambda m, b, s: ("claude -p", good)
    )
    assert retried and retried["class"] == "blocking", "pending, then settled on the retry"


@pytest.mark.blocking
def test_f9_a_diff_too_large_for_the_brief_is_refused_not_cut(tmp_path: Path) -> None:
    handoff = handoff_id(tmp_path, "D")
    _, places, _ = toy(tmp_path, [handoff])
    seed(places, handoff, "+x\n" * review_run.DIFF_IN_BRIEF_CHARS)
    called = []
    assert (
        review_run.run_arbiters(
            handoff, "F1", "", places, MODELS, TEMPLATE, lambda m, b, s: called.append(m)
        )
        is None
    )
    assert not called, "no arbiter rules on a cut diff"
    refused = [e for e in recorded(handoff, places) if (e["key"] or "").startswith("arbiter-")]
    assert refused and "too large" in refused[-1]["summary"]
    small = handoff_id(tmp_path, "E")
    _, places2, _ = toy(tmp_path / "e", [small]) if (tmp_path / "e").mkdir() is None else (0, 0, 0)
    seed(places2, small, "+y\n" * 70_000)  # past the old cut
    briefs = []
    review_run.run_arbiters(small, "F1", "", places2, MODELS, TEMPLATE,
                            lambda m, b, s: (briefs.append(b), ("claude -p", ""))[1])  # fmt: skip
    assert briefs and briefs[0].count("+y") == 70_000, "the whole diff, uncut"


@pytest.mark.blocking
def test_f11_the_unattended_queue_admits_only_michous_handoffs(tmp_path: Path) -> None:
    handoff = handoff_id(tmp_path, "W")
    _, places, _ = toy(tmp_path, [handoff])
    path = places.handoff_dir / f"{handoff.lower()}.md"
    path.write_text(path.read_text().replace("from: michou", "from: cowork"))
    assert "from michou" in loop.read_handoff_ready(places.handoff_dir, handoff)


# ---------------------------------------------------------------- review cycle 2 (AUDIT-0149)


@pytest.mark.blocking
def test_f13_a_failed_arbiter_call_never_reuses_an_earlier_reply(
    tmp_path: Path, monkeypatch
) -> None:
    folder = tmp_path / "bin"
    folder.mkdir()
    good = (
        '{"class": "advisory", "option": "keep it", "reversible": true, "blast_radius": 1, '
        '"reason": "r"}'
    )
    codex = folder / "codex"
    codex.write_text(
        "#!/bin/sh\n"
        f'if [ -e "{tmp_path}/once" ]; then exit 1; fi\n'
        f'touch "{tmp_path}/once"\n'
        'out=""; while [ $# -gt 0 ]; do [ "$1" = "-o" ] && out="$2"; shift; done\n'
        f"printf '%s\\n' '{good}' > \"$out\"\n"
    )
    codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{folder}:{os.environ['PATH']}")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    first = review_run.run_arbiter("gpt-toy", "brief", scratch)
    assert review_run.parse_ruling(first[1])["class"] == "advisory"
    second = review_run.run_arbiter("gpt-toy", "brief", scratch)
    assert second[1] == "", "a nonzero exit is no reply, whatever an older file says"


@pytest.mark.blocking
def test_f14_the_arbiters_see_the_reviewed_attempts_own_bundle_or_nothing(tmp_path: Path) -> None:
    """Review cycles 2 and 3, F14: the bundle of the attempt the newest successful outcome
    answers, whole and matching, or no arbitration."""
    mine, other = handoff_id(tmp_path, "M"), handoff_id(tmp_path, "O")
    _, places, _ = toy(tmp_path, [mine, other])
    seed(places, mine, "+mine # SEED\n", "F1 disputed: mine.")
    seed(places, other, "+theirs\n", "theirs")  # another handoff's later cycle
    seed(places, mine, "+mine # SEED\n", "a later attempt's words", ok=False)  # same diff, failed
    review_io.write_text(places.scratch / "review.patch", "+overwritten\n")
    briefs: list[str] = []

    def run_one(model, brief, scratch):
        briefs.append(brief)
        return "claude -p", ""

    review_run.run_arbiters(mine, "F1", "", places, MODELS, TEMPLATE, run_one)
    assert briefs and all("+mine # SEED" in b and "F1 disputed: mine." in b for b in briefs)
    assert all("The seed is in the diff." in b for b in briefs), "the attempt's own row"
    assert not any(w in b for b in briefs for w in ("theirs", "overwritten", "a later attempt"))
    for part, why in (("review.patch", "does not match"), ("review.dispositions", "missing"),
                      ("findings.md", "missing"), ("row", "no row for F1")):  # fmt: skip
        gone = handoff_id(tmp_path, "G" + part[:3].replace(".", ""))
        folder = seed(places, gone, "+gone\n", "d")
        if part == "review.patch":
            (folder / part).write_text("+tampered\n")
        elif part == "row":
            (folder / "findings.md").write_text("| F2 | blocking | x | y | z |\n")
        else:
            (folder / part).unlink()
        briefs.clear()
        assert review_run.run_arbiters(gone, "F1", "", places, MODELS, TEMPLATE, run_one) is None
        assert not briefs, f"{part}: refused before any arbiter runs"
        assert why in recorded(gone, places)[-1]["summary"], part


@pytest.mark.blocking
def test_f15_the_same_class_with_different_recommendations_is_a_split() -> None:
    def ruling(arbiter, option, blast, reversible=True):
        return {"arbiter": arbiter, "class": "blocking", "option": option, "blast_radius": blast,
                "reversible": reversible, "reason": "r"}  # fmt: skip

    narrow, broad = ruling("a", "patch the test", 1), ruling("b", "rewrite the module", 3)
    settled = loop.settle([broad, narrow])
    assert settled["split"] and not settled["escalate"] and "took a" in settled["reason"]
    doors = loop.settle([ruling("a", "drop the table", 2, False), ruling("b", "migrate", 2, False)])
    assert doors["escalate"] and doors["class"] is None, "two one-way doors go to Michou"
    same = loop.settle([ruling("a", "Remove the seed", 1), ruling("b", "remove  the seed", 2)])
    assert not same["split"], "one recommendation, spelled alike, is agreement"


@pytest.mark.blocking
def test_cycle_2_f8_unchanged_work_reviewed_after_the_ruling_is_not_its_execution() -> None:
    from tests.test_review import note, outcome, sha

    history = [outcome("H", 1, "BLOCK", "F2", sha(1)), outcome("H", 2, "BLOCK", "F2", sha(2))]
    history.append(note("H", "ruling:F2=blocking"))
    same = outcome("H", 3, "BLOCK", "F2", sha(2))  # captured before settlement, reviewed after
    assert not review.loop_state([*history, same]).halt
    changed = outcome("H", 4, "BLOCK", "F2", sha(4))
    assert review.loop_state([*history, same, changed]).halt


@pytest.mark.blocking
def test_cycle_2_f8_a_cycle_counts_only_if_its_intent_named_the_ruling() -> None:
    """Fable's option: the ruling settled during the gate, before the intent, and the intent
    (which read the rulings before its gate) does not name it: not its execution."""
    from tests.test_review import note, outcome, sha

    def intent(ruled: str) -> dict:
        return events.make_event(
            source="kgme", actor="kgme.review", kind="intent", job="review:H", key="review:H:i",
            summary=f"review:H cycle n sha=x reviewer=fake ruled={ruled}",
        )  # fmt: skip

    history = [outcome("H", 1, "BLOCK", "F2", sha(1)), outcome("H", 2, "BLOCK", "F2", sha(2))]
    history.append(note("H", "ruling:F2=blocking"))
    blind = intent("-")
    history += [blind, outcome("H", 3, "BLOCK", "F2", sha(3)) | {"ref": blind["id"]}]
    assert not review.loop_state(history).halt, "it read the rulings before the settlement"
    aware = intent("F2")
    history += [aware, outcome("H", 4, "BLOCK", "F2", sha(4)) | {"ref": aware["id"]}]
    assert review.loop_state(history).halt


@pytest.mark.blocking
def test_cycle_2_f3_the_commit_is_after_the_start_and_after_the_pass(tmp_path: Path) -> None:
    workspace, _, _ = toy(tmp_path, [])
    git = ["git", "-c", "user.name=toy", "-c", "user.email=toy@example.invalid"]

    def commit(message: str, when: int) -> None:
        (workspace / f"f{when}.txt").write_text(message)
        subprocess.run(["git", "add", "-A"], cwd=workspace, check=True)
        env = {
            **os.environ,
            "GIT_COMMITTER_DATE": f"{when} +0000",
            "GIT_AUTHOR_DATE": f"{when} +0000",
        }
        subprocess.run([*git, "commit", "-q", "-m", message], cwd=workspace, check=True, env=env)

    commit("toy: before the run (HANDOFF-X)", 1_800_000_000)
    start = loop.read_head(workspace)
    commit("toy: before the PASS (HANDOFF-X)", 1_800_000_100)
    passed = datetime.fromtimestamp(1_800_000_200).astimezone()
    assert loop.read_commit(workspace, start, "HANDOFF-X", passed) is None, "none after the PASS"
    commit("toy: after the PASS (HANDOFF-X)", 1_800_000_300)
    found = loop.read_commit(workspace, start, "HANDOFF-X", passed)
    head = subprocess.run(["git", "log", "-1", "--format=%h"], cwd=workspace, capture_output=True,
                          text=True).stdout.strip()  # fmt: skip
    assert found == head
