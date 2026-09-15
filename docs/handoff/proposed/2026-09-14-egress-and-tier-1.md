---
id: HANDOFF-0038
type: handoff
created: 2026-09-14T22:25:00-07:00
from: claude-code
to: claude-code
tier: 2
status: proposed
depends_on: HANDOFF-0032
plan_ref: PLAN-PHASE-1 step 13
---

# Handoff 0038 (proposed) — LuLu egress control, `age` for Tier 1, and the separate-user evaluation

## Why
ADR-013 §2 names two Phase 1 requirements the original plan omitted: a host egress tool and the Tier 1 boundary. Michou ruled 2026-09-14: LuLu, installed at the end of Phase 1 so it never blocks code; `age` encryption at rest for Tier 1 now; the separate macOS user evaluated and written up at Phase 1 exit, adopted unless it proves unworkable. This handoff discharges both requirements and fills the two network canary cells that 0032 reported as `advisory: layer missing`.

## What
1. `brew info --json=v2 --cask lulu`: record version and sha. `brew install --cask lulu`; `brew pin` is not available for casks, so record the version and note it in STATUS. LuLu's own installer requires Michou's approval in System Settings (a system extension); the agent stops and asks. No rule is created by the agent.
2. With Michou at the machine: one LuLu rule blocking outbound from `.venv/bin/python` to everything except `127.0.0.1`, as the per-worker rule for the Python job profile. Record the rule as text in the report; LuLu's rule file is not copied.
3. `brew info --json=v2 age`; `brew install age`; `brew pin age`. Write `docs/readers/tier-1-at-rest.md`: how the private repository's files are encrypted with `age` under Michou's key, decrypted only inside a local-model job with no network tools (ADR-013 §2, ADR-018 pattern B). Nothing under the private repository is touched (ADR-002); this is the procedure, written before the first Tier 1 note exists.
4. `docs/audit/…-tier-1-boundary-evaluation.md`: the separate macOS user evaluated on this machine: what it costs (second login, split VS Code and Obsidian workspaces, file ownership across users), what it buys (a boundary a same-user subprocess cannot cross by reading a path), a recommendation, and the question for Michou.
5. Re-run `make canary-agents`: the two network cells now report the `host` layer.

## Outputs
LuLu installed, one rule recorded, `age` installed and pinned, `docs/readers/tier-1-at-rest.md`, the evaluation audit, canary matrix re-run.

## Acceptance test
A canary destination (`http://127.0.0.1:9` and one external host) is blocked at the host level for the Python profile and the block is a `blocking` outcome in `logs/ledger-test/`; `age --version` matches the recorded pin; the evaluation audit ends with one recommendation and one question.

## Reviewer
Michou (system extension approval and the Tier 1 decision); Codex reviews the documents.

## Reversibility
`brew uninstall --cask lulu` (Michou removes the system extension in System Settings); `brew unpin age && brew uninstall age`. Documents by `git revert`.

## Needs from Michou
Present at the machine for the LuLu system-extension approval and the one rule. His ruling on the separate user after reading the evaluation.

## Report
`docs/audit/2026-1M-DD-egress-and-tier-1.md`. Set `status: done`, `completed:`. Commit `env: LuLu egress, age for Tier 1, boundary evaluation (HANDOFF-0038)`.
