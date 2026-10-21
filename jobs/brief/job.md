# brief — Loop 0, `kgme brief` v1 (HANDOFF-0034)

**Purpose.** The first loop that works end to end: manual, read-only against canonical inputs, local, no model call (Michou's ruling of 2026-09-14). It exercises the ledger's intent/outcome pair, the validator, the manifest, and `kgme clean`, and writes the artefact the cockpit will show. v2 adds a model for prose after a week of hand runs.

**Invocation.** `kgme brief [--date YYYY-MM-DD] [--dry-run]`, or `uv run python jobs/brief/run.py` with the same flags. Never scheduled in Phase 1.

**Inputs.** Every `.md` under `memory/notes/` and `memory/agent/` except `memory/agent/brief/` (the job never reads its own output); `memory/daily/<date>.md` if present; `memory/inbox/friction-log.md`. Each is read only after `manifest.toml` allows it and `kgme/lint.py` finds nothing blocking; one refusal is a `blocking` outcome for the run and no artefact. Of what is read, the brief is about: reminders with `status: open`; tasks with `status` in `open`, `doing`; the daily note; the friction log.

**Output.** `memory/agent/brief/<date>.md`: frontmatter `type: note, status: active, tier: 2, author: kgme, source: inferred, sources: [every input id]`; `id` and `created` kept across replacements, `modified` moved only when the content moves. Body: `# Brief <date>`, then `## Due and overdue` (items due on or before the day, sorted by due, then priority, then id), `## Today` (the daily note read by its headings, Today, Learned, Problems and solutions, Tomorrow, each labelled; until the day's own note exists, the previous evening's, drafted by `kgme daily` (HANDOFF-0050); a missing note is stated), `## Open tasks`, `## Friction since last brief` (friction-log entries dated on or after the previous brief's day, inclusive, plus the daily note's Friction section), `## Inputs` (id, path, sha256 of each). Every empty section says so.

**Transaction.** Key `brief:<date>`. `intent` before any write, carrying the intended destination and sha256 in its payload and the identity in its summary; the artefact is written to a temp file beside the destination, `fsync`, `os.replace`; `outcome` after. On start, an intent without an outcome is closed `ok` when the destination holds the intended hash, else `transient`, and the run rebuilds. A brief deleted with `kgme clean briefs --yes` regenerates byte-identical: its identity comes back from the ledger.

**Dry run.** `--dry-run` prints the brief to stdout, writes no file, appends one `note`.

**Side effects.** One file under `memory/agent/brief/`; one payload under `logs/scratch/payloads/`; ledger events (`intent`, `outcome`, or one `note`). Reads nothing outside `memory/` and `kgme.toml`.

**Manifest.** `manifest.toml` beside this file (HANDOFF-0032): read paths `memory/notes`, `memory/agent`, `memory/daily`, `memory/inbox`, `memory/templates`; write path `memory/agent/brief`; no network.
