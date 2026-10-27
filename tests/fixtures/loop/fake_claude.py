"""The toy arbiter: `claude -p --model <m> ... <brief>`, one ruling as JSON.

`ARBITER_MODE` decides: `agree` (both rule `blocking`, remove the seed), `split` (the first
model rules `blocking` with blast radius 3, the second `advisory` with blast radius 1, both
reversible). It records the brief, read from stdin as the real call sends it, in `ARBITER_LOG`.
Inputs: argv; `ARBITER_MODE`, `ARBITER_LOG`.
Outputs: the reply on stdout; exit 0.
Side effects: one line appended to `ARBITER_LOG`.
"""

import json
import os
import sys


def main(argv: list[str]) -> int:
    if argv[:1] == ["--version"]:
        print("0.0.0 (toy)")
        return 0
    model = argv[argv.index("--model") + 1]
    with open(os.environ["ARBITER_LOG"], "a") as log:
        log.write(
            json.dumps({"model": model, "brief": sys.stdin.read(), "pid": os.getpid()}) + "\n"
        )
    first = model.startswith("claude-opus")
    if os.environ.get("ARBITER_MODE") == "split" and not first:
        ruling = {"class": "advisory", "option": "accept the seed as documented",
                  "reversible": True, "blast_radius": 1,
                  "reason": "the brief requires it"}  # fmt: skip
    else:
        ruling = {"class": "blocking", "option": "remove the seed", "reversible": True,
                  "blast_radius": 3 if first else 2, "reason": "the seed is a defect"}  # fmt: skip
    print(f"Ruling below.\n```json\n{json.dumps(ruling)}\n```")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
