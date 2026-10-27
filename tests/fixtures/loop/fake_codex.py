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


def main(argv: list[str]) -> int:
    if argv[:1] == ["--version"]:
        print("0.0.0 (toy)")
        return 0
    out = Path(argv[argv.index("-o") + 1])
    match = re.search(r"(\S*review\.patch)", argv[-1])
    patch = Path(match[1]).read_text() if match else ""
    seeded = any(line.startswith("+") and "SEED" in line for line in patch.splitlines())
    out.write_text(BLOCK if seeded else PASS)
    print(json.dumps({"type": "turn.completed"}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
