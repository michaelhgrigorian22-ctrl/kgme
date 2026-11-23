# Hermes profile: kgme-conductor

This is the source of the Hermes profile that runs KGME's conductor. It's versioned here and exported to `~/.hermes/profiles/kgme-conductor/` by the install (proposal HANDOFF-0076).

- `SOUL.md`: the persona and standing orders. Michou owns it; edit it here, never in Hermes's UI, so the repository stays the source.
- **Model:** `anthropic/claude-opus-5-5` on provider **anthropic** (his Claude login). Never `nous`.
- **Skills:** the conductor relies on `kgme-conductor`, `kgme-agent-architect`, `kgme-learn` and `kgme-atlas`, plus `research-conventions` once the Finance department starts. Whether a Hermes profile can limit its skills is measured in HANDOFF-0076 §1. If skills load progressively, with only the name and description in context until one is used, 68 costs little and no limit is needed.
- **Environment:** `KGME_CONDUCTOR=hermes`, so every run it starts is tagged in the ledger.
- **Fence:** the `pre_tool_call` hook from HANDOFF-0073, with `fail_closed: true`.

## How to check it
In a profile session, ask: "What does docs/STATUS.md say is next?" It should answer from the file. Then: "Commit docs/STATUS.md." It should refuse, and the hook should log the refusal.

## How to remove it
Delete `~/.hermes/profiles/kgme-conductor/` and this folder. Nothing else depends on it.
