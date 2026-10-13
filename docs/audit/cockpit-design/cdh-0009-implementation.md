---
id: AUDIT-CDH-0009
type: report
created: 2026-10-13T16:35:00-07:00
author: cowork
source: inferred
sources:
  - CDH-0009
  - docs/design/cockpit-v0/station/ at 373de74
  - docs/design/cockpit-v0/chibi/*.svg at 373de74
  - logs/scratch/design-review/cdh-0009/
  - logs/scratch/design-review/references/station-reel-*.jpg
tier: 2
status: final
handoff: CDH-0009
period: "2026-10-13"
reviewed_sha: 373de74
review_canvas: "private artifact KGME Station https://claude.ai/artifact/HgsBCZ7fbFcZzFPVod6pWf, version 2 (1791933817-e6f5)"
---

### Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| CW14 | advisory | the artifact host | The published page stays blank for 20–50 s in the browser pane before its first paint: the host shows the page only once `load` fires, and `load` waits for the Google Fonts stylesheet and the three.js module from jsDelivr. The page itself runs meanwhile (its replay clock had advanced when it appeared). Served from the repository over HTTP it paints at once. | None in the page; the cockpit build will vendor three.js (HANDOFF-0044) and serve the font locally, so the real station has no remote wait. Noted for Michou so a blank first half-minute does not read as a failure. |
| CW15 | advisory | `station/index.html` (replay) | The first published version did not loop in the pane: the clock passed the sample's end without resetting, though it reset in headless Chromium. Rewritten before commit to reset on a precomputed `loopEnd` regardless of the cursor, with a `replay N` counter in the ledger line; version 2 observed looping (`replay 2`). The cause was not isolated; the guard removes the dependency on the cursor comparison. | Done before commit. |
| CW16 | cosmetic | `station/index.html` (bubbles) | Event bubbles can cover a room's chip for the seconds they are shown (7 s real), since chips sit at a room's back edge and bubbles rise from the crew in front of them. The chip's words return when the bubble fades; nothing is shown only in the bubble. | Accept, or move chips to the room's front edge; Michou's call. |

### Verdict

PASS

### Notes

**Delivered** on branch `design` as `373de74` (`design: the station, isometric wall view (CDH-0009)`). Files:

| Path | SHA-256 |
|---|---|
| `docs/design/cockpit-v0/station/index.html` | `937196d6767571f1b7ee07de448c2c12558f95dbf7e024773d08104086d8f4bb` |
| `docs/design/cockpit-v0/station/sample-events.jsonl` | `3739357052b0e144ed7aea1612ebf31057f8f3f35178341a1cdf3038589f4644` |
| `docs/design/cockpit-v0/station/README.md` | `1734602fc0cff126363213ea39d4dc37a3643954847a2c04fb6aa54124ffb1d2` |

`tests/test_design_sprites.py`: 30 passed (unchanged; the station reads the canonical SVGs at load and copies nothing). `kgme lint`: 0 blocking. No binary committed; the only remote script is `three@0.182.0` (`three.module.min.js` and `examples/jsm/` addons) from jsDelivr through an import map, pinned.

**What was drawn.** One hand-built page, not a canvas artboard (a rendered scene is script-built, which the `.dc.html` editor forbids; the handoff said so). The same body is the private review artifact "KGME Station"; the repository file wraps it in a document so `python3 -m http.server` from `docs/design/cockpit-v0/` serves it at `/station/`.

- *The ship.* An isometric deck (orthographic camera at 30° elevation, 45° azimuth) on a chamfered hull with a bow to the right, drawn in the cockpit's phosphor palette: ground `#0a0c10`, hull `#0d1117`, floors `#161d26`, walls `#141b22`, every edge a 1 px cyan line, a floor grid in `#1e2a33`, a starfield, board 3's scanlines and vignette and frame over it all. One bloom pass with a low threshold so only the edge lines and the state lights glow. Seven rooms, each a KGME place with its own chip: **Bridge** (you; the michou actor sits asleep in chalk until a human `note` or `approval` lands, then works for a moment), **Workshop** (one desk per `claude-code.*` run), **Review chamber** (`kgme.review`; the arbiter's seat fills when an `arbiter.*` note arrives), **Airlock** (`kgme.guard`, always present; a `refused` outcome lights the door magenta and the guard braces), **Archive** (`kgme.*`; the sync run walks in, pushes, walks out), **Dock** (shells and any actor the mapping does not know, as the stranger: the sample's `codex.exec` thread), **Engine room** (router and Ollama; phase 2, dashed, inactive).
- *The crew.* The chibi cast itself: each actor's canonical SVG is fetched from `../chibi/` at load and mounted as a `<symbol>`, then placed in the scene as an HTML billboard (`CSS2DRenderer`), 72 px at zoom 1 and scaling with the camera. The phosphor palette, the mode CSS and the `data-portrait` crops are board 10's, read from the files; the sticker palette is not used. Modes mirror the lifecycle word (working, waiting, transient, blocked; a quiet run waits). Movement is one 600 ms walk from the dock gate to a seat when a run opens and back when it closes; nothing wanders; no `is-animated` class is set, so the station adds no sprite animation of its own.
- *The words.* The tray bar (`ACTIVE RUNS · a`, stacked 24 px portraits, the summary in the F5 form `2 working (1 quiet) · 1 transient`) sits in the HUD with the clock, the ledger line (`live · 40 events · 6 runs · replay N`), session, harnesses and `following`. Each room's chip is a real button carrying the room's number, name and lifecycle words (`2 working (1 quiet)`, `1 transient`, `guarded · nothing pending`, `you · asleep`, `empty`, `phase 2 · inactive`). A bubble over an actor is that run's newest event, with its time and ADR-016 class chip (`ok`, `refused`, `blocking`, `transient`, `—`), shown 7 s. The pane (`a`, or a followed room) lists rows in the tray's two-line shape, as buttons, with the F1 contrast fix already applied to the focused row. Calm (`c`) drops to the wall: a plain-text page of the seven rooms and their rows, portraits hidden, every fact kept.
- *Light carries the words and nothing else.* A room's point light is cyan while it holds working runs, amber for waiting or transient, magenta for blocked, off when empty; the hull's edge lines go magenta only on a `halt:` note; grey static is left to board 6's treatment and is not in the sample.
- *Keys and pointer.* `1`–`7` follow a room (camera eases to it, zoom 1.9, the pane lists its runs), `Esc` the whole deck, `a` the runs pane, `c` calm, `r` restarts the replay; drag pans, the wheel zooms, a chip click follows. These are the page's own handlers, a drawing of the cockpit's; HANDOFF-0037's successor binds the real ones.
- *The sample.* `sample-events.jsonl`: 40 ADR-019 event v1 lines, one per line, every field present, ULID-shaped monotonic ids, payload refs for tool pairs and no bodies, derived from the samples boards 3, 5 and 11 carry: the builder's session (hook pairs, the guard's refusal, the commit), the sync run it opens (walks to the vault and closes), the review run (three transient attempts, exhaustion with a retry time), a second builder session that goes quiet, a Codex thread at the dock (opens, lints, tests, closes), the arbiter's ruling, Michou's note, the builder's resumed edits and the `make canary-agents` intent that waits. Replayed at ×20 from 19:40:00 and looping four minutes after the last line.
- *Lifecycle, as code.* A run's word comes from its newest intent or outcome: a blocking note anywhere halts it; a blocking outcome that names a retry time is transient; a blocking outcome is blocked; a transient outcome is transient; an intent with no outcome is waiting; otherwise working, and quiet when no event has come for longer than three times the run's median gap between intents (at least three minutes). A job run closes with the outcome of its run intent; a hook session stays open until a `session:end` note. This is the proposal for `render.py`; it refines board 11's prose (CDH-0008 F4 asked for the retry exception) and is written in the station README.
- *Reduced motion* removes bloom, the walks and the bubble fades. *Phone width:* the HUD stacks, the micro labels hide, no horizontal scroll (measured: 400 px scroll width at 400 px).

**Observed natively** (the published artifact in the browser pane, 800 × 1073): version 1 at 19:48 and 20:04 of the replay, the deck with crew in four rooms, chips and bubbles, the tray bar reading `2 working (1 quiet) · 1 waiting · 1 transient`, the guard braced with the refusal bubble, Michou on the bridge with his note; version 2 at 19:54 and, after the loop, the ledger line reading `0 events · 0 runs · replay 2` at 19:40:00. Loading from jsDelivr and the sibling files works inside the artifact's frame. Not observed in the pane: keys (the frame did not take focus from the pane's click), reduced motion, the wall at 2560.

**Observed standalone** (headless Chromium 1194 with SwiftShader, from the repository files served locally with the vendored three.js, labelled `standalone-`): the deck at 2560 × 1080 through the replay, following the Workshop at zoom 1.9 with its pane, calm dropping to the wall, the desk at 1440 × 900, the phone at 400 × 800, and a 30-second recording. Standalone evidence shows the design; the native captures show it runs where Michou will look.

**Evidence** under `logs/scratch/design-review/cdh-0009/` (hashes taken on the Mac after delivery):

| File | SHA-256 |
|---|---|
| `native-artifact-v1-pane-800px-19-48.jpg` | `1908984cad39b62b78c2226420b7e40c841f91e613f2a43a2731ae1323393498` |
| `native-artifact-v1-pane-20-04.jpg` | `7d85ada725556c9f558ba4da359f172ee06512cdbbaaec3e2818fb70ae17c438` |
| `native-artifact-v2-pane-19-54.jpg` | `9fbecb820ef19698ed803a208cd1b0b5cd6490e304f3eae4cdf7bc9e6c7bd0cb` |
| `native-artifact-v2-hud-replay-2.png` | `f21b7cb1128976eabae8dbfff77557a75a7cac6b53adf8414b6aa639c87f0a9d` |
| `standalone-wall-2560x1080.png` | `9e15bf47b68350ae86c7d878e958ec3074363f78bbb9c4264b84c96fcac4a237` |
| `standalone-follow-workshop-2560x1080.png` | `c6a43fadccb64bd32590db4cbc3d78fa143fde9de7d6145bc0d7f91be4c3a66f` |
| `standalone-calm-wall-2560x1080.png` | `1c234abac7144b4ff704f45a317ba0207b8be79b1b66e314b60f808ae6b3aedc` |
| `standalone-desk-1440x900.png` | `c89212855d96ae2b7fbe507a8a5e8c503527eeef74b2abea856dd8557d34a581` |
| `standalone-phone-400x800.png` | `fd6039e239a437862fdda98f9190eaa4849a02fd5707337c32e170312a8fa826` |
| `standalone-station-30s-1920x1080.webm` | `c3606c1ac7083e67f8f3c4b858553a53e7d45f06fa8379eebc5dd718d291c78b` |

Three reference frames from the reel Michou sent (`references/station-reel-*.jpg`) were used for the interaction pattern only: rooms as places, a crew that moves on events, a chip per room, a bubble per event, click a room to follow it. Nothing of the look or subject was reproduced.

**Not in this handoff, as written:** boards 7 and 9 were not changed (the `w` cycle and board 7's `1`–`7` rows wait for Michou's visual acceptance of the station, since a board change for a layout he may redraw is churn); board 1 gains nothing yet. Open for Michou: the look as a whole (a first pass); whether the crew should be larger than 72 px on the wall; whether a run's bubble should stay until the next event instead of fading; CW16; and whether the station replaces or joins board 9's four-column wall when the cockpit is built.

**Next:** CDH-0011, Codex's read-only review of `373de74`, proposed and `ready` in the Codex queue after CDH-0010 (the tray's fix cycle for AUDIT-CDH-0008). This report is not Michou's design approval.
