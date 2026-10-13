---
id: CDH-0007
type: handoff
created: 2026-10-12T17:40:00-07:00
from: michou
to: cowork
tier: 2
status: open
adopted_by: michou
adopted: 2026-10-13T11:58:00-07:00
depends_on: [CDH-0006]
design_track: HANDOFF-0036
---

# CDH-0007: The active-runs tray — the cast at work on the main boards

## Why

Michou, 2026-10-12 17:35, on a subagent tray he saw elsewhere (references in `logs/scratch/design-review/references/chatgpt-subagents-*.png`, interaction pattern only, never the look): "something like this also included on the main working pages when agents and shells from the multiple models with their icons for working type would be a great way of adding just that additional bit of display beyond the more dedicated agent frames." The cockpit already has the parts: 24 px head-crop portraits in run headers, one mode per lifecycle state, and a frame that carries system state. What is missing is the compact, always-visible summary of who is working right now, on the boards where the timeline is.

## The design, to draw

1. **Tray, collapsed.** One row in the top bar of boards 3, 4, 5 and 6 (and a column slot on board 9's wall): the 24 px phosphor portrait of every actor with an open run, overlapping slightly like a stack, then the text `3 working · 1 waiting` in the bar's type. The text is the signal; the portraits are decoration that mirrors it (one rule: noise never carries information). Each portrait's mode class mirrors that run's lifecycle word exactly as the run header does — working, waiting, transient, blocked. No tray when nothing is open: the slot reads `idle` in muted text and no portraits.
2. **Tray, expanded.** Key `a` (free on the map) opens it as a pane in the detail column, the way `o` opens open intents: one row per open run — portrait · actor (mapping name) · run id, short · the lifecycle word · elapsed since the run's first event, live · the run's latest event summary, ellipsised. `j`/`k` move, `Enter` jumps to that run in the timeline (`r` filter), `Esc` closes. A shell (Codex, Claude Code, a terminal worker) is an actor like any other: the mapping in `kgme.toml [sprites]` decides its face, the stranger until it is given one.
3. **States the tray must show in text, never only by portrait:** blocked (the row's class chip, magenta, and the frame flood as today), transient (amber chip), a run that has gone quiet (no event for longer than its median gap: `quiet 4m` in muted text, portrait in `waiting`), and halt (strike boxes as today). Calm hides every portrait and leaves the words; reduced motion freezes them; the tray adds no animation of its own — only the selected detail animates, as board 10 rules.
4. **Boards to change:** 1 (the tray as a component: collapsed, expanded row anatomy, the quiet state), 3 (tray in the top bar with three sample runs), 4 (tray with one blocked run and the halt), 5 (one waiting on an intent), 6 (tray greyed under disconnection with its last known state and `stale` in text), 7 (`a` added to the map, bound, with `o`'s wording), 9 (the wall's tray column). Board 10 unchanged. Samples are real event shapes from `logs/ledger`.
5. **Also, from AUDIT-CDH-0005 F2 (cosmetic):** in `docs/design/cockpit-v0/chibi/README.md`, the two opening references that still assign native verification to CDH-0002 and the three mode-table entries still reading `no outcome` are brought in line with the rendered board (`Class: —`, verified under CDH-0004/0006). Wording only.
6. **Not in this handoff:** any Phase 2 control (dispatch, approve, model choice) inside the tray; those stay dashed on board 8. The tray is read-only like the rest of v0.

## Do

Draw it in `docs/design/cockpit-v0/` on branch `design` in the worktree, native markup only (symbols reused from board 10 by copying the needed head-crop `<symbol>`s; the drift test extends to cover them), `{…}` holes, no iframe, no script-built UI. Commit by pathspec with message `design: active-runs tray, key a (CDH-0007)`, republish the review copy, observe natively, write `docs/audit/cockpit-design/cdh-0007-implementation.md`, then hand Michou the Codex review box. Captures to `logs/scratch/design-review/cdh-0007/`; no binaries under `docs/` or `memory/`.

## Acceptance

Michou can read, within ten seconds and without the keyboard map, who is working, who is waiting and who is blocked on board 3, and can open the tray with `a` and reach a run from it. Codex's read-only review finds no fact shown only by portrait or colour. Visual acceptance is Michou's.
