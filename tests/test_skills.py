"""`kgme skills install` and the skill-copy lint (HANDOFF-0048 §7, amendment 10).

Purpose: on a fixture repository with two skills and a fixture home: the installer links each
skill into the two home folders and the two local ones, keeps a link it made, refuses a
folder of the same name it did not install and never touches `synced/`; a `--copy` folder
gets a copy with its marker and is remembered; `kgme lint`'s check flags a copy whose own
files drifted, a copy whose source drifted, and a copy whose source is gone (cycle 1 F15);
the command refuses under an agent harness; the note records the measured state of
`~/.claude/skills/`.
Inputs: fixture folders under `tmp_path`.
Outputs: pytest assertions.
Side effects: files and links under `tmp_path`; events in a ledger under `tmp_path`.
"""

import os
from pathlib import Path

import pytest

from kgme import config, ledger, skills

SETTINGS = config.read_config()


def fixture(tmp_path: Path) -> tuple[Path, Path]:
    base = tmp_path / "repo"
    for name in ("kgme-planner", "kgme-builder"):
        (base / "skills" / name).mkdir(parents=True)
        (base / "skills" / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n# {name}\n")
    (base / "skills" / "not-a-skill").mkdir()
    home = tmp_path / "home"
    (home / ".claude" / "skills" / "synced").mkdir(parents=True)
    (home / ".claude" / "skills" / "synced" / "x.md").write_text("Claude's\n")
    (home / ".claude" / "skills" / "kgme-builder").mkdir()  # not ours: a folder of that name
    return base, home


def run(base: Path, home: Path, copies=(), environ=None) -> int:
    dirs = ledger.Dirs(base / "ledger", base / "trace", ("Read",))
    return skills.run_install(
        base, SETTINGS, home, copies, dirs, environ if environ is not None else {}
    )


@pytest.mark.blocking
def test_install_links_keeps_refuses_and_never_touches_synced(tmp_path: Path, capsys) -> None:
    base, home = fixture(tmp_path)
    assert run(base, home) == 1, "one refusal: the folder it did not install"
    out = capsys.readouterr().out
    planner = home / ".claude" / "skills" / "kgme-planner"
    assert (
        planner.is_symlink() and planner.resolve() == (base / "skills" / "kgme-planner").resolve()
    )
    assert (home / ".agents" / "skills" / "kgme-planner").is_symlink()
    local = base / ".claude" / "skills" / "kgme-planner"
    assert local.is_symlink() and os.readlink(local) == "../../skills/kgme-planner", "relative"
    assert (base / ".agents" / "skills" / "kgme-builder").is_symlink()
    assert "kgme-builder: refused: not installed by kgme" in out
    assert not (home / ".claude" / "skills" / "kgme-builder").is_symlink(), "left as it was"
    assert (home / ".claude" / "skills" / "synced" / "x.md").read_text() == "Claude's\n"
    assert "not-a-skill" not in out, "a folder without SKILL.md is not a skill"
    assert run(base, home) == 1
    assert "kgme-planner: kept" in capsys.readouterr().out
    (note,) = [
        e
        for e in ledger.read(ledger.Dirs(base / "ledger", base / "trace", ("Read",)))
        if e["job"] == "skills"
    ][:1]
    assert "~/.claude/skills before: dir kgme-builder; dir synced" in note["summary"]
    assert note["actor"] == "michou"


@pytest.mark.blocking
def test_copies_carry_a_marker_are_remembered_and_lint_sees_drift_on_either_side(
    tmp_path: Path,
) -> None:
    base, home = fixture(tmp_path)
    copies = (tmp_path / "no-links",)
    run(base, home, copies)
    copy = copies[0] / "kgme-planner"
    assert (copy / "SKILL.md").is_file() and (copy / skills.MARKER).is_file()
    assert skills.read_copies(base) == copies, "remembered for a later `kgme lint`"
    assert skills.read_findings(base) == []
    (copy / "SKILL.md").write_text("edited copy\n")
    found = skills.read_findings(base)
    assert [f.cls for f in found] == ["blocking"] and "drifted" in found[0].message
    run(base, home, copies)  # a fresh copy replaces ours
    assert skills.read_findings(base) == []
    (base / "skills" / "kgme-planner" / "SKILL.md").write_text("edited source\n")
    assert any("drifted" in f.message for f in skills.read_findings(base)), "the source side too"
    import shutil

    shutil.rmtree(base / "skills" / "kgme-planner")
    assert any("no longer holds" in f.message for f in skills.read_findings(base))
    (copies[0] / "kgme-other").mkdir()
    (copies[0] / "kgme-other" / "SKILL.md").write_text("someone else's\n")
    assert not any("kgme-other" in f.path for f in skills.read_findings(base)), (
        "no marker, not ours"
    )


@pytest.mark.blocking
def test_install_refuses_under_an_agent_harness_and_with_no_skills(tmp_path: Path, capsys) -> None:
    base, home = fixture(tmp_path)
    assert run(base, home, environ={"CLAUDECODE": "1"}) == 2
    assert "Michou's command" in capsys.readouterr().err
    empty = tmp_path / "empty"
    empty.mkdir()
    assert run(empty, home) == 2
