---
id: AUDIT-0115
type: report
status: final
handoff: HANDOFF-0057
author: claude-code
source: inferred
sources: ["HANDOFF-0057", "kgme/cheap.py", "tests/test_cheap.py", "logs/scratch/merge/trial-7f1c5ea93c30.log", "logs/scratch/handoff-0057/literal-design-in-trial.txt"]
tier: 2
created: 2026-10-25T17:01:39-07:00
period: 2026-10-25
---

# HANDOFF-0057: the cheap lane's fence denies the main checkout by name, wherever it lives

## What was built
1. **`build_red_profile(export, mains, denied, names)`** (`kgme/cheap.py`). In Seatbelt a later rule wins, so the profile writes its file rules in this order:
   - deny all writes;
   - allow `/private/tmp`, `/private/var/folders` and `/dev`;
   - deny `(subpath <m>)` for each main checkout;
   - allow `(subpath <export>)` last, so an export that sat under a checkout would stay writable. Untested: the fixtures' exports are siblings of their checkouts (`tmp_path/work` beside `tmp_path/repo`), so no test exercises that last rule (review cycle 1 F1, advisory).

   Network and the read denies are unchanged. `write_fix` writes the patch and the red command's output itself, outside the sandbox, after the run, so nothing the red run needs writes under a checkout.
2. **The regression** (`tests/test_cheap.py`): `test_the_red_run_never_writes_the_main_checkout_wherever_it_lives`. A fixture checkout under `tmp_path` has a probe writing into it. The write must be refused, and a write into the export must succeed. It was red before the change (`leak`, `logs/scratch/handoff-0057/red.txt`) and is green after. The existing F1 test is unchanged.
3. **The reader sentence** for the cheap section of `docs/readers/sessions.md`, a human path. It is drafted as `logs/scratch/handoff-0057/sessions-reader.diff` for Michou and applies cleanly.

## Deviation: two checkouts, not one
The handoff names one `main` argument. As written, that would not pass its own acceptance test:
- **The two folders differ in a trial.** In the F1 test, the probe writes into `ROOT`, the checkout running the tests, which in a merge trial is the `mkdtemp` clone. `write_fix` is handed `main=base`, the fixture checkout under pytest's `tmp_path`. Denying `base` alone leaves the trial clone writable.
- **Measured in a fresh clone under `mktemp -d`:** with only the `main` argument denied, the F1 test still leaks (`['refused', 'leak', 'refused']`, `logs/scratch/handoff-0057/literal-design-in-trial.txt`).
- **The fix:** `write_fix` passes both the main checkout it is given and the checkout this code runs from (`paths.root()`). In use they are the same folder; in a trial they are the clone and the fixture.

This keeps the handoff's intent ("never the main checkout, wherever it lives") and its ordering. Scored stakes 2 × edge 0.3 = 0.6: decided and recorded.

## Acceptance
- **`make check` in the real checkout:** green, 601 passed (`logs/scratch/handoff-0057/make-check.txt`).
- **`make check` in a fresh clone** (`git clone . <mktemp -d>/trial`, `core.hooksPath` set as the trial's clone has it, the two changed files laid over `HEAD`): green, 601 passed (`logs/scratch/handoff-0057/make-check-trial.txt`). This is the condition that failed four landings on 2026-10-25.
- **The landing:** the post-commit hook's `kgme merge design` writes an `ok` merge outcome and `main` holds the design commits. Confirmable only after this commit lands, so not in this report: the evidence is the `merge` outcome the hook writes to the ledger, and `git log main` holding the design commits.

## Left open
- Michou applies `logs/scratch/handoff-0057/sessions-reader.diff`.
- Review cycle 1 F1 (advisory): parameterize the regression with an export beneath the checkout, to exercise the final allow rule.
