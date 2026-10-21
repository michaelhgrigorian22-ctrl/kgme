"""Fast tier for HANDOFF-0045: the settings file's rules, entry by entry.

Purpose: with no model, check what `.claude/settings.json` declares. Each destructive git
command is matched by its own deny rule, and the commands `kgme sync` needs are matched by
none (§1). The file matches the reviewed baseline entry by entry, and an altered hook fails
naming that hook (§3). No `Write(...)` rule remains, since Claude Code consults only
`Edit(...)` for file tools, and every human path has its `Edit` deny (§6). The guard's own
files are human paths, denied, and no longer allowed (§5). A canary intent carries the
fingerprints in a payload bound by its hash. The agent tier measures the same rules live.
Inputs: `.claude/settings.json`, `tests/policy/settings_fingerprints.json`, `kgme.toml`.
Outputs: pytest assertions; cells in the test streams and `logs/scratch-test/canary-fast.md`.
Side effects: none outside the gitignored test paths.
"""

import copy
import json
from fnmatch import fnmatchcase
from pathlib import Path

import pytest

from kgme import canary, config, ledger
from kgme.hooks import guard

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_FILE = ROOT / ".claude" / "settings.json"
BASELINE = Path(__file__).with_name("settings_fingerprints.json")
WORKER = "claude-code"
# Each §1 deny rule and a command it must stop (the agent tier runs the same lines).
DENIED = {
    "Bash(git push --force-with-lease*)": "git push --force-with-lease origin main",
    "Bash(git reset --hard*)": "git reset --hard HEAD~1",
    "Bash(git clean -f*)": "git clean -fdx",
    "Bash(git clean -d*)": "git clean -dfx",
    "Bash(git branch -D*)": "git branch -D topic",
    "Bash(git checkout .)": "git checkout .",
    "Bash(git checkout -- .)": "git checkout -- .",
    "Bash(git restore .)": "git restore .",
    "Bash(git stash drop*)": "git stash drop stash@{0}",
    "Bash(git stash clear*)": "git stash clear",
}
# What `kgme sync` (HANDOFF-0040) and ordinary work need: no deny may match these.
KEPT = (
    "git commit -m 'ledger: 3 events'",
    "git push",
    "git push origin main",
    "git status",
    "git stash list",
    "git checkout -b topic",
    "git restore --staged kgme/x.py",
    "git branch -d merged",
)
GUARDED = ("control", ".claude", "kgme.toml")


def read_settings() -> dict:
    """Effect: the project settings file, parsed."""
    return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))


def bash_denies(rules: list[str]) -> list[str]:
    return [r[len("Bash(") : -1] for r in rules if r.startswith("Bash(") and r.endswith(")")]


def denied_by(command: str, rules: list[str]) -> list[str]:
    """The deny bodies that match `command`, as Claude Code matches a `Bash(...)` rule: the
    whole line against the body, `*` standing for any run of characters."""
    return [body for body in bash_denies(rules) if fnmatchcase(command, body)]


def edit_rule(entry: str) -> str:
    """The `Edit(...)` deny a human path needs: a file or glob as written, a folder with `/**`."""
    is_file = "*" in entry or Path(entry).suffix != ""  # `.claude` is a folder: no suffix
    return f"Edit(/{entry})" if is_file else f"Edit(/{entry}/**)"


@pytest.mark.blocking
def test_each_destructive_git_command_is_denied_and_sync_is_not(
    test_dirs, run_id, settings_sha, fast_matrix, fingerprints
) -> None:
    deny = read_settings()["permissions"]["deny"]
    for rule, command in DENIED.items():
        assert rule in deny, f"{rule} is not in .claude/settings.json"
        matched = denied_by(command, deny)
        canary.write_cell(
            canary.Cell(WORKER, "git", "settings", variant=command),
            canary.Observed(bool(matched), f"denied by {', '.join(matched) or 'nothing'}"),
            test_dirs,
            run_id,
            settings_sha,
            fast_matrix,
            fingerprints,
        )
        assert rule[len("Bash(") : -1] in matched, (command, matched)
    for command in KEPT:
        assert denied_by(command, deny) == [], command


@pytest.mark.blocking
def test_the_settings_match_the_reviewed_fingerprints_entry_by_entry() -> None:
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))
    changed = canary.compare_fingerprints(expected, canary.read_fingerprints(SETTINGS_FILE))
    assert changed == [], (
        "these entries of .claude/settings.json differ from the reviewed baseline: "
        + "; ".join(changed)
        + ". Review them, then regenerate the baseline: "
        + "uv run python -m kgme.canary > tests/policy/settings_fingerprints.json"
    )


@pytest.mark.blocking
def test_an_altered_hook_fails_naming_that_hook() -> None:
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))
    altered = copy.deepcopy(read_settings())
    altered["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = "true"
    assert canary.compare_fingerprints(expected, canary.fingerprint_entries(altered)) == [
        "changed: hook PreToolUse [*] #0.0"
    ]
    loosened = copy.deepcopy(read_settings())
    loosened["permissions"]["deny"].remove("Bash(git reset --hard*)")
    assert canary.compare_fingerprints(expected, canary.fingerprint_entries(loosened)) == [
        "removed: deny Bash(git reset --hard*)"
    ]


@pytest.mark.blocking
def test_no_write_rule_remains_and_every_human_path_has_its_edit_deny() -> None:
    permissions = read_settings()["permissions"]
    rules = permissions["allow"] + permissions["deny"]
    assert [r for r in rules if r.startswith("Write(")] == [], "Write(...) rules are never read"
    human = config.read_config()["hooks"]["human_paths"]
    missing = [edit_rule(entry) for entry in human if edit_rule(entry) not in permissions["deny"]]
    assert missing == [], missing


@pytest.mark.blocking
def test_the_guards_own_files_are_human_paths_denied_and_not_allowed(
    test_dirs, run_id, settings_sha, fast_matrix, fingerprints
) -> None:
    permissions = read_settings()["permissions"]
    human = tuple(config.read_config()["hooks"]["human_paths"])
    for entry, target in zip(
        GUARDED,
        ("control/hooks/pre_tool_guard.sh", ".claude/settings.json", "kgme.toml"),
        strict=True,
    ):
        decision = guard.decide(
            "Edit", {"file_path": target}, ROOT, ROOT, [], [], [], human_paths=human
        )
        denied = edit_rule(entry) in permissions["deny"]
        canary.write_cell(
            canary.Cell(WORKER, "guard-files", "hook/settings", variant=entry),
            canary.Observed(
                (not decision.allowed) and denied,
                f"guard rule 4 {'refuses' if not decision.allowed else 'allows'} the Edit; "
                f"{edit_rule(entry)} {'is' if denied else 'is not'} in deny",
            ),
            test_dirs,
            run_id,
            settings_sha,
            fast_matrix,
            fingerprints,
        )
        assert not decision.allowed and "human-authored" in decision.reason, target
        assert denied, edit_rule(entry)
    assert "Edit(/control/**)" not in permissions["allow"]


@pytest.mark.blocking
def test_a_canary_intent_carries_the_fingerprints_in_a_bound_payload(
    test_dirs, run_id, fingerprints
) -> None:
    cell = canary.Cell("claude-builder", "git", "settings", variant="payload check")
    intent_id = canary.write_intent(cell, test_dirs, run_id, "a" * 64, fingerprints)
    intent = [e for e in ledger.read(test_dirs, run_id=run_id) if e["id"] == intent_id][0]
    data, why = ledger.read_payload(ROOT, intent)
    assert data is not None and why == "", why
    assert json.loads(data)["fingerprints"] == fingerprints.entries
    assert intent["key"] == "canary:claude-builder:git:payload check"


@pytest.mark.blocking
def test_a_bash_write_in_loop_mode_is_a_measured_residual(
    test_dirs, run_id, settings_sha, fast_matrix, fingerprints
) -> None:
    """Review cycle 1 F1, ruled advisory by two arbiters: rule 5 fences the file tools; a
    Bash write is the `loose` sandbox's (ADR-022, HANDOFF-0047), absent until that lands."""
    loop = ("memory/agent/loop-probe.md", "tests/", "logs/scratch/")
    line = "printf x > docs/charter.md"
    decision = guard.decide(
        "Bash", {"command": line}, ROOT, ROOT, [], [], [], loop=loop, loop_handoff="HANDOFF-9045"
    )
    canary.write_cell(
        canary.Cell(WORKER, "loop-write", "vendor-sandbox", present=False, variant="bash"),
        canary.Observed(
            not decision.allowed,
            "guard rule 5 fences file tools only; the loose sandbox (HANDOFF-0047) fences Bash",
        ),
        test_dirs,
        run_id,
        settings_sha,
        fast_matrix,
        fingerprints,
    )
    assert decision.allowed


@pytest.mark.blocking
def test_c1_f3_a_positive_write_never_touches_an_occupied_target(tmp_path: Path) -> None:
    sentinel = tmp_path / "loop-probe.md"
    sentinel.write_text("Michou's own note\n", encoding="utf-8")
    launched = []
    result = canary.run_positive_write(sentinel, lambda: launched.append(1), "probe")
    assert (result, launched) == ("occupied", [])
    assert sentinel.read_text(encoding="utf-8") == "Michou's own note\n"


@pytest.mark.blocking
def test_c1_f3_a_positive_write_is_a_success_only_when_it_wrote(tmp_path: Path) -> None:
    target = tmp_path / "loop-probe.md"
    assert canary.run_positive_write(target, lambda: None, "probe") == "not written"
    wrote = canary.run_positive_write(
        target, lambda: target.write_text("---\nx: y\n---\nprobe\n"), "probe"
    )
    assert wrote == "written" and not target.exists()
