---
id: AUDIT-0141
type: report
status: final
handoff: HANDOFF-0061
author: claude-code
source: inferred
sources: ["HANDOFF-0061", "kgme/hooks/post_tool_ledger.py", "kgme/hooks/pre_tool_guard.py", "kgme/hooks/open_intents.py", "kgme/hooks/session_end.py", "cockpit/index.html", "cockpit/render.py"]
tier: 2
created: 2026-10-26T10:06:27-07:00
period: 2026-10-26
---

# HANDOFF-0061: runs that close

## The measurement (§2), before any fix
The open October tool intents were read from the ledger and the trace (`logs/scratch/handoff-0061/measure.py`, one line per intent in `open-intents.tsv`) at 09:47, five minutes after the handoff was written (09:42:53). The table records what was **observed**, the next event in the same session after each intent; the causes come after it, and they are **inferred**.

| | next event: another call's intent | next event: another call's outcome (calls in parallel) | none at measurement time | total |
|---|---|---|---|---|
| **the 97**: `tool:Bash`, written before the handoff | 89 | 7 | 1 | **97** |
| `tool:Bash` written after the handoff (this build session) | 0 | 0 | 1 | 1 |
| other tools (`ScheduleWakeup`, `AskUserQuestion`, a Playwright evaluate, `TaskStop`) | 3 | 0 | 1 | 4 |

**The cause, inferred from three facts.** Claude Code fires `PostToolUse` only for a call that succeeded. A call that fails or is interrupted fires `PostToolUseFailure`, with `error` and `is_interrupt` instead of `tool_response` (this build's hook types). KGME never registered that event. The facts:
- **The ledger.** Across every `tool:Bash` outcome, the post hook wrote 2,509 `ok`, the guard wrote 48 `refused`, and there is not one `error`: no failed Bash call ever had an outcome.
- **A probe in this session.** `echo …; exit 3` left its intent with no outcome, and `echo …` beside it got `ok`.
- **The order of the hook events,** measured in a clone (below).

So the 96 of the 97 that a later event followed are, most likely, calls that failed or were interrupted. That is an inference: the ledger cannot show an exit code it never received. For the one with no later event, the cause is **unknown**. "No later event at measurement time" does not establish that its session ended or was killed.

## What was built
1. **The measured cause, fixed in the hooks.** `kgme/hooks/post_tool_ledger.py` also handles `PostToolUseFailure`, through the same script. A failed or interrupted call's intent is closed `error` with class `advisory`, or `transient` for the timeout shapes ADR-016 names. It is never `blocking`: a tool's own failure is the model's to handle, not a halt, and `render.py` draws a run with a blocking newest outcome as blocked.
2. **The backstop, at the end of each batch** (§2, rebuilt on review cycle 1 F1 and F2). Claude Code fires `PostToolBatch` once after every call of a batch has resolved, before the next model request, with the batch's `tool_use_id`s; a single call is a batch of one. `post_tool_ledger.py` hands it to `kgme/hooks/open_intents.py`, which closes this session's intents whose key is one of the batch's ids and that still have no outcome: `error`, `transient`, "no post-tool record; closed at the end of its batch".
   - **It is safe because of the measured order.** In a clone, two parallel calls (`false` and `sleep 3`) fired `PostToolUseFailure`, then `PostToolUse` 2.8 s later, then `PostToolBatch` with both ids, 44 ms after the slower call's outcome was written. The per-call hooks have finished when the batch arrives, so a closed intent is one no post record will ever answer.
   - **It replaces the cycle-1 design.** That design closed intents at least 10 s and at most a day old on the next PreToolUse. F1 showed that age does not prove a call finished, and the cycle-1 rule both left a call 2 s later open and closed a live sibling 12 s in (`red-c1.txt`). The batch rule guesses nothing and touches only the batch's own calls, so no earlier intent, history included, is ever reached (F2).
   - **It is stronger than §2's letter:** the batch ends before the next call can start. `kgme/hooks/pre_tool_guard.py` is therefore unchanged and back at HEAD.
3. **`session:end`** (§1). `kgme/hooks/session_end.py` (`python -P -m`) appends one `note` keyed `session:end`, job `session`, to the session's run, with Claude Code's reason in its summary. `render.run_closed` is unchanged.
4. **The page fits** (§3). `.hud` takes `height: 100dvh`, with `100vh` as the fallback.
   - **Not reproduced first:** the clip did not show in Chromium at 12 sizes (800×700 to 1440×900, the demo ledger and Michou's real one) nor in Safari 26.6.2 at two.
   - **The tracked check** (F3), `tests/footer_check.py`, run by hand like `tests/station_equivalence.py`. It serves this checkout's `cockpit/` over a small temporary ledger and asserts the last key chip of desk, wall and station inside the viewport at 1440×900 and 1440×820, in Chromium (Playwright with the system Chrome, the library the Playwright MCP brings) and in WebKit (Safari through the system's `safaridriver`). Nothing is downloaded. It exits 1 when a chip is outside.
   - **Green on the change:** 0 outside, 12 rows.
   - **Red on a copy whose `.hud` is 110vh:** 8 outside (`footer-red.txt`).
   - **The earlier WebKit evidence is kept:** `webkit-check.txt` and `browser-checks.md`.
5. **Not built: §4,** the abandoned-run rule. It is the design track's (a CDH row first), and `render.py`'s rules are untouched.

## Acceptance
- **A session ended by hand closes its run.** In a fresh clone with the drafted settings and shell line, real Haiku sessions ran with a clean environment:
  - `false` alone: its intent, an `error` / `advisory` outcome through `PostToolUseFailure`, `session:end` reason `other`, and `render.build_view` draws the run closed.
  - `false` and `sleep 3` in parallel: each kept its real outcome, the batch closed nothing, the session ended, and the run was drawn closed.
  - In the tests, `tests/test_hooks_session_end.py` shows the run open before the note and closed after it.
- **A suppressed post leaves no open intent after the next call.** `tests/test_guard_open_intent.py` covers four cases:
  - the post of a call never runs, and its batch of one closes it before an immediate next call;
  - a long sibling's real outcome stays the one paired;
  - an older open intent of the same session (history, or a resumed session's past) and another session's are never reached;
  - the pure selection.
- **Failure events:** a failed, an interrupted and a timed-out call are closed `error` with `advisory`, `advisory` and `transient`.
- **The footer:** as above, in both engines at both sizes.
- **The 97:** as the table above names them.
- **`make check`:** lint 0 blocking, `kgme mods: 2 mod folders, 0 blocking`, 690 passed.

## Found on the way, stated plainly
- **27 of the measured intents were closed, and the outcomes stand.** The cycle-1 backstop was live for about 30 minutes and closed 27 of them, all from this build session (Claude Code's, building HANDOFF-0058 to 0061) and under a day old. They were closed by appended outcomes "no post-tool record; closed by the next call"; no line was edited, and the ledger is append-only, so those outcomes stay as disclosed (F2). Every other session's 72 are untouched, and so are this session's 2 older than a day. The batch backstop that replaces it reaches none of them.
- **One stray intent** (session `d64ff424`, 10:04:01) is in the main ledger with no outcome. It came from my first attempt at the live check: the child `claude` inherited this session's `CLAUDE_PROJECT_DIR`, so it ran `main`'s hooks, and `main`'s `SessionEnd` then ran its usual ledger sync and push. The checks after it ran with a clean environment. The clone's own sync tried to push to my checkout and git refused it; I then pointed the clone's remote at nowhere.

## Waiting for Michou
Under `logs/scratch/handoff-0061/`:
1. **`hooks-and-settings.diff`,** to apply together:
   - `control/hooks/session_end_sync.sh`: the `session:end` note before `kgme sync`;
   - `.claude/settings.json`: `PostToolUseFailure` and `PostToolBatch` registered with the existing post-hook script, 26 lines added and none changed;
   - `tests/policy/settings_fingerprints.json`: two new baseline lines, each the same fingerprint as `PostToolUse`'s. They must land with the settings, or the policy test goes red.
2. **`cockpit-reader.diff`:** one sentence on how runs close.

Until the first diff is applied, the failure handling, the batch backstop and the `session:end` module are present but not called.

**The demo servers are stopped:** 8655 and 8656 were last night's browser checks, and 8657 was this morning's served-station check. For this handoff I ran the demo on 8658 and `kgme cockpit` itself on 8642, both stopped. `safaridriver` runs only inside a check.

## Review cycle 1 (AUDIT-0142, BLOCK on F1 to F4), fixed
- **F1:** the age rule is replaced by the batch's own ids. Red on the cycle-1 rule (`red-c1.txt`); the tests cover an immediate next call, a long sibling, and a resumed session.
- **F2:** only the batch's own calls are reached. The test covers history in the same session, and the 27 earlier outcomes are disclosed.
- **F3:** `tests/footer_check.py`, tracked, red on a broken copy and green on the change.
- **F4:** the 97 reconciled, with the added and other-tool rows apart, the observed apart from the inferred, and the one unexplained case labelled unknown.

## Review cycle 2 (AUDIT-0143): PASS
- **F5 (cosmetic):** `tests/footer_check.py`'s `chromium` and `webkit` runners and its HTTP helper want `run_*` names and effect docstrings.
- **F6 (advisory):** the check takes the newest Playwright in the npx cache without verifying its version, the Playwright MCP's unpinned row in `docs/toolbox.md`.
- **F7 (advisory):** F4's reconciliation had no red command. Its counts are reproducible from `open-intents.tsv`, one line per intent with its time and class, filtered on the handoff's 09:42:53.

None is fixed after the PASS; reviewed code is not changed. F5 and F6 are for a small follow-up.

**State: ready, diffs pending.** The code is committed by pathspec. The handoff stays open until Michou applies `hooks-and-settings.diff`, and a session ended by hand then writes `session:end` on `main` and the cockpit draws its run closed on the next poll.

## For the approval screen
- **A failed tool call's class is `advisory`** (`transient` for timeouts), not `blocking`. Stakes 3, edge 0.4, score 1.2.
- **The backstop at `PostToolBatch`,** not the next `PreToolUse` §2 names. It is stronger, guesses nothing, and needs one more registration. Stakes 2, edge 0.3, score 0.6.

## Closed on main, 2026-10-26
- **Michou's commit `3ca626c`** applies the `session:end` line in `control/hooks/session_end_sync.sh`, registers `PostToolUseFailure` and `PostToolBatch` in `.claude/settings.json` with their two fingerprint lines, and adds the cockpit reader's sentence.
- **`make check` on `main`:** the policy test accepts the new fingerprints. Lint 0 blocking, `kgme mods: 2 mod folders, 0 blocking`, 690 passed.
- **The live proof on `main`.** `kgme cockpit` served 8642, and two Haiku sessions were started and ended by hand from the main checkout, with a clean environment, so they ran `main`'s own hooks.
  - **Session `17a3280b`:** `false` ran and exited 1. Its intent got `error` / `advisory`, "Bash error", through `PostToolUseFailure` 0.6 s later, and the session ended with `session:end`, reason `other`.
  - **Session `220d95d4`:** the model passed the whole prompt sentence to Bash, and Claude Code refused the command before running it (a parse error), so no post event fired. The batch backstop closed that intent 150 ms later, `error` / `transient`, "no post-tool record; closed at the end of its batch", and the session ended with `session:end`. That is the backstop's own case, proven live.
  - **The cockpit's next poll** (10:56:40, 19 s after the second session ended) drew both runs closed, in the page's state and in `/api/events`, and neither is listed in the active-runs pane.
  - The server on 8642 is stopped.
- **The handoff closes** with `completed:` set to the PASS review's `created` (AUDIT-0143, 2026-10-26T10:34:40-07:00).
- **Disclosed: one stray open call.** Session `d64ff424`'s `tool:Bash` intent of 10:04:01 stays in the main ledger with no outcome. It came from my first attempt at the live check in the acceptance clone: the child `claude` inherited this session's `CLAUDE_PROJECT_DIR`, so it ran `main`'s hooks, which then registered neither the failure event nor the batch, and `main`'s SessionEnd ran its usual ledger sync and push. Every check after it ran with a clean environment. The intent is history now, before the backstop's registration; it is left as written, and §4's abandoned-run rule will draw it.

## The review's follow-up (AUDIT-0143 F5, F6, F7), after the close
One commit, under this report.
- **F5:** `tests/footer_check.py`'s runners are `run_chromium` and `run_webkit`, its WebDriver helper is `run_webdriver`, and `read_playwright`, `write_ledger` and `main` each say what they read, return and do.
- **F6:** the check uses Playwright only at the version pinned in it, `PLAYWRIGHT = "1.64.0-alpha-1790635538000"`, the one the Playwright MCP had installed when the check was written and proven. `read_playwright` takes the installed copy whose `package.json` matches and refuses otherwise, naming what it found. Run with a pin that is not installed, the check exits 2 before driving a browser (`logs/scratch/handoff-0061/pin-red.txt`). With the pin, it is green: 0 outside, 12 rows. This is a check before use, not a pin of the MCP itself, whose row stays unpinned and Michou's to decide.
- **F7:** `logs/scratch/handoff-0061/check_cohort.py` counts the 97 from the frozen measurement (`open-intents.tsv`, the `tool:Bash` rows before the handoff's 09:42:53) and exits 1 unless a claim matches.
  - **Red on the cycle-1 report's claim:** `97 92 7 3` is refused, because the rows say 89, 7 and 1 (`cohort-check.txt`).
  - **Green on the corrected claim:** `97 89 7 1`.
  - **Why there was no red command before:** the corrected count was arithmetic over a measurement already taken; the check now makes it a command.

