"""Tests for the schema validator (HANDOFF-0031 acceptance and its review findings).

Purpose: one fixture per violation class yields exactly its finding with the expected class;
exempt paths are skipped and overlapping roots read a file once; datetimes are judged on the
raw text and nulls are refused where the schema requires an instant; provenance needs real
names; duplicate keys are caught however they are spelled; a boolean key does not stop the
scan; a mistyped root is an error; the real `memory/` and `docs/` carry no blocking finding.
Inputs: `tests/fixtures/vault/`, inline notes, the real repository roots, `kgme.toml`.
Outputs: pytest assertions.
Side effects: none. Reads only.
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
    settings = config.read_config()["lint"]
    notes = vault.read_notes(
        [paths.resolve(r) for r in settings["roots"]],
        [paths.resolve(p) for p in settings["exempt"]],
        tuple(settings["skip_dirs"]),
        paths.root(),
    )
    findings = lint.lint_files(notes)
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
