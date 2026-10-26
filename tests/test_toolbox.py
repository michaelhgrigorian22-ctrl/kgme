"""Tests for the toolbox checks (ADR-020, HANDOFF-0044 §3 and its acceptance test).

Purpose: the registry's rows and the tree stay in step. A planted `import httpx` in `kgme/`
with no row is blocking; a vendored file whose sha differs from its row is blocking; a
`<script src>` in a cockpit page naming a host is blocking; a row without a source or a sha is
blocking, without a licence advisory (schema 1.7); a pending row is reported, not verified; a
skill folder is hashed over every file in it; the real tree carries no blocking finding.
Inputs: fixture repositories under `tmp_path`; the real tree.
Outputs: pytest assertions.
Side effects: files under `tmp_path`.
"""

import hashlib
from pathlib import Path

import pytest

from kgme import paths, toolbox, toolbox_read

HEADER = "| " + " | ".join(toolbox.COLUMNS) + " |\n" + "|---" * len(toolbox.COLUMNS) + "|\n"


def row(name: str, kind: str, held: str, sha: str, **cells: str) -> str:
    c = {"source": "https://x", "licence": "MIT", "egress": "none", **cells}
    values = [name, kind, "f", c["source"], c["licence"], "1", held, sha, c["egress"], "u", "H"]
    return "| " + " | ".join(values) + " |\n"


YAML = row("pyyaml (import yaml)", "package", "uv.lock", "uv.lock")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


VALID = "sha256:" + "a" * 64
SDIST = f'sdist = {{ url = "https://x", hash = "{VALID}" }}\n'
LOCK = (
    """version = 1

[[package]]
name = "pyyaml"
version = "1"
"""
    + SDIST
)


def write_tree(tmp_path: Path, table: str, files: dict[str, str | bytes]) -> Path:
    """Effect: a checkout with the registry, a lock pinning pyyaml at the rows' version, and
    the given files (a `None`-free dict; pass `uv.lock` to replace the lock)."""
    for rel, text in {
        "docs/toolbox.md": "# t\n\n" + HEADER + table,
        "uv.lock": LOCK,
        **files,
    }.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode())
    return tmp_path


def blocking(found: list) -> list[tuple[str, str]]:
    return [(f.path, f.rule) for f in found if f.cls == "blocking"]


@pytest.mark.blocking
def test_a_planted_import_with_no_row_is_blocking(tmp_path: Path) -> None:
    files = {"kgme/a.py": "import yaml\nimport json\nfrom kgme import paths\n", "cockpit/x.py": ""}
    base = write_tree(tmp_path, YAML, files)
    assert blocking(toolbox_read.read_findings(base)) == []
    (base / "kgme" / "planted.py").write_text("import httpx\n")
    assert blocking(toolbox_read.read_findings(base)) == [("kgme/planted.py", "toolbox-import")]
    (base / "kgme" / "planted.py").write_text("from httpx.client import Client\n")
    assert blocking(toolbox_read.read_findings(base)) == [("kgme/planted.py", "toolbox-import")]


@pytest.mark.blocking
def test_a_vendored_file_whose_sha_differs_is_blocking(tmp_path: Path) -> None:
    held = b"export const x = 1;\n"
    vendored = "cockpit/static/vendor/lib-1.0.0.js"
    table = YAML + row("lib", "module", vendored, sha(held))
    base = write_tree(tmp_path, table, {vendored: held, "kgme/a.py": ""})
    assert blocking(toolbox_read.read_findings(base)) == []
    (base / vendored).write_bytes(held + b"// edited\n")
    assert blocking(toolbox_read.read_findings(base)) == [("docs/toolbox.md", "toolbox-sha")]
    (base / "cockpit/static/vendor/other.js").write_text("x")
    assert ("cockpit/static/vendor/other.js", "toolbox-held") in blocking(
        toolbox_read.read_findings(base)
    )


@pytest.mark.blocking
@pytest.mark.parametrize(
    "src",
    ["https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.module.js", "//cdn.example/x.js",
     "http://127.0.0.1/x.js"],
)  # fmt: skip
def test_a_script_src_naming_a_host_is_blocking(tmp_path: Path, src: str) -> None:
    page = f'<!doctype html><script type="module" src="{src}"></script>\n'
    base = write_tree(tmp_path, YAML, {"cockpit/index.html": page, "kgme/a.py": ""})
    assert blocking(toolbox_read.read_findings(base)) == [("cockpit/index.html", "toolbox-script")]


@pytest.mark.blocking
def test_a_local_script_must_be_a_vendored_file_with_a_row(tmp_path: Path) -> None:
    held, vendored = b"x\n", "cockpit/static/vendor/lib-1.0.0.js"
    page = '<script src="/static/vendor/lib-1.0.0.js"></script><script>inline()</script>\n'
    files = {"cockpit/index.html": page, vendored: held, "kgme/a.py": ""}
    base = write_tree(tmp_path, YAML + row("lib", "module", vendored, sha(held)), files)
    assert blocking(toolbox_read.read_findings(base)) == []
    (base / "cockpit/index.html").write_text('<script src="app.js"></script>\n')
    assert blocking(toolbox_read.read_findings(base)) == [("cockpit/index.html", "toolbox-script")]


@pytest.mark.blocking
def test_every_row_has_a_source_a_sha_and_a_licence() -> None:
    table = HEADER + "".join([
        row("ok", "harness", "machine: /bin/x", "a" * 64),
        row("no-source", "harness", "machine: /bin/x", "a" * 64, source="—"),
        row("no-sha", "module", "cockpit/static/vendor/x.js", "—"),
        row("no-licence", "harness", "machine: /bin/x", "b" * 64, licence="—"),
        row("api-no-host", "api", "machine: none", "c" * 64, egress="none"),
        row("lock-not-package", "module", "uv.lock", "uv.lock"),
        row("ok", "harness", "machine: /bin/y", "d" * 64),
        row("bad-kind", "plugin", "machine: /bin/z", "e" * 64),
    ])  # fmt: skip
    rows, parse = toolbox.parse_rows(table)
    assert parse == [] and len(rows) == 8
    found = {(f.cls, f.message.split(": ", 1)[1]) for f in toolbox.check_rows(rows)}
    assert found == {
        ("blocking", "no source"),
        ("blocking", "no sha256 (64 lowercase hex digits) of what we hold"),
        ("advisory", "no licence (blocking from schema 1.8)"),
        ("blocking", "a api row names the egress host it needs"),
        ("blocking", "`held: uv.lock` is for a package row whose sha is `uv.lock`"),
        ("blocking", "a second row with this name"),
        ("blocking", "kind must be one of " + ", ".join(toolbox.KINDS)),
    }


@pytest.mark.blocking
def test_a_malformed_table_or_a_missing_registry_is_blocking(tmp_path: Path) -> None:
    assert [f.rule for f in toolbox_read.read_findings(tmp_path)] == ["toolbox-table"]
    _, found = toolbox.parse_rows("| name | kind |\n|---|---|\n")
    assert [f.rule for f in found] == ["toolbox-table"]
    _, found = toolbox.parse_rows(HEADER + "| too | few |\n")
    assert [f.rule for f in found] == ["toolbox-table"]


@pytest.mark.blocking
def test_a_pending_row_is_reported_not_verified(tmp_path: Path) -> None:
    held = "pending: cockpit/static/vendor/three-0.182.0/three.module.js (HANDOFF-0058)"
    base = write_tree(tmp_path, YAML + row("three", "module", held, "d" * 64), {"kgme/a.py": ""})
    found = toolbox_read.read_findings(base)
    assert blocking(found) == []
    assert [(f.rule, f.cls) for f in found] == [("toolbox-pending", "advisory")]


@pytest.mark.blocking
def test_a_skill_folder_is_held_as_one_digest_over_every_file(tmp_path: Path) -> None:
    files = {"skills/grilling/SKILL.md": "# g\n", "skills/grilling/LICENSE": "MIT\n"}
    listing = [(rel.split("/", 2)[2], sha(text.encode())) for rel, text in files.items()]
    digest = toolbox.folder_sha(listing)
    table = YAML + row("grilling", "skill", "skills/grilling/", digest)
    own = {"skills/kgme-atlas/SKILL.md": "# ours\n", "kgme/a.py": ""}
    base = write_tree(tmp_path, table, {**files, **own})
    assert blocking(toolbox_read.read_findings(base)) == [], "a kgme- skill is KGME's own, no row"
    (base / "skills/grilling/extra.md").write_text("added\n")
    assert blocking(toolbox_read.read_findings(base)) == [("docs/toolbox.md", "toolbox-sha")]
    (base / "skills/stray").mkdir()
    (base / "skills/stray/SKILL.md").write_text("x\n")
    assert ("skills/stray/", "toolbox-held") in blocking(toolbox_read.read_findings(base))


@pytest.mark.blocking
def test_the_real_tree_carries_no_blocking_toolbox_finding() -> None:
    found = toolbox_read.read_findings(paths.root())
    assert blocking(found) == [], [f.line() for f in found if f.cls == "blocking"]


@pytest.mark.blocking
def test_review_f1_only_the_exact_src_attribute_counts(tmp_path: Path) -> None:
    held, vendored = b"x\n", "cockpit/static/vendor/lib-1.0.0.js"
    page = (
        '<script src="https://cdn.example/x.js" data-src="/static/vendor/lib-1.0.0.js"></script>\n'
    )
    files = {"cockpit/index.html": page, vendored: held, "kgme/a.py": ""}
    base = write_tree(tmp_path, YAML + row("lib", "module", vendored, sha(held)), files)
    assert blocking(toolbox_read.read_findings(base)) == [("cockpit/index.html", "toolbox-script")]
    assert toolbox.script_sources('<script data-src="a.js" SRC="b.js"></script>') == ["b.js"]


@pytest.mark.blocking
def test_review_f2_nested_cockpit_pages_are_checked(tmp_path: Path) -> None:
    page = '<script src="https://cdn.example/x.js"></script>\n'
    base = write_tree(tmp_path, YAML, {"cockpit/pages/example.html": page, "kgme/a.py": ""})
    assert blocking(toolbox_read.read_findings(base)) == [
        ("cockpit/pages/example.html", "toolbox-script")
    ]


@pytest.mark.blocking
@pytest.mark.parametrize(
    "lock,why",
    [
        (None, "uv.lock is missing"),
        ('version = 1\n[[package]]\nname = "other"\nversion = "1"\n', "pins no package"),
        (LOCK.replace('version = "1"', 'version = "2"'), "uv.lock pins 2, the row 1"),
        (
            LOCK.replace(SDIST, ""),
            "no well-formed",
        ),
    ],
)
def test_review_f3_a_lock_row_is_checked_against_the_lock(
    tmp_path: Path, lock: str | None, why: str
) -> None:
    base = write_tree(tmp_path, YAML, {"kgme/a.py": "import yaml\n"})
    if lock is None:
        (base / "uv.lock").unlink()
    else:
        (base / "uv.lock").write_text(lock)
    found = [f for f in toolbox_read.read_findings(base) if f.cls == "blocking"]
    assert [f.rule for f in found] == ["toolbox-lock"] and why in found[0].message, found


@pytest.mark.blocking
def test_review_f4_a_held_path_never_reads_outside_the_repository(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("not ours\n")
    base = tmp_path / "repo"
    table = YAML + "".join([
        row("abs", "module", str(outside / "secret.txt"), "a" * 64),
        row("up", "module", "../outside/secret.txt", "b" * 64),
        row("elsewhere", "module", "memory/notes/x.md", "c" * 64),
        row("link", "module", "cockpit/static/vendor/link.js", "d" * 64),
        row("skill", "skill", "skills/linked/", "e" * 64),
    ])  # fmt: skip
    write_tree(base, table, {"kgme/a.py": "", "memory/notes/x.md": "private\n"})
    (base / "cockpit/static/vendor").mkdir(parents=True)
    (base / "cockpit/static/vendor/link.js").symlink_to(outside / "secret.txt")
    (base / "skills/linked").mkdir(parents=True)
    (base / "skills/linked/SKILL.md").symlink_to(outside / "secret.txt")
    shas, problems = toolbox_read.read_held(base, toolbox.parse_rows(HEADER + table)[0])
    assert set(problems) == {
        str(outside / "secret.txt"), "../outside/secret.txt", "memory/notes/x.md",
        "cockpit/static/vendor/link.js", "skills/linked/",
    } and shas == {}, (problems, shas)  # fmt: skip
    found = blocking(toolbox_read.read_findings(base))
    assert found.count(("docs/toolbox.md", "toolbox-held")) == 5


@pytest.mark.blocking
def test_review_f5_a_missing_licence_is_blocking_from_schema_1_8(tmp_path: Path) -> None:
    assert toolbox.licence_class((1, 7)) == "advisory"
    assert toolbox.licence_class((1, 8)) == "blocking"
    assert toolbox.licence_class((2, 0)) == "blocking"
    assert toolbox.licence_class(None) == "blocking"
    table = YAML + row("model", "harness", "machine: /x", "a" * 64, licence="—")
    for version, cls in (("1.7", "advisory"), ("1.8", "blocking")):
        schema = f"---\nid: SCHEMA\nversion: {version}\n---\n"
        base = write_tree(tmp_path / version, table, {"kgme/a.py": "", "docs/schema-v1.md": schema})
        found = [f for f in toolbox_read.read_findings(base) if "licence" in f.message]
        assert [f.cls for f in found] == [cls], (version, found)


@pytest.mark.blocking
@pytest.mark.parametrize(
    "digest", ["sha256:aa", "md5:" + "a" * 64, "sha256:" + "A" * 64, "sha256:" + "a" * 63]
)
def test_review_c2_f3_a_lock_hash_must_be_a_sha256_digest(tmp_path: Path, digest: str) -> None:
    lock = LOCK.replace(VALID, digest)
    base = write_tree(tmp_path, YAML, {"kgme/a.py": "import yaml\n", "uv.lock": lock})
    found = [f for f in toolbox_read.read_findings(base) if f.cls == "blocking"]
    assert [f.rule for f in found] == ["toolbox-lock"] and "well-formed" in found[0].message


@pytest.mark.blocking
def test_review_c2_f4_a_symlinked_ancestor_is_refused_before_any_read(tmp_path: Path) -> None:
    """`skills/alias -> memory/notes` made `skills/alias/example.md` look local. The target
    is made unreadable, so any read would raise: the test proves no read occurs."""
    alias = row("alias", "skill", "skills/alias/example.md", "a" * 64)
    base = write_tree(tmp_path, YAML + alias, {"kgme/a.py": "", "memory/notes/example.md": "x\n"})
    (base / "skills").mkdir()
    (base / "skills/alias").symlink_to(base / "memory/notes")
    target = base / "memory/notes/example.md"
    target.chmod(0)
    try:
        rows = toolbox.parse_rows(HEADER + YAML + alias)[0]
        shas, problems = toolbox_read.read_held(base, rows)
        assert problems == {"skills/alias/example.md": "skills/alias is a symlink"} and shas == {}
        assert ("docs/toolbox.md", "toolbox-held") in blocking(toolbox_read.read_findings(base))
    finally:
        target.chmod(0o644)


@pytest.mark.blocking
@pytest.mark.parametrize(
    "link", ["cockpit/static/vendor/example.html", "cockpit/pages/page.html", "kgme/linked.py"]
)
def test_review_c3_f8_discovery_never_reads_a_symlinked_file(tmp_path: Path, link: str) -> None:
    """Review cycle 3 F8: the page and import walks read files before the held-path guard.
    The target lies outside the repository and is made unreadable, so any read would raise:
    the run proves no target content is read, and the link is a blocking finding."""
    outside = tmp_path / "outside.txt"
    outside.write_text("<script src='https://evil.example/x.js'></script>\nimport httpx\n")
    base = write_tree(tmp_path / "repo", YAML, {"kgme/a.py": ""})
    (base / link).parent.mkdir(parents=True, exist_ok=True)
    (base / link).symlink_to(outside)
    outside.chmod(0)
    try:
        found = blocking(toolbox_read.read_findings(base))
    finally:
        outside.chmod(0o644)
    assert (link, "toolbox-link") in found, found
    # a file under the vendor folder with no row is also its own finding; nothing else is
    assert set(found) <= {(link, "toolbox-link"), (link, "toolbox-held")}, found
