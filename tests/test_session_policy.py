"""Tests for the policy `kgme session loose` carries (HANDOFF-0047 review cycle 2 F1).

Purpose: the arbitration of F1 (two arbiters, option C): the main checkout's hooks, their
commands naming its scripts by absolute path, and its deny list go into the run copy passed with
`--settings`, so a workspace's own project settings can add rules but never remove the guard or
a deny; a workspace that disables hooks is refused; the start note hashes the carried policy.
Inputs: fixture checkouts and worktrees from `tests/sessiontools.py`.
Outputs: pytest assertions.
Side effects: repositories, worktrees, and streams under `tmp_path`; nothing is launched.
"""

import json
from pathlib import Path

import pytest
from sessiontools import GUARDED, launched, run_git, write_checkout, write_workspace

from kgme import ledger


def write_policy_checkout(tmp_path: Path) -> tuple[Path, dict, Path]:
    """Effect: a fixture checkout whose committed settings run the guard and deny two rules,
    and a worktree of it, byte-identical, as a fresh KGME workspace is."""
    base, settings = write_checkout(tmp_path)
    policy = {**GUARDED, "permissions": {"deny": ["Bash(rm -rf *)", "Edit(/control/**)"]}}
    (base / ".claude" / "settings.json").write_text(json.dumps(policy))
    run_git(base, "commit", "-q", "-am", "policy")
    return base, settings, write_workspace(base, tmp_path)


@pytest.mark.blocking
def test_c2_f1_the_run_copy_carries_the_main_checkouts_guard_and_denies(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 2 F1, the in-loop arbiters' option C: the main checkout's hooks, their
    commands naming its scripts by absolute path, and its deny list go into the run copy."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    monkeypatch.chdir(workspace)
    code, calls = launched(base, settings, "loose", "HANDOFF-9047")
    assert code == 0
    rendered = json.loads(Path(calls[0][1][4]).read_text())
    [group] = [g for g in rendered["hooks"]["PreToolUse"] if g["matcher"] == ""]
    assert group["hooks"][0]["command"] == f"{base}/control/hooks/pre_tool_guard.sh"
    assert {"Bash(rm -rf *)", "Edit(/control/**)"} <= set(rendered["permissions"]["deny"])
    assert rendered["disableAllHooks"] is False


@pytest.mark.blocking
@pytest.mark.parametrize(
    "changed",
    [
        {"note": "pre_tool_guard"},
        {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "true"}]}
                ]
            }
        },
        {**GUARDED, "permissions": {"deny": ["Bash(rm -rf *)"]}},
    ],
    ids=["inert-guard-string", "nonmatching-hook", "missing-deny-rule"],
)
def test_cowork_f1_a_workspace_whose_settings_differ_is_refused(
    tmp_path: Path, monkeypatch, capsys, changed: dict
) -> None:
    """Cowork's ruling on F1 (2026-10-21): identity. `loose` starts only when the workspace's
    `.claude/settings.json` is byte-identical to the main checkout's committed one."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    (workspace / ".claude" / "settings.json").write_text(json.dumps(changed))
    monkeypatch.chdir(workspace)
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    assert "byte-identical" in capsys.readouterr().err


@pytest.mark.blocking
@pytest.mark.parametrize("where", ["workspace", "main"])
def test_cowork_f1_a_local_allow_rule_is_refused(
    tmp_path: Path, monkeypatch, capsys, where: str
) -> None:
    """`--setting-sources project,local` loads `.claude/settings.local.json`, and a worktree
    session reads the main root's; one holding allow rules widens the level."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    root = workspace if where == "workspace" else base
    (root / ".claude" / "settings.local.json").write_text(
        json.dumps({"permissions": {"allow": ["Bash(*)"]}})
    )
    monkeypatch.chdir(workspace)
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    assert "settings.local.json" in capsys.readouterr().err


@pytest.mark.blocking
def test_cowork_f1_an_identical_workspace_is_accepted(tmp_path: Path, monkeypatch) -> None:
    base, settings, workspace = write_policy_checkout(tmp_path)
    monkeypatch.chdir(workspace)
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 0


@pytest.mark.blocking
def test_c2_f1_a_workspace_that_disables_hooks_is_refused(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A workspace's `settings.json` that disables hooks is no longer identical (Cowork's
    ruling); a `settings.local.json` that does is refused in its own words."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    monkeypatch.chdir(workspace)
    project = workspace / ".claude" / "settings.json"
    committed = project.read_text()
    project.write_text(json.dumps({"disableAllHooks": True}))
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    assert "byte-identical" in capsys.readouterr().err
    project.write_text(committed)
    (workspace / ".claude" / "settings.local.json").write_text(
        json.dumps({"disableAllHooks": True})
    )
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    assert "disables hooks" in capsys.readouterr().err


def read_carried(base: Path, settings: dict, workspace: Path, monkeypatch) -> dict:
    """Effect: a loose launch from `workspace`; its start note's record and its run copy."""
    monkeypatch.chdir(workspace)
    code, calls = launched(base, settings, "loose", "HANDOFF-9047")
    assert code == 0
    found = [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]
    record = json.loads(ledger.read_payload(base, found[-1])[0])
    return {**record, "rendered": json.loads(Path(calls[0][1][4]).read_text())}


@pytest.mark.blocking
def test_c2_f1_the_start_note_hashes_the_carried_policy(tmp_path: Path, monkeypatch) -> None:
    """A committed change to the main checkout's deny list changes the carried policy's hash."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    first = read_carried(base, settings, workspace, monkeypatch)["policy_sha256"]
    (base / ".claude" / "settings.json").write_text(
        json.dumps({**GUARDED, "permissions": {"deny": ["Bash(rm -rf *)"]}})
    )
    run_git(base, "commit", "-q", "-am", "narrower")
    again = write_workspace(base, tmp_path / "second")
    second = read_carried(base, settings, again, monkeypatch)["policy_sha256"]
    assert first != second, "a committed change to the deny list changes the carried hash"


@pytest.mark.blocking
def test_c6_f19_an_uncommitted_change_to_the_main_settings_cannot_weaken_the_launch(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 6 F19: the carried policy is the committed tree's (the ADR-022 addendum),
    so emptying the main checkout's working settings changes nothing a loose run carries."""
    base, settings, workspace = write_policy_checkout(tmp_path)
    before = read_carried(base, settings, workspace, monkeypatch)
    (base / ".claude" / "settings.json").write_text("{}\n")  # uncommitted
    after = read_carried(base, settings, workspace, monkeypatch)
    assert after["policy_sha256"] == before["policy_sha256"]
    rendered = after["rendered"]
    assert {"Bash(rm -rf *)", "Edit(/control/**)"} <= set(rendered["permissions"]["deny"])
    assert [g for g in rendered["hooks"]["PreToolUse"] if g["matcher"] == ""]
