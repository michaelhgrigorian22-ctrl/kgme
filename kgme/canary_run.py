"""One cell of the agent tier, run (HANDOFF-0032; review AUDIT-0028 F3 and F6): intent, launch,
measurement, outcome.

Purpose: every path out of a cell in one function, so the fast tier can walk each of them with
a fake launcher: an occupied target, a launch that raises, a worker that times out, a stream
without its terminal event or with a terminal error, and a measurement. Whatever happens after
the intent is written closes that same intent (ADR-013 §4).
Inputs: the `Cell`; `launch`, which runs the worker and returns its parsed `Run`; the probe's
`Aim`; `read_effect` and `read_refusals`, which read the world and the test ledger for a run;
whether the target was occupied before launch; the streams, run id, settings digest, matrix,
and the project settings' fingerprints for the intent's payload.
Outputs: the `Observed` written for the cell, and the `Run` when the worker returned one.
Side effects: the intent and outcome events and the matrix line, through `kgme.canary`; and
whatever the three callables do (a model run, a filesystem or socket read, a ledger read).
"""

import subprocess
from collections.abc import Callable
from pathlib import Path

from kgme import canary, canary_stream, ledger

OUT_OF_TURNS = "error_max_turns"  # Claude Code's result subtype when `--max-turns` is reached


def run_cell(
    cell: canary.Cell,
    launch: Callable[[], canary_stream.Run],
    aim: canary_stream.Aim,
    read_effect: Callable[[canary_stream.Run], bool],
    read_refusals: Callable[[canary_stream.Run], frozenset[str]],
    occupied: bool,
    dirs: ledger.Dirs,
    run_id: str,
    settings_sha: str,
    matrix: Path | None = None,
    fingerprints: canary.Fingerprints | None = None,
    read_control: Callable[[canary_stream.Run], bool] | None = None,
) -> tuple[canary.Observed, canary_stream.Run | None]:
    """Effects: intent, the worker, outcome. A cell that could not be measured is transient:
    an ADR-016 transient against the tooling, never a verdict on a layer."""
    intent = canary.write_intent(cell, dirs, run_id, settings_sha, fingerprints)

    def transient(why: str, run: canary_stream.Run | None) -> tuple[canary.Observed, None]:
        observed = canary.Observed(False, why, transient=True)
        canary.write_outcome(cell, observed, dirs, run_id, intent, matrix)
        return observed, run

    if occupied:
        return transient("the probe target is occupied; nothing launched", None)
    try:
        run = launch()
    except subprocess.TimeoutExpired:
        return transient("the worker timed out", None)
    except OSError as exc:
        return transient(f"the worker could not be launched: {type(exc).__name__}: {exc}", None)
    # A worker whose turns ran out after its aimed call still left the call, its refusal and
    # the world to read (HANDOFF-0060 §2): its silence afterwards is not a failure. Such a run
    # is measured only when the measurement decides, a refusal at a named layer or the
    # effect; anything else stays transient, as before.
    ran_out = run.complete and run.error and run.subtype == OUT_OF_TURNS
    if (run.returncode != 0 or not run.complete or run.error) and not ran_out:
        state = "complete" if run.complete else "incomplete"
        terminal = f", terminal error {run.subtype or '?'}" if run.error else ""
        return transient(f"invocation failed: exit {run.returncode}, stream {state}{terminal}", run)
    effect = read_effect(run)  # before the control, which itself reaches the listener
    control = read_control(run) if read_control is not None else None
    observed = canary_stream.classify(
        run, aim, effect, cell.worker, read_refusals(run), control_seen=control
    )
    if ran_out and not (observed.refused or effect):
        why = f"the worker ran out of turns ({run.subtype}) before a refusal or an effect was seen"
        return transient(why, run)
    if ran_out:
        observed = canary.Observed(observed.refused, f"{observed.detail}; then {run.subtype}")
    canary.write_outcome(cell, observed, dirs, run_id, intent, matrix)
    return observed, run


def read_hook_refusals(dirs: ledger.Dirs, run: canary_stream.Run) -> frozenset[str]:
    """Effect: the tool-call ids the guard refused in this worker's session, from the test
    ledger: each refused outcome the hook wrote keys its call by the vendor's `tool_use_id`
    (`kgme.hooks.common.call_key`). How a `loop-write` cell reads the guard's refusal from
    the ledger rather than from the model's reply (HANDOFF-0060 §2)."""
    if not run.session_id:
        return frozenset()
    return frozenset(
        e["key"]
        for e in ledger.read(dirs, run_id=run.session_id)
        if e["kind"] == "outcome" and e["status"] == "refused" and e.get("key")
    )
