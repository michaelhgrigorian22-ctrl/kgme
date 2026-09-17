---
id: AUDIT-0016
type: report
status: final
handoff: HANDOFF-0029
author: claude-code
source: fetched
origin: this repository, `make check`, `kgme review` runs and their audit files of 2026-09-16
tier: 2
created: 2026-09-16T10:30:00-07:00
period: 2026-09-16
---

# HANDOFF-0029 — `kgme review`: the loop as a ledgered command

Per HANDOFF-0029, adopted by Michou 2026-09-16. The handoff named this file with the 17th; the local date is the 16th. The first handoff reviewed by the tool it delivers: every cycle below was run by `kgme review` itself, and its audit files are the cycle records.

## What was built
| Path | Purpose | Lines |
|---|---|---|
| `kgme/review_parse.py` | pure: sections found by whole header lines; `parse_rows`, `parse_findings` (rows inside the Findings section only, escaped pipes, resolved by word boundary), `malformed_rows`, `parse_verdict` (inside the Verdict section only), `parse_review` (a table header, no malformed row, a verdict that agrees with the table), `tooling_failure`, `merge_reclassification`, `apply_rulings`, `verdict`, `counts` | 180 |
| `kgme/review.py` | pure: `summary_line` (ids inline while they fit, else a count and `ledger`), `state_chunks`, `blocking_ids` (raises on an incomplete reconstruction), `LoopState` (`cycles` for labels, `since_override` for the bound, rulings, `last_audit`, `active_halt`), `loop_state` | 171 |
| `kgme/review_text.py` | pure: `escalation_packet`, `audit_text` (cells escaped so the table parses back identically; reads the clock once) | 73 |
| `kgme/review_io.py` | effects, one named function each: `read_staged_patch`, `run_make_check`, `run_reviewer` (`codex exec --json -s read-only`, stdin closed, 600 s timeout), `read_handoff_path`, `read_next_audit_number`, `read_audit_table` (the parser's section lookup), `write_payload`, `read_handoff_events`, `write_ruling` (one per finding), `write_override`, `Places`, `read_places` | 218 |
| `kgme/review_run.py` | the cycle: halt enforcement, dispositions required after the first cycle, the previous table the ledger names in the prompt, dry run that writes nothing, intent, up to three reviewer attempts with jittered backoff, each failure a transient outcome referencing the intent, exhaustion a blocking error outcome, one reclassification retry merged by id, rulings applied, audit file, outcome bound to the diff hash with the JSON stream as payload, state chunks when the ids do not fit, halt packet persisted to the audit and a payload | 270 |
| `tools/review/prompt.md` | the fixed reviewer prompt with `$HANDOFF`, `$CYCLE`, `$PATCH_PATH`, `$SHA`, `$PRIOR_FINDINGS`, `$DISPOSITIONS` | 1 page |
| `kgme/cli.py` | `kgme review --handoff ID [--reviewer] [--arbiter] [--dispositions FILE] [--patch FILE] [--skip-check] [--dry-run]`; `kgme review rule --handoff --finding --class --reason [--arbiter]`; `kgme review override --handoff --reason` | +60 |
| `kgme.toml`, `kgme/paths.py` | `audit_dir`, `handoff_dir`, `review_prompt`, so no path is built outside `paths.py` | +3, +15 |
| `tests/test_review.py`, `tests/test_review_run.py` | seventeen tests, class-marked; the cycle tests run a fake `codex` on PATH that records its argv | 203 + 210 |

Exit codes: 0 PASS, 1 BLOCK or tooling exhausted, 2 usage or red gate, 3 halt.

## The loop bound, as coded
Per the handoff's "Needs from Michou" and the reader: a halt when one root cause stands blocking in three consecutive cycles, or when three or more root causes are still blocking after a fix cycle. Loop state is read back from the ledger alone: successful review outcomes are cycles; error outcomes (tooling) are not; a `note` keyed `ruling:<id>=<class>` is the arbiter's ruling and survives overrides; a `note` keyed `halt:` keeps the loop halted; an `approval` keyed `override:` clears the strike window and the halt but not the rulings or the last audit. Cycle numbers count every successful review of a handoff; the bound counts only the window since the last override. When the open ids do not fit the summary, they follow in `state:<outcome id>:<n>` notes and are reassembled per outcome, or the reconstruction raises. Under this bound the 0027/0028 loop of 2026-09-15 would have halted at its cycle three, where F2 stood blocking for the third time; that loop ran under the reader's prose and the builder's count, and is recorded as such in AUDIT-0014.

## Acceptance test (HANDOFF-0029)
| Check | Result |
|---|---|
| one round-trip on a toy diff produces an audit file with classed findings and an outcome bound to the diff hash | pass: test with a fake reviewer, and live, see Review loop |
| a synthetic ledger with three cycles on one root cause makes `loop_state` return halt | pass; two cycles do not |
| a synthetic 429 in the reviewer output is classed transient and does not count | pass: three transient attempts, one exhausted outcome, `loop_state.cycles == 0` |
| whole suite | 113 passed; `make check` green |

## Review loop
Every cycle below was run by `kgme review` on its own staged diff; the cycle records are its audit files. Reviewer `gpt-6-astra`; arbiter Opus 5 through the Agent tool, ruling recorded with `kgme review rule`.

| Cycle | Record | Diff | Verdict | What it found and what changed |
|---|---|---|---|---|
| 1 | AUDIT-0015 | `a80e6545cd7709e5` | BLOCK, 10 blocking, 2 cosmetic | The first real run of the tool worked end to end (intent, reviewer, audit, outcome bound to the hash). The reviewer found the tool permissive in ten ways: a reply with no parseable table became PASS; "unresolved" read as resolved; the reclassification retry could erase findings; a recorded halt did not stop the next run; the bound was four cycles where the handoff says three; a dry run wrote files; cycle two ran without prior findings; tooling failures had no bounded retry; loop state lived in a clippable summary; the halt packet reached only stdout; `--json` was missing. All accepted and fixed. |
| 2 | AUDIT-0017 | `a4de2844d72f3909` | BLOCK, 7 blocking; **halt** | Five root causes survived the fix cycle (F2, F5, F6, F8, F9) and two were new (F13 pipes unescaped on render, F14 attempt outcomes not closing their intent). The tool halted itself, appended the ADR-016 packet to the audit, bound it to a halt note, and refused to run again. The row-level half of F6 (reclassify a blocking row by its text) went to the arbiter: **advisory**, because the rule would have voided F6 itself and the prompt already assigns row classes to the reviewer; recorded as `ruling:F6=advisory`. Michou overrode on 2026-09-16 with every finding fixed: a review is accepted only with a table, no malformed row, and a verdict that agrees with the table; the prior table comes from the audit the ledger names; rulings survive an override; state lives in the ledger in bounded chunks that replay losslessly or raise; pipes are escaped on render; every attempt outcome references its intent; the attempt timeout is 600 s with jittered backoff. |
| 3 | AUDIT-0018 | `7f88a8298bb27675` | BLOCK, 2 blocking | Twelve rows verified closed. Two real remainders: a Findings header followed by prose containing the word PASS was still accepted, because the verdict fallback searched the whole text; and state chunks keyed by diff hash collided when the same diff was reviewed twice with different finding sets. Fixed: the verdict comes from its section only and a table header row is required; chunks are keyed by their outcome's event id. A builder error is also on record for this cycle: the patch script that was to land the override refinements failed on a reflowed docstring and nothing changed, so cycle three ran on the cycle-two code; the chain now asserts every replacement. Labels changed in the same fix: cycle numbers count every review of the handoff, the halt bound counts only cycles since the last override, and an override keeps the last audit so the reviewer keeps its finding ids. |
| 4, first run | ledger only | `d0e43d87733bfeb3` | tooling exhausted, not counted | The reviewer returned a valid BLOCK with one open finding three times, and the tool rejected it three times: the reviewer's F2 row quoted the string `## Verdict` inside a table cell, the section lookup split the text at that first occurrence, the word PASS in the same cell read as a contradicted verdict, and the failure was then blamed on a transient tooling failure because the Notes mention a 429. The tool's error, on record as four error outcomes in the ledger. Fixed: sections are found by whole header lines; rows, the table header, and the verdict are read only inside their own sections; an empty Verdict section is "no verdict"; the recorded reason for a rejected text is the parse problem, never a tooling guess. The reviewer's one open point from that run, an empty Verdict section followed by Notes yielding PASS, is closed by the same change. |
| 4, rerun | AUDIT-0019 | `1411df23ed1032fd` | BLOCK, 1 blocking | Fourteen rows verified closed, F6 advisory under the ruling. One new finding, F15, a sibling of F2 in the effects layer: the prior-table extractor for the next prompt still split on the first `## Verdict` substring, so a header quoted in a cell would truncate the table the next reviewer sees. Fixed with the parser's whole-line section lookup; the parser moved into `kgme/review_parse.py` to keep every module under the cap. |
| 5 | AUDIT-0020 | `7f91996f0f328a8b` | **PASS** | Fifteen rows verified closed, F6 advisory under the ruling, no new findings. The extractor uses the parser's whole-line section lookup; the parser lives in `kgme/review_parse.py`; every module is under the cap. |

Strikes under the bound as coded: one halt after cycle two (five survivors), overridden by Michou; after the override the window restarted, F2 and F9 stood blocking once more and closed, F15 was raised once and closed. Five successful cycles, one exhausted run, one arbitration, one override; the last cycle PASS.

## Incident, 2026-09-17: the guard crashed on a tilde word
Closing this handoff, a report edit carrying the cell `~330` (a line count) was refused with `guard failed: RuntimeError: Could not determine home directory`. The guard expands every Bash fragment with `expanduser`, which raises when a tilde word names no user; the guard's rule is that a crash fails closed, so the whole call was refused. Fixed as a HANDOFF-0028 follow-up in the same commit series: a tilde word the shell would not expand stays a literal path, resolved against the working directory like any other word; `~` and `~user` still expand and still reach the blocklist. Staged, compiled, exercised, swapped whole per the lockout rule; reviewed under `kgme review --handoff HANDOFF-0028`, the first use of the tool on a handoff other than its own.

## Deviations, stated
- The arbiter is not invoked by the command. Opus 5 runs through the Agent tool in-session, which a Python process cannot reach; `kgme review rule --arbiter <name>` records its ruling, once per finding, and the loop honours it. `--arbiter` on the cycle command names the arbiter in the escalation packet and nothing more.
- Cycle two and later require `--dispositions`. The reader assigns the dispositions to the builder; the command refuses to run a later cycle without them rather than sending the reviewer a blank.
- Findings are recorded under `docs/audit/AUDIT-NNNN-review-<handoff>-cycle-N.md`, one file per cycle, so the handoff's own report (this file) no longer carries the cycle tables; it points at them.
- Report filename carries the local date.

## Needs from Michou
None beyond the bound, which is coded as adopted. A word if the three-attempt, 30 and 60 second backoff is wrong for his machine.

## Next
HANDOFF-0030 stays open until 0031's dry run. HANDOFF-0031 (the validator) is next to adopt; its reviews will run through `kgme review`.
