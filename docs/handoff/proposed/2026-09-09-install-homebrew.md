---
id: HANDOFF-0008
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
status: proposed
tier: 2
depends_on: HANDOFF-0001
audit_ref: "Homebrew (`brew`) not installed."
---

# Handoff 0008 (proposed) — Install Homebrew

## Why
Audit reported `brew --version` = `command not found: brew`. Phase 0 §3 names Homebrew; every downstream tool proposal (`gh` in HANDOFF-0009, later `op`/`codex`) needs it or an explicit alternative. The stock install one-liner is `curl … | bash`, which the global permissions correctly `deny`; this proposal downloads the script first, lets it be inspected, then runs it explicitly.

## What
1. `mkdir -p ~/Downloads/brew-install`
2. `curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o ~/Downloads/brew-install/install.sh`
3. `wc -l ~/Downloads/brew-install/install.sh` and `head -40 ~/Downloads/brew-install/install.sh` — show Michou what will run.
4. `NONINTERACTIVE=1 bash ~/Downloads/brew-install/install.sh` — the `NONINTERACTIVE=1` skips the "press Return to continue" but the installer still prompts for the sudo password.
5. Add to `~/.zprofile` if missing: `eval "$(/opt/homebrew/bin/brew shellenv)"`. Re-source: `source ~/.zprofile`.
6. Verify: `brew --version` and `brew doctor`.

## Reversibility
Homebrew's official uninstall script: `curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh -o /tmp/brew-uninstall.sh && bash /tmp/brew-uninstall.sh`. Removes `/opt/homebrew/` and its tap/cache directories. Formulae that ship auxiliary state in `~/Library/Application Support/<name>/` remain and need per-app cleanup. The shellenv line in `~/.zprofile` must be removed manually.

## Risks
Installs a package manager with broad file access under `/opt/homebrew/`. Requires Xcode Command Line Tools (already present — `/Library/Developer/CommandLineTools`). First install ~5 min. `~/.zprofile` gets a new line; back it up first (`cp ~/.zprofile ~/.zprofile.bak.$(date +%Y%m%d)`).

## Needs from Michou
Sudo password for the installer. Approval after step 3 to run the downloaded script (a five-second inspection is enough — Michou needn't read all 800 lines).
