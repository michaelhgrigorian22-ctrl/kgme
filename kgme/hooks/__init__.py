"""Claude Code hook pair: the pre-tool guard and the post-tool ledger (HANDOFF-0028).

Purpose: make every Claude Code tool call an intent/outcome pair in the ledger (ADR-013 §4,
ADR-019 §3) and enforce the path blocklist by resolved path, which settings patterns cannot
do for symlinks and nested files (ADR-008).
Inputs: the hook JSON Claude Code writes to stdin.
Outputs: exit codes Claude Code understands; ledger events.
Side effects: see each module.
"""
