"""Tests for the hook's own PATH (HANDOFF-0062 §3): every tool the hook path runs resolves under it.

Purpose: a git hook runs with a bare environment, and `control/git-hooks/post-commit` sets its
`PATH` itself (AUDIT-0009). Everything the hook starts runs under that line: `kgme sync`, the
atlas, and `kgme merge design`, whose trial runs `make check` in a clone, whose mod step runs
`claude plugin validate`. A tool the line does not reach fails only there, where nobody is
watching (HANDOFF-0062: eight design trials refused for want of `claude`). This reads the line
from the hook file, never retyped, and resolves each tool on it, so a tool that moves to a
folder the line does not name is red here, in the shell, before it is red in a trial. The
checker itself is shown to catch a missing folder, on a copy of the line without it.
Inputs: `control/git-hooks/post-commit`; this machine's tools.
Outputs: pytest assertions.
Side effects: reads the hook file and checks the folders on its line for the tools; writes nothing.
"""

import os
import re
from pathlib import Path

import pytest

from kgme import paths

HOOK = paths.root() / "control" / "git-hooks" / "post-commit"
# the hook's own commands that are no shell builtin: git, uv, mkdir, date (review cycle 1 F1;
# printf, trap, [, exit and export are builtins); then what its children run: make (the merge
# trial's check), gh (git's credential helper when the sync pushes, AUDIT-0009), claude (make
# check's mod step, `kgme.mods`, HANDOFF-0059)
TOOLS = ("git", "uv", "mkdir", "date", "make", "gh", "claude")
PATH_LINE = re.compile(r'^PATH="([^"]*)"\s*$')


def parse_path_line(text: str) -> list[str]:
    """Pure: the folders of the hook's one `PATH="..."` line, `$HOME` expanded."""
    found = [m.group(1) for line in text.splitlines() if (m := PATH_LINE.match(line))]
    assert len(found) == 1, f"the hook sets PATH {len(found)} times; this reads exactly one line"
    home = str(Path.home())
    return [part.replace("${HOME}", home).replace("$HOME", home) for part in found[0].split(":")]


def read_where(tool: str, folders: list[str]) -> str | None:
    """Effect: where `tool` resolves on `folders`, as `command -v` would, by checking each folder
    for an executable file of that name; None if nowhere."""
    for folder in folders:
        candidate = os.path.join(folder, tool)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def read_missing(folders: list[str]) -> list[str]:
    """Effect: the tools of `TOOLS` that resolve on no folder of `folders` (`read_where`)."""
    return [tool for tool in TOOLS if read_where(tool, folders) is None]


@pytest.mark.blocking
def test_every_tool_the_hook_path_runs_resolves_under_the_hooks_own_path() -> None:
    folders = parse_path_line(HOOK.read_text())
    assert read_missing(folders) == [], f"not on the hook's PATH {folders}"


@pytest.mark.blocking
@pytest.mark.parametrize("tool", TOOLS)
def test_a_tool_whose_folder_leaves_the_line_is_red(tool: str) -> None:
    """The acceptance's red: a copy of the real line without every folder where `tool` lives."""
    folders = parse_path_line(HOOK.read_text())
    without = [f for f in folders if read_where(tool, [f]) is None]
    assert tool in read_missing(without)


@pytest.mark.blocking
def test_the_line_is_read_from_the_file_and_must_be_one() -> None:
    assert parse_path_line('x\nPATH="$HOME/a:/b"\nexport PATH\n') == [f"{Path.home()}/a", "/b"]
    with pytest.raises(AssertionError, match="sets PATH 2 times"):
        parse_path_line('PATH="/a"\nPATH="/b"\n')
    with pytest.raises(AssertionError, match="sets PATH 0 times"):
        parse_path_line("export PATH\n")
