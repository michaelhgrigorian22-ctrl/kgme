---
id: STATUS
type: note
status: active
created: 2026-09-10T09:50:00-07:00
modified: 2026-10-08T19:35:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — current status (ADR-014)

The one place that says what is true *now*. Historical records are never edited; this file is. Last updated 2026-10-08 19:35 PDT by Claude Code (HANDOFF-0032 done, AUDIT-0026).

## Phase
**Phase 0 — Prepare: complete as of 2026-09-11**, except the housekeeping list below. **Phase 1 — Loop 0 and the cockpit: open as of 2026-09-14.** Plan amended that evening after a four-model deliberation (AUDIT-0011); build order at `plans/phase-1-loop-0.md`. Done: HANDOFF-0025 packaging (AUDIT-0012), 0026 ledger (AUDIT-0013), 0027 permissions and 0028 hook pair (AUDIT-0014), 0029 `kgme review` (AUDIT-0016, reviewed by itself over five cycles), 0030 schema v1.3 and 0031 validator (AUDIT-0022), 0032 canary tests and worker manifests (AUDIT-0026, seven cycles, two overrides); ADR-019 accepted. Next to adopt: 0040 `kgme sync` (step 7b, added by Cowork 2026-10-08), then 0033 `kgme clean`; their reviews run through `kgme review`. Nothing runs unattended; the hooks run on every Claude Code tool call in the repository.

## Gates before anything is scheduled (ADR-013 §6)
| Gate | State | Record |
|---|---|---|
| Completed backup + tested restore | **MET** 2026-09-11 — Backblaze (private key, 1-year history), restore hash-verified; private GitHub remote `michaelhgrigorian22-ctrl/kgme` in sync | AUDIT-0007, AUDIT-0009 |
| Charter accepted | **MET** 2026-09-11 — v0.2 accepted; v0.1 archived; four `[REVIEW]` refinements open, non-blocking | `charter.md` |
| Ledger durable and tracked | **MET** 2026-09-15 — ADR-019 accepted; `kgme/ledger.py` the one writer; `logs/ledger/2026-09.jsonl` tracked and holding real events since the hooks went live; `logs/trace/` untracked for read-only tool calls | HANDOFF-0026, AUDIT-0013 |
| Repo-scoped permissions + hooks | **MET** 2026-09-15 — `.claude/settings.json` in ask-mode with explicit allow and deny (0027); pre-tool guard and post-tool ledger hooks live on every call (0028). Interactive sessions: deny and prompt proven by Michou; background-job sessions keep deny and the hooks but not the prompt, carried into 0032's canary matrix | AUDIT-0014 |
| Canary tests per worker | **MET for the Phase 1 workers 2026-09-28** — fast tier (20 cells, manifests and guard) in `make check`; agent tier (`make canary-agents`, 10 live cells) run ten times 2026-09-20 to 2026-09-28, no cell `fail` since Michou's ruling of 2026-09-23 (project deny rules on human paths, guard rule 4). Residuals named cell by cell: four inconclusive cells where the worker made no call and so exercised no layer (Claude env in every run and tier1 in the last runs, the model declining on its own; Codex rm-rf and write-outside, Codex replying REFUSED without a command); Codex read cells advisory (no read boundary, deferred to 0038); both network cells advisory until LuLu (0038); every canary intent records the `~/.claude/settings.json` digest | AUDIT-0026; reviews AUDIT-0027 to AUDIT-0029 and the cycle that follows the override |

## Ground layer (done)
Firewall on · Homebrew 6.0.22 (pinned installer `8949852`, analytics off) · `gh` 2.100.0 pinned · `gh auth` over HTTPS via credential helper · Codex CLI 0.154.0 · shell aliases (`kgh`, `kgme-claude`, `kgme-codex`) and the `kgme` function · Python 3.13 via uv, PyYAML 6.0.3, ruff 0.16.7, pytest 9.1.1 pinned · git identity set · ADR-001…018 accepted · every handoff 0001–0023 done; 0024 abandoned as unnecessary.

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
| `kgme` shell alias | **Done 2026-09-14:** `kgh` jumps to the repo; `kgme` is a shell function over `uv run --frozen --project` | HANDOFF-0025 |
| Review gate | **Built 2026-09-17:** `kgme review` runs the loop from the ledger; halt when one root cause stands blocking three consecutive cycles or three survive a fix cycle; `kgme review rule` records the arbiter, `kgme review override` records Michou. First halt, override, and arbitration all happened on its own review | AUDIT-0016, `docs/readers/review-loop.md` |
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
