---
id: AUDIT-0095
type: report
status: final
handoff: HANDOFF-0056
author: claude-code
source: inferred
sources: ["HANDOFF-0056", "kgme/atlas_slice.py", "kgme/atlas_read.py", "kgme/session.py", "tests/test_atlas_slice.py", "logs/scratch/handoff-0056/baseline.md"]
tier: 2
created: 2026-10-22T02:10:00-07:00
period: 2026-10-22
---

# HANDOFF-0056: atlas slices for agents, and the skill that asks for them

## What was built
- **`kgme atlas --slice HANDOFF-NNNN` and `--around <path>`** (repeatable), with `--base`, `--budget`, `--out`.
  - **The pure half:** `kgme/atlas_slice.py`.
  - **The effects:** `atlas_read.read_slice` and `run_slice`.
- **Built in memory from the tree at `--base`,** through the same `read_sources` and `atlas.build_graph` that `kgme atlas` uses. It writes nothing under `atlas/` and does not depend on the post-commit hook. A tree that is not a checkout, the cheap lane's export shape, is walked instead of listed with `git ls-files`.
- **Seeds:**
  - **What counts:** the handoff's `Outputs` (`loop_outputs.parse_outputs`, with `{a,b}` patterns expanded by the atlas's own `expand`) and every `--around` path. A folder seed takes the nodes under it.
  - **Order:** the files named outright come first, then a folder's, each group sorted by path, so a named file is never cut for a folder's. HANDOFF-0047's Outputs name `docs/readers/`, which without this put ten readers ahead of `kgme/session.py`.
- **One step out, ranked:** the seeds, then the tests that import them, their importers, what they import, and the readers, ADRs, and handoffs that name them, each rank sorted by path, each node once at its first rank. The atlas's links are undirected sets, so direction comes from kinds: a test linking a code node imports it; a code node linking a code node imports it; a document linking a node names it. For a document, the code it links is listed as "names", not "imports".
- **Rendered as plain text:**
  - **One block per node:** its path and rank, the atlas's own line (wikilinks turned into paths), and its neighbours by path. A neighbour's lists stop at 12 with "+N more"; a seed's lists are whole.
  - **The budget:** blocks are kept whole up to the budget (tokens as characters / 4; `kgme.toml [atlas] slice_budget`, 3,000 until that diff is applied).
  - **The last line:** "Cut at the budget of N tokens: K nodes (importer a, document b, ...)", or "Complete: K nodes within N tokens."
- **The data boundary, for every model:** no slice names a path under `memory/`, `logs/`, or a `tier1_paths` root that lies inside the tree, whatever `--base` is.
- **Deterministic:** the same tree and arguments give identical bytes.
- **Carried at launch:** `kgme session loose --handoff ID` builds the handoff's slice from the workspace and writes one carried file, passed with `--append-system-prompt-file`.
  - **Order:** the main checkout's committed `CLAUDE.md`, then the committed skill (`skills/kgme-atlas/SKILL.md`, once Michou has applied it), then the slice.
  - **The start note:** `carried` (the parts, in order), `slice_sha256`, `slice_tokens`, `slice_cut`, and `skill_sha256`. A slice that cannot be built is left out and its reason recorded as `slice_error`: an aid is never a reason to refuse a launch.
  - **A dry run:** it prints the carried file after the settings, under `--- carried: CLAUDE.md, <skill>, slice ---`, and its note names the slice's sha256.
  - **`tight` and `work`** carry nothing.

## Acceptance test
All pass (`tests/test_atlas_slice.py`, 9 tests on a temporary clone of this repository; three new rows in `tests/test_session.py`):
- **A HANDOFF-0047 slice:** `kgme atlas --slice HANDOFF-0047` names `kgme/session.py`, with `tests/test_session.py` among its tests and `kgme/cli.py` as its importer, within the 3,000-token default. It names nothing under `memory/` or `logs/`, and a second run prints identical bytes.
- **`--budget 500`:** truncates within 500 tokens and ends with the "Cut at the budget" line.
- **`--around kgme/ledger.py`:** its seed block lists `kgme/hooks/common.py` among its importers and `tests/test_ledger_concurrency.py` among its tests.
- **A branch's own tree:** from a worktree of the clone on another branch, a module added only there is among `kgme/ledger.py`'s importers in that worktree's slice, and not in the clone's.
- **A tree without git, `memory/`, or `logs/`:** the slice builds. A `tier1_paths` root inside it (`kgme/secret/`, where the atlas would otherwise read it) is dropped, and is named when it is not Tier 1.
- **`kgme session loose --handoff <toy> --dry-run`:** shows the carried file in order (`CLAUDE.md`, the skill when committed, the slice), and the start note records the slice's sha256, tokens, and cut count.
- **Not run yet:** the live check that a `work` session lists `kgme-atlas` among its skills waits for Michou to apply the skill and make the links.

## Measured (§4): the baseline
From the ledger (`logs/scratch/handoff-0056/baseline.md`, extracted by a subagent):

| handoff | session | window | read-only calls before the first edit, per `[hooks] read_only_tools` | Bash calls in that window (all read-only on inspection) | first review's blocking count |
|---|---|---|---|---|---|
| HANDOFF-0047 | `2a6be7da…` | 15:44:04 to 15:46:27 (first edit in its Outputs) | 1 | 5 | 7 (AUDIT-0076) |
| HANDOFF-0055 | `2a6be7da…` | 20:59:44 to 21:02:42 | 1 | 19 | 8 (AUDIT-0084) |

**The metric as defined cannot fall.** `read_only_tools` is Read, Grep, Glob, LS, TodoRead, and this session read files almost entirely through Bash (`cat`, `sed`, `grep`): the whole 25-hour run has 36 Read calls and no Grep, Glob, or LS. So "read-only tool calls before the first edit" is 1 for both handoffs.

**Proposed for the weekly review:** count Bash calls before the first edit as well, and in time have the hook tag a read-only Bash call.

**The baseline is also biased low:** both handoffs ran in one long session that had already read the code. A fresh `loose` launch with a slice starts without that.

**The comparison** (the same numbers for the first three handoffs built with slices) is the weekly review's.

## Decisions made on the route (ADR-023 scores, stakes × edge)
- **Named files before a folder's nodes within the seed rank** (2 × 0.2 = 0.4): the handoff orders ranks and sorts by path within a rank. Without this, an `Outputs` that names a folder fills the budget before the files the handoff names outright.
- **Neighbour lists capped at 12, a seed's whole** (1 × 0.2): one block of a well-connected module (`kgme/ledger.py` has more than 40 neighbours) would otherwise take the budget. A seed's lists are what the acceptance reads ("lists its importers").
- **A slice that fails is left out of a launch, not a refusal** (2 × 0.2 = 0.4): it is an aid, and the note records why.
- **A tree that is not a checkout is walked** (1 × 0.1): the handoff names the cheap lane's export as a `--base`.
- **HANDOFF-0053 has not landed,** so its route's slice (seeded with its `--red` test file) is 0053's to carry, as §3 provides.

## Review
Cycle 1 (AUDIT-0096): BLOCK on six findings, all accepted and fixed directly, red first (`logs/scratch/handoff-0056/red-c1.txt`, 10 failed):
- **F1, the data boundary:** excluded paths are now dropped from the tree before any file is opened, not after the graph is built. A base that is a Tier 1 root, or lies inside one, is refused. The test records every file opened and finds none under the Tier 1 root or `memory/`.
- **F2, the title:** an excluded `--around` path is dropped before the title is made, so `--around memory/example.md` names nothing excluded anywhere in the text.
- **F3, test back-links:** the atlas links a module back to the tests that import it, and that link was read as an import. A test now has no importers; its modules are its imports.
- **F4, documents:** documents that name a file anywhere in backticks, not only in their `Outputs`, now reach its slice. `read_document_refs` reads each reader, ADR, and handoff, and a document seed lists the files it names.
- **F5, the budget:**
  - The header and the longest possible last line are counted before any block, so the whole text fits.
  - A budget of 0 or below is refused, as is one too small for the header and last line.
  - An omitted budget takes the default, but a given 0 is not replaced by it.
- **F6, the dry run:** `--dry-run` with a slice prints its size and writes nothing, `--out` included.
- **F7 (advisory):** a test now shows a named file seeded before a folder's nodes, though it sorts later.
- **F8 (advisory):** `read_slice` has its return annotation. The module sizes are for the weekly review.

Cycle 2 (AUDIT-0097): BLOCK on F2 and F3, both incomplete fixes from cycle 1, fixed red first (`logs/scratch/handoff-0056/red-c2.txt`, 2 failed).
- **F2:** only one leading `./` was stripped, so `././memory/...`, `kgme/../memory/...`, or an absolute path under `logs/` still reached the title. `read_permitted` now resolves each `--around` argument against the base before it is filtered, seeded, or named, and drops one outside the tree.
- **F3:** cycle 1's fix dropped real test-to-test imports (`tests/test_review_run.py` imports `tests/test_review.py`). Imports are now directed edges read from each Python source with the atlas's own `read_imports`, tests included (`atlas_slice.Edges`), rather than inferred from the atlas's undirected links. Both ends of that import are kept.
- **F7 and F8** stay advisory, for the weekly review.

Cycle 3 (AUDIT-0098): BLOCK on F9: cycle 2's normalisation dropped the base itself, so `--around .` gave an empty slice. The root is now a folder seed (`./`) of every permitted node. Red first (`logs/scratch/handoff-0056/red-c3.txt`): `.`, `./`, and the absolute base; each now seeds the tree, is cut at the budget with its seeds counted, and names nothing excluded.

Cycle 4 (AUDIT-0099): BLOCK on F10: with `--base` omitted the base was the current directory, so from `<checkout>/kgme` git returned paths the reader rejects, and the slice came back empty. The base is now the checkout or worktree containing it (`git rev-parse --show-toplevel`; a tree that is not one stays as given). Without `--base`, a relative `--around` path is taken from where you stand. Red first (`logs/scratch/handoff-0056/red-c4.txt`): from `kgme/`, `--slice HANDOFF-0047` finds its handoff, `--around .` seeds `kgme/`, and `--around ledger.py` seeds `kgme/ledger.py`.

Cycle 5 (AUDIT-0100): BLOCK on F1 again, a regression from F10: the base was promoted to its checkout before the Tier 1 check, so `--base <clone>/kgme/secret` (a Tier 1 root) built the clone's slice, and an export nested in a checkout was read as that checkout. Now:
- **Discovery** of the containing checkout happens only when `--base` is omitted (the CLI); a given `--base` is the tree as given, refused at once if it is or lies in a Tier 1 root.
- **A given tree** is read by its tracked files only when it is a checkout's or worktree's root; otherwise it is walked, as an export.
- **Red first** (`logs/scratch/handoff-0056/red-c5.txt`): a Tier 1 base inside a checkout is refused; an export nested in the clone gives its own files, not the clone's.

Cycle 6 (AUDIT-0101): PASS. Advisories for the weekly review: F7 (named files before a folder's nodes in the seed rank, against §1's single path order, tested and explained here), F8 (module sizes: `session.py` 360, `cli.py` 413, `test_session.py` 356, `test_atlas_slice.py` 331).

## Diffs and drafts for Michou (human paths), in `logs/scratch/handoff-0056/`
- **`kgme.toml`** (`kgme.toml.diff`): `slice_budget = 3000` under `[atlas]`.
- **The skill:** `skills/kgme-atlas/SKILL.md` and an empty `skills/kgme-atlas/lessons.md`, for Cowork's review and then Michou's.
  - **What it says:** when to ask for a slice (before planning a handoff, before editing an unread file, when a review names an unfamiliar one); how (use a carried slice, else the command, then open the real files); never to orient by reading `atlas/` or `memory/`.
  - **To apply:** copy it to `skills/kgme-atlas/`, then link it, never copy it:
    ```
    ln -s ../../skills/kgme-atlas .claude/skills/kgme-atlas
    ln -s ../../skills/kgme-atlas .agents/skills/kgme-atlas
    ```
- **`docs/readers/obsidian.md`** (`obsidian.md.diff`, for Cowork): a slices paragraph at the end of Part 3.

## Not done, and why
- **The live skill check in a `work` session** waits for the skill and its links.
- **The weekly comparison** of the baseline is the weekly review's.
