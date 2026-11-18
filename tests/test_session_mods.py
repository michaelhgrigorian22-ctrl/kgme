"""Tests for KGME's mods (HANDOFF-0059, ADR-024): what a level loads, and the `make check` step.

Purpose: `kgme session` passes `--plugin-dir` for each mod `kgme.toml [mods]` names for the
level, and a `loose` session's command line carries none, whatever the table says; a name that
is not a mod folder is refused. The check holds what `claude plugin validate` lists to
`[mods.allows]`: the exact listing passes, a hook or call more is blocking, and so is a mod
with no entry; and with the real `claude`, planting a `tool.call` hook in a mod folder turns
the check red.
Inputs: fixture checkouts under `tmp_path`; validate reports as `claude plugin validate --json`
writes them; the real `claude`, where it is installed.
Outputs: pytest assertions.
Side effects: files under `tmp_path`; `claude plugin validate` in the last test; nothing is
launched.
"""

import json
import shutil
from pathlib import Path

import pytest
from sessiontools import launched, write_checkout, write_workspace

from kgme import mods, session_logic

COCKPIT = ["session.start", "ui.render", "$.ui", "$.clock", "$.http", "$.state"]
CAPTURE = ["session.start", "command.run", "$.command", "$.process"]
ALLOWS = {"kgme-cockpit": COCKPIT, "kgme-capture": CAPTURE}


def report(*notes: str, success: bool = True) -> dict:
    """A `claude plugin validate --json` report holding one hooks file with these notes."""
    return {
        "success": success,
        "manifest": {"errors": []},
        "contents": [{"errors": [], "notes": list(notes)}],
    }


CAPTURE_REPORT = report(
    "./register.tsx hooks: session.start, command.run{command=capture}",
    "./register.tsx answers its own command: command.run{command=capture}",
    "./register.tsx calls: $.command.register, $.process.run",
)
COCKPIT_REPORT = report(
    "./register.tsx hooks: session.start, ui.render{component=Pane, requestId=kgme-cockpit}",
    "./register.tsx calls: $.clock.every, $.http.fetch, $.state.get, $.state.set, "
    "$.ui.open, $.ui.resolve, $.ui.status",
    "./register.tsx state writes: kgme-cockpit.snapshot",
)


def write_mod(base: Path, name: str) -> Path:
    folder = base / "mods" / name
    (folder / ".claude-plugin").mkdir(parents=True)
    (folder / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": name, "version": "0.1.0"})
    )
    return folder


@pytest.mark.blocking
def test_a_level_loads_the_mods_its_table_names(tmp_path: Path) -> None:
    base, settings = write_checkout(tmp_path)
    for name in ("kgme-cockpit", "kgme-capture"):
        write_mod(base, name)
    settings["mods"] = {"work": ["kgme-cockpit", "kgme-capture"], "tight": ["kgme-cockpit"]}
    for level, names in (("work", ["kgme-cockpit", "kgme-capture"]), ("tight", ["kgme-cockpit"])):
        code, calls = launched(base, settings, level)
        assert code == 0
        argv = calls[0][1]
        dirs = [argv[i + 1] for i, a in enumerate(argv) if a == "--plugin-dir"]
        assert dirs == [str(base / "mods" / n) for n in names], level


@pytest.mark.blocking
def test_with_no_table_no_level_loads_a_mod(tmp_path: Path) -> None:
    base, settings = write_checkout(tmp_path)
    code, calls = launched(base, settings, "work")
    assert code == 0 and "--plugin-dir" not in calls[0][1]


@pytest.mark.blocking
def test_a_loose_session_carries_no_plugin_dir_whatever_the_table_says(
    tmp_path: Path, monkeypatch
) -> None:
    base, settings = write_checkout(tmp_path)
    write_mod(base, "kgme-cockpit")
    settings["mods"] = {"loose": ["kgme-cockpit"], "cheap": ["kgme-cockpit"]}
    workspace = write_workspace(base, tmp_path)
    monkeypatch.chdir(workspace)
    code, calls = launched(base, settings, "loose", "HANDOFF-9047", ["build it"])
    assert code == 0 and "--plugin-dir" not in calls[0][1]
    assert mods.level_mods("loose", settings) == [] and mods.level_mods("cheap", settings) == []
    with pytest.raises(ValueError, match="loose loads no mod"):
        session_logic.build_argv(
            "loose",
            Path("s.json"),
            "m",
            {"max_turns": 1, "max_budget_usd": 1},
            [],
            None,
            (Path("x"),),
        )


@pytest.mark.blocking
@pytest.mark.parametrize("names", [["../control"], ["kgme cockpit"], "kgme-cockpit", [3]])
def test_a_name_that_is_not_a_plain_mod_name_is_refused(names) -> None:
    with pytest.raises(ValueError, match="list of mod folder names"):
        mods.level_mods("work", {"mods": {"work": names}})


@pytest.mark.blocking
def test_a_named_mod_that_is_not_a_mod_folder_stops_the_launch(tmp_path: Path, capsys) -> None:
    base, settings = write_checkout(tmp_path)
    (base / "mods" / "empty").mkdir(parents=True)
    settings["mods"] = {"work": ["empty"]}
    code, calls = launched(base, settings, "work")
    assert code == 2 and calls == []
    assert "names empty: not a mod folder" in capsys.readouterr().err


@pytest.mark.blocking
def test_the_listing_is_hook_events_and_dollar_nouns() -> None:
    assert mods.listing(CAPTURE_REPORT) == set(CAPTURE)
    assert mods.listing(COCKPIT_REPORT) == set(COCKPIT)


@pytest.mark.blocking
def test_handoff_0074_a_trailing_note_is_dropped_from_a_hooked_event() -> None:
    """The validate format of 2026-11-17, verbatim: a note in parentheses after the event."""
    noted = report(
        "./register.tsx hooks: session.start, ui.render{component=Pane, requestId=kgme-cockpit}"
        " (default matcher key: plugin)",
        *COCKPIT_REPORT["contents"][0]["notes"][1:],
    )
    assert mods.listing(noted) == set(COCKPIT)
    bare = report("./register.tsx hooks: ui.render (default matcher key: plugin)")
    assert mods.listing(bare) == {"ui.render"}
    assert mods.check_mod("kgme-cockpit", noted, ALLOWS) == []
    stranger = report(
        "./register.tsx hooks: tool.call{tool=Bash} (default matcher key: plugin), ui.renderX"
    )
    assert mods.check_mod("kgme-cockpit", stranger, ALLOWS) == [
        "hooks or calls its handoff did not name: tool.call, ui.renderX"
    ]


@pytest.mark.blocking
def test_the_exact_listing_passes_and_anything_more_is_blocking() -> None:
    assert mods.check_mod("kgme-capture", CAPTURE_REPORT, ALLOWS) == []
    assert mods.check_mod("kgme-cockpit", COCKPIT_REPORT, ALLOWS) == []
    planted = report(
        *CAPTURE_REPORT["contents"][0]["notes"], "./register.tsx hooks: tool.call{tool=Bash}"
    )
    assert mods.check_mod("kgme-capture", planted, ALLOWS) == [
        "hooks or calls its handoff did not name: tool.call"
    ]
    fetches = report(
        "./register.tsx hooks: session.start", "./register.tsx calls: $.http.fetch, $.fs.write"
    )
    assert mods.check_mod("kgme-capture", fetches, ALLOWS) == [
        "hooks or calls its handoff did not name: $.fs, $.http"
    ]


@pytest.mark.blocking
def test_a_mod_with_no_allows_entry_or_a_failed_validation_is_blocking() -> None:
    assert mods.check_mod("stranger", CAPTURE_REPORT, ALLOWS) == [
        "no kgme.toml [mods.allows] entry names what its handoff allows"
    ]
    failed = report(success=False)
    failed["contents"][0]["errors"] = ["next is declared again"]
    assert mods.check_mod("kgme-capture", failed, ALLOWS) == [
        "claude plugin validate: next is declared again"
    ]


@pytest.mark.blocking
def test_a_folder_that_is_not_a_mod_or_cannot_be_validated_is_blocking(
    tmp_path: Path, capsys
) -> None:
    (tmp_path / "mods" / "loose-file").mkdir(parents=True)
    write_mod(tmp_path, "kgme-capture")
    assert mods.run_check(tmp_path, {"mods": {"allows": ALLOWS}}, claude="") == 1
    out = capsys.readouterr().out
    assert "mods/loose-file: not a mod folder" in out
    assert "mods/kgme-capture: claude is not on PATH, so the mod cannot be validated" in out


@pytest.mark.blocking
def test_with_no_mod_folder_the_check_passes(tmp_path: Path) -> None:
    assert mods.run_check(tmp_path, {}, claude="") == 0


@pytest.mark.blocking
@pytest.mark.skipif(shutil.which("claude") is None, reason="claude is not installed here")
def test_planting_a_tool_call_hook_turns_the_check_red(tmp_path: Path, capsys) -> None:
    """HANDOFF-0059 acceptance: the real `claude plugin validate` lists the planted hook."""
    folder = write_mod(tmp_path, "kgme-capture")
    (folder / "hooks").mkdir()
    (folder / "hooks" / "hooks.json").write_text('{ "modules": ["./register.ts"] }')
    module = folder / "hooks" / "register.ts"
    module.write_text(
        "import type { Register } from 'claude-code'\n"
        "export const register: Register = on => {\n"
        "  on('session.start', async ($, e, next) => {\n"
        "    await $.command.register({ name: 'capture', description: 'c' })\n"
        "    return next(e)\n"
        "  })\n"
        "}\n"
    )
    settings = {"mods": {"allows": ALLOWS}}
    assert mods.run_check(tmp_path, settings) == 0, capsys.readouterr().out
    planted = "  on('tool.call', ($, e, next) => next(e))\n}\n"
    module.write_text(module.read_text().removesuffix("}\n") + planted)
    assert mods.run_check(tmp_path, settings) == 1
    assert "hooks or calls its handoff did not name: tool.call" in capsys.readouterr().out


@pytest.mark.blocking
def test_review_c1_f1_a_symlinked_mods_folder_is_neither_loaded_nor_validated(
    tmp_path: Path, capsys
) -> None:
    """Review cycle 1 F1: only the leaf was checked, so a `mods/` linked out of the repository
    loaded and validated a regular child."""
    base, settings = write_checkout(tmp_path)
    outside = tmp_path / "outside"
    write_mod(outside, "kgme-cockpit")
    (base / "mods").symlink_to(outside / "mods")
    settings["mods"] = {"work": ["kgme-cockpit"], "allows": ALLOWS}
    code, calls = launched(base, settings, "work")
    assert code == 2 and calls == []
    assert "mods/ is a symlink; no mod is loaded through one" in capsys.readouterr().err
    assert mods.run_check(base, settings, claude="") == 1
    out = capsys.readouterr().out
    assert "mods: mods/ is a symlink; no mod is loaded through one [blocking]" in out
    assert "kgme mods: 0 mod folders, 1 blocking" in out


@pytest.mark.blocking
def test_review_c1_f2_a_level_with_mods_names_its_checkout_as_the_uv_project(
    tmp_path: Path, monkeypatch
) -> None:
    """Review cycle 1 F2: `/capture` runs `uv run --frozen kgme capture`; the launcher names the
    checkout as uv's project, so where the terminal stands does not matter."""
    base, settings = write_checkout(tmp_path)
    write_mod(base, "kgme-capture")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    settings["mods"] = {"work": ["kgme-capture"]}
    code, calls = launched(base, settings, "work")
    assert code == 0 and calls[0][2]["UV_PROJECT"] == str(base)
    settings["mods"] = {}
    code, calls = launched(base, settings, "work")
    assert code == 0 and calls[0][2].get("UV_PROJECT") != str(base)  # no mod, no project named
