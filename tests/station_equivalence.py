"""The closing check of HANDOFF-0037 (the arbiter's ruling on F2, 2026-10-25): does
`cockpit/render.py`'s lifecycle agree with the station prototype at a given commit?

Purpose: the lifecycle was ported from the station prototype before any `canvas` approval
existed. Before the handoff closes, this runs the prototype's own `lifecycle` and `runClosed`
(its JavaScript, extracted verbatim from `index.html`) and the Python port over the sample
events, everything read at the commit Michou's newest `canvas` approval names: the functions,
the `QUIET_FLOOR` constant they use, and the sample events, whose span sets the clocks (every
30 seconds from the minute of the first event to four quiet floors after the last). It
refuses, rather than passes, when it would prove nothing (review cycle 2 F5): a floor that
differs from `render.QUIET_FLOOR_MS` is a disagreement, and a run with no comparison exits 2.
Zero disagreements is the condition; any difference is followed in `render.py` and in
`tests/test_render.py`'s pinned cases. Not collected by pytest (it needs Node); run by hand:
`uv run --frozen python tests/station_equivalence.py <commit>`.
Inputs: a commit (default `HEAD`); `git`; Node v25.9.0 on PATH, pinned and checked here (ADR-015,
review cycles 2 and 3 F6), installed through nvm under `~/.nvm`.
Outputs: one summary line and the disagreements on stdout; exit 0 when they agree, 1 when
they do not, 2 when the check cannot run or would compare nothing.
Side effects: `git show` reads; `node --version`; one `node` process.
"""

import json
import re
import subprocess
import sys

from cockpit import render

STATION = "docs/design/cockpit-v0/station/index.html"
SAMPLE = "docs/design/cockpit-v0/station/sample-events.jsonl"
STEP_MS = 30_000
TAIL_FLOORS = 4
NODE_VERSION = "v25.9.0"
FLOOR = re.compile(r"\bQUIET_FLOOR\s*=\s*(\d+(?:\s*\*\s*\d+)*)")
RUNNER = """
const QUIET_FLOOR = %d;
%s
const events = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = [];
for (const now of %s) {
  const runs = new Map();
  for (const e of events) {
    if (Date.parse(e.ts) > now) continue;
    if (!runs.has(e.run_id)) runs.set(e.run_id, {events: []});
    runs.get(e.run_id).events.push(e);
  }
  for (const [id, run] of runs) {
    const l = lifecycle(run, now);
    out.push([now, id, l.word, l.quiet, runClosed(run)]);
  }
}
console.log(JSON.stringify(out));
"""


def read_at(commit: str, path: str) -> str:
    """Effect: one file as it is at `commit`."""
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], capture_output=True, text=True, check=True
    ).stdout


def read_node_version() -> str | None:
    """Effect: the version `node` on PATH reports (`v25.9.0`), or None when there is none."""
    try:
        done = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.strip() or None


def extract(html: str, name: str) -> str:
    """Pure: the source of `function <name>(...) { ... }`, braces balanced."""
    start = html.index(f"function {name}(")
    depth, index = 0, html.index("{", start)
    while True:
        depth += {"{": 1, "}": -1}.get(html[index], 0)
        if depth == 0:
            return html[start : index + 1]
        index += 1


def read_floor(html: str) -> int:
    """Pure: the station's `QUIET_FLOOR`, a product of integer literals, in ms; ValueError if
    the file states it otherwise, so a rewritten constant cannot be skipped."""
    found = FLOOR.search(html)
    if not found:
        raise ValueError("the station states no QUIET_FLOOR this check can read")
    value = 1
    for factor in found.group(1).split("*"):
        value *= int(factor)
    return value


def build_clocks(events: list[dict], floor_ms: int) -> list[int]:
    """Pure: every 30 seconds from the minute of the first event to four floors after the
    last, so every run is seen working, waiting, and gone quiet."""
    stamps = sorted(render.ts_ms(e["ts"]) for e in events)
    if not stamps:
        return []
    start = stamps[0] - stamps[0] % 60_000
    end = stamps[-1] + TAIL_FLOORS * floor_ms
    return list(range(start, end + 1, STEP_MS))


def run_station(html: str, floor_ms: int, events: list[dict], clocks: list[int]) -> list[list]:
    """Effect: the prototype's answers, from Node."""
    functions = extract(html, "lifecycle") + "\n" + extract(html, "runClosed")
    script = RUNNER % (floor_ms, functions, json.dumps(clocks))
    done = subprocess.run(
        ["node", "-e", script], input=json.dumps(events), capture_output=True, text=True,
        check=True,
    )  # fmt: skip
    return json.loads(done.stdout)


def compare(answers: list[list], events: list[dict]) -> list[tuple]:
    """Pure: every (clock, run) where the port's word, quiet note or closing differs."""
    differences = []
    for now, run_id, word, quiet, closed in answers:
        seen = [e for e in events if e["run_id"] == run_id and render.ts_ms(e["ts"]) <= now]
        ours = (*render.lifecycle(seen, now), render.run_closed(seen))
        if ours != (word, quiet, closed):
            differences.append((now, run_id, (word, quiet, closed), ours))
    return differences


def main(argv: list[str]) -> int:
    version = read_node_version()
    if version != NODE_VERSION:
        print(f"station check: needs Node {NODE_VERSION}, found {version}; not run")
        return 2
    commit = argv[0] if argv else "HEAD"
    resolved = subprocess.run(
        ["git", "rev-parse", commit], capture_output=True, text=True, check=True
    ).stdout.strip()
    html = read_at(resolved, STATION)
    events = [json.loads(line) for line in read_at(resolved, SAMPLE).splitlines() if line.strip()]
    floor = read_floor(html)
    differences: list[tuple] = []
    if floor != render.QUIET_FLOOR_MS:
        differences.append(("QUIET_FLOOR", floor, render.QUIET_FLOOR_MS))
    clocks = build_clocks(events, floor)
    answers = run_station(html, floor, events, clocks) if clocks else []
    if not answers:
        print(f"station at {resolved}: 0 comparisons; nothing proved, refused")
        return 2
    differences += compare(answers, events)
    print(
        f"station at {resolved}: floor {floor} ms, {len(clocks)} clocks, "
        f"{len(answers)} comparisons, {len(differences)} disagreements"
    )
    for difference in differences:
        print(difference)
    return 1 if differences else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
