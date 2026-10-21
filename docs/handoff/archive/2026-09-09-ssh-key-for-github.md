---
id: HANDOFF-0010
type: handoff
created: 2026-09-09T20:24:00-07:00
from: claude-code
to: claude-code
tier: 2
depends_on: HANDOFF-0001
audit_ref: "`~/.ssh` does not exist; no SSH key material for a GitHub remote."
status: superseded
superseded_by: HANDOFF-0023
reason: "Reissued by Cowork with the amendments from AUDIT-0004 (Codex review), 2026-09-11."
---

# Handoff 0010 (proposed) — Generate an ed25519 SSH key for GitHub

## Why
Audit reported `~/.ssh` does not exist. Phase 0 §3 names "SSH key registered with GitHub"; Phase 0 §7 needs SSH to push to a private repo. ed25519 is the current-generation default (smaller, faster, at least as strong as RSA-4096).

## What
1. `mkdir -p ~/.ssh && chmod 700 ~/.ssh`.
2. `ssh-keygen -t ed25519 -C "michaelhgrigorian22@gmail.com" -f ~/.ssh/id_ed25519` — `ssh-keygen` prompts for a passphrase interactively (Michou types it, twice; nothing is echoed).
3. `chmod 600 ~/.ssh/id_ed25519` and `chmod 644 ~/.ssh/id_ed25519.pub`.
4. Add to macOS Keychain-integrated ssh-agent (persists across reboots): create/edit `~/.ssh/config` with `Host github.com\n  UseKeychain yes\n  AddKeysToAgent yes\n  IdentityFile ~/.ssh/id_ed25519`; then `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`.
5. Print the public key only: `cat ~/.ssh/id_ed25519.pub`. **Never print the private key.** Michou copies the public key into GitHub → Settings → SSH and GPG keys → New SSH key.
6. Verify later (after step 5): `ssh -T git@github.com` should greet by GitHub username.

## Reversibility
`rm -rf ~/.ssh` removes the keypair locally. Any GitHub entry created from the public key must be revoked separately in GitHub → Settings → SSH keys. Keychain entry: `security delete-generic-password -l "SSH: ..." login.keychain` (or from Keychain Access).

## Risks
The private key `~/.ssh/id_ed25519` is a credential. Passphrase-protected per this proposal; never commit, never print, never copy elsewhere. The `.gitignore` in this repo does not cover `~/.ssh/` because `~/.ssh/` is outside the repo — but if a working file were ever created inside the repo containing key material, `git add .` would happily stage it. Never write key material into the repo tree.

## Needs from Michou
A passphrase (his to choose and remember — password manager recommended). A GitHub account to paste the public key into (Phase 0 §7). Present to type the passphrase.
