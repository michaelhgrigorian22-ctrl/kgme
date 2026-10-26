---
id: ADR-020
type: decision
status: accepted
created: 2026-10-25T23:50:00-07:00
author: claude-code
source: inferred
sources: ["HANDOFF-0044", "ADR-008", "ADR-015", "ADR-017"]
tier: 2
supersedes: null
---

# ADR-020 — The toolbox: a third-party thing enters KGME through one row

*Draft for Michou's acceptance, written by Claude Code for HANDOFF-0044 from its §1 and its amendments. The diff is shown under ADR-004.*

## Context
Michou, 2026-10-13: "using multiple packages and repos work to build even more intricate and interesting projects is also something we should do way more often." The constitution prices a dependency and does not forbid one:
- **ADR-015:** a third-party dependency costs an ADR line (what, why, source, pinned version).
- **ADR-008:** adding a dependency is a visible act.
- **ADR-017:** the cockpit is plain text and loads no remote asset.

Paid by hand, the price is high enough that tools are rarely asked for. This ADR makes it one row in one file, checked by `kgme lint`.

## Decision
1. **One row, one file.** A third-party package, JavaScript module, skill, harness, model, dataset, asset pack or API enters KGME through one row of `docs/toolbox.md`. The row gives the name, the kind, what it is for, where it comes from (URL), the licence, the pinned version, what we hold and its sha256, the egress host it needs, where it is used, and the handoff that brought it in. Removing a tool is deleting its row and what the row points at.
2. **How each kind is held.**
   - **Python packages** stay in `uv.lock`, and the row points at it.
   - **JavaScript modules** the cockpit serves are vendored as plain, unminified text under `cockpit/static/vendor/`, with the file's sha in the row. A minified file is a bundle and does not qualify.
   - **A vendored skill** lives under `skills/<name>/` with its licence notice, linked from `.claude/skills/` and `.agents/skills/`. Its row holds the folder, hashed over every file in it.
   - **Binary assets** (character packs, fonts, models) are never committed. `make assets` fetches each by its pinned URL and sha into a gitignored folder.
   - **A harness or a cloud model** is recorded as installed on the machine. That sha is not verifiable from a clone.
   - **An API** is a row with its egress host. Its secret lives in the vault (ADR-008), its host in the egress allowlist, and the router (ADR-007) is its only caller.
3. **`kgme lint` checks the rows** (`kgme/toolbox.py`):
   - every import outside the standard library in `kgme/` and `cockpit/` names a package row;
   - no `<script src>` in `cockpit/` names a host;
   - every vendored file and skill has a row whose sha is what the tree holds;
   - every row has a source and a sha, and a model or an API has an egress host.

   All of these are `blocking`. A row without a licence is `advisory` under schema 1.7 and `blocking` from the next schema line.
4. **What stays the same.** A dependency is still a visible act, still pinned, still removable. `memory/` and the vault stay off limits to anything third-party, and the cockpit still loads nothing remote at runtime. The toolbox makes the act cheap; it does not make it silent.

## Consequences
- Asking for a tool costs a row, and the row is the review's first line.
- A harness's or a cloud model's sha describes this machine. A clone checks that the row exists, not the binary.
- The scout that looks for tools is its own handoff, written after HANDOFF-0038 (HANDOFF-0044, amendments 1 and 5).
