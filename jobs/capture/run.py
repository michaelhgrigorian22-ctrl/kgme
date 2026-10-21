"""The capture job's entry point (HANDOFF-0050): the thin layer ADR-015 asks of every job.

Purpose: parse the arguments and hand the run to `kgme.capture_io.run_capture`. `kgme capture`
in the CLI runs the same function; this file exists so the job folder is runnable on its own.
Inputs: the kind (`remind`, `task`, `friction`, `note`, `daily`), the words, `--due WHEN`,
`--dry-run`.
Outputs: the exit code of the run.
Side effects: those of `run_capture`: one new note, or one appended line, and ledger events.
"""

import argparse
import sys

from kgme import capture, capture_io, config, paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobs/capture/run.py", description="kgme capture")
    parser.add_argument("kind", choices=capture.KINDS)
    parser.add_argument("words", help="Michou's words, verbatim")
    parser.add_argument("--due", help="when: 'friday 9am', 'tomorrow', '2026-10-20 14:00'")
    parser.add_argument("--dry-run", action="store_true", help="print it; write nothing")
    args = parser.parse_args(argv)
    return capture_io.run_capture(
        args.kind, args.words, args.due, paths.root(), config.read_config(), None, args.dry_run
    )


if __name__ == "__main__":
    sys.exit(main())
