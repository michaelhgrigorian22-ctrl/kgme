"""Tests for the `kgme-loop` profile (HANDOFF-0043 item 4): the canary probes it refuses.

Purpose: the supervisor's declared boundary: it reads the queue and the ledger, writes only
under `logs/`, has no network of its own, and refuses every probe the matrix plants, the
human-authored paths and the code it supervises included.
Inputs: `control/policy/profiles/kgme-loop.toml`; the planted probes.
Outputs: pytest assertions.
Side effects: none beyond the fixtures'.
"""

import pytest

from kgme import paths, policy
from tests.policy.test_manifest import check, probes

PROFILE = paths.root() / "control" / "policy" / "profiles" / "kgme-loop.toml"


@pytest.mark.blocking
def test_the_loop_profile_refuses_every_probe_and_writes_only_logs(planted) -> None:
    loop = policy.read_manifest(PROFILE)
    assert loop.kind == "python-job" and loop.network_destinations == ()
    for probe, (op, target) in probes(planted).items():
        assert not check(planted, loop, op, target).allowed, probe
    assert check(planted, loop, "read", "docs/handoff/x.md").allowed
    assert check(planted, loop, "write", "logs/scratch/loop/run/builder-0.jsonl").allowed
    for target in ("kgme/loop.py", "tests/test_loop.py", "docs/handoff/x.md", "memory/notes/x.md",
                   "control/review/arbiter-prompt.md", "kgme.toml", "CLAUDE.md"):  # fmt: skip
        assert not check(planted, loop, "write", target).allowed, target
    assert not check(planted, loop, "network", "https://api.anthropic.com/").allowed
