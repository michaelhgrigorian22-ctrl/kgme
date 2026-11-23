---
id: HANDOFF-0075
type: handoff
created: 2026-11-23T13:35:00-08:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0045]
---

# Proposal 0075 — Close the bypass flags, prove the fence, and a fast pre-commit hook

## Why
- **A bypass rule that lives only in prompts.** The rule against skipping hooks is written only in prompts (`control/review/codex-builder-prompt.md`: "never `-c core.hooksPath=…` and never `--no-verify`"), and the guard doesn't enforce it. Under Rat Stack's correction ladder and `kgme-agent-architect` law 7, a rule an agent can break belongs in code.
- **Unproven fences.** "Prove the fence" (law 8): KGME's fences have canary tests, but no standing probe re-runs every bypass on demand.
- **Late failures.** Lint and format failures surface only at `kgme review`, about 6 minutes in. A pre-commit check of a few seconds catches them at commit time.

## What
1. **Guard: bypass flags.** For every agent tool call, refuse:
   - `git commit --no-verify` and `git commit -n`;
   - any `-c core.hooksPath=…` or `git config core.hooksPath`, unless it's KGME's own code doing it (`kgme/merge.py`, `kgme/cheap.py` and `kgme/crew_io.py` set it on their own trial clones);
   - `--no-gpg-sign` is out of scope.
   
   Refuse a command that sets an environment variable to change hook behavior. Refusals are logged like every other guard refusal.
2. **Prove the fence on demand: `kgme fence prove`.** It runs each refusal the guard promises as a live probe against a throwaway clone and prints refused or allowed for each:
   - destructive git;
   - a write outside Outputs in loop mode;
   - a human-path write;
   - the new bypass flags;
   - once 0073 lands, the Hermes fence probes.
   
   Any allowed probe fails the command. Add it to `make canary` and the weekly review.
3. **Fast pre-commit hook** (`control/git-hooks/pre-commit`): `ruff check`, `ruff format --check` and `kgme lint` on the staged files only, with a target under 10 seconds. `make check` stays the review gate. The hook is skipped inside KGME's own trial clones, as the post-commit hook is today.
4. **Readers** for the guard and the hook gain "How to check it" (`kgme fence prove`) per the new CLAUDE.md convention.

## Outputs
`kgme/hooks/guard.py` and its tests, `kgme/fence.py` (with its CLI wiring), `control/git-hooks/pre-commit`, `tests/`. Human paths are delivered as diffs: `Makefile`, `docs/readers/`.

## Acceptance test (under five minutes)
1. `kgme fence prove` prints every probe as refused, on a clean checkout.
2. A staged file with a ruff error is refused at commit, in under 10 seconds.
3. `git commit --no-verify` from a Claude Code session is refused by the guard.

## Reversibility
Revert, and remove `control/git-hooks/pre-commit`.

## Needs from Michou
Adoption, after 0073.
