---
id: AUDIT-0007
type: report
status: final
handoff: HANDOFF-0019
author: claude-code
source: fetched
tier: 2
created: 2026-09-11T13:05:00-07:00
---

# Backblaze backup verification and restore test - 2026-09-11

Read-only per HANDOFF-0019. No Backblaze setting was changed, nothing installed, no log line printed. Machine checks ran 12:50 to 13:05 on 2026-09-11; Michou supplied A4, A5, and the B8 hash at 13:12 and the report was finalised then.

## A1. Installed and running

`/Library/Backblaze.bzpkg/` contains `bzbmenu.app`, `bzbui_interface.xml`, `bzdata`, `bzfilelist`, `bzfirsttouchurl.txt`, `bzinstall.xml`, `bzinstallername.txt`, `bztransmit`, `bzupdates`, `UninstallBackblaze.app`, `userPub.pem`. Installer version recorded in `bzinstallername.txt`: `10.0.1.1038`. `pgrep -fl bztransmit` found no process at 12:52 (the uploader runs as a transient job between scans and was idle); the resident service `bzserv` (`/Applications/Backblaze.app/Contents/MacOS/bzserv`, PID 57858) was running.

## A2. Exclusions

Both rule files are world-readable (`bzexcluderules_editable.xml`, 18,552 bytes, modified 2026-09-11 08:06; `bzexcluderules_mandatory.xml`, 94,615 bytes, 377 rules, modified 08:15). Every rule requires all of its criteria to match; a rule scoped to a folder cannot fire outside it.

- **Editable file, macOS rules:** 14, all scoped to iTunes podcasts, Chrome and Safari caches, Firefox cache, Dropbox cache, Spotify, Slack, Docker containers, and `loginhelper.app`. None can match under `~/Projects`, `~/Documents`, or `~/Desktop`.
- **Mandatory file, macOS rules not anchored under `~/Library` or photo libraries:** about 40, covering `.Trashes`, `.Trash`, `/Developer`, `/Network`, `Backups.backupdb`, WD SmartWare stores, Spotlight indexes, Final Cut render files, Retrospect and Lightroom catalogs, `.ds_store`, `.localized`, `.lockn`, `.ithmb`, `.xip`, Colima and container images, OrbStack, Dropbox cache, iTunes `.ipsw`, `/Users/.<hidden>` and `/Users/Deleted Users`. None names `Projects`, `Documents`, or `Desktop`, and none matches a path under them.
- **Extension rules that looked dangerous** (`pdf`, `png`, `jpg`, `htm`, `css`, `sh`, `log`, `plist`, `ttf`, `dylib`, `mov`, `mp3`, `tmp`, `cache`, `manifest`, and others, 28 rules) are **all scoped to `/library/application support/steam/`** or to a single named file (`catalog.lrcat.lock`, `com.apple.softwareupdate/cache.db`). A `.pdf` under `~/Projects/Finance` cannot match any of them.
- **Folder exclusions set in the app** (`bzinfo.xml`, `bzdirfilter` entries only): the defaults `/Applications`, `/Library`, `/System`, `/private`, `/usr`, `/bin`, `/sbin`, `/etc`, `/dev`, `/opt`, `/net`, `/home`, `/automount`, `/Developer`, `/.MobileBackups`, `/Backups.backupdb`, with `/` set to `all`. No user-added folder exclusion exists.

**Nothing under `~/Projects/Finance` is excluded.** Corroborated by A3: the folder's file count in the transmitted log matches its on-disk count.

## A3. Proof of upload

`/Library/Backblaze.bzpkg/bzdata/bzlogs/bzreports_lastfilestransmitted/` holds **one** daily log, `11.log` (48.4 MB, 218,769 lines, last written 2026-09-11 12:21:39), because today is the first backup day; there is no second file to count. Counts of lines containing each string (counts only):

| String | Lines in `11.log` |
|---|---:|
| `Projects/Finance` | 28,068 |
| `Projects/Automate` | 187 |
| `finance-python/.venv` | 24,615 |
| `_editable_impl_finance_python.pth` | 9 |

AUDIT-0005 counted 28,071 files under `~/Projects/Finance`; 28,068 transmitted lines is that figure less the three `.DS_Store`-class files the mandatory rules drop. The nine `.pth` lines match the nine copies of that file on disk (§B).

## A4. Private encryption key

Cannot be verified from the command line. Michou's confirmation, verbatim: "Yes i confirm september 11, 2026 at 12:54." Recorded as: Michou confirms PEK enabled, 2026-09-11 12:54.

## A5. Version history

Michou's statement, verbatim: "i got 1 year." Retention selected: 1-year extended version history.

## B6. Source hash

Deviation from the handoff, recorded as such: the handoff asked for a file Michou names under `~/Projects/Finance/Active/`, restored to `~/Downloads/kgme-restore-test/`. Michou instead restored `_editable_impl_finance_python.pth` directly to `~/Downloads/`. That name exists at nine places on disk, and they are not identical:

| Bytes | sha256 | Location |
|---:|---|---|
| 66 | `e760dca4f300f0960ea0319f1ff50a6e648a5e17d0625c0cf609ab32e46e99b3` | `~/Projects/Finance/ARCHIVE PITCHES - SUMMER 26 INTERNSHIP/finance-python/.venv/lib/python3.13/site-packages/` and one `~/.cache/uv/archive-v0/` entry |
| 52 | `25e583453d6b842034192e41b462c1230820b9275e03454dacca6993b418f375` | one `~/.cache/uv/archive-v0/` entry |
| 42 | `3380ecb5f289e9e1fea45c9fca888156c9c0a7db048a8cc27fb3d72d39a93a5d` | six `~/.cache/uv/archive-v0/` entries |

Each is a one-line path file from an editable install at a different historical project location (66 bytes: `…/Projects/Finance/Active/finance-python/src`; 42 bytes: `~/finance-python/src`; 52 bytes: `~/Downloads/finance-python/src`). The restored file in `~/Downloads` is **42 bytes** (Finder metadata, 2026-09-11 12:43), so its source is one of the six identical `uv` cache copies and its expected hash is `3380ecb5…a93a5d`.

## B7. Restore

Done by Michou in the Backblaze web UI on 2026-09-11 at about 12:43; file landed at `~/Downloads/_editable_impl_finance_python.pth`.

## B8. Restored hash and comparison

This session cannot read `~/Downloads` (`Operation not permitted` from `shasum`, `cat`, and the file-read tool alike, with the sandbox off; the `claude` process has no Files and Folders grant for Downloads). Michou ran the hash himself and pasted it at 13:12:

```
3380ecb5f289e9e1fea45c9fca888156c9c0a7db048a8cc27fb3d72d39a93a5d  /Users/michaelgrigorian/Downloads/_editable_impl_finance_python.pth
```

Identical to the on-disk hash of the six 42-byte `~/.cache/uv/archive-v0/` copies computed in B6. The file restored from Backblaze is byte-for-byte the file that was backed up. B9 (deleting the restored file) is Michou's.

## Gate

**Gate 1 (completed backup + tested restore): MET, 2026-09-11T13:12:00-07:00**

## HANDOFF-0020 — firewall

Prior state, recorded 2026-09-11T13:06:00-07:00, verbatim from `/usr/libexec/ApplicationFirewall/socketfilterfw`:

```
--getglobalstate:    Firewall is disabled. (State = 0)
--getallowsigned:    Automatically allow built-in signed software ENABLED.
                     Automatically allow downloaded signed software ENABLED.
--getallowsignedapp: (not a query flag in this macOS build; the tool printed its usage text. --getallowsigned above covers both signed-software settings.)
--getstealthmode:    Firewall stealth mode is off
--getblockall:       Firewall has block all state set to disabled.
```

Michou ran `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on` in his own terminal tab (his report: password entered, no confirmation text printed). New state, verified 2026-09-11T13:40:00-07:00:

```
--getglobalstate:  Firewall is enabled. (State = 1)
--getallowsigned:  Automatically allow built-in signed software ENABLED.
                   Automatically allow downloaded signed software ENABLED.
--getstealthmode:  Firewall stealth mode is off
--getblockall:     Firewall has block all state set to disabled.
```

Only the global state changed. Reversal: `sudo … --setglobalstate off` restores the recorded state exactly.
