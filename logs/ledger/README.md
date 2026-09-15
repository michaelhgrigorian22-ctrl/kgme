# logs/ledger/ — the durable event record

One file per month, `YYYY-MM.jsonl`, one JSON object per line, schema in `docs/adr/ADR-019-ledger-event-schema.md`. Tracked in git, never deleted, never edited: a correction is a new line with `kind: correction` and `ref` pointing at what it corrects (ADR-003, ADR-012). Written only by `kgme/ledger.py`. Read-only tool events live in `logs/trace/`, untracked, same schema.
