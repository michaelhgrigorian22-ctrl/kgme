"""Fast tier of the canary matrix (HANDOFF-0032): the manifest layer against every probe.

Purpose: every manifest in the repository parses; the Python jobs' manifests refuse each probe
and allow the job's own work; a manifest never widens the blocklist or Tier 1; symlinks are
resolved before the roots apply; the shape is strict; the agent profiles declare what the
settings file and the vendor sandbox enforce.
Inputs: `jobs/*/manifest.toml`, `cockpit/manifest.toml`, `control/policy/profiles/*.toml`, the
`planted` fixture.
Outputs: pytest assertions; one cell per job and probe in the test streams and the fast matrix.
Side effects: none outside `tmp_path` and the gitignored test paths.
"""

from pathlib import Path

import pytest

from kgme import canary, policy

ROOT = Path(__file__).resolve().parents[2]
JOBS = {
    "brief": ROOT / "jobs" / "brief" / "manifest.toml",
    "clean": ROOT / "jobs" / "clean" / "manifest.toml",
    "capture": ROOT / "jobs" / "capture" / "manifest.toml",
    "daily": ROOT / "jobs" / "daily" / "manifest.toml",
    "cockpit": ROOT / "cockpit" / "manifest.toml",
}
PROFILES = {
    "claude-builder": ROOT / "control" / "policy" / "profiles" / "claude-builder.toml",
    "codex-reviewer": ROOT / "control" / "policy" / "profiles" / "codex-reviewer.toml",
    "codex-builder": ROOT / "control" / "policy" / "profiles" / "codex-builder.toml",
}
MINIMAL = """
name = "probe"
kind = "python-job"
max_tier = 2
read_paths = {reads}
write_paths = {writes}
tools = []
network_destinations = {network}
"""


def check(planted, manifest: policy.Manifest, op: str, target: str) -> policy.Verdict:
    return policy.check(
        manifest, op, target, ROOT, planted.blocklist, planted.patterns, planted.tier1_roots
    )


def synthetic(reads="[]", writes="[]", network="[]") -> policy.Manifest:
    return policy.parse_manifest(MINIMAL.format(reads=reads, writes=writes, network=network))


def probes(planted) -> dict[str, tuple[str, str]]:
    return {
        "env": ("read", str(planted.env)),
        "tier1": ("read", str(planted.tier1)),
        "rm-rf": ("delete", str(planted.victim)),
        "write-outside": ("write", "docs/canary-probe.md"),
        "network": ("network", "http://127.0.0.1:9/"),
    }


@pytest.mark.blocking
def test_every_manifest_parses_and_names_its_worker() -> None:
    for name, path in {**JOBS, **PROFILES}.items():
        manifest = policy.read_manifest(path)
        assert manifest.name == name and manifest.max_tier in (2, 3)
        assert manifest.kind == ("agent-profile" if name in PROFILES else JOBS_KIND[name])


JOBS_KIND = {
    "brief": "python-job",
    "clean": "python-job",
    "capture": "python-job",
    "daily": "python-job",
    "cockpit": "app",
}


@pytest.mark.blocking
def test_job_manifests_refuse_every_probe(
    planted, test_dirs, run_id, settings_sha, fast_matrix, fingerprints
) -> None:
    for name, path in JOBS.items():
        manifest = policy.read_manifest(path)
        for probe, (op, target) in probes(planted).items():
            verdict = check(planted, manifest, op, target)
            detail = verdict.reason if not verdict.allowed else "manifest allowed the probe"
            canary.write_cell(
                canary.Cell(name, probe, "manifest"),
                canary.Observed(not verdict.allowed, detail),
                test_dirs,
                run_id,
                settings_sha,
                fast_matrix,
                fingerprints,
            )
            assert not verdict.allowed, (name, probe, verdict)
            assert verdict.layer == "manifest"


@pytest.mark.blocking
def test_job_manifests_allow_their_own_work(planted) -> None:
    brief = policy.read_manifest(JOBS["brief"])
    assert check(planted, brief, "read", "memory/notes/x.md").allowed
    assert check(planted, brief, "read", "memory/daily/2026-09-20.md").allowed
    assert check(planted, brief, "write", "memory/agent/brief/2026-09-20.md").allowed
    assert not check(planted, brief, "write", "memory/notes/x.md").allowed
    assert not check(planted, brief, "write", "memory/agent/other.md").allowed
    assert check(planted, brief, "tool", "read").allowed
    assert not check(planted, brief, "tool", "delete").allowed
    clean = policy.read_manifest(JOBS["clean"])
    assert check(planted, clean, "delete", "memory/agent/brief/2026-09-20.md").allowed
    assert check(planted, clean, "delete", "kgme/__pycache__/paths.cpython-313.pyc").allowed
    assert check(planted, clean, "delete", "tests/policy/__pycache__").allowed
    assert check(planted, clean, "delete", ".ruff_cache/x").allowed
    assert not check(planted, clean, "delete", "logs/ledger/2026-09.jsonl").allowed
    assert not check(planted, clean, "delete", "kgme/paths.py").allowed
    assert not check(planted, clean, "delete", "docs/x.md").allowed
    capture = policy.read_manifest(JOBS["capture"])
    assert check(planted, capture, "read", "memory/templates/reminder.md").allowed
    assert check(planted, capture, "write", "memory/notes/pay-the-renewal.md").allowed
    assert check(planted, capture, "write", "memory/inbox/friction-log.md").allowed
    assert check(planted, capture, "write", "memory/daily/2026-10-16.md").allowed
    assert not check(planted, capture, "write", "memory/inbox/other.md").allowed
    assert not check(planted, capture, "write", "memory/agent/x.md").allowed
    assert not check(planted, capture, "write", "memory/templates/reminder.md").allowed
    assert not check(planted, capture, "read", "docs/handoff/x.md").allowed
    assert not check(planted, capture, "tool", "git").allowed
    daily = policy.read_manifest(JOBS["daily"])
    assert check(planted, daily, "read", "docs/handoff/done/x.md").allowed
    assert check(planted, daily, "read", "docs/audit/x.md").allowed
    assert check(planted, daily, "write", "memory/daily/2026-10-16.md").allowed
    assert check(planted, daily, "tool", "git").allowed
    assert not check(planted, daily, "write", "memory/notes/x.md").allowed
    assert not check(planted, daily, "write", "memory/inbox/friction-log.md").allowed
    assert not check(planted, daily, "read", "docs/adr/x.md").allowed
    cockpit = policy.read_manifest(JOBS["cockpit"])
    assert check(planted, cockpit, "read", "logs/ledger/2026-09.jsonl").allowed
    assert not check(planted, cockpit, "write", "cockpit/x").allowed
    # the network check keys on the declaration: a manifest that declares 127.0.0.1:9 may reach it
    declared = synthetic(network='["127.0.0.1:9"]')
    assert check(planted, declared, "network", "http://127.0.0.1:9/").allowed
    assert not check(planted, declared, "network", "http://127.0.0.1:8642/").allowed
    assert policy.destination("https://api.anthropic.com/v1/messages") == "api.anthropic.com:443"
    assert policy.destination("api.openai.com:443") == "api.openai.com:443"


@pytest.mark.blocking
def test_a_manifest_never_widens_the_blocklist_or_tier_1(planted) -> None:
    wide = synthetic(reads=f'["{planted.env.parent}", "/"]', writes=f'["{planted.env.parent}"]')
    assert not check(planted, wide, "read", str(planted.env)).allowed
    assert not check(planted, wide, "read", str(planted.tier1)).allowed
    assert not check(planted, wide, "read", "memory/private/positions.md").allowed
    assert not check(planted, wide, "write", str(planted.tier1)).allowed
    assert check(planted, wide, "read", str(planted.victim / "keep.txt")).allowed


@pytest.mark.blocking
def test_symlinks_are_resolved_before_the_roots_apply(planted, tmp_path: Path) -> None:
    agent = tmp_path / "agent"
    agent.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (agent / "link").symlink_to(elsewhere)
    manifest = synthetic(writes=f'["{agent}"]')
    assert check(planted, manifest, "write", str(agent / "real.md")).allowed
    assert not check(planted, manifest, "write", str(agent / "link" / "x.md")).allowed
    assert not check(planted, manifest, "delete", str(agent / "link")).allowed


@pytest.mark.blocking
def test_manifest_shape_is_strict() -> None:
    good = MINIMAL.format(reads="[]", writes="[]", network="[]")
    with pytest.raises(ValueError, match="missing"):
        policy.parse_manifest(good.replace("tools = []\n", ""))
    with pytest.raises(ValueError, match="unknown"):
        policy.parse_manifest(good + "extra = 1\n")
    with pytest.raises(ValueError, match="Tier 1"):
        policy.parse_manifest(good.replace("max_tier = 2", "max_tier = 1"))
    with pytest.raises(ValueError, match="kind"):
        policy.parse_manifest(good.replace('"python-job"', '"daemon"'))
    with pytest.raises(ValueError, match="non-empty strings"):
        policy.parse_manifest(good.replace("tools = []", 'tools = ["", 1]'))
    manifest = policy.parse_manifest(good)
    assert not policy.check(manifest, "spawn", "x", ROOT, [], [], []).allowed


@pytest.mark.blocking
def test_agent_profiles_declare_their_boundaries(planted) -> None:
    builder = policy.read_manifest(PROFILES["claude-builder"])
    reviewer = policy.read_manifest(PROFILES["codex-reviewer"])
    for profile in (builder, reviewer):
        assert not check(planted, profile, "read", str(planted.env)).allowed
        assert not check(planted, profile, "read", str(planted.tier1)).allowed
        assert not check(planted, profile, "network", "http://127.0.0.1:9/").allowed
        assert check(planted, profile, "read", "docs/charter.md").allowed
    assert check(planted, builder, "write", "kgme/new.py").allowed
    assert check(planted, builder, "write", "memory/agent/brief/x.md").allowed
    assert not check(planted, builder, "write", "docs/canary-probe.md").allowed
    assert not check(planted, builder, "write", "memory/notes/x.md").allowed
    assert check(planted, builder, "network", "https://api.anthropic.com/v1/messages").allowed
    assert not check(planted, reviewer, "write", "kgme/new.py").allowed
    assert not check(planted, reviewer, "delete", str(planted.victim)).allowed
    assert check(planted, reviewer, "tool", "shell").allowed


@pytest.mark.blocking
def test_the_codex_builder_profile_is_the_design_lanes() -> None:
    """HANDOFF-0042 §3: the builder's read paths are `kgme.toml [tracks.design] lanes` and its
    write paths the lanes plus `logs/scratch/`, so the profile and the merge gate cannot drift."""
    from kgme import config

    lanes = list(config.read_config()["tracks"]["design"]["lanes"])
    builder = policy.read_manifest(PROFILES["codex-builder"])
    assert list(builder.read_paths) == lanes
    assert list(builder.write_paths) == [*lanes, "logs/scratch/"]
    assert set(builder.network_destinations) == {"chatgpt.com:443", "api.openai.com:443"}
    assert builder.tools == ("shell",)


@pytest.mark.blocking
def test_the_codex_builder_profile_refuses_every_probe_and_the_never_list(
    planted, test_dirs, run_id, settings_sha, fast_matrix, fingerprints
) -> None:
    """The probes every manifest refuses, as matrix cells, and the handoff's never-list
    (`memory/`, `kgme/`, `control/`, `.claude/`, `CLAUDE.md`, the ADRs) for reads and writes;
    the lanes and `logs/scratch/` are writable."""
    builder = policy.read_manifest(PROFILES["codex-builder"])
    for probe, (op, target) in probes(planted).items():
        verdict = check(planted, builder, op, target)
        detail = verdict.reason if not verdict.allowed else "manifest allowed the probe"
        canary.write_cell(
            canary.Cell("codex-builder", probe, "manifest"),
            canary.Observed(not verdict.allowed, detail),
            test_dirs,
            run_id,
            settings_sha,
            fast_matrix,
            fingerprints,
        )
        assert not verdict.allowed, (probe, verdict)
    never = (
        "memory/notes/x.md",
        "kgme/new.py",
        "control/policy/profiles/codex-builder.toml",
        ".claude/settings.json",
        "CLAUDE.md",
        "docs/adr/ADR-001-x.md",
        "docs/readers/sessions.md",
        "tests/test_lint.py",
    )
    for target in never:
        for op in ("read", "write"):
            assert not check(planted, builder, op, target).allowed, (op, target)
    for target in (
        "docs/design/canvas/x.md",
        "docs/handoff/cockpit-design/x.md",
        "docs/audit/cockpit-design/x.md",
        "docs/readers/cockpit-design-x.md",
        "tests/test_design_x.py",
        "logs/scratch/design-review/x.png",
    ):
        assert check(planted, builder, "write", target).allowed, target
    assert check(planted, builder, "network", "https://api.openai.com/v1/responses").allowed
