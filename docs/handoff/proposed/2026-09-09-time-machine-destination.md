---
id: HANDOFF-0006
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
status: proposed
tier: 2
depends_on: HANDOFF-0001
audit_ref: "No Time Machine destination configured; latest-backup mount fails."
---

# Handoff 0006 (proposed) — Configure a Time Machine destination

## Why
The audit found `tmutil destinationinfo` empty and `tmutil latestbackup` returning `Error Domain=com.apple.backupd.ErrorDomain Code=17 "Failed to mount destination."`. Charter and ADR-008 both assume Time Machine is running; Phase 0 §3 lists it in the fix-now candidates. Without a destination, the "reversible" property that KGME relies on holds only for content already in git — the 1.8 GB of Finance archives and the 1.8 GB of School archives have no rollback path.

## What
Michou plugs in an external SSD or HDD (or supplies a network share URL). Then:

1. `diskutil list` → identify the target disk (`/dev/diskN`).
2. **Stop and confirm the identifier with Michou verbatim before continuing.**
3. `sudo diskutil eraseDisk APFS "KGME-TM" $DISK` (destructive on the target disk).
4. `sudo tmutil setdestination /Volumes/KGME-TM`.
5. `sudo tmutil enable`; then `tmutil startbackup --auto` and let the first full backup complete (can be hours).
6. Verify: `tmutil destinationinfo`, `tmutil latestbackup`.

## Reversibility
- Setting/removing destination: reversible via `sudo tmutil removedestination <ID>`.
- Erasing the target disk: **not reversible** — anything on the disk before step 3 is lost.

## Risks
Wrong `diskutil` identifier at step 3 erases the wrong volume. Verifying the identifier with Michou before the erase is mandatory. First backup takes hours; interrupting it starts over. Use an external disk, not `/`.

## Needs from Michou
Physical presence, an external disk (128 GB minimum, 1 TB recommended), the sudo password, and explicit verbal confirmation of the `/dev/diskN` identifier before step 3 runs.
