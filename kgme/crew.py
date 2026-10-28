"""`kgme crew`, the logic: the plan, its gate, readiness, the merge gate, the order (HANDOFF-0048).

Purpose: everything the crew decides from values alone (ADR-015). A plan is markdown the
planner writes to `logs/scratch/crew/<run>/plan.md`: one `## Task: <name>` section per task,
with `outputs:`, `acceptance:`, `harness:`, `model:` and `after:` lines and a description.
`parse_plan` reads it; `check_plan` is the mechanical gate (§3): a task without `Outputs` or
an acceptance check, two tasks whose `Outputs` overlap with no edge between them, a cycle, an
`Outputs` path that is human or blocklisted, or more independent tasks than the cap
(`[crew] max_width`; `[crew] parallel` is the dispatch width, which serialises any plan, so
the amended acceptance test's two independent tasks pass at width 1); `ready_tasks` names
what may start; `merge_gate` is the gate before a task branch merges (§5): changed paths a
subset of its `Outputs`, no human path, blocklisted path, symlink or binary, no secret the
scanner finds, no zero-width or bidirectional control character, a dependency change with
its toolbox row, and the checks green; `integration_order` is the plan order. The effects
(`run_crew` and what it calls) are in `kgme.crew_io`.
Inputs: plan text, tasks, the lists `kgme.toml` names, changed paths and their bytes.
Outputs: tasks, refusals (one line each), orders.
Side effects: none.
"""

import dataclasses
import hashlib
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from kgme import cheap, loop_outputs
from kgme.hooks import guard

TASK_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
HANDOFF_ID = re.compile(r"^HANDOFF-[0-9A-Za-z-]{1,40}$")
HARNESSES = ("claude", "codex")
TRUNK = "main"
INTEGRATION = "integration"
PARALLEL_DEFAULT = 1
MAX_WIDTH_DEFAULT = 3
PLAN_CYCLES_DEFAULT = 6


@dataclass(frozen=True)
class Task:
    """One task of a plan: what it may write, how it is checked, who builds it."""

    handoff: str
    name: str
    outputs: tuple[str, ...]
    acceptance: str
    harness: str = "claude"
    model: str = ""
    level: str = "loose"
    description: str = ""
    after: tuple[str, ...] = ()


def read_crew(settings: dict) -> dict:
    """Pure: `kgme.toml [crew]` with its defaults filled in (amendment 4: width 1)."""
    crew = dict(settings.get("crew", {}))
    crew.setdefault("root", cheap.WORK_DIR)
    crew.setdefault("parallel", PARALLEL_DEFAULT)
    # the plan gate's cap on independent tasks: `[crew] parallel` is how many run at once and
    # serialises any plan, so the gate's cap is its own key (the amended acceptance test has
    # two independent tasks at width 1); it is never below `parallel`
    crew.setdefault("max_width", max(MAX_WIDTH_DEFAULT, int(crew["parallel"])))
    crew.setdefault("max_plan_cycles", PLAN_CYCLES_DEFAULT)
    crew.setdefault("harness", "claude")
    crew.setdefault("model", settings.get("models", {}).get("builder", ""))
    return crew


def workspace_name(handoff: str, task: str) -> str:
    """Pure: the folder a task's worktree takes, under the root: `handoff-nnnn-<task>`."""
    if not HANDOFF_ID.match(handoff):
        raise ValueError(f"not a handoff id: {handoff!r}")
    if not TASK_NAME.match(task) or task == INTEGRATION:
        raise ValueError(f"not a task name (a-z, 0-9, -, not {INTEGRATION}): {task!r}")
    return f"{handoff.lower()}-{task}"


def branch_name(handoff: str, task: str) -> str:
    """Pure: the task branch."""
    return f"crew/{handoff}/{task}"


def integration_branch(handoff: str) -> str:
    """Pure: the handoff's integration branch, `crew/<handoff>/integration`: git refuses a
    ref that is both a name and a folder, so the proposal's `crew/<handoff>` cannot sit
    beside its tasks' `crew/<handoff>/<task>` (measured 2026-10-27: "cannot lock ref")."""
    return f"crew/{handoff}/integration"


def quarantine_branch(run: str, task: str) -> str:
    """Pure: where a quarantined task's branch goes."""
    return f"quarantine/{run}/{task}"


def unit(handoff: str, task: str) -> str:
    """Pure: the review unit of a task, the id its review events carry (`review:<unit>`)."""
    return f"{handoff}:{task}"


def split_unit(name: str) -> tuple[str, str | None]:
    """Pure: a unit back into (handoff, task); a plain handoff id has no task."""
    handoff, _, task = name.partition(":")
    return handoff, task or None


def outputs_text(task: Task) -> str:
    """Pure: the task's Outputs as the `## Outputs` section `kgme.loop_outputs` parses, so the
    guard and the sandbox fence a task as they fence a handoff."""
    return "## Outputs\n" + ", ".join(f"`{p}`" for p in task.outputs) + "\n"


TASK_HEAD = re.compile(r"^## Task:\s*(?P<name>\S+)\s*$", re.M)
FIELD = re.compile(r"^(?P<key>outputs|acceptance|harness|model|after):\s*(?P<value>.*)$")
TICKED = re.compile(r"`([^`\s]+)`")
# zero-width and bidirectional control characters (§5): none may enter a merged text
HIDDEN = {
    0x200B: "zero width space", 0x200C: "zero width non-joiner", 0x200D: "zero width joiner",
    0x2060: "word joiner", 0xFEFF: "zero width no-break space", 0x202A: "LRE", 0x202B: "RLE",
    0x202C: "PDF", 0x202D: "LRO", 0x202E: "RLO", 0x2066: "LRI", 0x2067: "RLI", 0x2068: "FSI",
    0x2069: "PDI",
}  # fmt: skip
# the built-in scanner, used when `kgme.toml [crew] scanner` names no pinned tool: shapes
# of keys and tokens, never their values in a refusal
SECRET_RULES = (
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b")),
    ("assigned secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd)\s*[=:]\s*['\"][^'\"\s]{16,}['\"]"
    )),
)  # fmt: skip
DEPENDENCY_FILES = ("pyproject.toml", "uv.lock")
TOOLBOX = "docs/toolbox.md"


def parse_plan(text: str) -> list[Task]:
    """Pure: the tasks a plan names, in plan order. The handoff comes from the first line
    `# Plan: HANDOFF-NNNN`; a task's `outputs` are backticked paths, `after` a comma list."""
    head = re.search(r"^# Plan:\s*(?P<handoff>HANDOFF-[0-9A-Za-z-]+)", text, re.M)
    handoff = head["handoff"] if head else ""
    heads = list(TASK_HEAD.finditer(text))
    tasks: list[Task] = []
    for index, match in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
        body = text[match.end() : end]
        fields: dict[str, str] = {}
        description: list[str] = []
        for line in body.splitlines():
            field = FIELD.match(line.strip())
            if field and field["key"] not in fields:
                fields[field["key"]] = field["value"].strip()
            elif line.strip():
                description.append(line.rstrip())
        # the same rule as a handoff's Outputs (`kgme.loop_outputs.parse_outputs`): relative,
        # inside the repository, shaped like a path; anything else is left out (cycle 1 F4)
        outputs = tuple(
            loop_outputs.parse_outputs("## Outputs\n" + fields.get("outputs", "") + "\n")
        )
        acceptance = fields.get("acceptance", "").strip("` ")
        after = tuple(a.strip() for a in fields.get("after", "").split(",") if a.strip())
        tasks.append(
            Task(handoff, match["name"], outputs, acceptance, fields.get("harness", ""),
                 fields.get("model", ""), "loose", "\n".join(description).strip(), after)
        )  # fmt: skip
    return tasks


def resolve_task(task: Task, crew: dict, builder: str = "", codex_default: str = "") -> Task:
    """Pure: the task with its harness and model settled together (review cycles 2 and 3,
    F18): a blank harness is `[crew] harness`; a model that does not run under the harness
    is dropped; a blank model is `[crew] model` when that runs under the harness, else the
    harness's own default (`builder`, `[models] builder`, for Claude; `codex_default`,
    `[models] reviewer`, for Codex); what still does not fit stays blank, and `check_plan`
    refuses it. A Codex task reassigned to Claude takes a Claude model, never its Codex one."""
    harness = task.harness or str(crew.get("harness") or "claude")
    model = task.model if fits_harness(task.model, harness) else ""
    crew_model = str(crew.get("model") or "")
    if not model:
        fallback = builder if harness == "claude" else codex_default
        model = crew_model if fits_harness(crew_model, harness) else fallback
    if not fits_harness(model, harness):
        model = ""
    return dataclasses.replace(task, harness=harness, model=model)


def fits_harness(model: str, harness: str) -> bool:
    """Pure: a `claude-` model runs under Claude Code, any other named model under Codex."""
    return bool(model) and (model.startswith("claude-") == (harness == "claude"))


def plan_sha(text: str) -> str:
    """Pure: a plan's identity, the hash of its text with blank lines and spacing normalised."""
    normal = "\n".join(" ".join(ln.split()) for ln in text.splitlines() if ln.strip())
    return hashlib.sha256(normal.encode("utf-8")).hexdigest()[:16]


def _overlap(a: tuple[str, ...], b: tuple[str, ...]) -> str | None:
    for x in a:
        for y in b:
            px, py = PurePosixPath(x.rstrip("/")), PurePosixPath(y.rstrip("/"))
            if px == py or px in py.parents or py in px.parents:
                return f"{x} and {y}"
    return None


def _reaches(edges: dict[str, tuple[str, ...]], start: str, goal: str) -> bool:
    seen, stack = set(), [start]
    while stack:
        here = stack.pop()
        if here == goal:
            return True
        if here in seen:
            continue
        seen.add(here)
        stack.extend(edges.get(here, ()))
    return False


def depths(tasks: list[Task]) -> dict[str, int] | None:
    """Pure: each task's depth (the longest chain of edges before it), or None on a cycle."""
    edges = {t.name: t.after for t in tasks}
    found: dict[str, int] = {}
    visiting: set[str] = set()

    def depth(name: str) -> int | None:
        if name in found:
            return found[name]
        if name in visiting:
            return None
        visiting.add(name)
        best = 0
        for before in edges.get(name, ()):
            if before not in edges:
                continue
            got = depth(before)
            if got is None:
                return None
            best = max(best, got + 1)
        visiting.discard(name)
        found[name] = best
        return best

    for task in tasks:
        if depth(task.name) is None:
            return None
    return found


def is_forbidden_path(
    path: str, human_paths: tuple[str, ...], name_patterns: list[str], tier1: tuple[str, ...]
) -> str | None:
    """Pure: why an `Outputs` path may not be built on: human (`[hooks] human_paths`), a
    blocklisted name, or Tier 1; None when it may."""
    rel = PurePosixPath(path.rstrip("/"))
    if guard.is_human_path(PurePosixPath("/r") / rel, PurePosixPath("/r"), human_paths):
        return f"{path} is a human path"
    if any(guard._name_matches(part, pattern) for part in rel.parts for pattern in name_patterns):
        return f"{path} is blocklisted"
    for root in tier1:
        if rel == PurePosixPath(root) or PurePosixPath(root) in rel.parents:
            return f"{path} is Tier 1"
    return None


def check_plan(
    tasks: list[Task],
    parallel: int,
    human_paths: tuple[str, ...],
    name_patterns: list[str],
    tier1: tuple[str, ...] = (),
) -> list[str]:
    """Pure: the plan gate's refusals (§3), empty for a plan that may be reviewed."""
    refusals: list[str] = []
    if not tasks:
        return ["the plan names no task"]
    names = [t.name for t in tasks]
    for name in names:
        if not TASK_NAME.match(name):
            refusals.append(f"{name}: not a task name (a-z, 0-9, -)")
    if len(set(names)) != len(names):
        refusals.append("two tasks share a name")
    for task in tasks:
        if not task.outputs:
            refusals.append(f"{task.name}: no Outputs")
        if not task.acceptance:
            refusals.append(f"{task.name}: no acceptance check")
        if task.harness not in HARNESSES:
            refusals.append(f"{task.name}: harness {task.harness!r} is not one of {HARNESSES}")
        elif not task.model:
            refusals.append(f"{task.name}: no model runs under harness {task.harness}")
        elif not fits_harness(task.model, task.harness):
            refusals.append(f"{task.name}: model {task.model} does not run under {task.harness}")
        for before in task.after:
            if before not in names:
                refusals.append(f"{task.name}: after {before}, which the plan does not name")
        for path in task.outputs:
            why = is_forbidden_path(path, human_paths, name_patterns, tier1)
            if why:
                refusals.append(f"{task.name}: {why}")
    edges = {t.name: t.after for t in tasks}
    for index, a in enumerate(tasks):
        for b in tasks[index + 1 :]:
            shared = _overlap(a.outputs, b.outputs)
            if shared and not (_reaches(edges, a.name, b.name) or _reaches(edges, b.name, a.name)):
                refusals.append(f"{a.name} and {b.name}: Outputs overlap ({shared}) with no edge")
    levels = depths(tasks)
    if levels is None:
        refusals.append("the edges form a cycle")
    else:
        widest = max(list(levels.values()).count(d) for d in set(levels.values()))
        if widest > parallel:
            refusals.append(f"width {widest} exceeds the cap {parallel}")
    return refusals


def ready_tasks(tasks: list[Task], done: set[str], stopped: set[str]) -> list[Task]:
    """Pure: the tasks that may start now, in plan order: not done, not stopped, every
    `after` done, and no stopped task anywhere before them (a halted task's dependents wait)."""
    edges = {t.name: t.after for t in tasks}
    ready = []
    for task in tasks:
        if task.name in done or task.name in stopped:
            continue
        if any(_reaches(edges, task.name, s) for s in stopped):
            continue
        if all(before in done for before in task.after):
            ready.append(task)
    return ready


def integration_order(tasks: list[Task]) -> list[str]:
    """Pure: the plan's order, each task after everything it is `after`."""
    order: list[str] = []
    remaining = list(tasks)
    while remaining:
        named = {x.name for x in tasks}
        step = [t for t in remaining if all(b in order for b in t.after if b in named)]
        if not step:
            break
        order.extend(t.name for t in step)
        remaining = [t for t in remaining if t.name not in order]
    return order


def hidden_characters(text: str) -> list[str]:
    """Pure: the zero-width and bidirectional controls in `text`, named once each."""
    return sorted({f"U+{ord(c):04X} ({HIDDEN[ord(c)]})" for c in text if ord(c) in HIDDEN})


def scan_secrets(text: str) -> list[str]:
    """Pure: the built-in scanner: the rules a text trips, by name, never by value."""
    return [name for name, rule in SECRET_RULES if rule.search(text)]


def is_binary(data: bytes) -> bool:
    """Pure: git's test, a NUL in the first 8000 bytes."""
    return b"\0" in data[:8000]


def merge_gate(
    changed: list[str],
    outputs: tuple[str, ...],
    human_paths: tuple[str, ...],
    name_patterns: list[str],
    contents: dict[str, bytes | None],
    symlinks: set[str],
    scanner_hits: list[str],
    check_ok: bool | None,
    acceptance_ok: bool | None,
    tier1: tuple[str, ...] = (),
) -> list[str]:
    """Pure: the merge gate's refusals (§5), empty when the task branch may merge. `contents`
    maps a changed path to its bytes on the branch (None for a deletion); a mechanical
    refusal quarantines the task. `check_ok` and `acceptance_ok` are None when not run."""
    refusals: list[str] = []
    if not changed:
        refusals.append("the branch changes nothing")
    from kgme import loop_outputs

    for path in changed:
        if not loop_outputs.is_inside(PurePosixPath(path), outputs):
            refusals.append(f"{path} is outside the task's Outputs")
        why = is_forbidden_path(path, human_paths, name_patterns, tier1)
        if why:
            refusals.append(why)
        if path in symlinks:
            refusals.append(f"{path} is a symlink")
        data = contents.get(path)
        if data is None:
            continue
        if is_binary(data):
            refusals.append(f"{path} is binary")
            continue
        text = data.decode("utf-8", errors="replace")
        for found in hidden_characters(text):
            refusals.append(f"{path} carries {found}")
    if any(PurePosixPath(p).name in DEPENDENCY_FILES for p in changed) and TOOLBOX not in changed:
        refusals.append(f"a dependency file changed without its row in {TOOLBOX}")
    refusals.extend(f"the scanner found a {hit}" for hit in scanner_hits)
    if check_ok is False:
        refusals.append("make check is red on the merge result")
    if acceptance_ok is False:
        refusals.append("the task's acceptance check is red on the merge result")
    return refusals


def screen(handoff: str, state: dict) -> str:
    """Pure: the one approval screen (§6): plan cycles, tasks by harness and model, cycles
    and strikes, quarantines, audits, the gate, the diff by path."""
    lines = [f"kgme crew {handoff}: {state.get('status', '?')}"]
    lines.append(
        f"  plan cycles: {state.get('plan_cycles', 0)}; integration {state.get('sha') or 'none'}"
    )
    for task in state.get("tasks", []):
        lines.append(
            f"  {task['name']}: {task['status']}; {task.get('harness', '?')}/"
            f"{task.get('model', '?')}; cycles {task.get('cycles', 0)}; strikes "
            f"{task.get('strikes', 0)}; audits {', '.join(task.get('audits', [])) or 'none'}; "
            f"reviewer {task.get('reviewer', '?')}"
        )
    for row in state.get("quarantined", []):
        lines.append(f"  quarantined {row['name']}: {row['reason']}")
    lines.append(f"  gate: {state.get('gate', 'not run')}")
    for path in state.get("diff", []):
        lines.append(f"    {path}")
    return "\n".join(lines)
