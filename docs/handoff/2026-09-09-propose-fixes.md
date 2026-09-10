---
id: HANDOFF-0003
type: handoff
created: 2026-09-09T20:20:00-07:00
from: cowork
to: claude-code
status: open
tier: 2
depends_on: HANDOFF-0002
---

# Handoff 0003 — Turn the audit into *proposed* fix handoffs (planning only)

Run only after HANDOFF-0002 is `done`. This handoff **changes nothing on the machine**. Its output is a set of proposals Michou will approve or reject in the morning. This is the "prepare, then ask" principle applied to setup itself.

## Input
`docs/audit/2026-09-09-machine-audit.md`, especially its **"Gaps and risks noticed"** section, read against `docs/plans/phase-0-prepare.md` §3 (fix-now list) and `docs/adr/ADR-008-secrets-and-policy.md`.

## Output
For each gap that the Phase 0 plan or ADR-008 says should be fixed, write **one** proposed handoff at
`docs/handoff/proposed/<today, local date YYYY-MM-DD>-<kebab-topic>.md` with frontmatter:

```
---
id: HANDOFF-00NN        # continue numbering from 0004
type: handoff
created: <ISO 8601 with offset>
from: claude-code
to: claude-code
status: proposed
tier: 2
depends_on: HANDOFF-0001
audit_ref: <the finding it addresses, quoted briefly>
---
```

Each proposal must contain, in this order: **Why** (the audit finding, one paragraph); **What** (the exact commands or steps, nothing hand-wavy); **Reversibility** (how to undo it, honestly — "cannot be undone" is an acceptable answer and must be stated); **Risks** (what could go wrong, what it touches); **Needs from Michou** (a password, a choice, a login — e.g. FileVault needs him present; git identity needs his name and email; a GitHub account is his to create). Keep each under 300 words. One outcome per proposal.

Likely candidates, *only if the audit shows them missing*: FileVault; Time Machine destination; Homebrew; `uv`; `gh`; git identity; SSH key for GitHub; renaming any path with spaces under `~/Projects`; a `pmset` change for the morning heartbeat; removing or documenting existing global `CLAUDE.md` / MCP config that would apply inside this repo. Do **not** propose anything the audit did not surface, and do not propose installing Playwright, Ollama models, or Chrome profiles — those are separate designed steps.

Then write `docs/audit/2026-09-09-fix-plan.md` (frontmatter: `type: report`, `handoff: HANDOFF-0003`) listing every proposal in the order you recommend running them, with a one-line rationale for the order, and a note of anything in the audit you judged **not** worth fixing and why.

## Rules
- Write only under `docs/handoff/proposed/` and the one report. Change nothing else.
- A proposal with `status: proposed` is **not** executable. It becomes executable only when Michou changes it to `status: open` (or asks you to, in his presence). Do not run any of them.
- Finish by setting this handoff's `status: done` with `completed:`, and commit with message `handoff: proposed fixes from machine audit (HANDOFF-0003)`.

## Report to Michou
Three sentences: how many proposals, which one you'd run first and why, and which ones need him physically present.
