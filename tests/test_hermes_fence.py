"""Canary cells for Hermes's fence inside ~/Projects/KGME: the acceptance, the directory, dispatch.

Purpose: the fence allows only what it fully understands (Cowork's rulings on review cycles 1
and 2, threat model: accidental and casual writes, not an adversarial shell). A call is inside
when Hermes's process directory, the terminal's `workdir`, or any argument resolves inside the
root; Hermes's session directory never reaches the hook, so a relative path is refused and a
terminal call without an absolute `workdir` is treated as inside. Dispatch runs only the
brain's own `kgme`; an unrecognised payload or a crash refuses (fail closed). Each cell names
the finding it answers (F1 to F6 of AUDIT-0176-review-handoff-0073-cycle-1). The shell rules
are in `test_hermes_fence_shell.py`, the write paths in `test_hermes_fence_paths.py`.
Inputs: a fixture home from `tests/fencetools.py`.
Outputs: pytest assertions.
Side effects: files under `tmp_path`; the module and the wrapper run as subprocesses.
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from fencetools import env_of, inside, make_home, outside, run, verdict

from kgme import hermes_fence as fence
from kgme import hermes_fence_policy as policy
from kgme.hermes_fence_parse import Call


@pytest.fixture
def home(tmp_path: Path) -> Path:
    return make_home(tmp_path)


# --- the acceptance cases ------------------------------------------------------------------


@pytest.mark.blocking
def test_acceptance_write_into_kgme_is_refused_and_a_proposal_is_written(home: Path) -> None:
    brain = home / "KGME/brain"
    refused = verdict(home, "write_file", {"path": str(brain / "kgme/cli.py"), "content": "x"})
    assert not refused.allow and "docs/handoff/" in refused.reason
    assert not verdict(home, "write_file", {"path": str(brain / "control/x"), "content": ""}).allow
    proposal = {"path": str(brain / "docs/handoff/proposed/2026-11-20-x.md"), "content": "x"}
    assert verdict(home, "write_file", proposal).allow


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "git commit -m x", "git add -A", "git push", "git reset --hard", "git checkout main",
    "git -c core.pager=sh log", "git -C . commit -m x", "git diff --output=x",
])  # fmt: skip
def test_acceptance_git_writes_are_refused(home: Path, command: str) -> None:
    assert not inside(home, command).allow
    assert not run(home, command).allow  # the directory unknown


# --- F1: the directory the call runs in ------------------------------------------------------


@pytest.mark.blocking
def test_f1_a_relative_write_is_refused_wherever_hermes_was_started(home: Path) -> None:
    for process in (home / "elsewhere", home / "KGME/brain"):
        v = verdict(home, "write_file", {"path": "kgme/cli.py", "content": "x"}, process)
        assert not v.allow and "absolute" in v.reason
    patch = {"mode": "replace", "path": "docs/STATUS.md", "old_string": "a", "new_string": "b"}
    assert not verdict(home, "patch", patch).allow


@pytest.mark.blocking
def test_f1_a_terminal_call_without_an_absolute_workdir_is_inside(home: Path) -> None:
    for workdir in (None, "brain", "~/KGME/brain"):
        v = run(home, "rm -f kgme/cli.py", workdir=workdir)
        assert not v.allow and "workdir" in v.reason, workdir
    assert run(home, "git status").allow


@pytest.mark.blocking
def test_f1_the_process_directory_inside_makes_every_terminal_call_inside(home: Path) -> None:
    v = outside(home, "rm -f x", process=home / "KGME/brain")
    assert not v.allow


@pytest.mark.blocking
def test_f1_outside_with_the_directory_known_everything_passes_unchanged(home: Path) -> None:
    for command in ("rm -f x", "python -c 'print(1)'", "echo hi > y | wc", "git commit -m x"):
        v = outside(home, command)
        assert v.allow and v.args is None, command


@pytest.mark.blocking
def test_f1_execute_code_is_refused_everywhere(home: Path) -> None:
    assert not verdict(home, "execute_code", {"code": "print(1)"}).allow


@pytest.mark.blocking
def test_f1_the_root_comes_from_the_real_home_not_home(home: Path, tmp_path: Path) -> None:
    profile = tmp_path / "profile-home"
    profile.mkdir()
    env = env_of(home, HOME=str(profile))
    target = {"path": "~/KGME/brain/kgme/cli.py", "content": "x"}
    assert not verdict(home, "write_file", target, env=env).allow  # ~ under the real home
    (profile / "KGME").symlink_to(home / "KGME")
    assert not verdict(home, "write_file", target, env=env).allow  # and under $HOME
    assert fence.read_root({"HOME": str(profile)}).parent.parent != profile


def test_f1_unknown_tools_naming_a_path_are_judged_like_writes(home: Path) -> None:
    brain = home / "KGME/brain"
    assert not verdict(home, "delete_file", {"path": str(brain / "kgme/cli.py")}).allow
    assert not verdict(home, "delete_file", {"path": "kgme/cli.py"}).allow
    assert verdict(home, "web_extract", {"urls": ["https://example.com/a/b"]}).allow
    assert verdict(home, "delegate_task", {"goal": "summarise docs/STATUS.md for me"}).allow
    assert verdict(home, "read_file", {"path": "kgme/cli.py"}).allow


# --- F4: dispatch runs only the brain's kgme -------------------------------------------------


@pytest.mark.blocking
def test_f4_an_executable_merely_named_kgme_is_refused(home: Path) -> None:
    fake = home / "elsewhere/kgme"
    fake.write_text("#!/bin/sh\n")
    fake.chmod(0o755)
    for command in (f"{fake} --help", "./kgme --help", "../elsewhere/kgme --help",
                    "python -m kgme lint", "uv run kgme lint", "uv run --frozen kgme lint",
                    f"uv run --frozen --project {home}/elsewhere kgme lint",
                    f"uv run --with x --frozen --project {home}/KGME/brain kgme lint"):  # fmt: skip
        assert not inside(home, command).allow, command
        assert not run(home, command).allow, command


@pytest.mark.blocking
def test_f4_the_trusted_forms_run_the_resolved_binary(home: Path) -> None:
    brain = home / "KGME/brain"
    trusted = str(brain / ".venv/bin/kgme")
    link = home / "elsewhere/k"
    link.symlink_to(brain / ".venv/bin/kgme")
    for command in (
        f"{trusted} lint",
        f"{link} lint",
        "kgme lint",
        "~/KGME/brain/.venv/bin/kgme lint",
    ):
        v = run(home, command)
        assert v.allow, (command, v.reason)
        words = shlex.split(v.args["command"])
        assert words[words.index(trusted)+1:] == ["lint"], command  # fmt: skip
    v = run(home, f"uv run --frozen --project {brain} kgme lint")
    words = shlex.split(v.args["command"])
    assert str(home / "bin/uv") in words
    assert words[-6:] == ["run", "--frozen", "--project", str(brain), "kgme", "lint"]


@pytest.mark.blocking
@pytest.mark.parametrize("command", ["kgme approve --what code", "kgme merge design",
                                     "kgme skills install", "kgme --quiet approve"])  # fmt: skip
def test_f4_michous_own_kgme_acts_stay_refused(home: Path, command: str) -> None:
    assert not run(home, command).allow


# --- F6: effects apart from policy -----------------------------------------------------------


def test_f6_the_decision_reads_nothing(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    call = Call("write_file", {"path": "/r/brain/kgme/x.py", "content": ""}, "/x")
    facts = policy.Facts(root=Path("/r"), homes=("/h",), resolved={"/r/brain/kgme/x.py":
                         (Path("/r/brain/kgme/x.py"),), "/x": (Path("/x"),)}, entries={},
                         trusted_kgme=Path("/r/brain/.venv/bin/kgme"), brain=Path("/r/brain"),
                         programs={}, env={})  # fmt: skip

    def forbidden(*_a, **_k):
        raise AssertionError("the policy touched the filesystem")

    for name in ("realpath", "exists", "isdir"):
        monkeypatch.setattr(os.path, name, forbidden)
    for name in ("listdir", "lstat", "stat"):
        monkeypatch.setattr(os, name, forbidden)
    monkeypatch.setattr(fence.glob, "glob", forbidden)
    assert not policy.judge(call, facts).allow


# --- failing closed --------------------------------------------------------------------------


@pytest.mark.blocking
def test_an_unrecognised_payload_is_refused_naming_keys_not_values(home: Path) -> None:
    v = fence.run_decide(json.dumps({"event": "x", "secret": "hunter2"}), home / "KGME", {}, home)
    assert not v.allow and "secret" in v.reason and "hunter2" not in v.reason
    assert not fence.run_decide("not json", home / "KGME", {}, home).allow


def module(home: Path, stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", "-m", "kgme.hermes_fence", "--root", str(home / "KGME"),
         "--home", str(home)],
        input=stdin, capture_output=True, text=True, check=False, env=env_of(home),
    )  # fmt: skip


@pytest.mark.blocking
def test_the_hook_exits_2_to_block_and_prints_hermes_modify_to_allow(home: Path) -> None:
    brain = home / "KGME/brain"
    call = {"tool_name": "terminal", "tool_input": {"command": "git commit -m x",
            "workdir": str(brain)}, "cwd": str(home / "elsewhere")}  # fmt: skip
    blocked = module(home, json.dumps(call))
    assert blocked.returncode == 2 and "kgme-fence" in blocked.stderr
    call["tool_input"]["command"] = "git status"
    allowed = module(home, json.dumps(call))
    directive = json.loads(allowed.stdout)  # agent/shell_hooks.py:651-653
    assert allowed.returncode == 0 and directive["action"] == "modify"
    assert directive["args"]["command"].startswith("/usr/bin/env -i ")
    call["tool_input"] = {"command": "rm -f x", "workdir": str(home / "elsewhere")}
    plain = module(home, json.dumps(call))
    assert plain.returncode == 0 and plain.stdout == ""


@pytest.mark.blocking
def test_the_wrapper_fails_closed_without_its_interpreter(tmp_path: Path) -> None:
    hook = tmp_path / "kgme-fence"
    hook.write_text(fence.wrapper(str(tmp_path / "missing" / "python")))
    hook.chmod(0o755)
    done = subprocess.run([str(hook)], input="{}", capture_output=True, text=True, check=False)
    assert done.returncode == 2 and "refusing" in done.stderr
    hook.write_text(fence.wrapper(sys.executable))  # the real one: an empty payload refuses
    done = subprocess.run([str(hook)], input="{}", capture_output=True, text=True, check=False,
                          env={**os.environ, "HOME": str(tmp_path)})  # fmt: skip
    assert done.returncode == 2
