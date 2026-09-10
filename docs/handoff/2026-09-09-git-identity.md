---
id: HANDOFF-0005
type: handoff
created: 2026-09-09T20:05:00-07:00
from: michou
to: claude-code
status: done
completed: 2026-09-09T20:22:00-07:00
tier: 2
depends_on: HANDOFF-0001
name: "Michael Grigorian"
email: "michaelhgrigorian22@gmail.com"
---

# Handoff 0005 — Set the git identity

**Michou fills in `name:` and `email:` above before this runs.** Claude Code must refuse to run it while either value still contains `FILL IN`.

Why this is Michou's decision and not the agent's: commit authorship is durable and, once the repository is pushed, public. The email can be a real address or, later, GitHub's private no-reply address for the account (`<id>+<user>@users.noreply.github.com`); a change later does not rewrite history, so the choice today is not fatal, but it is his.

## Steps
1. Confirm both frontmatter values are filled in. If not, stop and say so.
2. `git config --global user.name "<name>"` and `git config --global user.email "<email>"` using exactly the values above.
3. `git config --global init.defaultBranch main`.
4. Print `git config --global --list` (these three keys only).
5. Set this handoff `status: done` with `completed:`. Then say: "HANDOFF-0002 can now resume from step 3."

## Do not
Touch any other git setting. Create keys. Add remotes.
