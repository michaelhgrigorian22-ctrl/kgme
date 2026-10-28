"""Tests for one ledger whatever the checkout (HANDOFF-0047 §3).

Purpose: the ledger, trace, and test streams resolve from the repository's git common
directory, the main checkout's `.git`, so a session in any worktree appends to the main
checkout's `logs/`; outside a git repository the resolution fails closed. End to end, the
live hook entry points run from a worktree write into the main checkout's test ledger and
none into the worktree's, and the post-tool hook's payload lands in the main checkout's
`logs/scratch/payloads/` with a ref that resolves from there (Michou, 2026-10-21).
Inputs: throwaway repositories under `tmp_path`; a clone of this repository with this tree's
`kgme/` copied in.
Outputs: pytest assertions.
Side effects: repositories, a worktree, and streams under `tmp_path` only; nothing in this
repository is written.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kgme import ledger, paths

ROOT = paths.root()


def run_git(repo: Path, *argv: str) -> None:
    """Effect: one quiet git command in `repo`, with a fixed identity."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@localhost", *argv],
        cwd=repo, check=True, capture_output=True,
    )  # fmt: skip


def write_repo_with_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """Effect: a repository with one commit and a worktree of it beside it."""
    main = tmp_path / "main"
    main.mkdir()
    run_git(main, "init", "-q", "-b", "main")
    (main / "a.md").write_text("x\n")
    run_git(main, "add", "a.md")
    run_git(main, "commit", "-q", "-m", "one")
    worktree = tmp_path / "wt"
    run_git(main, "worktree", "add", "-q", "--detach", str(worktree))
    return main.resolve(), worktree.resolve()


@pytest.mark.blocking
def test_a_worktree_resolves_to_its_main_checkout(tmp_path: Path) -> None:
    main, worktree = write_repo_with_worktree(tmp_path)
    assert ledger.read_main_checkout(worktree) == main
    assert ledger.read_main_checkout(main) == main
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip
    assert ledger.read_main_checkout(ROOT) == Path(common).resolve().parent, (
        "this checkout, or its main checkout when the suite runs in a worktree (HANDOFF-0048)"
    )


@pytest.mark.blocking
def test_outside_a_repository_the_resolution_fails_closed(tmp_path: Path) -> None:
    alone = tmp_path / "alone"
    alone.mkdir()
    with pytest.raises(RuntimeError, match="not inside a git repository"):
        ledger.read_main_checkout(alone)


@pytest.mark.blocking
def test_the_hook_in_a_worktree_writes_the_main_checkouts_ledger(tmp_path: Path) -> None:
    clone = tmp_path / "clone"
    run_git(tmp_path, "clone", "-q", "--no-hardlinks", str(ROOT), str(clone))
    worktree = tmp_path / "wt"
    run_git(clone, "worktree", "add", "-q", "--detach", str(worktree))
    for checkout in (clone, worktree):  # this tree's code, in both copies
        shutil.rmtree(checkout / "kgme")
        shutil.copytree(
            ROOT / "kgme", checkout / "kgme", ignore=shutil.ignore_patterns("__pycache__")
        )
    payload = {
        "session_id": "worktree-probe",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
        "tool_use_id": "toolu_worktree_probe",
        "cwd": str(worktree),
    }
    done = subprocess.run(
        [sys.executable, "-m", "kgme.hooks.pre_tool_guard", "--test-streams"],
        input=json.dumps(payload), cwd=worktree, capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr

    def streams(checkout: Path) -> str:
        found = [p.read_text() for p in (checkout / "logs").glob("*-test/**/*.jsonl")]
        return "".join(found)

    assert "worktree-probe" in streams(clone), "the event is in the main checkout's streams"
    assert "worktree-probe" not in streams(worktree), "and none is in the worktree's"
    done = subprocess.run(
        [sys.executable, "-m", "kgme.hooks.post_tool_ledger", "--test-streams"],
        input=json.dumps({**payload, "tool_response": {"stdout": "a.md"}}),
        cwd=worktree, capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    held = lambda checkout: list((checkout / "logs" / "scratch" / "payloads").rglob("*.json"))  # noqa: E731
    assert held(clone) and not held(worktree), "payloads follow the ledger to the main checkout"
    [outcome] = [
        json.loads(line)
        for line in streams(clone).splitlines()
        if '"outcome"' in line and "worktree-probe" in line
    ]
    assert (clone / outcome["payload_ref"]).is_file(), "and its ref resolves from there"


def write_vault_repo(tmp_path: Path) -> tuple[Path, Path]:
    """Effect: the capture tests' seeded vault, committed as a repository, and a worktree of it."""
    from capturetools import write_vault

    main = write_vault(tmp_path)
    run_git(main, "init", "-q", "-b", "main")
    run_git(main, "add", "-A")
    run_git(main, "commit", "-q", "-m", "vault")
    worktree = tmp_path / "wt"
    run_git(main, "worktree", "add", "-q", "--detach", str(worktree))
    return main.resolve(), worktree.resolve()


def run_job(job: str, base: Path) -> int:
    """Effect: one job by its direct call on `base`, as the CLI calls it."""
    from capturetools import SETTINGS, THURSDAY

    from kgme import atlas_read, brief_io, capture_io, clean_io, daily_io

    if job == "capture":
        return capture_io.run_capture(
            "friction", "said in a worktree", None, base, SETTINGS, THURSDAY
        )
    if job == "brief":
        return brief_io.run_brief("2026-10-16", False, base, SETTINGS)
    if job == "daily":
        return daily_io.run_daily("2026-10-15", base, SETTINGS, None, False)
    if job == "clean":
        return clean_io.run_clean("briefs", True, base, SETTINGS, home=base)
    return atlas_read.run_atlas(base, SETTINGS)


@pytest.mark.blocking
@pytest.mark.parametrize("job", ["capture", "brief", "daily", "clean"])
def test_a_job_refuses_to_run_from_a_worktree(tmp_path: Path, job: str, capsys) -> None:
    """HANDOFF-0047 review cycle 3 F12 and F13, ruled advisory by two arbiters (option A): a
    job's shared record names no workspace, so jobs run in the main checkout until
    HANDOFF-0048 gives records a workspace; from a worktree they refuse before any read or
    ledger write. The atlas is not refused: it writes only its own ignored view, and
    HANDOFF-0051 regenerates it on every branch, the design worktree's included."""
    from capturetools import SETTINGS

    main, worktree = write_vault_repo(tmp_path)
    before = ledger.read(ledger.read_base_dirs(SETTINGS, main))
    assert run_job(job, worktree) == 2
    assert "HANDOFF-0048" in capsys.readouterr().err
    assert ledger.read(ledger.read_base_dirs(SETTINGS, main)) == before
    assert not list(worktree.rglob("logs/ledger/**/*.jsonl"))


@pytest.mark.blocking
def test_review_refuses_to_run_from_a_worktree(tmp_path: Path, monkeypatch, capsys) -> None:
    from kgme import cli

    _, worktree = write_vault_repo(tmp_path)
    monkeypatch.setattr(paths, "root", lambda: worktree)
    assert cli.main(["review", "--handoff", "HANDOFF-0047", "--dry-run"]) == 2
    assert "HANDOFF-0048" in capsys.readouterr().err


@pytest.mark.blocking
def test_a_job_on_a_folder_that_is_not_a_checkout_keeps_its_own_ledger(tmp_path: Path) -> None:
    from capturetools import SETTINGS, write_vault

    base = write_vault(tmp_path)
    assert run_job("capture", base) == 0
    assert ledger.read(ledger.read_base_dirs(SETTINGS, base))


@pytest.mark.blocking
def test_the_guard_in_a_worktree_reads_the_outputs_list_the_launcher_wrote(
    tmp_path: Path,
) -> None:
    """HANDOFF-0047 review cycle 2 F9: `kgme session loose` writes the Outputs list in the
    main checkout; the guard in the workspace must read that one, so a write inside the
    Outputs is allowed and one outside is refused for being outside, not for want of a list."""
    from kgme import config, loop_outputs

    settings = config.read_config()
    clone = tmp_path / "clone"
    run_git(tmp_path, "clone", "-q", "--no-hardlinks", str(ROOT), str(clone))
    worktree = tmp_path / "wt"
    run_git(clone, "worktree", "add", "-q", "--detach", str(worktree))
    for checkout in (clone, worktree):
        shutil.rmtree(checkout / "kgme")
        shutil.copytree(
            ROOT / "kgme", checkout / "kgme", ignore=shutil.ignore_patterns("__pycache__")
        )
    toy = "## Outputs\n`memory/agent/inside.md`\n"
    run = "01J0LOOPRUNFORWORKTREETEST"
    scratch = paths.scratch_test_dir(settings, clone.resolve())
    _, digest = loop_outputs.write_outputs(clone.resolve(), scratch, "HANDOFF-9047", run, toy)
    env = {
        **__import__("os").environ,
        loop_outputs.ENV_HANDOFF: "HANDOFF-9047",
        loop_outputs.ENV_RUN: run,
        loop_outputs.ENV_SHA: digest,
    }

    def guard(path: str) -> subprocess.CompletedProcess:
        payload = {
            "session_id": "loop-worktree", "tool_name": "Write",
            "tool_use_id": f"toolu_{path[-9:]}",
            "tool_input": {"file_path": str(worktree / path), "content": "x"}, "cwd": str(worktree),
        }  # fmt: skip
        return subprocess.run(
            [sys.executable, "-m", "kgme.hooks.pre_tool_guard", "--test-streams"],
            input=json.dumps(payload), cwd=worktree, env=env, capture_output=True, text=True,
            check=False,
        )  # fmt: skip

    inside = guard("memory/agent/inside.md")
    assert inside.returncode == 0, inside.stderr
    outside = guard("memory/agent/outside.md")
    assert outside.returncode == 2 and "outside HANDOFF-9047's Outputs" in outside.stderr
