"""The planted artefacts of the canary matrix (ADR-013 §3, HANDOFF-0032), in a temp directory.

Purpose: every probe's target is created here at test time, never in the repository: an env
file, a Tier 1 file under a directory a test `kgme.toml` declares as a Tier 1 root, a directory
for `rm -rf` to aim at, and the guard's lists read from that test config.
Inputs: `tmp_path`; the repository's `kgme.toml` as the template of the test config.
Outputs: a `Planted`.
Side effects: files under `tmp_path`.
"""

import uuid
from dataclasses import dataclass
from pathlib import Path

from kgme import config, paths

TIER1_LINE = 'tier1_paths = ["memory/private"]'


@dataclass(frozen=True)
class Planted:
    """The probe targets, the test config, and the guard's lists read from that config."""

    env: Path
    tier1: Path
    victim: Path
    outside: Path
    marker: str
    toml: Path
    settings: dict
    blocklist: list[Path]
    patterns: list[str]
    tier1_roots: list[Path]


def plant(tmp_path: Path) -> Planted:
    """Create the targets under `tmp_path` and read the test config they belong to."""
    marker = f"canary {uuid.uuid4()}"
    env = tmp_path / ".env"
    env.write_text(marker + "\n")
    tier1 = tmp_path / "tier1" / "positions.md"
    tier1.parent.mkdir()
    tier1.write_text(marker + "\n")
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "keep.txt").write_text("keep\n")
    text = config.config_path().read_text(encoding="utf-8")
    assert TIER1_LINE in text, "the tripwire line the test config extends"
    toml = tmp_path / "kgme.toml"
    toml.write_text(text.replace(TIER1_LINE, f'tier1_paths = ["memory/private", "{tier1.parent}"]'))
    settings = config.read_config(toml)
    hooks = settings["hooks"]
    return Planted(
        env=env,
        tier1=tier1,
        victim=victim,
        outside=tmp_path / "note.md",
        marker=marker,
        toml=toml,
        settings=settings,
        blocklist=[paths.resolve(p) for p in hooks["blocklist"] if not p.startswith("**/")],
        patterns=[p[3:] for p in hooks["blocklist"] if p.startswith("**/")],
        tier1_roots=paths.tier1_paths(settings),
    )
