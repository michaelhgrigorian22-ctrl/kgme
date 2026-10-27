---
id: AUDIT-0147
type: report
status: final
handoff: HANDOFF-0043
author: claude-code
source: inferred
sources: ["HANDOFF-0043", "kgme/loop.py", "kgme/review.py", "kgme/review_run.py", "tests/test_loop.py"]
tier: 2
created: 2026-10-26T18:20:09-07:00
period: 2026-10-26
---

# HANDOFF-0043: `kgme loop`, the supervisor

**State: ready, diffs pending.** The supervisor, the halt measures, the arbiter pair and the toy are built and green. Five human-path files wait as diffs under `logs/scratch/handoff-0043/`, for one commit by Michou. The amendments at adoption (13 to 24) and Michou's rulings of 2026-10-26 bound the work; the withdrawn items were not built.

## Measured first: the second arbiter (amendment 20)
- **Both CLIs accept a second family.** Each candidate answered a one-word prompt with exit 0 on 2026-10-26:
  - `claude -p --model claude-fable-5-1` under claude 2.1.310;
  - `codex exec -m gpt-5.6-sol` under codex-cli 0.164.0.
- **The pair is `claude-opus-5-5` and `claude-fable-5-1`.** Codex is the reviewer (`gpt-6-astra`, alternate `gpt-5.6-sol`), so `gpt-5.6-sol` is the reviewer's own family, and amendment 20 excludes it.
- **The real pair, run once on a toy brief**, through `review_run.run_arbiter` and the staged `arbiter-prompt.md`. Both ruled `blocking`, option "remove the seed", reversible, blast radius 1, each with its reason (`logs/scratch/handoff-0043/arbiter-measure/`).
- **A defect, found by that run and fixed.** `claude`'s `--tools` takes a variadic list, so a brief placed after `--tools ""` was read as a tool name. The first real run gave both arbiters no prompt, and both replies came back empty. The brief now goes in on stdin. The toy's arbiter stub reads stdin as the real call does, and the acceptance test asserts that the brief reaches each arbiter.

## What was built
- **`kgme/loop.py`**: `kgme loop --queue A,B [--workspace PATH] [--stall-minutes 15]`.
  - Its pure functions: `next_handoff`, `live_children`, `is_stalled`, `reset_time`, `halt_reason`, `settle`, `read_stream`, `closing_screen`.
  - Its effects: `run_loop`, `start_caffeinate`, `start_builder`, `read_group`, `kill_group`.
  - The builder is a fresh `uv run kgme session loose --handoff <id> -- --output-format stream-json --verbose` per handoff, run as its own process group in the workspace given (amendment 14). `loose` refuses the main checkout and runs only from a worktree, so creating workspaces stays HANDOFF-0048's job.
  - The run's first intent names the level, the builder's model, and both harness versions (amendments 6 and 10).
  - Its closing outcome names the commit, the audit ids and the stream's usage and cost (amendment 18).
- **`kgme/review.py`**: the three-cycle halt is replaced by amendment 16's three measures, read from the ledger over the window since the last override:
  - (a) a settled ruling, executed, with the same root cause blocking in the next cycle;
  - (b) a diff hash reviewed a second time with no settled ruling between the two reviews;
  - (c) three red gates whose failing count never fell.

  `to_arbiters` names the findings blocking two consecutive cycles with no settled ruling. Strikes, `runs` and survivors stay as telemetry.
- **`kgme/review_run.py`**:
  - `write_gate` records every gate `kgme review` runs as a `gate:` note with its failing count (`review.gate_failures`).
  - `write_halt` is the halt tail, shared by a cycle, a gate and the loop.
  - `run_arbiters` runs the pair (amendments 12 and 20):
    - both arbiters run in parallel, each a fresh read-only `-p` run that exits;
    - each ruling is its own `ruling:<id>@<model>=<class>` note, actor `arbiter.<model>`, with the brief's path and sha256 and the reply in its payload;
    - one settled `ruling:<id>=<class>` follows, through `review_io.write_ruling`, so every older reader keeps working;
    - a split adds a `split:` note for the approval screen.
  - The cycle's dispositions are kept on disk as `review.dispositions`.
- **`kgme/cli.py`, `kgme/cli_parser.py`**: `kgme loop` and `kgme review arbitrate`.
  - `cli_parser.py` is in scope by Michou's ruling: the parser moved there in HANDOFF-0060, after 0043's Outputs list was written.
  - `kgme review` writes a `gate:` note for every gate it runs.
  - The arbiter pair runs only once `[models] arbiters` and the brief exist. Until then `kgme loop` says so and does not arbitrate.

## The amended acceptance test, case by case (`tests/test_loop.py`, 12 tests, about 40 s)
- **The toy closes without a keystroke.** The ledger reads loop intent, red gate, green gate, review BLOCK, green gate, review PASS, loop outcome. Between them the stub builds, and it commits on PASS.
  - Every review, gate and loop event of the handoff sits under the loop's first intent. The stub's own tool events do too, but only because the stub writes `parent` from `KGME_LOOP_PARENT`. A real session's hook events do not read that variable: they form their own tree, which the loop reaches through a `loop:` note naming the session id (AUDIT-0148 F4, ruled advisory; the hook-side parent is proposal HANDOFF-0063).
  - Every failure is classed.
  - The closing screen names the commit, both audit ids and the usage `in=1200 out=340 cost=$0.42`, which the closing payload also holds.
- **The unfixable seed.** Two BLOCK cycles send F1 to the two arbiter stubs: two processes, each given the brief that holds the dispute and the seeded diff.
  - Their agreeing rulings are three events: one per arbiter, then the settlement.
  - The ruling is executed, F1 blocks again, and the run halts with "F1 blocked again after its ruling was executed". There is no commit, and the queue goes on to a second toy that closes.
- **Splitting stubs** (`blocking` at blast 3, `advisory` at blast 1, both reversible) settle `advisory`, with a `split:` note "for the approval screen". A second arbitration of the same finding is refused.
- **The stall switch.** A silent builder, past the stall with no live call, is killed with its whole group: SIGTERM, then SIGKILL after the grace. It gets a `blocking` outcome "stalled run killed", and its scratch moves to `quarantine/`. A builder inside an eight-second call is not killed; it ends by itself, and its outcome is "ended without a PASS review".
- **The pause.** A limit message that names a time pauses until that time: Codex's form, verbatim from a local transcript ("try again at 4:22 PM"). A message without a time waits the 30-minute interval. Either way the pause is one `transient` note, and the run then resumes and closes, with two cycles counted and no halt.
- **`caffeinate`** is started as `caffeinate -i -w <the loop's pid>` and has exited when the loop returns.
- **Pure cases**:
  - `reset_time` reads the epoch, date, clock-time, "resets 9pm" and "in 1 hour 5 minutes" forms, and returns None when no time or no limit is named;
  - stall needs both silence and no live call;
  - `settle` handles agreement, the smallest blast radius, one-way doors, and ties going to the stricter class;
  - `next_handoff` keeps the queue order;
  - `read_stream` reads the session id, the compaction and its context size, the limit line and the cost.
- **The review suites** were rewritten for the measures: three cycles are telemetry, two go to the arbiters, and each of (a), (b) and (c) halts. A same-diff halt replaces the third-cycle halt in `test_review_run.py`, and a ruling between two reviews of one diff is progress (found when the existing ruling test re-reviewed an unchanged diff).

## Found while building, and fixed
- **The stall race.** A long call ends and, before the post hook's outcome, the loop sees silence and no child; the busy stub was killed this way. A stall now has to hold on two consecutive polls.
- **`killpg` EPERM.** macOS refuses `killpg` when a member of the group is a zombie. `signal_group` then signals the group's members one by one.
- **`--tools ""` swallowed the brief**, the arbiter defect above.

## Michou's rulings of 2026-10-26, applied
- **Amendment 5 by the stream.** A `compact_boundary` record in the builder's stream is a `transient` note naming the trigger and the context size the stream gives: `pre_tokens`, or the last assistant usage. It is never a cycle.
  - **How a compacted builder finds its place:** it re-reads `logs/scratch/review.patch`, `logs/scratch/review.dispositions` and the audit file that the ledger's last cycle names.
  - No hook or `.claude/settings.json` is touched.
- **The unverified Claude limit form.** Claude Code's "resets 9pm" and "usage limit reached|<epoch>" forms are parsed but were not seen on this machine. Anything unparsed falls to the 30-minute retry.
- **No 0048 tonight.** Nothing has run under the loop outside the tests.

## Waiting for Michou: five diffs, one commit (`logs/scratch/handoff-0043/`)
1. `kgme.toml.diff`: `[models] arbiters = ["claude-opus-5-5", "claude-fable-5-1"]`.
2. `arbiter-prompt.md.diff`: `control/review/arbiter-prompt.md`, the fixed brief.
3. `kgme-loop.toml.diff`: `control/policy/profiles/kgme-loop.toml`, the job profile. It reads the queue, `control/review` and `logs`, writes only `logs`, and has no network of its own.
4. `test_loop_profile.py.diff`: `tests/policy/test_loop_profile.py`, the canary probes for that profile, in the same commit, since it is red without it.
5. `review-loop.md.diff`: the reader's halt measures, the arbiter pair, and a new "The loop" section with the never-list.

An acceptance clone (`logs/scratch/handoff-0043/clone`) holds the build with all five applied. Its `make check` result is recorded in "Acceptance" below.

## For the approval screen
- **The pair and the brief.** Opus 5.5 and Fable 5.1, both through `claude -p`. Arbiters chosen by specialty wait for ten recorded pairs (amendment 20).
- **The workspace** (F2, advisory). Until 0048, `kgme loop` needs a worktree given by `--workspace`. `kgme review` refuses a worktree (HANDOFF-0047 F12), and `loose`'s pinned permissions exclude staging and committing, so a real builder cannot yet review or commit from its workspace. The arbiter pair ruled that route outside 0043's mandate, on two conditions:
  - the loop never reports `closed` without a commit naming the handoff (F3's `close_status`);
  - the end-to-end route from a loose workspace (build, review and commit under the real pinned permissions) is a named acceptance case of HANDOFF-0048 before any production queue runs.
- **Hook events and the tree** (F4, advisory). A real session's hook events are reached from the loop's tree through the `loop:` note that names the session id, not through `parent`. The live hooks reading `KGME_LOOP_PARENT` is proposal HANDOFF-0063, under `docs/handoff/proposed/`.
- **A limit message that never stops.** A builder that prints one on every start pauses on every start, by amendment 19's letter; nothing caps it.

## Acceptance
- **`make check` in the acceptance clone**, with the five diffs applied, passes: lint 0 blocking, `kgme mods: 2 mod folders, 0 blocking`, 759 passed (`logs/scratch/handoff-0043/make-check-clone.txt`).
- **On `main`** before the smoke fix, the gate failed only on `tests/test_smoke.py`, which pins the subcommand list (757 passed). `loop` is now listed there as the fourteenth subcommand.
- **`tests/test_smoke.py`** is touched for that one line. It is under `tests/`, which this handoff's builder may write.

## Review cycle 1 (AUDIT-0148, BLOCK): eleven blocking, one cosmetic
Each fix starts with a red test (`logs/scratch/handoff-0043/red-c1.txt`: twelve red before the fixes, all green after).
- **F1, fixed.** The session had no execution request: `loose` runs `-p`, and stdin was closed.
  - `execution_request` gives the session one line on stdin, as Michou gives it: "HANDOFF-X is open and adopted by Michou: <path>. Execute it under CLAUDE.md...". It is a pointer, not a prompt of the loop's own.
  - The test parses `builder_argv` with the real `kgme` parser (session, loose, the handoff, the stream flags) and shows the line reaching the child's stdin.
- **F2, ruled advisory.** The arbiter pair agreed: outside the mandate. Both rulings are in the ledger with the brief's sha256. Executed as above under "For the approval screen".
- **F3, fixed.** `close_status`:
  - `closed` needs the newest cycle to be a PASS, with no red gate or failed review after it, and a commit naming the handoff;
  - a PASS without a commit is `ready` (diffs pending);
  - anything else is `ended`.

  Tests: a PASS followed by a red gate, a PASS followed by a failed review, and a PASS without a commit.
- **F4, ruled advisory.** The arbiter pair agreed. Executed: the loop writes the `loop:` note naming the session, the line above is corrected, and proposal HANDOFF-0063 is filed.
- **F5, fixed.** Nothing settles without a valid ruling from each model of the pair. A failure is a `transient` `arbiter-failed:` note, and the finding stays pending: the loop tries the pair again after `ARBITER_RETRY` (five minutes). Tests cover one arbiter failing and both failing, each followed by a retry that settles.
- **F6, fixed.** A split with no reversible option settles nothing. It writes a `blocking` `split:` note and a halt for Michou (ADR-023). Test: two one-way doors.
- **F7, fixed.** A ruling needs a known class, a non-empty option and reason, a JSON boolean `reversible`, and an integer blast radius from 1 to 5. Anything else is no ruling, never a crash. There are five malformed cases.
- **F8, fixed.** Measure (a) counts only a review whose intent comes after the settled ruling, so a review already running when the ruling lands is not its execution.
- **F9, fixed.** The arbiters get the whole diff. A diff over 400,000 characters is refused with a note, never cut. Tests: a diff past the old 60,000 cut reaches the brief whole, and an oversized one is refused before any arbiter runs.
- **F10, fixed.** The usage of each try is added to the run's (`add_usage`). The limit test reads 1300 in, 350 out and $0.47 across its two tries.
- **F11, fixed.** The unattended queue admits `from: michou` only (amendment 13). Test: an open Cowork handoff is refused.
- **F12, cosmetic, recorded.**
  - `kgme/loop.py` keeps its logic and effects together because the amended Outputs names the one file for both ("effects: ...; logic: ..., pure over a run's ledger events"), with the pure functions first.
  - The dead `_passed` is gone.
  - A split into `loop_logic.py` is a mechanical follow-up if Michou wants it.

## Review cycle 2 (AUDIT-0149, BLOCK): F3 and F8 again, F13 and F14 new
F2 and F4 are now advisory, as their rulings say. Each fix starts with a red test (`logs/scratch/handoff-0043/red-c2.txt`). F3 and F8 had stood two cycles, so they went to the arbiter pair with the builder's proposed fixes as its argument. Each ruling is in the clone's ledger with its brief's sha256.
- **F3, ruled advisory; both arbiters' conditions executed.**
  - A PASS counts only when the newest gate before it is green, so a red gate followed by a PASS with no green gate is no close.
  - `closed` also needs the handoff moved to `done/`. Without that the run is `ready`, diffs pending.
  - Opus's condition: a matching commit from before the run's start head does not count.
  - Fable's condition: the commit must be no earlier than the final PASS (`read_commit`'s `not_before`).
  - The commit-to-diff hash binding is declined, as both ruled: human-path diffs are reviewed applied but committed by Michou, so the commit differs from the reviewed diff by design.
  - Tests: red then PASS, an open handoff, and a commit before the start and before the PASS.
- **F8, ruled blocking.** The arbiters agreed on the class and named two compatible options, and both are executed. Measure (a) now counts a cycle as executing a ruling only when all three hold:
  - it started after the ruling;
  - it reviewed a diff not reviewed before the ruling (Opus), so unchanged work captured before the settlement is no execution;
  - its intent names the ruling among those it knew before its gate (Fable). `kgme review` reads the settled rulings before running `make check` and writes them into the cycle's intent (`ruled=F2,...`).

  Tests: settlement during the gate on unchanged work, and settlement before an intent that does not name it.
- **F13, fixed.** Each arbiter call writes a new output file, and a nonzero exit is no reply. Test: a fake `codex` that succeeds once, then fails without writing; the failure is not read as the earlier ruling.
- **F14, fixed.** `kgme review` keeps each reviewed cycle's own snapshot, `logs/scratch/evidence/<handoff>/<sha16>/` (the patch and the dispositions). The arbiters read the newest reviewed cycle's snapshot, check its hash against the hash the outcome names, and use that cycle's own audit for the finding row.
  - Missing or mismatched evidence is refused with a note.
  - Tests: another handoff's later cycle and an overwritten global patch do not reach the brief; a tampered snapshot and a missing one are both refused before any arbiter runs.
- **F12, cosmetic, recorded as before.** The module split and the effect-prefix renames (`start_builder`, `signal_group`, `kill_group`, `_supervise`) are a mechanical follow-up.
- **For the approval screen.** On F8 the arbiters agreed on the class but named different options. `settle` compares classes, not options. Here both options were executed; a case where options conflict under one class is not yet handled.

## Review cycle 3 (AUDIT-0150, BLOCK): F14 again, F15 new
Red tests on the cycle-3 code: `logs/scratch/handoff-0043/red-c3.txt`.
- **F14, ruled blocking by the pair, both options being the builder's proposed fix; executed.**
  - The evidence bundle is keyed by the review attempt (its intent id): `logs/scratch/evidence/<handoff>/<intent id>/` holds the patch and dispositions, written when the attempt starts, and the audit's findings table, written with the audit.
  - The arbiters read the bundle of the attempt that the newest successful outcome answers (`ref`), check its patch against the outcome's hash, and take the finding's row from that bundle.
  - A missing patch, dispositions file, findings table or row, or a patch that does not match, is refused with a `transient` note before any arbiter runs.
  - Tests: a failed attempt on the same diff after a successful one does not leak its words; another handoff and an overwritten global patch do not reach the brief; each of the four missing or mismatched parts is refused.
- **F15, fixed.** Agreement is now the same class and the same recommendation, compared after case and spacing are normalised.
  - Anything else is a split, on the class or on the option under one class. A split takes the reversible option with the smallest blast radius and is listed for the approval screen; a split with no reversible option goes to Michou.
  - The `split:` note now leads with "for the approval screen" and names each arbiter's option.
  - Tests: two reversible options under `blocking` settle by blast radius, two one-way doors escalate, and one recommendation spelled alike is agreement.
- **F12, cosmetic, recorded as before.**

## Review cycle 4 (AUDIT-0151): PASS
- **No blocking finding is left.** F12 (cosmetic) stands as recorded follow-up work: the split of `kgme/loop.py` and `kgme/review_run.py` into logic and effect modules, and the effect-prefix renames.
- **Four cycles, AUDIT-0148 to AUDIT-0151.** The arbiter pair ruled five findings over them: F2 and F4 advisory, F3 advisory, F8 and F14 blocking. Every ruling was agreed between the two models, and every ruling was executed.
  - The pair was the one this handoff builds, run in the acceptance clone through `kgme review arbitrate`.
  - The arbiter events and the review events stay in the clone's ledger (`logs/scratch/handoff-0043/clone/logs/ledger/`). `main`'s ledger does not carry them, because the review ran where Michou's diffs were applied.
- **On `main`.** This commit lands the code, the tests, the fixtures, this report, the four review audits and proposal HANDOFF-0063. The five human-path diffs wait under `logs/scratch/handoff-0043/`. `make check` on `main` without them is green (below), because no test there needs `[models] arbiters`, the brief or the profile, and the profile's test ships in the diff bundle.
- **State: ready, diffs pending.** The handoff closes after Michou commits the five diffs together and `make check` is green with them. `completed:` is then AUDIT-0151's `created`, 2026-10-26T19:13:22-07:00.
- **Before any real queue.** By the arbiters' F2 ruling, HANDOFF-0048 must carry the end-to-end loose-workspace route (build, review and commit under the real pinned permissions) as a named acceptance case, and nothing runs under the loop until then. Michou has already ruled that 0048 is not tonight's queue.

