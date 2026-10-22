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
from sessiontools import GUARDED, launched, write_checkout, write_workspace

from kgme import ledger


def carried(base: Path, settings: dict, tmp_path: Path, monkeypatch, workspace_settings) -> dict:
    """Effect: a `loose` launch from a workspace whose `.claude/settings.json` is
    `workspace_settings`; the rendered run copy it would pass."""
    workspace = write_workspace(base, tmp_path)
    (workspace / ".claude" / "settings.json").write_text(json.dumps(workspace_settings))
    monkeypatch.chdir(workspace)
    code, calls = launched(base, settings, "loose", "HANDOFF-9047")
    assert code == 0
    return json.loads(Path(calls[0][1][4]).read_text())


@pytest.mark.blocking
@pytest.mark.parametrize(
    "workspace_settings",
    [
        {},
        {"note": "pre_tool_guard"},
        {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "true"}]}
                ]
            }
        },
        {"permissions": {"deny": []}},
    ],
)
def test_c2_f1_the_run_copy_carries_the_main_checkouts_guard_and_denies(
    tmp_path: Path, monkeypatch, workspace_settings: dict
) -> None:
    """Review cycle 2 F1, ruled by two arbiters (option C): the main checkout's hooks and
    deny list go into the run copy passed with `--settings`, so a workspace's own project
    settings can add rules but never remove the guard or a deny; the hook commands name the
    main checkout's scripts by absolute path."""
    base, settings = write_checkout(tmp_path)
    (base / ".claude" / "settings.json").write_text(json.dumps({
        **GUARDED, "permissions": {"deny": ["Bash(rm -rf *)", "Edit(/control/**)"]},
    }))  # fmt: skip
    rendered = carried(base, settings, tmp_path, monkeypatch, workspace_settings)
    [group] = [g for g in rendered["hooks"]["PreToolUse"] if g["matcher"] == ""]
    assert group["hooks"][0]["command"] == f"{base}/control/hooks/pre_tool_guard.sh"
    assert {"Bash(rm -rf *)", "Edit(/control/**)"} <= set(rendered["permissions"]["deny"])
    assert rendered["disableAllHooks"] is False


@pytest.mark.blocking
def test_c2_f1_a_workspace_that_disables_hooks_is_refused(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    base, settings = write_checkout(tmp_path)
    workspace = write_workspace(base, tmp_path)
    for name in ("settings.json", "settings.local.json"):
        (workspace / ".claude" / name).write_text(json.dumps({"disableAllHooks": True}))
        monkeypatch.chdir(workspace)
        assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
        assert "disableAllHooks" in capsys.readouterr().err
        (workspace / ".claude" / name).write_text("{}")


@pytest.mark.blocking
def test_c2_f1_the_start_note_hashes_the_carried_policy(tmp_path: Path, monkeypatch) -> None:
    base, settings = write_checkout(tmp_path)
    monkeypatch.chdir(write_workspace(base, tmp_path))
    digests = []
    for deny in (["Bash(rm -rf *)", "Edit(/control/**)"], ["Bash(rm -rf *)"]):
        (base / ".claude" / "settings.json").write_text(
            json.dumps({**GUARDED, "permissions": {"deny": deny}})
        )
        launched(base, settings, "loose", "HANDOFF-9047")
        found = [
            e
            for e in ledger.read(ledger.read_default_dirs(settings, base))
            if e["job"] == "session"
        ]
        record = json.loads(ledger.read_payload(base, found[-1])[0])
        digests.append(record["policy_sha256"])
    assert digests[0] != digests[1], "a changed deny list changes the carried policy's hash"
