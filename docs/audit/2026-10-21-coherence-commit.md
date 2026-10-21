---
id: AUDIT-0069
type: report
status: final
handoff: HANDOFF-0054
author: claude-code
source: inferred
sources: ["HANDOFF-0054", "make check of 2026-10-21 in brain/ and in a fresh clone", "tests/test_coherence.py"]
tier: 2
created: 2026-10-21T02:10:00-07:00
period: 2026-10-21
---

# HANDOFF-0054: the coherence check resolves paths against the commit, not the machine

Adopted by Michou (`f1846ff`) and built after HANDOFF-0045 was committed (`62c97fd`), before HANDOFF-0051, as he ordered.

**Outputs**, as the handoff lists them: `kgme/vault.py`, `kgme/coherence.py`, `tests/test_coherence.py`, `memory/attachments/.gitkeep`. **Not applied by the builder:** the one sentence for the place the check is described. Neither `README.md` nor any reader describes the coherence check. `docs/schema-v1.md`, a human path, does, so the sentence is below as a diff for Michou.

## Red command, run first
`tests/test_coherence.py::test_the_whole_tree_is_coherent`, run against a fresh `git clone --no-hardlinks` of `main` at `ac1e091` in a temporary directory, before any change: **1 failed**, eleven `coherence-path` findings. Nine are the handoff's diagnosis:
- **Clean-target roots:** `logs/trace` twice, `logs/scratch` twice, `logs/scratch/review.patch` twice, and `logs/ledger-test`.
- **A folder with no tracked file:** `memory/attachments` twice.

Two were not in the diagnosis: `docs/design/cockpit-v0/chibi/README.md` and `docs/handoff/cockpit-design`, both named by `docs/readers/cockpit-design.md`. They resolve in `brain/` only through the local `design` branch, which this checkout has through the design worktree and a fresh clone has only as `origin/design`. That is a second machine-dependent input, fixed with the first. The same check, in-process and kept as `test_the_whole_tree_is_coherent_in_a_fresh_clone`, ran red beside the three fixture cases:
- a path under a clean target was refused for want of the rule;
- an untracked `docs/untracked.md` resolved;
- `origin/design` was not read.

## What was built
1. **Existing paths are the index (§1).** `vault.read_existing_paths` is now the paths `git ls-files -z --cached` lists, tracked and staged, with every folder above each; the `os.walk` and `SKIP_WALK` are gone. A file only this machine has, and a folder that holds no tracked file, do not resolve. Outside a git checkout it raises, so a check never passes over nothing.
2. **Regenerable roots are absent by design (§2).** `vault.read_regenerable` reads every `kgme.toml` `[clean.targets]` entry; the list is never copied into code. `coherence.is_regenerable` treats a path at or under a root, or under a folder some leading part of the path matches as a glob (`**/__pycache__`), as resolving whether or not it exists. `ABSENT_BY_DESIGN` keeps its three non-regenerable cases. `check_tree` takes the entries as `regenerable`, after `design` and before `cls`, and `check_paths` takes them last, after `declared` (review cycle 2 F4); `read_coherence_inputs` returns them sixth, so `kgme lint` passes them through unchanged.
3. **The design branch, wherever the checkout is.** `vault.read_design_paths` lists the local `design` branch when there is one (it may be ahead, since design pushes are Michou's) and `origin/design` otherwise.
4. **`memory/attachments/.gitkeep`**, tracked (§3).
5. **Tests (§4).**
   - The fresh-clone check, in-process. It clones this repository with no hard links, stages into the clone what this checkout has staged, blob by blob from the index, so the clone holds what the next commit will, and fetches the design ref into it.
   - A path under a clean target resolves with its root absent, and one outside does not.
   - An untracked file that exists does not resolve, a staged new file does, and a folder holding only an untracked `.DS_Store` does not.
   - The design paths come from `origin/design` in a clone without a local `design` branch.

## Acceptance test
- **`make check` in `brain/`:** green.
- **`make check` in a fresh clone:** a `git clone --no-hardlinks` in a temporary directory with this change applied to its index, after `make setup` there, is green, 353 passed, `kgme lint` 0 blocking. Its first run failed one test, the fresh-clone test itself: a clone of a clone carries no `origin/design`. The test now fetches the design ref into its clone.
- **`kgme lint` in a fresh clone:** no `coherence-path` finding at all, so none the walk-based check lacked.
- **The design branch:** it tracks no placeholder (`git ls-tree -r design` lists nothing under `logs/trace` or `logs/scratch`). A clone of it, checked with this code, shows 0 findings, so the placeholders in the design worktree, which are untracked there, can be deleted without turning its check red. They were not deleted: that worktree is outside this handoff's Outputs. In their place, the full gate: a fresh clone of the `design` branch (`479816c`), with this change applied to its index and neither `logs/trace` nor `logs/scratch` present at all (it holds only `logs/ledger`), passes `make check` after `make setup`: 365 passed, `kgme lint` 0 blocking (review cycle 1 F2).

## Review
Cycle 1 (AUDIT-0070, `gpt-6-astra`): BLOCK.
- **F1 (blocking):** the clean-target exemption tested only the token as written, while resolution tries it from the root and from the document's folder; `generated/result.md` in `docs/README.md`, with `docs/generated` a clean target, was a finding. Red first: `uv run --frozen pytest -q tests -k c1_f1_a_document_relative` failed with the `generated/result.md` finding beside the expected one. Fixed: `coherence.candidates` gives both readings, and the exemption applies to either.
- **F2 (advisory):** the design-branch gate run is recorded above.
- **F3 (cosmetic):** the test module's side effects are described as they are.

## Decisions made on the route (ADR-023 scores, stakes × edge)
- **`origin/design` as the fallback** for a checkout without a local `design` branch, beyond the handoff's text: the two cockpit-design findings were the same machine dependence. The local branch wins when it exists. 2 × 0.2 = 0.4.
- **The fresh-clone test includes the staged change**, copied blob by blob from the index, so it can pass before the commit that makes it true; nothing outside git's index enters. 2 × 0.1 = 0.2.
- **Every clean target counts, `memory/agent` included:** a document naming a brief that has been cleaned still resolves. That is §2's definition. 2 × 0.2 = 0.4.
- **The sentence goes to `docs/schema-v1.md`**, the one document that describes the coherence checks, as a diff. 1 × 0.2 = 0.2.

## Diff for Michou to apply (human path)
`docs/schema-v1.md`, the paragraph that ends "Both are coherence checks, `advisory` for one week of use and then `blocking`.":

```diff
-... Both are coherence checks, `advisory` for one week of use and then `blocking`.
+... Both are coherence checks, `advisory` for one week of use and then `blocking`. A backticked repository path in a live document resolves against the commit, the index's paths and the folders above them, never against what a machine's runs created, and a path at or under a `kgme.toml` `[clean.targets]` entry resolves whether or not it exists (HANDOFF-0054).
```

## Not done, and why
- The schema sentence above waits for Michou.
- The design worktree's placeholders are his to delete.
