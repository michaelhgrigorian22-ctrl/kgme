"""`control/schema/lint.py`: the entry point `docs/schema-v1.md` names for the validator.

Purpose: a stable path a human or a hook can run; everything happens in `kgme lint`.
Inputs: the same arguments as `kgme lint`.
Outputs: its output and exit code.
Side effects: none of its own.
"""

import sys

from kgme.cli import main

if __name__ == "__main__":
    sys.exit(main(["lint", *sys.argv[1:]]))
