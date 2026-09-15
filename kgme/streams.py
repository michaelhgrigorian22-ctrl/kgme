"""Vendor event streams to v1 events (ADR-019 §3, `tool_call`; HANDOFF-0026 fixture test).

Purpose: turn the JSON Lines that `claude -p --output-format stream-json` and
`codex exec --json` emit into ledger events of one shape. Phase 1 only proves these parse
the two recorded fixtures under `tests/fixtures/`; Phase 2 calls them live from the cockpit.
Inputs: the lines as strings, and a fallback timestamp for lines that carry none.
Outputs: lists of event dicts, valid under `kgme.events.validate_event`.
Side effects: none. Neither parser opens a file; the caller hands it the lines.
"""

import json
from datetime import datetime

from kgme.events import classify_failure, clip, make_event


def _local_iso(vendor_ts: str | None, fallback_ts: str) -> str:
    """A vendor timestamp (ISO, usually UTC `Z`) as local time with offset, else the fallback."""
    if not vendor_ts:
        return fallback_ts
    parsed = datetime.fromisoformat(vendor_ts.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return fallback_ts
    return parsed.astimezone().isoformat(timespec="milliseconds")


def parse_claude_stream(lines: list[str], fallback_ts: str) -> list[dict]:
    """`claude -p --output-format stream-json` lines to v1 events, one run per session_id.

    Mapping: `system/init` becomes a `note`; each `tool_use` block becomes a `tool_call` keyed
    by the vendor's tool-use id (its input stays out of the summary); each `tool_result`
    becomes a `tool_call` with the same key; `result` becomes an `outcome` whose status
    follows `is_error`. Rate-limit lines are not actions and are skipped. Model text never
    enters a summary (ADR-019 §4): a text block is recorded by its length only.
    """
    found: list[dict] = []
    run_id: str | None = None
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        kind = line.get("type")
        run_id = line.get("session_id") or run_id
        ts = _local_iso(line.get("timestamp"), fallback_ts)
        if kind == "system" and line.get("subtype") == "init":
            found.append(
                make_event(
                    source="claude-code",
                    actor="claude-code.stream",
                    kind="note",
                    run_id=run_id,
                    ts=ts,
                    summary=clip(
                        f"session start model={line.get('model')} "
                        f"version={line.get('claude_code_version')}"
                    ),
                )
            )
        elif kind == "assistant":
            for block in line.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    found.append(
                        make_event(
                            source="claude-code",
                            actor="claude-code.stream",
                            kind="tool_call",
                            run_id=run_id,
                            ts=ts,
                            job=f"tool:{block.get('name')}",
                            key=block.get("id"),
                            summary=clip(f"tool_use {block.get('name')}"),
                        )
                    )
                elif block.get("type") == "text":
                    found.append(
                        make_event(
                            source="claude-code",
                            actor="claude-code.stream",
                            kind="note",
                            run_id=run_id,
                            ts=ts,
                            summary=f"assistant text chars={len(block.get('text', ''))}",
                        )
                    )
        elif kind == "user":
            for block in line.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    found.append(
                        make_event(
                            source="claude-code",
                            actor="claude-code.stream",
                            kind="tool_call",
                            run_id=run_id,
                            ts=ts,
                            key=block.get("tool_use_id"),
                            summary=clip(f"tool_result is_error={bool(block.get('is_error'))}"),
                        )
                    )
        elif kind == "result":
            failed = bool(line.get("is_error"))
            failure_text = f"{line.get('subtype')} {line.get('result')}"
            found.append(
                make_event(
                    source="claude-code",
                    actor="claude-code.stream",
                    kind="outcome",
                    run_id=run_id,
                    ts=ts,
                    status="error" if failed else "ok",
                    class_=classify_failure(failure_text) if failed else None,
                    key=run_id,
                    summary=clip(
                        f"result {line.get('subtype')} turns={line.get('num_turns')} "
                        f"duration_ms={line.get('duration_ms')} "
                        f"cost_usd={line.get('total_cost_usd')}"
                    ),
                )
            )
    return found


def parse_codex_exec(lines: list[str], fallback_ts: str) -> list[dict]:
    """`codex exec --json` lines to v1 events, one run per thread_id.

    Codex lines carry no timestamps, so every event takes `fallback_ts`. Mapping:
    `thread.started` becomes a `note`; `item.completed` becomes a `note` for agent messages
    and reasoning recorded by length only, never by text (ADR-019 §4); a `tool_call` for
    command executions and file changes (the command text stays out of the summary; its exit
    code does not); `turn.completed` becomes an `outcome` with status `ok`, `turn.failed`
    one with status `error`.
    """
    found: list[dict] = []
    run_id: str | None = None
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        kind = line.get("type")
        if kind == "thread.started":
            run_id = line.get("thread_id")
            found.append(
                make_event(
                    source="codex",
                    actor="codex.stream",
                    kind="note",
                    run_id=run_id,
                    ts=fallback_ts,
                    summary=clip(f"thread start {run_id}"),
                )
            )
        elif kind == "item.completed":
            item = line.get("item", {})
            item_type = item.get("type")
            if item_type == "command_execution":
                found.append(
                    make_event(
                        source="codex",
                        actor="codex.stream",
                        kind="tool_call",
                        run_id=run_id,
                        ts=fallback_ts,
                        job="tool:Bash",
                        key=item.get("id"),
                        summary=clip(f"command_execution exit={item.get('exit_code')}"),
                    )
                )
            elif item_type == "file_change":
                found.append(
                    make_event(
                        source="codex",
                        actor="codex.stream",
                        kind="tool_call",
                        run_id=run_id,
                        ts=fallback_ts,
                        job="tool:Edit",
                        key=item.get("id"),
                        summary=clip(f"file_change {len(item.get('changes', []))} file(s)"),
                    )
                )
            elif item_type in ("agent_message", "reasoning"):
                found.append(
                    make_event(
                        source="codex",
                        actor="codex.stream",
                        kind="note",
                        run_id=run_id,
                        ts=fallback_ts,
                        key=item.get("id"),
                        summary=f"{item_type} chars={len(item.get('text', ''))}",
                    )
                )
        elif kind in ("turn.completed", "turn.failed"):
            usage = line.get("usage") or {}
            failed = kind == "turn.failed"
            failure_text = str((line.get("error") or {}).get("message", ""))
            found.append(
                make_event(
                    source="codex",
                    actor="codex.stream",
                    kind="outcome",
                    run_id=run_id,
                    ts=fallback_ts,
                    status="error" if failed else "ok",
                    class_=classify_failure(failure_text) if failed else None,
                    key=run_id,
                    summary=clip(
                        f"{kind} input_tokens={usage.get('input_tokens')} "
                        f"output_tokens={usage.get('output_tokens')}"
                    ),
                )
            )
    return found
