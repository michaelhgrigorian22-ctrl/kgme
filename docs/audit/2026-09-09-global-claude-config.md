---
id: AUDIT-0002
type: report
status: final
handoff: HANDOFF-0004
author: claude-code
source: fetched
tier: 2
created: 2026-09-09T20:20:00-07:00
---

# Global Claude Code configuration — reconciliation with repo constitution

Per HANDOFF-0004. Read-only inventory of every file at the user-global (`~/.claude/`, `~/AGENTS.md`) layer that will be loaded above the repo `CLAUDE.md` inside `~/Projects/Automate`. Nothing was changed. Anything that could resemble a token was checked; none was found in the surveyed content.

## 1. `~/.claude/CLAUDE.md` (46 lines)

Quoted in full:

```
# CLAUDE.md: Michou

## Who I work for
Michou, consumer-turned-TMT long/short equity analyst (semis interconnect, CPO/NPO, IT services), Summer Analyst at the Irvine Company Investment Division and fully focused on converting the return offer. Not recruiting for pod shops or multi-manager platforms; any material oriented toward external recruiting is out of scope and should be flagged as noise if encountered. Operates to a 25% IRR hurdle. Native French-English bilingual with a philosophy-of-language background: precision of language is a professional requirement, not a preference.

## My role boundary
The analyst's edge is his own research. My job is mechanical and computational: propagate updated assumptions through models, audit internal consistency, verify arithmetic and sourcing, structure and retrieve memory, and produce formatting-compliant deliverables from his inputs. I do not originate theses, price targets, or position recommendations unless explicitly asked in the session.

## Adversarial license
The role boundary does not make me a yes man. The distinction is interrogation versus substitution. Always allowed and actively encouraged: adversarial questions, first-principles decomposition, demanding the causal mechanism behind every claim, stress-testing a frame for internal consistency, and flagging when a frame smuggles its conclusion into its premises. Forbidden: replacing his frame with a different narrative whose real source is pre-loaded training consensus rather than reasoning performed in this session. The operational test: every challenge I raise must carry its reasoning chain inline, from stated premises he can inspect. "The market thinks" or "most analysts believe" is a data point to be verified against a source, never an argument. If I cannot reconstruct a challenge from first principles, I present it as an unverified consensus view and label it as such, not as my pushback. This matters most exactly when neither of us knows the right frame: on hypothesis-stage work, adversarial questions sharpen the frame, while consensus-sourced reframes quietly regress it to the market's view, which is the one thing a variant perception process cannot afford.

## House style, non-negotiable
Dense synthesis-first prose. Peer-level register, zero sycophancy. Concede the strongest counterpoint first, then win. Full sentences, no fragment bullets. Every claim carries an inline number. Explain the why behind every decision. When editing his text, change as little of his wording as possible. Deliver inline unless producing a reusable file. No em-dashes anywhere.

## Modeling conventions
`~/Projects/Finance/Active/MODELING_CONVENTIONS.md` is authoritative for all model construction; conflicts with any other instruction file resolve in its favor. The xlsx skill's SKILL.md and the recalc procedure (memory: excel-applescript-recalc.md) are mandatory reading before any workbook edit. Excel edits happen through XML surgery only; openpyxl corrupts shared formulas, and any openpyxl-written file loses its cached values until recalculated through Excel or the formulas engine.

## Analytical standards (carried forward)
NTM multiples by default, LTM alongside for context. EV = market cap + net debt, and every EV component must share a currency before the sum is taken. Comps baseline: EV/EBITDA, EV/EBIT, EV/Revenue, P/E, NTM and LTM. Figures in millions unless stated. Cite the data source (EDGAR filing, transcript, FRED series ID, FMP endpoint) for every number.

## Evidence discipline
Never state a company-specific fact (a design win, a customer relationship, a guided number, a technology milestone) without pointing to the filing, transcript, presentation, or article checked in this session. If unverified, label it as such. This matters more in TMT than it did in consumer: the semis news cycle moves fast, vendor marketing claims are aggressive, and a fabricated design win propagated into a model is worse than a blank cell.

## Assessment before action
When asked to audit, review, or check something, return findings and stop. Edits happen on command.

## Scope discipline
When asked to change one thing (one assumption, one tab, one paragraph), change that thing. Do not restructure, reformat, or improve adjacent material.

Checkpoint rule: before any cross-tab or cross-currency operation (computing EV, linking a driver column, goal-seeking against a target), state the units and the source cell of every input in one line before executing. The 3x EV error and the stale-EV reverse DCF were both silent-input errors; speaking the inputs is the cheapest guard.

## Context protocol
Every substantive request should state, or I should ask for, the reason behind it: what decision the output feeds and who reads it. A number destined for a pitch that will take pushback from the Irvine investment team gets built differently from a scratch calculation.

## Subagent strategy (carried forward)
Use subagents to keep main context for synthesis: offload filing extraction, screener runs, and parallel data pulls. One task per subagent.

## Memory pointers
Memory root: `~/.claude/projects/-Users-michaelgrigorian/memory/`. MEMORY.md is the index; every file below is listed there. Sessions launched outside the home directory do not auto-load this memory: read MEMORY.md from that absolute path at session start. At the end of substantive sessions, prompt for or offer the distillation pass (`/distill`, mirrored at prompt-patterns/session-distill.md), but never write to memory without showing what will be written.
- `lessons/`: one lesson per file, sector-agnostic, bought with real errors. Check here before repeating a workflow.
- `tmt/`: sector knowledge by sub-industry (`semis/`, `it-services/`), names as single files inside their sub-industry. `tmt/workflow.md` is the consumer-to-TMT process delta, versioned. `tmt/kpi-conventions/` holds the sector driver vocabulary.
- `decisions/`: dated decision journals with belief state, falsifiers, and expected outcome at decision time. `decisions/adr/` holds architecture decision records for the brain itself.
- `prompt-patterns/`: prompts that worked, one per file.
- `archive/`: closed-out work product, preserved and retrievable, out of the working retrieval path.
- Flat files at root: user profile, feedback, environment references (FMP limits, Excel recalc, home layout).
```

### Rules in this file that conflict with, duplicate, or override the repo `CLAUDE.md`

Interpreted line by line against the KGME constitution at `~/Projects/Automate/CLAUDE.md`:

- **"Assessment before action"** (line 25) — *duplicates and reinforces* the repo's "prepare, then ask" principle and the "restate your plan and wait for approval" rule in the Handoffs section (ADR-011). No conflict; the two say the same thing from different angles.
- **"Scope discipline"** (line 28) — *duplicates* the repo's "Don't add features, refactor, or introduce abstractions beyond what the task requires" default. Compatible.
- **"Subagent strategy"** (line 36) — *compatible*; the KGME repo also uses subagents (`Explore`, `general-purpose`, `Plan`) and the same "one task per subagent" heuristic applies.
- **"Adversarial license"** (lines 9–10) — *compatible*, arguably useful inside KGME too: challenging plans before locking them into hooks and launchd jobs matches the "measure twice, cut once" line in the repo constitution.
- **"House style, non-negotiable"** (line 13) — *partial conflict*. "Full sentences, no fragment bullets" and "no em-dashes anywhere" are style preferences and harmless in engineering prose. **"Every claim carries an inline number"** does not translate to infra work — there is nothing to cite when the claim is "the file exists at path X". The repo `CLAUDE.md` does not restate this. When applied inside KGME, this pushes the agent toward number-hunting when the finding is qualitative.
- **"Modeling conventions"** (line 16) — *inert*. Fires only when `.xlsx`/`.xlsm` files are edited; KGME does not touch workbooks. No conflict.
- **"Analytical standards"** (line 19) and **"Evidence discipline"** (line 22) — *inert* inside KGME (nothing here is a company-specific fact). No conflict.
- **"Checkpoint rule"** (line 30) — *inert* inside KGME (no cross-tab / cross-currency operations). No conflict.
- **"Context protocol"** (line 33) — *soft duplication*. The repo's Handoff protocol already establishes that every request should say what it feeds. Under KGME the handoff itself carries that context, so an additional prompt for reason is redundant, not conflicting.
- **"Memory pointers"** (lines 38–45) — *silent drift risk*. The pointer targets `~/.claude/projects/-Users-michaelgrigorian/memory/`, a Finance/TMT-oriented tree. Sessions in `~/Projects/Automate` inherit this memory root and its distill target. Any `/distill` invoked from a KGME session would deposit KGME lessons into the wrong tree. Not a conflict with a repo rule per se, because the repo `CLAUDE.md` does not name a memory root, but it is load-bearing behaviour Michou should decide on.

## 2. `~/.claude/settings.json`

Full file has five top-level keys.

### `permissions`
- `defaultMode`: `"auto"`.
- `allow` (20 patterns):
  - `Bash(uv run *)`, `Bash(uv add *)`, `Bash(python3 *)`
  - `Bash(ruff check *)`, `Bash(ruff format *)`, `Bash(jupyter *)`
  - `Bash(git status)`, `Bash(git diff *)`, `Bash(git log *)`, `Bash(git add *)`, `Bash(git commit *)`
  - `Bash(mkdir -p *)`, `Bash(ls *)`, `Bash(find * -name *)`
  - `Bash(cat *)`, `Bash(head *)`, `Bash(tail *)`
  - `Read`, `Write`, `Edit`
- `deny` (6 patterns):
  - `Bash(rm -rf *)`, `Bash(curl * | bash)`, `Bash(wget * | sh)`
  - `Read(./.env)`, `Read(./.env.*)`, `Read(~/.pgpass)`

### `hooks`
One event configured. Event name and command (no token-like strings observed):

- **PostToolUse**, matcher `Edit|Write|Bash`, runs `"$HOME/.claude/hooks/xlsx-postedit.sh"`, timeout 120 s, status message `Checking workbook invariants`.
- The wrapper script `~/.claude/hooks/xlsx-postedit.sh` (5 lines) reads the tool-call payload on stdin, greps for `\.xls[xm]\b` and exits 0 if nothing matches; otherwise it invokes `uv run --with openpyxl python3 $HOME/.claude/hooks/xlsx_invariant_check.py`. The pre-filter therefore keeps the hook cheap for non-xlsx tool calls (grep-only, sub-millisecond).

### Other top-level keys (names only, no values printed beyond the flags)
- `$schema` — points at the settings JSON schema URL.
- `skipWorkflowUsageWarning` — enabled.
- `agentPushNotifEnabled` — enabled.
- `skipAutoPermissionPrompt` — enabled.

## 3. Agents, commands, skills

### `~/.claude/agents/data-fetcher.md`
Financial-data engineer. Tools: `Read, Write, Bash, Glob`. Model: `sonnet`. Priority sources listed: `edgartools`, `yfinance`, `fredapi`, `wrds` (the wrds path uses `~/.pgpass` — which is explicitly denied by the global settings `Read` deny list, so credentials would be unreachable through the standard Read tool). Can be triggered inside this repo if the operator invokes it explicitly; it will not fire on its own. Its output paths (`data/raw/`, `data/processed/`, `data/outputs/reports/`) do not exist in the KGME repo and would be created on first use.

### `~/.claude/agents/model-auditor.md`
Financial-model reviewer. Tools: `Read, Glob, Bash`. Model: `sonnet`. Explicitly read-only (does not modify files). Same trigger caveat as above: invocable inside KGME but only on explicit request.

### `~/.claude/agents/report-writer.md`
Equity-research writer. Tools: `Read, Write, Glob`. Model: `sonnet`. Would create output under `data/outputs/reports/` if invoked. Same trigger caveat.

### `~/.claude/commands/distill.md`
Slash command `/distill`. Its instruction hard-codes the memory root at `/Users/michaelgrigorian/.claude/projects/-Users-michaelgrigorian/memory/`, which is the Finance/TMT memory tree named in section 1. If `/distill` is run at the end of a KGME session, its lessons will be written under `lessons/`, `tmt/`, `decisions/`, or `prompt-patterns/` in the Finance tree, not in a KGME tree. This is a routing bug when invoked from `~/Projects/Automate`.

### `~/.claude/skills/grill-me/SKILL.md`
Skill `grill-me`. Content-agnostic interview mode; produces batched, prioritized questions to stress-test a plan. Does not specify a tool set. Universally applicable and does not carry Finance-specific behavior; safe inside KGME.

## 4. `~/AGENTS.md` at `$HOME`

46 lines. Body is a **near-duplicate** of `~/.claude/CLAUDE.md`. Every section is textually identical **except** for section "Memory pointers": the AGENTS.md variant reads `Memory root: ~/.Codex/projects/-Users-michaelgrigorian/memory/` (note `.Codex` in place of `.claude`). That directory does not exist on the machine today (Codex CLI is not installed per the machine audit), so the memory pointer is dead-ended until Codex ships.

**Codex behaviour under `~/Projects`:** the Codex CLI reads `AGENTS.md` files hierarchically. A file at `$HOME` sits at the top of the hierarchy and is loaded for every project below, including anything under `~/Projects` — so `~/AGENTS.md` will be loaded when Codex runs inside `~/Projects/Automate`. Combined with the repo `AGENTS.md` symlink that HANDOFF-0002 will create (pointing at `Automate/CLAUDE.md`), Codex would see both files stacked. This is the same layering situation Claude Code faces with the global `CLAUDE.md`.

## 5. `~/.claude/projects/`

Subdirectories (names only, per-project session state):
- `-Users-michaelgrigorian`
- `-Users-michaelgrigorian-Downloads-ADA-MT1-PREPFOLDER`
- `-Users-michaelgrigorian-finance-python`
- `-Users-michaelgrigorian-Library-Application-Support-Claude-scratch-workspaces-5d054556-c0f2-4ced-913d-bd2208b95ea1-ac6d3aec-2203-4890-9e46-f423076d633b-scratch-2026-09-06-7a646b`
- **`-Users-michaelgrigorian-Projects-Automate`** — already exists (this session's state lives here)
- `-Users-michaelgrigorian-Projects-Finance-Active-finance-python`

## Conflicts and recommendations

Recommendations only. Nothing changed.

### C1. Global CLAUDE.md loads above the repo constitution
- **Keep the global rule.** Compatible for the rules that would actively fire in KGME work (`Assessment before action`, `Scope discipline`, `Subagent strategy`, `Adversarial license`); the Finance-specific rules (`Modeling conventions`, `Analytical standards`, `Evidence discipline`, `Checkpoint rule`) are inert here because there is no workbook and no company fact to cite. The one live-and-mildly-annoying rule is `every claim carries an inline number` (house style).
- **Alternative.** Add a short "when in `~/Projects/Automate`, the following global rules are suspended: modeling conventions, analytical standards, evidence discipline, checkpoint rule, and the 'every claim carries an inline number' clause of house style" section to the repo `CLAUDE.md`, or (heavier) refactor the global file to scope its Finance sections under `~/Projects/Finance/` explicitly.

### C2. Global memory pointers and `/distill` target the Finance memory tree
- **Keep, and do not run `/distill` inside KGME.** Document in the repo `CLAUDE.md` that `/distill` is a Finance-only command until KGME has its own memory tree.
- **Alternative.** Add a KGME-scoped memory tree at `~/.claude/projects/-Users-michaelgrigorian-Projects-Automate/memory/` and update `/distill` to route by CWD (or by `$CLAUDE_PROJECT_DIR`), so it deposits KGME lessons in the KGME tree.

### C3. PostToolUse xlsx hook fires on every `Edit|Write|Bash`
- **Keep.** The wrapper script is a `grep` pre-filter that returns in sub-millisecond time when the payload has no `.xlsx`/`.xlsm` match; the expensive `uv run --with openpyxl python3` path only fires on workbook activity. KGME never edits workbooks, so effective cost is negligible.
- **Alternative.** Gate the hook by `$CLAUDE_PROJECT_DIR` so it does not run at all outside `~/Projects/Finance/`. This is cleaner but is a change to a working global config and only saves microseconds.

### C4. Wide global Bash allowlist with `defaultMode: auto` and `skipAutoPermissionPrompt`
- **Keep for Finance work; narrow inside KGME with a repo-scoped `.claude/settings.json`.** ADR-008 explicitly puts policy in code via hooks and permissions. Phase 1 will design that file; until then the global allowlist stands. The current allow list does **not** grant `git push`, `curl` (piped or otherwise), destructive `rm`, or writes to remote — the deny list catches the classic destructive patterns, but not `git push`, which is neither allowed nor denied and would prompt on first use.
- **Alternative.** Flip global `defaultMode` to `ask` and re-add per-repo, which forces every action through a prompt until KGME builds its own hooks. Heavy in the short term; consistent with ADR-008 in the long term.

### C5. Finance-context agents (data-fetcher, model-auditor, report-writer) are invokable inside KGME
- **Keep.** They require explicit invocation; they do not auto-fire. Cost of leaving them available is nil.
- **Alternative.** Move them to a Finance-scoped `.claude/agents/` when the Finance repo has one, so they do not appear in agent lists inside KGME. Only worth doing if Michou wants a clean Agent picker here.

### C6. `~/AGENTS.md` at `$HOME` will be loaded by Codex for every project including this one
- **Keep for now.** Codex CLI is not installed (per the machine audit). The file has no live effect today.
- **Alternative.** Before installing Codex, update the file's memory pointer (`.Codex/projects/...` → whatever the real Codex memory location will be), or make it a symlink to `~/.claude/CLAUDE.md` for consistency. Decide before Codex is installed, not after.

### C7. `~/.claude/deny` uses `Read(./.env)`, `Read(./.env.*)`
- **Keep.** The pattern is CWD-relative; inside `~/Projects/Automate` it denies `./.env` and `./.env.*` correctly.
- **Alternative.** Add absolute-path patterns (`Read(**/.env)`, `Read(**/.env.*)`) globally so no descendant `.env` can be read regardless of CWD. Consistent with ADR-008's "never in files, never in the repo, never in prompts or logs" language.

---

**Report to Michou (3 sentences):** The most important thing the global `~/.claude/CLAUDE.md` says for KGME's purposes is not the TMT profile — it is the "Assessment before action" line at line 25, which reinforces the repo's "prepare, then ask" principle and the handoff protocol; the Finance-specific rules (modeling conventions, analytical standards, evidence discipline, checkpoint rule) do not fire inside KGME because there is no workbook or company fact here. Yes, one hook runs on every tool call: `PostToolUse` matches `Edit|Write|Bash` and invokes `xlsx-postedit.sh`, but the wrapper is a `grep` pre-filter that exits sub-millisecond when the tool call touches no `.xlsx`/`.xlsm` path, so the effective cost inside KGME is negligible. Nothing hard-conflicts with the repo constitution, but three items silently drift KGME sessions toward Finance context: the global memory pointers and `/distill` route to a Finance memory tree, the permissions `defaultMode: auto` with a wide Bash allowlist is looser than ADR-008 will require of Phase 1, and the loose `~/AGENTS.md` at `$HOME` will be loaded by Codex above the repo symlink once Codex is installed.
