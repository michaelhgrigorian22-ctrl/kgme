"""`kgme review`, the state: what one handoff's loop has recorded, read back from the ledger.

Purpose: the ledger summaries a review cycle writes and their reconstruction into a
`LoopState` that decides the halt (`docs/readers/review-loop.md` bound, ADR-016). Parsing
lives in `kgme.review_parse`, rendering in `kgme.review_text`.
Inputs: findings, identifiers, prior ledger events for one handoff.
Outputs: summary lines, state chunks, a `LoopState`.
Side effects: none.
"""

import re
from dataclasses import dataclass

from kgme import events
from kgme.review_parse import Finding, counts, open_blocking

BLOCKING_INLINE = re.compile(r"blocking=(?P<ids>[F0-9,]+|-)")
BLOCKING_IN_LEDGER = re.compile(r"blocking=#(?P<count>\d+):ledger")
AUDIT_TOKEN = re.compile(r"audit=(?P<audit>AUDIT-\d{4})")
STATE_CHUNK_CHARS = 150
CONSECUTIVE_CYCLES_TO_HALT = 3
SURVIVOR_THRESHOLD = 3


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


def loop_state(handoff_events: list[dict]) -> LoopState:
    """Reconstruct the loop from events with `job: review:<handoff>`, in id order.

    Each successful `outcome` is one review cycle; its summary names the open blocking ids,
    inline or through `state:<outcome id>:<n>` notes. An error outcome is a tooling failure and
    is not a cycle. A `note` keyed `ruling:<id>=<class>` is the arbiter's ruling and holds
    until a contrary ruling; rulings survive overrides. A `note` keyed `halt:` leaves the loop
    halted until an `approval` keyed `override:`, which clears the strike history and the halt
    but keeps `last_audit`, so the next cycle still sees the previous table.

    Halt (HANDOFF-0029, reader): three or more root causes still blocking after a fix cycle,
    or one root cause blocking in three consecutive cycles.
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
    active_halt = False
    last_audit: str | None = None
    total = 0
    for event in ordered:
        key = event["key"] or ""
        if event["kind"] == "approval":
            cycles, active_halt = [], False
        elif event["kind"] == "note" and key.startswith("ruling:"):
            finding_id, _, cls = key[len("ruling:") :].partition("=")
            rulings[finding_id] = cls
        elif event["kind"] == "note" and key.startswith("halt:"):
            active_halt = True
        elif event["kind"] == "outcome" and event["status"] == "ok":
            ids = blocking_ids(event["summary"], chunks.get(event["id"]))
            cycles.append({i for i in ids if rulings.get(i, "blocking") == "blocking"})
            total += 1
            audit = AUDIT_TOKEN.search(event["summary"])
            last_audit = audit["audit"] if audit else last_audit
    if not cycles:
        return LoopState(
            total, 0, (), (), {}, False, "no cycle recorded", active_halt, rulings, last_audit
        )
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
    longest = max(runs.values(), default=0)
    if len(survivors) >= SURVIVOR_THRESHOLD:
        halt = True
        reason = f"{len(survivors)} root causes survived a fix cycle: {', '.join(survivors)}"
    elif longest >= CONSECUTIVE_CYCLES_TO_HALT:
        worst = next(i for i, r in runs.items() if r == longest)
        halt, reason = True, f"{worst} has stood blocking for {longest} consecutive cycles"
    else:
        halt, reason = False, "within the bound"
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
    )
