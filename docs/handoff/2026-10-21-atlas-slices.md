---
id: HANDOFF-0056
type: handoff
created: 2026-10-21T23:39:00-07:00
from: michou
to: claude-code
tier: 2
status: open
depends_on: [HANDOFF-0047, HANDOFF-0051]
plan_ref: PLAN-PHASE-1 step 9d
---

# Handoff 0056 — Atlas slices: a map of a task's neighbourhood for any model, and the skill that asks for it

## Why
Michou, 2026-10-21, after a day with the atlas as his Obsidian vault: "does this or cna this in any way help contextualize the agents that I run both with regard to new project branches and new models altogether? i feel like its a simpler context window", then "or a skill in kgme app".

The atlas (HANDOFF-0051) is already a dependency map of the repository: about 330 notes and 7,700 words, recording which module imports which, which tests cover which module, which handoff produced which audit, and which reader or ADR names which file. Agents get none of it today. Claude Code and Codex explore well, so for them the gain is modest. It is largest for the models that come next: the cheap lane's DeepSeek (HANDOFF-0053), billed per token; local models on the second host, with small windows; and crew builders in fresh worktrees (HANDOFF-0048). None of them should spend their first turns finding where things are.

What helps is not the whole map but a slice: the files a handoff names plus one step out (their imports, their importers, their tests, the readers and ADRs that name them), as plain text under a token budget. Agents reach it two ways. A skill (ADR-022 §5: roles and know-how are skills any harness reads) tells an agent when to ask for a slice and how to read it. The launcher carries the slice into sessions that discover nothing for themselves, as it already carries the committed `CLAUDE.md` to `loose` (ADR-022, addendum of 2026-10-21). The command builds the slice; the skill only calls it, so the data boundary is enforced in code, not left to a model following links.

## What
1. **`kgme atlas --slice HANDOFF-NNNN`, `kgme atlas --around <path>`** (either or both; `--around` may repeat), with `--base <dir>` (default: the checkout it runs from), `--budget <tokens>` and `--out <file>` (default: stdout).
   - **Built in memory from the tree it describes.** The graph comes from the tracked files at `--base`, through the same reader and builder `kgme atlas` uses. It writes nothing under `atlas/` and does not depend on the post-commit hook having run, so a worktree on any branch, or an export like the cheap lane's, gets a slice of its own tree.
   - **Seeds:** the handoff's `Outputs` (parsed as the loop already parses them) and any `--around` paths; a folder seed takes the nodes under it.
   - **One step out, ranked:** the seeds' own nodes; then the tests that import them; then their importers; then what they import; then the readers, ADRs and handoffs that name them. Within each rank, sorted by path.
   - **Rendered as plain text, not wikilinks:** one block per node, its path, the one line the atlas already writes about it, and its neighbours by path. Truncated at the budget (tokens estimated as characters ÷ 4; default from `kgme.toml [atlas] slice_budget`), ending with one line naming how many nodes were cut and from which ranks.
   - **The data boundary, for every model:** a slice never names a path under `memory/`, `logs/`, or a `tier1_paths` root. A slice built from a cheap-lane export lacks them anyway; the filter holds whatever `--base` points at.
   - **Deterministic:** the same tree and arguments give identical bytes.
2. **The skill:** a `kgme-atlas` skill folder with its SKILL.md and an empty `lessons.md`, in the SKILL.md format Claude Code and Codex both read. Short and model-agnostic. When: before planning a handoff, before editing a file not yet read in the session, when a review names an unfamiliar file. How: run the command for the handoff or the path, then open the real files it names (the map says where things are, not what they say). Never orient by reading `atlas/` or `memory/` directly. If a slice was carried into the prompt at launch, use it and do not rebuild it. Skills are human paths (ADR-022 §5): Claude Code drafts both files to `logs/scratch/handoff-0056/`, Cowork reviews the text, and Michou applies them. Until 0048's `kgme skills install`, Michou links the folder into the repository's `.claude/skills/` and `.agents/skills/` by hand (a link, never a copy).
3. **Carried at launch.** `kgme session loose --handoff ID` builds the slice for that handoff from the workspace and appends it, with the skill's SKILL.md, to the file it already passes with `--append-system-prompt-file`: one file, `CLAUDE.md` first, then the skill, then the slice. The start note records the slice's sha256, its token estimate, and how many nodes were cut. If HANDOFF-0053 has landed when this is built, its route carries a slice seeded with the test file its `--red` command names; if not, 0053 does so when it lands. `tight` and `work` discover the skill as usual and carry nothing.
4. **Measured, so it earns its place (ADR-023, Learn).** The report gives a baseline from the ledger for the sessions that built HANDOFF-0047 and HANDOFF-0055, each Claude Code session by the hooks' `run_id`: read-only tool calls before the session's first edit, and the first review's blocking count. The same two numbers are read for the first three handoffs built with slices, at the weekly review. If they do not fall, the carry is removed and the skill stays as an interactive aid.

## Outputs
`kgme/atlas_slice.py` (pure: seeds, ranking, filter, rendering), `kgme/atlas_read.py` (the slice's effects), `kgme/cli.py` (`atlas` flags), `kgme/session.py` (the carried file under `loose`), `kgme.toml` (`[atlas] slice_budget`: a diff Michou applies), `skills/kgme-atlas/SKILL.md` and `skills/kgme-atlas/lessons.md` (drafts Michou applies), `.claude/skills/kgme-atlas` and `.agents/skills/kgme-atlas` (links Michou makes), `tests/test_atlas_slice.py`, rows in `tests/test_session.py`, and a slices section in `docs/readers/obsidian.md` (as a diff for Cowork).

## Acceptance test (under fifteen minutes)
- `kgme atlas --slice HANDOFF-0047` on a temporary clone names `kgme/session.py`, the tests that import it, and its importers, within the default budget; names nothing under `memory/` or `logs/`; and a second run prints identical bytes.
- `--budget 500` truncates and ends with the line naming what was cut.
- `--around kgme/ledger.py` lists its importers, `kgme/hooks/common.py` among them, and `tests/test_ledger_concurrency.py`.
- From a worktree of a clone on another branch, a file added only on that branch appears in its slice and not in the main checkout's.
- Built from a repository without `memory/` or `logs/` (the cheap lane's shape), the slice builds and names nothing outside that tree; a `tier1_paths` root is dropped even where it is tracked.
- `kgme session loose --handoff <toy> --dry-run` shows the carried file in order (`CLAUDE.md`, the skill, the slice), and its start note records the slice's sha256.
- Live, after Michou applies the skill and its links: a `work` session lists `kgme-atlas` among its skills.

## Defaults chosen (ADR-023, stakes × edge)
- Every slice excludes `memory/`, `logs/` and Tier 1 roots, for every model, rather than a filter per provider: 2 × 0.2 = 0.4. Code context needs none of them, and one rule cannot be misrouted.
- The slice is built in memory from the tree it describes, not read from `atlas/`: 1 × 0.1 = 0.1. This leaves aside the post-commit hook's skip of a worktree whose branch lacks the atlas code (the design worktree today), which only matters to Obsidian, and Obsidian opens the main checkout.
- Default budget: 3,000 tokens: 1 × 0.3 = 0.3. It is a `kgme.toml` value Michou can change.
- The skill is linked by hand until 0048's installer: 1 × 0.1 = 0.1.

## Reviewer
Codex read-only under `kgme review`. Cowork reviews the skill text and the reader section before Michou applies them.

## Reversibility
Door: two-way. Blast radius: one read-only command, one skill, one carried file in `loose` launches. Remove the two links to stop the skill being discovered, remove the carry lines to stop the prompt, or `git revert`.

## Needs from Michou
Adoption. Applying the `kgme.toml` diff and the skill files, and making the two links.

## Report
`docs/audit/2026-10-DD-atlas-slices.md`, named in `report:` on closing. Commit `atlas: slices for agents, and the skill that asks for them (HANDOFF-0056)`.
