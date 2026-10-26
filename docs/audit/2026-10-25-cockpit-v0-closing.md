---
id: AUDIT-0117
type: report
status: final
handoff: HANDOFF-0037
author: claude-code
source: inferred
sources: ["HANDOFF-0037", "AUDIT-0112", "AUDIT-0113", "AUDIT-0114", "cockpit/index.html", "cockpit/render.py", "cockpit/server.py", "cockpit/manifest.json", "cockpit/icon.png", "tests/station_equivalence.py", "tests/test_server.py", "tests/test_render.py"]
tier: 2
created: 2026-10-25T18:30:17-07:00
period: 2026-10-25
---

# HANDOFF-0037: cockpit v0, the read-only timeline (closing report, both halves)

**This is the handoff's closing report and covers both halves.** AUDIT-0112 reported the first half (the view, the server, `kgme cockpit`; committed as `11698ca`, reviewed by AUDIT-0113 and AUDIT-0114) and is an interim report, never the handoff's `report:` (the arbiter's ruling on AUDIT-0113 F1). This report adds the second half: the page, the Dock files, the reader, and the closing conditions.

## Built from the approved canvas
Michou's approval in the ledger: `approve:canvas:11b686baa0eccfbb21832728c4d77d4f2953c7ff`, 2026-10-25T18:16:07-07:00, "cockpit v0 canvas: design through CDH-0019 and CDH-0031 as landed by kgme merge design; CDH-0030 WebKit check deferred to the Tauri ADR". It was read from the ledger. `kgme approve --show` stays denied to agents, and that is correct. Every design file was read with `git show 11b686b:<path>`.

## What the second half built
1. **`cockpit/index.html`** (§3). One self-contained file of 42 KB with inline CSS and JS. It loads no remote asset and fetches no web font. It renders the approved design's five states from boards 2 to 6 of `11b686b`:
   - **Empty:** board 2.
   - **Live:** board 3.
   - **Blocking:** board 4. The frame floods magenta, the ledger line reads `halted`, and the detail opens on the halt note.
   - **Unmatched intent:** board 5. An amber strip over the frame, the open-intent panel, and the "outcome lands here" block.
   - **Disconnected:** board 6. A persistent band under the header, never a modal, with the last snapshot kept and inspectable.
   - **The keyboard map** follows board 7 and the design reader's key line; Phase 2 keys are drawn dashed and unbound.
   - **Calm** drops every decorative layer and keeps every fact (the one rule).

   It polls `/api/events` every two seconds and displays the server's run states; it decides none. Every event string is set as text: no `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` or `eval`, as held by `tests/test_server.py`. The page spec drawn from the boards is `logs/scratch/handoff-0037/page-spec.md`; every degradation in it is listed under "Deviations" below.
2. **`cockpit/manifest.json` and `cockpit/icon.png`** (§4). The manifest is standalone, with `start_url` `/`, the ground colour, and one 512 × 512 icon declared at 192 and 512. The page links the manifest and an `apple-touch-icon` for Safari's "Add to Dock". The manifest's description and the page state that the Dock icon does not start the server.
3. **`docs/readers/cockpit.md`** (§5), a human path, drafted as `logs/scratch/handoff-0037/cockpit-reader.diff` for Michou. It covers starting the cockpit, installing it to the Dock, reading the timeline, and the keys. **The README sentence** item 4 asks for (the Dock icon does not start the server) is drafted for the front door as `logs/scratch/handoff-0037/readme.diff`.
4. **Cycle 2's cosmetic findings:**
   - **F4:** `do_GET` delegates its file reads to `read_file`, and `Handler.__init__` is documented.
   - **F6:** the closing check pins and checks Node v25.9.0 exactly (nvm), refusing any other version.

## The closing conditions
- **F2, the lifecycle against the approved commit** (the arbiter's ruling on AUDIT-0113 F2; AUDIT-0114 F5 advisory).
  - **The check now reads everything from the chosen commit:** the station's `lifecycle` and `runClosed`, its `QUIET_FLOOR`, and the sample events, with the clocks derived from those events. It refuses a zero-comparison run, and a floor different from the port's counts as a disagreement.
  - **At `11b686b`:** floor 180000 ms, 49 clocks, **255 comparisons, 0 disagreements** (`logs/scratch/handoff-0037/equivalence-approved.txt`; the same at `997a730`).
  - **`render.py`** needed no change. Its docstring now records the check in place of "provisional".
- **F1, this report covers both halves** and is the one the handoff's `report:` names.

## Acceptance (the whole handoff)

**Checked in a browser** (Playwright, Chromium at 1440 × 900) against the server over a scratch ledger seeded with the design's 40 sample events (the real ledger was never touched). Screenshots are under `logs/scratch/handoff-0037/shots/`.

| item | evidence | result |
|---|---|---|
| `kgme cockpit` serves on `127.0.0.1:8642` | `tests/test_server.py`; run live against the real ledger (AUDIT-0112) | met |
| the page renders the last fifty events in time order, grouped by run | 40 rows in 14 run groups, timestamps in order (`live-2.png`) | met |
| an event appended by hand appears within two seconds without reload | appended at 18:28:08.331, drawn at 18:28:09.401: 1.07 s | met |
| an event whose summary contains `<script>` renders as text | the row shows `<script>window.PWNED=1</script> appended by hand` as text; no `script` element created; `window.PWNED` unset | met |
| a connection to the LAN address is refused | `test_a_connection_to_the_lan_address_is_refused` | met |
| every non-GET request returns 404 | `test_every_method_but_get_is_404` (eight methods, one invented) | met |
| the Dock icon opens the page while the server runs | manifest, icon and `apple-touch-icon` served (`test_the_dock_files_are_served`). The install itself is a click in Michou's browser and was not performed by the builder | pending Michou |
| Michou uses it for one evening | the handoff's own reviewer step | pending Michou |

The five states were each drawn and checked: live with an open intent (`live-2.png`), blocking with the halt's detail open (`blocking.png`), disconnected (`disconnected.png`), and empty (`empty.png`). Calm and the `?` overlay (`keys.png`) were checked too. In every run, the console showed only the expected failed fetches after the server was stopped.

`make check`: 605 passed, lint 0 blocking.

## Deviations, each the builder's choice where the design is silent or the data is absent
- **No app icon is designed at `11b686b`.** `icon.png` is drawn from the approved palette alone: the ground, the cyan live frame, and three timeline rows. Generated by `logs/scratch/handoff-0037/make_icon.py`. Scored stakes 2 × edge 0.6 = 1.2: for the approval screen.
- **The font:** every board loads JetBrains Mono from Google Fonts. The page names it first and falls back to system monospace, so nothing is fetched.
- **Portraits:** the server serves only the four routes, so the Tray is drawn in its calm form (its own rule: "Calm hides every portrait and leaves the words").
- **Board 5's 150 s escalation and timeout bar** would have the page decide a state from data the API lacks. They are omitted; elapsed time is shown.
- **Data not in `/api/events` is named, never guessed:** strike counts, open handoff, last review, quotas and the system facts. Each prints `not supplied by /api/events` or `—`. (`payload_sha256` is in the API, `build_view` keeping every field; the first build wrongly labelled it absent, review cycle 3 F10. The detail now shows the returned hash.)
- **Header counts** are of the events and runs the page holds, not ledger totals.
- **Disconnected** prints `<host> · no response`, since a browser cannot tell refused from timed out.
- **`w`** (desk → wall → station) is approved but unbuilt; see review cycle 3 F11.
- **The `?` overlay** draws the key map as board 7's four legend panels, not its drawn 48 px keyboard.
- **Run state map:** the server returns states only for runs touched or still open (review cycle 1 F3), so the page merges `runs` rather than replacing it, keeping a closed run's header facts.

## Outputs widening (recorded in AUDIT-0112, carried here)
`tests/test_smoke.py` (accepted by Cowork) and `tests/station_equivalence.py` (the arbiter's tracked closing check).

## Review cycle 3 (AUDIT-0118, BLOCK), fixed
Checked in the browser against a scratch ledger of 61 events: the 40 samples, 20 notes, and one trace event whose parent is the first sample.
- **F7:** a trace row whose parent the page does not hold (outside the window or evicted) was hidden with nothing to expand it from. It now hides only while its parent is held. In the browser, that trace row shows.
- **F8:** with `since`, `build_view` returned the newest `limit` events after the cursor, so a burst of more than 50 between polls skipped events: an intent's outcome could be lost for good. With `since` it now returns the oldest `limit` after the cursor, and successive polls walk every event in order. The regression `test_polling_with_the_cursor_never_skips_an_event` is red on the pre-fix code, where the first poll misses the outcome.
- **F9:** the runs pane had no selection of its own. `j` and `k` now move within the pane while it is open, and `Enter` filters to the selected run. In the browser, `a` `j` `Enter` filtered to the second of the open runs.
- **F10:** the detail now shows the returned `payload_sha256` (`6c794d15…161c9e` on a sample event).
- **F1 (advisory), the fifty-event boundary:** with 61 events held, the first page draws exactly 50 (`test_the_first_page_is_the_newest_fifty_of_more`, and in the browser).
- **F11 (the approved `w` binding): ruled outside the mandate by the arbiter, held for Michou** (ledger `01M5TY4SX0CHXS0GRXA2NZXMR6`; not a strike).
  - **The conflict:** HANDOFF-0037 asks for the keyboard map as approved, and the design reader at `11b686b` binds `w` to desk → wall → station. But its scope is a read-only timeline and nothing else, its routes are four, and it loads no remote asset (§3). The station needs three.js, vendored only under HANDOFF-0044, a proposal. Either reading overrides something Michou approved.
  - **Michou chooses:** amend 0037 to defer `w` to a follow-up handoff that names the binding in its acceptance (F11 then becomes advisory), or widen 0037 to the wall, the station, their routes and the vendored module.
  - **Meanwhile:** `w` stays unbound, and the `?` map lists it under `Approved · deferred`, not as Phase 2.
  - **Michou's decision, 2026-10-25:** defer `w` to a follow-up handoff, filed with or after HANDOFF-0044's adoption, whose acceptance names the binding. The amendment to HANDOFF-0037 is drafted as `logs/scratch/handoff-0037/handoff-amendment-f11.diff` for Cowork. With it applied, F11 is advisory under that condition.
- **F12 (cosmetic, deferred):** the page is 540 lines in one inline file, and its effects are not named by ADR-015's prefixes. Splitting it means a build step or extra routes, which the handoff's one-file, four-route shape rules out. Left for the weekly review.

## Deferred, not a gap in the page
CDH-0030, the WebKit check, has not run. Michou's approval defers it to the Tauri ADR.

## Left open
- Michou applies `logs/scratch/handoff-0037/cockpit-reader.diff`, installs the page to the Dock, and uses it for one evening.
- AUDIT-0114 F5's remaining clause is closed by this cycle; F4 and F6 are fixed.
- Decisions the page spec raised for Michou:
  - whether "halted" should read for any blocked run (the board equates the two);
  - whether the header counts should say "held";
  - a server-side addendum for strike state;
  - the focus tint following the row's chip.
