---
id: HANDOFF-0057
type: handoff
created: 2026-10-25T16:46:06-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0053, HANDOFF-0055]
plan_ref: PLAN-PHASE-1 step 7d
---

# Handoff 0057 — The cheap lane's fence denies the main checkout by name, wherever that checkout lives

## Why
HANDOFF-0053's red run executes code the session wrote, so it runs under the session's fence (`build_red_profile` in `kgme/cheap.py`): no network, no read under a denied root, writes only to the export, the temporary folders and `/dev`. The main checkout is refused by omission: it is not in the writable list. That holds on Michou's checkout under `~/Projects/KGME/brain` and fails anywhere under the temporary folders.

`kgme merge design` (HANDOFF-0055) runs its trial in a clone made by `tempfile.mkdtemp` (`run_trial` in `kgme/merge.py`), so in a trial the main checkout *is* under `/private/var/folders`. There, `test_review_f1_the_launchers_red_run_is_fenced_like_the_session` in `tests/test_cheap.py` writes its probe into the checkout, the fence allows it, and the test reports a leak. Four landings in a row failed this way on 2026-10-25 (trials at `c57e5de`, `997a730`, `bcf72af`, `7f1c5ea`; the trial logs are under logs/scratch/merge). The design branch changes nothing under `kgme/` or `tests/`; it is blocked by a latent defect on `main` that 0055's trial surfaced for the first time after 0053 landed at `fe15fb4`. Until it is fixed no design commit reaches `main`, and the canvas approval that HANDOFF-0037's page waits on cannot be named.

The test is right and the fence is loose: a cheap session launched from any checkout under the temporary folders could write it. Fix the fence, not the test.

## What
1. **`build_red_profile` takes the main checkout** (`export`, `main`, `denied`, `names`) and emits, in this order, since in Seatbelt a later rule wins: deny all writes; allow the temporary folders and `/dev`; **deny `(subpath <main>)`**; allow `(subpath <export>)` last, so an export that happens to sit under the main checkout (a fixture's does) stays writable and nothing else under the checkout does. Nothing the red run needs writes under the main checkout: `write_fix` writes the red command's output and the patch itself, outside the sandbox, after the run.
2. **One regression in `tests/test_cheap.py`:** a checkout under `tmp_path` (as `write_cheap_checkout` makes it) with the probe writing into *that* checkout is refused. This reproduces the merge trial's failure in the real checkout; it is red before the change and green after. The existing F1 test stays as written.
3. **One sentence** in the cheap section of `docs/readers/sessions.md`: the red run can write the export, the temporary folders and `/dev`, and never the main checkout, wherever it lives (a diff for Michou).

## Outputs
`kgme/cheap.py`, `tests/test_cheap.py`, `docs/readers/sessions.md` (human path: a diff).

## Acceptance test (under ten minutes)
`make check` is green in the real checkout **and** in a fresh clone under `mktemp -d` (`git clone . <tmp>/trial`, then `make check` there), which is what the merge trial does. After this handoff's commit lands on `main`, the post-commit hook's `kgme merge design` writes an `ok` merge outcome to the ledger and `main` holds the design commits (twelve as of 16:40 PDT, through CDH-0031).

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one profile string, one test, one reader sentence. `git revert`.

## Needs from Michou
Adoption now, ahead of HANDOFF-0044: it is small and it unblocks the design landing and the canvas approval. Applying the `docs/readers/sessions.md` diff.
