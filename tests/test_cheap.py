"""Tests for the cheap lane (HANDOFF-0053), with `claude` replaced by a stand-in.

Purpose: the deterministic half of the acceptance test. A `code` model runs only as
`kgme session work --model cheap --red ...`; the export holds no `memory/` (bar
`memory/templates/`) or `logs/`, and no history of them; the settings deny the brain, the
design worktree, `~/Projects/Finance`, and the Tier 1 roots at the permission and sandbox
layers, deny Bash network, and run the guard and ledger hooks from the main checkout's code;
the fix comes home as `fix.patch`, which applies in the main checkout; the start and end
notes are in its ledger. The hook and guard checks against the real code are in
`tests/test_cheap_live.py`, the review cycles' regressions in `tests/test_cheap_review.py`
(split by HANDOFF-0060 §3, moves only), the live cells in `tests/policy/test_agents_cheap.py`.
Inputs: `tmp_path`; the fixture checkout of `tests/sessiontools.py`; the template draft.
Outputs: pytest assertions.
Side effects: repositories, exports, and streams under `tmp_path`; nothing is launched.
"""

import json
import subprocess
from pathlib import Path

import pytest
from cheaptools import RED, read_session_notes, run_fixing, run_out, write_cheap_checkout
from sessiontools import run_git

from kgme import cheap, ledger, session


@pytest.mark.blocking
@pytest.mark.parametrize(
    "level,handoff,red,why",
    [
        ("work", None, None, "needs --red"),
        ("tight", None, RED, "runs only as"),
        ("loose", "HANDOFF-9047", RED, "runs only as"),
    ],
)
def test_a_code_model_runs_only_through_the_cheap_lane(
    tmp_path: Path, capsys, level, handoff, red, why
) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    code = session.run_session(
        level, handoff, [], base, settings, model_key="cheap", red=red,
        run_claude=run_fixing, execute=lambda *a: pytest.fail("launched"),
    )  # fmt: skip
    assert code == 2 and why in capsys.readouterr().err


@pytest.mark.blocking
def test_red_without_a_code_model_and_a_code_builder_are_refused(tmp_path: Path, capsys) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    assert session.run_session("work", None, [], base, settings, red=RED) == 2
    assert "needs --model" in capsys.readouterr().err
    settings["models"]["builder_provider"] = "ollama-cloud"
    assert session.run_session("work", None, [], base, settings) == 2
    assert "builder is a code-class model" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_export_holds_no_memory_or_logs_and_no_history_of_them(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    export, tree = cheap.write_export(base, settings, "R1")
    assert (export / "kgme" / "toy.py").is_file() and (
        export / "memory/templates/daily.md"
    ).is_file()
    assert not (export / "memory" / "notes").exists() and not (export / "logs").exists()
    listed = run_out(export, "log", "--all", "--name-only", "--format=", "--", "memory", "logs")
    assert set(listed.split()) == {"memory/templates/daily.md"}, "templates only, named"
    assert run_out(export, "rev-list", "--all", "--count") == "1"
    assert run_out(export, "rev-parse", "HEAD^{tree}") == tree


@pytest.mark.blocking
def test_the_settings_deny_the_roots_and_the_network_and_pin_the_hooks(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "R2")
    launch, record = cheap.read_cheap_launch("cheap", RED, base, settings, "R2", export)
    body = json.loads(launch.settings)
    deny, read_denied = body["permissions"]["deny"], body["sandbox"]["filesystem"]["denyRead"]
    for root in record["denied_roots"]:
        assert f"Read(/{root}/**)" in deny and f"Edit(/{root}/**)" in deny and root in read_denied
    assert str(base) in record["denied_roots"]
    assert str(Path.home() / "Projects" / "Finance") in record["denied_roots"]
    assert body["sandbox"]["network"] == {"allowedDomains": [], "strictAllowlist": True}
    assert {"WebFetch", "WebSearch"} <= set(deny)
    assert body["sandbox"]["filesystem"]["allowWrite"] == [str(export)]
    commands = [h["command"] for g in body["hooks"].values() for grp in g for h in grp["hooks"]]
    assert all(f'--project "{base}"' in c for c in commands) and len(commands) == 2
    assert launch.argv[:3] == ["claude", "--setting-sources", "local"]
    assert launch.argv[launch.argv.index("--model") + 1] == "toy-model:cloud"
    for slot in cheap.MODEL_SLOTS:
        assert launch.env[slot] == "toy-model:cloud"
    assert (
        launch.env["ANTHROPIC_BASE_URL"] == cheap.OLLAMA_URL
        and launch.env["ANTHROPIC_API_KEY"] == ""
    )
    assert "--max-budget-usd" not in launch.argv
    assert "tests/test_toy.py" in launch.claude_md.split("# Atlas slice")[1]


@pytest.mark.blocking
def test_the_fix_comes_home_as_a_patch_with_both_notes_in_the_main_ledger(
    tmp_path: Path, capsys
) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    code = session.run_session(
        "work", None, [], base, settings, model_key="cheap", red=RED, run_claude=run_fixing
    )
    assert code == 0, capsys.readouterr().err
    start, end = read_session_notes(base, settings)[-2:]
    assert start["key"] == "session:work" and end["key"] == "session:work:cheap:end"
    assert start["run_id"] == end["run_id"]
    begun = json.loads(ledger.read_payload(base, start)[0])
    assert begun["lane"] == "cheap" and begun["provider"] == "ollama-cloud" and begun["red"] == RED
    assert begun["export_tree"] and begun["denied_roots"]
    ended = json.loads(ledger.read_payload(base, end)[0])
    assert ended["red_status"] == 0 and ended["turns"] == 3 and ended["exit_reason"] == "success"
    patch = base / ended["patch"]
    assert "a + b" in patch.read_text()
    worktree = tmp_path / "apply"
    run_git(base, "worktree", "add", "-q", "--detach", str(worktree))
    subprocess.run(["git", "apply", str(patch)], cwd=worktree, check=True)
    assert subprocess.run(["python3", "tests/test_toy.py"], cwd=worktree).returncode == 0
    assert "a - b" in (base / "kgme" / "toy.py").read_text(), "the main checkout untouched"


@pytest.mark.blocking
def test_a_session_that_does_not_go_green_exits_one_with_its_patch(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)

    def run_failing(argv, cwd, env, **_):
        reply = {"type": "result", "subtype": "error_max_turns", "num_turns": 60}
        return subprocess.CompletedProcess(argv, 1, json.dumps(reply), "")

    assert session.run_session(
        "work", None, [], base, settings, model_key="cheap", red=RED, run_claude=run_failing
    ) == 1  # fmt: skip
    ended = json.loads(ledger.read_payload(base, read_session_notes(base, settings)[-1])[0])
    assert ended["exit_reason"] == "error_max_turns" and ended["red_status"] == 1


@pytest.mark.blocking
def test_a_dry_run_builds_no_export(tmp_path: Path, capsys) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    code = session.run_session(
        "work", None, [], base, settings, dry_run=True, model_key="cheap", red=RED
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "--model toy-model:cloud" in out and "--- carried: CLAUDE.md, slice ---" in out
    assert not (tmp_path / "work").exists()


@pytest.mark.blocking
def test_the_red_files_seed_the_slice_and_name_the_test_not_to_edit() -> None:
    red = "uv run --frozen pytest tests/fixtures/cheap/toy_red.py::test_add_sums -q"
    assert cheap.read_red_files(red) == ["tests/fixtures/cheap/toy_red.py"]
    assert "without editing `tests/fixtures/cheap/toy_red.py`" in cheap.build_prompt(red)
