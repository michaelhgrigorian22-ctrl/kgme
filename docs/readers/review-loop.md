---
id: READER-REVIEW-LOOP
type: note
status: active
created: 2026-09-14T23:10:00-07:00
modified: 2026-10-16T01:55:00-07:00
author: claude-code
source: stated
tier: 2
---

# The review loop — how a diff gets reviewed, iterated, and committed

*Written 2026-09-14 at Michou's direction from his ruling that a blocking review finding opens a fix-and-re-review loop between models before it ever reaches him. ADR-016 fixes the classes and the bound; ADR-019 §7 is the decision record; HANDOFF-0025 adopted this protocol for hand use and HANDOFF-0029 (done 2026-09-17, AUDIT-0016) made it `kgme review`. This reader is the human-readable copy; `kgme.toml` `[models]` is the machine-readable one, and a test checks the two agree.*

## Models
| Role | Provider | Identifier | How invoked | Notes |
|---|---|---|---|---|
| Builder | Claude Code | the session's model | interactive or `claude -p` | Writes the diff |
| Reviewer | Codex CLI | `gpt-6-astra` | `codex exec -s read-only -m gpt-6-astra --json` | Default reviewer; Codex config default model |
| Reviewer, alternate | Codex CLI | `gpt-5.6-sol` | `codex exec -s read-only -m gpt-5.6-sol --json` | Used when Astra reviewed the previous cycle on the same root cause |
| Arbiter | Claude | Opus 5.5 (`claude-opus-5-5`) | Agent tool, model `opus`, read-only | One arbitration per disputed finding; the other lab from the reviewer |
| Also available | Codex CLI | `gpt-5.6-luna`, `gpt-5.6-terra` | same form | Present in the Codex model cache on this machine; unassigned |

A reviewer that must resolve links needs `-s workspace-write -c 'sandbox_workspace_write.network_access=true'` plus a do-not-write instruction and a pre/post SHA-256 check of the tree; read-only is for everything else.

## The commands
| Command | What it does |
|---|---|
| `kgme review --handoff HANDOFF-NNNN` | one cycle on the staged diff: runs `make check` (a red gate is not reviewed), writes the patch and its hash to `logs/scratch/`, appends the `intent`, runs the reviewer, writes the cycle's audit file, appends the `outcome`. Exit 0 PASS, 1 BLOCK or tooling exhausted, 2 usage, 3 halt. |
| `--dispositions FILE` | the builder's answer to the previous cycle's findings, required from the second cycle on; the previous table goes to the reviewer with it, so finding ids stay stable |
| `--reviewer`, `--arbiter` | override the `[models]` defaults; the arbiter is only named in the packet, since it runs through the Agent tool in-session |
| `--patch FILE`, `--skip-check`, `--dry-run` | review a patch file instead of the staged diff; skip the gate; print the prompt and write nothing |
| `kgme review rule --handoff … --finding F2 --class advisory --reason … [--arbiter …]` | record the arbiter's ruling, once per finding; the loop applies it to every later cycle, overrides included |
| `kgme review override --handoff … --reason …` | Michou's one-word answer to a halt, as an `approval`; clears the strike window and the halt, keeps rulings and the previous table |

## The cycle
1. **Builder stages the diff** for one handoff and runs `kgme review --handoff <id>`. The command runs `make check`, writes `git diff --staged` to `logs/scratch/review.patch`, and appends a ledger `intent`: `job: review:<handoff id>`, `key: review:<handoff id>:<diff sha256>`.
2. **Reviewer reads** the handoff, the patch, and the acceptance test, and returns findings under the prompt in `control/review/prompt.md`. Every finding carries an ADR-016 class: `blocking`, `transient`, `cosmetic`, `advisory`. A finding without a class is returned to the reviewer once, with the original review, and only the missing classes are merged back; if still unclassed it is recorded as `advisory`. A reply that is not a review (no table, a malformed row, a verdict that contradicts the table, an empty Verdict section) is a failed attempt: up to three attempts with jittered backoff, each a `transient` outcome referencing the intent, then a `blocking` error outcome that closes it and counts as no strike.
3. **Findings land** in `docs/audit/AUDIT-NNNN-review-<handoff>-cycle-N.md`, cells escaped so the table parses back identically, the reviewer's text verbatim below. A ledger `outcome` closes the intent with the diff hash, the class counts, the audit id, and the open blocking ids, inline when they fit or in `state:<outcome id>:<n>` notes when they do not; the reviewer's JSON stream is the outcome's payload.
4. **No `blocking` finding:** the builder commits, binding the commit message to the reviewed diff hash. Cosmetic findings are auto-fixed by `ruff format` if deterministic, else noted. Advisory findings go to the weekly review.
5. **A `blocking` finding:** the builder fixes it and runs the next cycle with `--dispositions`. Each cycle's events carry `parent: <the first review intent id>` so the whole loop is one tree in the ledger.
6. **Disagreement:** if the builder holds that a `blocking` finding is not blocking, the arbiter reads the finding, the diff, and both arguments, and rules once; the ruling is recorded with `kgme review rule` and applied from the next cycle on. There is no second arbitration on the same finding.
7. **A halt** appends the ADR-016 packet to the cycle's audit file and to a payload bound to a `halt:` note, prints it, and refuses every further cycle until `kgme review override` records Michou's answer.

## The bound (ADR-016)
- Strikes count **distinct blocking root causes**, never attempts. The same root cause across three cycles is one strike with an attempt count.
- **Tooling failures never count:** sandbox without network, HTTP 429, `curl` 000, a reviewer timeout. They are `transient`, retried within ADR-016's bound, and if exhausted they reclassify to `blocking: exhausted` against the tooling, not the diff.
- **Halt** when three distinct blocking root causes are still unresolved after the builder's fix cycle and the re-review, or when one root cause has stood blocking in three consecutive cycles. A first-cycle review may raise any number of findings; strikes are what survives a fix. (Wording amended by Michou 2026-09-15 after the first halt fired at the end of cycle one, before any fix attempt; coded in `kgme/review.py` `loop_state` under HANDOFF-0029, which counts the window since the last override.) (ADR-023, accepted 2026-10-16: a count no longer decides by itself. Until HANDOFF-0043 changes `loop_state`, the coded halt still fires at the third cycle and is answered by Michou's override; the ruling of the next rule should settle a root cause before then.)
- **Two cycles, then a ruling (ADR-023).** When a blocking finding is disputed, or one root cause has stood blocking for two consecutive cycles, the builder sends it to the arbiter: the model named by `kgme.toml [models] arbiter`, in a fresh context, given the finding, the diff and both arguments, never the builder's conversation; the ruling is recorded with `kgme review rule`. The ruling downgrades the finding, recommends an option (each option with its door, one-way or two-way, and its blast radius), or rules it outside the mandate. The builder executes the ruling in the next cycle; on a split it takes the reversible option with the smallest blast radius and says why. Only an outside-the-mandate ruling, or a ruling executed twice with the same root cause returning, goes to Michou. (Michou's rule of 2026-10-13, that a third patch on the same mechanism is not an option, stands: the ruling replaces the patch. Amended by Michou 2026-10-16.)
- **A fix cycle starts with a red command.** Before the patch, the builder's disposition names, for each `blocking` finding, one command that goes red on that finding's exact symptom (deterministic, seconds, runnable with nobody present) and shows it having run once; where no such command exists the disposition says so, and that absence is itself a finding for the reviewer. A patch without its red command is not a fix cycle. (Michou, 2026-10-14, adopting the Phase 1 discipline of `diagnosing-bugs` in `mattpocock/skills`; the review that brought it in is `memory/agent/2026-10-13-external-repos-review.md`.)
- A halt sends Michou the ADR-016 escalation packet, one screen: what failed, its class, the evidence, the options (override / reject / retry), a recommended default, and what happens if he does nothing (nothing is committed). The intended reply is one word.

## What the loop never does
It never edits an accepted ADR, the charter, or `CLAUDE.md`. It never commits over an unresolved `blocking` finding without Michou's word. It never runs the reviewer with write access to the tree. It never counts a punctuation finding as a strike.
