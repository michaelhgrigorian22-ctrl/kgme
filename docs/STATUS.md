---
id: STATUS
type: note
status: active
created: 2026-09-10T09:50:00-07:00
modified: 2026-09-11T14:00:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — current status (ADR-014)

The one place that says what is true *now*. Historical records are never edited; this file is. Updated whenever a status changes. Last updated 2026-09-11 14:00 PDT by Cowork.

## Phase
**Phase 0 — Prepare, narrowed on 2026-09-10** (see `plans/phase-0-prepare.md` §8). Nothing runs unattended. No runtime code exists yet; the first code will be the validator and the policy canary tests, then Loop 0.

## Gates before anything is scheduled (ADR-013 §6)
| Gate | State | Governing record |
|---|---|---|
| Completed backup + tested restore | **MET 2026-09-11 13:12 PDT** (Backblaze 10.0.1.1038; PEK enabled per Michou 12:54; 1-year version history; restore of one file hash-verified; AUDIT-0007) | HANDOFF-0019 — done |
| Ledger durable and tracked | ADR-012 proposed; `.gitignore` corrected; no ledger written yet | ADR-012 |
| Repo-scoped permissions + hooks | not built; global settings are `auto` mode (AUDIT-0002) | ADR-013 §2 |
| Canary tests per worker | not built | ADR-013 §3 |
| Charter accepted | draft v0.1, `[REVIEW]` passages open | `charter.md` |

## Open decisions (Michou)
| Decision | Options / recommendation | Blocks |
|---|---|---|
| Password manager | none installed; Apple Passwords (built into macOS) is the zero-cost interim — the Backblaze private key must live somewhere tonight | secrets handling (ADR-008) |
| Accept ADR-012 … 018 | Read; say the word; Claude Code commits with `status: accepted` | Everything below |
| Backup | **decided 2026-09-11: Backblaze** (no external drive). Set the private encryption key; consider 1-year version history | HANDOFF-0019 |
| GitHub account | **created 2026-09-11** → HANDOFF-0023 does `gh auth login` (HTTPS) and the private remote | — |
| Conventions pointer | **decided 2026-09-11: `~/Projects/Finance/Active/MODELING_CONVENTIONS_V2.md`** (newest). Applied by HANDOFF-0018 step (c) | — |
| Global instruction files | strip nothing yet; fix the dangling pointer and the `~/AGENTS.md` memory path; decide later whether Finance rules move under `~/Projects/Finance/` | Codex/Claude drift |
| Sleep policy | A / B / C after two weeks of observation | proposal 0012 |
| Tier 1 boundary | **backup half decided:** Tier 1 goes off-machine only under Backblaze's private encryption key (ADR-002 open question closed). Access half unchanged: encrypt at rest (`age`) now; separate macOS user evaluated in Phase 1 | ADR-013 §2 |
| Egress control tool | LuLu / Little Snitch class — Phase 1 | ADR-013 §2 |
| Control surface | **proposed (ADR-017):** desk = local cockpit app (a view over the ledger); phone = Telegram later | Phase 1 |
| First loop | Loop 0 = `kgme brief` (manual, read-only, local) — proposed in the plan | Phase 1 start |

## Proposals (`docs/handoff/proposed/`) — adoption = move to `docs/handoff/`, `from: michou`, `status: open`
| Id | Topic | Disposition |
|---|---|---|
| 0006 | Time Machine | **abandoned** — replaced by Backblaze; HANDOFF-0019 verifies and restore-tests |
| 0007 | Firewall | **superseded** → HANDOFF-0020 (open) |
| 0008 | Homebrew | **superseded** → HANDOFF-0021 (open) |
| 0009 | `gh` | **superseded** → HANDOFF-0022 (open) |
| 0010 | SSH key | **superseded** → HANDOFF-0023 (open): `gh auth login` over HTTPS + private remote |
| 0011 | Rename paths | **rejected** → folded into the migration plan; only paths KGME touches; metadata-only manifest first |
| 0012 | `pmset` | **deferred** to end of observation window; capture `pmset -g custom` and `sched` first |
| 0016 | Finance folder disposal | **abandoned** (scope error) → 0018 |
| 0018 | `finance-python` disposal | **awaiting Michou**: archive 80 files (6 MB) + 2 memory notes, delete `.venv`/caches/transcripts, fix pointers; final `rm` gated on completed backup. Needs the conventions-pointer decision |

## Handoffs done
0001 audit · 0002 repo init · 0003 propose fixes · 0004 global config · 0005 git identity · 0013 Codex review · 0014 Finance inventory (mis-scoped, data still valid) · 0015 aliases · 0017 finance-python inventory.

## Corrections to date
Six entries in `corrections.md`: timezone; report frontmatter; id collision; Finance scope error; "copied library" inference; ledger contradiction. All Cowork's. All caught by the process before harm.

## Deferred on purpose (2026-09-10 narrowing)
Ollama models and embeddings · Playwright and the browser worker · Telegram · path renaming outside `Automate` · additional providers · scheduling. Each returns when Loop 0 or the friction log demonstrates need.
