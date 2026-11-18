---
id: READER-AGENT-FRAMEWORK
type: note
status: active
created: 2026-11-18T01:00:00-08:00
modified: 2026-11-18T01:00:00-08:00
author: cowork
source: stated
tier: 2
---

# Bilal's agent-building framework

*Written by Cowork on 2026-11-18, at Michou's direction, from Bilal's walkthrough of 2026-11-17. Bilal is a software engineer who builds agents. Michou ruled that this framework is how KGME builds agents from now on. `CLAUDE.md` "How agents are built" holds the binding rules; this reader is the reasoning behind them. ADR-025 holds the structure: departments, roles, build-first. The illustrated copy is the Claude Doc "Bilal's Agent-Building Framework".*

## The premise
An agent is a "word-based reality" built around a model, plus deterministic rules that hold it in place. Building one comes down to three jobs:
- give it the tools and context it needs, and let it make its own;
- measure whether it does the job;
- keep up with every new technique.

The medium is code, not visual builders. A builder like n8n can't express the fine-grained control that full autonomy needs. Code can, and the agent writes it.

## 1. Context is attention
Like eyes, an agent can only weigh a few things at once.
- **Tools.** Give it tools by category ("this is for editing"). When it asks for a category, its context switches to show only those tools.
- **Knowledge.** Slice it the same way, so the agent gets a slice and never the whole tree.
- **The prerequisite.** Understand the problem well enough to draw it.

## 2. Tooling follows the objective
Start from the objective and work back:
- what the agent needs to reach the objective;
- what it can build for itself.

An agent that writes its own tools isn't limited to the ones it was given.

## 3. Evals: score the trace, gate what matters
- **Score the trace.** Score the whole trace, from first step to last, not only the final answer.
- **Use a multi-dimension rubric.**
  - **Intent fidelity:** the end of the trace matches the goal stated at the first step.
  - **Context retrieval:** the right tool calls reached the right context.
  - **A domain dimension** for the quality of the result. Bilal left it unnamed; Cowork's note: without it, a run can be faithful and well-sourced and still wrong.
- **Gates.** These are the checks where, in Bilal's words, "if it didn't do this right, there's no chance it got the problem right". Lock them down.
- **The eval board.** Walk through the agent's tool use against the objective, and keep every rule that makes it likelier to reach it.
- **Alignment.** The rubric must match what is good now, and changes as that does.

## 4. Ride the frontier
Every new advance solves a problem nobody had a standard answer for. Before adopting one, name the problem it solves and what it costs.

Subagents and orchestration solve the context problem, at a price in money and time. A computation that runs often can't afford fan-out; manage its context by hand instead.

## Operating model
Michou talks to one orchestrator.
- It manages a team of agents and managers of agents.
- It always hands off the task and keeps the work going.
- It reviews and orchestrates, and does no work itself.
- The subagents it spawns should be visible.

## The hard part
The difficulty is nondeterminism and real-world ambiguity:
- acting on platform UIs;
- sifting large mail stores;
- resolving references without asking: "this address" may match three deals, and the agent must work out which.

## Cowork's qualifications (adopted with the framework)
1. **A rubric is domain judgment.** In finance, the gates are Michou's to write.
2. **An orchestrator-only setup costs more with every agent it adds.** A frequent job gets one agent with a tight slice.
3. **Errors compound across levels.** Cap the depth at three, and gate every handoff between agents.
4. **"Don't ask" has a threshold.** ADR-023's stakes × edge test decides when an agent asks.
