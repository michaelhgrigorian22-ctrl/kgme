---
id: AUDIT-0083
type: report
status: final
handoff: HANDOFF-0055
author: claude-code
source: inferred
sources: ["HANDOFF-0055", "kgme/merge.py", "kgme/approve.py", "tests/test_merge.py", "tests/test_approve.py", "logs/scratch/handoff-0055/dry-run.txt"]
tier: 2
created: 2026-10-21T21:15:00-07:00
period: 2026-10-21
---

# HANDOFF-0055: the design track lands on `main` continuously; approval on a commit

## What was built
- **`kgme merge design [--dry-run] [--base <checkout>]`** (`kgme/merge.py`).
  - **Main checkout:** it is resolved as the ledger resolves it (`ledger.read_main_checkout`), so the hook may start it from the design worktree.
  - **Nothing to do:** when `design` holds no commit `main` lacks, it writes nothing.
  - **The trial:** a temporary local clone at `main` runs `git merge --no-ff design` (no hook) and the trial tree's `make check`, and the clone is removed however it ends. A red trial writes a `blocking` outcome naming the first failed test and saves the full output to `logs/scratch/merge/trial-<sha>.log`; `main` is untouched.
  - **The lanes:** a merge that changes any path outside them is refused, every path named, with the trial's result.
  - **The landing:** only at a quiet point: on `main`, at the commit the trial tried, nothing staged, no `index.lock`, no merge, rebase, cherry-pick, or revert in progress. Not quiet is a `transient` outcome, and the next trigger retries. What lands is the trial's own merge commit (message `merge: design <sha> (kgme merge)`, the main checkout's identity), fetched into the main repository. It lands by `git merge --ff-only` in the main checkout: its first parent is the tested `main`, so git refuses the fast-forward when `main` has moved (a fresh trial follows, cycle 4 F13) and any merge while one is unfinished (cycle 5 F17), and it moves the ref, index, and tree under its own lock as any merge does (cycle 5 F16). `run_merge` then pushes through `kgme sync`, since a `git merge` fires no post-commit hook.
  - **Records:** one intent and one outcome per run, keyed `merge:design:<full sha>`. A dry run records nothing.
  - **Concurrency:** a lock in the git directory (`kgme-merge.lock`) keeps two hook runs from trying the same merge.
- **Pure half:** `lane_paths` (a lane ending in `/` holds its folder, any other is a glob on the whole path) and `is_quiet`. The lanes come from `kgme.toml [tracks.design] lanes`, and until that diff is applied, from a default equal to §1.
- **`kgme approve --what <name> --sha <commit> [--note "<words>"]` and `kgme approve --show <name>`** (`kgme/approve.py`).
  - **The event:** one `approval`, source `human`, actor `michou`, job `approve`, key `approve:<name>:<full sha>`. The full sha sits in the key because the ledger's redactor replaces any run of 40 or more such characters in a summary.
  - **Refusals:** a commit not on `main`, and any agent harness marker.
  - **The markers, read in each harness on 2026-10-21:** Claude Code sets `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT`; Codex sets `CODEX_SANDBOX`, `CODEX_THREAD_ID`, and `CODEX_SESSION_ID`. `CODEX_MANAGED_BY_NPM` is left out, since an npm wrapper may set it in an ordinary terminal.
  - **`--show`:** prints the newest approval's time, full commit, and words.
- **`kgme/cli.py`:** the two subcommands, dispatched through one thin `run_track`. `tests/test_smoke.py` lists them.

## Acceptance test
All in temporary repositories (`tests/test_merge.py`, `tests/test_approve.py`; 29 tests, all pass, about 15 seconds):
- **In-lane commit:** a design commit inside the lanes lands on `main` as a two-parent merge with the stated message, intent and outcome `ok`, the trial removed.
- **By the hook:** with the hook line installed in a fixture (a stand-in check), a commit on `main` lands the waiting design commit in the background within the minute.
- **The production path, measured (cycle 1 F8):** in a temporary clone of this repository with a bare origin, the drafted post-commit hook, and the real `make check` in the trial, from the state after Michou's first manual merge, one design SVG commit landed on `main` **61 s** after the trigger commit and was pushed (`logs/scratch/handoff-0055/f8-measure.txt`). That missed the handoff's original one-minute bound by 1 s: the trial's `make check` alone is about 58 s. Michou's ruling (option A, ledger `01M5H4F2VTTE7RGGDAKVKNJZV9`): the bound is within about two minutes, one `make check` plus margin, so the full check stays the gate. The measured 61 s meets it.
- **From the design worktree:** a run from the worktree merges in the main checkout, and the events land in the main checkout's ledger only.
- **Outside the lanes:** a design commit touching `control/review/` is refused, the path named with "trial green", `main` unchanged, outcome `refused`.
- **Red trial:** `main` is untouched, outcome `error`/`blocking`. The default check is the trial tree's own `make check`.
- **Not quiet:** with a staged file, the run waits (`transient`, `main` unchanged); after the commit, the next run lands it.
- **Dry run:** records and merges nothing.
- **`kgme approve` under each of the five markers:** refused, no event. Live from this Claude Code session: `kgme approve: refused: CLAUDECODE is set, so an agent harness runs this; an approval is Michou's, from his own terminal`, exit 2.
- **A commit not on `main`, or none at all:** refused.
- **From a terminal with no marker:** records the event, resolves a short sha to the full one, and `--show` prints the newest.
- **Not tested by me:** `kgme approve` from Michou's own terminal; that is his to run.

## The real branch, dry run (`logs/scratch/handoff-0055/dry-run.txt`)
`kgme merge design --dry-run` on `design` `0c9f89237eb3` (40 commits) into `main` `ea1737f2cfad`: **trial green**, but the merge changes 7 paths outside the lanes, all under `control/review/`:
- `control/review/codex-builder-prompt.md`
- `control/review/design-prompt.md`
- `control/review/design-reference/ui-ux-pro-max/LICENSE`
- `control/review/design-reference/ui-ux-pro-max/PROVENANCE.md`
- `control/review/design-reference/ui-ux-pro-max/data/stacks/threejs.csv`
- `control/review/design-reference/ui-ux-pro-max/data/ux-guidelines.csv`
- `control/review/design-reference/ui-ux-pro-max/references/quick-reference.md`

So the first merge is Michou's, by hand (`git merge --no-ff design` in his terminal), as the handoff foresaw. After it, design commits inside the lanes land by themselves.

## Decisions made on the route (ADR-023 scores, stakes × edge)
- **The trial is a temporary local clone, not a worktree** (3 × 0.3 = 0.9, for the approval screen).
  - **What forced it:** the first real dry run in a worktree was red, and so is plain `main` in any worktree. A worktree's hooks and ledger resolve to the main checkout since HANDOFF-0047, so four tests that need their own checkout fail there: `test_paths_worktree::test_a_worktree_resolves_to_its_main_checkout`, the two hook tests in `test_hooks.py`, and `test_guard_loop::test_the_live_guard_refuses_the_charter_write_as_a_blocking_outcome`. Worse, the trial's test events would land in the main checkout's `ledger-test` streams.
  - **Why a clone:** a clone (`git clone --shared`, detached at `main`, `core.hooksPath` set as `make setup` sets it, after the merge) is its own main checkout: green as a fresh clone is, nothing reaching the real one.
  - **Why not the tests:** making the four tests worktree-aware would change what they assert, outside this handoff's Outputs.
  - **Seam:** `run_trial` alone.
- **Hook git variables are dropped at entry** (1 × 0.1). Started from a commit hook, git exports `GIT_INDEX_FILE` and others, which made the trial's git commands act on the committing checkout; found by the hook test.
- **`--base`** (1 × 0.1): the hook passes the committing checkout, as it does to `kgme sync`; without it the command resolves the checkout that holds the code.
- **A red trial is `blocking`; outside the lanes is `refused`/`advisory`** (1 × 0.2): red needs a fix on `design`; outside the lanes needs only Michou's hand.
- **`kgme/cli.py` grows to 388 lines** (2 × 0.2): it was already over the size convention (F17 of HANDOFF-0047, for the weekly review). The new code adds one dispatcher; the logic is in the two modules.

## Review
Cycle 1 (AUDIT-0084): BLOCK, eight blocking findings, all accepted.
- **Fixed, red first** (`logs/scratch/handoff-0055/red-c1.txt`, 10 failed):
  - F1: the merge lands the tested commit, never the branch name.
  - F2: paths are NUL-delimited with renames off.
  - F3: the run pushes its merge through `kgme sync`, since a `git merge` fires no post-commit hook.
  - F4: a waiting trigger waits; heads are read under the lock; a `main` that moved during the trial is tried again, up to three times.
  - F5: every failure after the intent closes it, and open intents are reconciled at the start.
  - F6: approval names are plain and matched whole.
  - F7: the newest approval is by instant, then by id.
  - F9 and F10, the naming and the markers.
- **F8, measured and put to Michou:** 61 s on the production path, against the handoff's one minute.

Cycle 2 (AUDIT-0085): BLOCK on F5, F8, and F11.
- **F11:** a check that ran past its bound was a `blocking` red trial; it now raises to the attempt's handler and closes as `transient`.
- **F5:** a run that died after its merge left an intent no later run closed, because the no-work return came before the reconciling. Now a run with open intents takes the lock and reconciles first, closing a landed one as `ok` ("is on main") and any other as `transient`.
- Red first for both (`logs/scratch/handoff-0055/red-c2.txt`), and a git timeout is shown closing with one outcome too.
- **F9:** the remaining helper names.
- **F8:** Michou ruled option A: the bound is within about two minutes. He took the recommendation.

Cycle 3 (AUDIT-0086): BLOCK on F12.
- **The finding:** a design trigger ran the committing worktree's code, and when that held `kgme/merge.py`, the CLI read that worktree's `kgme.toml`, so a branch's own lanes or check could govern a merge into `main`.
- **The fix:** `kgme merge` now reads the main checkout's `kgme.toml` whichever checkout starts it; the applied hook runs the main checkout's code.
- **Red first** (`logs/scratch/handoff-0055/red-c3.txt`): the design-worktree test failed against the earlier hook draft. The branch-`kgme.toml` test passed against the pre-fix CLI too, since a test process runs the main checkout's code, so it guards the rule rather than reproducing the bug.
- **Cycle 3 saw none of the applied diffs,** which were staged after it started; cycle 4 reviews them with the code.
- **Cowork's advisory, taken:** a design head whose newest outcome is a lane refusal is skipped without a trial or an event until the head moves, so an out-of-lane head no longer runs `make check` and writes another refusal on every trigger. A dry run still runs the trial.

Cycle 4 (AUDIT-0087): BLOCK on F13.
- **F13:** a commit on `main` between the quiet check and `git merge` would have landed, and been pushed, a merge on an untested first parent; ordinary commits do not take the merge lock. Red first (`logs/scratch/handoff-0055/red-c4.txt`): one trial, and the landed merge's first parent was the commit that raced in. Now the trial's own merge commit lands, by compare-and-swap of `main` from the tested commit, under the main checkout's `index.lock` (`write_landing`), and a moved `main` gets a fresh trial: two trials, the second on the new `main`, a clean tree after.
- **F14 (advisory), taken:** the branch-settings test replaces the lanes instead of duplicating `[tracks.design]`, and the design-hook test now commits a prompt under `control/review/` beside a branch `kgme.toml` that widens the lanes to `control/`: the main checkout's lanes refuse it.
- **F15 (cosmetic):** `kgme/merge.py`'s docstring now says the run pushes through `kgme sync`. The same sentence in `docs/readers/merging.md`, and its "the check's last line", are a human path: a two-sentence diff for Michou in `logs/scratch/handoff-0055/merging.md.diff`.

Cycle 5 (AUDIT-0088): BLOCK on F16 and F17, both in the landing cycle 4 introduced.
- **F16:** an exception after `main` moved and before the index was installed would have left the checkout inconsistent, with no repair.
- **F17:** the locked recheck ignored an unfinished `--no-commit` merge.
- **The fix, one for both and for F13:** the hand-rolled landing (`index.lock`, `update-ref`, `read-tree`) is replaced by `git merge --ff-only <the trial's commit>`. Red first (`logs/scratch/handoff-0055/red-c5.txt`): a `--no-commit` merge started after the quiet check, and `main` still moved; a landing that fails mid-way. Now the unfinished merge is left alone (`transient`, `MERGE_HEAD` kept), a failed landing leaves ref, index, and tree as `HEAD` and the next run lands, and the F13 race still gets a fresh trial.
- **F15:** still the reader diff for Michou (`logs/scratch/handoff-0055/merging.md.diff`).
- **Size:** `kgme/merge.py` was 387 lines, over ADR-015's convention; for the weekly review with HANDOFF-0047's F17.

Cycle 6 (AUDIT-0089): BLOCK on F16 (its second cycle) and F18.
- **F16:** git installs the index before it moves the ref, so a held `refs/heads/main.lock` left `main` unmoved with the trial's tree staged, a `transient` outcome, the trial ref deleted, and every later run waiting forever.
- **F18:** a branch switch inside the landing advanced that branch and wrote a false `ok`.
- **To the two arbiters before any patch** (F16 had stood two cycles; F18 shares its root: no git primitive binds "advance main and update its checkout" against a person operating the same checkout). Both chose option A, bounded detection with no automatic reset in Michou's checkout:
  - `claude-opus-5-5`: both blocking, ledger `01M5H7A51269Q555J9C5ZCT9RX` and `01M5H7A54JQ9DM778F7NDC0ABK`.
  - `claude-fable-5-1`, concurring on A, classed both advisory: "full recovery (B) crosses ADR-004 and is a barred third mechanism".
- **Executed:**
  - **Before:** `refs/heads/main.lock` joins the quiet set, and `write_landing` reads the quiet point and the branch again just before `git merge --ff-only`.
  - **After, whatever git answered:** it checks three facts: the checkout is on `main`, `main` is the trial commit, the index matches HEAD.
  - **On a mismatch:** one `blocking` outcome naming the state (which branch moved, whether the trial's tree is staged) and the repair commands; `refs/kgme/merge-trial` kept; no sync; nothing reset.
  - **The latch** is Fable's (Opus's would wait for the ref's removal by hand): later runs refuse, writing nothing, while that outcome is newest and the checkout is not quiet, and resume by themselves once it is.
- **Red first, failures injected inside git's sequence** (`logs/scratch/handoff-0055/red-c6.txt`): a ref lock taken as the fast-forward starts; a stale ref lock before it; a branch switch as it starts. Now: blocking, named, latched, and Michou's repair (`git merge --ff-only refs/kgme/merge-trial`) lands it, after which the next run has nothing to do; a stale lock is a wait that touches nothing; a switch is blocking, names the branch, and writes no `ok`.
- **Residual, recorded:** a commit, switch, or ref lock in the milliseconds between the final recheck and git's own sequence is not prevented; it is detected and named, never repaired by kgme.

Cycle 7 (AUDIT-0090): BLOCK on F16 and F19, two paths option A's checks missed (the arbiters' test for reopening).
- **F16:** a landing that raised (a timeout) skipped the three post-checks; now they run after an exception too, and only a checkout verified unchanged stays `transient`.
- **F19:** the kept trial shared the disposable trial ref, so a dry run or a newer design head could replace it under the recorded repair command. A blocked landing is now kept under its own `refs/kgme/merge-blocked/<sha>`, which the outcome's repair command names. The latch refuses every design head, writing nothing, while such a ref remains and the checkout is not quiet. A kept ref is deleted once its commit is on `main`, that is, once the repair has landed.
- **Red first** (`logs/scratch/handoff-0055/red-c7.txt`): a timeout raised after git staged the trial; a blocked landing followed by a dry run and a new design head. Now: one blocking outcome with the trial kept; the kept ref unchanged through both; after the repair, the kept ref cleared and the newer head landed.

Halt and override: F16 had stood blocking in cycles 5, 6, and 7, so the loop halted; Michou recorded the override (`01M5H96ZPRCB7MZM56CG3JPY7M`). Cowork, arbiter, ruled before cycle 8 that if F16 returned with another landing failure path it would not be patched, and the simpler design would be taken instead.

Cycle 8 (AUDIT-0091): BLOCK on F16 again: after a partial landing, a timeout in the post-check itself escaped as `transient` before any kept ref existed. As Cowork ruled, the path is not patched; the design changes:
- **The kept ref first:** the recovery ref (`refs/kgme/merge-blocked/<design sha>`) is written before git is invoked on the main checkout.
- **Blocking after git:** once git is invoked, only a verified landing counts; a git error, a timeout, any unverified end, or a post-check that cannot run is one `blocking` outcome with the ref kept and the latch.
- **A verified landing** deletes the ref. A kept ref is cleared once its design commit (the kept merge's second parent) is on `main`, by Michou's repair or by a later landing.
- **What is still transient:** moves and waits seen by the rechecks before git is invoked, which touch nothing.
- **The trade, Cowork's:** a failed landing no longer retries by itself; when nothing was touched, the checkout stays quiet, the latch holds nothing, and the next trigger lands it.
- **Red first** (`logs/scratch/handoff-0055/red-c8.txt`): a partial landing whose post-check times out; now one blocking outcome, the ref intact. The cycle-5 test is updated to the new contract: blocking, the ref kept, the next run landing and clearing it.
- **The reader:** its blocked-landing section said "after it has begun changing your checkout" and "once that commit is on `main`"; a two-line diff for Michou (`logs/scratch/handoff-0055/merging.md.diff`).

Cycle 9 (AUDIT-0092): BLOCK on F16: the fallback was incomplete. One diagnostic read (which commit a switched branch received) sat outside the boundary, so a failure there wrote `transient` after a known wrong-branch landing. Every effect after git is invoked, diagnostics included, is now inside it. Red first (`logs/scratch/handoff-0055/red-c9.txt`): the branch-switch case with that read timing out, which now gives one blocking outcome naming the intact kept ref, and no sync.

Cycle 10 (AUDIT-0093): PASS, nothing open blocking.

## Diffs (human paths): applied
Michou applied and staged all four on 2026-10-21; they are in this commit.
- **`kgme.toml` and `.claude/settings.json`:** the drafts below, as written.
- **`control/git-hooks/post-commit`:** Cowork's correction of the draft. My first draft checked the committing checkout for `kgme/merge.py`, and the design branch has none, so no design commit would ever have triggered a merge. `merge()` now resolves the main checkout (`git rev-parse --path-format=absolute --git-common-dir`, minus `/.git`) and checks and runs `kgme/merge.py` from there. `test_c3_f12_the_design_worktree_runs_the_main_checkouts_merge` runs the applied hook from a design worktree whose own tree has no `kgme/merge.py`; the commit lands on `main`.
- **`docs/readers/merging.md`:** Cowork applied it from the draft. The two lanes that do not exist on `main` yet are described in words, for the coherence check, and the stop line reads "remove the two merge calls".

**One step remains on Michou's machine.** The design worktree (`~/Projects/KGME/design`) has the relative `core.hooksPath control/git-hooks`, so it runs the `design` branch's own copy of the hook, which has no `merge` call; it gets one only when `design` merges `main`. Until then, a design commit triggers nothing, and a waiting one lands after the next commit on `main`. The test above wires its worktree the recommended way, per-worktree config pointing at the main checkout's hooks:
```
git config extensions.worktreeConfig true
git -C ~/Projects/KGME/design config --worktree core.hooksPath /Users/michaelgrigorian/Projects/KGME/brain/control/git-hooks
```
The main checkout's own `core.hooksPath`, which `make check` reads, is unchanged. The other way is for the design session to merge `main` once.

The drafts, for the record (`logs/scratch/handoff-0055/`):

`kgme.toml` (`kgme.toml.diff`), appended:
```toml
[tracks.design]
# The design track's lanes (HANDOFF-0055 §1): `kgme merge design` lands a design commit on main
# by itself only when everything it changes is inside them and the trial's `make check` is
# green. A folder ends in `/`; anything else is a glob on the whole path. HANDOFF-0042 reuses it.
lanes = [
  "docs/design/",
  "docs/handoff/cockpit-design/",
  "docs/audit/cockpit-design/",
  "docs/readers/cockpit-design*.md",
  "tests/test_design_*.py",
]
```

`control/git-hooks/post-commit`: superseded by Cowork's correction, applied (above). As applied, `merge()` runs after the atlas on `design` (in the background subshell off `main`) and after the atlas on `main` (in the sync subshell, after the push).

`.claude/settings.json` (`settings.json.diff`): `"Bash(*kgme approve*)"` appended to `permissions.deny`.

`docs/readers/merging.md` (new, `logs/scratch/handoff-0055/merging.md`): what merges by itself, the trial, the lanes, the quiet point, approving, stopping it.

## Not done, and why
- **The ADR-022 §3 addendum and the amendments to 0036 and 0037** (§5) were committed at adoption, in `f8609e9`.
- **The design track's README and builder prompt** are the design session's.
- **The first merge** is Michou's, by hand, after this commit.
