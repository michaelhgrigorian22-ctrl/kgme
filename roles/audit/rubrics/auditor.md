# Rubric: audit.auditor

Scored on the run's trace in the ledger, not only on its output (ADR-025 §4).

## Dimensions
- `intent` (gate): the end matches the goal the run stated first.
- `context` (gate): the run read what the task needed before acting.
- `trace` (gate): every score cites the ledger events it was read from.
- `rubric`: each dimension of the audited role's rubric is scored, gates first.
