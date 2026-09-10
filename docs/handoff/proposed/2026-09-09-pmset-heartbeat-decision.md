---
id: HANDOFF-0012
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
status: proposed
tier: 2
depends_on: HANDOFF-0001
audit_ref: "`pmset -g` shows sleep=0 (never), displaysleep=0; sleep additionally asserted by seven processes including `Claude`."
---

# Handoff 0012 (proposed) — Decide and set `pmset` for the morning heartbeat

## Why
Audit finding 6: sleep is `0` (never); sleep is additionally asserted by seven processes including `Claude`. Uptime 9 days 20 h confirms the Mac has not slept. Phase 0 §3: "Decide whether the Mac stays awake on power so a morning heartbeat actually fires — informed by two weeks of observation." Current setting is a decision by inertia, not intent.

## What
Three options; Michou picks one after two weeks of friction-log data (Phase 0 §4).

- **A. Keep current.** Mac never sleeps; heartbeat always fires. Battery drain when unplugged.
- **B. Sleep unplugged, awake on power.** `sudo pmset -c sleep 0 displaysleep 30`; `sudo pmset -b sleep 5 displaysleep 5`. Heartbeat fires only on power. Long overnight tasks pause on lid close (battery).
- **C. Scheduled wake.** `sudo pmset repeat wakeorpoweron MTWRFSU 07:00:00`. Wakes daily at 07:00. Some Macs fail to wake with lid closed and no external power; needs testing on this M4 Pro.

## Reversibility
`sudo pmset restoredefaults` for the current power source. `sudo pmset repeat cancel` removes scheduled repeats. All three fully reversible.

## Risks
Option B interrupts long-running processes on battery lid-close. Option C wakes regardless of Michou's schedule; confirm with test wake before committing. Any option that lets the Mac sleep also stops `caffeinate` from doing what it does today; verify no tooling depends on `sleep=0`.

## Needs from Michou
Two weeks of friction-log observations first. Then a decision between A/B/C. **Do not run before the observation window closes**; this exists so the decision is on the record.
