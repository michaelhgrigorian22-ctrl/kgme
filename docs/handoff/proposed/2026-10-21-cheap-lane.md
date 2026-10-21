---
id: HANDOFF-0053
type: handoff
created: 2026-10-21T01:20:00-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0045, HANDOFF-0047]
plan_ref: PLAN-PHASE-1 step 7d
---

# Handoff 0053 (proposed) — The cheap lane: Claude Code on an Ollama cloud model grinds a red command to green in a code-only export, and its fix comes back as a diff through the normal review

## Why
Michou, 2026-10-21: he wants to run "the new deepseek flash 4.1" through Ollama inside Claude Code "to cheapen some of the debugging we do". DeepSeek-V4.1-Flash is a large mixture-of-experts model; Ollama serves it only from its cloud (`deepseek-v4.1-flash:1017-cloud`), so it runs on neither the MacBook nor the planned 64 GB mini, and every token the session reads leaves the machine for Ollama's servers (US, sometimes Europe; Ollama's policy: prompts not logged, not trained on, zero retention required of its hosts). Ollama speaks the Anthropic Messages API (v0.14+), so Claude Code, its hooks and the guard run unchanged with only the model swapped. **Michou's ruling, 2026-10-21: code only.** The session may see code and documents (`kgme/`, `jobs/`, `tests/`, `control/`, `docs/`, the top-level files); never `memory/`, `logs/`, or a Tier 1 path. STATUS deferred Ollama "until Loop 0 passes or the friction log demands them"; this is Michou's demand, scoped to cloud models for code. Local models stay deferred to the mini (Phase 3).

## What
1. **Providers carry a data class.** `kgme.toml [providers]` (a human path; a diff Michou applies): `anthropic = "tier2"`, `openai = "tier2"`, `ollama-cloud = "code"`, and later `ollama-local = "tier1"`. `[models] cheap = "deepseek-v4.1-flash:1017-cloud"`, provider `ollama-cloud`. A model whose provider's class is `code` can be launched only through item 2; the launcher refuses any other route.
2. **`kgme session work --model cheap --red "<command>"`** (HANDOFF-0047's launcher). For a `code` provider it:
   - exports `HEAD` minus `memory/` and `logs/` (`git archive` with excluding pathspecs) into `~/Projects/KGME/work/cheap-<run>/`, initialised as its own one-commit repository, so no object store holding `memory/` is reachable and the fix is a plain `git diff`. If tests need `memory/templates/` (templates, no personal content), the export adds it and the report names it; nothing else under `memory/`;
   - starts `claude` in the export with `ANTHROPIC_BASE_URL` at the local Ollama server, every model slot Claude Code uses (main, background, subagent) pinned to the cheap model (variable names checked against Claude Code's docs at build time), `--max-turns` from `[sessions]` (Claude Code's `--max-budget-usd` prices Anthropic models, so it is not the cap here; Ollama's plan credits are);
   - passes a settings file that keeps the main checkout's guard and ledger hooks by absolute path, with the ledger root pinned to the main checkout by the launcher (the export's own `.git` must not become the ledger's home); `Read`/`Edit` deny and the sandbox's read deny for Bash on `~/Projects/KGME/brain`, `~/Projects/KGME/design`, `~/Projects/Finance` and every `tier1_paths` root; no Bash network;
   - prompt: make `<command>` exit 0 without editing the test it names; stop on green, on the turn cap, or when a fix needs a file outside the export.
3. **The fix comes home as a diff, never a commit.** On exit the launcher writes `logs/scratch/cheap/<run>/fix.patch` and the red command's final output. The builder (Claude Code at its usual model) or the loop applies it in the real checkout, runs `make check`, and `kgme review` judges it as any diff; the cheap model never touches the main checkout, `main`, or a push.
4. **Ledger.** Start note: level, provider, model, export tree hash, denied roots, red command. End note: exit reason, turns, patch sha256, red command's final status.
5. **Not this route.** Ollama's Claude Desktop integration ("Apps → Connect Claude") is not used: it swaps the models of the whole desktop app, Cowork included, until disconnected. `ollama launch claude` is not used either: the launcher owns the environment so the ledger records it.
6. **Canary cells** (agent tier): asked to read `memory/inbox/friction-log.md` by its absolute path in the brain checkout, the cheap session is refused at the Read-deny layer and, through Bash, at the sandbox layer; `git log --all -- memory` in the export finds nothing; a Bash network call is refused; launching `--model cheap` without `--red` or outside the launcher is refused.

## Outputs
`kgme/session.py` (the `code` route), `kgme/cheap.py` (export, patch), `control/policy/sessions/cheap.json` (human path: a diff Michou applies), `kgme.toml` (`[providers]`, `[models] cheap`: a diff), `tests/test_cheap.py`, canary rows, a reader section (proposed: `docs/readers/sessions.md`, as a diff).

## Acceptance test (under fifteen minutes)
A fixture with one failing test: `kgme session work --model cheap --red "uv run --frozen pytest tests/fixtures/cheap/test_toy.py"` exports, runs, and leaves `fix.patch`; applied in a temporary worktree of the real checkout, `make check` passes. The export contains no `memory/` (bar templates if named) or `logs/`, and no history of either. Every canary cell is refused at its named layer. The start and end notes are in the main checkout's ledger.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one launcher route, one settings file, two `kgme.toml` tables, a folder under `work/`. `git revert`; deleting `[models] cheap` turns the lane off.

## Needs from Michou
Adoption after 0047. Ollama installed (pinned via Homebrew, v0.15 or later), an Ollama account signed in by him (`ollama signin`; agents never handle passwords), and a plan that serves the model: Pro is 20 USD a month with 60 USD of usage credits; DeepSeek-V4.1-Flash reached Max and Team accounts first, so check it on Pro before paying. Applying the `kgme.toml` and `cheap.json` diffs.

## Report
`docs/audit/2026-10-DD-cheap-lane.md`, named in `report:` on closing. Commit `session: the cheap lane, code only, fixes as diffs (HANDOFF-0053)`.
