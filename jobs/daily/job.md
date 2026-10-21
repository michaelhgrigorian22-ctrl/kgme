# daily — `kgme daily` (HANDOFF-0050)

**Purpose.** The daily note is drafted, not typed: today, learned, problems and solutions, tomorrow, friction, from what the day left behind, and Michou's own lines under a closing heading.

**Invocation.** `kgme daily [--date YYYY-MM-DD]`, or `uv run python jobs/daily/run.py`. By hand now; 21:30 every day once the Phase 3 heartbeat exists.

**What it writes.** `memory/daily/<date>.md`, only when it does not exist, and only when the ledger holds an event of that day. Frontmatter `type: daily, status: open, tier: 2, source: inferred, author: kgme, sources: [every event, commit, handoff, report, and note a line cites]`. Sections, each opening with a comment that says it is inferred and from what: `## Today` (the day's commits from `git log`, with the handoff files they moved; handoffs completed that day; the day's job outcomes and Michou's ledger notes, each with its event id; the count of agent tool calls), `## Learned` (the day's reports under `docs/audit/`, review cycles excepted, and the arbiter's rulings), `## Problems and solutions` (each blocked review, refused or failed outcome, then the first later outcome of the same job that cleared it, or "still open"; anything the draft could not read), `## Tomorrow` (open handoffs; open reminders and tasks due by the end of the next day, overdue included), `## Friction` (the friction log's lines dated that day), `## Michou` (marked `stated`: the lines `kgme capture daily` held for the day; later captures append here). An empty section says so.

**A second run** does nothing and records nothing. So does a day with no ledger event.

**Transaction.** As `kgme capture`'s: one `intent` (destination and sha256 prefix), the file created new and written whole, one `outcome`; refusals and failures are classified outcomes; the vault lock; open intents reconciled on start.

**Manifest.** `manifest.toml` beside this file: read `memory/notes`, `memory/agent`, `memory/daily`, `memory/inbox`, `memory/templates`, `docs/handoff`, `docs/audit`; write `memory/daily`; tool `git` for one read-only `git log`; no network.
