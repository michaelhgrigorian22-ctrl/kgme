---
id: READER-COCKPIT
type: note
status: active
created: 2026-10-25T18:40:00-07:00
modified: 2026-10-26T01:00:09-07:00
author: claude-code
source: inferred
sources: ["HANDOFF-0037", "HANDOFF-0058", "ADR-017", "ADR-020", "cockpit/server.py", "cockpit/render.py", "cockpit/index.html", "docs/readers/cockpit-design.md"]
tier: 2
---

# Reader: the cockpit

*Written 2026-10-25 by Claude Code for HANDOFF-0037; the wall and the station added 2026-10-26 for HANDOFF-0058. The decision is ADR-017; the design is the canvas Michou approved at `11b686b`.*

## What it is
A read-only timeline over the ledger, served by your own machine. It shows every event the hooks and jobs write, grouped by run, and the state each run is in. It never writes anything, launches anything, or connects anywhere: it listens on `127.0.0.1:8642` (`kgme.toml [cockpit]`, loopback only) and reads `logs/ledger/` and `logs/trace/`.

## How to start it
Run `kgme cockpit` from the repository and open `http://127.0.0.1:8642/`. It serves until you press Ctrl-C. The Dock icon does not start the server: launchd waits for Phase 3, so start it by hand first.

## Installing to the Dock
- **Chrome:** with the page open, choose "Install page as app" (or Cast, Save and Share → Install page as app). The icon opens the page in its own window while the server runs.
- **Safari:** File → Add to Dock.

## Reading the timeline
- **Rows:** time, kind (`▶` intent, `◀` outcome, `✎` note, `✓` approval), job, summary, class, and Δt, the time from an intent to its outcome. Rows are grouped by run; the group header carries the run's actor, job, start, event count and state.
- **Run states** come from the server and are never decided by the page: working, waiting (an intent has no outcome yet), transient (a retry is scheduled), blocked (a blocking outcome or note stopped the run), and quiet within working (no event for longer than the run's median gap between intents, never under three minutes).
- **The frame carries the system's state:** cyan while live, magenta flood when a run is blocked (the ledger line reads `halted`), an amber strip while an intent waits for its outcome, and grey static when the server cannot be reached. Disconnected never hides the record: a band under the header says so, and the last snapshot stays readable.
- **Read-only trace events** (Read, Grep and the like) are collapsed under their parent; `t` expands them.

## Three views of one state: `w`
`w` cycles desk → wall → station → desk, and the page remembers the last one. All three draw the same poll of `/api/events` and the same run states; none decides one.
- **The desk** is the timeline above.
- **The wall** (board 9) is for an external monitor, four columns from 2144 px wide (three below, stacked under 1000):
  - four hours of events per minute, with a minute before the oldest event held marked unknown, never zero;
  - the runs pane, always open, with portraits;
  - counts of the events held, by kind and class;
  - the selected event's context, the timeline, the event row as the server returned it (the payload's bytes are not served), and its detail.
- **The station** is the orbital deck of the approved canvas, drawn with three.js: rooms are KGME places, each open run a crew member in its room, and the hull turns magenta while a run is halted. Its own keys:
  - `1`–`7` follow a room;
  - `Esc` the whole deck;
  - `a` the runs and system pane;
  - `c` calm, which drops the deck to the same facts as text;
  - `w` back to the desk.

  three.js is served from `127.0.0.1:8642/static/vendor/`, each file with its row and sha in `docs/toolbox.md`. If a file is missing, the station says it did not load and `w` still returns to the desk.

## Keys
`j` `k` move, `g` `G` oldest and newest, `Enter` detail, `Esc` back, `u` parent, `f` follow, `/` filter (`run:`, `kind:`, `job:` or text), `1`–`4` class, `0` all classes, `r` this run (or retry while disconnected), `t` trace, `o` open intents, `a` runs pane, `x` clear, `c` calm, `p` payload path, `w` the next view, `?` the full map and the system facts. Dashed keys are Phase 2: reserved, not bound. No key acts while you type in the filter line, except Enter and Esc.

## What it does not show yet
Strike counts, the open handoff, the last review and the system facts (session, quotas, latency) are not in `/api/events`; the page names them and prints `not supplied by /api/events` rather than guessing.
