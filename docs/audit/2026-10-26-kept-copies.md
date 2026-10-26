---
id: AUDIT-0132
type: report
status: final
handoff: HANDOFF-0052
author: claude-code
source: inferred
sources: ["HANDOFF-0052", "kgme/brief_kept.py", "kgme/brief.py", "kgme/brief_io.py", "kgme/capture_recover.py", "kgme/clean_kept.py", "jobs/brief/manifest.toml", "jobs/brief/job.md", "tests/test_brief_kept.py"]
tier: 2
created: 2026-10-26T01:57:16-07:00
period: 2026-10-26
---

# HANDOFF-0052: kept copies in the brief

The morning brief gains `## Kept copies`, which lists every copy `kgme capture` kept under `memory/` (`.<name>.capture-<intent id>`). A past day's note gets no later capture, so a save kept beside one is found the next morning, not only when someone runs `kgme clean kept`.

## What was built
1. **The section** (§1):
   - **Pure half, `kgme/brief.py`:** `KeptCopy` and `_kept_section`. The section sits between `Friction since last brief` and `Inputs`.
   - **Effects half, `kgme/brief_kept.py` (new):** it walks `memory/` without following links, reads each copy through the brief's own gate (`brief_read.read_gated`), hashes it, and judges it against the hashes its capture recorded in the ledger.
   - **What it prints:**
     - A copy that holds a save its file lacks gets one line: "`<copy>` holds a save `<file>` lacks: merge it by hand, then delete it". The words are the handoff's.
     - A copy no capture recorded adds "(no kgme capture recorded it)", and a copy the gate refuses adds "(could not be checked: …)".
     - The copies still as kept get one line: their count, their total size in bytes, and `kgme clean kept --yes`.
     - With no copies: "No kept copies under memory/.".
   - **Read-only:** the brief deletes nothing.
2. **One rule, not three** (§1, "never a second copy of the rule"). The rule existed twice: `capture_recover.read_divergent` compared a 32-digit prefix, and `clean_kept.read_reason` a 16-digit one. It is now one pure function, `capture_recover.holds_save(digest, recorded)`, which compares at the shorter of the digest's length and the recorded 32. `kgme capture`, `kgme clean kept` and the brief all call it, and the behaviour of the two old callers is unchanged at their lengths. This widens the Outputs by `kgme/capture_recover.py` and `kgme/clean_kept.py`.
3. **The manifest** (§2): `jobs/brief/manifest.toml` gains `memory/**/.*.capture-*` in `read_paths`, a glob `kgme/policy.py` already matches. Nothing else widens. `jobs/brief/job.md` names the input, the section and the read path.
4. **The schedule** (§3) waits for the Phase 3 heartbeat, as the handoff says. Until then the brief's line names the command.

## Design decisions, each recorded
- **A new module, not `brief_read.py`.** `capture_recover` imports `brief_read`, so `brief_read` could not import the rule without a cycle. `kgme/brief_kept.py` sits between them, and `brief.py` stays pure.
- **A copy the gate refuses is named, not skipped.** A symlinked copy, for instance, cannot be shown to be what its capture kept, so it is listed as holding a save, with the gate's reason.
- **An unlistable folder under `memory/` stops the brief,** as an unlistable input folder already does: a brief missing a subtree would say there are no copies.
- **The section is not in `sources:`.** The copies are not notes and carry no id. The section is part of the body, so its content moves the brief's content hash, and a brief whose copies changed is rewritten.

## Acceptance
- **`tests/test_brief_kept.py::test_the_acceptance_test`, the handoff's test end to end on copies `kgme capture` really kept.** It uses a capture vault with a past day's note (2026-10-15) and the friction log, and the brief runs on 2026-10-16. The three copies are made this way:
  - one daily capture keeps a copy of the note, which is then edited after the fact;
  - two friction captures keep two copies, and the first is set to that capture's own bytes, which the second capture read as the file.

  Then:
  - the brief's section names the edited copy and its file, and counts the other two with their total size and the command;
  - `kgme clean kept --yes` refuses and removes nothing;
  - after the edited copy is deleted by hand, it removes the other two, and the next brief says "No kept copies under memory/.".
- **Also:** a copy no capture recorded is named; a symlinked copy is named "could not be checked" and every file under `memory/` is byte-identical after the brief; and the one rule holds at 64 and 16 digits for both recorded values, and refuses an empty digest, an unreadable one and an unrecorded copy.
- **Red on `HEAD`:** the brief has no `Kept copies` section, so the acceptance test fails at its first assertion. `tests/test_brief.py`'s section list gains the section.
- **`make check` passes:** lint 0 blocking, 672 passed with the build in the tree.

## Review cycle 1 (AUDIT-0133, BLOCK on F1), fixed
- **F1:** discovery took only names whose intent id parses (`capture_fs.KEPT_NAME`). A copy such as `.friction-log.md.capture-orphan` falls inside the handoff's `.*.capture-*` and is refused by `kgme clean kept` as unrecorded, yet the brief left it out: alone, the brief said "No kept copies".
  - **The fix:** discovery now takes the glob itself. A name whose id does not parse is a copy no capture recorded, named with its file, which is the name before `.capture-`.
  - **Proof:** red on the cycle-1 module (`logs/scratch/handoff-0052/red-c1.txt`), green after.
- **F2 (advisory):** `kgme/brief.py` is 346 lines with the renderer. It is left for the weekly review: moving its sections out is a split of its own.

## Review cycle 2 (AUDIT-0134, BLOCK on F3), fixed
- **F3:** the wider discovery admitted `..capture-orphan`, whose name names no file. `path.with_name("")` raised before the gate, so one malformed copy stopped the brief. Such a copy is now named with `<folder>/?` and "its name names no file". Red on the cycle-2 module (`red-c2.txt`), green after.
- **F2** stays advisory.

## Review cycle 3 (AUDIT-0135): PASS
F2 stays advisory, for the weekly review. The handoff closes on this PASS.

## Waiting for Michou
- **`logs/scratch/handoff-0052/capture-reader.diff`** (`docs/readers/capture.md`): one sentence, saying the morning brief finds a copy beside a past day's note, plus its `modified` and `sources`. The handoff closes without it, because the reader is not checked by lint.
