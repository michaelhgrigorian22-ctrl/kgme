---
id: HANDOFF-0077
type: handoff
created: 2026-11-24T14:15:00-08:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0073]
---

# Proposal 0077 — Reviewer tiers chosen by path, a `diff` data class, and a replay eval to pick the models

## Why
- **The reviewer has no home.** Michou's ChatGPT subscription lapsed on 2026-11-23, so `kgme review`'s Codex login is gone.
- **A new catalog with uncertain terms.** He now has a Nous plan, with GPT, Gemini, Kimi, DeepSeek and others. Nous Portal's privacy policy allows prompts to be retained and disclosed to providers, including for training.
- **Michou's ruling of 2026-11-24.** KGME content stays on Anthropic. Critical reviews go to an OpenAI API key. Standard reviews and cheap workers may use Nous, but only under a new `diff` data class: the diff under review and its one handoff, nothing else. Tier 1 is for local models only, ever.

## What
1. **The `diff` data class.** `kgme.toml [providers]` gains `nous = "diff"`, and the schema learns the class: a `diff` provider receives only the staged diff (or patch) and the text of the handoff under review. No other file, no `docs/` beyond that handoff, nothing from `memory/` or `logs/`. The review launcher builds the reviewer's input itself and refuses to hand a `diff` provider a workspace or a file path.
2. **Tiers chosen by code.** `kgme review` picks the tier from the paths the diff touches, never from a model's judgment:
   - **critical:** `kgme/hooks/`, `kgme/hermes_fence*`, `control/`, `roles/`, `kgme/session*`, `kgme/approve.py`, `.claude/`;
   - **standard:** everything else under `kgme/`, `jobs/` or `tests/`;
   - **light:** docs only.
   
   `kgme.toml [models]` names a reviewer per tier. A diff that touches any critical path is critical.
3. **The routes.** Critical goes to Codex on an OpenAI API key (`provider openai-api`, class `tier2`, under API terms). Standard goes to a Nous model through an OpenAI-compatible endpoint, under the `diff` class. Light runs lint only, unless the handoff asks for more.
4. **The replay eval.** Before choosing the standard reviewer, replay 30 past reviews from `docs/audit/`. Take the ones with blocking findings that held up, plus clean PASSes, and run each candidate model on the same diff and handoff. For each model, score:
   - recall of the real blocking findings;
   - false blockers;
   - cost per review.
   
   The candidates are at least one GPT, one Gemini, one Kimi and one DeepSeek model from the Nous catalog. Choose the cheapest model whose recall on real blockers is within 10% of the critical reviewer's. Write the results to `docs/audit/`.
5. **The `audit.reviewer` role.** Declare it in the registry with a rubric for each tier, per `kgme-agent-architect`.

## Acceptance test (under five minutes)
- A diff touching `kgme/hooks/guard.py` routes as critical, and one touching only `kgme/brief.py` routes as standard.
- A `diff`-class reviewer's input holds exactly the diff and the handoff, which a test checks byte for byte.
- The replay report exists, and names the chosen model with its scores.

## Needs from Michou
- An OpenAI API key for Codex: `codex login --with-api-key`. It lives in the vault, never in the repo.
- Adoption after 0073.
