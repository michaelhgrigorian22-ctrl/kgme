---
id: HANDOFF-0067
type: handoff
created: 2026-10-28T13:20:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0040, HANDOFF-0045]
plan_ref: PLAN-PHASE-1 step 10d
---

# Handoff 0067 — A commit from Michou's shell holds human paths only

## Why
Twice a commit from Michou's shell has swept Claude Code's staged, unreviewed work onto `main`: on 2026-10-25 (`9865a93`, `9d6f9db`, corrections entry of 23:08) and on 2026-10-28 (`7849748`, thirty-five files of HANDOFF-0048 under a merge's title, corrections entry of 10:21). Both times the rule was a sentence ("name the files on the commit") and the box that broke it was Cowork's. The second case is one the sentence cannot cover: a merge commit takes no pathspec, and a refused `git merge` followed by a bare `git commit` commits the whole index. Michou asked for the guard on 2026-10-28 ("this seems pretty inconvenient to fuck up").

The division of labour already gives the rule. Every non-human path reaches `main` by a committer that marks itself: Claude Code (`CLAUDECODE`, the variables `kgme/approve.py` already reads to refuse an agent harness), `kgme sync` (`KGME_SYNC_RUN`, `kgme/sync_git.py`), and `kgme merge design` (a merge commit, for which git runs no `pre-commit` hook). What Michou commits by hand is adoptions, STATUS, corrections, readers, policy, applied diffs: human paths (`kgme.toml [hooks] human_paths`).

## What
1. **Measure first.** List the commits on `main` since 2026-10-01 made with no marker (author time, message, paths) and classify each path as human or not by `guard.is_human_path` over `[hooks] human_paths`. Every non-human path among them is a case the guard would have refused; the report names them. Expected among them: `skills/` and the repository's `.agents/skills/` links, which Michou applies (HANDOFF-0048 amendment 10) but `human_paths` does not list; and the vendored three.js of HANDOFF-0058, a deliberate hand commit of code. The report says, for each, whether `human_paths` should name it or the escape hatch (item 2) is the right door; a change to `human_paths` is a diff for Michou.
2. **The hook.** `control/git-hooks/pre-commit` (a human path: a diff) runs `python -P -m kgme.hooks.commit_scope` with the hook's own `PATH` line (HANDOFF-0062). It passes at once when `CLAUDECODE` or `KGME_SYNC_RUN` is set, or when `KGME_COMMIT_ANY=1` is set by hand for one command. Otherwise it reads the paths of the commit about to be made from the index git hands the hook (`git diff --cached --name-only -z`; for `git commit -- <paths>` git runs the hook against a temporary index holding only those paths, so a pathspec commit is judged on exactly its paths), and refuses, exit 1, if any is not a human path, printing each such path and the two doors: `git commit -m "…" -- <your paths>`, or `KGME_COMMIT_ANY=1 git commit …` for a deliberate hand commit of code. A merge commit Michou concludes by hand (`MERGE_HEAD` present) is judged the same way: its index is the merge result, so a staged foreign file shows.
3. **The test.** `tests/test_commit_scope.py` in a temporary repository with the hook installed: a staged code file and a staged reader, bare `git commit` refused naming the code file; `git commit -- <reader>` passes and leaves the code file staged; `KGME_COMMIT_ANY=1` passes; `CLAUDECODE=1` passes; `KGME_SYNC_RUN=x` passes; a hand-concluded merge with a foreign file staged is refused. The tool-resolution test of HANDOFF-0062 gains the new hook's tools.
4. **`make setup`** already points `core.hooksPath` at `control/git-hooks/`; nothing else to install. The reader that names the hooks (`docs/readers/review-loop.md` or the sessions reader, whichever the measurement shows lists them) gets one sentence: a diff.

## Outputs
`kgme/hooks/commit_scope.py`, `tests/test_commit_scope.py`, `tests/test_hook_path.py` (the new hook's tools), `control/git-hooks/pre-commit` and `kgme.toml` if item 1 names a path (human paths: diffs under `logs/scratch/handoff-0067/`), a reader sentence (a diff), the measurement in the report.

## Acceptance test (under five minutes)
The six cases of item 3 green. Replaying the morning of 2026-10-28 in a scratch clone (thirty-five files staged by a session marked as Claude Code, then Michou's `git merge --no-ff design` refused and a bare `git commit` from an unmarked shell) leaves the index as it was and prints the code paths. `make check` green.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: one hook; removing `control/git-hooks/pre-commit` restores today's behaviour. `git revert`.

## Needs from Michou
Adoption; the hook and any `human_paths` diff; the habit of `KGME_COMMIT_ANY=1` on a deliberate hand commit of code, which the hook's refusal prints.

## Report
`docs/audit/2026-10-DD-commit-scope-guard.md`. Set `status: done`, `completed:`. Commit `hooks: a commit from Michou's shell holds human paths only (HANDOFF-0067)`.
