"""The clean job's entry point (HANDOFF-0033): the thin layer ADR-015 asks of every job.

Purpose: parse the arguments and hand the run to `kgme.clean_io.run_clean`, which plans
through the pure `kgme.clean`, writes the `intent`, deletes through `kgme.clean_fs`, and
writes the outcomes. `kgme clean` in the CLI runs the same function; this file exists so
the job folder is runnable on its own, as every job folder is. Never scheduled in Phase 1.
Inputs: `TARGET` (a name from `kgme.toml` `[clean.targets]`), `--yes` to delete, `--dry-run`
(the default, stated). No path: the run acts on this checkout.
Outputs: the exit code of the run: 0 done, 1 refused or failed, 2 usage.
Side effects: those of `run_clean`: under `--yes`, deletions and a payload under scratch;
ledger events either way.
"""

import argparse
import sys

from kgme import clean_io, config, paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobs/clean/run.py", description="kgme clean")
    parser.add_argument("target", help="a target name from kgme.toml [clean.targets]")
    parser.add_argument("--yes", action="store_true", help="delete what the plan lists")
    parser.add_argument("--dry-run", action="store_true", help="print the plan; the default")
    args = parser.parse_args(argv)
    if args.yes and args.dry_run:
        print("kgme clean: --yes and --dry-run contradict; pass one", file=sys.stderr)
        return 2
    return clean_io.run_clean(args.target, args.yes, paths.root(), config.read_config())


if __name__ == "__main__":
    sys.exit(main())
