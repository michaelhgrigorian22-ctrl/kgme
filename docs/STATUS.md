---
id: STATUS
type: note
status: active
created: 2026-09-10T09:50:00-07:00
modified: 2026-10-16T14:20:00-07:00
author: cowork
source: stated
tier: 2
---

# KGME — current status (ADR-014)

The one place that says what is true *now*. Historical records are never edited; this file is. Last updated 2026-10-16 14:20 PDT by Cowork (HANDOFF-0049 Part A done, `f60f4b6`, AUDIT-0057 PASS at cycle 3; HANDOFF-0034 done 2026-10-15, `7cf034b`, AUDIT-0053; HANDOFF-0033 done 2026-10-14, AUDIT-0050).

## Phase
**Phase 0 — Prepare: complete as of 2026-09-11**, except the housekeeping list below. **Phase 1 — Loop 0 and the cockpit: open as of 2026-09-14.** Plan amended that evening after a four-model deliberation (AUDIT-0011); build order at `plans/phase-1-loop-0.md`. Done: HANDOFF-0025 packaging (AUDIT-0012), 0026 ledger (AUDIT-0013), 0027 permissions and 0028 hook pair (AUDIT-0014), 0029 `kgme review` (AUDIT-0016, reviewed by itself over five cycles), 0030 schema v1.3 and 0031 validator (AUDIT-0022), 0032 canary tests and worker manifests (AUDIT-0026, seven cycles, two overrides), 0040 `kgme sync` (AUDIT-0034, six cycles, one override: every commit is pushed by the backgrounded post-commit hook and the ledger is committed by `kgme sync`, one mode, one lock); ADR-019 accepted. 0033 `kgme clean` done 2026-10-14 (AUDIT-0050, eight cycles, two halts closed by Michou's overrides of 2026-10-13: the hold-and-restore design rejected and rebuilt by pathname with one final check per deletion; his ruling of 2026-10-14 puts a local process swapping repository directories during a clean run outside the threat model; report `audit/2026-10-08-loop-0.md`). 0034 `kgme brief` v1 done 2026-10-15 (AUDIT-0053, three cycles; Cowork's ruling as arbiter on F1 and F6 executed: one gated reader for every brief read and one failure boundary per run; payload verification shared with `kgme clean` as `ledger.read_payload`; due instants read in `kgme.toml` `[brief] timezone`). Loop 0's pair is built; the week of hand runs starts on this commit, and the first real brief waits for the seeded vault (0035). The cockpit design track (0036) runs in parallel under Cowork, Codex, and Michou; 0037 waits for its approval. Nothing runs unattended; the hooks run on every Claude Code tool call in the repository. **Loop 0 built 2026-10-15** (`kgme brief` v1, HANDOFF-0034, `7cf034b`): the week of hand runs starts on that commit. **The constitution changed 2026-10-16:** `CLAUDE.md` "How decisions are made" (ADR-023 accepted) governs every session.

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
| First three workers | daily brief and coursework→calendar named; the third waits for ten real friction entries (8 of 10 on 2026-10-16, captured from Michou's own words; HANDOFF-0050 makes capture by talking the route) | HANDOFF-0039 |
| Weekly review slot | **Decided 2026-09-14:** Sunday 18:00 PT | first held at Phase 1 exit (0039) |
| Working copy of finance-python | stays for now; delete later or not at all | — |
| `kgme` shell alias | **Done 2026-09-14:** `kgh` jumps to the repo; `kgme` is a shell function over `uv run --frozen --project` | HANDOFF-0025 |
| Review gate | **Built 2026-09-17; amended 2026-10-16 (ADR-023 accepted):** `kgme review` runs the loop from the ledger; a disputed or persistent blocking finding goes to the arbiter and the ruling is executed; a loop stops on measured non-convergence, a budget or a ruling outside the mandate. The coded three-cycle halt in `kgme/review.py` remains until HANDOFF-0043 replaces it; `kgme review rule` records rulings, `kgme review override` records Michou. | HANDOFF-0029, HANDOFF-0043 |
| Schema v1.2 | **Decided 2026-09-14:** validator covers `memory/` and `docs/`; repair by schema rule for append-only types, never by editing an ADR | HANDOFF-0030 |

## Proposals still open (`docs/handoff/proposed/`)
0011 path renaming — folded into the migration plan · 0012 `pmset` — deferred to end of observation window · **0025–0039 Phase 1 sequence (2026-09-14)**, adopted one by one in order; 0030 is for Cowork, 0035 for Michou, 0036 for Cowork and Michou. All others superseded, abandoned, or done.

**Next, in order (2026-10-16):** (1) **0049 Part B, Michou's:** with no session open, `kgh` then `control/move-home.sh` (moves the two checkouts into `~/Projects/KGME/` as `brain/` and `design/`, repairs the worktree, rebuilds `.venv`, runs `make check`); then `KGME_HOME`/`kgh`/`kgq` in `~/.zshrc`, the Codex profile's writable root, Warp's new-tab folder; re-add `~/Projects/KGME` in Cowork; skip the Obsidian step (0051 sets the vault). (2) 0050 capture by talking and drafted daily notes (unblocks 0035). (3) 0045 guard: destructive git, Outputs scoping, per-entry fingerprints, the guard's own files protected. (4) 0051 the atlas: Obsidian as a lens, regenerated on every commit (can run beside 0045). (5) 0047 session levels (ADR-022 proposed). (6) 0042 design-track registration. (7) 0037 cockpit v0, after the canvas is approved (0036). (8) 0043 `kgme review --loop`. (9) 0048 `kgme crew`. Then 0035 (seeded through capture), 0038, 0044, 0039 exit audit. Later: 0046 `kgme dream` (after 0043 and the Phase 3 heartbeat). Proposed decisions waiting for Michou: ADR-021 (Tier 1 disclosure by request; amends ADR-002), ADR-022 (session levels). Accepted 2026-10-16: ADR-023 outcome-governed loops. Reviews behind these: `memory/agent/2026-10-13-external-repos-review.md` (four repos) and the ui-ux-pro-max rubric (design track).

## Housekeeping (non-blocking)
- VS Code → Open Recent → clear the three dead `finance-python` entries (UI only).
- `brew doctor`: Command Line Tools 26.3 via System Settings → Software Update.
- Duplicate Claude Code install: `which -a claude`, remove the stale 2.1.111.
- Warp new-tab directory → `~/Projects/KGME/brain` after the move (`~/.warp/tab_configs/startup_config.toml`).
- Follow-up, cosmetic: `tests/test_brief_review.py` is 406 lines against ADR-015's ~300 (AUDIT-0053 F13); split by concern in a later diff, not the reviewed one.
- Delete the restore-test file left in `~/Downloads`; delete `~/Downloads/kgme-restore-test/` if present.
- Friction log: 8 of 10 (2026-10-16). Cockpit wishlist: keep adding, by capture once 0050 lands.
- `docs/roadmap.md` (Cowork, 2026-09-12) was untracked until the 2026-09-14 commit; now in git.

## Corrections to date
Eight entries in `corrections.md`, all Cowork's, all caught before harm: timezone; report frontmatter; id collision; Finance scope error; "copied library" inference; ledger contradiction; sudo-in-handoff; Time-Machine gate on a Backblaze machine (0024).

## Deferred on purpose
Ollama models and embeddings · Playwright / browser worker · Telegram · Groq · path renaming outside Automate · scheduling of any job · live ingestion of vendor streams, in-app approvals, `/btw` lane, dispatch, VS Code follow (Phase 2) — until Loop 0 passes or the friction log demands them.
