"""The `kgme` command line.

Purpose: one entry point, one subcommand per capability, each built by its own handoff.
Until a handoff lands, its subcommand says so and exits 2. `lint` (HANDOFF-0031) validates
every note under the configured roots against the schema and exits 1 on a blocking finding.
`ledger` (HANDOFF-0026) reads both streams or appends one human-authored event. `review`
(HANDOFF-0029) runs one cycle of the review loop, or records a ruling or an override.
Inputs: argv.
Outputs: exit code; one line per finding or event, a summary, or a review's escalation packet.
Side effects: `ledger note`, `review`, `review rule`, and `review override` append to the real
ledger; `review` also runs `make check` and `codex exec`, writes the scratch patch, a payload,
and an audit file under `docs/audit/`. `lint`, `ledger read`, and `review --dry-run` only read.
"""

import argparse
import json
import sys

CLASSES = ("blocking", "transient", "cosmetic", "advisory")
NOT_BUILT = {
    "brief": "HANDOFF-0034",
    "clean": "HANDOFF-0033",
    "cockpit": "HANDOFF-0037",
}


def build_parser() -> argparse.ArgumentParser:
    """Declare every subcommand so `kgme --help` is the map of Phase 1."""
    parser = argparse.ArgumentParser(prog="kgme", description="Kuang Grade Mark Eleven.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("brief", help="Loop 0: write today's brief from the vault")
    subcommands.add_parser("clean", help="delete disposable outputs by named target")
    lint_parser = subcommands.add_parser("lint", help="validate every note under memory/ and docs/")
    lint_parser.add_argument(
        "--root", action="append", help="lint this root instead of kgme.toml's"
    )
    lint_parser.add_argument(
        "--include-cosmetic", action="store_true", help="print cosmetic findings"
    )
    lint_parser.add_argument(
        "--base", help="directory the folder rules and exemptions are relative to (repo root)"
    )
    review_parser = subcommands.add_parser("review", help="run the review loop on the staged diff")
    review_parser.add_argument("--handoff", help="the handoff id under review, e.g. HANDOFF-0029")
    review_parser.add_argument("--reviewer", help="Codex model id; default from kgme.toml [models]")
    review_parser.add_argument("--arbiter", help="who rules on disputes; default from kgme.toml")
    review_parser.add_argument(
        "--dispositions", help="file: the builder's dispositions of prior findings"
    )
    review_parser.add_argument("--patch", help="review this patch file instead of the staged diff")
    review_parser.add_argument(
        "--skip-check", action="store_true", help="do not run make check first"
    )
    review_parser.add_argument(
        "--dry-run", action="store_true", help="print the prompt; write nothing"
    )
    review_parser.add_argument("--test-streams", action="store_true", help=argparse.SUPPRESS)
    review_actions = review_parser.add_subparsers(dest="action", required=False)
    rule = review_actions.add_parser("rule", help="record the arbiter's ruling on one finding")
    rule.add_argument("--handoff", required=True)
    rule.add_argument("--finding", required=True, help="the finding id, e.g. F2")
    rule.add_argument("--class", dest="cls", required=True, choices=CLASSES)
    rule.add_argument("--reason", required=True)
    rule.add_argument("--arbiter", help="who ruled; default from kgme.toml [models].arbiter")
    override = review_actions.add_parser("override", help="Michou's override of a halt")
    override.add_argument("--handoff", required=True)
    override.add_argument("--reason", required=True)
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
        return run_lint(args)
    if args.command == "ledger":
        return run_ledger(args)
    if args.command == "review":
        return run_review(args)
    print(f"kgme {args.command}: not built ({NOT_BUILT[args.command]})", file=sys.stderr)
    return 2


def run_lint(args: argparse.Namespace) -> int:
    """`kgme lint` (HANDOFF-0031): one line per finding, a summary, exit 1 on any blocking one."""
    from pathlib import Path

    from kgme import config, lint, paths, vault

    settings = config.read_config()
    section = settings["lint"]
    base = Path(args.base).resolve() if args.base else paths.root()
    roots = (
        [Path(r).resolve() for r in args.root]
        if args.root
        else [paths.resolve(r, base) for r in section["roots"]]
    )
    exempt = [paths.resolve(p, base) for p in section["exempt"]]
    try:
        notes = vault.read_notes(roots, exempt, tuple(section["skip_dirs"]), base)
    except FileNotFoundError as error:
        print(f"kgme lint: {error}", file=sys.stderr)
        return 2
    findings = lint.lint_files(notes)
    for finding in findings:
        if finding.cls != "cosmetic" or args.include_cosmetic:
            print(finding.line())
    tally = lint.counts(findings)
    print(
        f"kgme lint: {len(notes)} notes, {tally['blocking']} blocking, "
        f"{tally['advisory']} advisory, {tally['cosmetic']} cosmetic"
    )
    return 1 if tally["blocking"] else 0


def run_review(args: argparse.Namespace) -> int:
    """One review cycle on the staged diff (HANDOFF-0029), or a ruling or override event."""
    from pathlib import Path

    from kgme import config, review_io, review_run

    settings = config.read_config()
    places = review_run.read_places(args.test_streams)
    arbiter = args.arbiter or settings["models"]["arbiter"]
    if args.action == "rule":
        recorded = review_io.write_ruling(
            args.handoff, args.finding, args.cls, args.reason, arbiter, places
        )
        if recorded is None:
            print(
                f"kgme review: {args.finding} already has a ruling; one per finding",
                file=sys.stderr,
            )
            return 2
        print(recorded)
        return 0
    if args.action == "override":
        print(review_io.write_override(args.handoff, args.reason, places))
        return 0
    if not args.handoff:
        print("kgme review: --handoff is required", file=sys.stderr)
        return 2
    if args.patch:
        patch = review_io.read_text(Path(args.patch))
    else:
        patch = review_io.read_staged_patch(places.root)
    if not patch.strip():
        print("kgme review: nothing staged; stage the handoff's diff first", file=sys.stderr)
        return 2
    if not args.skip_check and not args.dry_run:
        code, output = review_io.run_make_check(places.root)
        if code != 0:
            print(output[-1500:], file=sys.stderr)
            print("kgme review: make check failed; a red gate is not reviewed", file=sys.stderr)
            return 2
    model = args.reviewer or settings["models"]["reviewer"]
    dispositions = review_io.read_text(Path(args.dispositions)) if args.dispositions else ""
    return review_run.run_cycle(
        args.handoff, model, dispositions, patch, places, args.dry_run, arbiter=arbiter
    )


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
