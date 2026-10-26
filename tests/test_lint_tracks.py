"""Tests for the validator's registered tracks (HANDOFF-0042, schema v1.6; moved out of
`tests/test_lint.py` by HANDOFF-0060 §3, unchanged).

Purpose: the tracks are read whole or not at all; a record sits in a state folder or a
registered track's folder; a record in a track's folder carries the track's prefix.
Inputs: inline records and tracks.
Outputs: pytest assertions.
Side effects: none.
"""

import pytest

from kgme import lint

TRACK = lint.Track(
    "design", "CDH", "AUDIT-CDH", "docs/handoff/cockpit-design", "docs/audit/cockpit-design"
)


def record(kind: str, identifier: str) -> str:
    """A valid handoff or report with the given id."""
    fields = {
        "handoff": "from: cowork\nto: claude-code\n",
        "report": "author: codex\nsource: stated\nhandoff: CDH-0001\nperiod: 2026-10-25\n",
    }[kind]
    status = "open" if kind == "handoff" else "final"
    return (
        f"---\nid: {identifier}\ntype: {kind}\ncreated: 2026-10-25T12:00:00-07:00\n"
        f"status: {status}\ntier: 2\n{fields}---\nbody\n"
    )


def track_rules(text: str, rel_path: str) -> list[tuple[str, str]]:
    found = lint.lint_note(text, rel_path, {}, (TRACK,))
    return [(f.rule, f.cls) for f in found if f.rule.startswith("track")]


@pytest.mark.blocking
def test_tracks_are_read_whole_or_not_at_all() -> None:
    """HANDOFF-0042 §1: a `[tracks.*]` table with only `lanes` registers nothing; a partial
    registration is an error, never silently ignored."""
    assert lint.read_tracks({}) == ()
    assert lint.read_tracks({"tracks": {"design": {"lanes": ["docs/design/"]}}}) == ()
    full = {
        "handoff": "CDH",
        "audit": "AUDIT-CDH",
        "handoff_folder": "docs/handoff/cockpit-design/",
        "audit_folder": "docs/audit/cockpit-design/",
    }
    assert lint.read_tracks({"tracks": {"design": full}}) == (TRACK,)
    partial = {key: value for key, value in full.items() if key != "audit_folder"}
    with pytest.raises(ValueError, match="audit_folder"):
        lint.read_tracks({"tracks": {"design": partial}})


@pytest.mark.blocking
def test_a_record_sits_in_a_state_folder_or_a_registered_track_folder() -> None:
    """Schema v1.6: below docs/handoff/ and docs/audit/, only done/, proposed/, archive/ and the
    registered track folders; any other subfolder is blocking."""
    for rel in (
        "docs/handoff/x.md",
        "docs/handoff/done/x.md",
        "docs/handoff/proposed/x.md",
        "docs/handoff/archive/x.md",
    ):
        assert track_rules(record("handoff", "HANDOFF-0001"), rel) == [], rel
    assert track_rules(record("handoff", "CDH-0001"), "docs/handoff/cockpit-design/x.md") == []
    assert track_rules(record("report", "AUDIT-CDH-0001"), "docs/audit/cockpit-design/x.md") == []
    for rel in ("docs/handoff/stray/x.md", "docs/audit/stray/x.md", "docs/audit/done/deep/x.md"):
        found = track_rules(record("handoff", "HANDOFF-0001"), rel)
        assert ("track-folder", "blocking") in found or rel == "docs/audit/done/deep/x.md", rel
    assert lint.lint_note(record("handoff", "HANDOFF-0001"), "docs/handoff/stray/x.md", {}) == [
        f
        for f in lint.lint_note(record("handoff", "HANDOFF-0001"), "docs/handoff/stray/x.md", {})
        if not f.rule.startswith("track")
    ], "without tracks passed, a single-note caller sees no track rule"


@pytest.mark.blocking
def test_a_record_in_a_track_folder_carries_the_tracks_prefix() -> None:
    """Schema v1.6: a handoff in the track's handoff folder carries `CDH-`, a report in its
    audit folder `AUDIT-CDH-`; the main sequence's prefixes there are blocking."""
    handoff = "docs/handoff/cockpit-design/x.md"
    audit = "docs/audit/cockpit-design/x.md"
    assert track_rules(record("handoff", "HANDOFF-0099"), handoff) == [("track-id", "blocking")]
    assert track_rules(record("report", "AUDIT-0099"), audit) == [("track-id", "blocking")]
    assert track_rules(record("report", "AUDIT-CDH-0099"), audit) == []
    assert track_rules(record("handoff", "CDH-0099"), "docs/handoff/x.md") == []
