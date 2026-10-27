"""Tests for the pure half of `kgme review` (HANDOFF-0029).

Purpose: the findings parser against real reviewer shapes, malformed rows, inconsistent
verdicts, escaped pipes round-tripping through the audit text, the summary line and the
ledger state chunks that replay losslessly, the halt bound, rulings surviving an override,
and the escalation packet.
Inputs: sample markdown and synthetic events.
Outputs: pytest assertions.
Side effects: none.
"""

import pytest

from kgme import events, review, review_parse, review_text

SAMPLE = """## Findings

| id | class | file:line | finding | fix |
|---|---|---|---|---|
| F1 | blocking, resolved | `a.py:6` | **Verified.** Fixed. | None. |
| F2 | blocking | `b.py:101` | Script detection misses `a \\| b`. | Cover it. |
| F3 | blocking, unresolved | `c.py:9` | Still open. | Fix it. |
| F7 | advisory | `t.py:3` | Coverage gap. | Strengthen. |
| F9 | cosmetic | `c.py:1` | Naming. | Rename. |
| F12 |  | `d.py:9` | The reviewer forgot the class. | Add one. |

## Verdict

**BLOCK: 2 unresolved blocking root causes, F2 and F3.**

## Notes

Reviewed sha256 prefix `deadbeef00000000`.
"""

PASS_TEXT = (
    "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n\n"
    "## Verdict\n\nPASS\n"
)


def outcome(handoff: str, cycle: int, verdict: str, blocking: str, sha: str = "0" * 16) -> dict:
    return events.make_event(
        source="kgme",
        actor="kgme.review",
        kind="outcome",
        status="ok",
        class_="blocking" if verdict == "BLOCK" else None,
        job=f"review:{handoff}",
        summary=(
            f"review:{handoff} cycle {cycle} {verdict} sha={sha} blocking={blocking} "
            f"transient=0 cosmetic=0 advisory=0 audit=AUDIT-{cycle:04d}"
        ),
    )


def note(handoff: str, key: str, kind: str = "note", summary: str | None = None) -> dict:
    return events.make_event(
        source="human",
        actor="michou",
        kind=kind,
        job=f"review:{handoff}",
        key=key,
        summary=summary or key,
    )


@pytest.mark.blocking
def test_parse_findings_reads_classes_resolution_pipes_and_missing_class() -> None:
    found = review_parse.parse_findings(SAMPLE)
    assert [f.id for f in found] == ["F1", "F2", "F3", "F7", "F9", "F12"]
    assert found[0].cls == "blocking" and found[0].resolved
    assert found[1].cls == "blocking" and not found[1].resolved and "a | b" in found[1].text
    assert found[2].cls == "blocking" and not found[2].resolved, "unresolved is not resolved"
    assert found[5].cls is None
    assert review_parse.parse_verdict(SAMPLE) == "BLOCK"
    assert review_parse.open_blocking(found) == ["F2", "F3"]
    assert review_parse.verdict(found) == "BLOCK"


@pytest.mark.blocking
def test_parse_review_rejects_noise_malformed_rows_and_contradictions() -> None:
    assert review_parse.parse_review(SAMPLE).parseable
    assert review_parse.parse_review(PASS_TEXT).parseable
    assert not review_parse.parse_review("I could not read the patch. BLOCK?").parseable
    assert not review_parse.parse_review("## Findings\n\nno table\n\n## Verdict\n\nBLOCK").parseable
    incomplete = "## Findings\n\nReview incomplete; cannot PASS this change.\n"
    assert not review_parse.parse_review(incomplete).parseable
    assert review_parse.parse_verdict("PASS in prose, no section") is None
    empty_verdict = (
        "## Findings\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n\n"
        "## Verdict\n\n## Notes\nReview incomplete; cannot PASS this change.\n"
    )
    parsed = review_parse.parse_review(empty_verdict)
    assert not parsed.parseable and parsed.problem == "no verdict"
    quoting = (
        "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
        "| F2 | blocking | r.py:9 | searches after `## Verdict`; an accepted PASS results. "
        "| Bound it. |\n"
        "\n## Verdict\n\nBLOCK: 1 open.\n\n## Notes\n\n| id | class | x | y | z |\n"
    )
    parsed = review_parse.parse_review(quoting)
    assert parsed.parseable and parsed.verdict_word == "BLOCK"
    assert [f.id for f in parsed.findings] == ["F2"], "a table in the Notes is not findings"
    mixed = (
        "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
        "| F1 | advisory | a | b | c |\n| F2 | blocking | broken row without enough cells |\n\n"
        "## Verdict\n\nBLOCK\n"
    )
    parsed = review_parse.parse_review(mixed)
    assert not parsed.parseable and "malformed" in parsed.problem
    contradiction = SAMPLE.replace(
        "**BLOCK: 2 unresolved blocking root causes, F2 and F3.**", "PASS"
    )
    parsed = review_parse.parse_review(contradiction)
    assert not parsed.parseable and "contradicts" in parsed.problem
    assert review_parse.tooling_failure("HTTP 429 Too Many Requests") is not None
    assert review_parse.tooling_failure(SAMPLE) is None


@pytest.mark.blocking
def test_audit_text_round_trips_escaped_pipes_and_lists_open_ids() -> None:
    findings = review_parse.default_unclassed_to_advisory(review_parse.parse_findings(SAMPLE))
    text = review_text.audit_text(15, "HANDOFF-X", 1, "ab" * 32, "m", findings, "BLOCK", SAMPLE)
    assert "open_blocking: [F2, F3]" in text and "verdict: BLOCK" in text
    again = review_parse.parse_findings(text)
    assert [f.id for f in again] == [f.id for f in findings]
    assert next(f for f in again if f.id == "F2").text == "Script detection misses `a | b`."
    assert not review_parse.malformed_rows(text.partition("## Reviewer text")[0])


@pytest.mark.blocking
def test_reclassification_merges_by_id_and_rulings_apply() -> None:
    original = review_parse.parse_findings(SAMPLE)
    retried = review_parse.parse_rows(
        "| F12 | advisory | x | y | z |\n| F2 | cosmetic | x | y | z |"
    )
    merged = review_parse.merge_reclassification(original, retried)
    assert [f.id for f in merged] == [f.id for f in original]
    assert next(f for f in merged if f.id == "F12").cls == "advisory"
    assert next(f for f in merged if f.id == "F2").cls == "blocking", "only unclassed rows change"
    ruled = review_parse.apply_rulings(merged, {"F2": "advisory"})
    assert review_parse.open_blocking(ruled) == ["F3"]


@pytest.mark.blocking
def test_summary_line_and_state_chunks_replay_eighty_ids_losslessly() -> None:
    few = review_parse.default_unclassed_to_advisory(review_parse.parse_findings(SAMPLE))
    line = review.summary_line("HANDOFF-0029", 2, "BLOCK", "abc" * 30, few, "AUDIT-0015")
    assert len(line) <= 200 and "blocking=F2,F3" in line and "audit=AUDIT-0015" in line
    assert review.blocking_ids(line) == {"F2", "F3"} and review.state_chunks(few) == ["F2,F3"]
    many = [review_parse.Finding(f"F{i}", "blocking", False, "", "", "") for i in range(1, 81)]
    sha = "abcdef0123456789" * 4
    long = review.summary_line("HANDOFF-0029", 3, "BLOCK", sha, many, "AUDIT-0016")
    assert len(long) <= 200 and "blocking=#80:ledger" in long
    chunks = review.state_chunks(many)
    assert len(chunks) >= 2 and all(len(c) <= review.STATE_CHUNK_CHARS for c in chunks)
    assert review.blocking_ids(long, chunks) == {f"F{i}" for i in range(1, 81)}
    with pytest.raises(ValueError, match="incomplete"):
        review.blocking_ids(long, chunks[:1])
    with pytest.raises(ValueError, match="incomplete"):
        review.blocking_ids(long)
    first = outcome("H", 1, "BLOCK", "#80:ledger", sha[:16])
    history = [first]
    history += [
        note("H", f"state:{first['id']}:{i}", summary=f"ids={c}") for i, c in enumerate(chunks)
    ]
    state = review.loop_state(history)
    assert state.cycles == 1 and len(state.open_ids) == 80 and state.last_audit == "AUDIT-0001"
    # The same diff reviewed again with one id fewer: chunks belong to their own outcome (F9).
    fewer = [review_parse.Finding(f"F{i}", "blocking", False, "", "", "") for i in range(1, 80)]
    second = outcome("H", 2, "BLOCK", "#79:ledger", sha[:16])
    history.append(second)
    history += [
        note("H", f"state:{second['id']}:{i}", summary=f"ids={c}")
        for i, c in enumerate(review.state_chunks(fewer))
    ]
    replayed = review.loop_state(history)
    assert replayed.cycles == 2 and len(replayed.open_ids) == 79 and "F80" not in replayed.open_ids


def sha(n: int) -> str:
    return f"{n:016x}"


@pytest.mark.blocking
def test_three_cycles_on_one_root_cause_are_telemetry_and_two_send_it_to_the_arbiters() -> None:
    """HANDOFF-0043 amendment 16: the count no longer halts; two cycles go to the arbiters."""
    history = [outcome("H", 1, "BLOCK", "F2", sha(1))]
    assert review.loop_state(history).to_arbiters == ()
    history.append(outcome("H", 2, "BLOCK", "F2", sha(2)))
    state = review.loop_state(history)
    assert state.runs == {"F2": 2} and state.to_arbiters == ("F2",) and not state.halt
    history.append(note("H", "ruling:F2@claude-fable-5-1=advisory"))
    assert review.loop_state(history).to_arbiters == ("F2",), "one arbiter settles nothing"
    history.append(outcome("H", 3, "BLOCK", "F2", sha(3)))
    state = review.loop_state(history)
    assert state.runs == {"F2": 3} and not state.halt and state.reason == "converging"
    many = [outcome("H", c, "BLOCK", "F1,F2,F3", sha(c)) for c in (1, 2, 3)]
    assert not review.loop_state(many).halt, "three survivors are telemetry too"


@pytest.mark.blocking
def test_a_ruling_executed_and_the_same_root_cause_blocking_again_halts() -> None:
    """Measure (a): the settled ruling is executed, and the next cycle still blocks on it."""
    history = [outcome("H", 1, "BLOCK", "F2", sha(1)), outcome("H", 2, "BLOCK", "F2", sha(2))]
    history.append(note("H", "ruling:F2=blocking"))
    assert not review.loop_state(history).halt and review.loop_state(history).to_arbiters == ()
    history.append(outcome("H", 3, "BLOCK", "F2", sha(3)))
    state = review.loop_state(history)
    assert state.halt and state.reason == "F2 blocked again after its ruling was executed"
    fixed = history[:-1] + [outcome("H", 3, "BLOCK", "F5", sha(3))]
    assert not review.loop_state(fixed).halt, "another root cause is progress"


@pytest.mark.blocking
def test_a_review_started_before_the_ruling_does_not_count_as_its_execution() -> None:
    """Review cycle 1 F8: arbitration runs beside the builder, so a review whose intent came
    before the ruling and whose outcome came after it says nothing about the ruling."""
    early = events.make_event(
        source="kgme", actor="kgme.review", kind="intent", job="review:H", key="review:H:x",
        summary="review:H cycle 3",
    )  # fmt: skip
    history = [outcome("H", 1, "BLOCK", "F2", sha(1)), outcome("H", 2, "BLOCK", "F2", sha(2))]
    history += [early, note("H", "ruling:F2=blocking")]
    late = outcome("H", 3, "BLOCK", "F2", sha(3)) | {"ref": early["id"]}
    assert not review.loop_state([*history, late]).halt, "started before the ruling"
    after = outcome("H", 4, "BLOCK", "F2", sha(4))  # its own id stands for its intent
    assert review.loop_state([*history, late, after]).halt


@pytest.mark.blocking
def test_a_diff_reviewed_twice_halts() -> None:
    """Measure (b): the same diff hash under review again in the window."""
    history = [outcome("H", 1, "BLOCK", "F2", sha(1)), outcome("H", 2, "BLOCK", "F3", sha(1))]
    state = review.loop_state(history)
    assert state.halt and f"diff {sha(1)} was reviewed before" in state.reason
    history.append(note("H", "override:H", kind="approval"))
    assert not review.loop_state(history).halt, "an override clears the window"
    ruled = history[:1] + [note("H", "ruling:F2=advisory"), history[1]]
    assert not review.loop_state(ruled).halt, "a ruling between the two is progress"


@pytest.mark.blocking
def test_three_red_gates_whose_failing_count_never_falls_halt() -> None:
    """Measure (c), read from `gate:` notes."""

    def gates(*counts: int) -> list[dict]:
        return [
            note("H", f"gate:H:{i}", summary=review.gate_summary("H", 1 if n else 0, n))
            for i, n in enumerate(counts, 1)
        ]

    state = review.loop_state(gates(3, 3, 4))
    assert state.halt and "has not fallen in 3 gates (3, 3, 4)" in state.reason
    assert not review.loop_state(gates(3, 2, 2)).halt, "it fell once"
    assert not review.loop_state(gates(3, 3, 0, 3)).halt, "a green gate breaks the run"
    assert not review.loop_state(gates(5, 5)).halt


@pytest.mark.blocking
def test_gate_failures_counts_what_a_red_gate_prints() -> None:
    assert review.gate_failures(0, "3 failed") == 0
    assert review.gate_failures(2, "== 3 failed, 690 passed in 9s ==") == 3
    assert review.gate_failures(2, "kgme lint: 330 notes, 2 blocking, 9 advisory") == 2
    assert review.gate_failures(2, "kgme mods: 2 mod folders, 2 blocking") == 2
    assert review.gate_failures(2, "1 failed, 2 errors in 3s") == 3
    assert review.gate_failures(2, "make: *** [check] Error 1") == 1, "red is never zero"


@pytest.mark.blocking
def test_transient_outcomes_rulings_halt_notes_and_overrides() -> None:
    hung = events.make_event(
        source="kgme",
        actor="kgme.review",
        kind="outcome",
        status="error",
        class_="transient",
        job="review:H",
        summary="review:H cycle 2 attempt 1/3 reviewer timed out; not counted",
    )
    history = [outcome("H", 1, "BLOCK", "F2,F8", sha(1)), hung]
    history.append(outcome("H", 2, "BLOCK", "F2,F8", sha(2)))
    assert review.loop_state(history).cycles == 2
    history += [note("H", "ruling:F8=advisory"), outcome("H", 3, "BLOCK", "F2,F8", sha(3))]
    state = review.loop_state(history)
    assert state.open_ids == ("F2",) and not state.halt and state.rulings == {"F8": "advisory"}
    history.append(note("H", "halt:H:3"))
    assert review.loop_state(history).active_halt
    history.append(note("H", "override:H", kind="approval"))
    after = review.loop_state(history)
    assert after.cycles == 3 and after.since_override == 0 and not after.active_halt
    assert after.rulings == {"F8": "advisory"}, "rulings survive an override"
    assert after.last_audit == "AUDIT-0003", "the previous table stays visible"
    history.append(outcome("H", 4, "BLOCK", "F2,F8", sha(4)))
    fresh = review.loop_state(history)
    assert fresh.open_ids == ("F2",) and fresh.last_audit == "AUDIT-0004"
    assert fresh.cycles == 4 and fresh.since_override == 1 and not fresh.halt


@pytest.mark.blocking
def test_escalation_packet_is_one_screen_with_the_four_parts() -> None:
    state = review.loop_state([outcome("H", c, "BLOCK", "F2") for c in (1, 2)])
    assert state.halt
    packet = review_text.escalation_packet("H", state, review_parse.parse_findings(SAMPLE), "opus")
    for part in ("What failed", "Evidence", "Options", "Recommended default", "If you do nothing"):
        assert part in packet
    assert "arbiter opus" in packet and packet.count("\n") < 20
