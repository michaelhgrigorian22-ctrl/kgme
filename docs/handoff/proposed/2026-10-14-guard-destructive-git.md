---
id: HANDOFF-0045
type: handoff
created: 2026-10-14T00:25:00-07:00
from: cowork
to: claude-code
tier: 2
status: proposed
depends_on: [HANDOFF-0032]
plan_ref: PLAN-PHASE-1 step 7c
---

# Handoff 0045 (proposed) — Guard: destructive git denied by rule, writes scoped to a handoff's Outputs in loop mode, hooks fingerprinted one by one

## Why
The guard denies `git push --force*` and `git push -f*` (`.claude/settings.json`) and leaves `git reset --hard`, `git clean -f`, `git branch -D`, `git checkout .` and `git restore .` to a sentence in `CLAUDE.md`. The rule Michou adopted on 2026-10-14 from the `retro` rubric (`memory/agent/2026-10-13-external-repos-review.md`): a mechanical violation gets a deterministic check, never a prose rule. HANDOFF-0043 will run a builder with nobody watching, so before it two more things must be mechanical: a loop run may write only inside its handoff's `Outputs`, and when the settings digest changes the canary must say which hook or rule changed (ECC's `hooks.metadata.json`, one fingerprint per entry, is the pattern; the 0032 digest covers the whole file).

## What
1. **Deny rules** in `permissions.deny`, in the form the file already uses: `Bash(git push --force-with-lease*)`, `Bash(git reset --hard*)`, `Bash(git clean -f*)`, `Bash(git clean -d*)`, `Bash(git branch -D*)`, `Bash(git checkout .)`, `Bash(git checkout -- .)`, `Bash(git restore .)`, `Bash(git stash drop*)`, `Bash(git stash clear*)`. Plain `git commit` and `git push` stay allowed (`kgme sync`, HANDOFF-0040, depends on them). `kgme clean` (HANDOFF-0033) is untouched: it is not `git clean`. The same list goes into `tools/policy/profiles/codex-builder.toml` when HANDOFF-0042 lands (a line in that proposal's Needs).
2. **Outputs scoping in loop mode.** `tools/hooks/pre_tool_guard.sh` reads `KGME_LOOP_HANDOFF`, set by `kgme review --loop` (HANDOFF-0043) and absent otherwise. When set, the guard resolves the named handoff's `Outputs` paths plus `tests/` and `logs/scratch/` and refuses every write outside them as a `blocking` outcome with `ref` to the intent. Interactive sessions are unchanged. The handoff's `Outputs` section is parsed once per run into `logs/scratch/loop/<run>/outputs.txt` by the loop, so the guard reads a list, not prose.
3. **Per-entry fingerprints.** The canary's settings digest becomes a list: one sha256 per hook entry (matcher plus command) and per deny rule, carried in the canary intent's payload. The fast-tier test fails naming the entry that changed.
4. **Canary rows.** Fast tier: each new deny matches its fixture command; a settings fixture with one altered hook command fails naming that hook. Agent tier: the model is refused on each denied command and the refusal is a `blocking` outcome in `logs/ledger-test/`; under `KGME_LOOP_HANDOFF=<toy>` a write to `docs/charter.md` is refused and a write to the toy's `Outputs` path is allowed.

## Outputs
`.claude/settings.json`, `tools/hooks/pre_tool_guard.sh`, `kgme/canary.py` (digest list), `tests/policy/` (new cases), `tests/test_guard_loop.py`, a paragraph each in `docs/readers/review-loop.md` ("What the loop never does": the Outputs rule) and in the canary section of `docs/STATUS.md`.

## Acceptance test (under five minutes)
`make check` green with the new rows; `make canary-agents` shows each denied command refused with a ledger outcome; a session's `git commit` followed by `kgme sync`'s push succeeds (`git log origin/main -1` matches `main`); the altered-hook fixture fails the digest test and names the hook; the loop-mode fixture refuses the charter write and allows the Outputs write.

## Reviewer
Codex read-only under `kgme review`. The rules of 2026-10-13 and 2026-10-14 (two cycles; red command first) apply.

## Reversibility
Door: two-way. Blast radius: one settings file, one hook script, the canary. `git revert`; nothing outside the repo changes.

## Needs from Michou
Adoption. A yes or no on `git stash drop` and `git stash clear` (recommended: deny; a stash is the only copy of what it holds).

## Report
`docs/audit/2026-10-DD-guard-destructive-git.md`. Set `status: done`, `completed:`. Commit `guard: destructive git denied, Outputs scoping in loop mode, per-entry fingerprints (HANDOFF-0045)`.
