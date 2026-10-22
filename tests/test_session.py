"""Tests for `kgme session <level>` (HANDOFF-0047, ADR-022).

Purpose: each level builds the command line ADR-022 names, with `--setting-sources
project,local`, the rendered run copy of its template, its permission mode, the model from
`kgme.toml [models] builder`, and for `loose` the headless hard stops from `[sessions]`; the
template's placeholders become absolute paths (the sandbox's plain form, an `Edit` rule's
`//` form), and `{outputs}` is the handoff's `Outputs` plus `tests/` and `logs/scratch/`, in
the workspace the run builds in. `loose` refuses without caps; it runs one executable handoff
(open, at the top of `docs/handoff/`, from `cowork` or `michou`); it starts only from a
worktree of this repository whose project settings run the guard, never the main checkout;
extra arguments that would widen a level are refused. One ledger note before the launch,
in the main checkout's ledger, names the level and the run copy's sha256, and its payload,
in the main checkout too, the full argv; a dry run starts nothing; the CLI passes on only what
follows `--`; the templates Michou applies declare what ADR-022 says.
Inputs: fixture checkouts and worktrees under `tmp_path`; this repository's applied templates.
Outputs: pytest assertions.
Side effects: repositories, worktrees, and streams under `tmp_path`; nothing is launched.
"""

import json
import tempfile
from pathlib import Path

import pytest
from sessiontools import (
    APPLIED,
    TOY,
    launched,
    write_checkout,
    write_workspace,
)  # fmt: skip

from kgme import ledger, loop_outputs, paths, session


@pytest.mark.blocking
@pytest.mark.parametrize("level,mode", [("tight", "plan"), ("work", "auto")])
def test_an_interactive_level_is_one_launcher_line(tmp_path: Path, level: str, mode: str) -> None:
    base, settings = write_checkout(tmp_path)
    code, calls = launched(base, settings, level)
    assert code == 0 and len(calls) == 1
    argv = calls[0][1]
    assert argv[:4] == ["claude", "--setting-sources", "project,local", "--settings"]
    assert argv[5:] == ["--permission-mode", mode, "--model", "claude-opus-5-5"]
    copy = Path(argv[4])
    assert copy.is_relative_to(base / "logs" / "scratch" / "sessions") and copy.is_file()
    rendered = json.loads(copy.read_text())
    if level == "work":
        assert rendered["sandbox"]["filesystem"]["allowWrite"] == [
            str(base), str(Path(tempfile.gettempdir()).resolve())
        ]  # fmt: skip
        assert rendered["sandbox"]["allowUnsandboxedCommands"] is False
    else:
        assert rendered["permissions"]["disableAutoMode"] == "disable"


@pytest.mark.blocking
def test_loose_runs_one_handoff_headless_fenced_to_its_workspace(
    tmp_path: Path, monkeypatch
) -> None:
    base, settings = write_checkout(tmp_path)
    workspace = write_workspace(base, tmp_path)
    monkeypatch.chdir(workspace)
    code, calls = launched(base, settings, "loose", "HANDOFF-9047", ["build it"])
    assert code == 0
    _, argv, env = calls[0]
    assert argv[5:9] == ["--permission-mode", "dontAsk", "--model", "claude-opus-5-5"]
    hard_stops = ["-p", "--permission-prompts", "none", "--max-turns", "60"]
    carried = str(Path(argv[4]).with_name("CLAUDE.md"))
    assert argv[9:] == [
        *hard_stops,
        "--max-budget-usd",
        "15",
        "--append-system-prompt-file",
        carried,
        "build it",
    ]
    rendered = json.loads(Path(argv[4]).read_text())
    allowed = [
        str(workspace / p) for p in ("kgme/toy.py", "docs/audit/toy.md", "tests", "logs/scratch")
    ]
    assert rendered["sandbox"]["filesystem"]["allowWrite"] == allowed, "the workspace's files"
    edits = [r for r in rendered["permissions"]["allow"] if r.startswith("Edit(")]
    assert edits == [
        f"Edit(/{workspace}/kgme/toy.py)", f"Edit(/{workspace}/docs/audit/toy.md)",
        f"Edit(/{workspace}/tests/**)", f"Edit(/{workspace}/logs/scratch/**)",
    ]  # fmt: skip
    assert all(e.startswith("Edit(//") for e in edits), "an absolute Edit rule is written //"
    assert env[loop_outputs.ENV_HANDOFF] == "HANDOFF-9047"
    assert env["UV_NO_SYNC"] == "1" and env["UV_CACHE_DIR"] == str(
        workspace / "logs" / "scratch" / "uv-cache"
    ), "uv's cache inside the fence (measured live, 2026-10-21)"
    assert loop_outputs.read_outputs(paths.scratch_dir(settings, base), env) == tuple(
        ["kgme/toy.py", "docs/audit/toy.md", *loop_outputs.ALWAYS]
    ), "the guard reads the same fence the sandbox enforces"


@pytest.mark.blocking
def test_loose_refuses_without_caps_model_or_template(tmp_path: Path, monkeypatch, capsys) -> None:
    base, settings = write_checkout(tmp_path)
    monkeypatch.chdir(write_workspace(base, tmp_path))
    assert launched(base, settings, "loose")[0] == 2
    assert launched(base, {**settings, "sessions": {}}, "loose", "HANDOFF-9047")[0] == 2
    assert launched(base, {**settings, "models": {"reviewer": "x"}}, "work")[0] == 2
    (base / session.TEMPLATES / "work.json").unlink()
    assert launched(base, settings, "work")[0] == 2
    err = capsys.readouterr().err
    assert "--handoff" in err and "[sessions]" in err and "builder" in err and "Michou" in err


@pytest.mark.blocking
def test_loose_starts_only_from_a_worktree_of_this_repository(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The live `loose` cell (2026-10-21): the sandbox let a Bash line write to the working
    directory outside `allowWrite`, a recorded residual; so `loose` never starts in the main
    checkout (Michou, 2026-10-21), nor from a folder that is not a worktree of this
    repository (review cycle 1 F1)."""
    base, settings = write_checkout(tmp_path)
    for inside in (base, base / "docs"):
        monkeypatch.chdir(inside)
        assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    monkeypatch.chdir(unrelated)
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    err = capsys.readouterr().err
    assert "outside the main checkout" in err and "worktree of" in err
    monkeypatch.chdir(write_workspace(base, tmp_path))
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 0


@pytest.mark.blocking
@pytest.mark.parametrize(
    "extra",
    [
        ["--allowedTools", "WebFetch"],
        ["--allowed-tools=WebFetch"],
        ["--dangerously-skip-permissions"],
        ["--permission-mode", "bypassPermissions"],
        ["--settings", "/tmp/x.json"],
        ["--setting-sources", "user"],
        ["--add-dir", "/"],
        ["--max-turns", "999"],
        ["--model", "other"],
    ],
)
def test_extra_arguments_never_widen_a_level(tmp_path: Path, extra: list, capsys) -> None:
    base, settings = write_checkout(tmp_path)
    assert launched(base, settings, "work", None, extra)[0] == 2
    assert "not allowed" in capsys.readouterr().err
    assert launched(base, settings, "work", None, ["--verbose", "a prompt"])[0] == 0


@pytest.mark.blocking
@pytest.mark.parametrize(
    "rel,text",
    [
        ("docs/handoff/done/toy.md", TOY.replace("status: open", "status: done")),
        ("docs/handoff/proposed/toy.md", TOY.replace("status: open", "status: proposed")),
        ("docs/handoff/toy.md", TOY.replace("status: open", "status: done")),
        ("docs/handoff/toy.md", TOY.replace("from: michou", "from: claude-code")),
    ],
)
def test_loose_runs_only_an_executable_handoff(
    tmp_path: Path, monkeypatch, rel: str, text: str, capsys
) -> None:
    base, settings = write_checkout(tmp_path, {rel: text})
    monkeypatch.chdir(write_workspace(base, tmp_path))
    assert launched(base, settings, "loose", "HANDOFF-9047")[0] == 2
    assert "not executable" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_start_note_and_its_payload_are_the_main_checkouts(tmp_path: Path, monkeypatch) -> None:
    base, settings = write_checkout(tmp_path)
    workspace = write_workspace(base, tmp_path)
    monkeypatch.chdir(workspace)
    _, calls = launched(base, settings, "loose", "HANDOFF-9047")
    copy = Path(calls[0][1][4])
    found = ledger.read(ledger.read_default_dirs(settings, workspace))
    [note] = [e for e in found if e["job"] == "session"]
    digest = session.sha256_text(copy.read_text())
    assert note["summary"] == f"session loose: settings sha256={digest[:16]} model=claude-opus-5-5"
    data, why = ledger.read_payload(base, note)
    assert why == "", "the payload resolves from the main checkout"
    record = json.loads(data)
    assert record["argv"] == calls[0][1] and record["settings_sha256"] == digest
    assert {"claude_version", "template_sha256", "model", "level", "workspace"} <= set(record)
    assert not list(workspace.rglob("session-*.json")), "no payload in the workspace"


@pytest.mark.blocking
def test_a_job_writing_from_a_worktree_writes_the_main_ledger(tmp_path: Path) -> None:
    """Review cycle 1 F4: `read_base_dirs`, which every job uses, resolves the main checkout
    too; a folder that is not a git checkout (a test's isolated streams) keeps its own."""
    base, settings = write_checkout(tmp_path)
    workspace = write_workspace(base, tmp_path)
    assert ledger.read_base_dirs(settings, workspace).ledger == paths.ledger_dir(settings, base)
    alone = tmp_path / "alone"
    alone.mkdir()
    assert ledger.read_base_dirs(settings, alone).ledger == paths.ledger_dir(settings, alone)


@pytest.mark.blocking
def test_a_dry_run_starts_nothing_and_writes_only_a_note(tmp_path: Path, capsys) -> None:
    base, settings = write_checkout(tmp_path)
    calls = []
    code = session.run_session(
        "work", None, [], base, settings, dry_run=True, execute=lambda *a: calls.append(a)
    )
    assert code == 0 and calls == []
    assert not (base / "logs" / "scratch" / "sessions").exists()
    assert "--permission-mode auto" in capsys.readouterr().out
    notes = ledger.read(ledger.read_default_dirs(settings, base))
    assert [e["key"] for e in notes] == ["session:work:dry-run"]


@pytest.mark.blocking
def test_the_cli_reads_its_own_flags_and_passes_only_what_follows_dashes(monkeypatch) -> None:
    """Found running the acceptance by hand (2026-10-21): `--dry-run` after the level was
    taken as an extra `claude` argument, so the launcher started `claude`."""
    from kgme import cli

    seen = []
    monkeypatch.setattr(session, "run_session", lambda *a, **k: seen.append(a) or 0)
    assert cli.main(["session", "tight", "--dry-run"]) == 0
    assert cli.main(["session", "loose", "--handoff", "HANDOFF-9047", "--", "build it", "-x"]) == 0
    (level, handoff, extra, _, _, dry), (level2, handoff2, extra2, _, _, dry2) = seen
    assert (level, handoff, extra, dry) == ("tight", None, [], True)
    assert (level2, handoff2, extra2, dry2) == ("loose", "HANDOFF-9047", ["build it", "-x"], False)


@pytest.mark.blocking
def test_the_applied_templates_declare_what_adr_022_says() -> None:
    """The templates are human paths Michou applies (HANDOFF-0045 §5); this holds them to
    ADR-022 and to his rulings."""
    loaded = {
        level: json.loads((APPLIED / f"{level}.json").read_text()) for level in session.LEVELS
    }
    tight, work, loose = loaded["tight"], loaded["work"], loaded["loose"]
    assert tight["permissions"]["disableAutoMode"] == "disable"
    assert "allow" not in tight["permissions"]
    for level in (work, loose):
        assert level["permissions"]["disableBypassPermissionsMode"] == "disable"
        sandbox = level["sandbox"]
        assert (sandbox["enabled"], sandbox["allowUnsandboxedCommands"]) == (True, False)
        assert sandbox["failIfUnavailable"] is True
    assert work["sandbox"]["filesystem"]["allowWrite"] == ["{repo}", "{tmp}"]
    assert loose["sandbox"]["filesystem"]["allowWrite"] == ["{outputs}"]
    assert "Edit({outputs})" in loose["permissions"]["allow"]
    staging = [
        r
        for r in loose["permissions"]["allow"]
        if r.startswith(("Bash(git add", "Bash(git commit"))
    ]
    assert staging == [], "a loose builder never stages or commits; the loop commits (Michou)"
    assert "network" not in loose["sandbox"], "no network domains"


@pytest.mark.blocking
def test_f18_loose_loads_no_project_settings_and_carries_claude_md(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 5 F18, Michou's ruling (option A, ADR-022 addendum of 2026-10-21): `loose`
    launches with `--setting-sources local`, so the project's broad allows never join its pinned
    list; the main checkout's committed `CLAUDE.md` is carried with
    `--append-system-prompt-file`, its sha256 in the start note. `tight` and `work` keep
    `project,local`."""
    import subprocess

    base, settings = write_checkout(tmp_path)
    (base / "CLAUDE.md").write_text("# The constitution\nRead it.\n")
    subprocess.run(["git", "add", "CLAUDE.md"], cwd=base, check=True)
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@l", "commit", "-qm", "c"],
        cwd=base,
        check=True,
    )
    (base / "CLAUDE.md").write_text("# an uncommitted edit\n")
    monkeypatch.chdir(write_workspace(base, tmp_path))
    code, calls = launched(base, settings, "loose", "HANDOFF-9047", ["build it"])
    assert code == 0
    argv = calls[0][1]
    assert argv[:3] == ["claude", "--setting-sources", "local"]
    carried = Path(argv[argv.index("--append-system-prompt-file") + 1])
    assert carried.read_text().startswith("# The constitution\nRead it.\n"), "CLAUDE.md first"
    found = [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]
    record = json.loads(ledger.read_payload(base, found[-1])[0])
    assert record["claude_md_sha256"] == session.sha256_text(carried.read_text())
    monkeypatch.chdir(base)
    _, interactive = launched(base, settings, "work")
    assert interactive[0][1][:3] == ["claude", "--setting-sources", "project,local"]
    assert "--append-system-prompt-file" not in interactive[0][1]


@pytest.mark.blocking
def test_0056_loose_carries_claude_md_then_the_skill_then_the_slice(
    tmp_path: Path, monkeypatch
) -> None:
    """HANDOFF-0056 §3: one carried file, `CLAUDE.md` first, then the committed `kgme-atlas`
    skill, then the handoff's slice built from the workspace; the start note records the
    slice's sha256, its token estimate, and how many nodes were cut."""
    import subprocess

    base, settings = write_checkout(tmp_path)
    (base / "kgme").mkdir()
    (base / "kgme" / "toy.py").write_text('"""The toy."""\n')
    (base / "skills" / "kgme-atlas").mkdir(parents=True)
    (base / session.SKILL).write_text("# kgme-atlas\nAsk for a slice.\n")
    subprocess.run(["git", "add", "-A"], cwd=base, check=True)
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@l", "commit", "-qm", "s"],
        cwd=base,
        check=True,
    )
    monkeypatch.chdir(write_workspace(base, tmp_path))
    code, calls = launched(base, settings, "loose", "HANDOFF-9047", ["build it"])
    assert code == 0
    argv = calls[0][1]
    text = Path(argv[argv.index("--append-system-prompt-file") + 1]).read_text()
    first, skill, slice_ = (
        text.index("# Fixture constitution"),
        text.index("# kgme-atlas"),
        text.index("# Atlas slice"),
    )
    assert first < skill < slice_, "CLAUDE.md, then the skill, then the slice"
    assert "kgme/toy.py" in text[slice_:], "the slice of the toy's Outputs"
    found = [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]
    record = json.loads(ledger.read_payload(base, found[-1])[0])
    assert record["carried"] == ["CLAUDE.md", session.SKILL, "slice"]
    assert record["slice_sha256"] == session.sha256_text(text[slice_:])
    assert record["slice_tokens"] > 0 and record["slice_cut"] == 0


@pytest.mark.blocking
def test_0056_a_loose_dry_run_shows_the_carried_file_in_order(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    base, settings = write_checkout(tmp_path)
    monkeypatch.chdir(write_workspace(base, tmp_path))
    code = session.run_session(
        "loose", "HANDOFF-9047", [], base, settings, dry_run=True, execute=lambda *a: None
    )
    assert code == 0
    out = capsys.readouterr().out
    carried = out.split("--- carried: CLAUDE.md, slice ---\n", 1)[1]
    assert carried.index("# Fixture constitution") < carried.index("# Atlas slice: HANDOFF-9047")
    note = [
        e for e in ledger.read(ledger.read_default_dirs(settings, base)) if e["job"] == "session"
    ]
    assert "slice sha256=" in note[-1]["summary"]
