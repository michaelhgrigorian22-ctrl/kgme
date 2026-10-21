# clean — the disposable-class deleter (HANDOFF-0033)

**Purpose.** Delete regenerable output (ADR-012's disposable class) by named target and nothing else, so that bare `rm -rf` can stay denied everywhere (Michou's ruling of 2026-09-14). Loop 0's reconstruction test deletes a brief with `kgme clean briefs --yes` and regenerates it.

**Invocation.** `kgme clean <target>` prints the plan and deletes nothing; `kgme clean <target> --yes` deletes it. `kgme clean <anything else>` exits 2 with the list of targets. The command takes no path: it acts on this repository's root. The tests reach a seeded checkout by calling `run_clean` with that checkout as both the base and the authorized root, which the CLI and the runner cannot say; a base inside or above the authorized root, or one without `.git`, exits 2 before anything is read or written. `jobs/clean/run.py` is the same run, callable from the job folder. Never scheduled in Phase 1.

**Inputs.** The target's entries from `kgme.toml` `[clean.targets]`; `jobs/clean/manifest.toml`; the filesystem under the target's roots, listed with `lstat`, no symlink followed.

| Target | Entries | What goes |
|---|---|---|
| `briefs` | `memory/agent/brief` | every brief; the folder stays |
| `agent` | `memory/agent` | every machine note and brief; the folder stays |
| `scratch` | `logs/scratch` | review patches, payloads, hook errors, staging; the folder stays |
| `trace` | `logs/trace` | the untracked read-only tool stream (ADR-019 §2) |
| `caches` | `**/__pycache__`, `.ruff_cache`, `.pytest_cache` | each match whole; a glob never enters `.git` or `.venv` |
| `venv` | `.venv` | the environment's contents; `uv sync --frozen` rebuilds it |
| `ledger-test` | `logs/ledger-test`, `logs/trace-test` | the test streams |
| `kept` | `memory/**/.*.capture-*` | the copies `kgme capture` keeps beside a file it adds a line to (HANDOFF-0050), each only while it hashes to what its capture's `kept` ledger note recorded; any other is refused and named, and the plan deletes nothing (`kgme/clean_kept.py`) |

**Outputs.** The plan on stdout, one line per path with its size. Exit 0 when done, 1 when the plan was refused or a deletion failed or an entry changed under it, 2 on an unknown target.

**Side effects.** Under `--yes`: every planned file is hashed, every summary built and measured as the ledger will see it, and the plan written as a payload under `logs/scratch/payloads/` (every path numbered, with its size, device, inode, modification time, and sha256 prefix), created new and never through a link; one ledger `intent` names the payload; then files are unlinked first and empty directories removed bottom-up, by pathname. Immediately before each deletion one final check asks what the plan asked: the path resolves where the plan resolved it, it is not a link, it is the device and inode the plan listed, and a file has the size and modification time the plan listed; any difference refuses it. No descriptor chain, no rename to a private name, no restore (Michou's override of 2026-10-13). Accepted residual risk: a process that writes through a descriptor it already holds, or swaps the entry, between the final check and the unlink is not defended against; the outcome's hash is the one taken before the intent. One `outcome` per path (`deleted #n <size> B sha256 <prefix> <path>`, `removed #n <dir>/`, `refused #n: <why>: <path>`, `error #n: could not delete: <why>: <path>`; a path too long for the summary is shortened from the left, its number pointing into the payload) and one `closed:` outcome last. The first failure or changed entry stops the run. A refused plan, under `--yes` or not, writes the `intent`, one `refused` outcome of class `blocking` per refusal, and the close; a dry run of a clean plan appends one `note`. The payload is written whole, every byte and an fsync, or removed and the run refused. On start, a plan left without its `closed:` outcome is reconciled against its payload, path by path, and closed as `transient`.

**Refusals (the plan deletes nothing if it holds one).** A symlink, in the target's root, in any component above it, or under it; one that appears later, in any component, stops the run at that entry. A directory or entry the listing could not read or stat. An entry that is not what the plan saw at its final check: another inode, another kind, a link in its path, or a file whose size or modification time changed since the plan. A payload whose directory sits below a link, or that cannot be written whole, or a summary that cannot fit the ledger (every outcome is fitted after redaction, the path shortened first, the text last). Any path with a `.git` part. Anything under `logs/ledger/`. Anything whose resolved path leaves the repository or the target's roots. Anything the manifest refuses: the guard's blocklist (`.env` files among them) and the Tier 1 roots, whatever the target says.

**Manifest.** `manifest.toml` beside this file (HANDOFF-0032), checked by `kgme/policy.py` for every entry before the plan is made.
