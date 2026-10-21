---
id: HANDOFF-0009
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
tier: 2
depends_on: HANDOFF-0008
audit_ref: "GitHub CLI (`gh`) not installed."
status: superseded
superseded_by: HANDOFF-0022
reason: "Reissued by Cowork with the amendments from AUDIT-0004 (Codex review), 2026-09-11."
---

# Handoff 0009 (proposed) — Install `gh` via Homebrew

## Why
Audit reported `gh --version` = `command not found`. Phase 0 §3 names it; Phase 0 §7 (Accounts) needs it to create the private KGME repository and push. Depends on HANDOFF-0008 being `done` so `brew` exists.

## What
1. `brew install gh`
2. Verify: `gh --version` (expect the current stable, roughly `gh version 2.x`).
3. **Do not run `gh auth login`** — authentication is Phase 0 §7 territory and requires Michou to complete a browser or device-code flow with the GitHub account he chooses.

## Reversibility
`brew uninstall gh`. Removes the binary and its Homebrew cache. Any `gh auth` credentials would live in `~/.config/gh/hosts.yml`; this proposal does not create that file (no auth is run), so nothing to clean up. If auth is later run, `gh auth logout` clears it and the file can be removed with `rm -rf ~/.config/gh`.

## Risks
Minimal. `gh` is a first-party GitHub-maintained project with a stable release cadence. No sudo required (Homebrew installs into `/opt/homebrew/`). No network side effects until `gh auth login` is run separately.

## Needs from Michou
Nothing for the install itself. For the later `gh auth login` step (out of scope for this proposal): Michou present at the terminal to complete the browser flow, and the GitHub account he intends to use (Phase 0 §7).
