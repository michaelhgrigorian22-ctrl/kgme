"""The toy reviewer: `codex exec ... -o <file> <prompt>`, deterministic.

Reads the patch the prompt names and writes a review to the `-o` file: BLOCK with F1 while an
added line carries the seed (`SEED`), PASS with F1 resolved once none does.
Inputs: argv as `kgme.review_io.run_reviewer` builds it.
Outputs: the review text in the `-o` file; one JSON line on stdout; exit 0.
Side effects: that one file.
"""

import json
import re
import sys
from pathlib import Path

HEAD = "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
BLOCK = HEAD + (
    "| F1 | blocking | toy.py:2 | The seed is in the diff. | Remove the seed. |\n\n"
    "## Verdict\n\nBLOCK: 1 open.\n\n## Notes\n\nnone\n"
)
PASS = HEAD + (
    "| F1 | blocking, resolved | toy.py:2 | The seed is gone. | None. |\n\n"
    "## Verdict\n\nPASS\n\n## Notes\n\nnone\n"
)


def build(argv: list[str]) -> int:
    """The builder form (HANDOFF-0048): the prompt on stdin names `Write only these Outputs:
    a, b`; the first Output is written in the worktree `-C` names, and the stream carries one
    started and completed command and one file change, as `codex exec --json` prints them.
    A prompt holding `SEED` writes the seed into the file, so the toy reviewer blocks once."""
    prompt = sys.stdin.read()
    where = Path(argv[argv.index("-C") + 1])
    match = re.search(r"Write only these Outputs: ([^\s,]+)", prompt)
    target = where / match[1] if match else where / "toy_codex.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    # the seed stays on a fix cycle only when the task says KEEP SEED, so a persistent blocker
    # can be driven to the arbiters; it goes once a settled ruling is in the prompt
    fixing = "Findings of the previous" in prompt
    keep = "KEEP SEED" in prompt and "settled rulings" not in prompt
    seed = "  # SEED" if "SEED" in prompt and (not fixing or keep) else ""
    counter = where / "logs" / "scratch" / "builds.txt"
    counter.parent.mkdir(parents=True, exist_ok=True)
    builds = int(counter.read_text() or "0") + 1 if counter.is_file() else 1
    counter.write_text(str(builds))
    if keep:  # a different diff each cycle, the seed kept: a persistent blocker, not a repeat
        seed += f"  # build {builds}"
    (where / "logs" / "scratch").mkdir(parents=True, exist_ok=True)
    (where / "logs" / "scratch" / "last-prompt.txt").write_text(prompt)
    target.write_text(f"def add(a, b):\n    return a + b{seed}\n")
    (where / "logs" / "scratch" / "dispositions.md").write_text(
        "F1: disputed, the seed is required.\n" if keep else "F1: fixed, the seed is gone.\n"
    )
    for record in (
        {"type": "thread.started", "thread_id": "toy-thread"},
        {"type": "item.started", "item": {"type": "command_execution", "id": "c1",
         "command": "cat AGENTS.md"}},
        {"type": "item.completed", "item": {"type": "command_execution", "id": "c1",
         "command": "cat AGENTS.md", "exit_code": 0, "aggregated_output": ""}},
        {"type": "item.completed", "item": {"type": "file_change", "id": "f1",
         "changes": [{"path": str(target), "kind": "add"}]}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {"type": "turn.completed"},
    ):  # fmt: skip
        print(json.dumps(record), flush=True)
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--version"]:
        print("0.0.0 (toy)")
        return 0
    if "-C" in argv and argv[-1:] == ["-"]:
        return build(argv)
    out = Path(argv[argv.index("-o") + 1])
    match = re.search(r"(\S*review\.patch)", argv[-1])
    patch = Path(match[1]).read_text() if match and Path(match[1]).is_file() else ""
    lines = patch.splitlines()
    added = [ln for ln in lines if ln.startswith("+")]
    # a diff: the seed on an added line; a plan (no diff lines): the seed anywhere (0048)
    seeded = any("SEED" in ln for ln in (added or lines))
    out.write_text(BLOCK if seeded else PASS)
    print(json.dumps({"type": "turn.completed"}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
