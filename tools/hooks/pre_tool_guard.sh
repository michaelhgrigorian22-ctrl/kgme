#!/bin/sh
# PreToolUse (HANDOFF-0028). Every tool call passes through the Python guard, which writes the
# intent and blocks by resolved path. The guard's own verdict is exit 0 (proceed) or 2 (block).
# Anything else, including uv or Python failing to start or an import error, is mapped to 2:
# a guard that cannot run fails closed (ADR-013 §2). No `exec`: the mapping must run.
uv run --frozen --project "$CLAUDE_PROJECT_DIR" python -m kgme.hooks.pre_tool_guard
code=$?
if [ "$code" -eq 0 ]; then
  exit 0
fi
if [ "$code" -ne 2 ]; then
  echo "refused: guard exited $code before deciding (startup or import failure); failing closed" >&2
fi
exit 2
