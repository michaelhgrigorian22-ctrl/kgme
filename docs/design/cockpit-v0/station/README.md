# The station (CDH-0009)

A second wall layout: the ship, its rooms and the crew at work, drawn dark and on theme. Not a canvas artboard (a rendered scene is script-built, which the `.dc.html` editor forbids): one hand-built page.

- `index.html` — the page. Serve `docs/design/cockpit-v0/` over HTTP (`python3 -m http.server 8080` from that folder) and open `/station/`. It reads the cast from `../chibi/*.svg` at load and replays `sample-events.jsonl` at ×20, looping.
- `sample-events.jsonl` — 40 ledger lines in ADR-019 event v1 shape, one JSON object per line, derived from the samples boards 3, 5 and 11 carry (2026-10-08, 19:40 to 19:52). Ids are ULID-shaped; raw bodies never appear.
- The only remote script is `three@0.182.0` from jsDelivr through an import map (`three.module.min.js` and `examples/jsm/`), pinned. The cockpit itself may load nothing remote (ADR-017); HANDOFF-0044 proposes vendoring the module as plain text under `cockpit/static/vendor/` when the station leaves the design track.
- Rooms are KGME places: Bridge (you), Workshop (`claude-code.*`), Review chamber (`kgme.review`, `arbiter.*`), Airlock (`kgme.guard`), Archive (`kgme.*`), Dock (shells, the stranger), Engine room (phase 2, dashed). The sprite mapping is a copy of `kgme.toml [sprites]`, first match wins.
- Words first: the tray bar in the HUD, a chip per room with its lifecycle words, a bubble per newest event with its class chip; light in a room mirrors the chip and never replaces it. Keys: `1`–`7` follow a room, `Esc` the whole deck, `a` the runs pane, `c` calm (drops to the wall, plain text), `r` restarts the replay. Reduced motion removes bloom, walks and fades.
- Lifecycle words, as on board 11: working · waiting (an intent with no outcome) · transient (the newest outcome is transient, or an exhausted retry that names a time) · blocked (a blocking outcome or note with nothing after it) · quiet (a working run with no event for longer than three times its median gap between intents, at least three minutes). A job run closes with the outcome of its run intent; a hook session stays open until a `session:end` note.

Review copy: the private artifact "KGME Station" (Cowork's), republished from this folder.
