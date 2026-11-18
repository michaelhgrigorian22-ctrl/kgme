---
id: HANDOFF-0074
type: handoff
created: 2026-11-18T01:05:00-08:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-11-18T11:36:16-08:00
report: docs/audit/AUDIT-0172-review-handoff-0074-cycle-1.md
depends_on: [HANDOFF-0059]
---

# Proposal 0074 — `kgme mods` reads `claude plugin validate`'s new note format

## Why
- **`make check` has been red on `main` since Claude Code updated on 2026-11-17** (its `types/` and `tsconfig.json` regenerated at 23:50 PST). The failing check: `mods/kgme-cockpit: hooks or calls its handoff did not name: ui.render (default matcher key: plugin) [blocking]`.
- **The cause.** `kgme.toml [mods.allows]` already names `ui.render`. The validate report now writes a hooked event as `ui.render (default matcher key: plugin)`. `kgme/mods.py`'s `MATCHER` strips only `{…}` matchers, so the listing keeps the parenthesis, and the name no longer matches.
- **What it blocks.** `kgme review` refuses every red gate (HANDOFF-0071 was refused at 00:56), and `kgme merge design` has refused 8 design commits since 00:39.

## What
1. Make `listing` drop a trailing parenthetical note from each hooked event name, as well as the `{…}` matcher it already strips. Event names stay exact: `ui.render` must still not match `ui.renderX`.
2. Add a red-first test using the new note text verbatim, beside the existing listing tests. It asserts `ui.render (default matcher key: plugin)` lists as `ui.render`, and that an event the allows list doesn't name is still blocking.
3. Don't commit the regenerated `mods/*/tsconfig.json`. Add them to `.gitignore` beside `.claude-plugin/types/`, which is already ignored, since Claude Code writes both.

## Outputs
`kgme/mods.py`, the mods test file, `.gitignore`.

## Acceptance test (under five minutes)
`uv run python -P -m kgme.mods` reports 0 blocking, and `make check` is green, with HANDOFF-0071's staged diff left untouched in the index.

## Reviewer
Codex through `kgme review --handoff HANDOFF-0074`.

## Reversibility
One revert.

## Needs from Michou
Adoption. Commit it alone with `git commit -o`, so 0071's staged diff stays out.
