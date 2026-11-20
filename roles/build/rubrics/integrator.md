# Rubric: build.integrator

Scored on the run's trace in the ledger, not only on its output (ADR-025 §4).

## Dimensions
- `intent` (gate): the end matches the goal the run stated first.
- `context` (gate): the run read what the task needed before acting.
- `no-merge` (gate): the run merged, pushed and approved nothing.
- `screen`: the one approval screen names every task, quarantine, gate result and the line to type.
