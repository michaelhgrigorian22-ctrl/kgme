---
id: AUDIT-0009
type: report
status: final
handoff: HANDOFF-0023
author: claude-code
source: fetched
tier: 2
created: 2026-09-11T14:20:00-07:00
---

# GitHub authentication over HTTPS and the private remote - 2026-09-11

Per HANDOFF-0023. Part A (browser login) was Michou's, in his own terminal tab; Parts B and C were Claude Code's, with Part C run only after his explicit "go" at about 14:15. No token was printed, read, or stored outside gh's keyring entry.

## Part B, verification (read-only)

`gh auth status`, status lines as printed (token masked by gh itself):

```
github.com
  ✓ Logged in to github.com account michaelhgrigorian22-ctrl (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

- `~/.config/gh/`: `config.yml`, `hosts.yml`. `grep -c oauth_token ~/.config/gh/hosts.yml` → 0; the file's keys are `git_protocol`, `user`, `users` only. Storage is the macOS keyring, not a plaintext file.
- `git config --global --get-regexp credential` before Part C: none. Across all scopes, only Apple's system `credential.helper=osxkeychain` (from the Command Line Tools gitconfig). That helper does not know gh's token, so a push would have stalled on a prompt; the step 1 "authenticate git with your GitHub credentials" answer had not taken effect. Fixed in Part C with `gh auth setup-git`, which Michou approved in the "go".
- Username per `gh api user`: `michaelhgrigorian22-ctrl`, matching what Michou reported.

## Part C, pre-flight (before "go")

| Check | Result |
|---|---|
| `git ls-files` count | 64 |
| `git log --oneline \| wc -l` | 13 |
| `.env`, key material, `memory/private/` among tracked names | none (the one name match is `docs/adr/ADR-008-secrets-and-policy.md`, the policy itself) |
| Token-shaped strings in tracked content (`ghp_`, `github_pat_`, `sk-ant-`, `AKIA`) | 0 files |
| Files over 5 MB | none; largest is 19,914 bytes |
| Existing remotes | none; branch `main` |

## Part C, actions after "go"

1. `~/.gitconfig` backed up to `~/.gitconfig.bak.20260911`; `gh auth setup-git` added, shown as the diff against the backup:
   ```
   5a6,11
   > [credential "https://github.com"]
   >     helper =
   >     helper = !/opt/homebrew/bin/gh auth git-credential
   > [credential "https://gist.github.com"]
   >     helper =
   >     helper = !/opt/homebrew/bin/gh auth git-credential
   ```
   (The empty `helper =` line is gh's convention to clear inherited helpers for that host before adding its own.)
2. `gh repo create kgme --private --source=. --remote=origin --push` → `https://github.com/michaelhgrigorian22-ctrl/kgme`; `* [new branch] HEAD -> main`; `main` tracks `origin/main`.

## Verification

| Item | Value |
|---|---|
| `git remote -v`, host only | github.com |
| `gh repo view --json isPrivate,visibility` | `{"isPrivate":true,"visibility":"PRIVATE"}` |
| `origin/main` equals local `main` after push | yes, 0a263f8 |

## Reversibility

`gh repo delete michaelhgrigorian22-ctrl/kgme --yes` removes the remote repository (GitHub keeps it recoverable for 90 days); `git remote remove origin` locally; `cp ~/.gitconfig.bak.20260911 ~/.gitconfig` removes the credential helper lines; `gh auth logout` revokes the local session, and the token can also be revoked at github.com → Settings → Applications.
