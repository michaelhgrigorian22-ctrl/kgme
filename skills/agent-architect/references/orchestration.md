# Orchestration: one lead, a shared store, independent verification

Sources: Anthropic, "Safely scaling multi-agent teams with Claude Fable 5.2" (claude.dev, 2026-11-09), in which 1,000 agents reproduced a Lean proof of Fermat's Last Theorem in 28.7 hours; Kem (GlitchCatClub)'s reel of 2026-11-20 and his comments; Michou's guide, `multi-agent-orchestration-guide.md`. The figures are Anthropic's own and not independently verified. One run is not a reliability statistic.

## The loop
1. **Align.** Write the definition of done and its *mechanical* check before any work starts. No mechanical check means no definition of done: build the smallest checker first.
2. **Plan.** The lead writes the plan into the shared store. Everyone reads the same plan.
3. **Implement.** Workers claim tasks from a shared list, each in its own sandbox and branch.
4. **Verify.** A checker independent of the writer decides. The agent that wrote it never checks it.

## The rules that carry it
- **Agents never message each other.** All coordination goes through the shared store and git.
- **State lives in the shared store, never in an agent's context or private memory.** Anthropic's early attempts failed this way: agents lost track of project state and stopped collaborating.
- **First claim wins.** A task belongs to whoever claims it first, by an atomic update. That's what prevents duplicate work.
- **Lead or merge job is the only path to `main`,** and it refuses conflicts and faults.
- **Split until each piece fits one context window.** Never ask a worker to grind through something too big.
- **Difficulty verdicts are signals, not facts.** In the Fermat run, 47 of 60 pieces were judged infeasible early, and most were proved later. Triage, then revisit what was set aside.
- **Once running, the shared list is the source of work.** The lead's job narrows to verification, triage and unblocking: "do not wait for me".
- **Put checks in the harness, not in ever-longer prompts.** Over-constrained prompts make agents bureaucratic rather than good.

## When to use it, and when not
- **Use a team** for long work (about a million tokens or more in total) that splits into independent, mechanically checkable pieces.
- **Use one agent plus a checker** for small jobs. Readers can fan out; writers usually shouldn't.
- **Codebases don't split like proofs:** shared state and merge conflicts. Keep code teams small (one lead, two or three workers) and scale only when the measured bottleneck is parallel work, not coordination.
- **Measure tokens per landed task** on the first run. Whether cheaper models for workers pay off is an open question: test it, don't assume it.

## Mapping onto KGME
| Pattern | KGME today | Gap |
|---|---|---|
| Lead | `crew` planner (`build.planner`); the conductor across departments | None |
| Sandboxes | `kgme workspace` worktrees, `loose` level | No network isolation per worker until 0038 |
| Merge job | `kgme merge`, `approve --what code` | None |
| Checker | `make check` and `kgme review` (Codex), plus role rubrics | Rubric scoring (0046) not built |
| Shared store | Ledger (append-only events) plus `docs/STATUS.md` | **No shared task table with atomic claim.** Add one: SQLite in the main checkout (transactions, no server), with the tables `announce`, `assign`, `notes`, `subtasks`, `landed` |
| No direct messaging | Agents coordinate through files and the ledger | Keep it that way |

## Private memory (Hermes, Claude memory)
Per-agent memory is for the **conductor's continuity with Michou**: his preferences, his rulings, pointers into the repo. It is never where task or project state lives. If an agent's memory and the shared store disagree, the store wins, and the memory entry gets corrected.
