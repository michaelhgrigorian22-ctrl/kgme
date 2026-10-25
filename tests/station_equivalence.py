"""The closing check of HANDOFF-0037 (the arbiter's ruling on F2, 2026-10-25): does
`cockpit/render.py`'s lifecycle agree with the station prototype at a given commit?

Purpose: the lifecycle was ported from the station prototype before any `canvas` approval
existed, so it is provisional. Before the handoff closes, this runs the prototype's own
`lifecycle` and `runClosed` (its JavaScript, extracted verbatim from `index.html`) and the
Python port over the sample events, both read at the commit Michou's newest `canvas`
approval names, at 51 clocks from 19:40 to 20:05, and prints the commit, the number of
comparisons, and every disagreement. Zero disagreements is the condition; any difference is
followed in `render.py` and in `tests/test_render.py`'s pinned cases. Not collected by pytest
(it needs Node); run by hand: `uv run --frozen python tests/station_equivalence.py <commit>`.
Inputs: a commit (default `HEAD`); `git`; `node` on PATH.
Outputs: one summary line and the disagreements on stdout; exit 0 when they agree, 1 if not.
Side effects: `git show` reads; one `node` process.
"""

import json
import subprocess
import sys

from cockpit import render

STATION = "docs/design/cockpit-v0/station/index.html"
SAMPLE = "docs/design/cockpit-v0/station/sample-events.jsonl"
START = "2026-10-08T19:40:00.000-07:00"
CLOCKS = 51
STEP_MS = 30_000
RUNNER = """
const QUIET_FLOOR = 3 * 60 * 1000;
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


def extract(html: str, name: str) -> str:
    """Pure: the source of `function <name>(...) { ... }`, braces balanced."""
    start = html.index(f"function {name}(")
    depth, index = 0, html.index("{", start)
    while True:
        depth += {"{": 1, "}": -1}.get(html[index], 0)
        if depth == 0:
            return html[start : index + 1]
        index += 1


def run_station(html: str, events: list[dict], clocks: list[int]) -> list[list]:
    """Effect: the prototype's answers, from Node."""
    functions = extract(html, "lifecycle") + "\n" + extract(html, "runClosed")
    script = RUNNER % (functions, json.dumps(clocks))
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
    commit = argv[0] if argv else "HEAD"
    resolved = subprocess.run(
        ["git", "rev-parse", commit], capture_output=True, text=True, check=True
    ).stdout.strip()
    events = [json.loads(line) for line in read_at(resolved, SAMPLE).splitlines() if line.strip()]
    start = render.ts_ms(START)
    clocks = [start + k * STEP_MS for k in range(CLOCKS)]
    answers = run_station(read_at(resolved, STATION), events, clocks)
    differences = compare(answers, events)
    print(f"station at {resolved}: {len(answers)} comparisons, {len(differences)} disagreements")
    for difference in differences:
        print(difference)
    return 1 if differences else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
