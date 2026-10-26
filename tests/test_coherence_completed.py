"""Tests for the `completed:` coherence check (HANDOFF-0060 §4).

Purpose: a done handoff's `completed:` is the `created` of its PASS review audit (Michou's rule
of 2026-10-21, `docs/STATUS.md`). Ten seconds off is one `advisory` line from `kgme lint`,
whatever `[coherence] blocking_from` makes the other checks; equal is no line; a handoff with
no PASS review, or an open one, is not this check's; the latest PASS of several is the one.
Inputs: fixture handoffs and audits under `tmp_path`.
Outputs: pytest assertions.
Side effects: files under `tmp_path` only.
"""

from pathlib import Path

import pytest

from kgme import coherence, vault

PASSED = "2026-10-26T00:17:35-07:00"


def write(base: Path, rel: str, text: str) -> None:
    (base / rel).parent.mkdir(parents=True, exist_ok=True)
    (base / rel).write_text(text, encoding="utf-8")


def handoff(base: Path, completed: str, status: str = "done", hid: str = "HANDOFF-0901") -> str:
    folder = "docs/handoff/done" if status == "done" else "docs/handoff"
    rel = f"{folder}/{hid.lower()}.md"
    write(
        base,
        rel,
        f"---\nid: {hid}\ntype: handoff\nstatus: {status}\ncompleted: {completed}\n"
        f"report: docs/audit/report.md\n---\n\n# A handoff\n",
    )
    return rel


def review(base: Path, number: int, created: str, verdict: str = "PASS") -> None:
    write(
        base,
        f"docs/audit/AUDIT-{number:04d}-review-handoff-0901-cycle-{number}.md",
        f"---\nid: AUDIT-{number:04d}\ntype: report\nhandoff: HANDOFF-0901\n"
        f"created: {created}\nverdict: {verdict}\n---\n\n# Review\n",
    )


def found(base: Path) -> list[str]:
    handoffs = vault.read_handoffs(base)
    return [f.line() for f in coherence.check_completed(handoffs, vault.read_passes(base))]


@pytest.mark.blocking
def test_ten_seconds_off_its_pass_review_is_one_advisory_line(tmp_path: Path) -> None:
    rel = handoff(tmp_path, "2026-10-26T00:17:45-07:00")
    review(tmp_path, 1, "2026-10-26T00:01:00-07:00", "BLOCK")
    review(tmp_path, 2, PASSED)
    lines = found(tmp_path)
    assert lines == [
        f"{rel}: coherence-completed [advisory] `completed` 2026-10-26T00:17:45-07:00 is not "
        f"the `created` of its PASS review AUDIT-0002, {PASSED} (10 s apart)"
    ]
    blocking = coherence.check_tree(
        vault.read_handoffs(tmp_path), [], frozenset({"docs/audit/report.md"}), "",
        passes=vault.read_passes(tmp_path), cls="blocking",
    )  # fmt: skip
    assert [f.cls for f in blocking if f.rule == "coherence-completed"] == ["advisory"]


@pytest.mark.blocking
def test_equal_is_no_line_and_the_latest_pass_is_the_one(tmp_path: Path) -> None:
    handoff(tmp_path, PASSED)
    review(tmp_path, 1, "2026-10-25T20:00:00-07:00")
    review(tmp_path, 2, PASSED)
    assert found(tmp_path) == []


@pytest.mark.blocking
def test_no_pass_review_or_an_open_handoff_is_not_this_checks(tmp_path: Path) -> None:
    handoff(tmp_path, "2026-10-26T00:17:45-07:00")
    review(tmp_path, 1, PASSED, "BLOCK")
    assert found(tmp_path) == []
    handoff(tmp_path, "2026-10-26T00:17:45-07:00", status="open", hid="HANDOFF-0902")
    assert found(tmp_path) == []


@pytest.mark.blocking
def test_review_c2_f4_the_latest_pass_is_the_latest_instant_across_an_offset_change(
    tmp_path: Path,
) -> None:
    """Review cycle 2 F4: on 2026-11-01, 01:00:05-08:00 is ten seconds after 01:59:55-07:00,
    though it sorts first as text; the latest PASS is the later instant."""
    rel = handoff(tmp_path, "2026-11-01T01:59:55-07:00")
    review(tmp_path, 1, "2026-11-01T01:59:55-07:00")
    review(tmp_path, 2, "2026-11-01T01:00:05-08:00")
    assert vault.read_passes(tmp_path)["HANDOFF-0901"][0] == "AUDIT-0002"
    assert found(tmp_path) == [
        f"{rel}: coherence-completed [advisory] `completed` 2026-11-01T01:59:55-07:00 is not "
        "the `created` of its PASS review AUDIT-0002, 2026-11-01T01:00:05-08:00 (10 s apart)"
    ]
