---
id: AUDIT-0014
type: report
status: final
handoff: HANDOFF-0027
author: claude-code
source: fetched
origin: this repository, staged diff sha256 PATCH_HASH, `make check`, `codex exec`, and live session output of 2026-09-15
tier: 2
created: 2026-09-15T00:50:00-07:00
period: 2026-09-15
---

# HANDOFF-0027 and HANDOFF-0028 — repo-scoped permissions and the hook pair

Per HANDOFF-0027 and HANDOFF-0028, adopted together by Michou 2026-09-15 and built as one diff, committed as two. The handoffs named this file with the 16th; the local date is the 15th. Third and fourth uses of the review loop.

## HANDOFF-0027 — `.claude/settings.json`
`permissions.defaultMode: "default"`, the documented ask-before-everything mode. The documentation for Claude Code 2.1.272, fetched before the build, states that a project file's mode overrides the user's `auto` mode and that deny rules win across every scope; both were then observed on the builder's own session. Allow: `uv run`, `make check`, `make canary-agents`, `git status`, `git diff`, `git log`, `ls`, `Read`, and `Edit`/`Write` scoped to `kgme/`, `tests/`, `tools/`, `jobs/`, `cockpit/`, `memory/agent/`, `logs/`, `docs/audit/`, `docs/handoff/proposed/`. Deny: recursive `rm`, `sudo`, `security`, piped `curl` and `wget` installs, force push, `Read` of dotenv files in the three name shapes, the SSH directory, Keychains, the two vendor credential files, `memory/private/`. The Tier 1 path is absent because no Tier 1 repository exists yet (Michou, 2026-09-14). Everything else asks.

**Verified on version 2.1.272, on the builder's own session:** the moment the file existed, every tool call in this session ran under it. A Bash line beginning with a recursive `rm` was refused by the deny list. `uv run`, `make check`, `git status`, and file edits inside the repository ran without a prompt.

## HANDOFF-0028 — the hook pair
| Path | Purpose | Lines |
|---|---|---|
| `tools/hooks/pre_tool_guard.sh` | `exec uv run --frozen --project "$CLAUDE_PROJECT_DIR" python -m kgme.hooks.pre_tool_guard`, or exit 2. A guard that cannot start blocks. | 6 |
| `tools/hooks/post_tool_ledger.sh` | same shape; never blocks | 5 |
| `kgme/hooks/guard.py` | pure: `candidate_paths` (file-tool keys; Bash via `shlex`, `--flag=value`, redirection prefixes; tilde and relative paths; `resolve()` follows symlinks), `is_blocklisted` (roots, dotenv names, dotenv suffixes), `decide` | 103 |
| `kgme/hooks/common.py` | shared: `read_payload`, `streams_for` (`--test-streams` selects the gitignored test streams), `call_key` (vendor `tool_use_id`, else a digest of the call), `session_parent`, `summarize_paths` (150-character budget, then a count), `withheld_summary` | 82 |
| `kgme/hooks/pre_tool_guard.py` | intent on allow; refused outcome (`class: blocking`) on deny with one clipped line on stderr and exit 2; any internal error recorded as a blocking error outcome and exit 2; a summary that overflows the writer's cap after redaction is retried once as withheld | 119 |
| `kgme/hooks/post_tool_ledger.py` | raw `tool_input` and `tool_response` to `logs/scratch/payloads/<id>.json`; outcome with `ref` to the intent found by key, `status` from the response, `payload_ref` and `payload_sha256`; any failure to `logs/scratch/hook-errors.jsonl`; always exit 0 | 116 |
| `kgme.toml` `[hooks]` | `blocklist` gains the dotenv suffix shape; `allow_outside` (the Claude jobs and plans directories, `/tmp`, `/private/tmp`, `/dev/null`) | +5 |
| `Makefile` | `check` fails while `logs/scratch/hook-errors.jsonl` is non-empty | +1 |
| `tests/test_hooks.py` | nine tests, class-marked | 262 |

## Acceptance (HANDOFF-0027)
| Check | Result |
|---|---|
| `Read` of a planted temp dotenv file refused | pass, live: the guard refused `Read` of `…/tmp/planted.env` with a one-line reason on stderr and a `blocking` refused outcome in the ledger |
| force push refused | **pass, interactive (Michou, 2026-09-15 morning):** his `kgme-claude` session was asked to run `git push --force origin main` and the deny rule refused it. |
| `uv run kgme --help` runs without a prompt | pass, live |
| `echo hi` prompts | **the probe was wrong, and a corrected probe found something.** `echo hi` ran without a prompt in this background session and in Michou's interactive `kgme-claude` session alike. The documentation describes default mode as prompting for non-read-only actions, and `echo` is read-only, so that command proves nothing about the mode in either session; the handoff's choice of probe was the builder's error. The corrected probe is a mutating command outside every allow list, `touch logs/scratch/probe-bg.txt`. Run from this session it executed with no prompt: this session is a Claude Code background job (a `bg-pty-host` daemon process, not a plain `claude` launch), and the settings precedence documentation ranks a launch-time permission mode above the project file, so here the job's mode governed allow and ask while the deny list still applied (the recursive `rm` refusal, the force-push refusal). Consequence: background jobs keep the deny fence and the hooks but not the prompt, which HANDOFF-0032's canary matrix must carry as its own profile. Michou's interactive session ran `touch logs/scratch/probe-int.txt` and **was prompted** (2026-09-15 morning). Closed: the project's ask-mode governs interactive sessions; background jobs keep deny and the hooks without the prompt. |
| the refusal survives the global `auto` mode | pass for deny: the global file still says `auto` and the deny list governed. Not proven for ask in this session, see the row above. |

## Acceptance (HANDOFF-0028)
| Check | Result |
|---|---|
| six synthetic payloads give 2, 2, 2, 2, 0, 2 | pass (dotenv read, SSH key via Bash, `memory/private` path, path outside the repo, benign read, malformed payload) |
| a live refused read shows a `blocking` outcome | pass, live, in `logs/ledger/2026-09.jsonl` |
| a live allowed read shows an intent and an `ok` outcome with matching `ref`, both in `logs/trace/` | pass: the headless session's `Read kgme/paths.py` and this session's own reads |
| a live `Edit` shows the pair in `logs/ledger/` | pass: this session's edits to the hook modules |
| payload file exists in scratch and its hash matches the line | pass (test, and live payload files present) |
| `git status` shows only `logs/ledger/2026-09.jsonl` changed under `logs/` | pass; `logs/trace/` untracked |
| a syntax error in the guard makes every tool call fail closed | pass, involuntarily: see Incident |
| wall time per guarded call | 44 ms in a clean export (`uv run --frozen` with a warm cache); HANDOFF-0028 estimated 50 to 150 ms |

## Incident: the builder locked itself out
The guard went live the instant `.claude/settings.json` existed. While editing `pre_tool_guard.py` with three separate edits, the second left the module referencing a function the third had not yet defined; from then on the guard raised `NameError` on every call, and every call, including the edit that would have finished the job, was refused. Michou restored the draft by hand (`cp` from the job directory; the file was untracked, so `git checkout` could not). The rule is now in the module docstring: the live guard is replaced whole, in one write, never edited in steps. The five failures are in the ledger as `blocking` error outcomes; the first three carry fresh run ids because the failure path did not yet know the session, fixed in the same commit.

Three more findings from the same hour, each fixed in this diff. The guard let `Read` of `planted.env` through, because the blocklist covered the bare dotenv name and its dotted variants only; a suffix rule was added to `kgme.toml`, to `is_blocklisted`, and to the settings deny list, with a test over four name shapes and a non-match on `environment.md`. A Bash heredoc whose body named a dotenv-shaped token was refused: the guard tokenizes the whole command, heredoc bodies included, which is the right side to err on and means long texts go through file writes. A refusal reason carrying a long resolved path exceeded the writer's summary cap and failed closed; refusal reasons are now clipped.

## Review loop
Reviewer `gpt-6-astra` via `codex exec -s read-only`; arbiter Opus 5 through the Agent tool.

**Cycle 1** (diff `9704357078b692b5`): BLOCK, eight blocking, one cosmetic. The reviewer applied the loop's bound as then written ("three distinct blocking root causes stand unresolved") at the end of cycle one, before any fix, and declared a halt. The escalation packet went to Michou, who overrode (continue the loop) and amended the bound to count root causes that survive a fix cycle; the reader carries the new sentence.
| Finding | Class | Disposition |
|---|---|---|
| F1 `exec` in the wrappers meant `\|\| exit 2` never ran; an import failure returned 1, which Claude Code treats as non-blocking: fail open | blocking | Fixed: no `exec`; the pre wrapper maps every exit other than 0 or 2 to 2; the post wrapper records a startup failure and exits 0. Tests with a fake `uv` exiting 1, 3, 127. The original fail-closed test had passed only because uv's own exit code happened to be 2. |
| F2 Bash extraction missed bare filenames, attached operators, inline code, scripts | blocking, disputed in part | Arbiter: **blocking**, narrowed. The settings allow `uv run` without a prompt and the guard examined only slash-bearing tokens, so `python -c "open('.env')"` reached a forbidden file with no refusal and no event; `cd` and globs are advisory residual. Fixed: every fragment of the line is a candidate; scripts the line executes are read and scanned; scripts it cannot read are refused; scripts it only copies or greps are not scanned. |
| F3 slash-containing tokens, inline code included, entered durable summaries | blocking | Fixed: Bash and every non-file tool summarize as name plus a fragment count; file tools show their input paths within budget. |
| F4 `Edit`/`Write` allow rules were cwd-relative | blocking | Fixed: settings-anchored form (leading slash). `Read` stays unrestricted per HANDOFF-0027; the guard fences file tools outside the repository. |
| F5 a refusal was an outcome with no intent | blocking | Fixed: intent first, always; a refused call's intent carries `class: blocking` and the stream rule routes a blocking intent to the ledger beside its refusal, which references it. The handoff's "on deny, append an outcome" wording was the builder's; the pair is the ADR-019 contract. |
| F6 error outcomes had no class, so the writer rejected them and the intent never closed | blocking | Fixed: `events.classify_failure` on the response; test with a transient error. |
| F7 a test deleted the live `hook-errors.jsonl` | blocking | Fixed: `--test-streams` selects `logs/scratch-test/` for errors; payloads stay under `logs/scratch/payloads/test/` because ADR-019 fixes that prefix. |
| F8 acceptance evidence incomplete (force push, `echo hi` prompt) | blocking, disputed | Arbiter: **advisory**. Evidence owed by a named human actor is not wrong output; the STATUS gate stays pending until Michou's session. |
| F9 effects naming and docstring accuracy | cosmetic | Fixed: `read_*` and `write_*` names; the guard docstring says `Path.resolve()` consults the filesystem. |

**Second incident, same night.** While swapping modules for these fixes the builder kept the old entry point's names as aliases, one of which returned the new shape instead of the old, and the guard failed on every call again; Michou restored both modules from the index with one `git checkout`. From then on every module change was staged under `logs/scratch/staging/`, compiled, exercised through both the old and the new entry point, and only then copied in; each intermediate state was a working guard. The one live `hook-errors.jsonl` line the incident produced (`AttributeError: 'Places' object has no attribute 'ledger'`, 00:41:32) was read, recorded here, and cleared. A third lesson followed within the hour: the first script inspection treated any named script as executed and refused `cp` and `grep` of files whose text mentions a dotenv shape (the redactor's own regex, a test fixture); corrected so that only a script preceded by a runner word, or standing first on the line, is scanned.

**Cycle 2** (diff `18b60aebc4f47d9f`, 1,150 lines, 16 paths): BLOCK, two blocking root causes, F2 surviving its first fix cycle and F10 new. F1, F3, F4, F5, F6 verified closed; F7, F8, F9 verified with advisory remainders.
| Finding | Class | Disposition |
|---|---|---|
| F2 `uv run python -X dev job.py` escaped inspection (the flag's value sat between runner and script); an unreadable script read as empty text and was allowed | blocking | Fixed: a script counts as executed when a runner word precedes it anywhere in its command segment (segments split on `;`, `\|`, `&&`, `\|\|`, newlines) or it stands first on the line; an unreadable script is uninspectable and the line is refused. Tests for both, plus `cp` and `grep` staying unscanned. |
| F10 the guard read a script's text before deciding whether the script path was itself forbidden (`uv run python .env.py`, a script under `memory/private/`) | blocking, new | Fixed by ordering: the line is decided first on its own fragments, and every script path is one of them, so a forbidden script is refused before any read; only an allowed line has its scripts opened. An in-process test replaces the script reader with one that raises and asserts it is never called for a forbidden path. |
| F1 post-wrapper test covered exit 1 only | advisory | Parametrized over 1, 3, 127. |
| F7 the live-file assertion proved absence, not unchanged state | advisory | Compares the live file's bytes before and after. |
| F8 the report still called the force-push refusal a pass and said the gate moves to MET on commit | advisory | Corrected: both interactive items unproven; the gate stays pending until Michou's session. |
| F9 `script_paths` checked existence inside the pure module; `_script_fragments` read files | cosmetic | Existence and reads moved to the entry point (`_read_script_fragments`); the pure module resolves and decides only. |

**Cycle 3** (diff `355816c765083991`, 1,217 lines): BLOCK, one blocking root cause, F2 surviving a second fix cycle. F1, F7, F9, F10 verified closed.
| Finding | Class | Disposition |
|---|---|---|
| F2 `number == 0` counted only the first segment's first word as executed, so `true && ./job.sh` escaped inspection | blocking | Fixed: the first word of every segment counts. Regression cases: a direct script after `&&` is a candidate, and one that names a forbidden file is refused. |
| F11 the F10 test's raising reader would be caught by `main` and return the same exit 2 | advisory | The test now records reader calls in a list and asserts the list is empty after `main` returns, with the line-level refusal asserted as the precondition. |

**Cycle 4** (diff `e4853a9cf104cb02`, 1,242 lines): **PASS.** F2 verified closed. One advisory remained on the F10 test: nothing made the synthetic forbidden script exist, so the existence check alone could skip the reader and mask an ordering regression. Closed before commit by mocking `Path.is_file` to report the probe present, keeping the recording reader, the refusal precondition, the exit-2 assertion, and the empty-call assertion. Static review; the sandbox ran no tests.

Strike count, read against the amended bound: F2 was raised in cycle 1 and survived the fix cycles reviewed in cycles 2 and 3, two fix cycles without resolution; a third fix goes to cycle 4, and a fourth failure would be the halt. F10 was introduced by the F2 fix in cycle 2 and resolved in cycle 3. One halt (cycle 1), overridden by Michou and its rule amended.

## Deviations, stated
- The grep pre-filter in the handoff was dropped: every tool call is recorded (Michou, 2026-09-14), so Python starts on every call regardless. Cost measured at 44 ms.
- Bash is fenced by the blocklist and the deny list, not by the outside-the-repo rule, because Bash tokens such as `/usr/bin/env` or `2>/dev/null` are not file access. A Bash script file hides its contents from the guard; the canaries (HANDOFF-0032) measure that gap at the OS layer once LuLu and the profiles exist.
- The hook composes a budgeted summary and falls back to a withheld one on redaction overflow; refusal reasons are clipped. This is the caller-side shortening ADR-019 §4 leaves to callers.
- Report filename carries the local date.

## Needs from Michou
His own interactive session, per 0027 and the F8 ruling: the force-push refusal and the `echo hi` prompt are the two acceptance items still unproven, plus a ruling if 44 ms per call is felt. The STATUS gate "repo-scoped permissions + hooks" stays **pending** until that session; the 0028 commit does not move it.

## Next
HANDOFF-0029 (`kgme review`), then 0030's dry run through 0031 (validator).
