#!/bin/sh
# SessionEnd (HANDOFF-0040, HANDOFF-0061). The session is over; this writes its `session:end`
# note, then starts `kgme sync` in the background,
# which commits logs/ledger/ by pathspec if a foreign event is new and pushes, so the
# session's events reach the remote. Not Stop: every turn would be a commit. Same shape and
# failure path as the post-commit hook: never blocks, never prompts, the run's lines go to
# logs/scratch/sync.log, and a failure to start goes to logs/scratch/hook-errors.jsonl, which
# makes `make check` fail until it is read and emptied.
GIT_TERMINAL_PROMPT=0
export GIT_TERMINAL_PROMPT
project="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
dir="${project:-.}/logs/scratch"
mkdir -p "$dir"
# HANDOFF-0061 §1: first the session's `session:end` note, from the hook input on stdin, so the
# cockpit draws the session closed and `kgme sync` carries the note; a failure to start is
# written beside the sync's.
uv run --frozen --project "$project" python -P -m kgme.hooks.session_end
code=$?
if [ "$code" -ne 0 ]; then
  printf '{"ts":"%s","error":"session_end_sync.sh: session_end exited %s"}\n' \
    "$(date +%Y-%m-%dT%H:%M:%S%z)" "$code" >> "$dir/hook-errors.jsonl"
fi
(
  trap '' HUP
  uv run --frozen --project "$project" kgme sync --base "$project"
  code=$?
  if [ "$code" -ne 0 ]; then
    printf '{"ts":"%s","error":"session_end_sync.sh: kgme sync exited %s"}\n' \
      "$(date +%Y-%m-%dT%H:%M:%S%z)" "$code" >> "$dir/hook-errors.jsonl"
  fi
) >> "$dir/sync.log" 2>&1 &
exit 0
