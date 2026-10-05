# KGME. `make check` is the gate before any commit (ADR-015). Nothing here needs sudo.
.PHONY: check canary-agents

check:
	uv sync --frozen
	uv run ruff check .
	uv run ruff format --check .
	uv run kgme lint
	uv run pytest -q tests -m "not agents"
	@if [ -s logs/scratch/hook-errors.jsonl ]; then echo "make check: logs/scratch/hook-errors.jsonl is not empty; a post-tool hook failed to log (HANDOFF-0028)"; exit 1; fi

canary-agents:
	uv run pytest -q tests/policy -m agents
	@echo; echo "Agent tier of the canary matrix (logs/scratch-test/canary-agents.md):"; cat logs/scratch-test/canary-agents.md
