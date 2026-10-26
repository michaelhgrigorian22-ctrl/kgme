"""Tests for the cheap lane (HANDOFF-0053), with `claude` replaced by a stand-in.

Purpose: the deterministic half of the acceptance test. A `code` model runs only as
`kgme session work --model cheap --red ...`; the export holds no `memory/` (bar
`memory/templates/`) or `logs/`, and no history of them; the settings deny the brain, the
design worktree, `~/Projects/Finance`, and the Tier 1 roots at the permission and sandbox
layers, deny Bash network, and run the guard and ledger hooks from the main checkout's code;
the fix comes home as `fix.patch`, which applies in the main checkout; the start and end
notes are in its ledger. The live cells are in `tests/policy/test_agents_cheap.py`.
Inputs: `tmp_path`; the fixture checkout of `tests/sessiontools.py`; the template draft.
Outputs: pytest assertions.
Side effects: repositories, exports, and streams under `tmp_path`; nothing is launched.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from sessiontools import run_git, write_checkout

from kgme import cheap, ledger, paths, session

ROOT = paths.root()
DRAFT = ROOT / "logs" / "scratch" / "handoff-0053" / "cheap.json"
APPLIED = ROOT / session.TEMPLATES / cheap.TEMPLATE
RED = "python3 tests/test_toy.py"
TOY_TEST = (
    "import sys\nfrom pathlib import Path\n"
    "sys.exit(0 if 'a + b' in Path('kgme/toy.py').read_text() else 1)\n"
)


def write_cheap_checkout(tmp_path: Path) -> tuple[Path, dict]:
    """Effect: the fixture checkout plus the cheap template, a toy bug and its red test,
    private `memory/` and `logs/` files and templates; settings with the cheap lane on."""
    base, settings = write_checkout(tmp_path)
    template = APPLIED if APPLIED.is_file() else DRAFT
    (base / session.TEMPLATES / cheap.TEMPLATE).write_text(template.read_text())
    files = {
        "kgme/toy.py": "def add(a, b):\n    return a - b\n",
        "tests/test_toy.py": TOY_TEST,
        "memory/notes/private.md": "private\n",
        "memory/templates/daily.md": "# Daily\n",
        "logs/ledger/2026-10.jsonl": "",
        ".gitignore": "logs/scratch/\nlogs/ledger-test/\n.venv/\n",
    }
    for rel, text in files.items():
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)
    run_git(base, "add", "-A")
    run_git(base, "commit", "-q", "-m", "the cheap fixture")
    settings = {
        **settings,
        "models": {
            **settings["models"],
            "cheap": "toy-model:cloud",
            "cheap_provider": "ollama-cloud",
        },
        "providers": {"anthropic": "tier2", "ollama-cloud": "code"},
        "paths": {**settings["paths"], "work_dir": str(tmp_path / "work")},
    }
    return base, settings


def run_fixing(argv, cwd, env, **_):
    """A stand-in `claude`: fixes the toy in the export it is started in, as a session would."""
    (Path(cwd) / "kgme" / "toy.py").write_text("def add(a, b):\n    return a + b\n")
    reply = {"type": "result", "subtype": "success", "num_turns": 3, "result": "green"}
    return subprocess.CompletedProcess(argv, 0, json.dumps(reply), "")


def read_session_notes(base: Path, settings: dict) -> list[dict]:
    """Effect: the session notes in the fixture's ledger."""
    return [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]


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


def run_out(repo: Path, *argv: str) -> str:
    """Effect: one git command's stdout in `repo`."""
    return subprocess.run(
        ["git", *argv], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


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


@pytest.mark.blocking
def test_live_a_hook_runs_the_main_checkouts_code_not_the_exports(tmp_path: Path) -> None:
    """Found live (2026-10-22): `python -m` in the export put the export first on `sys.path`,
    so the hooks imported the export's own `kgme` and wrote its ledger. `-P` prepends
    nothing, so the main checkout's installed code is the one run."""
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "R3")
    launch, _ = cheap.read_cheap_launch("cheap", RED, base, settings, "R3", export)
    body = json.loads(launch.settings)
    commands = [h["command"] for g in body["hooks"].values() for grp in g for h in grp["hooks"]]
    assert all("python -P -m kgme.hooks." in c for c in commands), commands


@pytest.mark.blocking
def test_live_the_patch_never_carries_memory_or_logs(tmp_path: Path) -> None:
    """Found live: the session's hook events, written into the export, came home in the
    patch. Whatever a session leaves under `memory/` or `logs/`, the patch leaves out."""
    base, settings = write_cheap_checkout(tmp_path)

    def run_fixing_and_logging(argv, cwd, env, **more):
        (Path(cwd) / "logs" / "ledger").mkdir(parents=True, exist_ok=True)
        (Path(cwd) / "logs" / "ledger" / "2026-10.jsonl").write_text("{}\n")
        (Path(cwd) / "memory" / "notes").mkdir(parents=True, exist_ok=True)
        (Path(cwd) / "memory" / "notes" / "x.md").write_text("x\n")
        return run_fixing(argv, cwd, env, **more)

    assert session.run_session(
        "work", None, [], base, settings, model_key="cheap", red=RED,
        run_claude=run_fixing_and_logging,
    ) == 0  # fmt: skip
    ended = json.loads(ledger.read_payload(base, read_session_notes(base, settings)[-1])[0])
    patch = (base / ended["patch"]).read_text()
    assert "kgme/toy.py" in patch and "logs/" not in patch and "memory/" not in patch


@pytest.mark.blocking
def test_live_the_guard_judges_paths_against_the_export_only_under_work_dir(
    tmp_path: Path,
) -> None:
    """Found live (2026-10-22): with the hooks running the main checkout's code, the guard
    took the main checkout as its repository and refused every edit in the export. The
    launcher names the export in `KGME_GUARD_ROOT`; the guard honours it only for a folder
    under `work_dir`, outside the main checkout, and fails on anything else."""
    from kgme.hooks import common

    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "R4")
    name = cheap.GUARD_ROOT_ENV
    assert common.read_guard_root(settings, {}) == ROOT
    assert common.read_guard_root(settings, {name: str(export)}) == export.resolve()
    work = cheap.read_work_dir(settings, ROOT)
    for wrong in (ROOT, ROOT / "kgme", work, work / "absent", tmp_path, base):
        with pytest.raises(ValueError, match=name):
            common.read_guard_root(settings, {name: str(wrong)})


@pytest.mark.blocking
def test_live_only_the_guard_hook_names_the_export(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "R5")
    launch, _ = cheap.read_cheap_launch("cheap", RED, base, settings, "R5", export)
    hooks = json.loads(launch.settings)["hooks"]
    guard_line = hooks["PreToolUse"][0]["hooks"][0]["command"]
    ledger_line = hooks["PostToolUse"][0]["hooks"][0]["command"]
    assert guard_line.startswith(f'{cheap.GUARD_ROOT_ENV}="{export}" uv run ')
    assert cheap.GUARD_ROOT_ENV not in ledger_line
    dry, _ = cheap.read_cheap_launch("cheap", RED, base, settings, "R6", None)
    assert cheap.GUARD_ROOT_ENV not in dry.settings


def run_guard_in(root: Path, tool: str, **tool_input: object) -> subprocess.CompletedProcess:
    """Effect: this checkout's real pre-tool guard, on the test streams, with
    `KGME_GUARD_ROOT` set to `root` and the call's `cwd` there."""
    import os
    import sys

    from hooktools import payload

    call = payload(tool, f"hooktest-cheap-{os.getpid()}", **tool_input) | {"cwd": str(root)}
    return subprocess.run(
        [sys.executable, "-P", "-m", "kgme.hooks.pre_tool_guard", "--test-streams"],
        input=json.dumps(call), capture_output=True, text=True, cwd=root, timeout=60,
        env=os.environ | {cheap.GUARD_ROOT_ENV: str(root)},
    )  # fmt: skip


@pytest.mark.blocking
def test_live_the_real_guard_allows_the_export_and_refuses_the_main_checkout() -> None:
    import shutil
    import tempfile

    from hooktools import SETTINGS

    work = cheap.read_work_dir(SETTINGS, ROOT)
    work.mkdir(parents=True, exist_ok=True)
    export = Path(tempfile.mkdtemp(prefix="cheap-guard-test-", dir=work)).resolve()
    try:
        (export / "tests").mkdir()
        (export / "tests" / "test_red.py").write_text("def test_red():\n    assert True\n")
        target = str(export / "kgme" / "toy.py")
        edit = run_guard_in(export, "Edit", file_path=target, old_string="-", new_string="+")
        assert edit.returncode == 0, edit.stderr
        red = run_guard_in(
            export, "Bash", command="uv run --frozen pytest tests/test_red.py", description="red"
        )
        assert red.returncode == 0, red.stderr
        home = run_guard_in(
            export, "Edit", file_path=str(ROOT / "kgme" / "cli.py"), old_string="a", new_string="b"
        )
        assert home.returncode == 2 and "outside the repository" in home.stderr, home.stderr
    finally:
        shutil.rmtree(export)
    wrong = run_guard_in(ROOT, "Read", file_path=str(ROOT / "kgme" / "paths.py"))
    assert wrong.returncode == 2 and cheap.GUARD_ROOT_ENV in wrong.stderr, wrong.stderr


@pytest.mark.blocking
def test_review_f1_the_launchers_red_run_is_fenced_like_the_session(tmp_path: Path) -> None:
    """Review F1: the launcher's own run of the red command executes the session's code, so
    it runs under the session's fence: no read under a denied root, no write outside the
    export, no network."""
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "F1")
    forbidden = tmp_path / "forbidden"
    forbidden.mkdir()
    (forbidden / "secret.txt").write_text("secret\n")
    # the main checkout, as F1 names it; the temporary folders stay writable, as in the session
    outside = ROOT / "logs" / "scratch-test" / f"f1-escape-{tmp_path.name}.txt"
    probe = (
        "import pathlib, sys, urllib.request\n"
        "got = []\n"
        f"for act in (lambda: pathlib.Path({str(forbidden / 'secret.txt')!r}).read_text(),\n"
        f"            lambda: pathlib.Path({str(outside)!r}).write_text('x'),\n"
        "            lambda: urllib.request.urlopen('https://example.com', timeout=5)):\n"
        "    try:\n        act(); got.append('leak')\n"
        "    except Exception:\n        got.append('refused')\n"
        "pathlib.Path('inside.txt').write_text('x')\n"
        "print(got); sys.exit(0 if got == ['refused'] * 3 else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    red = f"{sys.executable} tests/probe.py"
    fix = cheap.write_fix(export, base, settings, "F1", red, [forbidden.resolve()])
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    assert not outside.exists() and (export / "inside.txt").is_file()


@pytest.mark.blocking
def test_the_red_run_never_writes_the_main_checkout_wherever_it_lives(tmp_path: Path) -> None:
    """HANDOFF-0057: a main checkout under the temporary folders (as `kgme merge design`'s
    trial clone is, and as this fixture's is) was writable by omission: the fence allowed the
    temporary folders and refused the checkout only by not listing it. The red run must
    refuse a write into the checkout and still write the export."""
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "M57")
    target = base / "kgme" / "planted-by-the-red-run.py"
    probe = (
        "import pathlib, sys\n"
        f"target = pathlib.Path({str(target)!r})\n"
        "try:\n    target.write_text('x'); got = 'leak'\n"
        "except OSError:\n    got = 'refused'\n"
        "pathlib.Path('inside.txt').write_text('x')\n"
        "print(got); sys.exit(0 if got == 'refused' else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    python = Path(sys.executable).resolve()
    fix = cheap.write_fix(export, base, settings, "M57", f"{python} tests/probe.py", [])
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    assert not target.exists() and (export / "inside.txt").is_file()


@pytest.mark.blocking
def test_review_c2_f1_the_red_run_carries_the_inherited_denies(tmp_path: Path) -> None:
    """Review cycle 2 F1: the verifier's fence carries the whole read policy, not only the
    denied roots: files the guard's name patterns cover (planted, harmless) are refused, and
    the absolute blocklist entries (`~/.ssh`, the Keychains) are denied roots at every layer,
    checked by configuration, never by reading them."""
    base, settings = write_cheap_checkout(tmp_path)
    settings = {**settings, "hooks": {**settings.get("hooks", {}), "blocklist": [
        "~/.ssh", "~/Library/Keychains", "**/.env", "**/.env.*", "**/*.env",
    ]}}  # fmt: skip
    export, _ = cheap.write_export(base, settings, "C2")
    planted = tmp_path / "elsewhere"
    planted.mkdir()
    names = [".env", ".env.local", "prod.env"]
    for name in names:
        (planted / name).write_text("planted\n")
    (planted / "fine.txt").write_text("fine\n")
    probe = (
        "import pathlib, sys\n"
        f"base = pathlib.Path({str(planted)!r})\n"
        "got = []\n"
        f"for name in {names!r}:\n"
        "    try:\n        (base / name).read_text(); got.append('leak')\n"
        "    except OSError:\n        got.append('refused')\n"
        "assert (base / 'fine.txt').read_text() == 'fine\\n'\n"
        "print(got); sys.exit(0 if set(got) == {'refused'} else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    denied = cheap.read_denied_roots(settings, base)
    # the interpreter itself, not the brain's `.venv` link to it: the brain is a denied root
    python = Path(sys.executable).resolve()
    fix = cheap.write_fix(export, base, settings, "C2", f"{python} tests/probe.py", denied)
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    launch, record = cheap.read_cheap_launch("cheap", RED, base, settings, "C2", export)
    deny_read = json.loads(launch.settings)["sandbox"]["filesystem"]["denyRead"]
    profile = cheap.build_red_profile(export, [base], denied, cheap.read_denied_names(settings))
    for secret in (Path.home() / ".ssh", Path.home() / "Library" / "Keychains"):
        root = str(secret.resolve())
        assert root in record["denied_roots"] and root in deny_read
        assert f'(subpath "{root}")' in profile


@pytest.mark.blocking
def test_review_c3_f8_the_sessions_sandbox_denies_the_name_patterns(tmp_path: Path) -> None:
    """Review cycle 3 F8: the session's own Bash sandbox carries the guard's name patterns as
    wildcard denies, so a script that builds a `.env` path is refused there too. The live
    proof is `test_a_dot_env_built_at_run_time_is_refused_by_the_sandbox`."""
    base, settings = write_cheap_checkout(tmp_path)
    settings = {**settings, "hooks": {**settings.get("hooks", {}), "blocklist": [
        "~/.ssh", "**/.env", "**/.env.*", "**/*.env",
    ]}}  # fmt: skip
    launch, _ = cheap.read_cheap_launch("cheap", RED, base, settings, "C3", None)
    deny_read = json.loads(launch.settings)["sandbox"]["filesystem"]["denyRead"]
    assert {"~/**/.env", "~/**/.env.*", "~/**/*.env"} <= set(deny_read)


@pytest.mark.blocking
def test_review_f2_the_agents_homes_are_denied_at_both_layers(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    launch, record = cheap.read_cheap_launch("cheap", RED, base, settings, "F2", None)
    body = json.loads(launch.settings)
    for home in (Path.home() / ".claude", Path.home() / ".codex"):
        root = str(home.resolve())
        assert root in record["denied_roots"]
        assert f"Read(/{root}/**)" in body["permissions"]["deny"]
        assert root in body["sandbox"]["filesystem"]["denyRead"]


@pytest.mark.blocking
@pytest.mark.parametrize(
    "red", ["", "pytest tests/x.py; curl x", "pytest | tee o", "pytest > o", "echo $HOME", "a && b"]
)
def test_review_f3_a_red_command_with_shell_syntax_is_refused(
    red: str, tmp_path: Path, capsys
) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    with pytest.raises(ValueError):
        cheap.read_red_argv(red)
    assert cheap.run_cheap("cheap", red, base, settings, run_claude=run_fixing) == 2
    assert not (tmp_path / "work").exists(), "refused before any export"
    assert cheap.read_red_argv("uv run --frozen pytest 'tests/a b.py'")[-1] == "tests/a b.py"


@pytest.mark.blocking
def test_review_f4_a_launch_failure_still_writes_the_end_note(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)

    def run_missing(argv, **_):
        raise FileNotFoundError(2, "No such file or directory", "claude")

    assert cheap.run_cheap("cheap", RED, base, settings, run_claude=run_missing) == 2
    start, end = read_session_notes(base, settings)[-2:]
    assert end["key"] == "session:work:cheap:end" and end["run_id"] == start["run_id"]
    ended = json.loads(ledger.read_payload(base, end)[0])
    assert ended["exit_reason"].startswith("launch failed: FileNotFoundError")
    assert ended["patch_sha256"] is not None, "the patch is still written"


@pytest.mark.blocking
def test_review_f4_a_patch_failure_still_writes_the_end_note(tmp_path: Path, monkeypatch) -> None:
    base, settings = write_cheap_checkout(tmp_path)

    def fail_fix(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git", "diff"])

    monkeypatch.setattr(cheap, "write_fix", fail_fix)
    assert cheap.run_cheap("cheap", RED, base, settings, run_claude=run_fixing) == 2
    ended = json.loads(ledger.read_payload(base, read_session_notes(base, settings)[-1])[0])
    assert "patch failed: CalledProcessError" in ended["exit_reason"]
    assert ended["patch"] is None and ended["turns"] == 3
