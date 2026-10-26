---
id: ADR-024
type: decision
status: accepted
created: 2026-10-26T01:25:07-07:00
author: claude-code
source: inferred
sources: ["HANDOFF-0059", "ADR-020", "ADR-022", "HANDOFF-0050"]
tier: 2
supersedes: null
---

# ADR-024 — Mods: what a Claude Code mod may hook, and how one enters KGME

*Draft for Michou's acceptance, written by Claude Code for HANDOFF-0059 from its §1. The diff is shown under ADR-004.*

## Context
- **What a mod is.** A Claude Code mod is a TypeScript module that runs inside Claude Code's own process. It hooks the engine's events and reaches the world only through the engine's `$` interface. It asks no permission, so it has what Claude Code has.
- **Why it needs a rule.** A mod that hooks tool calls or runs processes is policy, and policy is a human path. HANDOFF-0059 brings the first two mods, a pane over `/api/events` and `/capture`, and sets the rule before them.

## Decision
1. **Where they live, and who loads them.**
   - KGME's own mods live under `mods/<name>/`, one folder each.
   - `kgme session` loads them with `--plugin-dir`, as `kgme.toml [mods]` names them for the level.
   - `loose` and `cheap` load none, whatever the table says: an unattended session draws no UI and gets no process surface it did not have.
2. **Some hooks and calls need their handoff to name them.** A mod hooks `tool.call`, `prompt.compose` or `prompt.submit`, or calls `$.process`, `$.fs` outside the repository, `$.model`, or `$.http` beyond loopback, only when the handoff that brings it in names the hook or the call and why. The committed policy (hooks, deny list, guard) stays the boundary, and no mod replaces it.
3. **A third-party mod enters through a toolbox row** (ADR-020). The row records its sha, and its handoff records the listing from `claude plugin validate`.
4. **`make check` holds each mod to its listing.** It runs `claude plugin validate` on every folder under `mods/` and compares the listing to `kgme.toml [mods.allows]`, which records the events and `$` nouns the mod's handoff names. Any of the following is `blocking`:
   - a hook or call more than the handoff named;
   - a mod with no entry;
   - a failed validation;
   - a mod folder on a machine without `claude`.

## Consequences
- **The allowance is a human path.** `[mods.allows]` is in `kgme.toml`, so no agent can widen it. Changing what a mod may do is a diff Michou applies, the same act as adopting the handoff that names it.
- **Validate is the reading.** `claude plugin validate` reads a mod the way the engine will, so the check sees what would load, not what a reviewer guessed from the source.
- **Turning mods off.** Emptying `[mods]` turns every mod off. Deleting a folder removes one.
