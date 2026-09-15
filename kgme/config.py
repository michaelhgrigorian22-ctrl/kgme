"""Read `kgme.toml`, the one configuration file (ADR-015).

Purpose: the only module that opens the configuration file. Everything else receives the
parsed dict as an argument, so a grep for `read_config` lists every place configuration
enters. No defaults are invented here; a missing key is a loud KeyError at the caller.
Inputs: `kgme.toml` at the repository root, or an explicit path for tests.
Outputs: a dict of the parsed TOML.
Side effects: reads one file. Writes nothing.
"""

import tomllib
from pathlib import Path


def config_path() -> Path:
    """`kgme.toml` next to the `kgme/` package. Pure: derived from this file's location."""
    return Path(__file__).resolve().parent.parent / "kgme.toml"


def read_config(path: Path | None = None) -> dict:
    """Parse the TOML at `path` (default: the repository's `kgme.toml`). The one read."""
    with open(path or config_path(), "rb") as handle:
        return tomllib.load(handle)
