# Rubric: conductor.hermes

Scored on the run's trace in the ledger, not only on its output (ADR-025 §4).

## Dimensions
- `intent` (gate): the end matches the goal the run stated first.
- `context` (gate): the run read `docs/STATUS.md` and the ledger before dispatching.
- `kgme-only` (gate): every change to the repository went through `kgme loop`, `kgme crew`, `kgme session` or `kgme agent run`; the conductor edited no code, `control/`, `memory/` or `logs/`, and ran no git write.
- `threshold`: Michou was asked only where stakes × edge reached 1.5 (ADR-023), in one batched brief with a recommendation each.
- `plain-report`: the report names what ran, what passed, what is waiting for Michou, and the exact commands he types, in plain words.
