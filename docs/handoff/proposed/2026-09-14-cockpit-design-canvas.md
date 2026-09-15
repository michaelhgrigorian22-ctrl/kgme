---
id: HANDOFF-0036
type: handoff
created: 2026-09-14T22:25:00-07:00
from: claude-code
to: cowork
tier: 2
status: proposed
depends_on: null
plan_ref: PLAN-PHASE-1 step 11 (parallel track)
---

# Handoff 0036 (proposed, for Cowork and Michou) — The cockpit design canvas

## Why
ADR-017 and the roadmap: design is taste, not code, can start any time, and must be approved by Michou before any cockpit code. AUDIT-0011 removed it from the numbered order so it never gates or is gated. It opens on day one of Phase 1 and must be approved before HANDOFF-0037 is adopted.

## What
1. A design canvas from `memory/notes/cockpit-wishlist.md`: cyberpunk, keyboard-first, legible at 2 a.m. v0 shows one screen, the ledger timeline, in five states: empty, live with events arriving, a `blocking` outcome, an unmatched intent (reconciliation pending), server disconnected.
2. Specified in the canvas: the one-column timeline with run grouping; filters by run, kind, class; keyboard map (mirroring Claude Code's bindings where they transfer: `j`/`k`, `/` filter, `Enter` detail, `Esc` back); visible focus; contrast ratio suitable for sustained night use; reduced-motion respected.
3. Phase 2 controls (`/btw` lane, model selector, approvals, dispatch) drawn greyed and labelled "Phase 2" so the boundary is visible, not implied.
4. Michou's acceptance recorded as an `approval` event in the ledger (by `kgme ledger note --kind approval`, from 0026) naming the canvas file hash.

## Outputs
The canvas (published artifact or `docs/readers/cockpit-design.md` with images under `memory/attachments/cockpit/`), Michou's `approval` event.

## Acceptance test
Michou can identify the timeline, a run, a failure class, and the keyboard focus from the canvas within ten minutes, using only the keyboard map as written, and approves it.

## Reviewer
Michou. Codex checks scope only: nothing in the canvas is Phase 2 without the label.

## Reversibility
Iterate; nothing is built from it until 0037.

## Needs from Michou
The wishlist's empty sections (Codex, Warp, Obsidian, aesthetic, things not wanted) filled in first, or a word that they stay empty for v0.

## Report
None beyond the approval event. `status: done` on approval. No commit of generated bundles (ADR-017).
