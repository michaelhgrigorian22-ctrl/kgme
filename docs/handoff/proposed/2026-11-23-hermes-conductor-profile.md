---
id: HANDOFF-0076
type: handoff
created: 2026-11-23T13:45:00-08:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0073]
---

# Proposal 0076 — The `kgme-conductor` Hermes profile, versioned in the repo and exported by script

## Why
Michou wants KGME tuned for Hermes at the switch. On 2026-11-23 a profile named `kgme-builder` ran on provider `nous`, with 68 skills loaded and Hermes's default persona. That breaks the Nous ruling of 2026-11-18, loads far more context than the conductor uses (law 1 of `kgme-agent-architect`), and lives only in Hermes's UI, so nothing reviews it and nothing can restore it.

## What
1. **Measure first:** the structure of a profile folder on Michou's install (`~/.hermes/profiles/<name>/`: `SOUL.md`, `.env`, the config keys for model and provider), and whether the export and import commands exist. Cite file and line. Also answer: **can a profile limit its skills, and do skills load progressively** (only the name and description until one is used)? If they load progressively, drop the skills allowlist from item 2.
2. **`control/hermes/kgme-conductor/`** holds the profile's source: `SOUL.md` (drafted by Cowork), a `profile.yaml` or equivalent with the model `anthropic/claude-opus-5-5`, provider `anthropic`, the skills allowlist from the README, and the hook from 0073.
3. **`kgme hermes export`** writes the profile into `~/.hermes/profiles/kgme-conductor/`. It backs up whatever is there first, and refuses to write any provider but `anthropic`.
4. **`kgme lint`** checks that the source names no `nous` provider and that every skill in its allowlist exists.

## Acceptance test (under five minutes)
Export, open the profile, and run the README's "How to check it". Then run the profile with a `nous` provider in the source: lint must block it.

## Needs from Michou
Adoption after 0073. Meanwhile: switch the current profile's provider to `anthropic` by hand, and rename it `kgme-conductor`. Builders are Claude Code, launched by the conductor through `kgme`.
