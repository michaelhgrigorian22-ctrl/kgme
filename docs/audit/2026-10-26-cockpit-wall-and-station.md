---
id: AUDIT-0126
type: report
status: final
handoff: HANDOFF-0058
author: claude-code
source: inferred
sources: ["HANDOFF-0058", "cockpit/index.html", "cockpit/server.py", "tests/test_server.py", "docs/design/cockpit-v0/Wall.dc.html", "docs/design/cockpit-v0/station/index.html", "docs/toolbox.md"]
tier: 2
created: 2026-10-26T01:07:19-07:00
period: 2026-10-26
---

# HANDOFF-0058: the cockpit's wall and station, `w` cycles desk → wall → station

**State: ready, diffs pending.** The code is built, reviewed and committed. The handoff stays open because its last step needs two human-path diffs, and the vendored folder cannot land before them:
- `docs/toolbox.md`, the rows;
- `docs/readers/cockpit.md`.

Without the rows, `kgme lint` blocks every vendored file, as ADR-020 intends. Both diffs and the folder are under `logs/scratch/handoff-0058/` (see "Waiting for Michou").

## What was built
1. **The view cycle** (§1, `cockpit/index.html`). `w` cycles desk → wall → station → desk, and the page remembers the view. All three views draw the one state the page polls: `S.events` and `S.runs` from `/api/events`. No view computes a run state. `w` leaves the deferred group of the keyboard map and joins View. The UNBOUND set keeps only the Phase 2 keys.
2. **The wall** (board 9 at `11b686b`), a second subtree of the same page. Its spec is `logs/scratch/handoff-0058/wall-spec.md`, every item cited to the board.
   - **Layout:** four columns at 2144 px and wider, measured 440 / 978 / 620 / 400 px at 2560 × 1080. Three columns below that, with the payload under the detail. Stacked under 1000 px. There is no horizontal overflow at either size.
   - **Contents:**
     - four hours of events per minute (240 buckets);
     - the runs pane, always open, with 24 px portraits;
     - counts of the events held;
     - the selection band, the timeline, the raw row and the detail.
   - **Shared, not copied:** `drawRows` takes its target. `runsPane` takes `{portraits}`. The bucket loop is one `buckets(minutes)` for the desk's hour and the wall's four hours.
3. **The station** (the canvas at `11b686b`), an `<iframe>` built once from a `<template>` in the same file.
   - **Why an iframe:** its stylesheet and ids (`.hud`, `.row`, `.chip`, `#wall`, `#clock`) are the canvas's and collide with the desk's. Renaming them would have meant rewriting the approved design.
   - **How the block is made:** `logs/scratch/handoff-0058/build_station.py` generates it from the approved file with 40 named, asserted edits (listed in `station-edits.txt`).
   - **The substantive edits:**
     - the canvas's `lifecycle()` and `runClosed()` become lookups into the server's `runs`, so the page decides nothing (`cockpit/render.py` is their port, checked equivalent under HANDOFF-0037);
     - the replay, its clock and its `p` and `r` keys are gone;
     - every `innerHTML` sink becomes nodes and text, so the HANDOFF-0037 page test holds;
     - the cast reads the inlined SVG sources;
     - `c` and `w` go to the page, giving one calm and one cycle;
     - the system facts the replay faked now read "not supplied by /api/events".
   - **Feeding and failure:** the page hands the station each poll. If a module fails to load, the station is hidden, a panel says why, and `w` still returns to the desk.
4. **The route** (§3 and amendment 3, `cockpit/server.py`). `GET /static/vendor/<path>` serves `.js` files only, under `cockpit/static/vendor/`.
   - **Path rules:** every segment must be a plain name, the path is never unquoted, no component may be a symlink, and the file must resolve inside the folder.
   - **Headers:** `no-store` and `nosniff`, as the other routes. Any other path or method is 404.
   - **Tests:** `tests/test_server.py` adds 21 cases: one served file, 19 escapes (`..`, encoded dots, `./`, `//`, a backslash, a file symlink, a folder symlink, a non-module type, folders, a query, the server's own files), and the real folder.
5. **three.js** (§2, amendment 1) is 13 unminified files at 0.182.0:
   - the core pair, whose shas match the rows Cowork pre-recorded;
   - the 11 example modules the approved station imports (CSS2DRenderer, the composer, bloom and output passes, and their imports), found by walking the imports from the CDN.

   The page's import map points `three` and `three/addons/` at `/static/vendor/three-0.182.0/`. Nothing else is loaded.

## Design decisions, each recorded
- **Amendment 1 named two rows; the station needs 13 files.** The canvas imports four addons and the bloom pass's chain. A minified bundle does not qualify (§2), so each module is its own row in the toolbox diff, `held` at its path and hashed. The alternative was dropping the bloom and the HTML labels from an approved design.
- **Every view counts the same runs.** The canvas left Michou's and the guard's runs (its fixed figures) out of its live list, so the station read `21 working · 1 waiting` where the desk read `22 working · 2 waiting` for the same poll. Found in the browser and fixed: the station's live list is exactly the runs the server returns open. Both views now read `22 working (1 quiet) · 2 waiting · 1 transient`.
- **Portraits use the station's actor-prefix table** (`kgme.toml [sprites]` as the canvas draws it, a drawing choice). The wall spec's alternative was every portrait as `stranger`, because `kgme.toml` has no `[sprites]` table and `/api/events` carries no sprite. One table keeps the wall and the station consistent.
- **The wall degrades what `/api/events` does not carry**, as the desk does:
  - payload bytes; the pane shows the event row as returned;
  - this month's count;
  - quotas;
  - this week's review verdicts;
  - strikes;
  - the build order.

  "Today" becomes "held". A minute before the oldest event held is unknown, never zero.
- **The station's `c` still drops to its own text view,** which the canvas calls "the wall". That is not board 9's wall, which `w` reaches.
- **`div.body`:** the desk's `.body` rule is narrowed to the one div it meant, because the cast's SVG groups carry `class="body"`.

## Acceptance
- **The view cycle,** in Chromium (Playwright) over the design's demo ledger, served from a scratch page folder with the vendored files (`logs/scratch/handoff-0058/page/`). `w` cycles desk → wall → station → desk, and focus returns to the timeline.
  - **Desk and station agree:** the station draws the same open runs as the desk, with 26 crew and the room chips' words from the server's runs.
  - **The station draws, nothing more:** it decides nothing. `lifecycle` and `runClosed` read `server[run.id]` only.
  - **Calm and the runs pane:** `c` inside the station sets the page's calm, and `a` lists 25 open runs.
- **The loads:** every script the station loads came from `127.0.0.1:8655/static/vendor/three-0.182.0/`, 13 requests, all 200, and nothing else was requested.
- **The station without the vendor folder** (`page-novendor/`, port 8656): 13 imports 404, the panel reads "The station's renderer stopped: a module it imports did not load.", and `w` returns to the desk.
- **The toolbox check is the acceptance** (amendment 1). In a fresh clone with the vendored folder and both diffs applied (`logs/scratch/handoff-0058/clone/`), `make check` passes: lint 0 blocking with no pending or unheld toolbox finding (the 13 files hash to their rows), and 653 passed. With the folder but without the rows, lint blocks every one of the 13 files (the two core rows are still pending, and a pending row holds nothing).
- **On `main`** (the code, no folder, no diffs), `make check` passes: 653 passed at cycle 1, lint 0 blocking. The two three.js rows stay advisory, pending.
- **A request outside the vendor folder** through the route is 404: `tests/test_server.py`, as above.
- **Screenshots:** `wall-1440.png`, `wall-2560.png`, `station-1440.png`.
- **Safari: not run.** This session drives Chromium only. The Safari re-check of the station as served (amendment 2) is for the morning, once the folder lands. The point to watch is the import map, which the page inserts into the station's document by script; Safari supports import maps from 16.4.

## Review cycle 1 (AUDIT-0127, BLOCK on F1 to F4)
- **F1, ruled advisory by the arbiter on a condition.** HANDOFF-0058 may not close until Michou applies `toolbox.diff` and the 13 vendored files land with it in one commit, and the toolbox check and the served-station check then pass on `main`. The fix F1 asked for, the folder and the rows in this commit, cannot be done inside the boundary.
- **F2, fixed.** The station built crew only from event rows, so an open run whose events all lay outside the poll's window was missing from the deck and the counts, and elapsed ran from the first event held.
  - The station now draws every open run of the server's `runs`, from its actor and `first_ts`, and a run with no event held says so.
  - Red on the cycle-1 page: the station read `22 working … 1 transient` while the desk read `… 1 blocked`. Green after: both read the same (`logs/scratch/handoff-0058/browser-checks.md`).
- **F3, fixed.** The hull decided a halt from the events the page held.
  - It now halts whenever the server calls a run blocked, the same rule as the desk's `halted`. A held halt note only names it, and without one the hull says the note is not held.
  - Red on the cycle-1 page: the hull read `nominal` over a blocked run.
- **F4, fixed.** A symlinked `static/` folder passed the containment check, because both sides resolved through it. The route now refuses it before anything else. Red on the cycle-1 module, green after (`red-c1.txt`, `test_review_c1_f4_a_symlinked_static_folder_serves_nothing`).
- **F5 (transient):** the Safari re-check, as above.

## Review cycle 2 (AUDIT-0128): PASS
- **F1** stays advisory under the arbiter's condition.
- **F5** (Safari) stays transient and open.
- **F6 (cosmetic):** the edit count is corrected to 40.
- The code is committed by pathspec. The handoff stays **open, ready, diffs pending**: it closes when Michou applies `toolbox.diff`, the 13 files land with it in one commit, the toolbox check and the served-station check pass on `main`, and Safari is checked.

## Waiting for Michou
All under `logs/scratch/handoff-0058/`:
1. **`toolbox.diff`** (`docs/toolbox.md`): the two three.js rows lose their pending mark, and 11 rows are added, one per example module, each `held` at its path with its sha.
2. **`cockpit-reader.diff`** (`docs/readers/cockpit.md`): the three views and `w`.
3. **The folder:** `fetched/three-0.182.0/`, copied without its `LICENSE` to `cockpit/static/vendor/three-0.182.0/` and committed with the toolbox diff, so lint never sees one without the other. The command is `rsync -a --exclude LICENSE logs/scratch/handoff-0058/fetched/three-0.182.0 cockpit/static/vendor/`.

Then the Safari re-check, and the handoff closes.

## For the approval screen
- **The station's `c` view keeps the canvas's name, "the wall",** beside board 9's wall. Stakes 2, edge 0.4, score 0.8.
- **Portraits from the station's actor-prefix table, not `kgme.toml`.** Stakes 2, edge 0.3, score 0.6. A `[sprites]` table and an API field would make it the server's.
- **At desk width the 240-bucket chart has columns under a pixel wide.** The spec's alternative is 120 two-minute buckets. Stakes 2, edge 0.3, score 0.6.
