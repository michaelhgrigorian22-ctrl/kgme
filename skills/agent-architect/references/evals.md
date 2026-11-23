# Rubrics and eval sets

Sources: Anthropic, "Demystifying evals for AI agents" (anthropic.com/research/demystifying-evals-for-ai-agents); Claude Platform docs, "Define success criteria and build evaluations"; Claude cookbook, "Outcomes: agents that verify their own work"; Bilal's walkthrough of 2026-11-17. Paraphrased here; read the originals for detail.

## Rubric
- **Shape.** Three to six dimensions, each a pass or fail, partial credit allowed on multi-step work.
  - Gates fail the run outright. Every role has two: `intent` (the end matches the goal stated first) and `context` (it read what the task needed before acting).
  - Add one domain dimension for the quality of the result. Without it, a run can be faithful and well-sourced and still wrong.
- **Two-expert test.** Two people who know the domain must reach the same verdict from the transcript alone. If they wouldn't, rewrite the dimension.
- **Grader order.** Code first: tests, lint, file and ledger checks, tool-call checks, tie-outs. Then a model judge. Then a human (Michou), mainly to calibrate the model judges.
- **Model judges:**
  - one judge per dimension, never one judge for everything;
  - the judge must cite evidence, such as a file and line, a quote or a ledger event, or it fails the dimension;
  - the judge may answer `unknown`, which counts as a failure to investigate, never as a pass;
  - the judge never sees the agent's own reasoning, only the outcome and the trace.
- **Reverse cases.** For each behavior, also test where it should *not* happen (should ask / shouldn't ask, should fetch / shouldn't fetch). One-sided evals produce one-sided agents.
- **Grade the outcome, not the exact path.** Agents find valid routes nobody anticipated. Check the path only for the gates and for safety.

## Eval set
- **Size and source.** Start with 20 to 50 tasks taken from real failures and the checks you already run by hand. Grow it later.
- **Every task:** an input, a reference solution or acceptance check that proves it's solvable, the graders, and a budget in turns and dollars.
- **Clean environment per trial.** Nothing shared: no main ledger, no leftover processes, no scratch from another trial.
- **Score pass@1 and pass^3.** At 75% per trial, pass^3 is about 42%. For an agent that runs unattended, pass^3 is the number that matters.
- **When a task scores 0% across many trials,** suspect the task or its grader first.
- **Read transcripts.** At least 10 in full each round, passes as well as failures. Scores hide grader bugs.
- **Saturation.** Near 100%, the set catches regressions but shows no improvement: graduate it into the regression suite and add harder tasks.

## Calibration loop
1. Michou grades 15 to 20 transcripts per dimension, blind to the judge.
2. Run the model judge on the same transcripts.
3. Where they disagree, the rubric wording is wrong, not the judge. Rewrite, then re-run.
4. Record the agreement rate in the role's run report, and re-calibrate when the role's skill or model changes.
