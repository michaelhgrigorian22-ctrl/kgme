---
id: AUDIT-0008
type: report
status: final
handoff: HANDOFF-0021
author: claude-code
source: fetched
tier: 2
created: 2026-09-11T13:55:00-07:00
---

# Homebrew install from a pinned, inspected installer - 2026-09-11

Per HANDOFF-0021. Claude Code did steps 1 to 3, 5, and 6; Michou ran the installer (step 4) in his own terminal tab at about 13:15, before the write-set report below was formally presented at 13:35 (the report was still given, and the on-disk result matched it). No password passed through this session.

## Pin and hash

| Item | Value |
|---|---|
| Scratch directory | `~/.kgme/quarantine/brew-install/` (kept; contains `install.sh`, `head.json`, `pinned-sha.txt`, `install.sh.sha256`) |
| `Homebrew/install` commit resolved at 13:07 | `8949852f785a3bacaba2a979d0790337950b0a4a` (committed 2026-09-11T08:52:19Z, "Merge pull request #1143 … dependabot/github_actions") |
| Download | `https://raw.githubusercontent.com/Homebrew/install/8949852f785a3bacaba2a979d0790337950b0a4a/install.sh` |
| `shasum -a 256 install.sh` | `25548e1da7930c1563dbbe2cb05834a4131c4da09234540b6fdac812fda3c287` |
| Size | 32,785 bytes, 1,151 lines, read in full |

## Write-set summary reported to Michou (macOS branch of the script)

- **Sudo, 11 calls, two paths.** `/opt/homebrew`: `install -d -o root -g wheel -m 0755` to create it; `mkdir -p` for 15 standard subdirectories (`bin etc include lib sbin share var opt share/zsh share/zsh/site-functions var/homebrew var/homebrew/linked Cellar Caskroom Frameworks`); `chmod ug=rwx` on them; `chmod go-w` on the two zsh directories; `chown michaelgrigorian` and `chgrp admin` on them; one `chown -R michaelgrigorian:admin /opt/homebrew`. `/etc/paths.d`: `mkdir -p`, `tee /etc/paths.d/homebrew` writing the line `/opt/homebrew/bin`, `chown root:wheel`, `chmod a+r`. No `chmod -R` anywhere; the only recursive operation is the `chown -R` scoped to `/opt/homebrew`.
- **Under `~`, no sudo:** creates `~/Library/Caches/Homebrew` and a `.cleaned` marker. Does not edit any shell profile; prints the `shellenv` line only.
- **Network:** `git fetch` of `https://github.com/Homebrew/brew` into `/opt/homebrew`, checkout of the latest release tag as branch `stable`, then `brew update --force --quiet` against `formulae.brew.sh`. No `homebrew-core` tap (`HOMEBREW_NO_INSTALL_FROM_API` unset).
- **Skipped on this machine:** Command Line Tools install (`/Library/Developer/CommandLineTools/usr/bin/git` present; CLT 26.2.0.0.1.1764812424), Xcode licence prompt (`xcrun clang` ran clean).
- **Exit hygiene:** `trap 'sudo -k' EXIT` because sudo was not cached beforehand. Confirmed afterwards: `sudo -n true` requires a password again.
- **Analytics:** suppressed during the run (`HOMEBREW_NO_ANALYTICS_THIS_RUN=1`), enabled after it until step 6.

Pre-checks before handing over: user in `admin` group; `/etc/paths.d` exists; no `/etc/homebrew/brew.no_install`; macOS 26.6 inside the script's supported window (oldest 15.0, newest-unsupported 28.0); Apple Silicon.

## Result

| Item | Value |
|---|---|
| `brew --version` | Homebrew 6.0.22 |
| `git -C "$(brew --repository)" rev-parse HEAD` | `08e85c4e42f5d8f1ea17c36cb59cf61c2ccb26c3` (tag `6.0.22`, branch `stable`, working tree clean) |
| `/opt/homebrew` | owner `michaelgrigorian:admin`, created 13:15, 40 entries |
| `/etc/paths.d/homebrew` | present, `root:wheel`, 18 bytes: `/opt/homebrew/bin` |
| `~/Library/Caches/Homebrew` | present, owned by the user; holds the API cache and `portable-ruby-4.0.6.arm64_big_sur.bottle.tar.gz` |
| `brew analytics off` | "InfluxDB analytics are disabled. Google Analytics were destroyed." |
| `brew doctor` | two warnings, both benign: a newer Command Line Tools release is available (26.3; update via Software Update, not proposed here), and Homebrew's `bin` was not in the PATH of the non-login shell that ran doctor (fixed by step 5 below; a fresh login shell resolves `brew`). |

One unexplained transient: the first verification pass at 13:46 reported `/opt/homebrew/bin/brew` and `/etc/paths.d/homebrew` as absent; a second pass one minute later found both with 13:16 modification times, and every later command saw them. Recorded, not diagnosed.

## Step 5, shell profile

`~/.zprofile` (5 lines, 2026-04-16) backed up to `~/.zprofile.bak.20260911`. Appended, shown as the diff against the backup:

```
5a6,7
>
> eval "$(/opt/homebrew/bin/brew shellenv)"
```

Not sourced into this session; verified in a fresh login shell (`zsh -lc`): `which brew` → `/opt/homebrew/bin/brew`, `brew --prefix` → `/opt/homebrew`.

## Reversibility

Documented restoration, not exact: Homebrew's uninstall script (pin it the same way at the time) removes `/opt/homebrew`; then remove `/etc/paths.d/homebrew` by hand (`sudo rm`), delete lines 6 to 7 of `~/.zprofile` or restore `~/.zprofile.bak.20260911`, and `rm -rf ~/Library/Caches/Homebrew`. The `/opt` directory itself pre-existed (it holds `/opt/R`) and is untouched.

## HANDOFF-0022 — gh

Ran 2026-09-11T14:02:00-07:00, no sudo.

| Item | Value |
|---|---|
| `brew info --json=v2 gh`, stable version | 2.100.0 |
| Runtime dependencies | none; build dependency `go` only (not installed, bottle poured) |
| Declared bottle sha256, `arm64_tahoe` | `4e98510bc683db27f42ff84c9c7f5b884e3109f499c08241991617031bd63666` |
| Downloaded bottle, `shasum -a 256` | `4e98510bc683db27f42ff84c9c7f5b884e3109f499c08241991617031bd63666` (matches the formula's declared sha256) |
| `brew install gh` | poured `gh--2.100.0.arm64_tahoe.bottle.tar.gz`; `/opt/homebrew/Cellar/gh/2.100.0`, 238 files, 40.3 MB; zsh completions to `/opt/homebrew/share/zsh/site-functions`; `INSTALL_RECEIPT.json` says `poured_from_bottle: true`, runtime dependencies empty |
| `gh --version` | `gh version 2.100.0 (2026-09-03)`, matches step 1 |
| `brew pin gh` | done; `brew list --pinned` → `gh` |
| `gh auth login` | **not run** (HANDOFF-0023) |
| `~/.config/gh` | does not exist |

Reversibility: `brew unpin gh && brew uninstall gh`; nothing else was installed alongside it, so there are no orphaned dependencies to remove.
