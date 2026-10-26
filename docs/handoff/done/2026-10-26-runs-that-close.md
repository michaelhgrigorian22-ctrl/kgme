---
id: HANDOFF-0061
type: handoff
created: 2026-10-26T09:42:53-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-26T10:34:40-07:00
report: docs/audit/2026-10-26-runs-that-close.md
depends_on: [HANDOFF-0058, HANDOFF-0040]
plan_ref: PLAN-PHASE-1 step 10d
---

# Handoff 0061 — Runs that close: a `session:end` note, outcomes for every intent, and a page that fits its window

## Why
Michou's first look at the cockpit's `w` views (2026-10-26 09:40): the key bar is cut off at the bottom of the window, and the active-runs pane lists sessions from weeks ago as working or waiting. The second is not the page's fault. `cockpit/render.py` closes a hook session (`tool:*` runs) on a `session:end` note, ported from the station prototype; nothing in KGME writes one. The SessionEnd hook (`control/hooks/session_end_sync.sh`, HANDOFF-0040) only starts `kgme sync`. So every Claude Code session since the ledger began is open: eleven in October, none ended. Beside that, 97 `tool:Bash` intents in October have no outcome, so each is an amber strip waiting for 17 days; the post hook did not fire for them (background commands, interrupted tools, killed sessions: to be measured, not guessed). The header's "2 open intents" is those two, from 2026-10-08.

## What
1. **`session:end`.** The SessionEnd hook appends one `note` with `key: session:end` to the session's run before it starts `kgme sync`, through the hook code (`kgme/hooks/session_end.py`, `python -P -m` like its siblings), with the reason Claude Code gives (`reason` in the hook input: clear, logout, prompt_input_exit, other). The shell line in `control/hooks/session_end_sync.sh` is a human path: a diff. `run_closed` is unchanged.
2. **Every intent gets an outcome.** Measure first: for the 97, classify from the ledger and trace what the tool was and what the session did next (a following intent in the same session means the tool returned and the post hook was missed; a session end means it was interrupted). Then fix the cause that the measurement names, in the hooks or in `kgme/ledger.py`, and not any other. If Claude Code does not fire PostToolUse for a case (an interrupted tool, say), the next PreToolUse in the same session closes the still-open intent of that session with a `transient` outcome "no post-tool record; closed by the next call", so no intent waits past its session's next event. The 97 historical intents stay as they are: the ledger is never edited; the cockpit's view of them is item 4's.
3. **The page fits.** The footer stays inside the window in Chrome, the installed app window and Safari: `100dvh` or the body's bottom padding, whichever the browser check proves; a Playwright check at 1440×900 and at the installed window's size asserts the last key chip is inside the viewport.
4. **A request to the design track, not built here:** a run whose newest event is older than a day with no `session:end` is drawn as abandoned, not working or waiting (grey, listed under the live runs, counted apart in the header), and its open intents are not "open" in the header count. That is a lifecycle rule, so it is the station prototype's first (a CDH row), and `render.py` follows it with its pinned cases when it lands; this handoff records the request and leaves the rule alone.

## Outputs
`kgme/hooks/session_end.py`, `kgme/hooks/pre_tool_guard.py` (the close of a still-open intent, item 2), `kgme/ledger.py` only if the measurement names it, `tests/test_hooks_session_end.py`, `tests/test_guard_open_intent.py`, `cockpit/index.html` (the footer), a Playwright check beside the page's existing ones, `control/hooks/session_end_sync.sh` (human path: a diff), `docs/readers/cockpit.md` (one sentence on closing: a diff), a measurement note in the report.

## Acceptance test (under ten minutes)
A session started and ended by hand writes a `session:end` note and the cockpit shows its run closed on the next poll. A Bash call whose post hook is suppressed in a test leaves no open intent after the next call in that session. In the browser check the last key chip's bottom edge is inside the viewport at both sizes, in Chromium and in WebKit. The report names, for the 97, how many fell in each cause.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one hook, one guard branch, one stylesheet rule. `git revert`.

## Needs from Michou
Adoption. Applying the hook and reader diffs. Which port he was looking at (the demo on a spare port shows `kgme.test` filler runs that are not in his ledger).
