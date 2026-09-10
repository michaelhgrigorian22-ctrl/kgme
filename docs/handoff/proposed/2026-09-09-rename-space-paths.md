---
id: HANDOFF-0011
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
status: proposed
tier: 2
depends_on: HANDOFF-0001
audit_ref: "Paths with spaces under `~/Projects/Finance`, `~/Projects/Personal`, `~/Projects/School`."
---

# Handoff 0011 (proposed) — Rename paths with spaces under `~/Projects`

## Why
Audit found spaces in filenames and folder names under Finance (28,071 files, e.g. `ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/`), Personal (75 files), and School (2,579 files). Phase 0 §3: "No spaces in any path under `~/Projects`; kebab-case folders. Rename before scripts depend on them." Automate and Tools are already clean.

## What
Curated pass, one folder at a time, in Michou's presence. For each candidate:

1. `find "<path>" -maxdepth 1 -mindepth 1 -name '* *'` → list children with spaces.
2. Propose kebab-case name (e.g., `"ARCHIVE PITCHES - SUMMER 26 INTERNSHIP" → "archive-pitches-summer-26-internship"`).
3. **Search for external references first**: `grep -rIl "<old name>" ~/Projects`; for workbooks, `unzip -p file.xlsx xl/externalLinks/*` and grep. If hits, update the referring workbook before renaming.
4. `mv "<old>" "<new>"`.

Order: Personal (75 files, lowest blast) → targeted folder renames in School (2,579 files) → Finance last (28,071 files, live models with external links).

## Reversibility
`mv <new> <old>` restores. Once downstream references have been rewritten to the new name, reverting the folder rename without also reverting the reference rewrites re-breaks the links.

## Risks
Excel external links resolve by absolute path; renaming a parent folder silently breaks every `[external.xlsx]Sheet1!$A$1`-style reference. Same for hard-coded paths in scripts and notebooks. VS Code recent-workspaces and Warp session history point at old names.

## Needs from Michou
Per-folder approval. A list of actively-used Finance workbooks so their references are updated first. Willingness to fix his own bookmarks in VS Code, Warp, and Obsidian.
