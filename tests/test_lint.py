"""Tests for the schema validator (HANDOFF-0031 acceptance and its review findings).

Purpose: one fixture per violation class yields exactly its finding with the expected class;
exempt paths are skipped and overlapping roots read a file once; datetimes are judged on the
raw text and nulls are refused where the schema requires an instant; provenance needs real
names; duplicate keys are caught however they are spelled; a boolean key does not stop the
scan; a mistyped root is an error; a `README.md` is skipped by name and `CDH` ids are a
family (v1.4); the registered tracks' folders and prefixes hold (v1.6), and the default lints
the commit, counting the untracked files it skips (HANDOFF-0042); the real `memory/` and
`docs/` carry no blocking finding.
Inputs: `tests/fixtures/vault/`, inline notes, the real repository roots, `kgme.toml`.
Outputs: pytest assertions.
Side effects: git repositories under `tmp_path`; otherwise reads only.
"""

from pathlib import Path

import pytest

from kgme import cli, config, lint, paths, vault

FIXTURES = Path(__file__).parent / "fixtures" / "vault"

EXPECTED: dict[str, list[tuple[str, str]]] = {
    "memory/notes/valid-note.md": [],
    "memory/notes/no-frontmatter.md": [("frontmatter", "blocking")],
    "memory/notes/missing-status.md": [("required", "blocking")],
    "memory/notes/bad-type.md": [("enum", "blocking")],
    "memory/notes/naive-datetime.md": [("datetime", "blocking")],
    "memory/notes/impossible-date.md": [("datetime", "blocking")],
    "memory/notes/fraction-seconds.md": [],
    "memory/notes/duplicate-id-a.md": [],
    "memory/notes/duplicate-id-b.md": [("unique-id", "blocking")],
    "memory/notes/decision-in-notes.md": [("folder", "blocking")],
    "memory/notes/fetched-no-origin.md": [("provenance", "blocking")],
    "memory/notes/inferred-no-sources.md": [("provenance", "blocking")],
    "memory/notes/unknown-field.md": [("unknown-field", "advisory")],
    "memory/notes/id-drift.md": [("id-format", "advisory")],
    "memory/notes/duplicate-key.md": [("frontmatter", "blocking")],
    "memory/notes/tier-is-bool.md": [("enum", "blocking")],
    "memory/notes/trailing-space.md": [("whitespace", "cosmetic")],
    "memory/daily/not-a-date.md": [("folder", "blocking")],
    "docs/handoff/handoff-with-author.md": [("required", "blocking"), ("type-field", "blocking")],
    "docs/audit/valid-report.md": [],
    "docs/audit/phase-0-report.md": [],
    "docs/audit/report-without-period.md": [("type-field", "blocking")],
}


def fixture_notes(roots: list[Path] | None = None) -> list[tuple[str, str]]:
    return vault.read_notes(
        roots or [FIXTURES / "memory", FIXTURES / "docs"],
        [FIXTURES / "memory" / "templates"],
        (".obsidian",),
        FIXTURES,
    )


def note(**fields: object) -> str:
    """A valid human note under memory/notes with any field overridden or added."""
    base: dict[str, object] = {
        "id": "20260915T120000",
        "type": "note",
        "created": "2026-09-15T12:00:00-07:00",
        "modified": "2026-09-15T12:00:00-07:00",
        "status": "active",
        "tier": 2,
        "source": "stated",
        "author": "human",
    }
    base.update(fields)
    lines = [f"{k}: {'null' if v is None else v}" for k, v in base.items() if v != "__omit__"]
    return "---\n" + "\n".join(lines) + "\n---\nbody\n"


def rules(text: str, rel_path: str = "memory/notes/x.md") -> list[tuple[str, str]]:
    return [(f.rule, f.cls) for f in lint.lint_note(text, rel_path, {})]


@pytest.mark.blocking
def test_each_planted_violation_yields_exactly_its_finding() -> None:
    findings = lint.lint_files(fixture_notes())
    seen: dict[str, list[tuple[str, str]]] = {path: [] for path in EXPECTED}
    for finding in findings:
        assert finding.path in EXPECTED, f"unexpected file in findings: {finding.path}"
        seen[finding.path].append((finding.rule, finding.cls))
    for path, expected in EXPECTED.items():
        assert sorted(seen[path]) == sorted(expected), f"{path}: {seen[path]}"


@pytest.mark.blocking
def test_exempt_paths_skipped_roots_ordered_and_overlaps_read_once() -> None:
    rels = [rel for rel, _ in fixture_notes()]
    assert not any(rel.startswith("memory/templates/") for rel in rels)
    per_root = [sorted(r for r in rels if r.startswith(root + "/")) for root in ("memory", "docs")]
    assert rels == per_root[0] + per_root[1], "roots in the configured order, sorted within each"
    assert (FIXTURES / "memory" / "templates" / "placeholder.md").exists()
    overlapping = fixture_notes([FIXTURES / "memory", FIXTURES / "memory" / "notes"])
    assert len(overlapping) == len({rel for rel, _ in overlapping}) == len(per_root[0])
    with pytest.raises(FileNotFoundError):
        fixture_notes([FIXTURES / "nowhere"])


@pytest.mark.blocking
def test_readme_is_exempt_by_name_and_cdh_ids_are_a_family(tmp_path: Path) -> None:
    """Schema v1.4 (HANDOFF-0041): any `README.md` is the index of its folder, not a note."""
    bare = "# An index\n\n- one\n"
    for rel in ("docs/handoff/some-track/README.md", "docs/design/x/README.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(bare)
    (tmp_path / "docs" / "handoff" / "some-track" / "index.md").write_text(bare)
    read = vault.read_notes([tmp_path / "docs"], [], (), tmp_path)
    assert [rel for rel, _ in read] == ["docs/handoff/some-track/index.md"]
    assert rules(bare, "docs/handoff/some-track/index.md") == [("frontmatter", "blocking")]
    assert vault.is_exempt(Path("docs/README.md"), [], ())
    assert not vault.is_exempt(Path("docs/readme.md"), [], ())
    assert rules(note(id="CDH-0007")) == []
    assert rules(note(id="AUDIT-CDH-0007")) == []
    assert rules(note(id="CDX-0007")) == [("id-format", "advisory")]


@pytest.mark.blocking
def test_datetimes_are_judged_on_the_raw_text_and_nulls_are_refused_where_required() -> None:
    assert rules(note(created="2026-09-15T12:00:00")) == [("datetime", "blocking")]
    assert rules(note(created="2026-09-15 12:00:00-07:00")) == [("datetime", "blocking")]
    assert rules(note(created="2026-09-15T12:00:00Z")) == [("datetime", "blocking")]
    assert rules(note(created="2026-02-30T12:00:00-07:00")) == [("datetime", "blocking")]
    assert rules(note(created="2026-09-15T12:00:00.426-07:00")) == []
    assert rules(note(created=None)) == [("datetime", "blocking")]
    assert rules(note(modified=None)) == [("datetime", "blocking")]
    done = "---\nid: HANDOFF-9100\ntype: handoff\ncreated: 2026-09-15T12:00:00-07:00\n"
    done += "from: michou\nto: claude-code\ntier: 2\nstatus: done\ncompleted: null\n---\nx\n"
    assert rules(done, "docs/handoff/x.md") == [("datetime", "blocking")]
    task = note(type="task", status="open", due=None, project='"[[kgme]]"', priority=2)
    assert rules(task) == []
    reminder = note(type="reminder", status="open", due=None, repeat=None, channel="phone")
    assert rules(reminder) == [("datetime", "blocking")]


@pytest.mark.blocking
def test_provenance_needs_real_names() -> None:
    assert rules(note(source="fetched", origin=True)) == [("provenance", "blocking")]
    assert rules(note(source="fetched", origin='""')) == [("provenance", "blocking")]
    assert rules(note(source="fetched", origin="EDGAR 10-K 2026-03-01")) == []
    assert rules(note(source="inferred", sources="[null]")) == [("provenance", "blocking")]
    assert rules(note(source="inferred", sources="[]")) == [("provenance", "blocking")]
    assert rules(note(source="inferred", sources="[20260915T101500]")) == []


@pytest.mark.blocking
def test_duplicate_keys_are_caught_bare_quoted_and_in_flow_style() -> None:
    quoted = note().replace("status: active\n", 'status: active\n"status": draft\n')
    assert rules(quoted) == [("frontmatter", "blocking")]
    flow = note(tags="{x: 1, x: 2}")
    assert rules(flow) == [("frontmatter", "blocking")]
    merged = note(tier="__omit__").replace("---\nid:", "---\nbase: &b {tier: 2}\n<<: *b\nid:")
    assert rules(merged) == [("unknown-field", "advisory")], "a merge key still loads"
    override = note().replace("---\nid:", "---\nbase: &b {tier: 3}\n<<: *b\nid:")
    assert rules(override) == [("unknown-field", "advisory")], "the note's own key still wins"
    in_merge = note().replace("status: active\n", '<<: {status: active, "status": draft}\n')
    assert rules(in_merge) == [("frontmatter", "blocking")], "a duplicate inside a merge source"
    in_list = note().replace("status: active\n", "<<: [{status: active}, {x: 1, x: 2}]\n")
    assert rules(in_list) == [("frontmatter", "blocking")], "or inside a list of merge sources"
    aliased = note().replace("status: active\n", "&k status: active\n*k : draft\n")
    assert rules(aliased) == [("frontmatter", "blocking")], "or spelled through an alias"


@pytest.mark.blocking
def test_a_boolean_key_is_a_finding_and_the_scan_continues() -> None:
    odd = note(on="value")
    found = rules(odd)
    assert ("frontmatter", "blocking") in found and ("unknown-field", "advisory") in found
    ok = note(id="20260915T120001")
    scan = lint.lint_files([("memory/notes/odd.md", odd), ("memory/notes/ok.md", ok)])
    assert [f.path for f in scan if f.cls == "blocking"] == ["memory/notes/odd.md"]
    assert not [f for f in scan if f.path == "memory/notes/ok.md"]


@pytest.mark.blocking
def test_a_yaml_error_renders_as_one_line_and_a_validator_error_is_a_finding() -> None:
    broken = "---\nid: [unclosed\ntype: note\n---\nx\n"
    findings = lint.lint_note(broken, "memory/notes/x.md", {})
    assert [(f.rule, f.cls) for f in findings] == [("frontmatter", "blocking")]
    assert "\n" not in findings[0].line()
    exploding = [("memory/notes/boom.md", None)]  # type: ignore[list-item]
    scan = lint.lint_files(exploding)
    assert [(f.rule, f.cls) for f in scan] == [("validator", "blocking")]


@pytest.mark.blocking
def test_the_real_vault_and_docs_carry_no_blocking_finding() -> None:
    """With the registered tracks (schema v1.6, HANDOFF-0042): every current file under the
    track folders passes unchanged."""
    full = config.read_config()
    settings = full["lint"]
    # the commit's files, as `kgme lint` reads them by default: an untracked file on this
    # machine must not turn `make check` red (HANDOFF-0042 review cycle 1 F1)
    notes, _ = vault.read_commit_notes(
        [paths.resolve(r) for r in settings["roots"]],
        [paths.resolve(p) for p in settings["exempt"]],
        tuple(settings["skip_dirs"]),
        paths.root(),
    )
    findings = lint.lint_files(notes, lint.read_tracks(full))
    blocking = [f.line() for f in findings if f.cls == "blocking"]
    assert blocking == [], "\n".join(blocking)
    assert len(notes) > 50


@pytest.mark.blocking
def test_cli_exit_codes(capsys) -> None:
    code = cli.main(["lint", "--base", str(FIXTURES)])
    out = capsys.readouterr().out
    assert code == 1 and out.splitlines()[-1].startswith("kgme lint: 22 notes")
    assert "memory/templates/" not in out, "exemptions follow --base"
    code = cli.main(["lint", "--base", str(FIXTURES), "--root", str(FIXTURES / "nowhere")])
    err = capsys.readouterr().err
    assert code == 2 and "not a directory" in err
    overlapping = ["--root", str(FIXTURES / "memory"), "--root", str(FIXTURES / "memory" / "notes")]
    code = cli.main(["lint", "--base", str(FIXTURES), *overlapping])
    out = capsys.readouterr().out
    assert code == 1 and out.splitlines()[-1].startswith("kgme lint: 18 notes")
    assert out.count("unique-id") == 1, "only the planted duplicate, not a file against itself"
    assert cli.main(["lint"]) == 0


TRACK = lint.Track(
    "design", "CDH", "AUDIT-CDH", "docs/handoff/cockpit-design", "docs/audit/cockpit-design"
)


def record(kind: str, identifier: str) -> str:
    """A valid handoff or report with the given id."""
    fields = {
        "handoff": "from: cowork\nto: claude-code\n",
        "report": "author: codex\nsource: stated\nhandoff: CDH-0001\nperiod: 2026-10-25\n",
    }[kind]
    status = "open" if kind == "handoff" else "final"
    return (
        f"---\nid: {identifier}\ntype: {kind}\ncreated: 2026-10-25T12:00:00-07:00\n"
        f"status: {status}\ntier: 2\n{fields}---\nbody\n"
    )


def track_rules(text: str, rel_path: str) -> list[tuple[str, str]]:
    found = lint.lint_note(text, rel_path, {}, (TRACK,))
    return [(f.rule, f.cls) for f in found if f.rule.startswith("track")]


@pytest.mark.blocking
def test_tracks_are_read_whole_or_not_at_all() -> None:
    """HANDOFF-0042 §1: a `[tracks.*]` table with only `lanes` registers nothing; a partial
    registration is an error, never silently ignored."""
    assert lint.read_tracks({}) == ()
    assert lint.read_tracks({"tracks": {"design": {"lanes": ["docs/design/"]}}}) == ()
    full = {
        "handoff": "CDH",
        "audit": "AUDIT-CDH",
        "handoff_folder": "docs/handoff/cockpit-design/",
        "audit_folder": "docs/audit/cockpit-design/",
    }
    assert lint.read_tracks({"tracks": {"design": full}}) == (TRACK,)
    partial = {key: value for key, value in full.items() if key != "audit_folder"}
    with pytest.raises(ValueError, match="audit_folder"):
        lint.read_tracks({"tracks": {"design": partial}})


@pytest.mark.blocking
def test_a_record_sits_in_a_state_folder_or_a_registered_track_folder() -> None:
    """Schema v1.6: below docs/handoff/ and docs/audit/, only done/, proposed/, archive/ and the
    registered track folders; any other subfolder is blocking."""
    for rel in (
        "docs/handoff/x.md",
        "docs/handoff/done/x.md",
        "docs/handoff/proposed/x.md",
        "docs/handoff/archive/x.md",
    ):
        assert track_rules(record("handoff", "HANDOFF-0001"), rel) == [], rel
    assert track_rules(record("handoff", "CDH-0001"), "docs/handoff/cockpit-design/x.md") == []
    assert track_rules(record("report", "AUDIT-CDH-0001"), "docs/audit/cockpit-design/x.md") == []
    for rel in ("docs/handoff/stray/x.md", "docs/audit/stray/x.md", "docs/audit/done/deep/x.md"):
        found = track_rules(record("handoff", "HANDOFF-0001"), rel)
        assert ("track-folder", "blocking") in found or rel == "docs/audit/done/deep/x.md", rel
    assert lint.lint_note(record("handoff", "HANDOFF-0001"), "docs/handoff/stray/x.md", {}) == [
        f
        for f in lint.lint_note(record("handoff", "HANDOFF-0001"), "docs/handoff/stray/x.md", {})
        if not f.rule.startswith("track")
    ], "without tracks passed, a single-note caller sees no track rule"


@pytest.mark.blocking
def test_a_record_in_a_track_folder_carries_the_tracks_prefix() -> None:
    """Schema v1.6: a handoff in the track's handoff folder carries `CDH-`, a report in its
    audit folder `AUDIT-CDH-`; the main sequence's prefixes there are blocking."""
    handoff = "docs/handoff/cockpit-design/x.md"
    audit = "docs/audit/cockpit-design/x.md"
    assert track_rules(record("handoff", "HANDOFF-0099"), handoff) == [("track-id", "blocking")]
    assert track_rules(record("report", "AUDIT-0099"), audit) == [("track-id", "blocking")]
    assert track_rules(record("report", "AUDIT-CDH-0099"), audit) == []
    assert track_rules(record("handoff", "CDH-0099"), "docs/handoff/x.md") == []


def write_repo(tmp_path: Path) -> Path:
    """Effect: a git repository with the lint roots, one valid committed note, and the
    planted cases of HANDOFF-0042's acceptance test staged or left untracked."""
    import subprocess

    repo = tmp_path / "repo"
    for rel, text in {
        "memory/notes/kept.md": note(),
        "docs/handoff/stray/planted.md": record("handoff", "HANDOFF-0098"),
        "docs/handoff/cockpit-design/wrong-prefix.md": record("handoff", "HANDOFF-0097"),
    }.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@localhost"]
    subprocess.run([*git, "init", "-q"], cwd=repo, check=True)
    subprocess.run([*git, "add", "-A"], cwd=repo, check=True)
    (repo / "docs" / "untracked.md").write_text("no frontmatter here\n")
    return repo


@pytest.mark.blocking
def test_the_default_lints_the_commit_and_counts_the_untracked_it_skips(tmp_path: Path) -> None:
    """HANDOFF-0042 §2: staged files are the commit's and are linted; an untracked file is
    skipped and counted; `--all` walks it."""
    repo = write_repo(tmp_path)
    roots, exempt = [repo / "memory", repo / "docs"], [repo / "memory" / "templates"]
    notes, skipped = vault.read_commit_notes(roots, exempt, (), repo)
    assert skipped == 1 and "docs/untracked.md" not in [rel for rel, _ in notes]
    found = [(f.path, f.rule) for f in lint.lint_files(notes, (TRACK,)) if f.cls == "blocking"]
    assert ("docs/handoff/stray/planted.md", "track-folder") in found
    assert ("docs/handoff/cockpit-design/wrong-prefix.md", "track-id") in found
    walked = vault.read_notes(roots, exempt, (), repo)
    assert "docs/untracked.md" in [rel for rel, _ in walked]
    outside, none_skipped = vault.read_commit_notes([tmp_path / "repo" / "docs"], [], (), tmp_path)
    assert none_skipped == 0 and len(outside) == 3, "no index outside a work tree: the walk"


@pytest.mark.blocking
def test_the_cli_counts_the_untracked_and_all_reports_it(tmp_path: Path, capsys) -> None:
    import subprocess

    repo = tmp_path / "repo"
    (repo / "memory" / "notes").mkdir(parents=True)
    (repo / "memory" / "notes" / "kept.md").write_text(note())
    (repo / "docs").mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    (repo / "docs" / "untracked.md").write_text("no frontmatter here\n")
    assert cli.main(["lint", "--base", str(repo)]) == 0
    last = capsys.readouterr().out.splitlines()[-1]
    assert "1 untracked skipped; `--all` walks them" in last, last
    assert cli.main(["lint", "--base", str(repo), "--all"]) == 1
    out = capsys.readouterr().out
    assert "docs/untracked.md: frontmatter [blocking]" in out and "untracked skipped" not in out
