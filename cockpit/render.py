"""The cockpit's view of the ledger, pure half (HANDOFF-0037 §2 and its amendment of 2026-10-21).

Purpose: what the page displays, decided here and nowhere else. Events are grouped by
`run_id`, an intent is paired with the outcome whose `ref` names it, an intent no outcome
names is unmatched, events nest by `parent`, and trace events (the read-only tools, ADR-019
§2) are collapsed under their parent until the page expands them. Each run's lifecycle
(working, waiting, transient, blocked, and quiet within working) is one function, ported rule
for rule from the station prototype (`docs/design/cockpit-v0/station/index.html`, `lifecycle`
and `runClosed`; its README states the rules) and tested against the design's sample events,
so the page shows what `/api/events` returns and never decides a state itself.
Checked against the approved canvas (the arbiter's ruling on review cycle 1 F2): ported from
the station at `997a730` before any approval existed, then compared by
`tests/station_equivalence.py` with the station at `11b686b`, the commit Michou's `canvas`
approval of 2026-10-25 names: the same 180000 ms quiet floor, 49 clocks, 255 comparisons, no
disagreement. Rerun it against any later approval.
Inputs: ledger and trace events as `kgme.ledger.read` returns them; the time, in epoch ms.
Outputs: plain dicts, ready for JSON.
Side effects: none.
"""

import statistics
from datetime import datetime

QUIET_FLOOR_MS = 3 * 60 * 1000
OPS = ("intent", "outcome")
MOVES = ("intent", "outcome", "approval")


def ts_ms(ts: str) -> int:
    """An event's `ts` as epoch milliseconds."""
    return int(datetime.fromisoformat(ts).timestamp() * 1000)


def lifecycle(events: list[dict], now_ms: int) -> tuple[str, str]:
    """A run's word and its quiet note (`quiet Nm`, or empty), from its events in order.

    In order: blocked while a blocking note is the newest of the notes, intents, outcomes and
    approvals since it (a halt holds until the run moves again); working with no intent or
    outcome yet; transient when the newest intent-or-outcome is a blocking outcome that names
    a retry time, or a transient outcome; blocked when it is a blocking outcome; waiting when
    it is an intent; else working, and quiet when no event has come for longer than the
    run's median gap between intents (the ordinary median), never less than three minutes."""
    blocking_note = moved = -1
    for index in range(len(events) - 1, -1, -1):
        kind = events[index]["kind"]
        if moved < 0 and kind in MOVES:
            moved = index
        if kind == "note" and events[index].get("class") == "blocking":
            blocking_note = index
            break
    if blocking_note >= 0 and blocking_note > moved:
        return "blocked", ""
    ops = [e for e in events if e["kind"] in OPS]
    if not ops:
        return "working", ""
    newest = ops[-1]
    if newest["kind"] == "outcome" and newest.get("class") == "blocking":
        retry = "retry after" in (newest.get("summary") or "")
        return ("transient" if retry else "blocked"), ""
    if newest["kind"] == "outcome" and newest.get("class") == "transient":
        return "transient", ""
    if newest["kind"] == "intent":
        return "waiting", ""
    intents = [ts_ms(e["ts"]) for e in ops if e["kind"] == "intent"]
    gaps = [later - earlier for earlier, later in zip(intents, intents[1:], strict=False)]
    limit = max(statistics.median(gaps), QUIET_FLOOR_MS) if gaps else QUIET_FLOOR_MS
    since_last = now_ms - ts_ms(events[-1]["ts"])
    if since_last > limit:
        return "working", f"quiet {max(1, since_last // 60000)}m"
    return "working", ""


def run_closed(events: list[dict]) -> bool:
    """A job run closes with the ok outcome of its run intent; a hook session (`tool:*`)
    stays open until a `session:end` note."""
    first, newest = events[0], events[-1]
    if newest["kind"] == "note" and newest.get("key") == "session:end":
        return True
    is_tool = (first.get("job") or "").startswith("tool:")
    return (
        newest["kind"] == "outcome"
        and newest.get("ref") == first["id"]
        and newest.get("status") == "ok"
        and not is_tool
    )


def group_runs(events: list[dict]) -> dict[str, list[dict]]:
    """Events by `run_id`, runs in order of first appearance, events in the order given."""
    runs: dict[str, list[dict]] = {}
    for event in events:
        runs.setdefault(event["run_id"], []).append(event)
    return runs


def pair(events: list[dict]) -> tuple[dict[str, str], set[str]]:
    """Intent id to the id of the outcome whose `ref` names it, and the unmatched intents."""
    outcomes = {e["ref"]: e["id"] for e in events if e["kind"] == "outcome" and e.get("ref")}
    intents = {e["id"] for e in events if e["kind"] == "intent"}
    return {i: outcomes[i] for i in intents if i in outcomes}, intents - set(outcomes)


def depth(event: dict, by_id: dict[str, dict]) -> int:
    """How many `parent` links lead up from `event` to an event outside `by_id` or a root."""
    level, seen, parent = 0, {event["id"]}, event.get("parent")
    while parent in by_id and parent not in seen:
        seen.add(parent)
        level += 1
        parent = by_id[parent].get("parent")
    return level


def build_view(
    ledger_events: list[dict],
    trace_events: list[dict],
    now_ms: int,
    since: str | None = None,
    limit: int = 50,
) -> dict:
    """What `/api/events` returns: without `since`, the newest `limit` events; with it, the
    oldest `limit` events after it, so successive polls never skip one; in id order (ULIDs
    sort by time), each tagged with its stream, its pairing, its depth, and whether it is
    collapsed (a trace event under a parent); and the state of every run they touch and of
    every run still open, computed over all the events given and at `now_ms`, so a state
    that changes with time alone (quiet) reaches a page polling with an unchanged cursor
    (HANDOFF-0037 review cycle 1 F3)."""
    tagged = [{**e, "stream": "ledger"} for e in ledger_events]
    tagged += [{**e, "stream": "trace"} for e in trace_events]
    tagged.sort(key=lambda e: e["id"])
    by_id = {e["id"]: e for e in tagged}
    pairs, unmatched = pair(tagged)
    # the first page is the newest `limit`; after it, the oldest `limit` past the cursor, so a
    # page polling with its cursor catches up without a gap (review cycle 3 F8)
    after = [e for e in tagged if since is None or e["id"] > since]
    shown = (after[-limit:] if since is None else after[:limit]) if limit > 0 else []
    rows = [
        {
            **e,
            "outcome_id": pairs.get(e["id"]),
            "unmatched": e["id"] in unmatched,
            "depth": depth(e, by_id),
            "collapsed": e["stream"] == "trace" and e.get("parent") in by_id,
        }
        for e in shown
    ]
    runs = group_runs(tagged)
    touched = [e["run_id"] for e in shown]
    still_open = [run_id for run_id, run in runs.items() if not run_closed(run)]
    states = {}
    for run_id in dict.fromkeys(touched + still_open):
        word, quiet = lifecycle(runs[run_id], now_ms)
        first = runs[run_id][0]
        states[run_id] = {
            "word": word,
            "quiet": quiet,
            "closed": run_closed(runs[run_id]),
            "actor": first["actor"],
            "job": first.get("job"),
            "first_ts": first["ts"],
            "last_ts": runs[run_id][-1]["ts"],
        }
    return {"events": rows, "runs": states, "cursor": rows[-1]["id"] if rows else since}
