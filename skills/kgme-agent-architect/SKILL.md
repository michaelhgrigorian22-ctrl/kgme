---
name: kgme-agent-architect
description: Design, build, evaluate and narrow an agent (a KGME role) from an objective, covering context, tools, topology, rubric, eval set and registry. Use before creating any new agent or role, when turning a workflow into an agent, or when an agent underperforms. Works in Claude Code and Hermes.
---

# kgme-agent-architect

An agent is a model inside a frame. The frame is a word-based reality (what the agent sees) plus code that holds what must hold (what it may do, and what counts as done). This skill is the procedure for building that frame well.

It builds on Bilal's framework (`docs/readers/agent-framework.md`), Anthropic's published guidance on agent evals (`references/evals.md`), and the failures KGME has already paid for (`references/failure-modes.md`). Read the references the first time you use this skill; read `references/orchestration.md` before designing any team.

## The laws
1. **Context is attention.** The agent sees what its task needs and nothing more: slices, not trees; tool categories opened on request, not every tool.
2. **Words ask, code enforces.** A rule that must hold (a permission, a limit, a format, a number that must tie) lives in code: launch flags, lint, guard, tests. The prompt explains the rule; it never carries it alone.
3. **Grade outcomes, gate the paths that matter.** Judge success on the end state. Score the trace only where the path itself is the point: intent, context, safety.
4. **Start from real failures.** Rubrics and eval tasks come from things that actually went wrong. Dimensions invented in the abstract drift toward what's easy to score.
5. **One conductor, few levels, cheap at the bottom.** At most three levels. Fan-out only where the context won't fit or the subtasks are independent.
6. **Measure, then narrow.** Run it, read the transcripts, profile what it actually called, then take away what it didn't need.
7. **Correct at the highest rung.** When an agent repeats a mistake, fix it as high on the ladder as it can hold: code, then lint and CI, then rules and skills, then the style guide last. A fix on a lower rung is a request the next run can ignore. (From Rat Stack's correction ladder.)
8. **Prove the fence; don't assert it.** "The hooks passed" isn't proof. For every fence, run the forbidden thing on purpose (a bad commit, a write outside Outputs, a bypass flag) and confirm it's refused, and run that probe again after every change to the fence.

## Procedure
Do the steps in order. Each step produces a written output, and the outputs together are the agent's design note.

0. **Is an agent the right tool?** If the steps are fixed, write code (a script or a job). If one prompt does it, write a skill. Build an agent only when the task needs judgment across several steps with tools.
1. **Objective.**
   - One sentence: what the agent achieves.
   - The done state, observable in the world: a file, a commit, a number, a sent draft.
   - Who consumes the output, and the non-goals.
2. **Draw the problem.** Inputs, decisions, outputs. Mark every step *model* (needs judgment) or *code* (a rule suffices). Every *code* step is a tool or a check to build, and never a prompt instruction.
3. **Context.**
   - What it must see, in what order: slice, files, conventions skill, examples.
   - What it must never see (tiers).
   - Disclose progressively: categories first, detail on request.
   - Estimate tokens. A fixed context above about 30% of the window is a design smell.
4. **Tools.**
   - Work back from the objective to the smallest set. For each tool, give the reason, its narrowest form, and what enforces that form (level, role lint, launch flags).
   - **A missing tool gets built** (ADR-025 §6): code with tests, entering the toolbox after scan and Audit.
   - Anything that touches the network or an account gets a host rule and its own role.
   - **Code mode.** When a task is many similar calls (read 40 files, query 30 rows), have the agent write one short program that makes them all and returns the result. It's cheaper and steadier than 40 tool calls. That program runs inside the same fences: a code-execution tool is a write path and is fenced like one.
   - **Real over fake.** Test against the real thing (real git, real files, real services) wherever a fake behaves differently. Every fake you keep is cleaned up with the test that made it.
5. **Topology.**
   - Use a single agent unless the context won't fit, the subtasks are independent, or the parts need different permissions.
   - Otherwise use a manager and workers, with a rubric gate on every handoff between them.
   - Cost check: runs per week × fan-out × cost per run.
   - For a team, follow `references/orchestration.md`: align, plan, implement, verify; state lives in the shared store; first claim wins; the writer never checks its own work.
6. **Rubric** (`references/evals.md` §Rubric).
   - Three to six dimensions, carrying the standing gates (`intent`, `context`) and one dimension for the domain quality of the result.
   - For each dimension: its grader type (code, then model, then human), the evidence the grader must cite, and its reverse case.
   - Every dimension passes the two-expert test.
7. **Eval set** (`references/evals.md` §Eval set).
   - 20 to 50 tasks: real failures, normal cases, and should-not cases.
   - Each task has a reference solution or an acceptance check.
   - Each trial runs in a clean environment, with a turn and dollar budget.
8. **Declare.**
   - `kgme agent new <department> <role>`, then fill the role file: purpose, skill, model, level, tools, tier_max, escalates_to, rubric.
   - Write the role's own skill (template below), and get `kgme lint` clean.
9. **Run, read, measure.**
   - Run the eval set for pass@1 and pass^3.
   - Read at least 10 transcripts in full, passes as well as failures.
   - Profile the tool calls the agent actually made, and log each failure with its root cause.
10. **Narrow and iterate.**
    - Remove the tools it didn't use.
    - Where a judgment kept coming out the same, turn it into code.
    - Fix the rubric wherever you and the judge disagree.
    - Graduate saturated evals into the regression suite.
    - Record lessons in the role skill's `lessons.md`, and keep it short.
    - Apply law 7 to each lesson: if it can be moved up a rung, into lint or code, write the handoff that moves it.
    - Write the agent's systems page (`docs/readers/agents/<role>.md`): what it does, **how to check it**, which is the one command that proves it works, and **how to remove it**, meaning what depends on it and what to delete.
    - List what's unfinished in `docs/DEBT.md`.

## A role's own skill: template
```
---
name: <role-skill>
description: <when this agent is used, one line>
---
# <role>
Objective: <one sentence>. Done when: <observable end state>.
Load first: <conventions skill, slice, files>, in this order.
Procedure: <numbered steps; mark the steps that a tool or check enforces>.
Output: <exact format and location>.
Escalate to <role or michou> when: <the ADR-023 threshold, stated concretely>.
Never: <the never-list; each item also enforced in code where it can be>.
Rubric: roles/<department>/rubrics/<role>.md
```

## Never
- A rule only in a prompt where code could hold it.
- A grader that passes without citing evidence.
- A new agent without an eval set, or tools added "just in case".
- Project or task state kept in an agent's private memory instead of the shared store.
- Shared state between trials: tests that leave processes running or write to the main ledger.
- A worker that stalls waiting: it records what it's waiting for and stops cleanly, to be restarted on that event.
- Treating a model reviewer's PASS as proof of anything outside its rubric.

## Output
A design note (steps 1 to 7) under `docs/readers/agents/<role>.md`, the role file, the role skill, the rubric, the eval tasks under `roles/<department>/evals/<role>/`, and a run report. Then iterate from step 9.
