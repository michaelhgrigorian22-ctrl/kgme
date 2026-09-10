---
id: ADR-008
type: decision
status: accepted
created: 2026-09-09T19:45:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-008 — Secrets and policy enforcement

## Context
A personal agent system with broad file access is one leaked token away from disaster, and prompt wording is not a security control. Meta's Muse and the failures reported around Instinct (autonomous sends, plaintext retention) set the reference.

## Decision
- Secrets live in macOS Keychain or a password manager CLI (1Password preferred if in use). Never in files, never in the repo, never in prompts or logs. Agents *invoke* a credential (a wrapper fetches it at runtime) and never read its value.
- Claude Code hooks enforce policy in code: a pre-tool hook blocks dangerous commands (destructive deletes, credential reads, pushes to remote, network calls from readers); a post-tool hook appends every tool call to the ledger.
- Approval gates: any irreversible or outward-facing action is prepared, shown, and executed only on explicit confirmation in the same session.
- Least privilege per job: each job declares the tools it needs and the highest data tier it may read; nothing else is mounted.
- Dependencies are pinned, from known sources, and kept few; each addition names what, why, and where from.
- FileVault on; Time Machine running; `logs/` and `memory/` excluded from any cloud sync that is not the encrypted GitHub remote for Tier 2/3.

## Alternatives considered
- `.env` files gitignored: still plaintext on disk and easily printed by an agent. Rejected for anything Tier 0.
- Trusting model instructions ("never print secrets") alone: necessary, not sufficient.

## Consequences
Every capability ships with its hook rules and its declared permissions. A weekly review reads the ledger for policy violations. Adding a dependency is a visible act.
