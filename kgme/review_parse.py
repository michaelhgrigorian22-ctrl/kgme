"""`kgme review`, the parser: a reviewer's markdown into classed findings and a verdict.

Purpose: read the reviewer's reply the way the prompt defines it (`tools/review/prompt.md`):
a `## Findings` table, a `## Verdict` line, `## Notes`. Sections are found by whole header
lines, so a header quoted inside a table cell opens nothing. Rows and the verdict are read
only inside their own sections.
Inputs: markdown text.
Outputs: `Finding` lists, a `Parsed` review, a verdict word, class counts.
Side effects: none.
"""

import re
from dataclasses import dataclass, replace

from kgme import events

CLASSES = ("blocking", "transient", "cosmetic", "advisory")
ESCAPED_PIPE = "\x00pipe\x00"
ROW = re.compile(
    r"^\|\s*(?P<id>F\d+)\s*\|\s*(?P<cls>[^|]*)\|\s*(?P<where>[^|]*)\|"
    r"\s*(?P<text>[^|]*)\|\s*(?P<fix>[^|]*)\|\s*$"
)
ROW_START = re.compile(r"^\|\s*F\d+\s*\|")
TABLE_HEADER = re.compile(r"^\|\s*(id\s*\||\(none\))", re.IGNORECASE | re.MULTILINE)
HEADER_LINE = re.compile(r"^## (?P<name>[A-Za-z ]+?)\s*$", re.MULTILINE)
VERDICT_WORD = re.compile(r"\b(PASS|BLOCK)\b")
RESOLVED_WORD = re.compile(r"\b(resolved|closed)\b")


@dataclass(frozen=True)
class Finding:
    """One row of the reviewer's table. `resolved` is the reviewer's own word for a closed row."""

    id: str
    cls: str | None
    resolved: bool
    where: str
    text: str
    fix: str


@dataclass(frozen=True)
class Parsed:
    """What the reviewer's text amounts to. Not `parseable` means it is not a usable review."""

    findings: list[Finding]
    verdict_word: str | None
    parseable: bool
    problem: str


def section(markdown: str, name: str) -> str | None:
    """The text under the line that is exactly `## <name>`, up to the next `## ` line, or None."""
    start = None
    for match in HEADER_LINE.finditer(markdown):
        if start is not None:
            return markdown[start : match.start()]
        if match["name"].strip() == name:
            start = match.end()
    return markdown[start:] if start is not None else None


def _cell(raw: str) -> str:
    return raw.replace(ESCAPED_PIPE, "|").strip()


def parse_rows(text: str) -> list[Finding]:
    """Finding rows anywhere in `text`: for a bare table, such as a reclassification reply.
    `\\|` inside a cell is a literal pipe."""
    found: list[Finding] = []
    for line in text.splitlines():
        match = ROW.match(line.strip().replace("\\|", ESCAPED_PIPE))
        if not match:
            continue
        cell = _cell(match["cls"]).lower()
        cls = next((c for c in CLASSES if re.search(rf"\b{c}\b", cell)), None)
        found.append(
            Finding(
                id=match["id"],
                cls=cls,
                resolved=bool(RESOLVED_WORD.search(cell)),
                where=_cell(match["where"]),
                text=_cell(match["text"]),
                fix=_cell(match["fix"]),
            )
        )
    return found


def parse_findings(markdown: str) -> list[Finding]:
    """Rows of the Findings section only; a table quoted in the Notes is not findings."""
    return parse_rows(section(markdown, "Findings") or "")


def malformed_rows(markdown: str) -> list[str]:
    """Lines in the Findings section that start like a finding row but do not parse as one."""
    bad = []
    for line in (section(markdown, "Findings") or "").splitlines():
        stripped = line.strip()
        if ROW_START.match(stripped) and not ROW.match(stripped.replace("\\|", ESCAPED_PIPE)):
            bad.append(stripped)
    return bad


def parse_verdict(markdown: str) -> str | None:
    """`PASS` or `BLOCK` from inside the Verdict section only; None if absent or empty."""
    body = section(markdown, "Verdict")
    match = VERDICT_WORD.search(body) if body else None
    return match.group(1) if match else None


def has_table(markdown: str) -> bool:
    """A findings table header row, or the explicit `| (none) |` row, in the Findings section."""
    body = section(markdown, "Findings")
    return bool(body) and bool(TABLE_HEADER.search(body))


def parse_review(markdown: str) -> Parsed:
    """A usable review: a Findings table, no malformed row, and a verdict its table agrees with.

    A reviewer's BLOCK over a table with no open blocking row, or a PASS over one that has some,
    is inconsistent and is not accepted; the cycle retries as a failed attempt.
    """
    findings = parse_findings(markdown)
    word = parse_verdict(markdown)
    if section(markdown, "Findings") is None:
        return Parsed(findings, word, False, "no Findings section")
    if not has_table(markdown):
        return Parsed(findings, word, False, "no findings table")
    bad = malformed_rows(markdown)
    if bad:
        return Parsed(findings, word, False, f"{len(bad)} malformed finding row(s)")
    if word is None:
        return Parsed(findings, word, False, "no verdict")
    if word != verdict(findings):
        return Parsed(findings, word, False, f"verdict {word} contradicts the table")
    return Parsed(findings, word, True, "")


def tooling_failure(text: str) -> str | None:
    """The reason when the reviewer's output looks like a tool failure (rate limit, timeout)."""
    if events.TRANSIENT_SIGNS.search(text or ""):
        return "reviewer output names a transient tooling failure"
    return None


def unclassed(findings: list[Finding]) -> list[Finding]:
    """Findings the reviewer left without an ADR-016 class."""
    return [f for f in findings if f.cls is None]


def merge_reclassification(original: list[Finding], retried: list[Finding]) -> list[Finding]:
    """Take a class from the retry only for rows that lacked one; every original row survives."""
    classes = {f.id: f.cls for f in retried if f.cls}
    return [replace(f, cls=classes.get(f.id)) if f.cls is None else f for f in original]


def default_unclassed_to_advisory(findings: list[Finding]) -> list[Finding]:
    """After the one retry the reader allows, an unclassed finding is recorded as advisory."""
    return [replace(f, cls="advisory") if f.cls is None else f for f in findings]


def apply_rulings(findings: list[Finding], rulings: dict[str, str]) -> list[Finding]:
    """The arbiter's class wins over the reviewer's for the findings it ruled on."""
    return [replace(f, cls=rulings[f.id]) if f.id in rulings else f for f in findings]


def open_blocking(findings: list[Finding]) -> list[str]:
    """Ids of blocking findings the reviewer did not mark resolved. Transient never counts."""
    return [f.id for f in findings if f.cls == "blocking" and not f.resolved]


def verdict(findings: list[Finding]) -> str:
    """`BLOCK` while any blocking finding stands open, else `PASS`."""
    return "BLOCK" if open_blocking(findings) else "PASS"


def counts(findings: list[Finding]) -> dict[str, int]:
    """How many findings of each class, resolved rows excluded."""
    return {c: sum(1 for f in findings if f.cls == c and not f.resolved) for c in CLASSES}
