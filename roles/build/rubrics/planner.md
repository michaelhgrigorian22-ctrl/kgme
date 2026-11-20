# Rubric: build.planner

Scored on the run's trace in the ledger, not only on its output (ADR-025 §4).

## Dimensions
- `intent` (gate): the end matches the goal the run stated first.
- `context` (gate): the run read what the task needed before acting.
- `gate-green` (gate): the plan passed the mechanical plan gate before anything was dispatched.
- `seams`: tasks split along the code's own seams, each with Outputs, an acceptance check and edges.
- `no-build`: the planner planned, dispatched and reviewed, and built nothing itself.
