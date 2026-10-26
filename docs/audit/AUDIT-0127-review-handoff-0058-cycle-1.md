---
id: AUDIT-0127
type: report
status: final
handoff: HANDOFF-0058
author: codex
source: inferred
sources: ["HANDOFF-0058", "staged diff sha256 eb955839de893e3bc6e227114dfaa1865ce08db3f3fce4cecccd0722e2a26085"]
tier: 2
created: 2026-10-26T01:13:35-07:00
period: 2026-10-26
review_cycle: 1
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F3, F4]
---

# Review of HANDOFF-0058, cycle 1

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `eb955839de893e3bc6e227114dfaa1865ce08db3f3fce4cecccd0722e2a26085`. Verdict **BLOCK**: blocking 4, transient 1, cosmetic 0, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | cockpit/index.html:1117 | The import map requires 13 modules absent from this patch and `cockpit/static/vendor/`. The report confirms that this configuration produces import failures. The successful clone check includes additional files, so it does not establish acceptance of this diff. | Include the vendor files and approved toolbox changes in the reviewed deliverable before enabling the station. |
| F2 | blocking | cockpit/index.html:1933 | Crew entries are created only from event rows. `/api/events` also returns open runs outside its initial 50-event window, so those runs disappear from station counts and rooms despite appearing on the desk. Elapsed time also starts at the first received event instead of the server’s `first_ts`. | Reconcile crew from `view.runs`, using its actor and timestamps. Handle unavailable event details explicitly. Add a case with an open run outside the event window. |
| F3 | blocking | cockpit/index.html:1740 | The hull still decides whether a halt is active from local event history. A halt followed by 200 ordinary notes is evicted from that history, making the hull show “nominal” while the server still reports the run blocked. This contradicts What §1’s server-owned state requirement. | Obtain the halt indication from server state and mark unavailable details explicitly. Add coverage for a halt outside retained history. |
| F4 | blocking | cockpit/server.py:94 | The symlink check starts below `static`, leaving `static` itself unchecked. If that directory is a symlink, both paths in the containment comparison resolve through it and an external module is served. Amendment 3 requires no symlink on the route. | Reject a symlinked `static` root before traversal and add that case to the route tests. |
| F5 | transient | docs/audit/2026-10-26-cockpit-wall-and-station.md:80 | The required Safari re-check has no evidence; the report identifies Chromium-only tooling. This is an outstanding validation limit, not evidence of a Safari defect. | Record the served station’s view cycle and module loading in Safari when that browser is available. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | cockpit/index.html:1117 | The import map requires 13 modules absent from this patch and `cockpit/static/vendor/`. The report confirms that this configuration produces import failures. The successful clone check includes additional files, so it does not establish acceptance of this diff. | Include the vendor files and approved toolbox changes in the reviewed deliverable before enabling the station. |
| F2 | blocking | cockpit/index.html:1933 | Crew entries are created only from event rows. `/api/events` also returns open runs outside its initial 50-event window, so those runs disappear from station counts and rooms despite appearing on the desk. Elapsed time also starts at the first received event instead of the server’s `first_ts`. | Reconcile crew from `view.runs`, using its actor and timestamps. Handle unavailable event details explicitly. Add a case with an open run outside the event window. |
| F3 | blocking | cockpit/index.html:1740 | The hull still decides whether a halt is active from local event history. A halt followed by 200 ordinary notes is evicted from that history, making the hull show “nominal” while the server still reports the run blocked. This contradicts What §1’s server-owned state requirement. | Obtain the halt indication from server state and mark unavailable details explicitly. Add coverage for a halt outside retained history. |
| F4 | blocking | cockpit/server.py:94 | The symlink check starts below `static`, leaving `static` itself unchecked. If that directory is a symlink, both paths in the containment comparison resolve through it and an external module is served. Amendment 3 requires no symlink on the route. | Reject a symlinked `static` root before traversal and add that case to the route tests. |
| F5 | transient | docs/audit/2026-10-26-cockpit-wall-and-station.md:80 | The required Safari re-check has no evidence; the report identifies Chromium-only tooling. This is an outstanding validation limit, not evidence of a Safari defect. | Record the served station’s view cycle and module loading in Safari when that browser is available. |

## Verdict

BLOCK with 4 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `eb955839de893e3b`. No files were changed and no tests were run.

The saved logs substantiate both reported 653-test passes. Route tests cover headers, methods, traversal and symlinks below `static`; Chromium evidence covers the three-view cycle. Neither covers F2–F4.

ADR-015: the Python files are 194 and 249 lines, have module contracts, and quarantine the added disk access in `read_static`. No `TODO`, `shell=True`, or new subprocess call appears. The 2,474-line page follows the handoff’s explicit single-file amendment. The separate toolbox diff pins and explains all 13 modules; both human-path diffs were inspected.
