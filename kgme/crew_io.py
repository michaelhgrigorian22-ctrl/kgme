"""`kgme crew`, the effects: the planner, the plan loop, dispatch, the merge gate, integration
(HANDOFF-0048 §3 to §6; the logic is in `kgme.crew`).

Purpose: `run_crew --handoff HANDOFF-NNNN` plans, builds and integrates one adopted handoff
with nobody watching, and stops at `awaiting approval`. The planner is a fresh read-only
`claude -p` run on the `kgme-planner` skill (amendment 11), replying with the plan, which
is written to `logs/scratch/crew/<run>/plan.md`; the plan gate (`kgme.crew.check_plan`)
sends a red plan back to the planner with its refusals and is not reviewed; a green plan is
one review cycle through `kgme.review_run.run_cycle` on the unit `<handoff>:plan` with the
plan reviewer's prompt (`control/review/plan-prompt.md`), by a reviewer of another vendor
than the planner, with the same arbitration, halts and dispositions as a diff; the loop
stops on `kgme.review.loop_state`'s measures, a plan seen before, or `[crew] max_plan_cycles`.
Dispatch runs `[crew] parallel` ready tasks (amendment 4: one) in plan order, each in its
own workspace (`kgme.workspace`), each through `kgme.loop.run_loop` on the unit
`<handoff>:<task>` with its adapter; a Codex task is built by `run_codex_task`, whose
review and commit the supervisor runs, since the vendor sandbox has no network. A closed
task goes to the merge gate (`run_merge_gate`: a trial clone merging the task branch on the
integration head, `make check` and the task's acceptance check there, the diff scanned and
`kgme.crew.merge_gate`) and, green, is integrated by fast-forwarding `crew/<handoff>/integration`; a
mechanical refusal, a halt or a stall quarantines the task and its dependents wait.
Integration runs the full gate and one review on the unit `<handoff>:integration` by a
vendor other than the majority of builders, then writes `awaiting approval` naming the
commit; `kgme approve --what code --sha <sha>` is Michou's.
Inputs: the handoff id, the main checkout, the parsed `kgme.toml`, the review places.
Outputs: exit code 0 at `awaiting approval`, 1 otherwise; the approval screen.
Side effects: ledger events (job `crew:<handoff>`); worktrees, branches, trial clones;
model runs; files under `logs/scratch/crew/<run>/`.
"""

import dataclasses
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path, PurePosixPath

from kgme import crew, events, ledger, loop, paths, review, review_io, review_run, workspace
from kgme.adapters import read_adapter
from kgme.sync_git import run_git
from kgme.workspace import Task, unit

PLAN_PROMPT = Path("control/review/plan-prompt.md")
PLANNER_SKILL = Path("skills/kgme-planner/SKILL.md")
PLANNER_TURNS = 40
PLANNER_TIMEOUT = 1800
CHECK_TIMEOUT = 1800
VENDOR_CLAUDE = "claude"
VENDOR_CODEX = "codex"


def vendor_of(model: str) -> str:
    """Pure: the vendor a model id runs under: `claude-` is Claude, anything else Codex
    (`kgme.review_io.reviewer_argv` dispatches the same way)."""
    return VENDOR_CLAUDE if model.startswith("claude-") else VENDOR_CODEX


def other_vendor_reviewer(builder_vendor: str, settings: dict) -> str:
    """Pure: a reviewer model of the other vendor than `builder_vendor`: the Codex reviewer
    for a Claude builder, the first Claude arbiter (a `claude -p` model) for a Codex one."""
    models = settings.get("models", {})
    if builder_vendor == VENDOR_CODEX:
        named = [m for m in models.get("arbiters", []) if vendor_of(m) == VENDOR_CLAUDE]
        return named[0] if named else str(models.get("builder", ""))
    return str(models.get("reviewer", ""))


def planner_request(
    handoff: str,
    handoff_path: str,
    prior: str,
    refusals: list[str],
    findings: str,
    cycle: int,
    rulings: str = "",
) -> str:
    """Pure: what the planner is asked, cycle by cycle: the handoff; on a red gate its
    refusals and the previous plan; on a review its findings table, the arbiters' settled
    rulings with their recommended options (cycle 1 F5), and the previous plan."""
    text = (
        f"Plan {handoff} ({handoff_path}) for the crew, cycle {cycle}. Reply with the plan "
        "alone, in the format the kgme-planner skill gives: a `# Plan: <handoff>` line, then "
        "one `## Task: <name>` section per task with `outputs:` (backticked paths), "
        "`acceptance:` (one command, red before and green after), `harness:`, `model:`, "
        "`after:` and a description.\n"
    )
    if refusals:
        text += "\nThe plan gate refused the previous plan:\n" + "\n".join(
            f"- {r}" for r in refusals
        )
    if findings:
        text += (
            "\nThe reviewer's findings on the previous plan; revise it and end your reply with a "
            "`## Dispositions` section, one line per finding, fixed or disputed and why:\n"
            + findings
        )
    if rulings:
        text += (
            "\nThe arbiter pair's settled rulings on those findings, to execute (a downgraded "
            "finding needs no change; a recommended option is the change to make):\n" + rulings
        )
    if prior:
        text += "\n\nThe previous plan:\n" + prior
    return text + "\n"


def split_reply(reply: str) -> tuple[str, str]:
    """Pure: a planner's reply into the plan and its `## Dispositions` section."""
    head, sep, tail = reply.partition("\n## Dispositions")
    return head.strip() + "\n", (sep + tail).strip() if sep else ""


def resolve_tasks(tasks: list[Task], settings: dict) -> list[Task]:
    """Pure: every task's harness and model settled together, the one way for the plan gate,
    dispatch and `kgme crew check-plan` (review cycle 3 F18): `[crew]` defaults, `[models]
    builder` for Claude, `[models] reviewer` for Codex."""
    crew_settings = workspace.read_crew(settings)
    models = settings.get("models", {})
    return [
        crew.resolve_task(
            t, crew_settings, str(models.get("builder", "")), str(models.get("reviewer", ""))
        )
        for t in tasks
    ]


def read_plan_prompt(main: Path) -> str | None:
    """Effect: the plan reviewer's prompt, a human path Michou applies; None when absent."""
    path = main / PLAN_PROMPT
    return path.read_text(encoding="utf-8") if path.is_file() else None


def planner_argv(model: str, main: Path) -> list[str]:
    """Pure: the planner's read-only `claude -p` run; the skill carried when it is applied."""
    argv = [
        "claude",
        "-p",
        "--model",
        model,
        "--permission-mode",
        "dontAsk",
        "--max-turns",
        str(PLANNER_TURNS),
        "--tools",
        "Read,Grep,Glob",
    ]
    if (main / PLANNER_SKILL).is_file():
        argv += ["--append-system-prompt-file", str(main / PLANNER_SKILL)]
    return argv


def run_planner(model: str, main: Path, request: str, out: Path) -> str:
    """Effect: one fresh planner run in the main checkout, read-only; its reply, kept in
    `out`; empty on a failure."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "KGME_LOOP"))}
    try:
        done = subprocess.run(
            planner_argv(model, main),
            input=request,
            capture_output=True,
            text=True,
            cwd=main,
            env=env,
            timeout=PLANNER_TIMEOUT,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    review_io.write_text(out, done.stdout)
    return done.stdout if done.returncode == 0 else ""


def _event(handoff: str, run: str, kind: str, key: str, parent: str | None, summary: str, **more):
    return events.make_event(
        source="kgme",
        actor="kgme.crew",
        kind=kind,
        job=f"crew:{handoff}",
        key=key,
        run_id=run,
        parent=parent,
        summary=events.clip(summary),
        **more,
    )


def run_plan_loop(
    handoff: str,
    main: Path,
    settings: dict,
    places: review_io.Places,
    run: str,
    parent: str | None,
    planner: Callable[[str, int], str],
    reviewer: str,
    arbiters: list[str],
    template: str | None,
    folder: Path,
    arbitrate: Callable | None = None,
) -> tuple[list[Task] | None, dict]:
    """Effect: the plan iterated to a PASS (§3) or stopped; the tasks and the telemetry.
    `arbitrate` is `kgme.review_run.run_arbiters` unless a test injects a stub."""
    arbitrate = arbitrate or review_run.run_arbiters
    crew_settings = workspace.read_crew(settings)
    human = tuple(settings["hooks"]["human_paths"])
    patterns = [p[3:] for p in settings["hooks"]["blocklist"] if p.startswith("**/")]
    tier1 = tuple(settings["paths"].get("tier1_paths", []))
    plan_unit = f"{handoff}:plan"
    plan_places = dataclasses.replace(places, prompt_path=main / PLAN_PROMPT)
    prior, refusals, findings, dispositions, rulings = "", [], "", "", ""
    seen: dict[str, int] = {}  # a plan's sha -> the settled rulings there were when it was reviewed
    telemetry: dict = {"plan_cycles": 0, "plan_refusals": 0, "stopped": ""}
    for cycle in range(1, int(crew_settings["max_plan_cycles"]) + 1):
        telemetry["plan_cycles"] = cycle
        reply = planner(
            planner_request(handoff, "", prior, refusals, findings, cycle, rulings), cycle
        )
        plan, dispositions = split_reply(reply)
        review_io.write_text(folder / f"plan-{cycle}.md", plan)
        tasks = crew.parse_plan(plan)
        tasks = resolve_tasks(tasks, settings)  # harness and model together (F18)
        refusals = crew.check_plan(tasks, int(crew_settings["max_width"]), human, patterns, tier1)
        sha = crew.plan_sha(plan)
        if refusals:
            telemetry["plan_refusals"] += 1
            ledger.append(
                _event(
                    handoff,
                    run,
                    "note",
                    f"plan:{cycle}",
                    parent,
                    f"crew {handoff} plan {cycle} refused by the gate: {'; '.join(refusals)}",
                    class_="blocking",
                ),
                places.dirs,
            )
            prior, findings = plan, ""
            continue
        settled = len(
            review.loop_state(review_io.read_handoff_events(plan_unit, places.dirs)).rulings
        )
        if sha in seen and seen[sha] >= settled:  # the same plan with no ruling since (F5)
            telemetry["stopped"] = f"plan {sha} was seen before"
            break
        seen[sha] = settled
        review_io.write_text(folder / "plan.md", plan)
        code = review_run.run_cycle(plan_unit, reviewer, dispositions, plan, plan_places, False)
        state = review.loop_state(review_io.read_handoff_events(plan_unit, places.dirs))
        if code == 0:
            ledger.append(
                _event(
                    handoff,
                    run,
                    "note",
                    f"plan:{cycle}",
                    parent,
                    f"crew {handoff} plan {cycle} PASS sha={sha}",
                ),
                places.dirs,
            )
            return tasks, telemetry
        if code == 3 or state.halt:
            telemetry["stopped"] = state.reason
            break
        for finding in state.to_arbiters:
            if arbiters and template:
                arbitrate(plan_unit, finding, dispositions, places, arbiters, template)
        findings = review_io.read_audit_table(places.audit_dir, state.last_audit or "")
        rulings = read_rulings_text(plan_unit, places)
        refusals, prior = [], plan
    telemetry["stopped"] = telemetry["stopped"] or "max_plan_cycles reached"
    ledger.append(
        _event(
            handoff,
            run,
            "note",
            "plan:stopped",
            parent,
            f"crew {handoff} plan stopped: {telemetry['stopped']}; nothing dispatched",
            class_="blocking",
        ),
        places.dirs,
    )
    return None, telemetry


def read_rulings_text(unit_name: str, places: review_io.Places) -> str:
    """Effect: the settled rulings of a unit, one line each, as the planner is given them:
    each `ruling:<id>=<class>` note whole (the class, the option, the reason) from its payload,
    never the clipped summary (cycle 4 F21; a builder's `loop.rulings_text` since F6)."""
    lines = [
        review_io.read_ruling_text(e, places.root)
        for e in review_io.read_handoff_events(unit_name, places.dirs)
        if e["kind"] == "note"
        and (e["key"] or "").startswith("ruling:")
        and "@" not in (e["key"] or "")
    ]
    return "\n".join(f"- {ln}" for ln in lines)


def read_changed(main: Path, base: str, head: str) -> list[str]:
    """Effect: the paths a branch changes against its base, renames off, NUL-delimited."""
    listed = run_git(["diff", "-z", "--no-renames", "--name-only", base, head], main)
    return [p for p in listed.stdout.split("\0") if p]


def read_blob(main: Path, sha: str, path: str) -> bytes | None:
    """Effect: `path` at `sha`, or None when it is not there (a deletion)."""
    done = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=main, capture_output=True)
    return done.stdout if done.returncode == 0 else None


def read_symlinks(main: Path, sha: str, changed: list[str]) -> set[str]:
    """Effect: which changed paths are symlinks at `sha` (mode 120000)."""
    if not changed:
        return set()
    listed = run_git(["ls-tree", "-z", sha, "--", *changed], main, check=False).stdout
    found = set()
    for entry in listed.split("\0"):
        if entry.startswith("120000 "):
            found.add(entry.split("\t", 1)[1])
    return found


def read_scanner_pin(main: Path, executable: str) -> str:
    """Effect: why a configured scanner may not run, or "": its first word must resolve on
    PATH to a file whose sha256 a `docs/toolbox.md` row of that name records (ADR-020; cycle
    1 F14), so the gate never runs a tool it has not pinned."""
    import hashlib
    import shutil as _shutil

    from kgme import toolbox_read

    registry = main / toolbox_read.REGISTRY
    if not registry.is_file():
        return f"no {toolbox_read.REGISTRY} to pin {executable} with"
    rows, _ = toolbox_read.parse_rows(registry.read_text(encoding="utf-8"))
    name = Path(executable).name
    matching = [r for r in rows if str(r.cells.get("name", "")).split()[:1] == [name]]
    if not matching:
        return f"{name} has no toolbox row"
    found = _shutil.which(executable)
    if not found:
        return f"{name} is not on PATH"
    digest = hashlib.sha256(Path(found).read_bytes()).hexdigest()
    pinned = {str(r.cells.get("sha256", "")).strip() for r in matching}
    if digest not in pinned:
        return f"{name} at {found} does not match its toolbox row's sha256"
    return ""


def run_scanner(
    settings: dict, diff_text: str, scratch: Path, main: Path | None = None
) -> list[str]:
    """Effect: `[crew] scanner` (a pinned tool, its argument list, the diff on stdin; a
    nonzero exit is one hit per non-empty stdout line, named by its first word) when Michou
    has set one and its toolbox row pins the executable on PATH (cycle 1 F14), else the
    built-in rules of `kgme.crew.scan_secrets`. An unpinned scanner is itself one hit."""
    command = workspace.read_crew(settings).get("scanner")
    if not command:
        return crew.scan_secrets(diff_text)
    argv = shlex.split(str(command))
    if not argv:
        return ["scanner: an empty command"]
    problem = read_scanner_pin(main or paths.root(), argv[0])
    if problem:
        return [f"scanner not pinned: {problem}"]
    try:
        done = subprocess.run(
            argv, input=diff_text, capture_output=True, text=True, cwd=scratch, timeout=300
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [f"scanner failure ({type(error).__name__})"]
    if done.returncode == 0:
        return []
    return [ln.split()[0] for ln in done.stdout.splitlines() if ln.strip()] or ["scanner hit"]


def run_task_trial(
    main: Path, task_sha: str, base_sha: str, acceptance: str | list[str], message: str
) -> tuple[bool | None, bool | None, str, str]:
    """Effect: the task branch merged on the integration head in a temporary shared clone,
    `make check` and the acceptance checks (one, or every integrated task's at integration,
    cycle 1 F11) run there; returns (check ok, acceptance ok, the merge commit's sha fetched
    into the repository, a line). A conflict is (None, None, "", the line); a check that
    cannot run (a missing command, a timeout) is red, never an exception (F13). The clone
    goes however it ends."""
    where = Path(tempfile.mkdtemp(prefix="kgme-crew-")) / "trial"
    try:
        run_git(["clone", "--quiet", "--shared", "--no-checkout", str(main), str(where)], main)
        run_git(["checkout", "--quiet", "--detach", base_sha], where)
        name = run_git(["config", "user.name"], main, check=False).stdout.strip() or "kgme"
        email = run_git(["config", "user.email"], main, check=False).stdout.strip()
        merged = run_git(
            [
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                f"user.name={name}",
                "-c",
                f"user.email={email or 'kgme@localhost'}",
                "merge",
                "--no-ff",
                "-m",
                message,
                task_sha,
            ],
            where,
            check=False,
        )
        if merged.returncode != 0:
            return None, None, "", f"the merge does not apply: {merged.stderr.strip()[:200]}"
        sha = run_git(["rev-parse", "HEAD"], where).stdout.strip()
        run_git(["config", "core.hooksPath", "control/git-hooks"], where)
        env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        check = subprocess.run(
            ["make", "check"],
            cwd=where,
            capture_output=True,
            text=True,
            env=env,
            timeout=CHECK_TIMEOUT,
        )
        accepted: bool | None = None
        commands = [acceptance] if isinstance(acceptance, str) else list(acceptance)
        for command in [c for c in commands if c]:
            try:
                ran = subprocess.run(
                    shlex.split(command),
                    cwd=where,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=CHECK_TIMEOUT,
                )
                green = ran.returncode == 0
            except (OSError, ValueError, subprocess.TimeoutExpired):
                green = False
            accepted = green if accepted is None else (accepted and green)
        run_git(["fetch", "--quiet", "--no-tags", str(where), f"HEAD:refs/crew/trial/{sha}"], main)
        line = f"trial {sha[:12]}: make check {'green' if check.returncode == 0 else 'red'}"
        return check.returncode == 0, accepted, sha, line
    finally:
        shutil.rmtree(where.parent, ignore_errors=True)


def run_merge_gate(
    main: Path, settings: dict, task: Task, record: dict, scratch: Path
) -> tuple[list[str], str, list[str]]:
    """Effect: the gate before a task branch merges (§5): the diff, its paths and contents,
    the scanner, the trial; returns (refusals, the merge commit sha when green, changed)."""
    base = workspace.read_integration_head(main, task.handoff)
    head = run_git(["rev-parse", f"refs/heads/{record['branch']}"], main).stdout.strip()
    changed = read_changed(main, base, head)
    # what the builder wrote in its workspace and never committed is judged too (cycle 2
    # F19): a stray tracked edit or an untracked file outside the task's Outputs refuses
    stray = read_stray_writes(Path(str(record.get("workspace", ""))), task.outputs)
    contents = {p: read_blob(main, head, p) for p in changed}
    links = read_symlinks(main, head, changed)
    diff_text = run_git(["diff", "--no-renames", base, head], main).stdout
    hits = run_scanner(settings, diff_text, scratch, main)
    ran = read_scanner_name(settings)
    human = tuple(settings["hooks"]["human_paths"])
    patterns = [p[3:] for p in settings["hooks"]["blocklist"] if p.startswith("**/")]
    tier1 = tuple(settings["paths"].get("tier1_paths", []))
    refusals = crew.merge_gate(
        changed, task.outputs, human, patterns, contents, links, hits, None, None, tier1
    )
    refusals += [f"an uncommitted write outside the Outputs in the workspace: {p}" for p in stray]
    if refusals:
        # the gate line names the scanner that ran (AUDIT-0157 F14, the arbiters' ruling)
        return [f"{r} (scanner: {ran})" if "scanner" in r else r for r in refusals], "", changed
    branch = workspace.integration_branch(task.handoff)
    message = f"crew: merge {task.name} into {branch} ({task.handoff})"
    check_ok, accepted, sha, line = run_task_trial(main, head, base, task.acceptance, message)
    refusals = crew.merge_gate(
        changed, task.outputs, human, patterns, contents, links, hits, check_ok, accepted, tier1
    )
    if check_ok is None:
        refusals.append(line)
    if not refusals:
        changed = [*changed, f"(scanner: {ran})"]  # named on the integrated note and the screen
    return refusals, sha if not refusals else "", changed


def read_scanner_name(settings: dict) -> str:
    """Pure: the scanner the gate runs, for the gate line (AUDIT-0157 F14, the ruling): the
    pinned tool `[crew] scanner` names, else the built-in rules."""
    scanner = str(workspace.read_crew(settings).get("scanner") or "")
    return f"pinned {shlex.split(scanner)[0]}" if scanner else "the built-in rules"


def read_stray_writes(workspace: Path, outputs: tuple[str, ...]) -> list[str]:
    """Effect: the paths a workspace holds changed or new (tracked and untracked, ignored
    ones left out) outside the task's Outputs, `tests/` and `logs/scratch/`; empty when the
    workspace is not there (review cycle 2 F19)."""
    from kgme import loop_outputs

    if not workspace.is_dir():
        return []
    listed = run_git(
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"], workspace, check=False
    ).stdout
    found = []
    for entry in listed.split("\0"):
        if len(entry) < 4:
            continue
        path = entry[3:].split(" -> ")[-1]
        if not loop_outputs.is_inside(PurePosixPath(path), outputs + loop_outputs.ALWAYS):
            found.append(path)
    return sorted(found)


def write_integration(main: Path, handoff: str, expected: str, sha: str) -> None:
    """Effect: `crew/<handoff>/integration` moved to the merge commit, only from the head the trial
    merged on (`update-ref` with the old value), so a parallel landing is refused."""
    branch = workspace.integration_branch(handoff)
    run_git(["update-ref", f"refs/heads/{branch}", sha, expected], main)
    run_git(["update-ref", "-d", f"refs/crew/trial/{sha}"], main, check=False)


def read_task_result(unit_name: str, intent_id: str, dirs: ledger.Dirs) -> dict:
    """Effect: how a task's loop run ended, from its closing `loop:` outcome after `intent_id`."""
    after = [e for e in review_io.read_handoff_events(unit_name, dirs) if e["id"] > intent_id]
    closing = [e for e in after if (e["key"] or "").startswith("loop:") and e["kind"] == "outcome"]
    audits = sorted(
        {m["audit"] for e in after if (m := review.AUDIT_TOKEN.search(e["summary"] or ""))}
    )
    cycles = review.loop_state(after).cycles
    if not closing:
        return {
            "status": "ended",
            "reason": "no closing outcome",
            "audits": audits,
            "cycles": cycles,
        }
    summary = closing[-1]["summary"]
    status = (
        "closed"
        if " closed:" in summary
        else "ready"
        if " ready:" in summary
        else ("halted" if " halted" in summary else "stalled" if "stalled" in summary else "ended")
    )
    return {
        "status": status,
        "reason": summary,
        "audits": audits,
        "cycles": cycles,
        "strikes": len(review.loop_state(after).survivors),
    }


def write_process(settings: dict, main: Path, name: str, proc) -> None:
    """Effect: the builder's process group into the workspace record while it runs, cleared
    when it ends, so `kgme workspace quarantine` kills what is live (cycle 1 F10)."""
    record = workspace.read_record(settings, main, name) or {}
    record["pgid"] = proc.pid if proc is not None else None
    workspace.write_record(settings, main, name, record)


def task_contract(task: Task) -> str:
    """Pure: the terms a task's review is judged by, for the reviewer's prompt (cycle 2 F20):
    its Outputs, its acceptance check and its description; the handoff's whole What is the
    integration review's measure."""
    return (
        f"This diff is task `{task.name}` of {task.handoff}, one task of its crew's plan, not "
        f"the whole handoff. Judge it against the task: Outputs {', '.join(task.outputs)}; "
        f"acceptance check `{task.acceptance}`, red before and green after; what it builds: "
        f"{task.description or '(see the plan)'}. The handoff's whole What and Acceptance test "
        "are the integration review's measure, not this one's."
    )


def run_codex_cycle(
    main: Path, settings: dict, places: review_io.Places, task: Task, ws: Path, reviewer: str
) -> tuple[str, str]:
    """Effect: the supervisor's turn once a Codex builder exited (cycle 1 F3 and F6): stage
    the task's Outputs, gate, review on the unit, and on PASS commit by pathspec; returns
    ("again", the findings for the next builder), ("done", "") or ("halted", why)."""
    name = unit(task.handoff, task.name)
    written = ws / "logs" / "scratch" / "dispositions.md"
    dispositions = review_io.read_text(written) if written.is_file() else ""
    run_git(["add", "--", *task.outputs], ws, check=False)
    patch = run_git(["diff", "--cached"], ws).stdout
    if not patch.strip():
        return "done", ""  # nothing staged: the loop closes it as ended, no PASS
    code, output = review_io.run_make_check(ws)
    gate = review_run.write_gate(name, code, output, places, "pair")
    if code != 0:
        if gate == 3:
            return "halted", "the gate halted: the failing count has not fallen"
        return "again", f"make check is red:\n{output[-1500:]}"
    ws_places = dataclasses.replace(places, workspace=ws)
    code = review_run.run_cycle(
        name, reviewer, dispositions, patch, ws_places, False, contract=task_contract(task)
    )
    state = review.loop_state(review_io.read_handoff_events(name, places.dirs))
    if code == 0:
        run_git(
            ["commit", "-q", "-m", f"crew: {task.name} ({task.handoff})", "--", *task.outputs], ws
        )
        return "done", ""
    if code == 3 or state.halt:
        return "halted", state.reason
    return "again", review_io.read_audit_table(places.audit_dir, state.last_audit or "")


def run_task_in_loop(
    main: Path,
    settings: dict,
    places: review_io.Places,
    task: Task,
    ws: Path,
    run: str,
    parent: str | None,
    arbiters: list[str],
    template: str | None,
    stall: timedelta,
    reviewer: str | None = None,
) -> dict:
    """Effect: one task through `kgme loop` on its unit, in its workspace, with its harness's
    adapter (amendment 6): the loop's intent under the crew's (F8), the builder's group in
    the workspace record (F10), a Codex task's review and commit the supervisor's (F6), by
    `reviewer` (default: the other vendor's)."""
    name = unit(task.handoff, task.name)
    adapter = read_adapter(task.harness)
    before = review_io.read_handoff_events(name, places.dirs)
    mark = before[-1]["id"] if before else ""
    model = task.model or str(workspace.read_crew(settings)["model"])
    record_name = workspace.workspace_name(task.handoff, task.name)
    codex = task.harness == "codex"
    reviewer = reviewer or (other_vendor_reviewer(VENDOR_CODEX, settings) if codex else "")
    loop.run_loop(
        [name],
        ws,
        places,
        arbiters,
        template,
        argv_for=(
            lambda _u, where: (
                adapter.argv(task, where, main) if codex else adapter.argv(task, where)
            )
        ),
        stall=stall,
        model=model,
        env=dict(os.environ),
        request_for=lambda _u, path, findings="": adapter.request(task, path, findings),
        parent=parent,
        adapter=adapter,
        on_process=lambda proc: write_process(settings, main, record_name, proc),
        after_exit=(lambda _run: run_codex_cycle(main, settings, places, task, ws, reviewer))
        if codex
        else None,
    )
    return read_task_result(name, mark, places.dirs)


def run_crew(
    handoff: str,
    main: Path,
    settings: dict,
    places: review_io.Places,
    arbiters: list[str],
    template: str | None,
    planner: Callable[[str, int], str] | None = None,
    run_task: Callable | None = None,
    merge_gate: Callable | None = None,
    stall: timedelta = timedelta(minutes=loop.STALL_MINUTES),
    arbitrate: Callable | None = None,
) -> int:
    """The command: plan, dispatch at width `[crew] parallel`, gate, integrate, stop at
    `awaiting approval` (§3 to §6)."""
    refused = loop.read_handoff_ready(places.handoff_dir, handoff)
    if refused:
        print(f"kgme crew: {refused}", file=sys.stderr)
        return 2
    plan_prompt = read_plan_prompt(main)
    if plan_prompt is None and planner is None:
        print(f"kgme crew: {PLAN_PROMPT} is missing; Michou applies it", file=sys.stderr)
        return 2
    crew_settings = workspace.read_crew(settings)
    run = events.new_ulid()
    folder = places.scratch / "crew" / run
    folder.mkdir(parents=True, exist_ok=True)
    intent = ledger.append(
        _event(
            handoff,
            run,
            "intent",
            f"crew:{handoff}:{run}",
            None,
            f"crew {handoff} run {run} width={crew_settings['parallel']}",
        ),
        places.dirs,
    )
    handoff_path = review_io.read_handoff_path(places.handoff_dir, handoff)
    shown = review_io.shown(handoff_path, places.root) if handoff_path else ""
    planner_model = str(crew_settings["model"])
    planner = planner or (
        lambda request, cycle: run_planner(
            planner_model,
            main,
            request.replace(f"({handoff})", f"({shown})", 1),
            folder / f"planner-{cycle}.txt",
        )
    )
    plan_reviewer = other_vendor_reviewer(vendor_of(planner_model), settings)
    tasks, state = run_plan_loop(
        handoff,
        main,
        settings,
        places,
        run,
        intent,
        planner,
        plan_reviewer,
        arbiters,
        template,
        folder,
        arbitrate=arbitrate,
    )
    state |= {"tasks": [], "quarantined": [], "status": "plan stopped", "diff": [], "sha": None}
    if tasks is None:
        print(crew.screen(handoff, state))
        ledger.append(
            _event(
                handoff,
                run,
                "outcome",
                f"crew:{handoff}:{run}",
                intent,
                f"crew {handoff} stopped at the plan: {state['stopped']}",
                status="error",
                class_="blocking",
                ref=intent,
            ),
            places.dirs,
        )
        return 1
    done, stopped = set(), set()
    builders = []
    run_task = run_task or run_task_in_loop
    merge_gate = merge_gate or run_merge_gate
    while True:
        ready = crew.ready_tasks(tasks, done, stopped)[: int(crew_settings["parallel"])]
        if not ready:
            break
        for task in ready:
            if task.harness == "codex" and not read_codex_ready(main, settings):
                task = resolve_tasks([dataclasses.replace(task, harness="claude")], settings)[0]
                ledger.append(
                    _event(
                        handoff,
                        run,
                        "note",
                        f"task:{task.name}:reassigned",
                        intent,
                        f"crew {handoff} task {task.name} built by claude: the codex "
                        "cells or the Claude reviewer route are not green",
                    ),
                    places.dirs,
                )
            ws, record = workspace.run_create(settings, main, task, run)
            ledger.append(
                _event(
                    handoff,
                    run,
                    "note",
                    f"task:{task.name}:start",
                    intent,
                    f"crew {handoff} task {task.name} started: {task.harness}/"
                    f"{task.model or crew_settings['model']} in {ws.name}",
                ),
                places.dirs,
            )
            result = run_task(
                main, settings, places, task, ws, run, intent, arbiters, template, stall
            )
            row = {
                "name": task.name,
                "status": result["status"],
                "harness": task.harness,
                "model": task.model or crew_settings["model"],
                "cycles": result.get("cycles", 0),
                "strikes": result.get("strikes", 0),
                "audits": result.get("audits", []),
                "reviewer": other_vendor_reviewer(task.harness, settings),
            }
            builders.append(task.harness)
            name = workspace.workspace_name(task.handoff, task.name)
            if result["status"] not in ("closed", "ready"):
                workspace.run_quarantine(
                    settings, main, name, run, result.get("reason", result["status"]), places.dirs
                )
                stopped.add(task.name)
                state["quarantined"].append({"name": task.name, "reason": result.get("reason", "")})
                row["status"] = f"{result['status']}, quarantined"
                state["tasks"].append(row)
                continue
            try:
                refusals, sha, changed = merge_gate(main, settings, task, record, folder)
            except (OSError, ValueError, subprocess.SubprocessError) as error:  # cycle 1 F13
                refusals, sha, changed = (
                    [f"the gate could not run: {type(error).__name__}: {error}"[:200]],
                    "",
                    [],
                )
            if refusals:
                workspace.run_quarantine(
                    settings, main, name, run, "; ".join(refusals), places.dirs
                )
                stopped.add(task.name)
                state["quarantined"].append({"name": task.name, "reason": "; ".join(refusals)})
                row["status"] = "refused at the merge gate, quarantined"
                state["tasks"].append(row)
                continue
            write_integration(
                main,
                handoff,
                record["base"] if not done else workspace.read_integration_head(main, handoff),
                sha,
            )
            done.add(task.name)
            row["status"] = f"integrated {sha[:12]}"
            state["tasks"].append(row)
            ledger.append(
                _event(
                    handoff,
                    run,
                    "note",
                    f"task:{task.name}:integrated",
                    intent,
                    f"crew {handoff} task {task.name} integrated at {sha[:12]}: "
                    f"{', '.join(changed)}",
                ),
                places.dirs,
            )
    if not done:
        state["status"] = "nothing integrated"
        print(crew.screen(handoff, state))
        ledger.append(
            _event(
                handoff,
                run,
                "outcome",
                f"crew:{handoff}:{run}",
                intent,
                f"crew {handoff}: nothing integrated",
                status="error",
                class_="blocking",
                ref=intent,
            ),
            places.dirs,
        )
        return 1
    head = workspace.read_integration_head(main, handoff)
    majority = max(set(builders), key=builders.count)
    integration_reviewer = other_vendor_reviewer(majority, settings)
    trunk = run_git(["rev-parse", workspace.TRUNK], main).stdout.strip()
    patch = run_git(["diff", "--no-renames", trunk, head], main).stdout
    state["diff"] = read_changed(main, trunk, head)
    checks = [t.acceptance for t in tasks if t.name in done]  # every oracle, again (F11)
    check_ok, accepted, _, line = run_task_trial(main, head, head, checks, "integration gate")
    check_ok = bool(check_ok) and accepted is not False
    state["gate"] = f"{line}; scanner: {read_scanner_name(settings)}"
    code = 1
    if check_ok:
        int_unit = f"{handoff}:integration"
        review_run.write_gate(int_unit, 0, "", places, "pair")
        code = run_integration_review(main, head, int_unit, integration_reviewer, patch, places)
    if code == 0:
        state["status"], state["sha"] = "awaiting approval", head
        ledger.append(
            _event(
                handoff,
                run,
                "outcome",
                f"crew:{handoff}:{run}",
                intent,
                f"crew {handoff} awaiting approval: commit {head[:12]} on "
                f"{workspace.integration_branch(handoff)}; `kgme approve --what code --sha "
                f"{head[:12]}`",
                status="ok",
                ref=intent,
            ),
            places.dirs,
        )
        print(crew.screen(handoff, state))
        return 0
    state["status"] = "integration not green"
    ledger.append(
        _event(
            handoff,
            run,
            "outcome",
            f"crew:{handoff}:{run}",
            intent,
            f"crew {handoff}: integration review or gate not green at {head[:12]}",
            status="error",
            class_="blocking",
            ref=intent,
        ),
        places.dirs,
    )
    print(crew.screen(handoff, state))
    return 1


def run_integration_review(
    main: Path, head: str, int_unit: str, reviewer: str, patch: str, places: review_io.Places
) -> int:
    """Effect: one review cycle of the integration diff with the reviewer reading the
    candidate tree itself, a throwaway worktree detached at `head` (cycle 1 F12); the ledger,
    the audit and the evidence stay the main checkout's."""
    where = Path(tempfile.mkdtemp(prefix="kgme-integration-")) / "candidate"
    run_git(["worktree", "add", "-q", "--detach", str(where), head], main, timeout=120)
    try:
        candidate = dataclasses.replace(places, workspace=where)
        return review_run.run_cycle(int_unit, reviewer, "", patch, candidate, False)
    finally:
        run_git(["worktree", "remove", "--force", str(where)], main, check=False, timeout=120)
        shutil.rmtree(where.parent, ignore_errors=True)


CODEX_READY = Path("logs/scratch-test/codex-adapter-ready.json")


def read_codex_ready(main: Path, settings: dict) -> bool:
    """Effect: whether the Codex adapter may build at `loose` (amendment 3): its conformance
    cells and the Claude reviewer route passed, recorded by `tests/policy` at
    `logs/scratch-test/codex-adapter-ready.json` with the adapter's and the reviewer's
    module hashes; stale or absent means Codex builds nothing and the report says so."""
    path = main / CODEX_READY
    if not path.is_file():
        return False
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return False
    from kgme.hooks.common import read_script_text  # the hashes the cells recorded

    for name, digest in (record.get("hashes") or {}).items():
        text = read_script_text(main / name)
        if text is None or review_io.sha256_text(text) != digest:
            return False
    return bool(record.get("cells_green")) and bool(record.get("reviewer_route_green"))


def run_crew_command(args, main: Path, settings: dict) -> int:
    """`kgme crew --handoff HANDOFF-NNNN [--stall-minutes N]` and `kgme crew check-plan FILE`."""
    if getattr(args, "action", None) == "check-plan":
        text = review_io.read_text(Path(args.plan))
        human = tuple(settings["hooks"]["human_paths"])
        patterns = [p[3:] for p in settings["hooks"]["blocklist"] if p.startswith("**/")]
        tier1 = tuple(settings["paths"].get("tier1_paths", []))
        refusals = crew.check_plan(
            resolve_tasks(crew.parse_plan(text), settings),  # as the crew does (cycle 3 F18)
            int(workspace.read_crew(settings)["max_width"]),
            human,
            patterns,
            tier1,
        )
        for line in refusals:
            print(line)
        print(f"kgme crew check-plan: {'refused' if refusals else 'green'}")
        return 1 if refusals else 0
    from kgme.cli import read_arbiters

    template, refused = read_arbiters(settings)
    if refused:
        print(f"kgme crew: {refused}; findings are not arbitrated until then", file=sys.stderr)
    places = review_run.read_places(False)
    return run_crew(
        args.handoff,
        main,
        settings,
        places,
        settings["models"].get("arbiters", []) if template else [],
        template,
        stall=timedelta(minutes=args.stall_minutes),
    )
