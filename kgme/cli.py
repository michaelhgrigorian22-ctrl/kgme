"""The `kgme` command line.

Purpose: one entry point, one subcommand per capability, each built by its own handoff.
Until a handoff lands, its subcommand says so and exits 2, except `lint`, which is a no-op
that exits 0 so `make check` runs green before HANDOFF-0031 (HANDOFF-0025 step 5).
`ledger` (HANDOFF-0026) reads both streams or appends one human-authored event.
Inputs: argv.
Outputs: exit code; one line on stdout or stderr.
Side effects: `ledger note` appends one line to the real ledger; `ledger read` opens the
stream files read-only. Nothing else touches disk yet.
"""

import argparse
import json
import sys

NOT_BUILT = {
    "brief": "HANDOFF-0034",
    "clean": "HANDOFF-0033",
    "review": "HANDOFF-0029",
    "cockpit": "HANDOFF-0037",
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
    ledger_parser = subcommands.add_parser("ledger", help="read or append ledger events by hand")
    ledger_actions = ledger_parser.add_subparsers(dest="action", required=True)
    read_parser = ledger_actions.add_parser("read", help="print events, one JSON line each")
    read_parser.add_argument("--stream", choices=("both", "ledger", "trace"), default="both")
    read_parser.add_argument("--since", help="only events after this id")
    read_parser.add_argument("--run", help="only events of this run_id")
    note_parser = ledger_actions.add_parser("note", help="append a human note or approval")
    note_parser.add_argument("summary")
    note_parser.add_argument("--kind", choices=("note", "approval", "correction"), default="note")
    note_parser.add_argument("--ref", help="id this approval or correction points at")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch. Returns the exit code; `sys.exit` happens only at the console-script edge."""
    args = build_parser().parse_args(argv)
    if args.command == "lint":
        print("kgme lint: not built (HANDOFF-0031); no-op, exit 0")
        return 0
    if args.command == "ledger":
        return run_ledger(args)
    print(f"kgme {args.command}: not built ({NOT_BUILT[args.command]})", file=sys.stderr)
    return 2


def run_ledger(args: argparse.Namespace) -> int:
    """`kgme ledger read` prints; `kgme ledger note` appends one human event to the real ledger."""
    from kgme import events, ledger

    if args.action == "read":
        for event in ledger.read(since=args.since, run_id=args.run, stream=args.stream):
            print(json.dumps(event, ensure_ascii=False))
        return 0
    event = events.make_event(
        source="human", actor="michou", kind=args.kind, summary=args.summary, ref=args.ref
    )
    print(ledger.append(event))
    return 0


if __name__ == "__main__":
    sys.exit(main())
