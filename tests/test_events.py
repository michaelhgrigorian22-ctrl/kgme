"""Tests for the pure event layer (HANDOFF-0026).

Purpose: the field set and enums, redaction, the stream rule, the size cap, ULID
monotonicity, and the two vendor-stream parsers against the recorded fixtures.
Inputs: `tests/fixtures/claude-stream.jsonl`, `tests/fixtures/codex-exec.jsonl`.
Outputs: pytest assertions.
Side effects: none; nothing is written.
"""

from pathlib import Path

import pytest

from kgme import events, streams, ulid

FIXTURES = Path(__file__).parent / "fixtures"
FALLBACK = "2026-09-14T23:00:00.000-07:00"
READ_ONLY = ["Read", "Grep", "Glob", "LS", "TodoRead"]


def event(**overrides: object) -> dict:
    fields: dict = dict(source="kgme", actor="kgme.test", kind="note", summary="hello")
    fields.update(overrides)
    return events.make_event(**fields)


@pytest.mark.blocking
def test_make_event_has_every_field_in_order_and_validates() -> None:
    made = event()
    assert list(made) == list(events.FIELDS)
    events.validate_event(made)


@pytest.mark.blocking
@pytest.mark.parametrize(
    "field, value",
    [
        ("kind", "wish"),
        ("source", "aliens"),
        ("class", "fatal"),
        ("status", "maybe"),
        ("ts", "2026-09-14T10:00:00-07:00"),
        ("ts", "2026-09-14T10:00:00.000Z"),
        ("id", "not-a-ulid"),
        ("id", "8ARZ3NDEKTSV4RRFFQ69G5FAV0"),
        ("id", "01ARZ3NDEKTSV4RRFFQ69G5FAV\n"),
        ("ref", "01ARZ3NDEKTSV4RRFFQ69G5FAV\n"),
        ("parent", "01ARZ3NDEKTSV4RRFFQ69G5FAV\n"),
        ("ts", "2026-09-14T10:00:00.000-07:00\n"),
        ("ts", "2026-99-99T99:99:99.000+99:99"),
        ("ts", "2026-02-30T10:00:00.000-07:00"),
        ("ref", "not-a-ulid"),
        ("parent", "item_0"),
        ("payload_ref", "logs/ledger/2026-09.jsonl"),
        ("payload_ref", "logs/scratch/payloads/../../x.json"),
        ("summary", "x" * 201),
        ("payload_sha256", "abc"),
    ],
)
def test_validate_rejects_bad_values(field: str, value: str) -> None:
    bad = event()
    bad[field] = value
    with pytest.raises(ValueError):
        events.validate_event(bad)


@pytest.mark.blocking
def test_validate_rejects_unknown_field_and_status_off_outcome() -> None:
    extra = event()
    extra["colour"] = "red"
    with pytest.raises(ValueError, match="unknown"):
        events.validate_event(extra)
    with pytest.raises(ValueError, match="only on outcome"):
        events.validate_event(event(status="ok"))
    with pytest.raises(ValueError, match="carry a status"):
        events.validate_event(event(kind="outcome"))
    with pytest.raises(ValueError, match="must carry a class"):
        events.validate_event(event(kind="outcome", status="refused"))
    with pytest.raises(ValueError, match="must carry a class"):
        events.validate_event(event(kind="outcome", status="error"))
    events.validate_event(event(kind="outcome", status="error", class_="transient"))
    events.validate_event(event(kind="outcome", status="ok", class_="cosmetic"))


@pytest.mark.blocking
@pytest.mark.parametrize("value", [True, 1.0, "1"])
def test_version_must_be_the_integer_one(value: object) -> None:
    bad = event()
    bad["v"] = value
    with pytest.raises(ValueError, match="integer"):
        events.validate_event(bad)


@pytest.mark.blocking
@pytest.mark.parametrize(
    "text",
    [
        "token=abc123DEF456ghi789",
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
        "sk-abcdefghijklmnop1234",
        "cat /Users/michou/.ssh/id_ed25519",
        "read ~/.claude/.credentials.json",
        "source ./project/.env.local",
        "cat .env",
        "ls .env.production.backup",
        "apikey: ZZZZZZZZZZZZZZ",
    ],
)
def test_redact_replaces_secret_shapes(text: str) -> None:
    out = events.redact(text)
    assert "<redacted:" in out
    for needle in (
        "abc123DEF456ghi789",
        "eyJhbGci",
        "abcdefghijklmnop",
        "id_ed25519",
        "credentials",
        ".env",
        "ZZZZ",
    ):
        assert needle not in out


@pytest.mark.blocking
def test_redact_leaves_ordinary_text_and_ulids_alone() -> None:
    plain = "Read kgme/paths.py in the environment; id 01ARZ3NDEKTSV4RRFFQ69G5FAV"
    assert events.redact(plain) == plain


@pytest.mark.blocking
def test_stream_rule() -> None:
    assert events.stream_for(event(kind="intent", job="tool:Read"), READ_ONLY) == "trace"
    blocked = event(kind="intent", job="tool:Read", class_="blocking")
    assert events.stream_for(blocked, READ_ONLY) == "ledger"
    assert (
        events.stream_for(event(kind="outcome", status="ok", job="tool:Grep"), READ_ONLY) == "trace"
    )
    assert events.stream_for(event(kind="intent", job="tool:Edit"), READ_ONLY) == "ledger"
    assert (
        events.stream_for(event(kind="outcome", status="refused", job="tool:Read"), READ_ONLY)
        == "ledger"
    )
    assert events.stream_for(event(kind="note", job="tool:Read"), READ_ONLY) == "ledger"
    assert events.stream_for(event(kind="intent", job="brief"), READ_ONLY) == "ledger"


@pytest.mark.blocking
def test_serialize_caps_and_month_file() -> None:
    assert events.month_file("2026-09-14T23:00:00.000-07:00") == "2026-09.jsonl"
    with pytest.raises(ValueError):
        events.serialize(event(key="k" * 5000))
    assert events.serialize(event()).endswith(b"\n")


@pytest.mark.blocking
def test_ulids_are_monotonic_within_a_millisecond() -> None:
    generator = ulid.Generator()
    first = generator.new(now_ms=1_700_000_000_000)
    second = generator.new(now_ms=1_700_000_000_000)
    third = generator.new(now_ms=1_699_999_999_000)
    assert first < second < third
    assert all(len(u) == 26 and events.ULID_PATTERN.match(u) for u in (first, second, third))


@pytest.mark.blocking
def test_claude_fixture_parses_into_valid_events() -> None:
    lines = (FIXTURES / "claude-stream.jsonl").read_text().splitlines()
    parsed = streams.parse_claude_stream(lines, FALLBACK)
    assert parsed, "fixture produced no events"
    for made in parsed:
        events.validate_event(made)
    kinds = [made["kind"] for made in parsed]
    assert kinds[0] == "note" and kinds[-1] == "outcome"
    assert parsed[-1]["status"] == "ok"
    assert len({made["run_id"] for made in parsed}) == 1
    assert parsed[0]["ts"].endswith(("-07:00", "-08:00"))


@pytest.mark.blocking
def test_codex_fixture_parses_into_valid_events() -> None:
    lines = (FIXTURES / "codex-exec.jsonl").read_text().splitlines()
    parsed = streams.parse_codex_exec(lines, FALLBACK)
    assert parsed, "fixture produced no events"
    for made in parsed:
        events.validate_event(made)
    assert [made["kind"] for made in parsed] == ["note", "note", "outcome"]
    assert parsed[-1]["status"] == "ok"
    assert all(made["ts"] == FALLBACK for made in parsed)


CLAUDE_TOOL_LINES = [
    '{"type":"system","subtype":"init","session_id":"s1","model":"m","claude_code_version":"v"}',
    '{"type":"assistant","session_id":"s1","timestamp":"2026-09-15T06:00:00.000Z","message":{"content":'
    '[{"type":"text","text":"SECRET PROSE token=abc123DEF456ghi789"},'
    '{"type":"tool_use","id":"toolu_1","name":"Read","input":{"file_path":"/x/.env"}}]}}',
    '{"type":"user","session_id":"s1","timestamp":"2026-09-15T06:00:01.000Z","message":{"content":'
    '[{"type":"tool_result","tool_use_id":"toolu_1","content":"password=hunter2","is_error":false}]}}',
    '{"type":"result","subtype":"success","session_id":"s1","is_error":false,"num_turns":1,'
    '"duration_ms":10,"total_cost_usd":0.01}',
]

CODEX_TOOL_LINES = [
    '{"type":"thread.started","thread_id":"t1"}',
    '{"type":"item.completed","item":{"id":"item_0","type":"reasoning","text":"private chain"}}',
    '{"type":"item.completed","item":{"id":"item_1","type":"command_execution",'
    '"command":"cat .env",'
    '"exit_code":0,"aggregated_output":"password=hunter2"}}',
    '{"type":"item.completed","item":{"id":"item_2","type":"file_change","changes":[{"path":"a"}]}}',
    '{"type":"turn.failed","error":{"message":"boom"}}',
]


@pytest.mark.blocking
def test_claude_tool_lines_map_to_tool_calls_and_model_text_never_enters_summaries() -> None:
    parsed = streams.parse_claude_stream(CLAUDE_TOOL_LINES, FALLBACK)
    for made in parsed:
        events.validate_event(made)
    assert [m["kind"] for m in parsed] == ["note", "note", "tool_call", "tool_call", "outcome"]
    assert parsed[2]["job"] == "tool:Read" and parsed[2]["key"] == "toolu_1"
    assert parsed[3]["key"] == "toolu_1"
    joined = " ".join(m["summary"] for m in parsed)
    for needle in ("SECRET", "token=", "hunter2", "/x/.env"):
        assert needle not in joined
    assert "chars=" in parsed[1]["summary"]


@pytest.mark.blocking
def test_codex_tool_lines_map_to_tool_calls_and_reasoning_never_enters_summaries() -> None:
    parsed = streams.parse_codex_exec(CODEX_TOOL_LINES, FALLBACK)
    for made in parsed:
        events.validate_event(made)
    assert [m["kind"] for m in parsed] == ["note", "note", "tool_call", "tool_call", "outcome"]
    assert parsed[2]["job"] == "tool:Bash" and "exit=0" in parsed[2]["summary"]
    assert parsed[3]["job"] == "tool:Edit"
    assert parsed[4]["status"] == "error" and parsed[4]["class"] == "blocking"
    joined = " ".join(m["summary"] for m in parsed)
    for needle in ("private chain", "cat .env", "hunter2"):
        assert needle not in joined


@pytest.mark.blocking
def test_failed_runs_carry_a_class_by_the_failure_shape() -> None:
    assert events.classify_failure("rate limit exceeded (429)") == "transient"
    assert events.classify_failure("request timed out") == "transient"
    assert events.classify_failure("boom") == "blocking"
    assert events.classify_failure("") == "blocking"
    claude_lines = [
        '{"type":"result","subtype":"error_during_execution","session_id":"s","is_error":true,'
        '"result":"Rate limit reached","num_turns":1,"duration_ms":1}',
    ]
    parsed = streams.parse_claude_stream(claude_lines, FALLBACK)
    assert parsed[-1]["status"] == "error" and parsed[-1]["class"] == "transient"
    codex_lines = ['{"type":"turn.failed","error":{"message":"upstream 503"}}']
    parsed = streams.parse_codex_exec(codex_lines, FALLBACK)
    assert parsed[-1]["status"] == "error" and parsed[-1]["class"] == "transient"
