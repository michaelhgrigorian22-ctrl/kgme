"""Canary cells for the conductor's attribution and role (HANDOFF-0073 §§3-4).

Purpose: under `KGME_CONDUCTOR=hermes`, the `agent:run` intent and outcome, the session note,
and the loop's and crew's events carry `[conductor: hermes]` in their summary, and the run's
payloads carry `conductor`; without it nothing changes; a value that is not a plain name is
never written; a conductor's terminal cannot `kgme approve`; `conductor.hermes` lints clean,
is its department's manager, and escalates to michou.
Inputs: fixture checkouts from `tests/roletools.py`; a recorder in place of `claude`; this
repository's roles.
Outputs: pytest assertions.
Side effects: repositories and test streams under `tmp_path`; nothing is launched.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from roletools import ROOT, SETTINGS, make_run_settings, role_text, write_repo

from kgme import approve, conductor, crew_io, events, ledger, loop, roles, roles_io, roles_run

MARK = "[conductor: hermes]"


def test_tag_marks_and_keeps_the_mark_within_the_cap() -> None:
    env = {"KGME_CONDUCTOR": "hermes"}
    assert conductor.tag("agent x: exit 0", env) == "agent x: exit 0 " + MARK
    long = conductor.tag("y" * 300, env)
    assert len(long) <= events.MAX_SUMMARY_CHARS and long.endswith(MARK)
    assert conductor.tag("plain", {}) == "plain"
    assert conductor.record(env) == {"conductor": "hermes"} and conductor.record({}) == {}


@pytest.mark.parametrize("value", ["", "Hermes", "hermes; rm -rf", "x" * 40, "a b"])
def test_a_value_that_is_not_a_plain_name_is_never_written(value: str) -> None:
    assert conductor.name({"KGME_CONDUCTOR": value}) is None
    assert conductor.tag("s", {"KGME_CONDUCTOR": value}) == "s"


@pytest.mark.blocking
def test_agent_run_under_hermes_carries_the_conductor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = write_repo(tmp_path, {"build/reader": role_text("build", "reader")})
    (base / "CLAUDE.md").write_text("# fixture\n")
    dirs = ledger.read_test_dirs(SETTINGS, base)
    monkeypatch.setenv("KGME_CONDUCTOR", "hermes")
    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "summarise",
                               dirs=dirs, run_child=lambda a, e: 0)  # fmt: skip
    assert code == 0
    written = ledger.read(dirs)
    run = [e for e in written if e["job"] == "agent:run"]
    note = [e for e in written if e["job"] == "session"]
    assert len(run) == 2 and len(note) == 1
    assert all(e["summary"].endswith(MARK) for e in run + note)
    for event in (run[0], note[0]):
        payload = json.loads((base / event["payload_ref"]).read_text())
        assert payload["conductor"] == "hermes"
    assert ledger.open_intents(roles_run.JOB, dirs) == []


def test_agent_run_without_a_conductor_is_unmarked(tmp_path: Path) -> None:
    base = write_repo(tmp_path, {"build/reader": role_text("build", "reader")})
    (base / "CLAUDE.md").write_text("# fixture\n")
    dirs = ledger.read_test_dirs(SETTINGS, base)
    roles_run.run_agent(base, make_run_settings(), "build.reader", "summarise", dirs=dirs,
                        run_child=lambda a, e: 0)  # fmt: skip
    assert not any("conductor" in e["summary"] for e in ledger.read(dirs))


def test_loop_and_crew_events_carry_the_conductor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KGME_CONDUCTOR", "hermes")
    run = SimpleNamespace(handoff="HANDOFF-9999", run=events.new_ulid())
    looped = loop._loop_event("note", run, None, "loop started")
    crewed = crew_io._event("HANDOFF-9999", events.new_ulid(), "note", "crew:x", None, "planned")
    for event in (looped, crewed):
        events.validate_event(event)
        assert event["summary"].endswith(MARK)


@pytest.mark.blocking
def test_a_conductor_terminal_cannot_approve() -> None:
    assert approve.read_agent({"KGME_CONDUCTOR": "hermes"}) == "KGME_CONDUCTOR"


@pytest.mark.blocking
def test_the_conductor_role_lints_clean_and_answers_to_michou() -> None:
    rel = "roles/conductor/hermes.toml"
    findings = [f for f in roles_io.read_findings(ROOT, SETTINGS) if f.path.startswith(
        "roles/conductor/")]  # fmt: skip
    assert [f.line() for f in findings if f.cls == "blocking"] == []
    every = roles_io.read_role_files(ROOT)
    path, data = every["conductor.hermes"]
    assert path == rel and data["kind"] == "manager" and data["escalates_to"] == "michou"
    assert roles.chain("conductor.hermes", roles_io.read_roles(ROOT)) == (
        ["conductor.hermes", "michou"], None)  # fmt: skip
    assert (ROOT / "skills" / str(data["skill"]) / "SKILL.md").is_file()
