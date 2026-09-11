---
id: ADR-016
type: decision
status: accepted
created: 2026-09-11T15:30:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-016 — Failure classes, bounded retries, and what earns a human interruption

*Proposed 2026-09-11 from a real observation: on another project, Michou's Codex↔Claude Code loop ran an audit phase with a three-strikes halt, and the three strikes were punctuation and GitHub rate limits. The procedure worked; the sensitivity was wrong. Becomes accepted on his word and commit.*

## Context
A halt-and-escalate rule that treats every failure as a strike turns the human into the retry mechanism for cosmetic and transient errors. That is the opposite of what "prepare, then ask" is for: the human is the gate for *consequential* decisions, not for typos and throttling. Without failure classes, a stricter audit makes the system noisier, not safer.

## Decision
Every check, test, and audit finding in KGME carries a **class**, and the class decides what happens — never the bare count.

| Class | Examples | Handling | Counts as a strike? |
|---|---|---|---|
| **blocking** | wrong output, policy violation (secret exposure, forbidden path, unapproved outward action), data-integrity failure, ambiguity about an irreversible step | stop the job; escalate | yes |
| **transient** | rate limit, timeout, network error, lock contention, provider outage | bounded retry with exponential backoff and jitter (default 3 attempts within 10 minutes), every attempt a ledger event; if the bound is exhausted, reclassify as `blocking: exhausted` | no — until exhausted |
| **cosmetic** | punctuation, whitespace, formatting, style | auto-fix if a deterministic tool exists (`ruff format`, a prose formatter), otherwise record as a `note`; surfaced in the weekly review, never in real time | never |
| **advisory** | a reviewer's non-blocking suggestion, a "consider…" | recorded for the weekly review | never |

- **Strikes count distinct root causes** of class `blocking` only. The same root cause recurring across retries is one strike with an attempt count, not three.
- **Escalation packet.** When a job does interrupt Michou it sends one screen: what failed, its class, the evidence, the options (override / reject / retry), a recommended default, and what happens if he does nothing (nothing runs). The intended reply is one word.
- **Rate limits are anticipated, not survived.** The router (ADR-007) knows each provider's limits, paces calls, and for `cosmetic`/cheap classes falls back to another provider or the local model rather than waiting or failing. A rate limit reaching the audit phase is itself a `note` against the router.
- **Acceptance criteria are per deliverable.** A check belongs in a job's audit gate only if failing it would make the deliverable wrong or unsafe for its stated audience. Punctuation in an internal data pull is not a check; typos in an external memo are a `cosmetic` auto-fix, still not a strike.
- Classes are a required field on ledger `outcome` events and on every test in `tests/`.

## Alternatives considered
- Raise the strike threshold: still interrupts for the wrong reasons, just later.
- No halting at all: loses the one property worth keeping — that consequential failures reach a human.

## Consequences
Loops get quieter and the interruptions that remain are worth reading. The weekly review gains a "notes and advisories" pile that shows where formatters or router pacing are missing. Loop 0's four acceptance tests are the first to carry classes.
