# KGME. `make check` is the gate before any commit (ADR-015). Nothing here needs sudo.
.PHONY: check canary-agents

check:
	uv sync --frozen
	uv run ruff check .
	uv run ruff format --check .
	uv run kgme lint
	uv run pytest -q tests -m "not agents"

canary-agents:
	@echo "make canary-agents: not built (HANDOFF-0032)"; exit 2
