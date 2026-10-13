---
id: CDH-0009
type: handoff
created: 2026-10-13T13:25:00-07:00
from: michou
to: cowork
tier: 2
status: open
adopted_by: michou
adopted: 2026-10-13T15:54:00-07:00
depends_on: [CDH-0007]
design_track: HANDOFF-0036
---

# CDH-0009: The station — the ship, its rooms and the crew at work, for the wall

## Why

Michou, 2026-10-13 13:17, on a reel of an isometric "spaceship" whose rooms are a bot's pipeline stages and whose crew walk between them (recording under `logs/scratch/design-review/references/station-reel-*.jpg`, the interaction pattern only, never the look or the subject): "the UI is just perfect … that little room made a little darker and more on theme with KGME would be SUCH a cool extra touch." The cockpit's rule holds for the desk views: signal in the centre, noise at the edges, nothing shown only by portrait or colour. The wall (board 9) is where the cockpit is allowed to be a mood: it sits on the external monitor, nobody operates it, and it is read from across a room. A ship view belongs there, as a second wall layout, with the facts kept in text exactly as the tray keeps them.

The cast already exists (board 10) and already has one mode per lifecycle word (CDH-0007). The station gives each actor a room and lets the ledger move them.

## The design, to draw

1. **The ship.** One deck in isometric projection (orthographic camera, the classic 2:1 angle), drawn dark: ground `#0a0c10`, hull and walls `#11151c`, every wall edge a 1 px cyan line, floor grid `#1e2a33`, the scanline overlay of board 3 over the whole frame, a starfield behind the hull. Rooms, each a KGME place, labelled in the HUD type (9 px caps, tracked) with the tray's words beside the name:
   - **Bridge** — Michou's chair; the clock, the frame state, the usage bars on the wall. `you` sits here (the michou actor), asleep when no `approval` or human `note` has landed in an hour.
   - **Workshop** — one desk per open `claude-code.*` run; the builder at a desk is `working`, standing beside it `waiting`, sagging `transient`. A second builder for a second session.
   - **Review chamber** — `kgme.review`'s bench, the three strike boxes on the wall as on board 4; the arbiter's seat behind it, empty until a `ruling:` note.
   - **Airlock** — `kgme.guard` at the door; a refusal is a magenta flash on the door frame and the guard braces.
   - **Archive** — `kgme.*` (sync, clean, brief, ledger) with the ledger as a vault; a push on commit is the scribe carrying a book to the vault.
   - **Dock** — where shells arrive: Codex, a terminal worker, any actor the sprite mapping does not know (the stranger), each with its own berth while its run is open.
   - **Engine room** — the router and the local model (`ollama idle` on board 9's header): a reactor that dims when idle. Phase 2, dashed, inactive, as board 8 draws its controls.
2. **The crew.** The chibi cast, not a new set of characters: each actor is its canonical SVG mounted as a billboard in the scene (the `CSS3DRenderer` places the live `<svg><use>` element in 3D, so board 10's mode CSS and motion keep working; no texture, no model, no binary). 72 px full figure in the scene; the 24 px portrait on the room chip. Mode mirrors the lifecycle word as the tray does. Movement is a straight walk between a run's room and the dock when a run opens or closes, 600 ms, nothing else: the crew do not wander.
3. **The words.** The tray's bar (CDH-0007) sits in the HUD strip at the top, unchanged. Each room's chip carries its lifecycle word and count (`WORKSHOP · 2 working · 1 quiet`, `REVIEW CHAMBER · transient · retry 23:06`, `AIRLOCK · 1 refused`). A speech bubble over an actor is that run's newest event summary with its class chip, exactly the tray row's last column, and fades after 20 s so a stale bubble never reads as live. Click a room, or press `1`–`7`, to follow it: the camera eases to it and the timeline on the right of the wall filters to its runs (`r`); `Esc` returns.
4. **Light carries state only as the frame does today:** the whole hull cyan while the ledger is live; a magenta flood from the room that holds a `blocking` outcome or a halt; amber from a room with an intent waiting; grey static over everything when the server is unreachable, crew frozen in their last pose with `stale` in text. Bloom is one post-processing pass with a low threshold so only the edge lines and the class lights glow. Reduced motion: no bloom, no walk, no fade. Calm (`c`): the station is decoration, so calm leaves it for the four-column wall (board 9) — the same keystroke, the same facts.
5. **Boards to change:** 9 (a second layout, `w` cycles desk → wall → station), 7 (`1`–`7` follow a room in station view; `w`'s row says so), 1 (the room palette and the light rule as a row). Board 10 unchanged.
6. **Not in this handoff:** any Phase 2 control; a mini-map; sound; letting the crew wander; any asset that is a binary. The station is read-only like the rest of v0.

## Do

This is not a canvas artboard: a rendered 3D scene is script-built, which the editor's format forbids. Draw it as one self-contained page under `docs/design/cockpit-v0/station/index.html` on branch `design`: inline CSS and script, three.js pinned by version from `cdnjs.cloudflare.com` through an import map (the prototype may load that one remote script; the cockpit itself may not, see HANDOFF-0044), sample events from `station/sample-events.json` in ADR-019 event v1 shape (board 3's rows and the tray samples), the cast read from `../chibi/*.svg` by `fetch` as the fixture does. Publish it as its own private review artifact for Michou to look at and move around in; record a 30-second capture of it under `logs/scratch/design-review/cdh-0009/`. Commit by pathspec with message `design: the station, isometric wall view (CDH-0009)`, write `docs/audit/cockpit-design/cdh-0009-implementation.md`, and queue CDH-0010, Codex's read-only review, in the README.

## Acceptance

From across the room, Michou can tell from the station alone whether anything is blocked (one room is magenta and its chip says so) and who is working; up close, every fact the station shows is also a word or a number in a chip or the HUD; `c` drops to the wall with nothing lost; the page loads nothing but the one pinned script and the repository's own files. Visual acceptance is Michou's.
