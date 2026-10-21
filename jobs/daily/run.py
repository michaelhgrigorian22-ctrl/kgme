"""The daily job's entry point (HANDOFF-0050): the thin layer ADR-015 asks of every job.

Purpose: parse the arguments and hand the run to `kgme.daily_io.run_daily`. `kgme daily` in
the CLI runs the same function; this file exists so the job folder is runnable on its own.
Inputs: `--date YYYY-MM-DD` (default today), `--dry-run`. No path: the run acts on this
checkout.
Outputs: the exit code of the run.
Side effects: those of `run_daily`: at most one new daily note, and ledger events.
"""

import argparse
import sys
from datetime import datetime

from kgme import config, daily_io, paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobs/daily/run.py", description="kgme daily")
    parser.add_argument("--date", help="the day to draft, YYYY-MM-DD; default today")
    parser.add_argument("--dry-run", action="store_true", help="print the draft; write nothing")
    args = parser.parse_args(argv)
    date = args.date or datetime.now().astimezone().date().isoformat()
    return daily_io.run_daily(date, paths.root(), config.read_config(), None, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
