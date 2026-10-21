"""PreToolUse entry point: write the intent, or the intent and its refusal (HANDOFF-0028).

Purpose: the enforcement layer ADR-008 named and the first half of the ADR-013 §4 pair. Since
2026-09-23 (HANDOFF-0032 follow-up, Michou's ruling) it also refuses the file-writing tools on
the human-authored paths `kgme.toml` `[hooks].human_paths` names: guard rule 4. In loop mode
(`KGME_LOOP_HANDOFF`, HANDOFF-0045 §2) it refuses a file write outside the handoff's
`Outputs` list, read from `<scratch>/loop/<KGME_LOOP_RUN>/outputs.txt`: guard rule 5.
Inputs: the hook JSON on stdin; `kgme.toml` `[hooks]` and `[paths]`; `--test-streams` for tests.
Outputs: exit 0 to let the call proceed under the settings file; exit 2 with one line on
stderr to block it. Nothing on stdout.
Side effects: one or two ledger or trace lines per call; reads any script a Bash line would
run, and only after the line itself has been allowed, so a forbidden path is never opened.
Any internal failure is itself recorded as a blocking outcome when the ledger can be reached,
and the call is blocked either way.

This module is live on every tool call of every Claude Code session in the repository. It is
never edited in place: a half-edited guard blocks the edit that would finish it (learned twice,
2026-09-15, AUDIT-0014). A new version is staged, exercised, and copied in whole.
"""

import os
import sys
from pathlib import Path

from kgme import events, ledger, loop_outputs, paths
from kgme.hooks import common, guard


def main(argv: list[str]) -> int:
    """Read, decide, record, exit. Returns the exit code; `sys.exit` happens only at the edge."""
    session_id = "no-session"
    try:
        payload = common.read_payload()
        session_id = str(payload.get("session_id") or session_id)
        places, settings = common.read_places(argv)
        hooks = settings["hooks"]
        tool_name = str(payload["tool_name"])
        tool_input = payload.get("tool_input") or {}
        cwd = Path(payload.get("cwd") or paths.root())
        blocklist = [paths.resolve(p) for p in hooks["blocklist"] if not p.startswith("**/")]
        blocklist += paths.tier1_paths(settings)
        name_patterns = [p[3:] for p in hooks["blocklist"] if p.startswith("**/")]
        allow_outside = [paths.resolve(p) for p in hooks.get("allow_outside", [])]
        human = tuple(hooks["human_paths"])
        handoff = os.environ.get(loop_outputs.ENV_HANDOFF, "")
        loop = loop_outputs.read_outputs(places.scratch)
        fences = {
            "human_paths": human,
            "loop": loop,
            "loop_handoff": handoff,
            "loop_dir": places.scratch / "loop",
        }
        rule = (cwd, paths.root(), blocklist, name_patterns, allow_outside)
        # First the line alone. Only an allowed line has its scripts opened: every script path
        # is itself a fragment of the line, so a forbidden one is refused before any read.
        decision = guard.decide(tool_name, tool_input, *rule, **fences)
        if decision.allowed:
            extra, uninspectable = _read_script_fragments(tool_name, tool_input, cwd, allow_outside)
            if extra or uninspectable:
                decision = guard.decide(
                    tool_name,
                    tool_input,
                    *rule,
                    extra_paths=extra,
                    uninspectable=uninspectable,
                    **fences,
                )
        parent = common.read_session_parent(session_id, places.streams)
        # A refused call's intent carries the blocking class so the writer routes it to the
        # ledger beside its refusal (ADR-019 §2); an allowed call's intent carries none.
        intent_id = _append_intent(
            payload,
            places.streams,
            tool_name,
            tool_input,
            session_id,
            parent,
            len(decision.paths),
            None if decision.allowed else "blocking",
        )
        if decision.allowed:
            return 0
        ledger.append(
            events.make_event(
                source="claude-code",
                actor="claude-code.hook",
                kind="outcome",
                status="refused",
                class_="blocking",
                run_id=session_id,
                job=f"tool:{tool_name}",
                key=common.call_key(payload),
                ref=intent_id,
                parent=parent,
                summary=events.clip(decision.reason),
            ),
            places.streams,
        )
        print(decision.reason, file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - a guard that cannot decide must block, and say why
        print(f"refused: guard failed: {type(error).__name__}: {error}", file=sys.stderr)
        _record_failure(argv, error, session_id)
        return 2


def _read_script_fragments(
    tool_name: str, tool_input: dict, cwd: Path, allow_outside: list[Path]
) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    """Paths named inside the scripts a Bash line runs, and the scripts the guard may not read.

    Effects live here, not in `guard`: the existence check and the read. A script outside the
    repository and the allowed roots, or one that cannot be read, is reported uninspectable and
    the line is refused; its text is never opened.
    """
    extra: list[Path] = []
    uninspectable: list[Path] = []
    root = paths.root()
    for script in guard.script_candidates(tool_name, tool_input, cwd):
        if not script.is_file():
            continue
        if not guard.is_under_any(script, [root, *allow_outside]):
            uninspectable.append(script)
            continue
        text = common.read_script_text(script)
        if text is None:
            uninspectable.append(script)
            continue
        extra.extend(guard.resolve_all(guard.fragments(text), cwd))
    return tuple(extra), tuple(uninspectable)


def _append_intent(
    payload: dict,
    dirs: ledger.Dirs,
    tool_name: str,
    tool_input: dict,
    session_id: str,
    parent: str | None,
    candidates: int,
    class_: str | None,
) -> str:
    """The intent, with the budgeted summary; if redaction still overflows the writer's cap,
    once more with the withheld summary. Any other error propagates and blocks the call."""
    fields = dict(
        source="claude-code",
        actor="claude-code.hook",
        kind="intent",
        class_=class_,
        run_id=session_id,
        job=f"tool:{tool_name}",
        key=common.call_key(payload),
        parent=parent,
    )
    try:
        summary = common.summarize_call(tool_name, tool_input, candidates)
        return ledger.append(events.make_event(summary=summary, **fields), dirs)
    except ValueError as error:
        if "after redaction" not in str(error):
            raise
        summary = common.withheld_call(tool_name, candidates)
        return ledger.append(events.make_event(summary=summary, **fields), dirs)


def _record_failure(argv: list[str], error: Exception, session_id: str) -> None:
    """Best effort: a blocking outcome naming the failure. If the ledger failed, stderr is all."""
    try:
        places, _ = common.read_places(argv)
        ledger.append(
            events.make_event(
                source="claude-code",
                actor="claude-code.hook",
                kind="outcome",
                status="error",
                class_="blocking",
                run_id=session_id,
                job="tool:unknown",
                summary=f"guard failed: {type(error).__name__}",
            ),
            places.streams,
        )
    except Exception:  # noqa: BLE001 - nothing left to report to
        return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
