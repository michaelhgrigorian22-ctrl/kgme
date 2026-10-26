---
id: HANDOFF-0058
type: handoff
created: 2026-10-25T22:46:44-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0037, HANDOFF-0044]
plan_ref: PLAN-PHASE-1 step 10b
---

# Handoff 0058 (proposed) — The cockpit's wall and station: `w` cycles desk → wall → station, from the approved canvas, with three.js vendored through the toolbox

## Why
The canvas Michou approved at `11b686b` binds `w` to desk → wall → station (board 9's wall, the orbital station of CDH-0019 and after). HANDOFF-0037 is the read-only timeline, four routes, no remote asset, and the station's renderer is three.js, which only HANDOFF-0044's toolbox lets into the tree. Review cycle 3 of 0037 found the gap (F11); the arbiter held it outside the mandate and Michou ruled on 2026-10-25: 0037 ships `w` unbound and labelled deferred, and the wall and the station come as this handoff, after 0044.

## What
1. **The wall and the station** as approved: the page gains the wall view and the station view at the commit the newest `canvas` approval names; `w` cycles desk → wall → station and back; the station's lifecycle stays the server's (`cockpit/render.py`), the page only draws it, as 0037's amendment of 2026-10-21 requires.
2. **three.js by the toolbox rule (ADR-020).** The unminified module at the station's pinned version (0.182.0 in the design canvas today) is vendored as plain text under `cockpit/static/vendor/` with its row in `docs/toolbox.md` (source, licence, sha256), and the server gains one route for that folder, read-only, same headers as the rest. A minified file is a bundle and does not qualify. No other remote asset: the station's textures and sprites are committed or fetched by `make assets` per their rows.
3. **Routes.** `GET /static/<file>` for vendored files only; every other path stays 404. The LAN refusal, `no-store` and `nosniff` hold.
4. **The keyboard map** drops the "deferred" label; `docs/readers/cockpit.md` gains the two views.

## Outputs
`cockpit/index.html`, `cockpit/server.py`, `cockpit/static/vendor/` (new), `docs/toolbox.md` (one row), `tests/test_server.py`, a page check for the three views, `docs/readers/cockpit.md` (human path: a diff).

## Acceptance test (under ten minutes)
With `kgme cockpit` running: `w` cycles desk → wall → station → desk; the station draws the runs `/api/events` returns and decides nothing itself; every script the page loads is served from `127.0.0.1:8642/static/` and its sha matches its toolbox row (`kgme lint` green); a request for a file outside `cockpit/static/vendor/` through that route is 404; the station is checked in Safari as well as Chrome (CDH-0030's check, if it has not run by then, runs here).

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one page, one route, one vendored folder, one toolbox row. `git revert`.

## Needs from Michou
Adoption after HANDOFF-0044 is done and HANDOFF-0037 closed. If the canvas has moved on by then, a new `canvas` approval first; the page is built from the newest one.
