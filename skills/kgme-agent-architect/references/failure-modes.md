# Failure modes KGME has paid for

Each entry gives the symptom, the cause, and the prevention, written as code wherever code can hold it. Add to this list; never shorten it.

| Failure | Symptom | Cause | Prevention |
|---|---|---|---|
| Rule only in the prompt | A role used tools it never declared (0071 F2) | Restriction written in the role's prompt, never enforced at launch | Enforce at launch (flags, rendered settings); lint and launch share one validator |
| Identity mismatch | A Tier 1 role escaped its findings (0071 F8) | Lookup rebuilt the path from the declared id | Carry the real source path; id and path mismatch is blocking |
| Orphaned test processes | 1.27 GB test ledger; hour-long suites; refused cleanups | Stub loops outlived interrupted tests and wrote to the main checkout's test ledger | Tests use a temporary ledger; every child process is killed with its test; one clean environment per trial |
| Silent stop | The loop "ended" with no reason (0073, at 60 turns) | Hard stop hit; no reason recorded | Every stop names which limit it hit; budgets are sized from measured runs |
| Routing around a fence | Builder fetched source from GitHub after a sandbox denied the local read | A tool available "just in case" (Agent, WebFetch) | Narrow tools to the objective; a need for outside access is a separate role with a host rule |
| Inherited permissions | Unattended run refused: local "always allow" rules present | A human clicked "always allow" in a session | Loose runs refuse extra local rules (built); humans choose "allow once" in the repo |
| Parallel work in one index | Two handoffs' diffs mixed; reviews covered the wrong code | Building on another uncommitted diff | One handoff per index or workspace; review by patch when sharing |
| Stale status as memory | A brief claimed a review had passed when it hadn't | Status read from a conversation, not the repo | Read `docs/STATUS.md` and the ledger before any brief; update STATUS at every ruling |
| Contended gate | Suites crawled; flaky reds | Two test suites running at once on shared folders | One gate at a time; isolated trial clones |
| Untracked handoff | `git mv` refused; script stopped | Adoption moved an untracked file | Adoption adds the file to git; scripts check before moving |
| Asset missing in a clean copy | Design trial red with 47 errors | Tests depended on an asset in a gitignored folder | Assets fetched by `make assets` in the trial, or tests skip with a named reason |
| State in private memory | Agents lose track of the project and stop collaborating (Anthropic's early multi-agent attempts) | Task state kept in context or per-agent memory | One shared store with transactions; memory holds only preferences and pointers |
| Fence that models semantics | Fence allowed `cd /dev/null; rm …` and a `/tmp/kgme` impostor (0073 F2, F4) | The allow decision simulated shell behavior | Allow only what's fully understood (simple commands, trusted absolute paths); refuse the rest |
| Bypass by flag | An agent commits with `--no-verify` or rewrites `core.hooksPath` | A rule stated only in prompts | The guard refuses the flags; canary tests prove the refusal |
