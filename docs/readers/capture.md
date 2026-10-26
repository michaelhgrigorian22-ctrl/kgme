---
id: READER-CAPTURE
type: note
status: active
created: 2026-10-21T00:30:00-07:00
modified: 2026-10-26T01:41:15-07:00
author: claude-code
source: inferred
sources: ["HANDOFF-0050", "HANDOFF-0052", "kgme/capture_io.py", "kgme/capture_fs.py", "kgme/daily_io.py", "kgme/brief_kept.py"]
tier: 2
---

# Reader: capture by talking, and the evening draft

*Written 2026-10-21 by Claude Code for HANDOFF-0050.*

## What it is
Two commands put what you say into the vault without you opening a file. `kgme capture` writes your words, verbatim, where they belong. `kgme daily` drafts the day's note from what the ledger and git recorded. In a session, when you state a reminder, a task, a friction, or a note, the agent runs `kgme capture` with your exact words and shows you what it printed (`CLAUDE.md`, "Capture on his word"). You can run both commands yourself.

## Capture
- `kgme capture remind "pay the Backblaze renewal" --due "friday 9am"` creates a new note in `memory/notes/` from `memory/templates/reminder.md`, with `source: stated`, `author: kgme`, and the due written in full with its offset (`2026-10-23T09:00:00-07:00`). `task` and `note` work the same way from their templates; `--due` applies to `remind` and `task` only.
- `--due` understands today, tomorrow, a weekday, `2026-10-20`, `oct 20`, `in 3 days`, `in 2 weeks`, each with an optional time (`9am`, `9:30pm`, `14:00`, `noon`; 09:00 when none). `next friday` and `this friday` are refused as ambiguous, and so is a time already passed. A refusal still records your words in the ledger, so nothing you said is lost.
- `kgme capture friction "<words>"` adds one line at the end of `memory/inbox/friction-log.md`, in the log's format: the date, the time, and your words.
- `kgme capture daily "<words>"` adds `- <words>` under a closing `## Michou` heading in today's note, adding the heading first if the note does not end under it. Before today's note exists, the line is held in the ledger and the evening draft writes it in.

The same words, of the same kind, on the same day, are captured once: a second run prints "already captured". `--dry-run` prints what would be written and writes nothing.

## What a capture never does
It never edits or deletes anything you wrote. A new note is published under a name that did not exist, so nothing is replaced. A line added to the friction log or to a daily note is written by replacing the file whole: KGME reads the file, writes its bytes plus the new line to a hidden file beside it, `.<name>.capture-<id>`, and swaps the two in one step. The file therefore holds either its old text or its old text plus the line, never half a line. KGME then checks that the file it swapped out is exactly what it read. If you saved the same file in Obsidian at that moment, it swaps back, keeps your save, and refuses; say it again. Capture deletes nothing: the swapped-out copy stays beside the file, hidden from Obsidian and from git, and the ledger records what it should hold (the file as read, or the capture's own text after a swap back). `kgme clean kept --yes` removes the copies that still hold exactly that. A copy that holds anything else holds a save of yours that reached it during the swap, and it is never removed: `kgme clean kept` refuses, names it, and removes no copy at all while it stands, and every later capture into that file refuses and names it too, until you merge it into the file by hand and delete it. A past day's note gets no later captures, so the morning brief finds a copy beside one: its `Kept copies` section names every copy that holds a save, with the file it belongs to, and counts the rest with the command that clears them (HANDOFF-0052). A power cut while a new note is published can leave a hidden `.<name>.tmp-<id>` beside it; the note itself is absent or complete, and the temp file can be deleted.

## The evening draft
`kgme daily` drafts `memory/daily/<date>.md` with five sections (Today, Learned, Problems and solutions, Tomorrow, Friction) and a closing `Michou` section holding the lines you captured that day. Every line names the event, commit, handoff, or report it came from. A problem is marked solved only by something that explicitly answers it: a later success under the same key, a PASS of the same review, or your override; otherwise it reads "still open at the end of the day". The draft is written only when the note does not exist and something happened that day, so it never touches a note you began yourself, and a second run does nothing. The next morning's brief reads the draft while the new day has no note yet.
