---
id: CHARTER
type: charter
status: accepted
version: 0.2
created: 2026-09-11T22:30:00-07:00
author: cowork
source: stated
tier: 2
supersedes: CHARTER v0.1 (archived at docs/archive/charter-v0.1.md)
accepted_by: michou
accepted: 2026-09-11T23:00:00-07:00
---

# KGME Charter — Kuang Grade Mark Eleven (v0.2)

> **Accepted by Michou on 2026-09-11.** Drafted by Cowork from his 2026-09-11 rewrite of §1 and ADR-012…018. Per ADR-014 this charter now sits above the ADRs: an ADR that conflicts with it is superseded. It changes only by a new ADR citing the section, plus Michou's approval and commit. The v0.1 draft is archived at `docs/archive/charter-v0.1.md`. Passages still marked **[REVIEW]** are open items Michou fills in at his own pace; they do not block acceptance.

## 1. Purpose

KGME is Michou's own environment for working with AI agents — the place where the harnesses live.

It began as an instrument to carry the small, recurring cognitive load of his life — remembering, reminding, fetching, preparing, filing — so that his attention goes to the work that needs it. That remains true and is now one use among several. As the project took shape, the objective widened: KGME is the interface where Claude Code, Codex, and whichever models come next are run, observed, and steered, designed to Michou's functional and aesthetic preference.

*Functional* means the interface mirrors every convenience of a terminal Claude Code session — across models and labs — with easy model picking, usage-efficiency optimisation, and the quality-of-life and accessibility details that turn a good tool into a great one. The reason KGME is worth building rather than just using a terminal is oversight: Michou wants to see and direct the activity of agents, primary brains and orchestrators across multiple models from multiple labs in one place, and to add what a terminal cannot offer. *(Michou, 2026-09-11, lightly edited.)*

It is an instrument and a workshop, not a companion in the emotional sense and not a decision-maker. It is built to be understood: by Michou in four years, by a model that has never seen it, by anyone reading the repository cold. A capability that cannot be explained from the documents is a defect, whatever it does.

## 2. Shape — the three layers

KGME is three things stacked, each a plain folder in one repository.

**The substrate** — memory and truth. A vault of provenance-tagged notes (`memory/`), an append-only ledger of every event (`logs/ledger/`), and a schema that keeps them commensurable. The files are the system; every tool is a view or a worker over them.

**The cockpit** — the interface. A local app that launches agent jobs through the vendors' own scriptable modes, ingests every event they emit into the ledger in one shape, renders one timeline across all models, and answers their permission prompts in Michou's own UI. It preserves the grammar of the terminal harness — side questions that never touch the main context, queued messages, interrupt, transcript, keyboard-first everything — and adds a model selector, an "optimized" mode that routes each question to the most efficient model and shows why, and an editor that follows the run. It lives in `cockpit/`, visible and auditable in VS Code, and is a view over the ledger, never a harness of its own.

**The workers** — what gets done. Jobs that remember, remind, fetch, prepare, and execute small approved actions: the daily brief; coursework from the school's systems into the personal calendar; reminders born from the friction log. **[REVIEW — name the first three you want working; the two above are the ones you have already named.]**

## 3. Principles

1. **Plain text, boring formats, bespoke over frameworks.** Markdown, YAML, JSONL, SQLite, git. Anything not plain text in git is at risk. No harness is re-implemented; Claude Code and Codex stay themselves and are driven, not replaced.
2. **The ledger is truth, and it is durable.** Three classes of data: canonical human documents (protected), durable event records (append-only, never deleted, never "regenerated"), disposable derived outputs (deletable). Every machine-written fact carries provenance — stated, inferred, or fetched. "Forget" hides; "purge" is a rare, human-approved act with its own record.
3. **Prepare, then ask — for what matters.** KGME reads, analyses, drafts and proposes freely within its permissions. Anything irreversible or outward-facing waits for an explicit human "go" in that moment; never a standing permission. And it interrupts only for failures that are *blocking*: transient errors are retried within bounds, cosmetic ones are auto-fixed or noted for the weekly review. The human is the gate for consequences, not the retry mechanism for typos.
4. **Policy is demonstrated, not declared.** Each worker has a permission manifest; boundaries are enforced in named layers and proven by canary tests before anything is scheduled. Agents that read untrusted content never hold write or send tools. Every action is recorded as intent before it runs and outcome after.
5. **Local first for what is private.** Tier 1 data never leaves the machine except by a per-item, logged, human-confirmed act — and never passes through a cloud model, not even as a tool result. Tier 0 data never enters the system at all.
6. **Human output is protected; machine output is disposable.** Nothing Michou wrote is overwritten without an approved diff. Everything an agent produced is regenerable and deletable without loss.
7. **Identity stays human.** Logins, MFA, passwords, payments, legal commitments: KGME never performs them and never represents itself as Michou to a third party. **[REVIEW — confirm you want this stated this strongly.]**
8. **Observable, and readable in ten minutes.** Every run logs what ran, which model, which tools, what it cost, and how it ended. Every file in the repository can be read cold in ten minutes and explained. A system Michou cannot explain is a bug.
9. **Small surface.** Few dependencies, pinned, from known sources. Twelve understood dependencies beat four hundred inherited ones.
10. **Evolves in the open.** Behaviour changes through documents — ADRs, handoffs, schema versions, the status page — and a weekly review, never silently. Autonomy is a dial turned up deliberately, class by class; never a default.
11. **Cheap models do volume, judgment goes to the best model.** Routing is by sensitivity first, then cost, then capability; the decision is visible and overridable every time.

## 4. Non-goals

- **Not a trading or execution system,** and not a source of investment decisions. It may fetch, file and remind about market material; it does not trade, size, or recommend.
- **Not an autonomous representative.** It does not negotiate, purchase, sign, or commit on Michou's behalf with any third party.
- **Not a new harness.** It does not re-implement Claude Code or Codex; it runs them and watches them.
- **Not a product.** Built for one person on one machine, on his own subscriptions; never hosted, sold, or offered to others.
- **Not cloud-hosted.** The brain lives on the laptop; cloud models are workers it calls, not where it lives.
- **Not a framework showcase.** If a library would make KGME harder to explain, it is the wrong library.
- **Not a substitute for judgment.** It prepares decisions; it does not make them.

**[REVIEW — anything else to rule out permanently?]**

## 5. What KGME may do without asking

- Read anything in Tier 2 and Tier 3 sources it has been granted.
- Write to `memory/agent/`, `logs/`, and its own working directories.
- Create *proposals* — draft events, reminders, messages, handoffs — for review.
- Retry transient failures within bounds; auto-fix cosmetic ones with a deterministic tool.
- Notify Michou through the cockpit (and, later, the phone).
- Run read-only jobs by hand; run them on a schedule only after their canary tests pass.

**[REVIEW — widen or narrow; this list changes only by ADR.]**

## 6. What KGME may never do unattended

Send a message or email. Delete anything outside `memory/agent/` and quarantine. Spend money. Log in anywhere, answer an MFA challenge, or handle a password. Read, modify, or transmit Tier 1 data. Modify this charter, an ADR, or `CLAUDE.md`. Install a dependency. Push to a remote. Submit a form on a third-party site. Share a Tier 1 fact with any cloud model. Execute anything that is not an open handoff from Michou or Cowork.

## 7. Data classification (summary — ADR-002 governs)

Tier 0, excluded: credentials, account numbers, session cookies, anything whose leak is a security risk regardless of safeguards. Tier 1, local-only: portfolio, positions, balances, financial figures. Tier 2, personal: notes, tasks, calendar, coursework, correspondence. Tier 3, public.

## 8. Governance

- Precedence when documents disagree: `CLAUDE.md` non-negotiables → this charter, once accepted → accepted ADRs → drafts. An ADR that conflicts with the charter is superseded.
- This charter changes only by a new ADR that cites the section changed, plus Michou's explicit approval and commit. ADRs are append-only.
- `docs/STATUS.md` is the single statement of what is true now; historical records are never edited.
- **Weekly review** **[REVIEW — pick a day and a time]**: KGME reports on itself — runs, failures by class, cost, routing decisions and overrides, the friction log, the notes-and-advisories pile. Michou decides what to add, remove, or widen. This is the only mechanism by which autonomy increases.
- Every capability enters through the same path: friction log or wishlist → handoff → build → review → ledger → weekly review.

## 9. Name

Kuang Grade Mark Eleven, after the icebreaker in *Neuromancer* — chosen because it gets through by being unlike what defenses expect, and because it is short as a namespace: `kgme`.
