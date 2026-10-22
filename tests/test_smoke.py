"""Smoke tests for HANDOFF-0025: the package imports, paths derive from the root, the CLI maps.

Purpose: keep `make check` meaningful before the first real module lands. Every test carries
an ADR-016 class marker, as ADR-016 requires of every test under `tests/`.
Inputs: the repository as checked out.
Outputs: pytest assertions.
Side effects: none. `read_config` reads `kgme.toml`; nothing is written.
"""

from pathlib import Path

import pytest

from kgme import cli, config, paths

SETTINGS = config.read_config()


@pytest.mark.blocking
def test_root_holds_config_and_package() -> None:
    root = paths.root()
    assert (root / "kgme.toml").is_file()
    assert (root / "kgme" / "__init__.py").is_file()


@pytest.mark.blocking
def test_paths_are_absolute_and_under_root() -> None:
    for path in (
        paths.vault(SETTINGS),
        paths.ledger_dir(SETTINGS),
        paths.trace_dir(SETTINGS),
        paths.scratch_dir(SETTINGS),
    ):
        assert path.is_absolute()
        assert path.is_relative_to(paths.root())


@pytest.mark.blocking
def test_paths_module_is_pure() -> None:
    """ADR-015: logic imports nothing from the effects layer."""
    source = Path(paths.__file__).read_text()
    assert "import tomllib" not in source
    assert "open(" not in source
    assert "from kgme import config" not in source


@pytest.mark.blocking
def test_config_has_every_section_phase_1_reads() -> None:
    assert set(SETTINGS) >= {"paths", "cockpit", "clean", "hooks", "models"}
    assert SETTINGS["models"]["reviewer"] == "gpt-6-astra"
    assert "Read" in SETTINGS["hooks"]["read_only_tools"]


@pytest.mark.blocking
def test_tier1_paths_are_absolute_after_resolution() -> None:
    for path in paths.tier1_paths(SETTINGS):
        assert path.is_absolute()


@pytest.mark.blocking
def test_cli_lists_eleven_subcommands_and_lint_is_a_no_op() -> None:
    names = set(cli.build_parser()._subparsers._group_actions[0].choices)
    assert names == {
        "atlas",
        "session",
        "brief",
        "capture",
        "clean",
        "daily",
        "lint",
        "review",
        "cockpit",
        "ledger",
        "sync",
    }
    assert cli.main(["lint"]) == 0
    assert cli.main(["cockpit"]) == 2


@pytest.mark.advisory
def test_models_table_in_reader_matches_config() -> None:
    """The reader and kgme.toml are kept in sync by hand; this notices drift (advisory)."""
    reader = Path(paths.root(), "docs", "readers", "review-loop.md").read_text()
    for key in ("reviewer", "reviewer_alternate", "arbiter"):
        assert f"`{SETTINGS['models'][key]}`" in reader


@pytest.mark.blocking
def test_no_secret_shaped_values_in_config() -> None:
    text = Path(paths.root(), "kgme.toml").read_text()
    for needle in ("sk-", "Bearer ", "password", "token="):
        assert needle not in text
