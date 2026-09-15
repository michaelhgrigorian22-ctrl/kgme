---
id: ADR-019
type: decision
status: accepted
accepted_by: michou
accepted: 2026-09-14T22:52:00-07:00
created: 2026-09-14T22:25:00-07:00
author: claude-code
source: inferred
sources: [ADR-003, ADR-008, ADR-012, ADR-013, ADR-015, ADR-016, ADR-017, AUDIT-0011]
modified: 2026-09-14T23:10:00-07:00
tier: 2
supersedes: [ADR-017 (partial: the event shape in §2 only), ADR-016 (partial: names the review-loop protocol as the escalation procedure for review findings)]
---

# ADR-019 — Ledger event schema v1: one shape, one writer, two streams, redaction at the choke point

*Proposed 2026-09-14 by Claude Code from the four-model deliberation of the Phase 1 plan (AUDIT-0011) and Michou's rulings of the same evening. Amended the same night at Michou's direction: a nullable `parent` field, and storage split into a git-tracked ledger for consequential events and an untracked trace for read-only tool events, same schema and writer. Becomes accepted on his word and commit. Until then the shape below is the working assumption of HANDOFF-0026.*

## Context
ADR-017 §2 fixes the event as `{ts, run_id, source, kind, class, payload_ref}`. The Phase 1 plan (PLAN-PHASE-1 step 2) adds `actor`. Neither carries an event id, a schema version, or a way for an `outcome` to name the `intent` it closes, which the reconciliation rule of ADR-013 §4 needs. ADR-016 line 33 makes `class` required on every `outcome` but defines no class for success. ADR-012 makes the ledger tracked in git and never deleted, so a secret that reaches a ledger line can only be removed by a history rewrite performed by Michou (ADR-012 §Forget vs purge). All four reviewers in AUDIT-0011 asked for the three missing fields; Opus 5 and Fable 5.1 identified the secret-in-ledger path as the only irreversible mistake available in Phase 1. Michou ruled on 2026-09-14 that raw tool inputs go to gitignored scratch and only a redacted summary reaches the ledger.

## Decision

### 1. The event, v1
One JSON object per line, UTF-8, in `logs/ledger/YYYY-MM.jsonl`. Field order is fixed for readability; every field is present, with `null` where not applicable.

| Field | Type | Rule |
|---|---|---|
| `v` | int | Schema version of this line. `1`. |
| `id` | string | ULID, monotonic within a process. Unique across the ledger. |
| `ts` | string | ISO 8601 with offset, milliseconds: `2026-09-14T08:03:11.412-07:00`. Always `datetime.now().astimezone()`, never `utcnow()`, never a literal offset. |
| `run_id` | string | ULID minted by the job at start; for Claude Code hook events, the vendor `session_id`; for Codex, the thread id from its first JSON event. |
| `source` | enum | `kgme` · `claude-code` · `codex` · `human` |
| `actor` | string | Dotted name of the writer: `kgme.brief`, `kgme.clean`, `claude-code.hook`, `codex.review`, `michou`. |
| `kind` | enum | `intent` · `outcome` · `tool_call` · `approval` · `correction` · `note` |
| `class` | enum or null | `blocking` · `transient` · `cosmetic` · `advisory` per ADR-016; `null` on any event that is not a failure or finding. This is the clarification ADR-016 left open. |
| `status` | enum or null | `ok` · `error` · `refused` on `outcome`; `null` elsewhere. Separate from `class` because a run can succeed while carrying a cosmetic finding. |
| `job` | string or null | Job name from its folder under `jobs/`, or `tool:<ToolName>` for hook events. |
| `key` | string or null | Idempotency key per ADR-013 §4 and ADR-015: `brief:2026-09-14`, `clean:briefs:2026-09-14T08:03`. |
| `ref` | string or null | `id` of the `intent` this `outcome` closes, or of the event a `correction` corrects. Transaction pairing. |
| `parent` | string or null | `id` of the event this one nests under: a tool call inside a job run, a sub-run inside a run, a review cycle inside a handoff. Hierarchy, distinct from `ref`. |
| `summary` | string | At most 200 characters, human-readable, already redacted (§3). |
| `payload_ref` | string or null | Repo-relative path under `logs/scratch/payloads/`, gitignored. |
| `payload_sha256` | string or null | Hex digest of the payload file at write time. |

### 2. Two streams, one schema, one writer
Every event is written by the same `append()` to one of two streams chosen by rule, never by the caller's preference:

| Stream | Path | Git | Class (ADR-012) | Holds |
|---|---|---|---|---|
| **ledger** | `logs/ledger/YYYY-MM.jsonl` | tracked, never deleted | durable event record | `intent`, `outcome`, `approval`, `correction`, `note`; every job event; every hook pair for a tool that writes, executes, or reaches the network (`Edit`, `Write`, `NotebookEdit`, `Bash`, `WebFetch`, `WebSearch`, MCP tools, and any tool not on the read-only list) |
| **trace** | `logs/trace/YYYY-MM.jsonl` | untracked (`.gitignore`), not backed up by git | disposable | hook pairs for read-only tools: `Read`, `Grep`, `Glob`, `LS`, `TodoRead`, and any tool the `[hooks] read_only_tools` list in `kgme.toml` names |

The rule lives in the writer: `append(event)` inspects `job` (`tool:<Name>`) and `kind`; a read-only tool's `intent`/`outcome` pair goes to trace, everything else to the ledger. A caller cannot route a consequential event to trace. A refused read-only call (`status: refused`, `class: blocking`) goes to the **ledger**, because a policy refusal is consequential whatever the tool. Deleting the trace loses nothing consequential by construction; `kgme clean trace` is a named target. Michou's 2026-09-14 ruling that every tool call is recorded stands; the split decides where, not whether.

### 3. Semantics
- **Every consequential action is a pair.** `intent` before, `outcome` after with `ref` pointing back. On start, a job calls `open_intents(job)` and reconciles any intent without an outcome by inspecting the destination (ADR-013 §4).
- **Hook events are pairs too.** The Claude Code pre-tool hook writes `kind: intent, job: tool:<Name>`; the post-tool hook writes `kind: outcome, ref: <that id>`. A tool that crashes mid-flight is an unmatched intent, never silence. `tool_call` is reserved for Phase 2 ingestion of vendor event streams, where no pre/post pair exists.
- **Tests never write the real streams.** Test runs point `paths.ledger_dir` and `paths.trace_dir` at `logs/ledger-test/` and `logs/trace-test/`, gitignored, so `make check` before a commit leaves the tree clean (ADR-012 tracks the real ledger).
- **`parent` builds the tree the cockpit renders.** A job run's events carry `parent: <run intent id>`; a hook pair inside a Claude Code session carries `parent: <session's first event id>` when one exists, else null; a review cycle carries `parent: <the handoff's review intent>`. `ref` pairs, `parent` nests.

### 4. One writer, redaction inside it
`kgme/ledger.py` exposes `append(event) -> id`, `read(since=None, run_id=None, stream="both")`, `open_intents(job)`. Nothing else opens a ledger or trace file for writing. `append`:
1. validates the field set and enums above and refuses an unknown field;
2. runs `redact()` over `summary`: anything matching the secret patterns of ADR-008 (token-shaped strings, `key=`, `password=`, `Bearer`, and any path under `~/.ssh`, `.env*`, `~/Library/Keychains`, `~/.claude/` or `~/.codex/` credential stores) is replaced by `<redacted:sha256-prefix>`;
3. refuses any serialized line over 4096 bytes rather than truncating;
4. selects the stream by the rule in §2 and the month file from the event's own local `ts`, per event, so a run crossing midnight on the last day of a month lands each event in the right file;
5. opens with `O_WRONLY | O_APPEND | O_CREAT`, takes `fcntl.flock(LOCK_EX)`, writes the line in one `os.write`, calls `os.fsync`, releases. Two agents appending at once cannot interleave.

Raw tool inputs, file bodies, command strings, and model outputs never enter a ledger line. They go to `logs/scratch/payloads/<id>.json` (disposable class per ADR-012, deletable by `kgme clean`, not backed up) and the line carries their hash. What survives a machine loss is the fact, the actor, the time, the outcome, and the hash; what does not survive is the replayable body. Michou accepted that trade on 2026-09-14.

### 5. Identity
ULIDs come from a `kgme/ulid.py` of about twenty lines using `os.urandom` and the standard monotonic increment; no dependency. `schema-v1.md` line 20 already commits agents to ULIDs for note ids, so one generator serves both.

### 6. Versioning
A change to the field set is `v: 2` with a migration script under `tools/ledger/`, never an edit to existing lines (ADR-003). Readers accept every version they know.

### 7. Relation to ADR-016: the review loop
ADR-016 fixes failure classes, bounded retries, and the escalation packet, and says a `blocking` finding stops the job and escalates. Michou ruled on 2026-09-14 that a `blocking` review finding first opens a fix-and-re-review loop between builder and reviewer models, with one arbitration by a model from the other lab, bounded by ADR-016's own strike rule (distinct blocking root causes only; tooling failures never count; halt at three distinct unresolved root causes or three cycles on one), and escalates to Michou with the ADR-016 packet only at the bound. That procedure is written in `docs/readers/review-loop.md` and enforced by `kgme review` (HANDOFF-0029), and its cycles are ledger events with `parent` set to the handoff's review intent. This section is the cross-reference ADR-016 cannot carry itself, since accepted ADRs are never edited; a reader of ADR-016 finds it through this ADR's `supersedes` line.

## Alternatives considered
- **Keep ADR-017's six fields.** No way to pair intent and outcome, deduplicate, or migrate. Rejected by all four reviewers.
- **Tracked, sanitized payload store under `logs/`** (Astra's proposal). Replay survives machine loss, but one sanitizer miss is permanent in git. Rejected by Michou 2026-09-14.
- **No payload store at all** (Opus's fallback). Simplest, but loses the ability to see what a tool was actually asked when a run is investigated. Rejected in favour of scratch plus hash.
- **A `seq` counter instead of ULID `id`.** Two events in one millisecond are ordered by the ULID's monotonic tail; the extra field was not needed.
- **One stream for everything.** Read, Grep, and Glob are the bulk of tool calls; tracking them in git would grow the durable ledger by an order of magnitude with events that decide nothing. Rejected by Michou 2026-09-14 in favour of the two-stream split.
- **Letting callers choose the stream.** A caller under deadline would route a consequential event to the untracked stream by mistake. The rule lives in the writer.
- **SQLite ledger.** Hides the journal behind a query layer; ADR-003 already declined it.

## Consequences
ADR-017 §2's event shape is superseded by §1 above; every other clause of ADR-017 stands, including the one-shape-for-every-source rule this ADR strengthens. ADR-016's escalation for review findings is preceded by the loop in §7; everything else in ADR-016 stands. The cockpit's `since` cursor is the ULID `id`, and its timeline reads both streams and nests by `parent`. The hook pair (HANDOFF-0028) is the writer's first client and the first live proof of ADR-013 §4. `kgme clean` gains `payloads` and `trace` as named targets. `.gitignore` gains `logs/trace/`, `logs/ledger-test/`, and `logs/trace-test/`. The Codex model identifiers used by the review loop live in `kgme.toml` `[models]` and in `docs/readers/review-loop.md`, not in any agent's memory.
