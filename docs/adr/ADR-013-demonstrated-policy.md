---
id: ADR-013
type: decision
status: accepted
created: 2026-09-10T09:40:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-013 — Policy is demonstrated, not declared: boundaries, canary tests, and the transaction contract

*Proposed in response to the external audit of 2026-09-10 (findings 2, 4, 5). Becomes accepted on Michou's word and commit.*

## Context
ADR-007 calls the router the policy choke point and ADR-008 relies on hooks and "restricted filesystem views." The audit is right that a router only governs calls made through it, that an independently capable subprocess (Claude Code, Codex, a Python worker) has its own reach, and that putting Tier 1 in a different directory does not make it inaccessible. The macOS application firewall is inbound-only and says nothing about what a worker may send out. ADR-009 recorded the ledger event after the commit, leaving a crash window in which an action succeeds unrecorded.

## Decision
1. **Permission manifest per worker.** Every worker (each Claude Code job profile, Codex job, Python job, browser worker) declares: readable paths, writable paths, tools, network destinations, highest data tier. The manifest lives in the repo beside the job.
2. **Enforcement in layers, each named.** Agent workers: a repo-scoped `.claude/settings.json` (ask-mode, explicit allow/deny) plus pre-tool hooks that block by path and command. Tier 1: at minimum encrypted at rest (`age`), decrypted only inside a local-model job that never holds network tools; the stronger boundary — a separate macOS user owning the Tier 1 repository with `0700` — is evaluated in Phase 1 and adopted unless it proves unworkable. Outbound network: the router for model calls; for everything else a per-worker egress rule via a host tool (LuLu or Little Snitch class) is a Phase 1 requirement, recorded here, not yet met.
3. **Canary tests before any scheduled job.** `tests/policy/` plants synthetic forbidden artefacts — a fake `.env`, a fake Tier 1 file, a forbidden destination — and each worker must demonstrably fail to read or reach them. Tests run before a job is first scheduled and after every permission change; results are ledger events.
4. **Transaction contract (write-ahead).** Approval binds to the hash of the exact proposed payload, its destination, and the relevant prior state. The ledger records an `intent` event *before* execution and an `outcome` event after. On every start, workers reconcile intents that lack outcomes by inspecting the destination and recording a reconciled outcome. Idempotency keys per item make re-runs safe.
5. **Bounded browser interface.** Models never receive a general "drive the browser" tool. The browser worker exposes named, allowlisted operations (`canvas.list_courses`, `canvas.get_file(id)`, …) that perform approved reads and return data. The dedicated profile isolates *accounts*; the operation allowlist is the *permission boundary*.
6. **Gate for scheduling.** No job runs unattended until: a completed backup exists and a restore has been tested; ADR-012's ledger durability is implemented; the worker's canary tests pass.

## Alternatives considered
- Trusting the router and prompt rules alone: the failure mode the audit names.
- Full OS sandboxing of every worker from day one: correct in principle; too heavy before Loop 0 exists. The canary tests make the gap measurable in the meantime.

## Consequences
The first code written in KGME is the validator and the canary tests, not a capability. ADR-009's pipeline gains the intent/outcome pair. ADR-010's browser worker gains an operation allowlist. Phase 1 acquires two named prerequisites: an egress tool decision and the Tier 1 boundary decision.
