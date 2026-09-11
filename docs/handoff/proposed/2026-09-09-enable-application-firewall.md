---
id: HANDOFF-0007
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
tier: 2
depends_on: HANDOFF-0001
audit_ref: "Application firewall disabled (State = 0)."
status: superseded
superseded_by: HANDOFF-0020
reason: "Reissued by Cowork with the amendments from AUDIT-0004 (Codex review), 2026-09-11."
---

# Handoff 0007 (proposed) — Enable the macOS application firewall

## Why
Audit reported `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate` = `Firewall is disabled. (State = 0)`. ADR-008's security posture assumes the firewall is on; the default this machine is running is inconsistent with that assumption. Turning it on is quick and low-cost.

## What
1. `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on`
2. `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsigned on` (allow signed applications automatically — avoids constant prompts).
3. `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsignedapp on` (same, for App Store apps).
4. Optional (recommend): `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on` (drop ICMP/port-scan probes).
5. Verify: `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate` returns `Firewall is enabled. (State = 1)`.

## Reversibility
`sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off` restores the current state. The `--setstealthmode off`, `--setallowsigned off`, etc. reverse the other flags. Fully reversible.

## Risks
Some LAN-adjacent services may prompt on next use: AirDrop, printer discovery, screen sharing, iTunes/Music library sharing, Zoom local-network features, Chrome remote debugging. Signed apps (Zoom, Chrome, VS Code, Warp, Claude, Ollama, Obsidian, Excel, Word) are auto-allowed by step 2, so most will not prompt. Anything unsigned (a hand-built Python binary, an older brew formula) will prompt. Stealth mode may make network diagnostics (ping from another machine) appear as if the Mac is offline — usually desirable.

## Needs from Michou
Sudo password (present). Willingness to click through 1–3 first-run allow prompts as they appear over the next day. Nothing else.
