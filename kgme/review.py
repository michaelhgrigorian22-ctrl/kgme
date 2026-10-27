"""`kgme review`, the state: what one handoff's loop has recorded, read back from the ledger.

Purpose: the ledger summaries a review cycle writes and their reconstruction into a
`LoopState` that decides the halt. The halt is ADR-023's measured non-convergence (HANDOFF-0043
amendment 16), replacing the three-cycle count: a ruling executed and the same root cause
blocking again, a reviewed diff hash seen before, or a failing-check count that has not fallen
in three consecutive gates; strike counts stay as telemetry. A finding that stood blocking two
consecutive cycles with no settled ruling goes to the arbiters (`to_arbiters`). Parsing lives
in `kgme.review_parse`, rendering in `kgme.review_text`.
Inputs: findings, identifiers, prior ledger events for one handoff; a gate's output.
Outputs: summary lines, state chunks, gate counts, a `LoopState`.
Side effects: none.
"""

import re
from dataclasses import dataclass

from kgme import events
from kgme.review_parse import Finding, counts, open_blocking

BLOCKING_INLINE = re.compile(r"blocking=(?P<ids>[F0-9,]+|-)")
BLOCKING_IN_LEDGER = re.compile(r"blocking=#(?P<count>\d+):ledger")
AUDIT_TOKEN = re.compile(r"audit=(?P<audit>AUDIT-\d{4})")
SHA_TOKEN = re.compile(r"\bsha=(?P<sha>[0-9a-f]{6,})")
RULED_TOKEN = re.compile(r"\bruled=(?P<ids>[F0-9,]+|-)")
FAILING_TOKEN = re.compile(r"\bfailing=(?P<count>\d+)")
STATE_CHUNK_CHARS = 150
CYCLES_TO_ARBITERS = 2  # the reader's two-cycle rule: the finding goes to the arbiters
GATES_WITHOUT_PROGRESS = 3  # amendment 16 (c)
# what a gate prints when it fails, counted: pytest's tally, lint's and the mods' blocking
GATE_COUNTS = (
    re.compile(r"(?P<n>\d+) failed\b"),
    re.compile(r"(?P<n>\d+) errors?\b"),
    re.compile(r"kgme lint: .*?(?P<n>\d+) blocking"),
    re.compile(r"kgme mods: .*?(?P<n>\d+) blocking"),
)


def summary_line(
    handoff: str, cycle: int, verdict_word: str, sha: str, findings: list[Finding], audit_id: str
) -> str:
    """The outcome summary `loop_state` reads back: ids inline while they fit the writer's cap,
    else a count and `ledger`, meaning the ids follow in `state_chunks` notes. Never clipped."""
    ids = open_blocking(findings)
    tally = counts(findings)
    head = f"review:{handoff} cycle {cycle} {verdict_word} sha={sha[:16]}"
    tail = (
        f"transient={tally['transient']} cosmetic={tally['cosmetic']} "
        f"advisory={tally['advisory']} audit={audit_id}"
    )
    inline = f"{head} blocking={','.join(ids) or '-'} {tail}"
    if len(inline) <= events.MAX_SUMMARY_CHARS:
        return inline
    return f"{head} blocking=#{len(ids)}:ledger {tail}"


def state_chunks(findings: list[Finding]) -> list[str]:
    """The open blocking ids in bounded pieces for `note` events, when they did not fit inline."""
    chunks: list[str] = []
    current = ""
    for finding_id in open_blocking(findings):
        candidate = f"{current},{finding_id}" if current else finding_id
        if len(candidate) > STATE_CHUNK_CHARS:
            chunks.append(current)
            current = finding_id
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def blocking_ids(summary: str, chunks: list[str] | None = None) -> set[str]:
    """The open blocking ids an outcome recorded, inline or reassembled from its state chunks.

    A deferred summary whose chunks are missing or do not add up to the recorded count is an
    incomplete reconstruction and raises, rather than returning a smaller set."""
    deferred = BLOCKING_IN_LEDGER.search(summary)
    if deferred:
        ids = {i for chunk in (chunks or []) for i in chunk.split(",") if i}
        if len(ids) != int(deferred["count"]):
            raise ValueError(
                f"state incomplete: {len(ids)} ids reassembled, {deferred['count']} recorded"
            )
        return ids
    match = BLOCKING_INLINE.search(summary)
    if not match or match["ids"] == "-":
        return set()
    return {i for i in match["ids"].split(",") if i}


def gate_failures(code: int, output: str) -> int:
    """Pure: how many checks a gate failed, from its exit code and output. A red gate whose
    output names no count is one failure, so a red gate is never zero."""
    if code == 0:
        return 0
    found = sum(int(m["n"]) for pattern in GATE_COUNTS for m in pattern.finditer(output))
    return max(found, 1)


def gate_summary(handoff: str, code: int, failing: int) -> str:
    """The `gate:` note's summary `loop_state` reads back."""
    return f"review:{handoff} gate {'green' if code == 0 else 'red'} failing={failing}"


@dataclass(frozen=True)
class LoopState:
    """Where one handoff's loop stands, read back from its ledger events.

    `cycles` counts every successful review of the handoff, for labels; `since_override`
    counts only those after the last override, for the halt bound."""

    cycles: int
    since_override: int
    open_ids: tuple[str, ...]
    survivors: tuple[str, ...]
    runs: dict[str, int]
    halt: bool
    reason: str
    active_halt: bool
    rulings: dict[str, str]
    last_audit: str | None
    to_arbiters: tuple[str, ...] = ()


def loop_state(handoff_events: list[dict]) -> LoopState:
    """Reconstruct the loop from events with `job: review:<handoff>`, in id order.

    Each successful `outcome` is one review cycle; its summary names the open blocking ids,
    inline or through `state:<outcome id>:<n>` notes, and the diff hash. An error outcome is a
    tooling failure and is not a cycle; an outcome keyed `loop:` is the loop's own close, not a
    cycle. A `note` keyed `ruling:<id>=<class>` is the settled ruling and holds until a contrary
    one; rulings survive overrides. A `note` keyed `ruling:<id>@<arbiter>=<class>` is one
    arbiter's ruling and settles nothing by itself. A `note` keyed `gate:` is one gate and its
    failing count. A `note` keyed `halt:` leaves the loop halted until an `approval` keyed
    `override:`, which clears the window the measures read and the halt but keeps `last_audit`,
    so the next cycle still sees the previous table.

    Halt (ADR-023, amendment 16), over the window since the last override: (a) a cycle after a
    settled ruling on a finding, started after that ruling, on a diff not reviewed before it,
    and whose intent names the ruling among those it knew before its gate, still has it
    blocking; (b) a diff
    hash reviewed twice with no
    settled ruling between the two reviews; (c) the
    last three gates red with a failing count that never fell. `to_arbiters`: the findings
    blocking in the last two consecutive cycles with no settled ruling.
    """
    ordered = sorted(handoff_events, key=lambda e: e["id"])
    chunks: dict[str, list[str]] = {}
    for event in ordered:
        key = event["key"] or ""
        if event["kind"] == "note" and key.startswith("state:"):
            _, owner, _ = key.split(":", 2)
            chunks.setdefault(owner, []).append(event["summary"].removeprefix("ids="))
    cycles: list[set[str]] = []
    rulings: dict[str, str] = {}
    ruled_at: dict[str, str] = {}  # finding -> the id of its settled ruling
    seen_before: dict[str, set[str]] = {}  # finding -> the diffs reviewed before its ruling
    every_sha: list[str] = []
    intent_ruled: dict[str, set[str]] = {}  # a cycle's intent -> the rulings it knew
    returned: list[str] = []
    shas: list[str] = []
    gates: list[int] = []
    active_halt = False
    last_audit: str | None = None
    total = 0
    for event in ordered:
        key = event["key"] or ""
        if event["kind"] == "intent" and (named := RULED_TOKEN.search(event["summary"] or "")):
            intent_ruled[event["id"]] = set(named["ids"].split(",")) - {"-"}
        if event["kind"] == "approval":
            cycles, shas, gates, ruled_at, returned, active_halt = [], [], [], {}, [], False
        elif event["kind"] == "note" and key.startswith("ruling:"):
            finding_id, _, cls = key[len("ruling:") :].partition("=")
            if "@" not in finding_id:
                rulings[finding_id] = cls
                ruled_at[finding_id] = event["id"]
                seen_before[finding_id] = set(every_sha)
                shas = []  # a settled ruling is progress: the same diff may be reviewed again
        elif event["kind"] == "note" and key.startswith("gate:"):
            failing = FAILING_TOKEN.search(event["summary"])
            gates.append(int(failing["count"]) if failing else 0)
        elif event["kind"] == "note" and key.startswith("halt:"):
            active_halt = True
        elif event["kind"] == "outcome" and event["status"] == "ok" and not key.startswith("loop:"):
            ids = blocking_ids(event["summary"], chunks.get(event["id"]))
            current = {i for i in ids if rulings.get(i, "blocking") == "blocking"}
            # executed means reviewed by a cycle started after the ruling (review cycle 1 F8):
            # the outcome's intent, or the outcome itself when it names none
            # and of a diff not reviewed before it: unchanged work is no execution (cycle 2 F8)
            started = event.get("ref") or event["id"]
            sha = SHA_TOKEN.search(event["summary"])
            reviewed = sha["sha"] if sha else ""
            knew = intent_ruled.get(event.get("ref") or "")  # None: an intent that names none
            returned += sorted(
                i for i in current
                if i in ruled_at and started > ruled_at[i] and reviewed not in seen_before[i]
                and (knew is None or i in knew)
            )  # fmt: skip
            cycles.append(current)
            shas.append(reviewed)
            every_sha.append(reviewed)
            total += 1
            audit = AUDIT_TOKEN.search(event["summary"])
            last_audit = audit["audit"] if audit else last_audit
    if not cycles:
        halt, reason = _gate_halt(gates)
        return LoopState(
            total, 0, (), (), {}, halt, reason or "no cycle recorded", active_halt, rulings,
            last_audit,
        )  # fmt: skip
    last = cycles[-1]
    survivors = sorted(last & cycles[-2]) if len(cycles) >= 2 else []
    runs: dict[str, int] = {}
    for finding_id in sorted(last):
        run = 0
        for cycle in reversed(cycles):
            if finding_id not in cycle:
                break
            run += 1
        runs[finding_id] = run
    seen = [sha for sha in shas if sha]
    repeated = sorted({sha for sha in seen if seen.count(sha) > 1})
    gate_halt, gate_reason = _gate_halt(gates)
    if returned:
        halt = True
        reason = f"{returned[0]} blocked again after its ruling was executed"
    elif repeated:
        halt, reason = True, f"diff {repeated[0]} was reviewed before in this window"
    elif gate_halt:
        halt, reason = True, gate_reason
    else:
        halt, reason = False, "converging"
    to_arbiters = tuple(
        i for i, run in runs.items() if run >= CYCLES_TO_ARBITERS and i not in rulings
    )
    return LoopState(
        total,
        len(cycles),
        tuple(sorted(last)),
        tuple(survivors),
        runs,
        halt,
        reason,
        active_halt,
        rulings,
        last_audit,
        to_arbiters,
    )


def _gate_halt(gates: list[int]) -> tuple[bool, str]:
    """Pure: measure (c), the last `GATES_WITHOUT_PROGRESS` gates red and never falling."""
    last = gates[-GATES_WITHOUT_PROGRESS:]
    if len(last) < GATES_WITHOUT_PROGRESS or 0 in last:
        return False, ""
    if all(later >= earlier for earlier, later in zip(last, last[1:], strict=False)):
        counts_text = ", ".join(str(n) for n in last)
        return True, f"the failing-check count has not fallen in {len(last)} gates ({counts_text})"
    return False, ""
