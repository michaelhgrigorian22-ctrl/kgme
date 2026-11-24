"""Canary cells for Hermes's fence: where `write_file` and `patch` land.

Purpose: inside ~/Projects/KGME the conductor writes only under `docs/handoff/`, `docs/adr/`,
`docs/readers/` and `docs/STATUS.md`. Every operation of Hermes's V4A grammar is checked and an
unknown one refuses the patch (F3 of AUDIT-0176-review-handoff-0073-cycle-1); containment is
by the folder on disk, so a case alias of the root is the root (AUDIT-0177 F8); Delete and
Move are judged on the entry itself, a final symlink kept, as Hermes acts on it (F9,
`tools/file_tools.py:166-171`).
Inputs: a fixture home from `tests/fencetools.py`.
Outputs: pytest assertions.
Side effects: files and symlinks under `tmp_path`.
"""

from pathlib import Path

import pytest
from fencetools import case_insensitive, make_home, outside, patch, verdict


@pytest.fixture
def home(tmp_path: Path) -> Path:
    return make_home(tmp_path)


# --- F3: Hermes's V4A patch grammar ----------------------------------------------------------


@pytest.mark.blocking
def test_f3_every_operation_of_the_grammar_is_checked(home: Path) -> None:
    b = home / "KGME/brain"
    ok = f"*** Update File: {b}/docs/STATUS.md\n@@\n-a\n+b\n"
    for bad in (f"*** Delete File: {b}/kgme/cli.py\n", f"***Delete File: {b}/kgme/cli.py\n",
                f"***  Delete   File:{b}/kgme/cli.py\n", f"*** Add File: {b}/kgme/new.py\n+x\n",
                f"*** Move File: {b}/docs/handoff/a.md -> {b}/kgme/a.py\n",
                f"*** Move File: {b}/kgme/cli.py -> {b}/docs/handoff/cli.py\n",
                f"*** Update File: {b}/kgme/cli.py\r\n@@\r\n-a\r\n+b\r\n"):  # fmt: skip
        assert not verdict(home, "patch", patch(ok, bad)).allow, bad
        assert not verdict(home, "patch", patch(bad, ok)).allow, bad


@pytest.mark.blocking
def test_f3_an_operation_the_fence_does_not_recognise_refuses_the_patch(home: Path) -> None:
    b = home / "KGME/brain"
    ok = f"*** Update File: {b}/docs/STATUS.md\n@@\n-a\n+b\n"
    v = verdict(home, "patch", patch(ok, f"*** Rename File: {b}/kgme/cli.py\n"))
    assert not v.allow and "Rename File" in v.reason
    add_body = f"*** Add File: {b}/docs/handoff/x.md\n+a\n*** Delete File: {b}/kgme/cli.py\n"
    assert not verdict(home, "patch", patch(add_body)).allow  # an op line inside an Add body
    after = patch(ok)["patch"] + f"*** Delete File: {b}/kgme/cli.py\n"
    assert not verdict(home, "patch", {"mode": "patch", "patch": after}).allow
    assert not verdict(home, "patch", patch("*** Update File: docs/STATUS.md\n@@\n-a\n+b\n")).allow


def test_f3_a_patch_inside_the_architects_paths_is_allowed(home: Path) -> None:
    b = home / "KGME/brain"
    ops = (f"*** Update File: {b}/docs/STATUS.md\n@@\n-a\n+b\n",
           f"*** Move File: {b}/docs/handoff/a.md -> {b}/docs/handoff/done/a.md\n",
           f"*** Add File: {b}/docs/adr/ADR-099-x.md\n+x\n")  # fmt: skip
    assert verdict(home, "patch", patch(*ops)).allow


# --- F8: a case alias of the root is the root ------------------------------------------------


@pytest.mark.blocking
def test_f8_a_case_alias_of_the_root_is_the_root(home: Path) -> None:
    if not case_insensitive(home):
        pytest.skip("a case-sensitive filesystem has no case alias")
    alias = home / "kgme/brain"
    for target in (alias / "kgme/cli.py", alias / "kgme/new.py", home / "KGME/BRAIN/Control/x",
                   home / "kgme/brain/kgme/sub/new.py"):  # fmt: skip
        assert not verdict(home, "write_file", {"path": str(target), "content": "x"}).allow
    upd = patch(f"*** Update File: {alias}/kgme/cli.py\n@@\n-a\n+b\n")
    assert not verdict(home, "patch", upd).allow
    assert not verdict(home, "patch", patch(f"*** Delete File: {alias}/KGME/CLI.PY\n")).allow
    assert not outside(home, f"rm {alias}/kgme/cli.py").allow
    assert not outside(home, "rm x", process=alias).allow


def test_f8_the_architects_paths_under_an_alias_stay_writable(home: Path) -> None:
    if not case_insensitive(home):
        pytest.skip("a case-sensitive filesystem has no case alias")
    proposal = {"path": str(home / "kgme/Brain/DOCS/handoff/proposed/x.md"), "content": "x"}
    assert verdict(home, "write_file", proposal).allow


# --- F9: Delete and Move act on the entry ----------------------------------------------------


@pytest.mark.blocking
def test_f9_delete_and_move_judge_the_entry_not_its_target(home: Path) -> None:
    b = home / "KGME/brain"
    target = home / "elsewhere/target"
    target.write_text("")
    (b / "kgme/outlink").symlink_to(target)
    (home / "elsewhere/inlink").symlink_to(b / "kgme/cli.py")
    for op in (f"*** Delete File: {b}/kgme/outlink\n",
               f"*** Move File: {b}/kgme/outlink -> {home}/elsewhere/moved\n",
               f"*** Move File: {home}/elsewhere/x -> {b}/kgme/outlink\n"):  # fmt: skip
        assert not verdict(home, "patch", patch(op)).allow, op
    assert verdict(home, "patch", patch(f"*** Delete File: {home}/elsewhere/inlink\n")).allow
    mv = patch(f"*** Move File: {home}/elsewhere/inlink -> {home}/elsewhere/renamed\n")
    assert verdict(home, "patch", mv).allow


@pytest.mark.blocking
def test_f9_a_parent_symlink_into_the_root_is_still_followed(home: Path) -> None:
    b = home / "KGME/brain"
    (home / "elsewhere/dir").symlink_to(b / "kgme")
    assert not verdict(
        home, "patch", patch(f"*** Delete File: {home}/elsewhere/dir/cli.py\n")
    ).allow
