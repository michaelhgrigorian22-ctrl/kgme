"""Canary cells for Hermes's fence: the terminal, as far as the fence reads the shell.

Purpose: inside ~/Projects/KGME a terminal command is one simple command, the brain's `kgme …`
or bare `git status|log|diff|show`, rewritten to run by absolute path under a clean
environment (AUDIT-0177 F7, the cycle-2 ruling). Outside, with the directory known, a call is
treated as inside when its text, read after quote removal and case-folding, changes directory
or names the root, when it does not lex, when it expands, or when it names a path inside
(F2 of both review cycles). Residue beyond that (a script, a variable) is the threat model's.
Inputs: a fixture home from `tests/fencetools.py`.
Outputs: pytest assertions.
Side effects: files under `tmp_path`.
"""

import shlex
from pathlib import Path

import pytest
from fencetools import case_insensitive, env_of, inside, make_home, outside, run


@pytest.fixture
def home(tmp_path: Path) -> Path:
    return make_home(tmp_path)


# --- F2: inside, one simple command ----------------------------------------------------------


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "cd /dev/null; rm kgme/cli.py", "cd /nonexistent || rm kgme/cli.py", "cd docs && ls",
    "true || cd x; rm y", "ls | cd x", "cd docs", "git log 2>/dev/null", "ls > /dev/null",
    "ls 2>&1", "kgme ledger read | grep x", "ls\nrm x", "(ls)", "ls &", "cat $HOME/x",
    "cat ${X}", "cat `pwd`", "echo $(id)", "cat <(ls)", "ls *", "cat {a,b}", "rg {--pre=sh,x}",
    "cat \"$X\"", "ls \\;", "X=1 ls", "KGME_CONDUCTOR=x kgme sync", "ls # rm x", "cat ~root/x",
    "rm kgme/cli.py", "echo x", "python -c 'print(1)'", "make check", "tee kgme/cli.py",
    "sed -i '' s/a/b/ kgme/cli.py", "rg --pre=sh x", "/bin/ls", "env ls",
])  # fmt: skip
def test_f2_inside_anything_but_one_allowlisted_simple_command_is_refused(
    home: Path, command: str
) -> None:
    assert not inside(home, command).allow
    assert not run(home, command).allow


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "cd .. ; cd KGME/brain; rm kgme/cli.py", "pushd ../KGME/brain && rm kgme/cli.py",
    "source ./x.sh", ". ./x.sh", "rm -rf ${R}ME/brain", "rm -rf $R/brain", "rm -rf `cat p`",
    "rm -rf ~/{KGME,x}", "eval 'rm x'", f"cat {'/'}dev/null; rm ~/KGME/brain/kgme/cli.py",
    "rm 'x", "echo \"unclosed",
])  # fmt: skip
def test_f2_outside_a_directory_change_or_an_expansion_makes_the_call_inside(
    home: Path, command: str
) -> None:
    assert not outside(home, command).allow


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "c''d {h}; c''d KGME; c''d brain; rm kgme/cli.py", "\"cd\" {h}; \"cd\" KGME/brain; rm x",
    "\\cd {h}; \\cd KGME/brain; rm x", "'pushd' {h} && 'pushd' KGME/brain && rm x",
    "c\"\"d {h}; c\"\"d KGME/brain; rm x", "c''d {h}; c''d KGME/brain; rm 'x",
])  # fmt: skip
def test_f2_a_quoted_directory_change_from_outside_is_inside(home: Path, command: str) -> None:
    # No argument resolves inside from the start: AUDIT-0177 F2's case, one level up.
    assert not run(home, command.format(h=home.name), workdir=home.parent).allow


@pytest.mark.blocking
def test_f2_outside_naming_the_root_in_any_case_is_inside(home: Path) -> None:
    root = str(home / "KGME")
    assert not outside(home, f"rm -rf {root[:-4]}K'G'ME").allow
    assert not outside(home, "echo ~/projects/kgme").allow  # the literal name, any case
    if case_insensitive(home):
        assert not outside(home, f"rm -rf {root.swapcase()}").allow
        assert not outside(home, f"rm -rf {root[:-4]}k'G'mE").allow


@pytest.mark.blocking
def test_f2_a_path_into_the_root_counts_from_outside(home: Path) -> None:
    root = home / "KGME"
    assert not outside(home, f"rm {root}/brain/kgme/cli.py").allow
    assert not outside(home, "rm ~/KGME/brain/kgme/cli.py").allow
    assert not outside(home, f"rm {root}/br*/kgme/cli.py").allow
    assert not outside(home, f"echo x > {root}/brain/kgme/cli.py").allow
    assert not outside(home, "rm ../KGME/brain/kgme/cli.py").allow
    (home / "elsewhere/link").symlink_to(root / "brain")
    assert not outside(home, "rm link/kgme/cli.py").allow
    assert outside(home, f"{root}/brain/.venv/bin/kgme lint").allow  # a dispatch: allowed


# --- F7: the inside allowlist, kgme and bare git reads ---------------------------------------


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "git status", "git log", "git diff", "git show", "kgme --help", "kgme skills",
    "kgme agent run build.integrator \"summarise the last crew run\"",
])  # fmt: skip
def test_f2_the_allowed_commands_run_rewritten_under_a_clean_environment(
    home: Path, command: str
) -> None:
    poisoned = env_of(home, GIT_EXTERNAL_DIFF="sh -c x", PYTHONPATH="/evil", BASH_ENV="/evil")
    v = inside(home, command, env=poisoned)
    assert v.allow and v.args is not None, v.reason
    words = shlex.split(v.args["command"])
    assert words[:2] == ["/usr/bin/env", "-i"]
    pairs = [w for w in words[2:] if "=" in w.split("/")[0]]
    assert f"HOME={home}" in pairs and "KGME_CONDUCTOR=hermes" in pairs
    assert not any(
        p.split("=")[0] in ("GIT_EXTERNAL_DIFF", "PYTHONPATH", "BASH_ENV") for p in pairs
    )
    program = words[2 + len(pairs)]
    assert Path(program).is_absolute(), program
    assert v.args["workdir"] == str(home / "KGME/brain")


@pytest.mark.blocking
@pytest.mark.parametrize("command", [
    "ls", "ls -la", "cat docs/STATUS.md", "grep -rn x docs", "rg x", "git status --porcelain",
    "git log -5", "git log --oneline", "git diff main", "git show HEAD", "git status docs",
    "rg --hostname-bin=/tmp/helper --hyperlink-format=default --color=always x README.md",
])  # fmt: skip
def test_f7_inside_only_bare_git_reads_and_kgme_run(home: Path, command: str) -> None:
    assert not inside(home, command).allow
    assert not run(home, command).allow


@pytest.mark.blocking
@pytest.mark.parametrize("command", ["git status", "git log", "git diff", "git show"])
def test_f7_bare_git_reads_run_without_global_or_system_config(home: Path, command: str) -> None:
    v = inside(home, command)
    assert v.allow and v.args["command"].endswith(f"/bin/git {command.split()[1]}"), v.reason
    assert "GIT_CONFIG_GLOBAL=/dev/null" in v.args["command"]
    assert "GIT_CONFIG_NOSYSTEM=1" in v.args["command"]


@pytest.mark.blocking
def test_f7_a_helper_the_shell_would_launch_is_never_reached(home: Path) -> None:
    marker = home / "elsewhere/launched"
    helper = home / "elsewhere/helper"
    helper.write_text(f"#!/bin/sh\ntouch {marker}\n")
    helper.chmod(0o755)
    v = inside(home, f"rg --hostname-bin={helper} --hyperlink-format=default x README.md")
    assert not v.allow and not marker.exists()


def test_f7_a_tilde_argument_to_kgme_is_expanded_by_the_fence(home: Path) -> None:
    v = run(home, "kgme lint ~/KGME/brain/docs")
    assert v.allow and str(home / "KGME/brain/docs") in v.args["command"]
