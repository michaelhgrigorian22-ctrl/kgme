"""Shared fixtures of the canary matrix (HANDOFF-0032): the planted artefacts and the streams.

Purpose: hand every canary test the same planted targets (`tests/policy/planted.py`), the
gitignored test streams, one run id per session, and one matrix file per tier.
Inputs: `kgme.toml`; `tmp_path`.
Outputs: fixtures.
Side effects: files under `tmp_path`; the matrix files are truncated once per session.
"""

from pathlib import Path

import pytest
from planted import Planted, plant

from kgme import canary, config, events, ledger, paths


@pytest.fixture
def planted(tmp_path: Path) -> Planted:
    return plant(tmp_path)


@pytest.fixture(scope="session")
def test_dirs() -> ledger.Dirs:
    return ledger.read_test_dirs(config.read_config())


@pytest.fixture(scope="session")
def run_id() -> str:
    return events.new_ulid()


@pytest.fixture(scope="session")
def settings_sha() -> str:
    """The digest of `~/.claude/settings.json` this run saw, read once and written into every
    intent (Michou, 2026-09-23): drift outside the repository shows in the ledger."""
    return canary.read_settings_sha()


def _fresh_matrix(name: str) -> Path:
    path = paths.scratch_test_dir(config.read_config()) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canary.MATRIX_HEADER, encoding="utf-8")
    return path


@pytest.fixture(scope="session")
def fast_matrix() -> Path:
    return _fresh_matrix("canary-fast.md")


@pytest.fixture(scope="session")
def agents_matrix() -> Path:
    return _fresh_matrix("canary-agents.md")
