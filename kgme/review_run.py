"""`kgme review`, the cycle: gate, intent, reviewer with bounded retries, audit, outcome, halt.

Purpose: run one cycle of `docs/readers/review-loop.md` with the primitives in
`kgme.review_io` and the logic in `kgme.review`, and leave every step in the ledger. Each gate
is a `gate:` note with its failing count (HANDOFF-0043 amendment 16 c). The cycle's diff,
dispositions and audit stay on disk (`review.patch`, `review.dispositions` under scratch, the
audit the ledger names), so a builder whose context was compacted re-reads them (amendment 5).
A disputed finding, or one blocking two consecutive cycles, goes to the arbiter pair of
`kgme.toml [models] arbiters` (amendment 20, `run_arbiters`): each a fresh read-only `-p` run on
one brief, in parallel, each ruling its own `ruling:<id>@<arbiter>=<class>` note with the
brief's path and sha256 in its payload, then one settled `ruling:<id>=<class>` (agreement, or
on a split the reversible option with the smallest blast radius, `kgme.loop.settle`) and, on a
split, a `split:` note for the approval screen.
Inputs: the handoff id, the patch text, the builder's dispositions, the places to write; for
the arbiters, the finding, the builder's argument, the brief template and the models.
Outputs: exit code 0 (PASS), 1 (BLOCK or tooling exhausted), 2 (usage), 3 (halt).
Side effects: appends ledger events; writes the scratch patch, hash and dispositions, the
reviewer's stream and text, the audit file, the briefs and the payloads, all through
`kgme.review_io`; sleeps between reviewer attempts; runs the arbiters. A dry run writes
nothing at all.
"""

import dataclasses
import json
import os
import random
import re
import subprocess
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from kgme import events, ledger, review, review_io, review_parse, review_text
from kgme.review_io import Places, read_places  # noqa: F401 - the CLI reaches them here

ATTEMPTS = 3
# ADR-016's default window is ten minutes; a review of a real diff takes about eight, so the
# window here is three attempts of at most ten minutes each plus backoff, stated as such.
DEFAULT_BACKOFF_SECONDS = (30, 60)
ARBITER_TIMEOUT_SECONDS = 900
TEXT_FIELDS = ("option", "reason")
ARBITER_REPLY = re.compile(r"\{[^{}]*\"class\"[^{}]*\}", re.S)
# the whole diff goes to the arbiters; one too large for a brief is refused, never cut (F9)
DIFF_IN_BRIEF_CHARS = 400_000
RECLASSIFY = (
    "Your review below left these findings without an ADR-016 class: $IDS. Reply with the same "
    "Findings table, every row carrying blocking, transient, cosmetic, or advisory, and change "
    "nothing else.\n\n$REVIEW"
)


def _event(kind: str, handoff: str, key: str, parent: str | None, summary: str, **more) -> dict:
    """An event of this job, `summary` clipped to the writer's cap."""
    return events.make_event(
        source="kgme",
        actor="kgme.review",
        kind=kind,
        job=f"review:{handoff}",
        key=key,
        parent=parent,
        summary=events.clip(summary),
        **more,
    )


def _jittered(seconds: int) -> float:
    """A backoff with up to half its length of jitter, per ADR-016."""
    return seconds + random.uniform(0, seconds / 2)


def run_reviewer_attempts(
    prompt: str,
    model: str,
    places: Places,
    handoff: str,
    key: str,
    parent: str,
    intent_id: str,
    cycle: int,
    backoff: tuple[int, ...],
) -> tuple[review_parse.Parsed | None, str]:
    """Up to `ATTEMPTS` reviewer runs. Every failed attempt is a transient outcome that
    references the intent; exhaustion is a blocking error outcome that closes it."""
    for attempt in range(1, ATTEMPTS + 1):
        code, text, stderr = review_io.run_reviewer(
            prompt,
            model,
            places.root,
            places.scratch / "review-out.md",
            places.scratch / "review-out.jsonl",
        )
        parsed = review_parse.parse_review(text)
        if code == 0 and parsed.parseable:
            return parsed, text
        if code == 124:
            reason = "reviewer timed out"
        elif code == 0 and text.strip():
            reason = f"reviewer text not accepted: {parsed.problem}"
        else:
            tooling = review_parse.tooling_failure(text + stderr)
            reason = tooling or f"reviewer exited {code} with no text"
        ledger.append(
            _event(
                "outcome",
                handoff,
                key,
                parent,
                f"review:{handoff} cycle {cycle} attempt {attempt}/{ATTEMPTS} "
                f"{reason}; not counted",
                status="error",
                class_="transient",
                ref=intent_id,
            ),
            places.dirs,
        )
        if attempt < ATTEMPTS and attempt - 1 < len(backoff):
            time.sleep(_jittered(backoff[attempt - 1]))
    ledger.append(
        _event(
            "outcome",
            handoff,
            key,
            parent,
            f"review:{handoff} cycle {cycle} tooling exhausted after {ATTEMPTS} attempts; "
            "not a strike",
            status="error",
            class_="blocking",
            ref=intent_id,
        ),
        places.dirs,
    )
    return None, ""


def run_cycle(
    handoff: str,
    model: str,
    dispositions: str,
    patch_text: str,
    places: Places,
    dry_run: bool,
    arbiter: str = "opus",
    backoff: tuple[int, ...] = DEFAULT_BACKOFF_SECONDS,
    rulings_seen: tuple[str, ...] | None = None,
) -> int:
    """One cycle. Returns the exit code; prints one line, or the escalation packet on a halt."""
    handoff_path = review_io.read_handoff_path(places.handoff_dir, handoff)
    if handoff_path is None:
        print(f"kgme review: no file under {places.handoff_dir} carries id {handoff}")
        return 2
    history = review_io.read_handoff_events(handoff, places.dirs)
    state = review.loop_state(history)
    if state.active_halt:
        print(f"kgme review: {handoff} is halted ({state.reason}); record an override first")
        return 3
    cycle = state.cycles + 1
    if cycle > 1 and not dispositions.strip():
        print(
            f"kgme review: cycle {cycle} needs --dispositions, "
            f"the builder's answer to cycle {cycle - 1}"
        )
        return 2
    sha = review_io.sha256_text(patch_text)
    # the settled rulings known before the gate (from the CLI), else at the cycle's start
    known = rulings_seen if rulings_seen is not None else tuple(sorted(state.rulings))
    patch_path = places.scratch / "review.patch"
    prior = ""
    if state.last_audit:
        prior = review_io.read_audit_table(places.audit_dir, state.last_audit)
    prompt = review_io.render_prompt(
        review_io.read_text(places.prompt_path),
        {
            "HANDOFF": handoff,
            "HANDOFF_PATH": review_io.shown(handoff_path, places.root),
            "CYCLE": str(cycle),
            "PATCH_PATH": review_io.shown(patch_path, places.root),
            "SHA": sha[:16],
            "PRIOR_FINDINGS": prior or "(none recorded)",
            "DISPOSITIONS": dispositions.strip() or "(first cycle; none)",
        },
    )
    if dry_run:
        print(
            f"dry run: {handoff} cycle {cycle}, diff {sha[:16]}, reviewer {model}; nothing written"
        )
        print(prompt)
        return 0
    review_io.write_text(patch_path, patch_text)
    review_io.write_text(places.scratch / "review.sha", sha[:16] + "\n")
    review_io.write_text(places.scratch / "review.dispositions", dispositions)
    parent = review_io.first_intent_id(history)
    key = f"review:{handoff}:{sha[:16]}"
    intent_id = ledger.append(
        _event(
            "intent",
            handoff,
            key,
            parent,
            f"review:{handoff} cycle {cycle} sha={sha[:16]} reviewer={model} "
            f"ruled={','.join(known) or '-'}",
        ),
        places.dirs,
    )
    parent = parent or intent_id
    write_evidence(places, handoff, intent_id, patch_text, dispositions)
    parsed, raw = run_reviewer_attempts(
        prompt, model, places, handoff, key, parent, intent_id, cycle, backoff
    )
    if parsed is None:
        print("reviewer tooling exhausted; recorded, not counted; run again later")
        return 1
    findings = parsed.findings
    if review_parse.unclassed(findings):
        ids = ", ".join(f.id for f in review_parse.unclassed(findings))
        ledger.append(
            _event(
                "note",
                handoff,
                f"reclassify:{sha[:16]}",
                parent,
                f"review:{handoff} cycle {cycle} reclassification asked for {ids}",
            ),
            places.dirs,
        )
        code, text, _ = review_io.run_reviewer(
            review_io.render_prompt(RECLASSIFY, {"IDS": ids, "REVIEW": raw}),
            model,
            places.root,
            places.scratch / "review-retry.md",
            places.scratch / "review-retry.jsonl",
        )
        if code == 0:
            findings = review_parse.merge_reclassification(findings, review_parse.parse_rows(text))
            raw += "\n\n## Reclassification\n\n" + text
    findings = review_parse.apply_rulings(
        review_parse.default_unclassed_to_advisory(findings), state.rulings
    )
    verdict_word = review_parse.verdict(findings)
    number = review_io.read_next_audit_number(places.audit_dir)
    audit_id = f"AUDIT-{number:04d}"
    audit_path = places.audit_dir / f"{audit_id}-review-{handoff.lower()}-cycle-{cycle}.md"
    audit_body = review_text.audit_text(
        number, handoff, cycle, sha, model, findings, verdict_word, raw
    )
    review_io.write_text(audit_path, audit_body)
    write_findings(places, handoff, intent_id, audit_body)
    payload_ref, digest = review_io.write_payload(
        places.payloads,
        f"{audit_id}-stream.jsonl",
        review_io.read_text(places.scratch / "review-out.jsonl"),
        places.root,
    )
    summary = review.summary_line(handoff, cycle, verdict_word, sha, findings, audit_id)
    outcome_id = ledger.append(
        _event(
            "outcome",
            handoff,
            key,
            parent,
            summary,
            status="ok",
            class_="blocking" if verdict_word == "BLOCK" else None,
            ref=intent_id,
            payload_ref=payload_ref,
            payload_sha256=digest,
        ),
        places.dirs,
    )
    if ":ledger" in summary:
        for index, chunk in enumerate(review.state_chunks(findings)):
            ledger.append(
                _event("note", handoff, f"state:{outcome_id}:{index}", parent, f"ids={chunk}"),
                places.dirs,
            )
    print(f"{verdict_word}: {review_io.shown(audit_path, places.root)}")
    state = review.loop_state(review_io.read_handoff_events(handoff, places.dirs))
    if not state.halt:
        return 0 if verdict_word == "PASS" else 1
    write_halt(handoff, state, findings, arbiter, places, audit_path, f"cycle {cycle}", audit_id)
    return 3


def write_halt(
    handoff: str,
    state: review.LoopState,
    findings: list,
    arbiter: str,
    places: Places,
    audit_path=None,
    label: str = "",
    audit_id: str | None = None,
) -> str:
    """Effect: the escalation packet, appended to the audit when there is one, as a payload,
    and the `halt:` note that holds the loop until an override; prints the packet."""
    packet = review_text.escalation_packet(handoff, state, findings, arbiter)
    if audit_path is not None:
        review_io.write_text(
            audit_path,
            review_io.read_text(audit_path) + f"\n## Escalation\n\n```\n{packet}\n```\n",
        )
    name = f"{audit_id or 'gate-' + events.new_ulid()}-escalation.txt"
    packet_ref, packet_digest = review_io.write_payload(places.payloads, name, packet, places.root)
    history = review_io.read_handoff_events(handoff, places.dirs)
    where = f"; packet in {audit_id}" if audit_id else ""
    note_id = ledger.append(
        _event(
            "note",
            handoff,
            f"halt:{handoff}:{label.replace(' ', '-') or 'gate'}",
            review_io.first_intent_id(history),
            f"review:{handoff} HALT after {label}: {state.reason}{where}",
            class_="blocking",
            payload_ref=packet_ref,
            payload_sha256=packet_digest,
        ),
        places.dirs,
    )
    print(packet)
    return note_id


def write_gate(handoff: str, code: int, output: str, places: Places, arbiter: str) -> int:
    """Effect: one `gate:` note with the gate's failing count; on measure (c), the halt.
    Returns the exit code `kgme review` gives a red gate: 3 on a halt, else 2."""
    history = review_io.read_handoff_events(handoff, places.dirs)
    failing = review.gate_failures(code, output)
    gates = sum(1 for e in history if (e["key"] or "").startswith("gate:"))
    ledger.append(
        _event(
            "note",
            handoff,
            f"gate:{handoff}:{gates + 1}",
            review_io.first_intent_id(history),
            review.gate_summary(handoff, code, failing),
            class_=None if code == 0 else "blocking",
        ),
        places.dirs,
    )
    state = review.loop_state(review_io.read_handoff_events(handoff, places.dirs))
    if code != 0 and state.halt and not state.active_halt:
        write_halt(handoff, state, [], arbiter, places, label=f"gate {gates + 1}")
        return 3
    return 2


def arbiter_argv(model: str, out_path: Path) -> tuple[list[str], str]:
    """Pure: the read-only, tool-less `-p` run of one arbiter and its harness name; the brief
    goes in on stdin. A `gpt-` model runs through `codex exec -s read-only`, anything else
    through `claude -p` with no tools and one turn. Measured 2026-10-26 (claude 2.1.310):
    `--tools` takes a variadic list, so a brief after `--tools ""` was read as a tool name and
    the arbiter got no prompt; stdin carries it instead."""
    if model.startswith("gpt-"):
        argv = ["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "-m", model]
        return argv + ["-o", str(out_path), "-"], "codex exec"
    return ["claude", "-p", "--model", model, "--max-turns", "1", "--tools", ""], "claude -p"


def parse_ruling(text: str) -> dict | None:
    """Pure: the last JSON object in an arbiter's reply that is a complete ruling: `class` one
    of ADR-016's, `option` and `reason` non-empty strings, `reversible` a JSON boolean,
    `blast_radius` an integer from 1 to 5. Anything else is no ruling (review cycle 1 F7)."""
    for raw in reversed(ARBITER_REPLY.findall(text)):
        try:
            ruling = json.loads(raw)
        except ValueError:
            continue
        radius = ruling.get("blast_radius")
        if (
            ruling.get("class") in review_parse.CLASSES
            and all(isinstance(ruling.get(k), str) and ruling[k].strip() for k in TEXT_FIELDS)
            and isinstance(ruling.get("reversible"), bool)
            and isinstance(radius, int) and not isinstance(radius, bool) and 1 <= radius <= 5
        ):  # fmt: skip
            return {
                k: ruling[k] for k in ("class", "option", "reversible", "blast_radius", "reason")
            }
    return None


def run_arbiter(model: str, brief: str, scratch: Path) -> tuple[str, str]:
    """Effect: one fresh arbiter run; its harness and reply text (empty on a failure). The
    child gets no Claude Code session variables, so it runs no hooks of this session."""
    out_path = scratch / f"arbiter-{model}-{events.new_ulid()}.txt"  # one per call (F13)
    argv, harness = arbiter_argv(model, out_path)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "KGME_LOOP"))}
    try:
        done = subprocess.run(
            argv, input=brief, capture_output=True, text=True, env=env,
            timeout=ARBITER_TIMEOUT_SECONDS,
        )  # fmt: skip
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return harness, ""
    if done.returncode != 0:  # a failed call is no reply, whatever is on disk (F13)
        return harness, ""
    text = done.stdout
    if out_path.exists():
        text += "\n" + review_io.read_text(out_path)
    return harness, text


def write_evidence(
    places: Places, handoff: str, attempt: str, patch_text: str, dispositions: str
) -> Path:
    """Effect: the bundle of one review attempt, `<scratch>/evidence/<handoff>/<intent id>/`:
    the patch and the dispositions it was reviewed with, and later (`write_findings`) its
    audit's findings table. Keyed by the attempt, so no other attempt, cycle or handoff
    overwrites it (review cycles 2 and 3, F14). Returns the folder."""
    folder = places.scratch / "evidence" / handoff / attempt
    review_io.write_text(folder / "review.patch", patch_text)
    review_io.write_text(folder / "review.dispositions", dispositions)
    return folder


def write_findings(places: Places, handoff: str, attempt: str, audit_text: str) -> None:
    """Effect: the attempt's audit findings table, into its bundle."""
    table = review_parse.section(audit_text, "Findings") or ""
    review_io.write_text(places.scratch / "evidence" / handoff / attempt / "findings.md", table)


def read_evidence(
    places: Places, handoff: str, history: list[dict], finding_id: str
) -> tuple[tuple[str, str, str] | None, str]:
    """Effect: the diff, dispositions and finding row of the handoff's newest successful
    review, read from the bundle of the attempt its outcome answers (`ref`), the patch checked
    against the hash the outcome names; or None and why, when any part is missing or does not
    match, or the diff is too large for a brief (F9: refused, never cut)."""
    cycles = [
        e for e in history
        if e["kind"] == "outcome" and e["status"] == "ok"
        and not (e["key"] or "").startswith("loop:") and review.SHA_TOKEN.search(e["summary"])
    ]  # fmt: skip
    if not cycles:
        return None, "no reviewed cycle to arbitrate"
    last = cycles[-1]
    sha = review.SHA_TOKEN.search(last["summary"])["sha"]
    if not last.get("ref"):
        return None, f"the reviewed cycle of diff {sha} names no attempt; its evidence is missing"
    folder = places.scratch / "evidence" / handoff / last["ref"]
    parts = {name: folder / name for name in ("review.patch", "review.dispositions", "findings.md")}
    absent = [name for name, path in parts.items() if not path.is_file()]
    if absent:
        return None, f"the evidence of the reviewed diff {sha} is missing ({', '.join(absent)})"
    diff = review_io.read_text(parts["review.patch"])
    if review_io.sha256_text(diff)[:16] != sha:
        return None, f"the evidence on disk does not match the reviewed diff {sha}"
    if len(diff) > DIFF_IN_BRIEF_CHARS:
        return None, f"the diff is too large for the brief ({len(diff)} chars)"
    rows = [
        ln for ln in review_io.read_text(parts["findings.md"]).splitlines()
        if ln.startswith(f"| {finding_id} |")
    ]  # fmt: skip
    if not rows:
        return None, f"the reviewed cycle of diff {sha} has no row for {finding_id}"
    return (diff, review_io.read_text(parts["review.dispositions"]), rows[-1]), ""


def run_arbiters(
    handoff: str,
    finding_id: str,
    argument: str,
    places: Places,
    models: list[str],
    template: str,
    run_one: Callable[[str, str, Path], tuple[str, str]] = run_arbiter,
) -> dict | None:
    """Effect: the arbiter pair on one finding, in parallel, each fresh and gone; every ruling
    and the settlement on the ledger. Returns the settlement, or None when no arbiter ruled
    or the finding already has a settled ruling."""
    from kgme import loop

    history = review_io.read_handoff_events(handoff, places.dirs)
    if any((e["key"] or "").startswith(f"ruling:{finding_id}=") for e in history):
        return None
    parent = review_io.first_intent_id(history)
    evidence, why = read_evidence(places, handoff, history, finding_id)
    if evidence is None or len(set(models)) < 2:
        why = why or "the pair is not two distinct models"
        ledger.append(
            _event("note", handoff, f"arbiter-refused:{finding_id}", parent,
                   f"arbiters not run on {finding_id}: {why}; not settled", class_="transient"),
            places.dirs,
        )  # fmt: skip
        return None
    diff, dispositions, row = evidence
    argument = argument if argument.strip() else dispositions
    brief = review_io.render_prompt(
        template,
        {
            "HANDOFF": handoff,
            "FINDING": row,
            "BUILDER_ARGUMENT": argument.strip() or "(the finding stood two cycles; no dispute)",
            "DIFF": diff,
        },
    )
    brief_path = places.scratch / "arbiter" / f"{handoff}-{finding_id}-brief.md"
    review_io.write_text(brief_path, brief)
    brief_sha = review_io.sha256_text(brief)
    with ThreadPoolExecutor(max_workers=len(models) or 1) as pool:
        replies = list(pool.map(lambda m: run_one(m, brief, brief_path.parent), models))
    rulings = []
    for model, (harness, text) in zip(models, replies, strict=True):
        ruling = parse_ruling(text)
        record = {
            "arbiter": model, "harness": harness, "brief": review_io.shown(brief_path, places.root),
            "brief_sha256": brief_sha, "reply": text, "ruling": ruling,
        }  # fmt: skip
        ref, digest = review_io.write_payload(
            places.payloads,
            f"ruling-{handoff}-{finding_id}-{model}-{events.new_ulid()}.json",
            json.dumps(record, indent=2) + "\n",
            places.root,
        )
        if ruling is None:
            ledger.append(
                _event(
                    "note",
                    handoff,
                    f"arbiter-failed:{finding_id}@{model}",
                    parent,
                    f"arbiter {model} ({harness}) gave no ruling on {finding_id}; not counted",
                    class_="transient",
                    payload_ref=ref,
                    payload_sha256=digest,
                ),  # fmt: skip
                places.dirs,
            )
            continue
        rulings.append({**ruling, "arbiter": model})
        ledger.append(
            events.make_event(
                source="kgme",
                actor=f"arbiter.{model}",
                kind="note",
                job=f"review:{handoff}",
                key=f"ruling:{finding_id}@{model}={ruling['class']}",
                parent=parent,
                summary=events.clip(
                    f"arbiter {model} ({harness}) ruled {finding_id}={ruling['class']}: "
                    f"{ruling['option']}; {ruling['reason']}"
                ),
                payload_ref=ref,
                payload_sha256=digest,
            ),  # fmt: skip
            places.dirs,
        )
    if len(rulings) < len(models):  # the pair, or nothing: a failure stays pending (F5)
        return None
    settled = loop.settle(rulings)
    if settled is None:
        return None
    if settled["escalate"]:  # a split among one-way doors is Michou's (ADR-023, F6)
        ledger.append(
            _event("note", handoff, f"split:{finding_id}", parent,
                   f"arbiters split on {finding_id}: {settled['split_text']}; no reversible "
                   "option, so it goes to Michou; nothing executed", class_="blocking"),
            places.dirs,
        )  # fmt: skip
        state = review.loop_state(review_io.read_handoff_events(handoff, places.dirs))
        state = dataclasses.replace(state, halt=True, reason=settled["reason"])
        write_halt(handoff, state, [], "pair", places, label=f"split {finding_id}")
        return settled
    review_io.write_ruling(handoff, finding_id, settled["class"], settled["reason"], "pair", places)
    if settled["split"]:
        ledger.append(
            _event(
                "note",
                handoff,
                f"split:{finding_id}",
                parent,
                f"for the approval screen: {finding_id} settled {settled['class']} by the "
                f"smallest blast radius on a split: {settled['split_text']}",
                class_="advisory",
            ),  # fmt: skip
            places.dirs,
        )
    return settled
