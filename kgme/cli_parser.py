"""The `kgme` command line's parser (moved out of `kgme/cli.py` by HANDOFF-0060 §3, unchanged).

Purpose: declare every subcommand, so `kgme --help` is the map of Phase 1; `kgme.cli` parses
with it and dispatches.
Inputs: none.
Outputs: an `argparse.ArgumentParser`.
Side effects: none.
"""

import argparse

CLASSES = ("blocking", "transient", "cosmetic", "advisory")


def build_parser() -> argparse.ArgumentParser:
    """Declare every subcommand so `kgme --help` is the map of Phase 1."""
    parser = argparse.ArgumentParser(prog="kgme", description="Kuang Grade Mark Eleven.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    brief_parser = subcommands.add_parser(
        "brief", help="Loop 0: write the day's brief from the vault"
    )
    brief_parser.add_argument("--date", help="the day to brief, YYYY-MM-DD; default today")
    brief_parser.add_argument(
        "--dry-run", action="store_true", help="print the brief; write nothing"
    )
    capture_parser = subcommands.add_parser(
        "capture", help="put Michou's words in the vault: remind, task, friction, note, daily"
    )
    capture_parser.add_argument("kind", choices=("remind", "task", "friction", "note", "daily"))
    capture_parser.add_argument("words", help="his words, verbatim, one line")
    capture_parser.add_argument(
        "--due", help="remind and task: 'friday 9am', 'tomorrow', '2026-10-20 14:00'"
    )
    capture_parser.add_argument(
        "--dry-run", action="store_true", help="print what would be written; write nothing"
    )
    daily_parser = subcommands.add_parser(
        "daily", help="draft the day's note from the ledger, once; nothing if it exists"
    )
    daily_parser.add_argument("--date", help="the day to draft, YYYY-MM-DD; default today")
    daily_parser.add_argument(
        "--dry-run", action="store_true", help="print the draft; write nothing"
    )
    session_parser = subcommands.add_parser(
        "session", help="start claude at a named level: tight, work, loose (ADR-022)"
    )
    session_parser.add_argument("level", choices=("tight", "work", "loose"))
    session_parser.add_argument("--handoff", help="the handoff a loose run builds")
    session_parser.add_argument("--task", help="one task of a crew handoff, from its workspace")
    session_parser.add_argument("--model", help="a code-class [models] key: the cheap lane (0053)")
    session_parser.add_argument("--red", help="the cheap lane's red command, to make exit 0")
    session_parser.add_argument(
        "--dry-run", action="store_true", help="print the command and settings; start nothing"
    )
    # `*`, never REMAINDER: the launcher's own flags are read wherever they sit, and only what
    # follows `--` reaches `claude` (found by hand, 2026-10-21)
    session_parser.add_argument("extra", nargs="*", help="after --: extra claude arguments")
    atlas_parser = subcommands.add_parser(
        "atlas", help="regenerate atlas/, the Obsidian lens on how KGME's parts connect"
    )
    atlas_parser.add_argument(
        "--dry-run", action="store_true", help="count the nodes and notes; write nothing"
    )
    atlas_parser.add_argument("--slice", metavar="HANDOFF", help="a slice for a handoff (0056)")
    atlas_parser.add_argument(
        "--around", action="append", default=[], metavar="PATH", help="a slice around a path"
    )
    atlas_parser.add_argument("--base", help="the tree a slice describes (default: here)")
    atlas_parser.add_argument("--budget", type=int, help="the slice's budget in tokens")
    atlas_parser.add_argument("--out", help="write the slice here (default: stdout)")
    merge_parser = subcommands.add_parser(
        "merge", help="land a track's green, in-lane commits on main (HANDOFF-0055)"
    )
    merge_parser.add_argument("track", choices=("design",))
    merge_parser.add_argument(
        "--dry-run", action="store_true", help="run the trial; record and merge nothing"
    )
    merge_parser.add_argument("--base", help="the checkout that committed (the hook's)")
    approve_parser = subcommands.add_parser(
        "approve", help="Michou's approval of a thing at a commit on main (HANDOFF-0055)"
    )
    approve_parser.add_argument("--what", help="what is approved: canvas, or code (HANDOFF-0048)")
    approve_parser.add_argument("--sha", help="the approved commit: on main, or a crew/* head")
    approve_parser.add_argument("--note", default="", help="his words")
    approve_parser.add_argument("--show", metavar="WHAT", help="print the newest approval")
    clean_parser = subcommands.add_parser(
        "clean", help="delete disposable outputs by named target; a dry run unless --yes"
    )
    clean_parser.add_argument(
        "target", nargs="?", help="briefs, agent, scratch, trace, caches, venv, ledger-test"
    )
    clean_parser.add_argument("--yes", action="store_true", help="delete what the plan lists")
    clean_parser.add_argument(
        "--dry-run", action="store_true", help="the default: print the plan, delete nothing"
    )
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
    lint_parser.add_argument(
        "--all", action="store_true", help="walk the working tree, untracked files included"
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
    review_parser.add_argument(
        "--workspace", help="review a KGME workspace's staged diff (default: the cwd, if one)"
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
    arbitrate = review_actions.add_parser(
        "arbitrate", help="send one finding to the arbiter pair of [models] arbiters (0043)"
    )
    arbitrate.add_argument("--handoff", required=True)
    arbitrate.add_argument("--finding", required=True, help="the finding id, e.g. F2")
    arbitrate.add_argument("--argument", help="a file holding the builder's argument")
    loop_parser = subcommands.add_parser(
        "loop", help="run adopted handoffs to their close, unattended (HANDOFF-0043)"
    )
    loop_parser.add_argument(
        "--queue", required=True, help="HANDOFF-NNNN[,HANDOFF-MMMM...], in the order to run"
    )
    loop_parser.add_argument(
        "--workspace", help="the worktree the builder runs in (default: the current directory)"
    )
    loop_parser.add_argument(
        "--stall-minutes", type=float, default=15, help="ledger silence with no live call"
    )
    workspace_parser = subcommands.add_parser(
        "workspace", help="KGME-owned worktrees for crew tasks (HANDOFF-0048)"
    )
    workspace_actions = workspace_parser.add_subparsers(dest="action", required=True)
    create = workspace_actions.add_parser("create", help="a task's worktree on its branch")
    create.add_argument("--handoff", required=True)
    create.add_argument("--task", required=True, help="the task name (a-z, 0-9, -)")
    create.add_argument("--outputs", required=True, help="comma-separated Outputs paths")
    create.add_argument("--acceptance", default="", help="the task's acceptance command")
    create.add_argument("--harness", help="claude or codex (default: [crew] harness)")
    create.add_argument("--model", help="the builder's model (default: [crew] model)")
    workspace_actions.add_parser("list", help="the workspaces under [crew] root")
    quarantine = workspace_actions.add_parser("quarantine", help="kill, rename, move, read-only")
    quarantine.add_argument("name")
    quarantine.add_argument("--run", help="the crew run id")
    quarantine.add_argument("--reason", default="")
    release = workspace_actions.add_parser("release", help="Michou's: writable, moved back")
    release.add_argument("name")
    remove = workspace_actions.add_parser("remove", help="Michou's: the worktree removed")
    remove.add_argument("name")
    crew_parser = subcommands.add_parser(
        "crew", help="plan, build and integrate one handoff to awaiting approval (HANDOFF-0048)"
    )
    crew_parser.add_argument("--handoff", help="the adopted handoff to crew")
    crew_parser.add_argument(
        "--stall-minutes", type=float, default=15, help="ledger silence with no live call"
    )
    crew_actions = crew_parser.add_subparsers(dest="action", required=False)
    check_plan = crew_actions.add_parser("check-plan", help="the mechanical plan gate on a file")
    check_plan.add_argument("plan", help="the plan file")
    skills_parser = subcommands.add_parser(
        "skills", help="link the repository's skills where every harness reads them (0048)"
    )
    skills_actions = skills_parser.add_subparsers(dest="action", required=True)
    install = skills_actions.add_parser("install", help="Michou's: links, and copies on request")
    install.add_argument(
        "--copy", action="append", default=[], metavar="DIR",
        help="a folder that will not follow links; gets a hashed copy",
    )  # fmt: skip
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
    sync_parser = subcommands.add_parser(
        "sync", help="commit logs/ledger/ if it changed, then push if ahead; never force"
    )
    sync_parser.add_argument("--base", help="the checkout to sync (default: this one)")
    return parser
