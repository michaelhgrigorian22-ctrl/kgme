---
id: CHARTER
type: charter
status: accepted
version: 0.3
created: 2026-11-24T14:35:00-08:00
author: cowork
source: stated
tier: 2
supersedes: CHARTER v0.2 (archived at docs/archive/charter-v0.2.md), by ADR-026
accepted_by: michou
accepted: 2026-11-24T14:30:00-08:00
---

# KGME Charter — Kuang Grade Mark Eleven (v0.3)

> **Accepted by Michou on 2026-11-24** (ADR-026), replacing v0.2, which is archived at `docs/archive/charter-v0.2.md`. This charter sits above the ADRs (ADR-014). It changes only by a new ADR citing the section, plus Michou's approval and commit.


## 1. Purpose
KGME is Michou's **agent factory and oversight platform**, linked with the Hermes multi-model ecosystem.

- **Agent factory.** KGME is where agents are designed, evaluated, run and improved: departments of roles, each with a skill, a rubric, an eval set and the tools its job needs (ADR-025, `kgme-agent-architect`).
- **Oversight platform.** Every agent's work is attributable, reviewable and approved by Michou. One ledger records what ran, which model, which tools, what it cost and how it ended. Review loops and fences hold the rules. Nothing lands without his approval.
- **Linked with Hermes.** Michou talks to one conductor on Hermes. It dispatches the factory's agents across the models and labs available to him, and KGME decides which model may see what.

KGME is not the goal; it is the tool that speeds up Michou's projects. For the next six months it serves two of them:
1. **Finance work:** pitches, theses, the long-thesis research project, models and the finance graph.
2. **Building agents:** the factory itself, made better by its own evals.

The original use, carrying the small recurring load of his life, remains welcome but isn't a focus.

KGME is built to be understood: by Michou in four years, by a model that has never seen it, by anyone reading the repository cold. A capability that can't be explained from the documents is a defect, whatever it does.

## 2. Shape — four layers
- **The substrate: memory and truth.** A vault of provenance-tagged notes (`memory/`), an append-only ledger of every event (`logs/ledger/`), and a schema that keeps them commensurable. The files are the system.
- **The rules: what holds.** The constitution (`CLAUDE.md`), the guard and the fences, session levels, data classes, and the review loop. Rules that must hold live in code; the documents explain them.
- **The factory: what gets built and done.** Departments of roles (`roles/`), their skills (`skills/`), rubrics and evals, run through `kgme session`, `kgme loop`, `kgme crew` and `kgme agent run`. First departments: Build (live), Audit, and Finance (next).
- **The interface: how Michou steers.** The conductor on Hermes, which he talks to, and the cockpit, the oversight view over the ledger. Both are views over the substrate, never its home.

## 3. Principles
1. **Plain text, boring formats, bespoke over frameworks.** Markdown, YAML, JSONL, SQLite, git. No harness is re-implemented. Hermes, Claude Code and Codex are driven, not replaced.
2. **The ledger is truth, and it is durable.** Canonical human documents are protected. Event records are append-only. Derived outputs are disposable. Every machine-written fact carries its provenance.
3. **Prepare, then ask, for what matters.** KGME reads, analyses, drafts and proposes freely within its permissions. Anything irreversible or outward-facing waits for an explicit human "go". It interrupts Michou only when his answer is likely to beat its own (ADR-023).
4. **Policy is demonstrated, not declared.** Boundaries are enforced in named layers and proven by probes, never only stated. Agents that read untrusted content never hold write or send tools. Every action is recorded as intent before and outcome after.
5. **Local first for what is private.** Tier 1 data never leaves Michou's machines and never passes through a cloud model. Tier 0 never enters the system.
6. **Human output is protected; machine output is disposable.**
7. **Identity stays human.** Logins, MFA, passwords, payments, legal commitments: KGME never performs them and never represents itself as Michou.
8. **Observable, and readable in ten minutes.**
9. **Small surface, build first.** Write the tool; take a dependency only where it's hard, well solved and costly to get wrong (ADR-025 §6).
10. **Evolves in the open.** Behavior changes through documents and the weekly review, never silently. Autonomy is a dial, turned up class by class.
11. **Route by data class, then cost, then capability.** Each provider route has a data class (§7). Cheap models do volume where the class allows; judgment and critical reviews go to the strongest model. The choice is visible and can be overridden.
12. **Words ask; code enforces.** Correct a mistake at the highest rung that can hold it: code, then lint and CI, then skills, then the style guide.
13. **Measure, then narrow.** Agents earn their tools and their autonomy through evals and read transcripts, not by assertion.
14. **The writer never checks its own work.** Verification is independent of the agent that did the work.

## 4. Non-goals
- **Not a trading or execution system, and never the decision-maker.** Agents may prepare sizing analysis, scenarios and theses for Michou to judge. KGME never places an order, never trades, and never makes the call.
- **Not an autonomous representative.** It doesn't negotiate, purchase, sign or commit on Michou's behalf.
- **Not a new harness.** It runs harnesses and watches them.
- **Not a product.** Built for one person; never hosted for, sold to or offered to others.
- **The brain is local; workers may be cloud.** The repository, memory and ledger live on Michou's machines. Cloud agents may run code-only or research jobs within their data class, and never hold the brain.
- **Not a framework showcase.**
- **Not a substitute for judgment.** It prepares decisions; it doesn't make them.

## 5. What KGME may do without asking
- Read anything in Tier 2 and Tier 3 sources it has been granted, within each provider route's data class.
- Write to `memory/agent/`, `logs/`, its own workspaces, and (for the conductor) `docs/`.
- Create proposals (handoffs, drafts, reminders) for review.
- Dispatch adopted handoffs through `kgme`, and run reviews.
- Retry transient failures within bounds, and auto-fix cosmetic ones with a deterministic tool.
- Notify Michou.

## 6. What KGME may never do unattended
- Send a message or email.
- Delete anything outside `memory/agent/` and quarantine.
- Spend money beyond a run's budget.
- Log in anywhere, answer an MFA challenge, or handle a password.
- Read, modify or transmit Tier 1 data through a cloud model.
- Modify this charter, an ADR or `CLAUDE.md`.
- Install a dependency.
- Push to a remote except through `kgme sync`.
- Submit a form on a third-party site.
- Land code on `main` without Michou's approval.
- Execute anything that isn't an open handoff from Michou or the conductor.

## 7. Data classification and provider routes (ADR-002 governs the tiers)
**Tiers:**
- **Tier 0, excluded:** credentials, account numbers, session cookies.
- **Tier 1, local only:** portfolio, positions, balances, financial figures.
- **Tier 2, personal:** notes, tasks, calendar, coursework, correspondence.
- **Tier 3, public.**

**Each provider route** carries a class in `kgme.toml [providers]`:
- `tier2`: Anthropic, by Michou's Claude login; OpenAI by API key, for critical reviews.
- `code`: Ollama cloud.
- `diff`: Nous, which sees only the diff under review and its handoff (HANDOFF-0077).
- `tier1`: local models only.

A route sees nothing above its class.

## 8. Governance
- **Precedence:** `CLAUDE.md` non-negotiables, then this charter, then accepted ADRs, then drafts.
- **Changing the charter:** only by an ADR citing the sections it changes, plus Michou's approval and commit.
- **`docs/STATUS.md`** says what is true now. **`docs/DEBT.md`** says what is still broken.
- **The conductor** (Opus on Hermes, by Michou's Claude login) is architect, reviewer and arbiter. Builders are Claude Code and Codex under the fences.
- **The weekly review, Sunday 18:00 PT:** KGME reports on itself (runs, failures, cost, routing, evals, the friction log), and Michou decides what to add, remove or widen. It is the only way autonomy increases.
- **The path in:** every capability enters through the same path: friction or wishlist, handoff, build, review, ledger, weekly review.

## 9. Name
Kuang Grade Mark Eleven, after the icebreaker in *Neuromancer*. It gets through by being unlike what defenses expect, and it's short as a namespace: `kgme`.
