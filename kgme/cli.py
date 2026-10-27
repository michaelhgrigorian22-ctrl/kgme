"""The `kgme` command line.

Purpose: one entry point, one subcommand per capability, each built by its own handoff.
Until a handoff lands, its subcommand says so and exits 2. `lint` (HANDOFF-0031) validates
every note under the configured roots against the schema and exits 1 on a blocking finding.
`ledger` (HANDOFF-0026) reads both streams or appends one human-authored event. `review`
(HANDOFF-0029) runs one cycle of the review loop, or records a ruling or an override. `sync`
(HANDOFF-0040) commits `logs/ledger/` by pathspec if it changed and pushes if ahead. `clean`
(HANDOFF-0033) deletes disposable output by named target, a dry run unless `--yes`. `brief`
(HANDOFF-0034) writes the day's brief from the vault, Loop 0, no model call. `capture`
(HANDOFF-0050) puts Michou's words in the vault, one new note or one appended line; `daily`
drafts the day's note from the ledger, once. `loop` (HANDOFF-0043) runs a queue of adopted
handoffs unattended, one fresh loose session each, in `kgme.loop`; `review arbitrate` sends one
finding to the arbiter pair.
Inputs: argv.
Outputs: exit code; one line per finding or event, a summary, or a review's escalation packet.
Side effects: `ledger note`, `review`, `review rule`, and `review override` append to the real
ledger; `review` also runs `make check` and `codex exec`, writes the scratch patch, a payload,
and an audit file under `docs/audit/`; `sync` runs `git commit` on the ledger and `git push`,
and appends its push events. `capture` writes one new note under `memory/notes/` or appends
one line, and `daily` creates at most one note under `memory/daily/`, each with its ledger
events. `lint`, `ledger read`, and `review --dry-run` only read.
"""

import argparse
import json
import sys
from pathlib import Path

from kgme.cli_parser import build_parser  # noqa: F401 - the parser lives beside, unchanged

NOT_BUILT: dict[str, str] = {}


def main(argv: list[str] | None = None) -> int:
    """Dispatch. Returns the exit code; `sys.exit` happens only at the console-script edge."""
    args = build_parser().parse_args(argv)
    if args.command == "lint":
        return run_lint(args)
    if args.command == "ledger":
        return run_ledger(args)
    if args.command == "review":
        return run_review(args)
    if args.command == "loop":
        return run_loop(args)
    if args.command == "sync":
        return run_sync(args)
    if args.command == "clean":
        return run_clean(args)
    if args.command == "brief":
        return run_brief(args)
    if args.command == "capture":
        return run_capture(args)
    if args.command == "daily":
        return run_daily(args)
    if args.command == "atlas":
        return run_atlas(args)
    if args.command == "session":
        return run_session(args)
    if args.command in ("merge", "approve"):
        return run_track(args)
    if args.command == "cockpit":
        return run_cockpit()
    print(f"kgme {args.command}: not built ({NOT_BUILT[args.command]})", file=sys.stderr)
    return 2


def run_cockpit() -> int:
    """`kgme cockpit` (HANDOFF-0037): serve the read-only timeline on the loopback host and
    port of `kgme.toml [cockpit]` until interrupted. The Dock icon does not start it."""
    from cockpit import server
    from kgme import config, ledger

    settings = config.read_config()
    try:
        return server.run_cockpit(settings, ledger.read_default_dirs(settings))
    except (ValueError, OSError) as error:
        print(f"kgme cockpit: {error}", file=sys.stderr)
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
    skip_dirs = tuple(section["skip_dirs"])
    skipped = 0
    try:
        tracks = lint.read_tracks(settings)
        if args.all:
            notes = vault.read_notes(roots, exempt, skip_dirs, base)
        else:
            notes, skipped = vault.read_commit_notes(roots, exempt, skip_dirs, base)
    except (FileNotFoundError, ValueError) as error:
        print(f"kgme lint: {error}", file=sys.stderr)
        return 2
    findings = lint.lint_files(notes, tracks)
    if not args.root and (base / "CLAUDE.md").is_file():
        from datetime import date

        from kgme import coherence  # the repository's own tree, not a fixture's (HANDOFF-0049)

        cls = coherence.finding_class(
            date.today(), settings.get("coherence", {}).get("blocking_from")
        )
        findings += coherence.check_tree(*vault.read_coherence_inputs(base), cls=cls)
        from kgme import toolbox_read  # every third-party thing has its row (ADR-020, 0044)

        findings += toolbox_read.read_findings(base)
    for finding in findings:
        if finding.cls != "cosmetic" or args.include_cosmetic:
            print(finding.line())
    tally = lint.counts(findings)
    untracked = f"; {skipped} untracked skipped; `--all` walks them" if skipped else ""
    print(
        f"kgme lint: {len(notes)} notes, {tally['blocking']} blocking, "
        f"{tally['advisory']} advisory, {tally['cosmetic']} cosmetic{untracked}"
    )
    return 1 if tally["blocking"] else 0


def run_review(args: argparse.Namespace) -> int:
    """One review cycle on the staged diff (HANDOFF-0029), or a ruling or override event. From a
    worktree it refuses before reading any diff (HANDOFF-0047 review cycle 3 F12)."""
    from pathlib import Path

    from kgme import config, ledger, paths, review, review_io, review_run

    refused = ledger.read_worktree_refusal(paths.root())
    if refused:
        print(f"kgme review: {refused}", file=sys.stderr)
        return 2

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
    if args.action == "arbitrate":
        template, refused = read_arbiters(settings)
        if refused:
            print(f"kgme review: {refused}", file=sys.stderr)
            return 2
        argument = review_io.read_text(Path(args.argument)) if args.argument else ""
        settled = review_run.run_arbiters(
            args.handoff, args.finding, argument, places, settings["models"]["arbiters"], template
        )
        if settled is None:
            print(f"kgme review: no settlement on {args.finding} (already ruled, or none ruled)")
            return 1
        print(f"{args.finding} settled {settled['class']}: {settled['reason']}")
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
    # the settled rulings this cycle knew before its gate, named in its intent (cycle 2 F8)
    seen = review.loop_state(review_io.read_handoff_events(args.handoff, places.dirs)).rulings
    if not args.skip_check and not args.dry_run:
        code, output = review_io.run_make_check(places.root)
        if code != 0:
            print(output[-1500:], file=sys.stderr)
            print("kgme review: make check failed; a red gate is not reviewed", file=sys.stderr)
            return review_run.write_gate(args.handoff, code, output, places, arbiter)
        review_run.write_gate(args.handoff, code, output, places, arbiter)
    model = args.reviewer or settings["models"]["reviewer"]
    dispositions = review_io.read_text(Path(args.dispositions)) if args.dispositions else ""
    return review_run.run_cycle(
        args.handoff, model, dispositions, patch, places, args.dry_run, arbiter=arbiter,
        rulings_seen=tuple(sorted(seen)),
    )  # fmt: skip


def read_arbiters(settings: dict) -> tuple[str | None, str | None]:
    """The arbiter brief and why the pair cannot run: `kgme.toml [models] arbiters` and
    `control/review/arbiter-prompt.md` are human paths Michou applies (HANDOFF-0043)."""
    from kgme import paths

    if len(settings.get("models", {}).get("arbiters", [])) < 2:
        return None, "kgme.toml [models] arbiters names no pair yet; Michou applies it"
    brief = paths.root() / "control" / "review" / "arbiter-prompt.md"
    if not brief.is_file():
        return None, "control/review/arbiter-prompt.md is missing; Michou applies it"
    return brief.read_text(encoding="utf-8"), None


def run_loop(args: argparse.Namespace) -> int:
    """`kgme loop --queue A,B [--workspace PATH] [--stall-minutes 15]` (HANDOFF-0043), in
    `kgme.loop`. The real streams; the arbiter pair only once Michou's diffs are applied."""
    from datetime import timedelta

    from kgme import config, loop, review_run

    settings = config.read_config()
    queue = [h.strip() for h in args.queue.split(",") if h.strip()]
    template, refused = read_arbiters(settings)
    if refused:
        print(f"kgme loop: {refused}; findings are not arbitrated until then", file=sys.stderr)
    return loop.run_loop(
        queue,
        Path(args.workspace or ".").resolve(),
        review_run.read_places(False),
        settings["models"].get("arbiters", []) if template else [],
        template,
        stall=timedelta(minutes=args.stall_minutes),
        model=settings["models"].get("builder", ""),
    )


def run_brief(args: argparse.Namespace) -> int:
    """`kgme brief [--date D] [--dry-run]` (HANDOFF-0034), in `kgme.brief_io`, on this
    repository's root; it takes no path, as `kgme clean` takes none (HANDOFF-0033 F9)."""
    from datetime import datetime

    from kgme import brief_io, config, paths

    date = args.date or datetime.now().astimezone().date().isoformat()
    return brief_io.run_brief(date, args.dry_run, paths.root(), config.read_config())


def run_capture(args: argparse.Namespace) -> int:
    """`kgme capture KIND "WORDS" [--due WHEN]` (HANDOFF-0050), in `kgme.capture_io`."""
    from kgme import capture_io, config, paths

    return capture_io.run_capture(
        args.kind, args.words, args.due, paths.root(), config.read_config(), None, args.dry_run
    )


def run_daily(args: argparse.Namespace) -> int:
    """`kgme daily [--date D]` (HANDOFF-0050), in `kgme.daily_io`, on this checkout."""
    from datetime import datetime

    from kgme import config, daily_io, paths

    date = args.date or datetime.now().astimezone().date().isoformat()
    return daily_io.run_daily(date, paths.root(), config.read_config(), None, args.dry_run)


def run_session(args: argparse.Namespace) -> int:
    """`kgme session <level> [--handoff ID] [-- extra]` (HANDOFF-0047), in `kgme.session`."""
    from kgme import config, paths, session

    extra = list(args.extra)
    return session.run_session(
        args.level, args.handoff, extra, paths.root(), config.read_config(), args.dry_run,
        model_key=args.model, red=args.red,
    )  # fmt: skip


def run_track(args: argparse.Namespace) -> int:
    """`kgme merge` and `kgme approve` (HANDOFF-0055), in `kgme.merge` and `kgme.approve`."""
    from kgme import approve, config, merge, paths

    settings = config.read_config()
    if args.command == "merge":
        from kgme import ledger

        base = Path(args.base).resolve() if args.base else paths.root()
        # the main checkout's kgme.toml governs a merge into main, never a branch's own lanes
        # or check (review cycle 3 F12)
        governing = ledger.read_main_checkout(base) / "kgme.toml"
        if governing.is_file():
            settings = config.read_config(governing)
        return merge.run_merge(base, settings, args.track, args.dry_run)
    if args.show:
        return approve.run_show(paths.root(), settings, args.show)
    if not (args.what and args.sha):
        print("kgme approve: --what and --sha, or --show WHAT", file=sys.stderr)
        return 2
    return approve.run_approve(paths.root(), settings, args.what, args.sha, args.note)


def run_atlas(args: argparse.Namespace) -> int:
    """`kgme atlas [--dry-run]` (HANDOFF-0051), in `kgme.atlas_read`, on this checkout; with
    `--slice` or `--around`, a slice of `--base` (HANDOFF-0056), read-only."""
    from kgme import atlas_read, config, paths

    if args.slice or args.around:
        here = Path.cwd().resolve()
        # without --base, the checkout around you (F10); with it, that tree as given (F1)
        base = Path(args.base).resolve() if args.base else atlas_read.read_tree_root(here)
        # without --base, a relative --around path is one from where you stand (F10)
        around = args.around if args.base else [str(here / a) for a in args.around]
        out = Path(args.out) if args.out else None
        return atlas_read.run_slice(
            base, config.read_config(), args.slice, around, args.budget, out, args.dry_run
        )
    return atlas_read.run_atlas(paths.root(), config.read_config(), args.dry_run)


def run_clean(args: argparse.Namespace) -> int:
    """`kgme clean TARGET [--yes]` (HANDOFF-0033): the run in `kgme.clean_io`, on this checkout."""
    from kgme import clean_io, config, paths

    settings = config.read_config()
    if not args.target:
        targets = ", ".join(sorted(settings["clean"]["targets"]))
        print(f"kgme clean: name a target: {targets}", file=sys.stderr)
        return 2
    if args.yes and args.dry_run:
        print("kgme clean: --yes and --dry-run contradict; pass one", file=sys.stderr)
        return 2
    return clean_io.run_clean(args.target, args.yes, paths.root(), settings)


def run_sync(args: argparse.Namespace) -> int:
    """`kgme sync [--base DIR]` (HANDOFF-0040): the run in `kgme.sync_io.run_sync`."""
    from pathlib import Path

    from kgme import config, paths, sync_io

    base = Path(args.base).resolve() if args.base else paths.root()
    if not (base / ".git").exists():
        print(f"kgme sync: {base} is not a git checkout", file=sys.stderr)
        return 2
    return sync_io.run_sync(base, config.read_config())


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
