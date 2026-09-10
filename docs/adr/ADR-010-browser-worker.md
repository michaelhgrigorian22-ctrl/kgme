---
id: ADR-010
type: decision
status: accepted
created: 2026-09-09T19:45:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-010 — The browser worker

## Context
Michou's school blocks creation of Canvas API tokens, so course material must be reached through an authenticated browser session on the school account, while the calendar lives on a personal Google account. Full control of his daily browser is the Instinct failure mode and is rejected.

## Decision
- A **dedicated Chrome profile owned by KGME**, logged into only the accounts a job needs (school SSO for Canvas and school mail). Never Michou's daily profile.
- Driven by **Playwright** (persistent context) for scheduled runs. The Claude in Chrome extension remains available for interactive, watched tasks in the daily browser.
- **Scoped by allowlists:** per job, a domain allowlist and an action allowlist. Navigate, read, and download are default; form submission, sending, and payment are denied unless a job is explicitly granted them and gated by approval.
- **API through the browser:** the Canvas web UI calls `/api/v1/...` with the session cookie; read-only API calls made from inside the authenticated browser context return structured JSON without HTML scraping. Prefer this; scrape only where it fails.
- **Canvas iCal feed** (a secret URL, Tier 0) covers structured due dates with zero automation, subscribed from the personal Google Calendar.
- **Auth check first:** every browser job verifies it is still logged in; on redirect to SSO or an MFA challenge it stops and asks for a human login. **MFA is never automated.**
- **Credential boundary:** the profile's cookies and tokens are never exported, copied, or logged. The browser is a credential the agent invokes but cannot read.
- The browser worker is a reader (ADR-009): no calendar, file-write, or messaging tools.

## Alternatives considered
- Cookie export to a headless client: turns a session into a portable credential. Rejected.
- Full control of the daily browser: rejected as above.

## Consequences
Session expiry means occasional manual re-login — accepted as the price of a stolen laptop being unable to act as Michou at the university. Check the university's acceptable-use policy before the first scheduled run.
