---
name: kgme-learn
description: Learn mode. While doing real work, explain to Michou what the agent is doing and why, in terms of how software behaves (processes, files, git, tests, permissions, fences), and keep a log of what he has covered. Use when Michou says "learn mode", "explain as you go" or "teach me while you do this".
---

# kgme-learn

Michou is learning how software *behaves*, not how to write it. The aim is a working model of processes, files, state, git, tests and fences, good enough to know which gates to ask for. Bilal's thesis and Rat Stack's learn mode both point the same way: learn on real work, not from a course.

## While learn mode is on
1. **Do the real task.** Learn mode adds explanation and never changes what gets done.
2. **At each step that teaches something,** add a short "what just happened" note, three sentences at most:
   - the concept, named plainly (for example "a git worktree", "a process outliving its parent", "an exit code");
   - why it matters for this task;
   - one way Michou could see it for himself (a command, a file, a ledger line).
3. **Prefer concepts tied to a failure we hit.** The list is in `skills/kgme-agent-architect/references/failure-modes.md`. Every one of them is a lesson that already happened.
4. **Check understanding once per session,** with one question he can answer in a line. Never quiz twice in a row.
5. **Never invent analogies that are wrong in the details.** If a simplification drops something, say what it drops.

## The log
Append to `memory/agent/learning-log.md`, one line per concept:
`- YYYY-MM-DD: <concept>: <one-line plain definition> (seen in: <task or file>)`

Before teaching a concept, check the log. If it's already covered, build on it rather than re-explaining.

## Off
Learn mode ends when Michou says so, or with the session. It never adds explanation to work done unattended.
