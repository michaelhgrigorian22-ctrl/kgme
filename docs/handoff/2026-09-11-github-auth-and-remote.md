---
id: HANDOFF-0023
type: handoff
created: 2026-09-11T14:00:00-07:00
from: cowork
to: claude-code
status: done
completed: 2026-09-11T14:22:00-07:00
tier: 2
depends_on: HANDOFF-0022
supersedes: HANDOFF-0010
---

# Handoff 0023 — GitHub authentication over HTTPS and the private remote

Replaces the rejected SSH-key proposal (0010). The credential is a token that `gh` stores in the macOS Keychain; git uses it through `gh`'s credential helper. No key files on disk; nothing for an agent to read. **Michou must have created the GitHub account first** (personal Gmail, two-factor on).

**Who types what:** Part A is Michou's, in his own terminal tab (a browser login is his). Parts B and C are Claude Code's; C waits for his explicit "go" before anything leaves the machine.

## Part A — Michou, in his own terminal tab
1. `gh auth login` → GitHub.com → HTTPS → authenticate in the browser. Choose **yes** when asked to authenticate git with your GitHub credentials.
2. Tell Claude Code the GitHub username (public information).

## Part B — Claude Code, verify (read-only)
3. `gh auth status` — record the status lines only (they show the account and scopes, not the token). Confirm the storage is the keyring, not a plaintext file: `ls ~/.config/gh/` names only; `hosts.yml` must **not** contain an `oauth_token` line — check with `grep -c oauth_token ~/.config/gh/hosts.yml || echo 0` (a count, never the value).
4. `git config --global --get-regexp credential` — record.

## Part C — the remote (outward-facing: approval gate)
5. Pre-flight, read-only: `git ls-files` — confirm no `.env`, no key material, nothing under `memory/private/`, no file over 5 MB. Report the file count. Confirm `git log --oneline | wc -l`.
6. Restate: "Create private repo `<user>/kgme`, add as `origin`, push `main`." **Wait for Michou's explicit go.**
7. `gh repo create kgme --private --source=. --remote=origin --push`.
8. Verify: `git remote -v` (host only), `gh repo view --json isPrivate,visibility` — must be private.

## Reversibility
`gh repo delete <user>/kgme --yes` removes the remote repository (GitHub keeps deleted repos recoverable for 90 days). `git remote remove origin` locally. `gh auth logout` revokes the local session; the token can also be revoked at github.com → Settings → Applications.

## Report
`docs/audit/2026-09-11-github-remote.md` (`id: AUDIT-0009`, `type: report`, `status: final`, `handoff: HANDOFF-0023`): auth status lines, credential helper, pre-flight counts, remote host, visibility. Update `docs/STATUS.md` Gate 1 row to note "git remote: private, pushed". Set `status: done`, `completed:`. Commit `repo: private GitHub remote added (HANDOFF-0023)` and push.
