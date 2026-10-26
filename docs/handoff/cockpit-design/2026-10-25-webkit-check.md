---
id: CDH-0030
type: handoff
created: 2026-10-25T15:35:00-07:00
from: michou
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0029]
design_track: HANDOFF-0036
---

# CDH-0030: The WebKit check

## Outcome and authority

Michou's ruling of 2026-10-25 on the native shell (relayed from the substantive session): Tauri stays open, Electron stays closed, and the decision is made later by its own ADR amending ADR-017, after he has used the Dock version for a couple of weeks. One check now keeps that door open: Tauri on macOS renders with WebKit, not Chrome, so the station page and the boards must hold in Safari. This row is that check. It is a read-only review of the design at the commit of CDH-0029; it changes no design file.

It is `ready` after CDH-0029 is done, so the check sees the sky as it will be approved. Cowork cannot run it: neither its container, its VM nor its browser pane has WebKit. Codex runs on the Mac.

## Do

1. **Drive Safari from the Mac.** `safaridriver` ships with macOS and speaks WebDriver on localhost; no install. It needs Michou's one-time switch, Safari → Develop → Allow Remote Automation (if Develop is hidden: Safari → Settings → Advanced → Show features for web developers). Start it with `safaridriver --port 4444` and talk to it with Python's `urllib` (no new dependency). If remote automation is not enabled, stop and say so in one line: that is Michou's step, not a missing prerequisite to work around.
2. **The station.** Serve `logs/scratch/vendor/` as for CDH-0023 and open `station-local.html?at=19:52:00&speed=1` in Safari at 1440 × 900 and 400 × 700. Check and record:
   - the three.js scene renders (WebGL context created, the deck's edge lines and the planets painted, no WebGL warnings in the page);
   - the chibi SVG symbols render (the `<use>` references across the symbol sheet);
   - every key of the station's map works (`1`–`7`, `a`, `c`, `p`, `r`, `Esc`, `Tab`): the same checks as the CDH-0026 and CDH-0028 harnesses, run through WebDriver;
   - the phosphor palette's contrast, measured on sampled pixels as in CDH-0028, since WebKit composites `backdrop-filter`, bloom and the shader wash differently;
   - `prefers-reduced-motion` and calm;
   - frame intervals over 30 s at ×2, reported beside Chromium's.
3. **The boards.** Load each of the eleven boards through the CSS projection of CDH-0027 (static HTML, no canvas runtime) in Safari at its design size, and record: fonts (JetBrains Mono from Google Fonts and the `ui-monospace` fallback; note which one painted), `clip-path` panels, the `:has()` and `:where()` selectors, the activity columns' CSS variables, the `details` disclosures, the key map, and contrast on sampled text. Chromium's captures from CDH-0027 are the reference.
4. **Record.** The result goes in the implementation report and, as Michou asked, as an audit note in the README's Status section: "WebKit check at `<sha>`: pass" with the numbers, or the list of what breaks. Pass means no change to HANDOFF-0037's canvas. Fail means each break is named with its cause and a fix proposed as a CDH row before canvas approval, because a page that only works in Chrome would force the shell decision early.

## Verify

- Every claim in the report cites a WebDriver screenshot or measurement under `logs/scratch/design-review/cdh-0030/`, hashed.
- `make check` green (nothing in the design changes; the report and README are the delivery).

Report, close out and commit as for CDH-0023, then stop for Cowork.

## Acceptance

- Safari's rendering of the station and the boards is recorded with evidence, and the README carries the audit note.
- Any break is a named, scored row, not a surprise at approval.
