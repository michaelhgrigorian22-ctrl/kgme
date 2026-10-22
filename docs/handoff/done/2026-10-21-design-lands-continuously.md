---
id: HANDOFF-0055
type: handoff
created: 2026-10-21T23:30:00-07:00
from: michou
to: claude-code
tier: 2
status: done
completed: 2026-10-22T01:13:43-07:00
report: docs/audit/2026-10-21-design-lands.md
depends_on: [HANDOFF-0047, HANDOFF-0054]
plan_ref: PLAN-PHASE-1 step 9a
---

# Handoff 0055 — The design track lands on `main` continuously; approval becomes a ledger event on a commit

## Why
Michou, 2026-10-21, on making the design merge his approval: "i feel like i set that rule without seeing a real buildout process yet ... smaller more frequent merges probably mitigate the need to go back over a massive build that took 3 days if the merge doesnt work when both sides are done." `design` is 35 commits ahead of `main` and waits for one merge on canvas approval. Its changes lie entirely in its own folders (the design docs and prototypes, its handoffs and audits, its readers, one test, and review prompts under `control/review/`); nothing KGME executes. Engineers would keep one trunk and treat sign-off as a separate act. The rule changes: design work merges into `main` as soon as it is green, and Michou's approval of the design is a ledger `approval` event naming a commit; HANDOFF-0037 builds only from an approved commit. Code is unchanged: Claude Code commits on PASS, and a crew's merge stays Michou's approval (ADR-022 §3, 0048).

## What
1. **Lanes.** `kgme.toml [tracks.design] lanes` (a diff Michou applies; HANDOFF-0042 reuses it): `docs/design/`, `docs/handoff/cockpit-design/`, `docs/audit/cockpit-design/`, `docs/readers/cockpit-design*.md`, `tests/test_design_*.py`.
2. **`kgme merge design [--dry-run]`**, run against the main checkout (resolved as 0047 resolves the ledger root):
   - nothing to do when `design` holds no commit `main` lacks;
   - a trial first: a temporary detached worktree at `main`, `git merge --no-ff design` there, `make check` there, the worktree removed however it ends;
   - refused, naming each path, when the merge would change anything outside the lanes. A path under `control/` or another human path is merged by Michou by hand (`git merge --no-ff design` in his terminal) after the trial says green;
   - then, only at a quiet point (the main checkout's index equals `HEAD`, no `index.lock`, no merge or rebase in progress), the same merge in the main checkout, message `merge: design <sha> (kgme merge)`; the post-commit hook pushes it. Not quiet: a `transient` outcome and the next trigger retries;
   - one intent and one outcome per run: the design commit, the trial's result, the merge commit or the refusal.
3. **Triggers.** The post-commit hook runs `kgme merge design` in its background subshell after the atlas, on `main` (after Claude Code's commits) and on `design` (after Codex's); a run with nothing to do writes nothing. Michou can run it by hand.
4. **`kgme approve --what <name> --sha <commit> [--note "<words>"]`** appends an `approval` event, actor `michou`, naming the commit and what is approved (first: `canvas`). It refuses a commit not on `main` and refuses to run under an agent harness (Claude Code's and Codex's environment markers, checked at build time); `.claude/settings.json` denies `Bash(*kgme approve*)` (a diff Michou applies). `kgme approve --show <name>` prints the newest approval.
5. **Record the rule.** Addendum to ADR-022 §3 and amendments to 0036 (item 4: the approval names a commit, recorded by `kgme approve`) and 0037 (built from the files at the approved commit), written by Cowork with this handoff. The design track's README and builder prompt are the design session's to update.

## Outputs
`kgme/merge.py` (effects: `run_merge`; logic: `lane_paths`, `is_quiet`, pure), `kgme/approve.py`, `kgme/cli.py` (`merge`, `approve`), `control/git-hooks/post-commit`, `kgme.toml` (`[tracks.design]`) and `.claude/settings.json` (the deny) as diffs Michou applies, `tests/test_merge.py`, `tests/test_approve.py`, a section in `docs/readers/sessions.md` or a new `docs/readers/merging.md` (as a diff).

## Acceptance test (under fifteen minutes)
In a temporary copy of the repository: a design commit inside the lanes merges by itself after a commit on `main` and appears on `main` within a minute; a design commit touching `control/review/` is refused with the path named and the trial's result; a red trial leaves `main` untouched; with a staged file in the main checkout the merge waits (`transient`) and lands on the next trigger; `kgme approve` from a Claude Code session is refused; from Michou's terminal it records the event and `--show` prints it.

## Reviewer
Codex read-only under `kgme review`.

## Reversibility
Door: two-way. Blast radius: merges of design-only folders into `main`, one hook line, two commands. Remove the hook line to stop it; `git revert` any merge.

## Needs from Michou
Adoption. Applying the `kgme.toml`, hook and settings diffs. The first merge by hand: the 35 commits waiting include prompts under `control/review/`, so `kgme merge design --dry-run` reports the trial and the paths, and he runs `git merge --no-ff design` once.

## Report
`docs/audit/2026-10-DD-design-lands.md`, named in `report:` on closing. Commit `merge: the design track lands on main continuously; approval on a commit (HANDOFF-0055)`.
