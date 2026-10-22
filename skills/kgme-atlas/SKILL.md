---
name: kgme-atlas
description: Ask KGME for an atlas slice, a short map of the files a task touches and their neighbours, before planning a handoff or editing a file you have not read yet.
---

# kgme-atlas

A slice is a map of one task's neighbourhood: the files a handoff's Outputs name, or a path you give, and one step out from them (the tests that import them, their importers, what they import, the readers, ADRs, and handoffs that name them), as plain text under a token budget.

## When
- Before planning a handoff.
- Before editing a file you have not read in this session.
- When a review names a file you do not know.

## How
1. If a slice was carried into your prompt at launch (a section headed `# Atlas slice:`), use it and do not build another.
2. Otherwise run one of:
   - `uv run --frozen kgme atlas --slice HANDOFF-NNNN`
   - `uv run --frozen kgme atlas --around <path>` (repeat `--around` for more paths)
3. Read the slice for where things are, then open the real files it names. The map says where things are and how they connect, not what they say.

## Never
- Never orient by reading `atlas/` or `memory/` directly. The command builds the slice from the tree you are in and leaves out `memory/`, `logs/`, and Tier 1 paths for every model.

## Lessons
See `lessons.md` beside this file, and keep it short.
