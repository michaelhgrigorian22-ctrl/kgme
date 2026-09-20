"""`kgme review`, the rendering: the escalation packet and the audit file text.

Purpose: turn a `LoopState` and a list of findings into the one-screen packet ADR-016 asks
for and into the durable audit record `kgme review` writes under `docs/audit/`.
Inputs: findings, a loop state, identifiers, the reviewer's raw text.
Outputs: strings.
Side effects: none, except `audit_text`, which reads the clock for its `created` field.
"""

from datetime import datetime

from kgme.review import LoopState
from kgme.review_parse import Finding, counts, open_blocking


def escape_cell(text: str) -> str:
    """A cell rendered back into a Markdown table: a literal pipe becomes `\\|`."""
    return text.replace("|", "\\|")


def escalation_packet(handoff: str, state: LoopState, findings: list[Finding], arbiter: str) -> str:
    """ADR-016's one screen: what failed, class, evidence, options, default, cost of silence."""
    open_rows = [f for f in findings if f.id in state.open_ids]
    evidence = (
        "\n".join(f"  {f.id} {f.where}: {f.text}" for f in open_rows) or "  (see the audit file)"
    )
    return (
        f"ESCALATION {handoff}: review loop halted after {state.cycles} cycles.\n"
        f"What failed: {state.reason}. Class: blocking.\n"
        f"Evidence:\n{evidence}\n"
        f"Options: override (kgme review override --handoff {handoff} --reason ...), reject "
        "(revert the working tree), retry (fix, then override, then kgme review again); a "
        f"disputed class goes to the arbiter {arbiter} once, recorded with kgme review rule.\n"
        "Recommended default: override and continue when the remaining findings are understood; "
        "reject when they are not.\n"
        "If you do nothing: nothing is committed."
    )


def audit_text(
    number: int,
    handoff: str,
    cycle: int,
    sha: str,
    model: str,
    findings: list[Finding],
    verdict_word: str,
    raw: str,
) -> str:
    """The durable record of one cycle: frontmatter, the classed table, the raw reviewer text.

    Cells are escaped so the table parses back identically. Reads the clock for `created`."""
    rows = "\n".join(
        f"| {f.id} | {f.cls}{', resolved' if f.resolved else ''} | {escape_cell(f.where)} | "
        f"{escape_cell(f.text)} | {escape_cell(f.fix)} |"
        for f in findings
    )
    tally = counts(findings)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"---\nid: AUDIT-{number:04d}\ntype: report\nstatus: final\nhandoff: {handoff}\n"
        f'author: codex\nsource: inferred\nsources: ["{handoff}", "staged diff sha256 {sha}"]\n'
        f"tier: 2\ncreated: {now}\nperiod: {now[:10]}\nreview_cycle: {cycle}\nreviewer: {model}\n"
        f"verdict: {verdict_word}\nopen_blocking: [{', '.join(open_blocking(findings))}]\n---\n\n"
        f"# Review of {handoff}, cycle {cycle}\n\n"
        f"Reviewer `{model}` via `codex exec --json -s read-only`, diff sha256 `{sha}`. "
        f"Verdict **{verdict_word}**: blocking {tally['blocking']}, "
        f"transient {tally['transient']}, cosmetic {tally['cosmetic']}, advisory "
        f"{tally['advisory']} (resolved rows excluded). Written by `kgme review`; the "
        "reviewer's text is verbatim below.\n\n"
        "## Findings\n\n| id | class | file:line | finding | fix |\n|---|---|---|---|---|\n"
        f"{rows or '| (none) | | | | |'}\n\n## Verdict\n\n{verdict_word}\n\n"
        f"## Reviewer text\n\n{raw.strip()}\n"
    )
