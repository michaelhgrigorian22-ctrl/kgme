---
id: READER-VSCODE
type: note
status: draft
created: 2026-09-09T20:00:00-07:00
modified: 2026-09-09T20:00:00-07:00
author: cowork
source: stated
tier: 2
---

# Reader — VS Code in KGME

*Part 1 (mental model) written 2026-09-09. Part 2 (setup on this machine) is added after the machine audit.*

## What it is, for you
VS Code is a free editor, but in KGME it is a **cockpit**, not a place you write code. Agents write the code; you oversee it. Four parts of VS Code matter, and they map onto how a portfolio manager reviews an analyst's work rather than onto programming.

1. **Explorer** (left sidebar): the repo as a tree. What exists, what changed recently, where the agents put things.
2. **Source Control** (the branching icon): the most important panel. Git records every change to every file; this panel shows them as red and green lines — tracked changes, exactly as in Word, or comparing two versions of a model in Excel. You read the *diff*, not the code. "Why did this line change?" is a question you can ask the agent that made it. Accepting is a commit; rejecting is a revert. Both are one click.
3. **Terminal** (bottom panel): where Claude Code and Codex run. You watch them work in the same window as the files they are changing. Nothing happens off-screen.
4. **Extensions**: Anthropic ships an official Claude Code extension and OpenAI an official Codex extension, so both agents can live in the sidebar. Plus one Python extension and one Markdown extension. That is the whole list.

## The oversight loop
An agent runs a handoff. Files change. Source Control lights up with every changed file. You open each diff, read the red and green, ask questions if anything is unclear, and commit when satisfied — or revert. The commit message names the handoff. That commit is the ledger entry for the change. Nothing reaches the repo's history without passing through your eyes.

## Why this works without you knowing the code
Diffs are small and local. A change to `router/llm.py` is fifteen lines, with a description from the agent of what and why. Your job is not to verify the syntax; it is to verify the *intent* — does this do what the handoff asked, and nothing else? That is a judgment you already exercise professionally.

## What VS Code is not
It is not the vault reader (Obsidian is), not the scheduler (launchd is), and not where KGME runs (the runtime is). It edits the same files as everything else and adds a review surface.

## Habits
- Open the repo as a workspace, not individual files.
- Never commit from a terminal without looking at the Source Control panel first.
- When an agent proposes a change you don't understand, ask it to explain the diff line by line before committing. That is what plan mode and review are for.

## Part 2 — Setup on this machine
*Pending the machine audit. Will cover: the four extensions, workspace settings, the `code` command-line helper, and connecting the Claude Code and Codex extensions to their subscriptions.*
