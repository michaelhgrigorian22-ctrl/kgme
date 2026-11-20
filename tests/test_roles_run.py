"""Tests for `kgme agent run` (HANDOFF-0071 §3, AUDIT-0173 F1-F4).

Purpose: a run writes `agent:run` intent and outcome events carrying the role id, the outcome
`ref`s its intent so no run is left open, whatever its end; the launch itself narrows the
level to the role's tools (`--tools`, the run copy's allow and deny), and a restriction the
launch cannot express is refused by name; a `cheap` role never runs; a role that fails lint
never runs; preparation, launch and interruption failures are classified outcomes.
Inputs: fixture checkouts from `tests/roletools.py`; a recorder in place of `claude`.
Outputs: pytest assertions.
Side effects: repositories and test streams under `tmp_path`; nothing is launched.
"""

import json
from pathlib import Path

import pytest
from roletools import SETTINGS, make_run_settings, role_text, write_file, write_repo

from kgme import ledger, roles_run

TASK = "summarise the last crew run"


def write_fixture(tmp_path: Path, roles_: dict[str, str]) -> tuple[Path, ledger.Dirs]:
    """Effect: a fixture checkout with `roles_` and a CLAUDE.md, and its test ledger."""
    base = write_repo(tmp_path, roles_)
    (base / "CLAUDE.md").write_text("# fixture\n")
    return base, ledger.read_test_dirs(SETTINGS, base)


def read_run_events(dirs: ledger.Dirs) -> list[dict]:
    """Effect: the `agent:run` events of the test ledger."""
    return [e for e in ledger.read(dirs) if e["job"] == "agent:run"]


def read_settings_copy(base: Path, dirs: ledger.Dirs) -> tuple[dict, dict]:
    """Effect: the run copy the launch wrote, parsed, and the session note's payload."""
    note = [e for e in ledger.read(dirs) if e["job"] == "session"][-1]
    payload = json.loads((base / note["payload_ref"]).read_text())
    return json.loads((base / payload["settings"]).read_text()), payload


# --- the ledger (F1) ---------------------------------------------------------------------


@pytest.mark.blocking
def test_run_writes_intent_and_outcome_events_carrying_the_role_id(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader",
                                                                    model="strong")})  # fmt: skip
    calls: list[tuple[list[str], dict]] = []

    def child(argv: list[str], env: dict) -> int:
        calls.append((argv, env))
        return 0

    code = roles_run.run_agent(base, make_run_settings(), "build.reader", TASK, dirs=dirs,
                               run_child=child)  # fmt: skip
    assert code == 0 and len(calls) == 1
    argv, env = calls[0]
    assert argv[argv.index("--model") + 1] == "claude-opus-5-5"
    assert argv[argv.index("--permission-mode") + 1] == "plan"
    assert argv[-1] == TASK
    prompt = Path(argv[argv.index("--append-system-prompt-file") + 1]).read_text()
    assert "build.reader" in prompt and "# kgme-fixture" in prompt
    intent, outcome = read_run_events(dirs)
    assert intent["kind"] == "intent" and outcome["kind"] == "outcome"
    assert intent["key"] == outcome["key"] == "agent:build.reader"
    assert "build.reader" in intent["summary"] and "build.reader" in outcome["summary"]
    assert outcome["parent"] == outcome["ref"] == intent["id"] and outcome["status"] == "ok"
    assert env["KGME_LOOP_PARENT"] == intent["id"]  # the session's own events nest under it
    _, payload = read_settings_copy(base, dirs)
    assert payload["role"] == "build.reader"
    assert ledger.open_intents(roles_run.JOB, dirs) == []


@pytest.mark.blocking
def test_a_failed_run_is_a_closed_error_outcome_and_print_is_tight_only(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {
        "build/reader": role_text("build", "reader"),
        "build/worker": role_text("build", "worker", level="work", tools=["Read"]),
    })  # fmt: skip
    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                               run_child=lambda a, e: 3, headless=True)  # fmt: skip
    assert code == 3
    outcome = read_run_events(dirs)[-1]
    assert outcome["status"] == "error" and outcome["class"] == "blocking"
    assert ledger.open_intents(roles_run.JOB, dirs) == []
    refused = roles_run.run_agent(base, make_run_settings(), "build.worker", "x", dirs=dirs,
                                  run_child=lambda a, e: 0, headless=True)  # fmt: skip
    assert refused == 2
    assert roles_run.run_agent(base, make_run_settings(), "build.none", "x", dirs=dirs) == 2


@pytest.mark.blocking
def test_a_role_that_fails_lint_never_runs(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader",
                                                                    tools=["Bash"])})  # fmt: skip
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 2 and calls == [] and read_run_events(dirs) == []


# --- the launch narrows the level (F2) ---------------------------------------------------


@pytest.mark.blocking
def test_the_launch_narrows_a_work_level_to_the_roles_tools(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/worker": role_text("build", "worker",
                                                                    level="work",
                                                                    tools=["Read"])})  # fmt: skip
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.worker", TASK, dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 0
    argv = calls[0]
    assert argv[argv.index("--tools") + 1] == "Read"
    assert "--strict-mcp-config" in argv and argv[-1] == TASK
    copy, payload = read_settings_copy(base, dirs)
    deny = set(copy["permissions"]["deny"])
    assert {"Edit", "Write", "Bash", "Agent", "WebFetch", "WebSearch", "Grep"} <= deny
    assert "Read" not in deny
    assert all(rule.split("(")[0] == "Read" for rule in copy["permissions"].get("allow", []))
    text = (base / payload["settings"]).read_text()
    assert payload["settings_sha256"] == roles_run.session.sha256_text(text)


@pytest.mark.blocking
def test_the_launch_drops_level_allow_rules_the_role_does_not_list(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader",
                                                                    tools=["Read"])})  # fmt: skip
    write_file(base, "control/policy/sessions/tight.json", json.dumps({"permissions": {
        "allow": ["Read", "Grep", "Bash(git status *)"], "deny": ["WebFetch"]}}))  # fmt: skip
    calls: list[list[str]] = []
    assert roles_run.run_agent(base, make_run_settings(), "build.reader", TASK, dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0) == 0  # fmt: skip
    copy, _ = read_settings_copy(base, dirs)
    assert copy["permissions"]["allow"] == ["Read"]
    assert {"WebFetch", "Grep", "Bash"} <= set(copy["permissions"]["deny"])


@pytest.mark.blocking
@pytest.mark.parametrize(
    "fields,profile,needle",
    [
        ({"level": "work", "tools": ["Bash(git diff *)"]}, None, "scoped rule"),
        ({"profile": "fenced", "tools": ["Read"]}, "fenced", "profile `fenced`"),
    ],
)
def test_a_restriction_the_launch_cannot_express_is_refused(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fields: dict,
    profile: str | None,
    needle: str,
) -> None:
    base, dirs = write_fixture(tmp_path, {"build/worker": role_text("build", "worker",
                                                                    **fields)})  # fmt: skip
    if profile:
        write_file(base, f"control/policy/profiles/{profile}.toml",
                   'tools = ["Read"]\nmax_tier = 2\nwrite_paths = ["docs"]\n')  # fmt: skip
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.worker", "x", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 2 and calls == [] and read_run_events(dirs) == []
    assert needle in capsys.readouterr().err


@pytest.mark.blocking
def test_the_levels_own_profile_at_work_is_expressed(tmp_path: Path) -> None:
    role = role_text("build", "worker", level="work", profile="claude-builder", tools=["Read"])
    base, dirs = write_fixture(tmp_path, {"build/worker": role})
    calls: list[list[str]] = []
    assert roles_run.run_agent(base, make_run_settings(), "build.worker", "x", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0) == 0  # fmt: skip
    assert calls[0][calls[0].index("--tools") + 1] == "Read"


@pytest.mark.blocking
@pytest.mark.parametrize("tool", ["Read,NotebookEdit", "Read NotebookEdit", "Bash(git diff *)"])
def test_a_tool_that_is_not_one_bare_name_never_launches(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], tool: str
) -> None:
    role = role_text("build", "worker", level="work", tools=["Read", tool])
    base, dirs = write_fixture(tmp_path, {"build/worker": role})
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.worker", "x", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 2 and calls == [] and read_run_events(dirs) == []
    assert "is not one bare tool name" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_launch_refuses_a_malformed_tool_without_lint() -> None:
    data = {"level": "work", "tools": ["Read", "Read,NotebookEdit"]}
    why = roles_run.launch_refusal(data, None, "work", "claude-builder", frozenset({"Read"}))
    assert why is not None and "is not one bare tool name" in why


# --- the source path selects the findings (AUDIT-0174 F8) --------------------------------


@pytest.mark.blocking
@pytest.mark.parametrize(
    "fields,needle", [({"tier_max": 1}, "Tier 1"), ({"tools": ["Bash"]}, "`Bash` is not allowed")]
)
def test_a_role_whose_id_is_not_its_path_never_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fields: dict, needle: str
) -> None:
    role = role_text("build", "reader", id="build.alias", **fields)
    base, dirs = write_fixture(tmp_path, {"build/reader": role})
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.alias", "x", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 2 and calls == [] and read_run_events(dirs) == []
    err = capsys.readouterr().err
    assert "roles/build/reader.toml" in err and needle in err
    assert "id `build.alias` is not `build.reader`" in err


# --- cheap is not a role level (F3) ------------------------------------------------------


@pytest.mark.blocking
def test_a_cheap_role_never_runs(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cheap = role_text("build", "red", level="cheap", model="cheap", tools=["Read"], tier_max=3)
    base, dirs = write_fixture(tmp_path, {"build/red": cheap})
    calls: list[list[str]] = []
    code = roles_run.run_agent(base, make_run_settings(), "build.red", "make test", dirs=dirs,
                               run_child=lambda a, e: calls.append(a) or 0)  # fmt: skip
    assert code == 2 and calls == [] and read_run_events(dirs) == []
    assert "not a role level" in capsys.readouterr().err
    assert not hasattr(roles_run, "run_cheap_role")


# --- every intent gets an outcome (F4) ---------------------------------------------------


@pytest.mark.blocking
def test_a_preparation_failure_closes_the_intent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader")})

    def broken(*args: object, **kwargs: object) -> dict:
        raise OSError("disk full")

    monkeypatch.setattr(roles_run.session, "write_start", broken)
    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                               run_child=lambda a, e: 0)  # fmt: skip
    assert code == 2
    outcome = read_run_events(dirs)[-1]
    assert outcome["status"] == "error" and outcome["class"] == "blocking"
    assert "preparation" in outcome["summary"] and "disk full" in outcome["summary"]
    assert ledger.open_intents(roles_run.JOB, dirs) == []


@pytest.mark.blocking
def test_a_launch_failure_closes_the_intent(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader")})

    def missing(argv: list[str], env: dict) -> int:
        raise FileNotFoundError(2, "No such file or directory", "claude")

    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                               run_child=missing)  # fmt: skip
    assert code == 2
    outcome = read_run_events(dirs)[-1]
    assert outcome["status"] == "error" and outcome["class"] == "blocking"
    assert "launch" in outcome["summary"] and "FileNotFoundError" in outcome["summary"]
    assert ledger.open_intents(roles_run.JOB, dirs) == []


@pytest.mark.blocking
def test_an_interruption_closes_the_intent(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader")})

    def interrupted(argv: list[str], env: dict) -> int:
        raise KeyboardInterrupt

    code = roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                               run_child=interrupted)  # fmt: skip
    assert code == 130
    outcome = read_run_events(dirs)[-1]
    assert outcome["status"] == "error" and outcome["class"] == "transient"
    assert "interrupted" in outcome["summary"]
    assert ledger.open_intents(roles_run.JOB, dirs) == []


@pytest.mark.blocking
def test_an_unexpected_error_closes_the_intent_and_is_raised(tmp_path: Path) -> None:
    base, dirs = write_fixture(tmp_path, {"build/reader": role_text("build", "reader")})

    def bug(argv: list[str], env: dict) -> int:
        raise RuntimeError("a bug")

    with pytest.raises(RuntimeError, match="a bug"):
        roles_run.run_agent(base, make_run_settings(), "build.reader", "x", dirs=dirs,
                            run_child=bug)  # fmt: skip
    outcome = read_run_events(dirs)[-1]
    assert outcome["status"] == "error" and "RuntimeError" in outcome["summary"]
    assert ledger.open_intents(roles_run.JOB, dirs) == []
