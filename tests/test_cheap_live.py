"""Tests for the cheap lane's hooks and guard against this checkout's real code (HANDOFF-0053;
moved out of `tests/test_cheap.py` by HANDOFF-0060 §3, unchanged).

Purpose: a hook runs the main checkout's code, not the export's; the patch never carries
`memory/` or `logs/`; the guard judges paths against the export only under `KGME_GUARD_ROOT`;
only the guard hook names the export; the real guard allows the export and refuses the main
checkout.
Inputs: `tmp_path`; this checkout's guard.
Outputs: pytest assertions.
Side effects: repositories and streams under `tmp_path` and the test streams.
"""

import json
from pathlib import Path

import pytest
from cheaptools import RED, ROOT, read_session_notes, run_fixing, run_guard_in, write_cheap_checkout

from kgme import cheap, ledger, session


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
        main = ledger.read_main_checkout(ROOT)  # this checkout, or the worktree's main one
        home = run_guard_in(
            export, "Edit", file_path=str(main / "kgme" / "cli.py"), old_string="a", new_string="b"
        )
        assert home.returncode == 2 and "outside the repository" in home.stderr, home.stderr
    finally:
        shutil.rmtree(export)
    wrong = run_guard_in(ROOT, "Read", file_path=str(ROOT / "kgme" / "paths.py"))
    assert wrong.returncode == 2 and cheap.GUARD_ROOT_ENV in wrong.stderr, wrong.stderr
