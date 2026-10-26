---
id: READER-MERGING
type: note
status: active
created: 2026-10-21T21:10:00-07:00
modified: 2026-10-22T01:32:53-07:00
author: claude-code
source: inferred
sources: ["HANDOFF-0055", "kgme/merge.py", "kgme/merge_rules.py", "kgme/approve.py"]
tier: 2
---

# Merging the design track, and approving a commit

The design track lands on `main` as it goes, not in one merge at the end (HANDOFF-0055). A design commit that changes only the design track's own folders, and passes `make check` once merged, is merged into `main` by itself. Your approval of the design is a separate act: a ledger event naming a commit, which HANDOFF-0037 builds from.

## What merges by itself
The lanes are set in `kgme.toml` under `[tracks.design]`: `docs/design/`, the cockpit-design folders under the handoff and audit folders, the readers whose names start with cockpit-design, and the tests whose names start with test_design_. After every commit on `main` or on `design`, the post-commit hook runs `kgme merge design` in the background. When `design` holds no commit `main` lacks, it does nothing and writes nothing. Otherwise:

1. **A trial.** In a temporary local clone at `main`, it runs `git merge --no-ff design`, then `make check`, then removes the clone. A clone rather than a worktree, because a worktree's hooks and ledger resolve to the main checkout, so tests there would write into it. A red trial leaves `main` as it was and writes a `blocking` outcome naming the first failing test or blocking lint line, and keeps the whole output under `logs/scratch/merge/`.
2. **The lanes.** If the merge would change a path outside the lanes (a prompt under `control/review/`, say), it is refused, and the outcome names each path. You merge it yourself once the trial is green: `git merge --no-ff design` in your terminal.
3. **A quiet point.** It merges in the main checkout only when nothing is staged there, no `index.lock` is held, no merge, rebase, or cherry-pick is in progress, and `main` has not moved since the trial. Otherwise it writes a `transient` outcome, and the next commit tries again.
4. **The merge.** `merge: design <sha> (kgme merge)`; `kgme merge` then pushes it through `kgme sync`, since a `git merge` fires no post-commit hook.

Each run writes one intent and one outcome. To see what a merge would do without doing it: `kgme merge design --dry-run`, which runs the trial and writes nothing.

## When a landing is blocked
Once `kgme merge` has started git on your checkout, any failure (git exits non-zero, times out, or leaves a state it cannot check) is a blocked landing, whether or not anything changed, and `kgme merge` undoes nothing. Moves and waits it sees before starting git touch nothing and are retried. It keeps the tested merge commit under a ref named refs/kgme/merge-blocked/ plus the design commit's short id, writes one `blocking` outcome that names that ref and the repair, and refuses every later design commit, writing nothing, until your checkout is quiet again. The repair, from your terminal: remove a stale main.lock under .git/refs/heads if the outcome mentions one, `git switch main`, then `git merge --ff-only` with the kept ref the outcome names. Once the design commit is on `main`, by your repair or by a later landing, the next run deletes the kept ref and carries on.

## Approving
From your own terminal:

```
kgme approve --what canvas --sha <commit> --note "<your words>"
kgme approve --show canvas
```

The first records an `approval` event, actor `michou`, naming the full commit. It refuses a commit that is not on `main`. It also refuses to run inside Claude Code or Codex, both of which set markers in the environment of every command they run, and `.claude/settings.json` denies the command to Claude Code as well. `--show` prints the newest approval: its time, its commit, and its words.

## Stopping it
Remove the two `merge` calls from `control/git-hooks/post-commit` (one for commits on `design`, one for commits on `main`). `git revert -m 1 <merge>` undoes a merge.
