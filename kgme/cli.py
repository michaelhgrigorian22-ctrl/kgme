"""The `kgme` command line.

Purpose: one entry point, one subcommand per capability, each built by its own handoff.
Until a handoff lands, its subcommand says so and exits 2, except `lint`, which is a no-op
that exits 0 so `make check` runs green before HANDOFF-0031 (HANDOFF-0025 step 5).
Inputs: argv.
Outputs: exit code; one line on stdout or stderr.
Side effects: none in this skeleton. Subcommands gain effects as their handoffs land.
"""

import argparse
import sys

NOT_BUILT = {
    "brief": "HANDOFF-0034",
    "clean": "HANDOFF-0033",
    "review": "HANDOFF-0029",
    "cockpit": "HANDOFF-0037",
    "ledger": "HANDOFF-0026",
}


def build_parser() -> argparse.ArgumentParser:
    """Declare every subcommand so `kgme --help` is the map of Phase 1."""
    parser = argparse.ArgumentParser(prog="kgme", description="Kuang Grade Mark Eleven.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("brief", help="Loop 0: write today's brief from the vault")
    subcommands.add_parser("clean", help="delete disposable outputs by named target")
    subcommands.add_parser("lint", help="validate every note under memory/ and docs/")
    subcommands.add_parser("review", help="run the review loop on the staged diff")
    subcommands.add_parser("cockpit", help="serve the read-only timeline on localhost")
    subcommands.add_parser("ledger", help="read or append ledger events by hand")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch. Returns the exit code; `sys.exit` happens only at the console-script edge."""
    args = build_parser().parse_args(argv)
    if args.command == "lint":
        print("kgme lint: not built (HANDOFF-0031); no-op, exit 0")
        return 0
    print(f"kgme {args.command}: not built ({NOT_BUILT[args.command]})", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
