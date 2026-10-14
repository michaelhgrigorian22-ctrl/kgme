---
id: 20261013T235600
type: note
created: 2026-10-13T23:56:00-07:00
modified: 2026-10-13T23:56:00-07:00
status: active
tier: 3
source: inferred
author: cowork
sources:
  - https://github.com/mattpocock/skills
  - https://github.com/affaan-m/ECC
  - https://github.com/public-apis/public-apis
  - https://github.com/JustVugg/colibri
tags: [toolbox, review-loop, dream-job, workers, router]
---

# External repos reviewed for KGME, 2026-10-13

Michou asked which of four repos are worth borrowing from as the goals get loftier. Cowork cloned each (shallow, 2026-10-13) and read the files named below; nothing was installed. Every borrow listed here is a proposal: it lands only through a handoff, and any file or package that enters the tree gets an ADR-020 toolbox row once HANDOFF-0044 is adopted.

| Repo | What it is | Licence · last commit · clone size | Verdict |
|---|---|---|---|
| mattpocock/skills | 27 small skills for coding agents, "an alternative to process-owning frameworks" | MIT · 2026-10-09 · 2.2 MB | **Borrow five files.** Highest signal of the four. |
| affaan-m/ECC | Agent harness OS: 71 agents, 311 skills, 97 command shims, hooks, memory, security scans, 277k stars | MIT · 2026-10-11 · 110 MB | **Never install. Borrow four ideas.** |
| public-apis/public-apis | Directory of free APIs by category, 486k stars | MIT · 2026-10-13 · 0.9 MB | **Directory, not a source.** Pick by egress host, not by listing. |
| JustVugg/colibri | Pure-C MoE inference that streams routed experts from SSD; GLM-5.2 744B on a laptop | Apache-2.0 · 2026-10-06 · 44 MB | **Concept only.** Below our hardware floor. |

## mattpocock/skills

The philosophy is KGME's: small composable skills, feedback loops over process, and the author's own warning that frameworks like GSD, BMAD and Spec-Kit "take away your control and make bugs in the process hard to resolve." Five pieces earn a place.

**`productivity/grilling`** is the interview primitive: map a plan as a design tree, ask the whole frontier of answerable questions in one round with a recommended answer attached to each, recompute the frontier after the answers, stop when nothing is left silently assumed. This is how a proposal should be interrogated before adoption. First target: HANDOFF-0043 (`kgme review --loop`), before it moves out of `proposed/`. Cowork already has a `grill-me` skill in this session; the primitive is what to vendor into the repo so Claude Code and Codex can run it too.

**`engineering/retro`** is the rubric for the dream job. It reads a session's primary sources and looks for seven classes of improvement: navigation pointers, automated checks that would have caught the mistake, coding standards (with the rule that a mechanical violation gets a deterministic check, never a prose rule), oversized steering files, tool economy, no-op instructions, and missing information access. Its reference section carries one idea KGME should adopt outright: the implementation agent has the most context pressure and the review agent the least, so standards are enforced in review, not in `CLAUDE.md`. KGME's version reads `logs/ledger/` plus `docs/audit/` plus the dispositions in `logs/scratch/`, and writes its candidates as a proposal in `docs/handoff/proposed/`.

**`engineering/diagnosing-bugs`** Phase 1 is the discipline the three attrition halts (0032 F1, 0040 F8, 0033 F1) lacked: before any hypothesis, name one command that goes red on this exact symptom, deterministic, seconds, agent-runnable, and show it having run once. The reader's two-cycle rule says what happens after two failed patches; this says what a patch cycle must start with. One line for `docs/readers/review-loop.md`: a fix cycle's disposition names the red-capable command for each blocking finding before the patch, or states that none exists, which is itself a finding.

**`engineering/pr`** contributes a three-line "Merge Danger" block: door (one-way or two-way), blast radius (one word), ramifications. Worth adding to the handoff template as advisory body text so every handoff says how reversible it is. Schema v1.x treats unknown fields as advisory, so no bump.

**`misc/git-guardrails-claude-code`** is a 40-line PreToolUse script that blocks `git push`, `git reset --hard`, `git clean -f`, `git branch -D`, `git checkout .` and `git restore .`. KGME's guard today denies `git push --force*` only (`.claude/settings.json` line 43); the other four destructive commands rely on the rule in `CLAUDE.md`. The retro rubric's own test applies: mechanical violation, deterministic check. Fold into the guard as deny rules (preferred, no new script) with canary rows, under the 0042 guard work or its own small handoff.

Also noted, not for now: `in-progress/loop-me` gives Phase 3 workers a vocabulary (trigger, checkpoint, push right, brief): defer the human checkpoint as far as it will go, then present a decision-ready brief, never the raw output. `in-progress/claude-handoff` launches a background agent with `claude --bg --name`; verify the flag exists in the installed CLI before 0043's runner assumes it. KGME's own handoff documents are stronger than the repo's `handoff` skill; skip it.

How to take the files: vendor the SKILL.md files by pathspec under `.claude/skills/<name>/` with the MIT notice, not the plugin (`claude plugin install mattpocock-skills@claude-plugins-official` drops 27 skill descriptions into every session's context and auto-updates outside the repo's control, which is the global-settings failure of 0032 in a new coat). Each vendored file is a toolbox row: name, purpose, URL, licence, pinned commit and sha256, egress none.

## affaan-m/ECC

Everything KGME's charter decided against, at scale: 311 skills, hooks as inline `node -e` blobs in `hooks.json`, a global install under `~/.claude`, a `SOUL.md`. The repo is 110 MB and moves fast (2.2.3 on 2026-10-01). Do not install it, as a plugin or otherwise. Four ideas survive the reading.

**The instinct model (`skills/continuous-learning-v2`)** is the "dreaming" pipeline built out. Hooks on PreToolUse and PostToolUse append to `observations.jsonl`; a background observer (Haiku) turns corrections, error resolutions and repeated workflows into atomic instincts, YAML with `trigger`, `confidence` 0.3–0.9, `domain`, `evidence`, and `scope` project or global; `/evolve` clusters instincts into skills, commands or agents; an instinct seen in two projects promotes to global. KGME has the first half already: `logs/ledger/` is `observations.jsonl` with a schema, redaction and git history. What is missing is the observer and the promotion gate. KGME's shape: a dream job reads the week's ledger, audits and dispositions and writes instinct notes to `memory/agent/` (`type: note`, `source: inferred`, `sources` naming the ledger ids, a `confidence` tag), and promotion into readers or `CLAUDE.md` is a proposed handoff Michou adopts. Two differences are deliberate: ECC stores instincts outside the repo in `~/.local/share/ecc-homunculus/projects/<hash>/`, and its observer captures full prompts and tool calls, which in KGME terms is a Tier 1 leak path; the ledger's 200-character redacted summaries are the right input.

**Hook integrity sidecar (`hooks/hooks.metadata.json`)** carries a stable id and a fingerprint (matcher plus command) per hook entry, and CI fails when the sidecar and `hooks.json` drift. The canary matrix already digests the whole settings file into intents (0032); a per-hook fingerprint names which hook changed rather than that something did. Small addition to the canary, when it is next touched.

**Strategic compact and PreCompact** (`skills/strategic-compact`, `hooks/memory-persistence`): a PreToolUse script reads the transcript's `usage` record to compute true context size and suggests `/compact` at phase boundaries; a PreCompact hook saves state first. For 0043 this matters: an unattended loop that auto-compacts mid-fix is a fresh attrition cause. A PreCompact hook that appends a ledger `note` (context size, phase) costs one line in the 0028 hook pair and gives the cockpit a context-pressure signal per run.

**The minimum-bar checklist (`the-security-guide.md`)** is a useful audit of where KGME stands. Met: log tool calls and approvals (ledger), restrict reads from secret paths (deny rules), approval for unsandboxed shell and off-repo writes (ask mode), narrow disposable memory (tiers), reviewer without network (Codex read-only). Partly met: separate identities (the agents run as Michou), sandboxing (a worktree is separation, not isolation), scanning hooks and skills as supply-chain artifacts (0044 toolbox, once adopted). Not met, and the one that goes into 0043: a dead-man switch. The guide's shape: the supervisor starts the task, the task writes a heartbeat every 30 seconds, the supervisor kills the process group (not the parent) when the heartbeat stalls, and the stalled run is quarantined for review. `--max-minutes` is a budget, not a kill path; the loop needs both. Also from the guide, a sentence for ADR-016: "recursive confidence is not approval," which is the merge-stays-manual ruling in four words.

## public-apis/public-apis

A directory to search, never a source to trust. The list has drifted toward submissions that read like ads (hosted-on-vercel lookups, "with sourced data" wrappers, a sponsored APILayer block at the top), and the two no-key sources a daily brief would reach for first, Open-Meteo and SEC EDGAR's `data.sec.gov`, are not in it at all. Still useful for discovering a category.

For `kgme brief` (0034) and Phase 3 workers, the shortlist is first-party and keyless where possible: FRED (`api.stlouisfed.org`, free key), Treasury FiscalData (`api.fiscaldata.treasury.gov`, no key), BLS (`api.bls.gov`, v1 no key), Federal Register (`federalregister.gov`, no key), USAspending (`api.usaspending.gov`, no key), Nager.Date public holidays (`date.nager.at`, no key), Open-Meteo (`api.open-meteo.com`, no key), SEC EDGAR (`data.sec.gov`, no key, User-Agent header required), Crossref (`api.crossref.org`, no key) for thesis sources. Each one adopted becomes a toolbox row with its egress host, and the egress allowlist for the worker that calls it names that host and nothing else.

One tier point that the data policy does not yet state: a brief that queries market data by the tickers Michou holds tells the provider what he holds. Ticker-level requests for his own book are a Tier 1 disclosure even when the response is public data. Mitigation belongs in the brief's design, not the API's: query a sector universe or a watchlist that is a superset of the book, or pull bulk end-of-day files and filter locally. Record as an ADR-002 amendment alongside the declassification mapping already on the open list.

## JustVugg/colibri

Shared weights stay in RAM; the routed experts of a mixture-of-experts model live on SSD and are read when the router selects them, through a per-layer LRU cache and a pinned hot set learned from the user's own work. Numbers from the README: GLM-5.2 needs 16 GB minimum, 24 GB as measured, and decodes at 0.05–0.1 tokens per second cold on a 25 GB laptop, which the authors call "the honest floor"; 1.83 tok/s on a 128 GB CPU-only box; 9 tok/s only with every expert resident on six RTX 5090s. OLMoE runs at 22 tok/s. The M4 Pro with 24 GB sits at the floor, so this is not a Phase 2 provider. The transferable idea is the cache: the system learns which experts the work actually uses and pins them. Router v0's version is the same discipline at model granularity: log which local model served which job class, measure, and pin the hot set in `kgme.toml` rather than choosing models up front. Licence note for the toolbox if it ever matters: the engine is Apache-2.0 but each model keeps its own licence (GLM-5.2 MIT, Qwen-Image-2.1 non-commercial).

## What this seeds, in order

Nothing here jumps the queue. 0033's rebuild closes first, then 0034, 0037, 0042.

1. **Review-loop reader, next edit** (with 0033's close or the next reader touch): the red-capable-command line from `diagnosing-bugs`.
2. **0043 amendments before adoption**: dead-man switch (heartbeat plus process-group kill, stalled runs quarantined), PreCompact ledger note, and a grilling pass on the proposal itself.
3. **Guard**: deny rules for `git reset --hard`, `git clean -f`, `git branch -D`, `git checkout .`, `git restore .` with canary rows; attach to the 0042 guard handoff or a small one of its own.
4. **0044 toolbox, first rows**: the vendored skills (grilling, retro, diagnosing-bugs, pr) and the brief's data sources with egress hosts.
5. **Handoff template**: the Merge Danger block as advisory body text.
6. **Dream job**, a new proposal after 0043 and the Phase 3 heartbeat: ledger plus audits plus dispositions in, instinct notes and a proposed handoff out, retro rubric as the prompt, Codex read-only as the first dreamer. Number to be assigned when drafted; 0041–0044 are taken.
7. **ADR-002 amendment**: ticker-level requests as Tier 1 disclosure; declassification mapping.
