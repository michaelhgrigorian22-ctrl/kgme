---
id: ADR-025
type: decision
status: accepted
created: 2026-11-17T23:45:00-08:00
author: cowork
source: stated
sources: ["ADR-020", "ADR-021", "ADR-022", "ADR-023", "HANDOFF-0046", "HANDOFF-0048", "HANDOFF-0064"]
tier: 2
supersedes: null
---

# ADR-025 — Departments, a role registry, and build-first (amends ADR-020 on when to take a dependency)

*Draft for Michou's acceptance, written by Cowork from his words of 2026-11-17.*

## Context
- **Michou, 2026-11-17.** KGME should run "way more agents", inside "a larger bureaucratic structure". Standing from now on: be "way more liberal" about making KGME's own tools and code and finding ways into things, with no going to find "other random shit" and no waiting for things to happen.
- **What an agent costs today.** Each one costs a handoff. The crew's three roles (0048, 0064) each took a skill, an agent file and Michou's application. At that price KGME will have few agents.
- **What already exists, for one department.** Session levels give each office its jurisdiction (ADR-022). Skills and `CLAUDE.md` are the written rules. ADR-023 and the arbiter pair are the chain of escalation. The ledger is the record.
- **What is missing.**
  - A cheap way to declare an agent.
  - Departments other than Build.
  - A measure of whether an agent did its job, read from its trace and not only from its output: does the end match the intent stated at the start, and did it fetch the right context with the right tools first.

## Decision
1. **Departments.** Agents are grouped in departments.
   - Each department has one manager role. The manager plans, dispatches and reviews, and does no work itself.
   - Worker roles are started per task and end with it.
   - The first departments are Build (the crew's planner, builder and integrator), Design (the design track as it is), Finance, Admin and Scout.
   - Audit sits outside every department and answers to Michou.
2. **A role is one file.** `roles/<department>/<role>.toml` declares:
   - its purpose and the skill it loads
   - its model tier and session level
   - its atlas slice and tools
   - its tier ceiling
   - its rubric and who it escalates to
   
   Adding an agent means writing that file, and `kgme lint` checks it.
3. **A role grants no power.**
   - A role names an existing session level (`control/policy/sessions/`) and, where it needs one, an existing profile (`control/policy/profiles/`). It may narrow either, never widen it.
   - Its `tier_max` is never more sensitive than its level reaches: numerically, `tier_max` is at least the level's ceiling. Tier 1 is never a role's to claim; ADR-021 stays the only route.
   - Because a role grants nothing, `roles/` is not a human path. Any agent may draft a role, and the lint is the fence. New levels and profiles stay Michou's.
4. **Every role has a rubric.**
   - It has three to six dimensions, scored on the run's trace in the ledger and not only on its output.
   - At least one dimension is a gate: fail it and the run fails, whatever else scored.
   - Every role carries two standing gates. **Intent:** the end matches the goal the run stated first. **Context:** the run read what the task needed before acting.
   - Departments add their own dimensions. Finance's are Michou's to write.
5. **Depth and cost.**
   - At most three levels: manager, worker, sub-worker.
   - Workers take the cheap tier wherever their level allows. Managers and the arbiter pair take the strongest.
   - Managers are started per task, not left running.
6. **Build-first.**
   - When KGME needs a tool, it writes it. A third-party dependency is taken only where writing it is hard, already well solved elsewhere and costly to get wrong: cryptography, parsers, protocol stacks. It still enters through a toolbox row under ADR-020.
   - Outside repositories are read for technique, not installed. Scout brings techniques, not packages.
   - Where there is no API, an agent may build its own way in: browser automation, local app stores, AppleScript, the endpoints Michou's own accounts already call. This is allowed on his own accounts and data only, and never past a sign-in, paywall or rule the account would be lost for.
   - The guard, the egress list and Tier 1 bind tools KGME writes exactly as they bind anything else.
   - A tool an agent writes joins the toolbox once its tests, the security scan and Audit pass.

## Amends
- ADR-020 §1, on the decision to take a dependency (build first). Its rules for how a dependency is held stand unchanged.
- Michou's ruling of 2026-10-13 (more outside repositories and public APIs) is reversed by his ruling of 2026-11-17.

## Alternatives considered
- **Agents as handoffs, as now.** Safe, but every agent costs Michou an application, so the count stays low.
- **Roles under `control/` as human paths.** Every new agent would wait for Michou. Rejected because a role grants nothing its level does not already grant.
- **One flat pool with no managers.** Cheaper, but no one owns a department's outcomes, and escalation has no shape.

## Consequences
- **HANDOFF-0071** builds the registry: `roles/`, `kgme agent`, the lint, the org chart in the atlas, and the crew's three roles declared as the Build department.
- **Finance** is the first new department (HANDOFF-0072), once Michou writes its rubric. It is where his time goes once KGME is built, and its gates need judgment only he can supply.
- **Scoring traces against rubrics** is HANDOFF-0046 (`kgme dream`), cut down and moved up to follow 0071.
- **HANDOFF-0038 (LuLu and host rules) moves up the queue.** Admin and any way in that needs the network run once 0038 gives each tool a host rule.
