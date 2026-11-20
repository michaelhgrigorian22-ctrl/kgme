# Rubric: build.builder

Scored on the run's trace in the ledger, not only on its output (ADR-025 §4).

## Dimensions
- `intent` (gate): the end matches the goal the run stated first.
- `context` (gate): the run read what the task needed before acting.
- `red-first` (gate): a failing test or check was run before the code that makes it pass.
- `outputs` (gate): every write fell inside the task's Outputs.
- `pass`: the run stopped at a PASS review with one commit by pathspec, or escalated.
