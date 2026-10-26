#!/bin/sh
# PostToolUse (HANDOFF-0028). The tool already ran; this records the outcome and the payload.
# It never blocks. If Python cannot even start, the failure is written here, to
# logs/scratch/hook-errors.jsonl under the project, and `make check` fails while that file is
# non-empty. The Python side records its own failures the same way.
uv run --frozen --project "$CLAUDE_PROJECT_DIR" python -P -m kgme.hooks.post_tool_ledger
code=$?
if [ "$code" -ne 0 ]; then
  dir="${CLAUDE_PROJECT_DIR:-.}/logs/scratch"
  mkdir -p "$dir"
  printf '{"ts":"%s","error":"post_tool_ledger.sh: python exited %s before recording"}\n' \
    "$(date +%Y-%m-%dT%H:%M:%S%z)" "$code" >> "$dir/hook-errors.jsonl"
fi
exit 0
