---
id: AUDIT-0044
type: report
status: final
handoff: HANDOFF-0033
author: codex
source: inferred
sources: ["HANDOFF-0033", "staged diff sha256 f721ee242139bb8fbb2c9c796d619c307ab0d60ba0451f8ed13023c2353ea132"]
tier: 2
created: 2026-10-09T22:53:27-07:00
period: 2026-10-09
review_cycle: 2
reviewer: gpt-6-astra
verdict: BLOCK
open_blocking: [F1, F2, F4, F6, F8]
---

# Review of HANDOFF-0033, cycle 2

Reviewer `gpt-6-astra` via `codex exec --json -s read-only`, diff sha256 `f721ee242139bb8fbb2c9c796d619c307ab0d60ba0451f8ed13023c2353ea132`. Verdict **BLOCK**: blocking 5, transient 0, cosmetic 1, advisory 0 (resolved rows excluded). Written by `kgme review`; the reviewer's text is verbatim below.

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_io.py:164` | Ancestor checks now reject pre-existing links, but hashing and deletion still use ordinary pathnames after the recheck. Replacing `memory/agent/brief` with a link to `docs` between lines 164 and 177 can redirect deletion to a human document. The replacement test runs before the recheck and misses this interval. | Anchor traversal and deletion to directory descriptors opened without following links. Test replacement after the final check, including between hashing and unlinking. |
| F2 | blocking | `kgme/clean_io.py:112` | The payload and `closed:` marker fix first-outcome blindness, but recovery remains incomplete. An interrupted deletion receives an outcome without size or hash, and the payload stores no file hash. Recovery also parses `reconciled #2:` as `#2:`, then compares it with `#2`; interruption before the close therefore produces a duplicate outcome on restart. | Persist the required deletion metadata before unlinking and restore it during reconciliation. Parse path numbers consistently. Test complete recovered metadata and interruption during reconciliation. |
| F3 | blocking, resolved | `kgme/clean_io.py:181` | Deletion now stops on the first caught failure or changed entry. The regression test checks that subsequent files remain untouched. | No further fix required for this finding. |
| F4 | blocking | `kgme/clean_read.py:44` | Both walks now collect traversal errors, but entry metadata failures still escape unrecorded. A directory with mode `0400` permits listing names but denies `lstat` of its children; `read_entry()` raises outside the error collector, before any classified plan outcome. The mode `000` test covers only the walk failure. | Collect metadata and root-probe errors as plan refusals. Add unreadable-root and readable-but-unsearchable-directory tests. |
| F5 | blocking, resolved | `kgme/clean_io.py:241` | Refused plans now receive blocking outcomes in both modes. The symlink test exercises default dry run and `--yes`, verifying that protected files remain untouched. | No further fix required for this finding. |
| F6 | blocking | `kgme/clean.py:169` | Size and hash now precede the shortened path, but the 200-character budget ignores subsequent ledger redaction. A long allowed path ending in `key=x` expands a full summary to 214 characters; `ledger.append()` rejects it after unlinking, leaving no deletion outcome. The regression deliberately avoids redaction. | Budget against the redacted summary and validate it before deletion. Add a long-path test whose synthetic filename expands during redaction. |
| F7 | cosmetic | `kgme/clean_io.py:90` | The previously named effects were renamed, but the new `_unclosed_intents()` reads the ledger without an ADR-015 effect prefix. | Rename it `read_unclosed_intents` and update its caller. |
| F8 | blocking | `kgme/clean_io.py:86` | The new payload writer bypasses the path guards. With `logs/scratch/payloads` linked to `docs` or an external directory, `clean agent --yes` writes its plan there and proceeds. Checking only the deletion candidates does not protect this new write effect. | Guard payload creation through checked directory descriptors without following links, refuse before deletion, and test a linked payload directory while cleaning another target. |

## Verdict

BLOCK

## Reviewer text

## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking | `kgme/clean_io.py:164` | Ancestor checks now reject pre-existing links, but hashing and deletion still use ordinary pathnames after the recheck. Replacing `memory/agent/brief` with a link to `docs` between lines 164 and 177 can redirect deletion to a human document. The replacement test runs before the recheck and misses this interval. | Anchor traversal and deletion to directory descriptors opened without following links. Test replacement after the final check, including between hashing and unlinking. |
| F2 | blocking | `kgme/clean_io.py:112` | The payload and `closed:` marker fix first-outcome blindness, but recovery remains incomplete. An interrupted deletion receives an outcome without size or hash, and the payload stores no file hash. Recovery also parses `reconciled #2:` as `#2:`, then compares it with `#2`; interruption before the close therefore produces a duplicate outcome on restart. | Persist the required deletion metadata before unlinking and restore it during reconciliation. Parse path numbers consistently. Test complete recovered metadata and interruption during reconciliation. |
| F3 | blocking, resolved | `kgme/clean_io.py:181` | Deletion now stops on the first caught failure or changed entry. The regression test checks that subsequent files remain untouched. | No further fix required for this finding. |
| F4 | blocking | `kgme/clean_read.py:44` | Both walks now collect traversal errors, but entry metadata failures still escape unrecorded. A directory with mode `0400` permits listing names but denies `lstat` of its children; `read_entry()` raises outside the error collector, before any classified plan outcome. The mode `000` test covers only the walk failure. | Collect metadata and root-probe errors as plan refusals. Add unreadable-root and readable-but-unsearchable-directory tests. |
| F5 | blocking, resolved | `kgme/clean_io.py:241` | Refused plans now receive blocking outcomes in both modes. The symlink test exercises default dry run and `--yes`, verifying that protected files remain untouched. | No further fix required for this finding. |
| F6 | blocking | `kgme/clean.py:169` | Size and hash now precede the shortened path, but the 200-character budget ignores subsequent ledger redaction. A long allowed path ending in `key=x` expands a full summary to 214 characters; `ledger.append()` rejects it after unlinking, leaving no deletion outcome. The regression deliberately avoids redaction. | Budget against the redacted summary and validate it before deletion. Add a long-path test whose synthetic filename expands during redaction. |
| F7 | cosmetic | `kgme/clean_io.py:90` | The previously named effects were renamed, but the new `_unclosed_intents()` reads the ledger without an ADR-015 effect prefix. | Rename it `read_unclosed_intents` and update its caller. |
| F8 | blocking | `kgme/clean_io.py:86` | The new payload writer bypasses the path guards. With `logs/scratch/payloads` linked to `docs` or an external directory, `clean agent --yes` writes its plan there and proceeds. Checking only the deletion candidates does not protect this new write effect. | Guard payload creation through checked directory descriptors without following links, refuse before deletion, and test a linked payload directory while cleaning another target. |

## Verdict

BLOCK with 5 open blocking findings.

## Notes

Reviewed SHA-256 prefix: `f721ee242139bb8f`, matching `review.sha`.

All 5 handoff acceptance items have tests. The builder reports 19 passing clean tests; I did not run tests or modify files. The report documents the unrelated gate failure and use of `--skip-check`.

The 3 clean modules contain 202, 135, and 279 lines, with module docstrings describing purpose, inputs, outputs, and effects. The patch introduces no dependencies, subprocess calls, `shell=True`, or TODOs. HANDOFF-0034 claims in the shared report concern implementation outside this patch and were not validated.

## Escalation

```
ESCALATION HANDOFF-0033: review loop halted after 2 cycles.
What failed: 4 root causes survived a fix cycle: F1, F2, F4, F6. Class: blocking.
Evidence:
  F1 `kgme/clean_io.py:164`: Ancestor checks now reject pre-existing links, but hashing and deletion still use ordinary pathnames after the recheck. Replacing `memory/agent/brief` with a link to `docs` between lines 164 and 177 can redirect deletion to a human document. The replacement test runs before the recheck and misses this interval.
  F2 `kgme/clean_io.py:112`: The payload and `closed:` marker fix first-outcome blindness, but recovery remains incomplete. An interrupted deletion receives an outcome without size or hash, and the payload stores no file hash. Recovery also parses `reconciled #2:` as `#2:`, then compares it with `#2`; interruption before the close therefore produces a duplicate outcome on restart.
  F4 `kgme/clean_read.py:44`: Both walks now collect traversal errors, but entry metadata failures still escape unrecorded. A directory with mode `0400` permits listing names but denies `lstat` of its children; `read_entry()` raises outside the error collector, before any classified plan outcome. The mode `000` test covers only the walk failure.
  F6 `kgme/clean.py:169`: Size and hash now precede the shortened path, but the 200-character budget ignores subsequent ledger redaction. A long allowed path ending in `key=x` expands a full summary to 214 characters; `ledger.append()` rejects it after unlinking, leaving no deletion outcome. The regression deliberately avoids redaction.
  F8 `kgme/clean_io.py:86`: The new payload writer bypasses the path guards. With `logs/scratch/payloads` linked to `docs` or an external directory, `clean agent --yes` writes its plan there and proceeds. Checking only the deletion candidates does not protect this new write effect.
Options: override (kgme review override --handoff HANDOFF-0033 --reason ...), reject (revert the working tree), retry (fix, then override, then kgme review again); a disputed class goes to the arbiter claude-opus-5-5 once, recorded with kgme review rule.
Recommended default: override and continue when the remaining findings are understood; reject when they are not.
If you do nothing: nothing is committed.
```
