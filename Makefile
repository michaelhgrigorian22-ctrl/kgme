# KGME. `make check` is the gate before any commit (ADR-015). Nothing here needs sudo.
.PHONY: check setup canary-agents assets

check:
	@test "$$(git config --get core.hooksPath)" = "control/git-hooks" || { echo "make check: core.hooksPath is not control/git-hooks, so commits are not pushed; run: make setup (HANDOFF-0040)"; exit 1; }
	uv sync --frozen
	uv run ruff check .
	uv run ruff format --check .
	uv run kgme lint
	uv run pytest -q tests -m "not agents"
	@if [ -s logs/scratch/hook-errors.jsonl ]; then echo "make check: logs/scratch/hook-errors.jsonl is not empty; a post-tool hook failed to log (HANDOFF-0028)"; exit 1; fi

canary-agents:
	uv run pytest -q tests/policy -m agents
	@echo; echo "Agent tier of the canary matrix (logs/scratch-test/canary-agents.md):"; cat logs/scratch-test/canary-agents.md

# Local configuration a clone cannot carry: the tracked post-commit hook pushes every commit
# (HANDOFF-0040). `make check` refuses to pass until this has run once.
setup:
	git config core.hooksPath control/git-hooks
	@echo "make setup: core.hooksPath = control/git-hooks; every commit on main now pushes (HANDOFF-0040, HANDOFF-0049)"

# Binary assets a toolbox row names (character packs, fonts, models) are never committed: this
# fetches each by its pinned URL and checks its sha256 into a gitignored folder (ADR-020,
# HANDOFF-0044). No row needs one yet, so it does nothing.
assets:
	@echo "make assets: no toolbox row names a binary asset yet (docs/toolbox.md); nothing to fetch"
