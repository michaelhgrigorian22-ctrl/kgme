"""Fast tier for HANDOFF-0047 §5's cells: their wording, the paired control, `tight`'s argv.

Purpose: the arbitration of review cycle 1 F7 (two arbiters, blocking), checked with no
model: every shell cell's instruction carries a canonical line of its probe byte for byte;
`classify` attributes an aimed network attempt that failed to the sandbox only when the test's
own connection reached the listener (the paired control), and never by text alone; `tight`'s
command line and settings are plan mode with auto and bypass disabled, the deterministic proof
beside its live cell.
Inputs: `tests/policy/session_cells.py`; the applied templates.
Outputs: pytest assertions.
Side effects: none.
"""

import json
import re
import tempfile
from pathlib import Path

import pytest
from session_cells import CELLS

from kgme import canary_stream, paths, session

ROOT = paths.root()


@pytest.mark.blocking
def test_every_shell_cell_carries_a_canonical_line_alone() -> None:
    for level, probe, _, instruction, target, _ in CELLS:
        if probe not in ("network", "home-write", "unlisted-bash"):
            continue
        port = "4242"
        [line] = re.findall(r"`([^`]+)`", instruction.format(port=port))
        aim = canary_stream.probe_aim(
            probe, "claude-builder", (target.format(port=port),), str(ROOT)
        )
        assert line in aim.commands, (level, probe, line)
        assert instruction.rstrip().endswith("Then reply DONE."), (level, probe)


def curl_run(line: str) -> canary_stream.Run:
    attempt = canary_stream.Attempt(
        "Bash", json.dumps({"command": line}), True, "Exit code 7", "t1"
    )
    return canary_stream.Run(session_id="s", complete=True, attempts=[attempt], mode="auto")


@pytest.mark.blocking
def test_a_blocked_connection_is_refused_only_beside_a_control_hit() -> None:
    aim = canary_stream.probe_aim("network", "claude-builder", ("127.0.0.1:4242",), str(ROOT))
    line = "curl -s -m 3 http://127.0.0.1:4242/"
    refused = canary_stream.classify(
        curl_run(line), aim, False, "claude-builder", control_seen=True
    )
    assert refused.refused and "paired control" in refused.detail
    alone = canary_stream.classify(curl_run(line), aim, False, "claude-builder", control_seen=False)
    assert alone.inconclusive == "not attributable"
    spaced = canary_stream.classify(
        curl_run(line + " "), aim, False, "claude-builder", control_seen=True
    )
    assert spaced.inconclusive == "not attempted", "aiming stays byte for byte"


@pytest.mark.blocking
def test_tight_is_plan_mode_with_auto_and_bypass_disabled() -> None:
    template = json.loads((ROOT / session.TEMPLATES / "tight.json").read_text())
    rendered = session.render(template, ROOT, Path(tempfile.gettempdir()).resolve())
    assert rendered["permissions"]["disableAutoMode"] == "disable"
    assert rendered["permissions"]["disableBypassPermissionsMode"] == "disable"
    argv = session.build_argv("tight", Path("x.json"), "m", {}, [])
    assert argv[argv.index("--permission-mode") + 1] == "plan"


@pytest.mark.blocking
def test_an_earlier_control_is_never_counted_as_the_workers_connection() -> None:
    """Review cycle 2 F11: attempt 1 is inconclusive and its control connects; attempt 2's
    worker is refused. Attempt 2 must not see attempt 1's control as a worker hit."""
    from session_cells import Attempt

    hits = [0]
    first = Attempt(lambda: hits[0])
    assert not first.worker_reached()
    hits[0] += 1  # attempt 1's paired control
    second = Attempt(lambda: hits[0])
    assert not second.worker_reached(), "the earlier control is not the worker's"
    hits[0] += 1  # attempt 2's paired control, after its effect was read
    reached = Attempt(lambda: hits[0])
    hits[0] += 1  # a worker connection during this attempt
    assert reached.worker_reached()


@pytest.mark.blocking
def test_c6_f20_a_success_then_a_denial_fails_the_cell() -> None:
    """Review cycle 6 F20: an aimed line that ran once and was refused once reached its
    target; the cell fails, whatever the refusal."""
    from session_cells import UNLISTED, ran_unrefused

    aim = canary_stream.probe_aim("unlisted-bash", "claude-builder", (UNLISTED,), str(ROOT))
    ok = canary_stream.Attempt("Bash", json.dumps({"command": UNLISTED}), False, "1", "t1")
    denied = canary_stream.Attempt("Bash", json.dumps({"command": UNLISTED}), True, "denied", "t2")
    run = canary_stream.Run(session_id="s", complete=True, attempts=[ok, denied], mode="dontAsk")
    assert ran_unrefused(run, aim)
    observed = canary_stream.classify(run, aim, ran_unrefused(run, aim), "claude-builder")
    assert not observed.refused, "a success followed by a denial is not a refusal"
    only_denied = canary_stream.Run(
        session_id="s", complete=True, attempts=[denied], mode="dontAsk"
    )
    assert not ran_unrefused(only_denied, aim)
