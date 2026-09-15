---
id: STATUS
type: note
status: active
created: 2026-09-10T09:50:00-07:00
modified: 2026-09-14T22:25:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — current status (ADR-014)

The one place that says what is true *now*. Historical records are never edited; this file is. Last updated 2026-09-14 22:25 PDT by Claude Code (Phase 1 deliberation, AUDIT-0011).

## Phase
**Phase 0 — Prepare: complete as of 2026-09-11**, except the housekeeping list below. **Phase 1 — Loop 0 and the cockpit: open as of 2026-09-14.** Plan amended that evening after a four-model deliberation (AUDIT-0011); build order at `plans/phase-1-loop-0.md`, fifteen proposals HANDOFF-0025…0039 under `handoff/proposed/`, ADR-019 (ledger event schema) proposed. Code starts when Michou adopts HANDOFF-0025. Nothing runs unattended. No runtime code exists yet.

## Gates before anything is scheduled (ADR-013 §6)
| Gate | State | Record |
|---|---|---|
| Completed backup + tested restore | **MET** 2026-09-11 — Backblaze (private key, 1-year history), restore hash-verified; private GitHub remote `michaelhgrigorian22-ctrl/kgme` in sync | AUDIT-0007, AUDIT-0009 |
| Charter accepted | **MET** 2026-09-11 — v0.2 accepted; v0.1 archived; four `[REVIEW]` refinements open, non-blocking | `charter.md` |
| Ledger durable and tracked | ADR-012 accepted; `.gitignore` tracks `logs/ledger/`; **no ledger written yet**; event shape fixed by ADR-019 (proposed) | HANDOFF-0026 |
| Repo-scoped permissions + hooks | **not built**; global settings are `auto` mode with a wide allowlist (AUDIT-0002) | HANDOFF-0027 (settings), 0028 (hook pair) |
| Canary tests per worker | **not built** | HANDOFF-0032; network cells advisory until LuLu (0038) |

## Ground layer (done)
Firewall on · Homebrew 6.0.22 (pinned installer `8949852`, analytics off) · `gh` 2.100.0 pinned · `gh auth` over HTTPS via credential helper · Codex CLI 0.154.0 · shell aliases (`kgme`, `kgme-claude`, `kgme-codex`) · git identity set · ADR-001…018 accepted · every handoff 0001–0023 done; 0024 abandoned as unnecessary.

## finance-python (done)
Unit reduced to its 80 human files (6.3 MB) at `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/`; byte-identical hash-verified archive with git baseline at `~/Archive/finance-python-2026-09/`; ~24,667 regenerable files / 906 MB removed; global conventions pointer → `Active/MODELING_CONVENTIONS_V2.md`; `~/.claude.json` dead keys and stale Claude Code state removed; two memory notes archived. **Michou's ruling: the working copy stays in place.** `~/Projects/Finance` untouched otherwise.

## Open decisions (Michou)
| Decision | Options / recommendation | Blocks |
|---|---|---|
| `rm -rf` policy | **Decided 2026-09-14:** global deny stays; `kgme clean` with named targets, allowlisted roots, one ledger event per deletion. | HANDOFF-0033 |
| Password manager | none; Apple Passwords interim (holds the Backblaze key) | ADR-008 secrets handling |
| Sleep policy | A / B / C after two weeks of observation | proposal 0012 |
| Tier 1 access boundary | **Decided 2026-09-14:** `age` at rest now; separate macOS user evaluated and ruled on at Phase 1 exit | HANDOFF-0038 |
| Egress control tool | **Decided 2026-09-14:** LuLu, installed at the end of Phase 1 | HANDOFF-0038 |
| First three workers | daily brief and coursework→calendar named; third waits for ten real friction entries (2026-09-14) | HANDOFF-0039 |
| Weekly review slot | **Decided 2026-09-14:** Sunday 18:00 PT | first held at Phase 1 exit (0039) |
| Working copy of finance-python | stays for now; delete later or not at all | — |
| `kgme` shell alias | **Decided 2026-09-14:** the CLI owns `kgme`; the `cd` alias is renamed, default `kgh` unless Michou names another | HANDOFF-0025 |
| Review gate | **Decided 2026-09-14:** a blocking-class finding opens a fix-and-re-review loop between models, bounded per ADR-016, escalating to Michou at the bound | HANDOFF-0025 (protocol), 0029 (command) |
| Schema v1.2 | **Decided 2026-09-14:** validator covers `memory/` and `docs/`; repair by schema rule for append-only types, never by editing an ADR | HANDOFF-0030 |

## Proposals still open (`docs/handoff/proposed/`)
0011 path renaming — folded into the migration plan · 0012 `pmset` — deferred to end of observation window · **0025–0039 Phase 1 sequence (2026-09-14)**, adopted one by one in order; 0030 is for Cowork, 0035 for Michou, 0036 for Cowork and Michou. All others superseded, abandoned, or done.

## Housekeeping (non-blocking)
- VS Code → Open Recent → clear the three dead `finance-python` entries (UI only).
- `brew doctor`: Command Line Tools 26.3 via System Settings → Software Update.
- Duplicate Claude Code install: `which -a claude`, remove the stale 2.1.111.
- Warp new-tab directory → `$KGME_HOME` (`~/.warp/tab_configs/startup_config.toml`).
- Delete the restore-test file left in `~/Downloads`; delete `~/Downloads/kgme-restore-test/` if present.
- Friction log: first real entries. Cockpit wishlist: keep adding.
- `docs/roadmap.md` (Cowork, 2026-09-12) was untracked until the 2026-09-14 commit; now in git.

## Corrections to date
Eight entries in `corrections.md`, all Cowork's, all caught before harm: timezone; report frontmatter; id collision; Finance scope error; "copied library" inference; ledger contradiction; sudo-in-handoff; Time-Machine gate on a Backblaze machine (0024).

## Deferred on purpose
Ollama models and embeddings · Playwright / browser worker · Telegram · Groq · path renaming outside Automate · scheduling of any job · live ingestion of vendor streams, in-app approvals, `/btw` lane, dispatch, VS Code follow (Phase 2) — until Loop 0 passes or the friction log demands them.
