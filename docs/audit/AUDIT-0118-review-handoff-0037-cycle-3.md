---
id: AUDIT-0118
type: report
status: final
handoff: HANDOFF-0037
author: codex
source: inferred
sources: ["HANDOFF-0037", "staged diff sha256 78ae2df4d5be5c985e28483291d8fb816c229314a5e0fdc1686e145d6cbf158d"]
tier: 2
created: 2026-10-25T18:40:46-07:00
period: 2026-10-25
review_cycle: 3
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F7, F8, F9, F10, F11]
---

# Review of HANDOFF-0037, cycle 3

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `78ae2df4d5be5c985e28483291d8fb816c229314a5e0fdc1686e145d6cbf158d`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 2, advisory 1 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:57 | The closing condition remains incomplete. Dock launch is explicitly unverified, `docs/readers/cockpit.md` exists only as a scratch diff, and the required README startup warning is absent. The 40-event browser sample also does not establish the 50-event boundary. | Keep HANDOFF-0037 open. Deliver the documentation and record the outstanding acceptance evidence before closing it. |
| F2 | advisory, resolved | cockpit/render.py:11 | The ledger names approved commit `11b686baa0eccfbb21832728c4d77d4f2953c7ff`. The recorded comparison against that revision reports 255 comparisons at 49 clocks, with 0 disagreements. | No further change is required for this finding. |
| F3 | blocking, resolved | cockpit/render.py:144 | Open runs still receive refreshed states independently of returned rows. The existing regression covers both sides of the 3-minute quiet threshold and excludes a closed run. | No further change is required for this finding. |
| F4 | cosmetic, resolved | cockpit/server.py:134 | Filesystem reads now delegate to documented `read_file`; `Handler.__init__` also has a docstring. | No further change is required for this finding. |
| F5 | advisory, resolved | tests/station_equivalence.py:138 | The comparison reads the selected revision’s quiet floor, derives clocks from its fixtures, and exits 2 when there are 0 comparisons. | No further change is required for this finding. |
| F6 | cosmetic | tests/station_equivalence.py:131 | The prerequisite is now documented, but the check accepts every Node 25 release. Mentioning the observed v25.9.0 does not pin the dependency to that version under ADR-015. | Pin and verify the complete supported version. |
| F7 | blocking | cockpit/index.html:239 | Trace rows become inaccessible when their parent is outside the returned window. The server marks collapse against its complete history, while `t` requires a selectable parent in the client. An in-memory reproduction returned 50 trace rows but displayed 0, with no parent available to expand them. | Provide an accessible parent placeholder or show otherwise unreachable trace rows. Cover parents outside the initial window and parents evicted from client memory. |
| F8 | blocking | cockpit/index.html:219 | Polling can preserve a false pending intent indefinitely. If its outcome is followed by 50 other events between polls, `build_view` returns only those final 50 rows. The client advances its cursor past the outcome and never clears the held intent’s `unmatched` flag. | Consume deltas without gaps or reconcile held rows against authoritative server state. Add a regression with an outcome followed by 50 later events. |
| F9 | blocking | cockpit/index.html:505 | The advertised runs-pane interaction does not select runs. Its rows have no selection state or controls; `j` and `k` still navigate timeline events, and `Enter` filters using the previously selected event. With 0 selected events, `a` then `Enter` does nothing. | Implement run selection and route navigation and Enter to the active pane. Verify selection between at least 2 open runs, including when the timeline selection belongs to a closed run. |
| F10 | blocking | cockpit/index.html:407 | Detail always labels `payload_sha256` “not supplied by /api/events”. The API preserves this field through `ledger.read` and `{**e}` in `build_view`, so a supplied hash is replaced with a false absence statement. | Render the returned hash, distinguish null from missing, correct the report, and verify an event with a non-null hash. |
| F11 | blocking | cockpit/index.html:459 | The approved reader at `11b686b` explicitly binds `w` to desk → wall → station. This implementation reclassifies it as Phase 2 and swallows the key. The recorded approval defers WebKit checking, not this 3-surface binding. | Implement the approved binding or obtain an explicit scope amendment before claiming full acceptance. |
| F12 | cosmetic | cockpit/index.html:207 | The new production page has 530 lines against ADR-015’s approximate 300-line guide. Network, DOM, and storage effects lack the prescribed effect names and function contracts; `poll` combines fetching, reconciliation, and rendering. | Separate logic from named, documented effects within the inline-page constraint, and reconcile the size exception explicitly without minifying the code. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | advisory | docs/audit/2026-10-25-cockpit-v0-closing.md:57 | The closing condition remains incomplete. Dock launch is explicitly unverified, `docs/readers/cockpit.md` exists only as a scratch diff, and the required README startup warning is absent. The 40-event browser sample also does not establish the 50-event boundary. | Keep HANDOFF-0037 open. Deliver the documentation and record the outstanding acceptance evidence before closing it. |
| F2 | advisory, resolved | cockpit/render.py:11 | The ledger names approved commit `11b686baa0eccfbb21832728c4d77d4f2953c7ff`. The recorded comparison against that revision reports 255 comparisons at 49 clocks, with 0 disagreements. | No further change is required for this finding. |
| F3 | blocking, resolved | cockpit/render.py:144 | Open runs still receive refreshed states independently of returned rows. The existing regression covers both sides of the 3-minute quiet threshold and excludes a closed run. | No further change is required for this finding. |
| F4 | cosmetic, resolved | cockpit/server.py:134 | Filesystem reads now delegate to documented `read_file`; `Handler.__init__` also has a docstring. | No further change is required for this finding. |
| F5 | advisory, resolved | tests/station_equivalence.py:138 | The comparison reads the selected revision’s quiet floor, derives clocks from its fixtures, and exits 2 when there are 0 comparisons. | No further change is required for this finding. |
| F6 | cosmetic | tests/station_equivalence.py:131 | The prerequisite is now documented, but the check accepts every Node 25 release. Mentioning the observed v25.9.0 does not pin the dependency to that version under ADR-015. | Pin and verify the complete supported version. |
| F7 | blocking | cockpit/index.html:239 | Trace rows become inaccessible when their parent is outside the returned window. The server marks collapse against its complete history, while `t` requires a selectable parent in the client. An in-memory reproduction returned 50 trace rows but displayed 0, with no parent available to expand them. | Provide an accessible parent placeholder or show otherwise unreachable trace rows. Cover parents outside the initial window and parents evicted from client memory. |
| F8 | blocking | cockpit/index.html:219 | Polling can preserve a false pending intent indefinitely. If its outcome is followed by 50 other events between polls, `build_view` returns only those final 50 rows. The client advances its cursor past the outcome and never clears the held intent’s `unmatched` flag. | Consume deltas without gaps or reconcile held rows against authoritative server state. Add a regression with an outcome followed by 50 later events. |
| F9 | blocking | cockpit/index.html:505 | The advertised runs-pane interaction does not select runs. Its rows have no selection state or controls; `j` and `k` still navigate timeline events, and `Enter` filters using the previously selected event. With 0 selected events, `a` then `Enter` does nothing. | Implement run selection and route navigation and Enter to the active pane. Verify selection between at least 2 open runs, including when the timeline selection belongs to a closed run. |
| F10 | blocking | cockpit/index.html:407 | Detail always labels `payload_sha256` “not supplied by /api/events”. The API preserves this field through `ledger.read` and `{**e}` in `build_view`, so a supplied hash is replaced with a false absence statement. | Render the returned hash, distinguish null from missing, correct the report, and verify an event with a non-null hash. |
| F11 | blocking | cockpit/index.html:459 | The approved reader at `11b686b` explicitly binds `w` to desk → wall → station. This implementation reclassifies it as Phase 2 and swallows the key. The recorded approval defers WebKit checking, not this 3-surface binding. | Implement the approved binding or obtain an explicit scope amendment before claiming full acceptance. |
| F12 | cosmetic | cockpit/index.html:207 | The new production page has 530 lines against ADR-015’s approximate 300-line guide. Network, DOM, and storage effects lack the prescribed effect names and function contracts; `poll` combines fetching, reconciliation, and rendering. | Separate logic from named, documented effects within the inline-page constraint, and reconcile the size exception explicitly without minifying the code. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix **`78ae2df4d5be5c98`**, matching `review.sha` and the patch digest.

No files were changed and no pytest or `make check` command was run. The stored check output reports **603 passed, 42 deselected, 0 blocking lint findings**. Browser behavior and the **1.07-second** append latency remain builder-supplied evidence; I inspected the supplied blocking screenshot. The 2 polling reproductions executed extracted frontend functions entirely in memory with simulated API responses.

The Python production modules remain below 300 lines. Subprocesses use argument lists; no `shell=True` or TODO was found in the reviewed implementation. Tooling limitations were not counted against the diff.
