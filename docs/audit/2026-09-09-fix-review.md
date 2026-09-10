---
id: AUDIT-0004
type: report
status: final
handoff: HANDOFF-0013
author: codex
source: inferred
tier: 2
created: 2026-09-09T23:20:37-07:00
---

# Independent review of proposed fixes

The 7 proposals address real audit findings, but 0 are approvable as written: 5 require amendment and 2 require replacement procedures. This review feeds Michou's approval decision; it does not authorize or execute any proposed fix. Evidence is the [machine audit](2026-09-09-machine-audit.md), [fix plan](2026-09-09-fix-plan.md), the proposals linked below, CLAUDE.md, ADR-002, ADR-008, ADR-011, and Phase 0. Command behavior was checked against installed macOS help/manuals and the official Homebrew sources cited inline; historical audit observations were not treated as fresh machine measurements.

## HANDOFF-0006: Time Machine destination

**Verdict: amend.** The [proposal](../handoff/proposed/2026-09-09-time-machine-destination.md) correctly cites audit gap 2: “No Time Machine destination configured.” The stronger assertion that Finance and School have no rollback path is unproven: the audit did not exclude other backups. Step 3 always erases an entire disk even though the goal is to configure a destination, and `$DISK` is never assigned or validated. Require a fresh identifier and capacity check, distinguish an existing suitable volume from a disk requiring erasure, and obtain approval for the exact whole-disk operation. The offered network-share alternative has no corresponding procedure.

The irreversibility warning for erasure is correct; removing the destination does not undo `tmutil enable` or restore prior destinations. Installed `tmutil(8)` states that `setdestination` replaces the destination list unless `-a` is used, requires Full Disk Access as well as root, and that `startbackup --auto` does not wait for completion. Record prior settings and verify a completed backup to the intended destination before relying on it. Sudo is disclosed, but Full Disk Access and backup encryption/data scope need an explicit decision under ADR-002 before copying private data; passwords must remain in Michou's own UI interaction under ADR-008.

**Simpler or safer:** Have Michou select an appropriate destination through Time Machine settings, approve erasure only if necessary, and verify the first completed backup before dependent work.

## HANDOFF-0007: Application firewall

**Verdict: amend.** The [proposal](../handoff/proposed/2026-09-09-enable-application-firewall.md) correctly cites audit gap 3, “Application firewall off,” but ADR-008 does not actually require a firewall; its device-security bullet names FileVault and Time Machine. The audit's own attribution to ADR-008 is unsupported by that ADR.

Step 1 matches the goal; steps 2 and 3 change automatic incoming-connection permissions, and optional step 4 changes stealth behavior. Installed `socketfilterfw -h` identifies `--setallowsigned` as built-in signed applications and `--setallowsignedapp` as downloaded signed applications, so the proposal's App Store description and claim that step 2 allows all listed third-party apps are wrong. Sudo is disclosed and no dependency is introduced, but these extra permissions exceed the cited finding under least privilege. Rollback to `off` is valid for the audited global state; setting every other flag to `off` cannot restore unknown previous values. Capture those values if those settings are separately approved.

**Simpler or safer:** Enable only the global firewall state and verify it, preserving the existing allowance and stealth settings.

## HANDOFF-0008: Homebrew

**Verdict: amend.** The [proposal](../handoff/proposed/2026-09-09-install-homebrew.md) addresses audit gap 5, “Homebrew not installed.” The audit establishes absence, but does not record the exact `command not found: brew` output presented as a quotation. Downloading before execution makes inspection possible, but `HEAD` is mutable, 40 lines do not expose the full installer, and neither the installer nor the fetched package-manager revision is pinned as ADR-008 requires.

The [official installer](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh) uses noninteractive sudo when `NONINTERACTIVE` is set, so step 4 does not prompt for a sudo password as claimed and can fail without existing authorization. It also performs recursive ownership changes under the Homebrew repository and, conditionally, its cache, and can write `/etc/paths.d/homebrew`; these exceed the stated `/opt/homebrew/` footprint. Disclose the full write set and review immutable installer and runtime revisions before approval. Sudo itself is disclosed.

The unpinned uninstall script is a new destructive action, not exact restoration of original ownership and shell state. Step 5 needs a minimal reviewed shell-profile diff, an absent-file branch, and a non-overwriting backup; sourcing the whole profile executes unrelated user code. Persistent staging in Downloads also conflicts with Phase 0 §3. The claim that five seconds of inspection is sufficient has no evidentiary basis.

**Simpler or safer:** Use an immutable, fully reviewed installer with pinned fetched revisions, interactive human sudo, and a narrowly approved shell-profile edit, documenting residual state on uninstall.

## HANDOFF-0009: GitHub CLI

**Verdict: amend.** The [proposal](../handoff/proposed/2026-09-09-install-gh-cli.md) correctly maps to audit gap 5, although the audit records “not installed,” not its purported exact shell error. `brew install gh` and “current stable” do not select an approved version under ADR-008. The [official formula metadata](https://formulae.brew.sh/api/formula/gh.json), checked in this session, lists 0 runtime dependencies, a Go build dependency, and an Apple Silicon Tahoe bottle; do not invent a large runtime dependency tree, but require the approved bottle or separately approve a source-build dependency set.

The [Homebrew manual](https://docs.brew.sh/Manpage) documents automatic update behavior before installation and automatic removal of unused dependencies on uninstall. Accordingly, installation has network effects before authentication, uninstall can touch more than `gh`, and cache removal is not an exact rollback guarantee. Pin the selected artifact and checksum before installation, constrain automatic side effects, and verify the exact version afterward. No sudo is proposed, and deferring login is correct. Delete the out-of-scope `rm -rf ~/.config/gh` cleanup advice: it can remove unrelated configuration and falls under the explicit deletion gate.

**Simpler or safer:** Install one approved, checksum-verified `gh` release artifact with bounded cleanup, keeping authentication as a separate human step.

## HANDOFF-0010: SSH key

**Verdict: reject the executable procedure.** The [proposal](../handoff/proposed/2026-09-09-ssh-key-for-github.md) cites real audit gap 4, “No SSH key material,” and Phase 0 names SSH registration; absence of SSH does not by itself prove that every private GitHub remote is blocked. The key comment matches HANDOFF-0005's supplied email, but that does not authorize credential handling.

Step 5 explicitly reads a file inside `~/.ssh`, contrary to CLAUDE.md's categorical ban on reading that directory's contents, even though the public key is not itself secret. Steps 2 and 4 also need reconciliation with ADR-008's requirement that secrets live in Keychain or a password manager rather than files: a passphrase-protected private-key file is still a policy exception, not one the reviewer can silently grant. Existing-file checks are absent, so the old audit cannot justify overwriting a key or config. The config template must use real newlines and a bounded host stanza.

`rm -rf ~/.ssh` is not a rollback: it destroys the generated private key and any unrelated keys, configuration, or trust records present at execution time. Keychain deletion and GitHub revocation are separate credential and outward-facing operations requiring their own approval; none should be a generic cleanup instruction. No sudo or package dependency is introduced, but the secret-access and deletion conflicts are decisive.

**Simpler or safer:** Replace this with a human-operated authentication setup after an explicit policy decision, letting the agent receive only non-secret success status.

## HANDOFF-0011: Paths with spaces

**Verdict: reject the executable procedure.** The [proposal](../handoff/proposed/2026-09-09-rename-space-paths.md) cites audit gap 9 and the actual Phase 0 path convention. However, step 3's `grep -rIl` reads contents across all of `~/Projects`, including possible `.env` files and Tier 1 material; printing filenames only does not make those reads permissible under CLAUDE.md and ADR-002. A project-wide search also cannot prove the absence of references outside that tree.

Step 3 additionally authorizes workbook modifications inside a rename proposal without a named file set, reviewed diffs, XML-only editing procedure, or recalculation and link verification. Its unquoted ZIP-member wildcard can be expanded or rejected by zsh before `unzip` runs; link targets may be in relationship parts, so this is not a complete link audit. Step 4 needs source/destination validation and collision checks: `mv` can overwrite a file or move into an existing directory. No sudo or dependencies are proposed, but the read and write scope violates least privilege.

The reversal warning correctly recognizes that reference edits must also be undone; a reverse `mv` alone still cannot restore overwritten destinations or workbook state. Personal's smaller file count is not evidence that its references are safe. HANDOFF-0014 now records an intended Finance disposal inventory, creating an additional planning conflict that must be resolved before scheduling Finance renames; it was read as context, not executed.

**Simpler or safer:** Use an approved metadata-only candidate manifest, allowlisted reference checks outside secret and Tier 1 paths, and separate reviewed edits with a verified backup and collision-safe rename map.

## HANDOFF-0012: Power settings

**Verdict: amend, retaining the observation deferral.** The [proposal](../handoff/proposed/2026-09-09-pmset-heartbeat-decision.md) cites audit gap 6's real `sleep=0` and active assertions. Its assertion that uptime proves the Mac has not slept is unsupported: uptime is not a sleep history. Installed `pmset(1)` describes `sleep` as an idle timer and explicitly says power assertions can override settings, so option A cannot guarantee heartbeat delivery and option B does not guarantee sleep while existing assertions remain active.

Option B also changes display timers, which need a stated reason beyond heartbeat scheduling. Option C writes the repeating schedule; `pmset(1)` permits only one repeating on/off pair, so pre-existing events must be captured first. All sudo commands are disclosed and no dependency is added. However, `restoredefaults` restores defaults, not the audited custom state, and `repeat cancel` cannot restore a displaced repeat schedule. Record `pmset -g custom`, `pmset -g sched`, and relevant assertions, then restore only changed values. The statement that allowing sleep stops `caffeinate` reverses the documented assertion relationship.

**Simpler or safer:** After the 2-week observation window, change only the chosen power settings, preserve their prior values and schedule, and test the actual heartbeat under the observed lid and power conditions.

## Ordering and execution eligibility

The fix plan correctly places HANDOFF-0008 before HANDOFF-0009 and defers HANDOFF-0012 until 2 weeks of observation. HANDOFF-0006 should gate any work justified by backup-based reversibility on a completed backup, not merely a running first backup; explicitly add that dependency to HANDOFF-0011 and resolve its Finance scope against HANDOFF-0014. A first backup started before key creation also cannot be presumed to contain that later key. The firewall has no Homebrew or SSH dependency and can run independently once amended.

All 7 proposals have `from: claude-code` and `status: proposed`, matching HANDOFF-0003's requested drafting format but failing CLAUDE.md/ADR-011's executable-handoff rule requiring an open handoff from Cowork or Michou. Changing status alone does not resolve that mismatch. Require explicit human adoption or reissuance before execution; this review's authorization applies only to HANDOFF-0013. Likewise, `gh` installation does not itself authorize login, repository creation, or push.

## Gaps needing coverage

Audit gaps 7 and 12 need a concrete configuration-reconciliation proposal or an explicit recorded deferral, not merely attribution to Cowork. [AUDIT-0002](2026-09-09-global-claude-config.md) §2 reports only a workbook post-tool hook, while ADR-008 requires dangerous-command enforcement and an append-only tool ledger; §3 also identifies memory routing into the Finance tree. Ownership of the eventual edits does not remove these missing outcomes. The prescribed `.Codex` memory index failed to open in this session because the path does not exist, confirming an actionable pointer problem without inspecting secrets or global configuration contents.

Audit gap 8 needs only a recorded disposition: Phase 0 §3 already says other Pythons remain untouched, and CLAUDE.md already mandates `uv`; no removal or installation proposal is warranted. Gap 10 needs a recorded install-or-defer decision if the CLI is required, based on a fresh executable-presence check rather than the old audit; this review does not infer CLI installation merely from operating as Codex. Gap 1 is already resolved by completed HANDOFF-0005, and gap 13 by HANDOFF-0002. Gaps 11 and 14 justify no repair on the available evidence, while gap 15 is explicitly assigned to the later Ollama step. No additional tool installation is justified by those observations.

Only this report and HANDOFF-0013's completion metadata were authorized for writing; no proposal, system setting, credential, workbook, or other repository file was changed, and no commit was run.
