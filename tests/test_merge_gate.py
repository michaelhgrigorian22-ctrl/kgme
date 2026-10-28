"""The merge gate (HANDOFF-0048 §5), from values alone.

Purpose: `kgme.crew.merge_gate` refuses a changed path outside the task's `Outputs`, a human
path, a blocklisted name, a symlink, a binary, a zero-width or bidirectional control
character, a dependency change without its toolbox row, a scanner hit, and a red check or
acceptance run, and lets a clean change through; the built-in scanner names the shapes it
trips and never the value; the hidden-character check names each code point once.
Inputs: paths, bytes, flags.
Outputs: pytest assertions.
Side effects: none.
"""

import os

import pytest

from kgme import config, crew

SETTINGS = config.read_config()
HUMAN = tuple(SETTINGS["hooks"]["human_paths"])
PATTERNS = [p[3:] for p in SETTINGS["hooks"]["blocklist"] if p.startswith("**/")]
OUTPUTS = ("kgme/toy.py", "tests/test_toy.py", "docs/audit/")


def gate(changed, contents=None, **more) -> list[str]:
    defaults = dict(outputs=OUTPUTS, human_paths=HUMAN, name_patterns=PATTERNS,
                    contents=contents or {p: b"x = 1\n" for p in changed}, symlinks=set(),
                    scanner_hits=[], check_ok=True, acceptance_ok=True)  # fmt: skip
    return crew.merge_gate(changed, **(defaults | more))


@pytest.mark.blocking
def test_a_clean_change_inside_the_outputs_passes() -> None:
    assert gate(["kgme/toy.py", "tests/test_toy.py", "docs/audit/toy.md"]) == []
    assert gate([]) == ["the branch changes nothing"]


@pytest.mark.blocking
@pytest.mark.parametrize(
    "changed, expected",
    [
        (["kgme/toy.py", "kgme/other.py"], "kgme/other.py is outside the task's Outputs"),
        (["kgme.toml"], "kgme.toml is a human path"),
        (["docs/readers/x.md"], "is a human path"),
        (["kgme/toy.py", "kgme/prod.env"], "is blocklisted"),
    ],
)
def test_paths_outside_human_or_blocklisted_are_refused(changed, expected) -> None:
    assert any(expected in r for r in gate(changed)), gate(changed)


@pytest.mark.blocking
def test_symlinks_binaries_and_hidden_characters_are_refused() -> None:
    assert "kgme/toy.py is a symlink" in gate(["kgme/toy.py"], symlinks={"kgme/toy.py"})
    assert "kgme/toy.py is binary" in gate(["kgme/toy.py"], {"kgme/toy.py": b"\x89PNG\0\0"})
    zero = {"kgme/toy.py": "x = 1  # ​\n".encode()}
    assert any("U+200B (zero width space)" in r for r in gate(["kgme/toy.py"], zero))
    bidi = {"kgme/toy.py": "x = 1  # ‮⁦\n".encode()}
    found = gate(["kgme/toy.py"], bidi)
    assert any("U+202E" in r for r in found) and any("U+2066" in r for r in found)
    assert crew.hidden_characters("plain text") == []
    assert gate(["kgme/toy.py"], {"kgme/toy.py": None}) == [], "a deletion has no bytes to scan"


@pytest.mark.blocking
def test_a_dependency_change_needs_its_toolbox_row_which_is_michous() -> None:
    """A task may not add a dependency: the row it needs is in `docs/toolbox.md`, a human
    path, so the gate refuses the change without the row and, with it, the row itself."""
    outputs = OUTPUTS + ("pyproject.toml", "uv.lock", "docs/toolbox.md")
    found = gate(["pyproject.toml", "uv.lock"], outputs=outputs)
    assert any("without its row in docs/toolbox.md" in r for r in found)
    with_row = gate(["pyproject.toml", "uv.lock", "docs/toolbox.md"], outputs=outputs)
    assert with_row == ["docs/toolbox.md is a human path"]


@pytest.mark.blocking
def test_scanner_hits_and_red_checks_refuse() -> None:
    assert "the scanner found a AWS access key" in gate(
        ["kgme/toy.py"], scanner_hits=["AWS access key"]
    )
    assert "make check is red on the merge result" in gate(["kgme/toy.py"], check_ok=False)
    assert "the task's acceptance check is red on the merge result" in gate(
        ["kgme/toy.py"], acceptance_ok=False
    )
    assert gate(["kgme/toy.py"], check_ok=None, acceptance_ok=None) == [], "not run is not red"


@pytest.mark.blocking
def test_the_built_in_scanner_names_the_shape_never_the_value() -> None:
    fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"
    fake_key = "sk-" + "a" * 24
    text = f'KEY = "{fake_aws}"\nOTHER = "{fake_key}"\n'
    hits = crew.scan_secrets(text)
    assert "AWS access key" in hits and "OpenAI-style key" in hits
    assert not any(fake_aws in h or fake_key in h for h in hits)
    assert crew.scan_secrets("x = 1\n") == []
    assert "private key" in crew.scan_secrets("-----BEGIN RSA PRIVATE KEY-----\n")
    assert "assigned secret" in crew.scan_secrets('password = "' + "p" * 20 + '"')


@pytest.mark.blocking
def test_a_configured_scanner_runs_only_when_its_toolbox_row_pins_it(tmp_path, monkeypatch) -> None:
    """Cycle 1 F14: `[crew] scanner` names a tool; the gate refuses to run one whose
    executable on PATH does not match a `docs/toolbox.md` row's sha256, and runs a pinned one
    with the diff on stdin, a nonzero exit being hits."""
    import hashlib

    from kgme import crew_io

    main = tmp_path / "main"
    (main / "docs").mkdir(parents=True)
    folder = tmp_path / "bin"
    folder.mkdir()
    tool = folder / "fakeleaks"
    tool.write_text(
        "#!/bin/sh\nif grep -q SECRET; then echo 'fake-key found'; exit 1; fi\nexit 0\n"
    )
    tool.chmod(0o755)
    monkeypatch.setenv("PATH", f"{folder}:{os.environ['PATH']}")
    settings = {"crew": {"scanner": "fakeleaks --stdin"}, "models": {"builder": "m"}}
    assert crew_io.run_scanner(settings, "x", tmp_path, main) == [
        "scanner not pinned: no docs/toolbox.md to pin fakeleaks with"
    ]
    digest = hashlib.sha256(tool.read_bytes()).hexdigest()
    header = (
        "| name | kind | for | source | licence | version | held | sha256 | egress | used in "
        "| handoff |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    (main / "docs" / "toolbox.md").write_text(
        "---\nid: TOOLBOX\n---\n\n"
        + header
        + f"| fakeleaks | tool | the gate's scanner | https://example.invalid | MIT | 1 | "
        f"machine: {tool} | {'0' * 64} | none | kgme/crew_io.py | HANDOFF-0048 |\n"
    )
    assert crew_io.run_scanner(settings, "x", tmp_path, main) == [
        f"scanner not pinned: fakeleaks at {tool} does not match its toolbox row's sha256"
    ]
    (main / "docs" / "toolbox.md").write_text(
        "---\nid: TOOLBOX\n---\n\n"
        + header
        + f"| fakeleaks | tool | the gate's scanner | https://example.invalid | MIT | 1 | "
        f"machine: {tool} | {digest} | none | kgme/crew_io.py | HANDOFF-0048 |\n"
    )
    assert crew_io.run_scanner(settings, "x = 1\n", tmp_path, main) == []
    assert crew_io.run_scanner(settings, "SECRET\n", tmp_path, main) == ["fake-key"]
    assert (
        crew_io.run_scanner({"crew": {}, "models": {"builder": "m"}}, "x", tmp_path, main) == []
    ), "built-in rules"
