---
name: kgme-integrator
description: Read a KGME crew run's integration branch, its gate and its diff, and write the one approval screen Michou reads before `kgme approve --what code`; never merge, never approve.
---

# kgme-integrator

The crew integrates mechanically (`kgme crew`: the merge gate, `crew/<handoff>/integration` fast-forwarded task by task in plan order, the full gate, one integration review by another vendor). This skill is the reader of that record, for the one screen Michou sees.

## Read
1. The crew's events: `kgme ledger read --stream ledger` filtered to `job: crew:<handoff>` and `review:<handoff>:*`; the plan under `logs/scratch/crew/<run>/plan.md`; the audits the events name under `docs/audit/`.
2. `git log --oneline main..crew/<handoff>/integration` and `git diff --stat main crew/<handoff>/integration`.
3. The quarantine records under `logs/scratch/workspaces/*/task.json` with `state: quarantined`.

## Write (to the session, or to `logs/scratch/crew/<run>/screen.md`)
One screen: plan cycles; each task with its harness, model, cycles, strikes, audits and reviewer; each quarantine with its reason; the gate's result; the diff by path; the approval-screen list (every judgement scored at or above 0.5, the arbiter splits); and the one line to type, `kgme approve --what code --sha <the integration head>`.

## Never
Merge, push, approve, edit a human path, or rerun a task. A conflict is a `blocking` outcome on the later task, rebuilt on the new head by the crew, not by you.
