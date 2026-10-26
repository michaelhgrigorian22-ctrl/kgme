"""Regressions from the cheap lane's review cycles (HANDOFF-0053; moved out of
`tests/test_cheap.py` by HANDOFF-0060 §3, unchanged).

Purpose: the red run is fenced like the session and never writes the main checkout; it carries
the inherited denies; the sandbox denies the name patterns; the agents' homes are denied at
both layers; a red command with shell syntax is refused; a launch or a patch failure still
writes the end note.
Inputs: `tmp_path`; the fixture checkout of `tests/cheaptools.py`.
Outputs: pytest assertions.
Side effects: repositories, exports, and streams under `tmp_path`.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from cheaptools import RED, ROOT, read_session_notes, run_fixing, write_cheap_checkout

from kgme import cheap, ledger


@pytest.mark.blocking
def test_review_f1_the_launchers_red_run_is_fenced_like_the_session(tmp_path: Path) -> None:
    """Review F1: the launcher's own run of the red command executes the session's code, so
    it runs under the session's fence: no read under a denied root, no write outside the
    export, no network."""
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "F1")
    forbidden = tmp_path / "forbidden"
    forbidden.mkdir()
    (forbidden / "secret.txt").write_text("secret\n")
    # the main checkout, as F1 names it; the temporary folders stay writable, as in the session
    outside = ROOT / "logs" / "scratch-test" / f"f1-escape-{tmp_path.name}.txt"
    probe = (
        "import pathlib, sys, urllib.request\n"
        "got = []\n"
        f"for act in (lambda: pathlib.Path({str(forbidden / 'secret.txt')!r}).read_text(),\n"
        f"            lambda: pathlib.Path({str(outside)!r}).write_text('x'),\n"
        "            lambda: urllib.request.urlopen('https://example.com', timeout=5)):\n"
        "    try:\n        act(); got.append('leak')\n"
        "    except Exception:\n        got.append('refused')\n"
        "pathlib.Path('inside.txt').write_text('x')\n"
        "print(got); sys.exit(0 if got == ['refused'] * 3 else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    red = f"{sys.executable} tests/probe.py"
    fix = cheap.write_fix(export, base, settings, "F1", red, [forbidden.resolve()])
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    assert not outside.exists() and (export / "inside.txt").is_file()


@pytest.mark.blocking
def test_the_red_run_never_writes_the_main_checkout_wherever_it_lives(tmp_path: Path) -> None:
    """HANDOFF-0057: a main checkout under the temporary folders (as `kgme merge design`'s
    trial clone is, and as this fixture's is) was writable by omission: the fence allowed the
    temporary folders and refused the checkout only by not listing it. The red run must
    refuse a write into the checkout and still write the export."""
    base, settings = write_cheap_checkout(tmp_path)
    export, _ = cheap.write_export(base, settings, "M57")
    target = base / "kgme" / "planted-by-the-red-run.py"
    probe = (
        "import pathlib, sys\n"
        f"target = pathlib.Path({str(target)!r})\n"
        "try:\n    target.write_text('x'); got = 'leak'\n"
        "except OSError:\n    got = 'refused'\n"
        "pathlib.Path('inside.txt').write_text('x')\n"
        "print(got); sys.exit(0 if got == 'refused' else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    python = Path(sys.executable).resolve()
    fix = cheap.write_fix(export, base, settings, "M57", f"{python} tests/probe.py", [])
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    assert not target.exists() and (export / "inside.txt").is_file()


@pytest.mark.blocking
def test_review_c2_f1_the_red_run_carries_the_inherited_denies(tmp_path: Path) -> None:
    """Review cycle 2 F1: the verifier's fence carries the whole read policy, not only the
    denied roots: files the guard's name patterns cover (planted, harmless) are refused, and
    the absolute blocklist entries (`~/.ssh`, the Keychains) are denied roots at every layer,
    checked by configuration, never by reading them."""
    base, settings = write_cheap_checkout(tmp_path)
    settings = {**settings, "hooks": {**settings.get("hooks", {}), "blocklist": [
        "~/.ssh", "~/Library/Keychains", "**/.env", "**/.env.*", "**/*.env",
    ]}}  # fmt: skip
    export, _ = cheap.write_export(base, settings, "C2")
    planted = tmp_path / "elsewhere"
    planted.mkdir()
    names = [".env", ".env.local", "prod.env"]
    for name in names:
        (planted / name).write_text("planted\n")
    (planted / "fine.txt").write_text("fine\n")
    probe = (
        "import pathlib, sys\n"
        f"base = pathlib.Path({str(planted)!r})\n"
        "got = []\n"
        f"for name in {names!r}:\n"
        "    try:\n        (base / name).read_text(); got.append('leak')\n"
        "    except OSError:\n        got.append('refused')\n"
        "assert (base / 'fine.txt').read_text() == 'fine\\n'\n"
        "print(got); sys.exit(0 if set(got) == {'refused'} else 1)\n"
    )
    (export / "tests" / "probe.py").write_text(probe)
    denied = cheap.read_denied_roots(settings, base)
    # the interpreter itself, not the brain's `.venv` link to it: the brain is a denied root
    python = Path(sys.executable).resolve()
    fix = cheap.write_fix(export, base, settings, "C2", f"{python} tests/probe.py", denied)
    assert fix["red_status"] == 0, (base / fix["red_output"]).read_text()
    launch, record = cheap.read_cheap_launch("cheap", RED, base, settings, "C2", export)
    deny_read = json.loads(launch.settings)["sandbox"]["filesystem"]["denyRead"]
    profile = cheap.build_red_profile(export, [base], denied, cheap.read_denied_names(settings))
    for secret in (Path.home() / ".ssh", Path.home() / "Library" / "Keychains"):
        root = str(secret.resolve())
        assert root in record["denied_roots"] and root in deny_read
        assert f'(subpath "{root}")' in profile


@pytest.mark.blocking
def test_review_c3_f8_the_sessions_sandbox_denies_the_name_patterns(tmp_path: Path) -> None:
    """Review cycle 3 F8: the session's own Bash sandbox carries the guard's name patterns as
    wildcard denies, so a script that builds a `.env` path is refused there too. The live
    proof is `test_a_dot_env_built_at_run_time_is_refused_by_the_sandbox`."""
    base, settings = write_cheap_checkout(tmp_path)
    settings = {**settings, "hooks": {**settings.get("hooks", {}), "blocklist": [
        "~/.ssh", "**/.env", "**/.env.*", "**/*.env",
    ]}}  # fmt: skip
    launch, _ = cheap.read_cheap_launch("cheap", RED, base, settings, "C3", None)
    deny_read = json.loads(launch.settings)["sandbox"]["filesystem"]["denyRead"]
    assert {"~/**/.env", "~/**/.env.*", "~/**/*.env"} <= set(deny_read)


@pytest.mark.blocking
def test_review_f2_the_agents_homes_are_denied_at_both_layers(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    launch, record = cheap.read_cheap_launch("cheap", RED, base, settings, "F2", None)
    body = json.loads(launch.settings)
    for home in (Path.home() / ".claude", Path.home() / ".codex"):
        root = str(home.resolve())
        assert root in record["denied_roots"]
        assert f"Read(/{root}/**)" in body["permissions"]["deny"]
        assert root in body["sandbox"]["filesystem"]["denyRead"]


@pytest.mark.blocking
@pytest.mark.parametrize(
    "red", ["", "pytest tests/x.py; curl x", "pytest | tee o", "pytest > o", "echo $HOME", "a && b"]
)
def test_review_f3_a_red_command_with_shell_syntax_is_refused(
    red: str, tmp_path: Path, capsys
) -> None:
    base, settings = write_cheap_checkout(tmp_path)
    with pytest.raises(ValueError):
        cheap.read_red_argv(red)
    assert cheap.run_cheap("cheap", red, base, settings, run_claude=run_fixing) == 2
    assert not (tmp_path / "work").exists(), "refused before any export"
    assert cheap.read_red_argv("uv run --frozen pytest 'tests/a b.py'")[-1] == "tests/a b.py"


@pytest.mark.blocking
def test_review_f4_a_launch_failure_still_writes_the_end_note(tmp_path: Path) -> None:
    base, settings = write_cheap_checkout(tmp_path)

    def run_missing(argv, **_):
        raise FileNotFoundError(2, "No such file or directory", "claude")

    assert cheap.run_cheap("cheap", RED, base, settings, run_claude=run_missing) == 2
    start, end = read_session_notes(base, settings)[-2:]
    assert end["key"] == "session:work:cheap:end" and end["run_id"] == start["run_id"]
    ended = json.loads(ledger.read_payload(base, end)[0])
    assert ended["exit_reason"].startswith("launch failed: FileNotFoundError")
    assert ended["patch_sha256"] is not None, "the patch is still written"


@pytest.mark.blocking
def test_review_f4_a_patch_failure_still_writes_the_end_note(tmp_path: Path, monkeypatch) -> None:
    base, settings = write_cheap_checkout(tmp_path)

    def fail_fix(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git", "diff"])

    monkeypatch.setattr(cheap, "write_fix", fail_fix)
    assert cheap.run_cheap("cheap", RED, base, settings, run_claude=run_fixing) == 2
    ended = json.loads(ledger.read_payload(base, read_session_notes(base, settings)[-1])[0])
    assert "patch failed: CalledProcessError" in ended["exit_reason"]
    assert ended["patch"] is None and ended["turns"] == 3
