"""`kgme review`, the cycle: gate, intent, reviewer with bounded retries, audit, outcome, halt.

Purpose: run one cycle of `docs/readers/review-loop.md` with the primitives in
`kgme.review_io` and the logic in `kgme.review`, and leave every step in the ledger.
Inputs: the handoff id, the patch text, the builder's dispositions, the places to write.
Outputs: exit code 0 (PASS), 1 (BLOCK or tooling exhausted), 2 (usage), 3 (halt).
Side effects: appends ledger events; writes the scratch patch and hash, the reviewer's stream
and text, the audit file, and the payloads, all through `kgme.review_io`; sleeps between
reviewer attempts. A dry run writes nothing at all.
"""

import random
import time

from kgme import events, ledger, review, review_io, review_parse, review_text
from kgme.review_io import Places, read_places  # noqa: F401 - the CLI reaches them here

ATTEMPTS = 3
# ADR-016's default window is ten minutes; a review of a real diff takes about eight, so the
# window here is three attempts of at most ten minutes each plus backoff, stated as such.
DEFAULT_BACKOFF_SECONDS = (30, 60)
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
    parent = review_io.first_intent_id(history)
    key = f"review:{handoff}:{sha[:16]}"
    intent_id = ledger.append(
        _event(
            "intent",
            handoff,
            key,
            parent,
            f"review:{handoff} cycle {cycle} sha={sha[:16]} reviewer={model}",
        ),
        places.dirs,
    )
    parent = parent or intent_id
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
    review_io.write_text(
        audit_path,
        review_text.audit_text(number, handoff, cycle, sha, model, findings, verdict_word, raw),
    )
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
    packet = review_text.escalation_packet(handoff, state, findings, arbiter)
    review_io.write_text(
        audit_path, review_io.read_text(audit_path) + f"\n## Escalation\n\n```\n{packet}\n```\n"
    )
    packet_ref, packet_digest = review_io.write_payload(
        places.payloads, f"{audit_id}-escalation.txt", packet, places.root
    )
    ledger.append(
        _event(
            "note",
            handoff,
            f"halt:{handoff}:{cycle}",
            parent,
            f"review:{handoff} HALT after cycle {cycle}: {state.reason}; packet in {audit_id}",
            class_="blocking",
            payload_ref=packet_ref,
            payload_sha256=packet_digest,
        ),
        places.dirs,
    )
    print(packet)
    return 3
