---
id: READER-REVIEW-LOOP
type: note
status: active
created: 2026-09-14T23:10:00-07:00
modified: 2026-09-14T23:10:00-07:00
author: claude-code
source: stated
tier: 2
---

# The review loop — how a diff gets reviewed, iterated, and committed

*Written 2026-09-14 at Michou's direction from his ruling that a blocking review finding opens a fix-and-re-review loop between models before it ever reaches him. ADR-016 fixes the classes and the bound; ADR-019 §7 is the decision record; HANDOFF-0025 adopts this protocol for hand use and HANDOFF-0029 turns it into `kgme review`. This reader is the human-readable copy; `kgme.toml` `[models]` is the machine-readable one, and the two are kept in sync by hand until a test does it.*

## Models
| Role | Provider | Identifier | How invoked | Notes |
|---|---|---|---|---|
| Builder | Claude Code | the session's model | interactive or `claude -p` | Writes the diff |
| Reviewer | Codex CLI | `gpt-6-astra` | `codex exec -s read-only -m gpt-6-astra --json` | Default reviewer; Codex config default model |
| Reviewer, alternate | Codex CLI | `gpt-5.6-sol` | `codex exec -s read-only -m gpt-5.6-sol --json` | Used when Astra reviewed the previous cycle on the same root cause |
| Arbiter | Claude | Opus 5 (`claude-opus-5`) | Agent tool, model `opus`, read-only | One arbitration per disputed finding; the other lab from the reviewer |
| Also available | Codex CLI | `gpt-5.6-luna`, `gpt-5.6-terra` | same form | Present in the Codex model cache on this machine; unassigned |

A reviewer that must resolve links needs `-s workspace-write -c 'sandbox_workspace_write.network_access=true'` plus a do-not-write instruction and a pre/post SHA-256 check of the tree; read-only is for everything else.

## The cycle
1. **Builder stages the diff** for one handoff, runs `make check`, and writes `git diff --staged` to `logs/scratch/review.patch`. A ledger `intent` is appended: `job: review:<handoff id>`, `key: review:<handoff id>:<diff sha256>`.
2. **Reviewer reads** the handoff, the patch, and the acceptance test, and returns findings. Every finding carries an ADR-016 class: `blocking`, `transient`, `cosmetic`, `advisory`. A finding without a class is returned to the reviewer once; if still unclassed it is recorded as `advisory`.
3. **Findings land** in `docs/audit/AUDIT-NNNN-review-<handoff>.md`. A ledger `outcome` closes the intent with the diff hash, the class counts, and the verdict.
4. **No `blocking` finding:** the builder commits, binding the commit message to the reviewed diff hash. Cosmetic findings are auto-fixed by `ruff format` if deterministic, else noted. Advisory findings go to the weekly review.
5. **A `blocking` finding:** the builder fixes it and returns to step 1 with the new hash. Each cycle's events carry `parent: <the first review intent id>` so the whole loop is one tree in the ledger.
6. **Disagreement:** if the builder holds that a `blocking` finding is not blocking, the arbiter reads the finding, the diff, and both arguments, and rules once. The ruling is a `note` event. There is no second arbitration on the same finding.

## The bound (ADR-016)
- Strikes count **distinct blocking root causes**, never attempts. The same root cause across three cycles is one strike with an attempt count.
- **Tooling failures never count:** sandbox without network, HTTP 429, `curl` 000, a reviewer timeout. They are `transient`, retried within ADR-016's bound, and if exhausted they reclassify to `blocking: exhausted` against the tooling, not the diff.
- **Halt** when three distinct blocking root causes are still unresolved after the builder's fix cycle and the re-review, or when one root cause has gone three cycles without resolution. A first-cycle review may raise any number of findings; strikes are what survives a fix. (Wording amended by Michou 2026-09-15 after the first halt fired at the end of cycle one, before any fix attempt.)
- A halt sends Michou the ADR-016 escalation packet, one screen: what failed, its class, the evidence, the options (override / reject / retry), a recommended default, and what happens if he does nothing (nothing is committed). The intended reply is one word.

## What the loop never does
It never edits an accepted ADR, the charter, or `CLAUDE.md`. It never commits over an unresolved `blocking` finding without Michou's word. It never runs the reviewer with write access to the tree. It never counts a punctuation finding as a strike.
