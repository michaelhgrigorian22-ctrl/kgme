---
id: ADR-021
type: decision
status: proposed
created: 2026-10-14T00:35:00-07:00
author: cowork
source: stated
tier: 2
supersedes: null
---

# ADR-021 — Tier 1 is disclosed by the request, not the response; encryption's place; the declassification gate (amends ADR-002)

## Context
ADR-002 fixes the tiers by location and says a Tier 1 fact leaves the machine only per item, per request, human-confirmed, written to the ledger. Two gaps surfaced on 2026-10-13 and 14. First, a request shaped by Tier 1 content discloses it even when the response is public: a brief that asks a market-data host for the tickers Michou holds has told that host what he holds. Second, Michou asked whether cryptography could carry Tier 1 to cloud models: "have we looked into encryption math or tools like Midnight to send large information and then sort it and filter it through an encrypted gateway?" This ADR answers both, so the answer lives in the repo and not in a chat.

## Decision
1. **Disclosure is judged by the request.** A worker's request to any host outside the machine may carry Tier 1 content (positions, tickers held, account identifiers, balances, amounts) only through the gate in §3. A worker that needs Tier 1 context queries a superset instead (a sector universe, a watchlist that contains the book, bulk end-of-day files) and filters locally under the Tier 1 profile. `kgme brief` is designed this way from its first market-data row (HANDOFF-0044 §3).
2. **Encryption's place.** At rest: `age` for the private repository and FileVault for the disk (HANDOFF-0038). In transit: TLS to every host, which the toolbox row's egress host implies. Never as declassification: a model must read plaintext to reason about it, so encrypting a payload and decrypting it at the provider moves the key, not the reader. "Send it encrypted, then sort and filter it behind a gateway" is the right shape only when the gateway runs on this machine under the Tier 1 profile. That gateway is the router (Sentinel, Phase 2), and the only thing that crosses the egress boundary is the gate's output.
3. **The gate.** Sentinel's declassification path is a transform, confirmed per item and ledgered as ADR-002 requires (`kind: approval`): dictionary-first pseudonymisation (ticker → token, counterparty → token, amounts → buckets or deltas) → the cloud call → rehydration on this machine. The dictionary lives in Tier 1 and never leaves. Its limit is transform versus substance: the gate may change identifiers and scale, never a structure a sector-aware reader could invert (a single-name position in a thin sector is identifiable through any token). The gate makes the confirmed act mechanical; it does not make it automatic.
4. **Techniques, placed.** Fully homomorphic encryption: not practical for language-model inference at any useful size; revisit only when a provider ships it, as a toolbox row. Zero-knowledge proof systems (Midnight and its kind): prove a statement about hidden data — eligibility, a balance above a threshold — without revealing it; the right tool for proving a fact to a third party, the wrong tool for having a model reason over the data; no KGME use today, recorded for the day one exists. Trusted execution environments ("confidential inference", attested enclaves on CPU and GPU, offered by several providers in 2026): the only mechanism by which a cloud model reads plaintext its operator cannot; it moves the trust from the provider to the hardware vendor and the attestation chain, and is permitted for Tier 1 only by a later ADR, after a provider is in the toolbox and a job verifies its attestation on every call. Local models (Ollama, Phase 2): the default for Tier 1 reasoning; the gate exists for the cases local is not good enough for.

## Alternatives considered
- Encrypt and send, decrypt at the provider: rejected; a key relocation, not a declassification.
- A provider's zero-retention terms as the boundary: rejected for Tier 1; a policy is not a mechanism. Sufficient for Tier 2 under the allowlist, as today.
- Tier 1 never leaves, no gate: rejected by Michou's own policy in ADR-002 ("he may explicitly choose to share a single position"); the gate is how that choice is made safe.

## Consequences
ADR-002's Tier 1 row reads "Local (Ollama) only; cloud through the gate of ADR-021, per item" once this ADR is accepted. ADR-020's toolbox row gains a column: the highest tier a request to that host may contain (default 3; 2 by allowlist; 1 only through the gate). Sentinel's specification includes the gate and its dictionary. `kgme brief` and every worker query supersets. ADR-007's routing table is amended when the router lands. The declassification mapping noted on the open list since 2026-10-09 is this ADR.
