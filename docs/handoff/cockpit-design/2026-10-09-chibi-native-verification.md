---
id: CDH-0004
type: handoff
created: 2026-10-09T23:06:00-07:00
from: michou
to: cowork
tier: 2
status: done
completed: 2026-10-12T15:32:00-07:00
adopted_by: michou
adopted: 2026-10-11T16:51:00-07:00
depends_on: [CDH-0003]
design_track: HANDOFF-0036
verification: CDH-0005
---

# CDH-0004: Native verification of the rebuilt board 10 (after CDH-0003)

## Outcome and authority

Repeat CDH-0002 against CDH-0003's delivery, in the native Design canvas. Reshaped 2026-10-11T16:55:00-07:00 by Cowork to match what happened: Codex implemented CDH-0003 (done 2026-10-11T15:51:09-07:00, committed on `design` as `0bb87d5`), so the native verification is Cowork's and Codex's read-only review follows as CDH-0005. Adopted by Michou's word of 2026-10-11 16:51 ("Cowork can now perform CDH-0004's native verification"). Same authority and limits as CDH-0002: verify, do not repair, do not approve, do not start HANDOFF-0037.

## Do

1. Confirm CDH-0003 is `done`, its report exists, and every recorded hash and both digests match the files on disk; run `tests/test_design_sprites.py` and `kgme lint`. Confirm boards 1–9 are byte-identical to `7bf773f`.
2. Mount the delivery into the existing private review copy (the Design artifact "KGME Cockpit v0 — CDH-0002 review copy"), publishing only the changed files. Never the accepted viewer.
3. Run every check in CDH-0002's "Visual and behavioral checks", natively: all 49 specimens and both palette pairs on board 10 with no missing-frame error; the 24 px and 72 px contexts at actual size on both surfaces; each actor's seven modes through the board's 16 buttons in Play; calm via the Tweaks tab; the environment's reduced-motion setting; the Phase 2 card still dashed and unbound; no new keybinding; boards 7 and 8 unchanged.
4. Write `docs/audit/cockpit-design/cdh-0004-cowork-verification.md` in CDH-0002's exact format (`id: AUDIT-CDH-0004`, `CW` ids continuing from CW7, the three sections, hashes, canvas identity, proposed rulings). Captures under `logs/scratch/design-review/cdh-0004/`, never under `docs/` or `memory/`. Commit the report and this handoff's closeout on `design` by pathspec. Then set this file `done` with `completed:`, and hand Michou the CDH-0005 paste box for Codex.

## Closeout

Findings return to Michou. A `PASS` here is the native verification of the cast; HANDOFF-0036 closes on Michou's `approval` ledger event naming a committed sha, and `design` is merged to `main` on his word, never by this handoff.
