"""The brief job's entry point (HANDOFF-0034): the thin layer ADR-015 asks of every job.

Purpose: parse the arguments and hand the run to `kgme.brief_io.run_brief`, which writes the
`intent`, calls the pure `kgme.brief`, and writes the `outcome`. `kgme brief` in the CLI
runs the same function; this file exists so the job folder is runnable on its own, as every
job folder is.
Inputs: `--date YYYY-MM-DD` (default today), `--dry-run`. No path: the run acts on this checkout.
Outputs: the exit code of the run.
Side effects: those of `run_brief`: one artefact under `memory/agent/brief/`, ledger events, a
payload under scratch. A dry run prints the brief and appends one `note`.
"""

import argparse
import sys
from datetime import datetime

from kgme import brief_io, config, paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobs/brief/run.py", description="kgme brief v1")
    parser.add_argument("--date", help="the day to brief, YYYY-MM-DD; default today")
    parser.add_argument("--dry-run", action="store_true", help="print the brief; write nothing")
    args = parser.parse_args(argv)
    date = args.date or datetime.now().astimezone().date().isoformat()
    return brief_io.run_brief(date, args.dry_run, paths.root(), config.read_config())


if __name__ == "__main__":
    sys.exit(main())
