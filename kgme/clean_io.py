"""`kgme clean`, the run: the lock, the payload, the deletions, the events.

Purpose: `run_clean` orders the job per HANDOFF-0033 and its review. It refuses an unknown
target or a checkout other than this repository (F9; a seeded checkout is reached only by
the tests' direct call with it as both `base` and `home`), takes `kgme-clean.lock` without
waiting (F15), reconciles the plans an ended run left open and stops on untrusted evidence
(F14), lists, checks each entry against `jobs/clean/manifest.toml`, plans, and prints. A
refused plan records its `intent`, `refused` outcomes, and close in either mode (F5); a
clean dry run appends one `note`. Under `--yes` every file is hashed and every summary
fitted after redaction before the intent (F6), the plan is written as a payload, one
`intent` names it, files then empty directories are deleted by pathname after one final
check each (`kgme.clean_fs`), one `outcome` per path, the first refusal or failure stops
the run (ADR-016), and one `closed:` outcome ends it.
Inputs: the target name, whether to delete, the checkout, the parsed `kgme.toml`, the
authorized root (this repository's, by default).
Outputs: an exit code: 0 done, 1 refused, failed, or locked out, 2 unknown target or
checkout; lines on stdout.
Side effects: the lock; `run_deletions` unlinks files and removes empty directories;
`run_locked` writes the payload; `write_*` and `run_locked` append ledger events to the
checkout's own streams; reconciliation is `kgme/clean_reconcile.py`.
"""

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from kgme import clean_fs, clean_kept, clean_read, clean_reconcile, events, ledger, paths, policy
from kgme.clean import (
    CleanPlan,
    Entry,
    Refusal,
    deleted_summary,
    fit_summary,
    fit_text,
    keep_holding,
    plan_clean,
    plan_lines,
    plan_record,
    plan_summary,
    removed_summary,
    shown,
)

JOB = "clean"
ACTOR = "kgme.clean"
MANIFEST = Path("jobs") / "clean" / "manifest.toml"
CLOSE = "closed: "
CAP = events.MAX_SUMMARY_CHARS
BEFORE = "refused: before any deletion: "


def _measure(text: str) -> int:
    """The length the ledger checks: the longer of the raw text and its redaction, since
    `ledger.append` refuses either over the cap (review cycle 4, F6)."""
    return max(len(text), len(events.redact(text)))


@dataclass(frozen=True)
class CleanResult:
    """What `run_deletions` did."""

    deleted_files: int
    removed_dirs: int
    refused: int
    errors: int
    bytes: int


def _event(kind: str, run_id: str, key: str, summary: str, **more) -> dict:
    return events.make_event(
        source="kgme",
        actor=ACTOR,
        kind=kind,
        job=JOB,
        key=key,
        run_id=run_id,
        summary=fit_text(summary, CAP, _measure),
        **more,
    )


def write_outcome(
    dirs: ledger.Dirs,
    run_id: str,
    key: str,
    intent_id: str,
    summary: str,
    status: str,
    cls: str | None = None,
) -> str:
    """One outcome under the plan's intent, its summary fitted as the ledger will see it."""
    summary = fit_text(summary, CAP, _measure)
    event = _event(
        "outcome", run_id, key, summary, status=status, class_=cls, ref=intent_id, parent=intent_id
    )
    return ledger.append(event, dirs)


def write_refusals(
    plan: CleanPlan, root: Path, dirs: ledger.Dirs, run_id: str, key: str, intent_id: str
) -> None:
    """One `refused` outcome of class `blocking` per refusal, then the close: nothing deleted."""
    for refusal in plan.refused:
        head = f"refused: {refusal.reason}: "
        summary = fit_summary(head, shown(refusal.entry.path, root), "", CAP, _measure)
        write_outcome(dirs, run_id, key, intent_id, summary, "refused", "blocking")
    summary = f"{CLOSE}refused, nothing deleted: {len(plan.refused)} entries may not be deleted"
    write_outcome(dirs, run_id, key, intent_id, summary, "refused", "blocking")


def write_stop(
    dirs: ledger.Dirs, run_id: str, key: str, intent_id: str, number: int, left: int
) -> None:
    """The close of a run that stopped at `number` (ADR-016)."""
    summary = f"{CLOSE}stopped at #{number}; {left} planned paths left untouched"
    write_outcome(dirs, run_id, key, intent_id, summary, "error", "blocking")


def run_deletions(
    plan: CleanPlan,
    root: Path,
    dirs: ledger.Dirs,
    run_id: str,
    key: str,
    intent_id: str,
    digests: dict[Path, str],
) -> CleanResult:
    """Delete the plan: files first, then empty directories deepest first, each by
    pathname after one final check that it is still the entry the plan listed, one `outcome`
    per path carrying the hash in `digests`. The first failure or changed entry stops the run
    (ADR-016); the close says how many were left."""
    deleted = removed = errors = total = 0
    numbered = [*enumerate(plan.files, 1), *enumerate(plan.dirs, len(plan.files) + 1)]
    for number, entry in numbered:
        rel = shown(entry.path, root)
        try:
            if entry.is_dir:
                clean_fs.run_rmdir(entry.path, entry)
                summary = removed_summary(number, rel, CAP, _measure)
                removed += 1
            else:
                clean_fs.run_unlink(entry.path, entry)
                digest = digests[entry.path]
                summary = deleted_summary(number, entry.size, digest, rel, CAP, _measure)
                deleted += 1
                total += entry.size
        except clean_fs.Refused as refused:
            summary = fit_summary(f"refused #{number}: {refused}: ", rel, "", CAP, _measure)
            write_outcome(dirs, run_id, key, intent_id, summary, "refused", "blocking")
            write_stop(dirs, run_id, key, intent_id, number, len(numbered) - number)
            return CleanResult(deleted, removed, 1, 0, total)
        except OSError as error:
            head = f"error #{number}: could not delete: {error.strerror}: "
            summary = fit_summary(head, rel, "", CAP, _measure)
            write_outcome(dirs, run_id, key, intent_id, summary, "error", "blocking")
            write_stop(dirs, run_id, key, intent_id, number, len(numbered) - number)
            return CleanResult(deleted, removed, 0, 1, total)
        write_outcome(dirs, run_id, key, intent_id, summary, "ok")
    summary = f"{CLOSE}deleted {deleted} files {total} B, removed {removed} dirs"
    write_outcome(dirs, run_id, key, intent_id, summary, "ok")
    return CleanResult(deleted, removed, 0, errors, total)


def _refused_entries(errors: list[tuple[Path, str]]) -> list[Refusal]:
    """Listing errors as refusals: a directory that could not be read is a plan that cannot be
    trusted, so it deletes nothing (review F4)."""
    return [
        Refusal(Entry(path, path, True, False, 0), f"could not list: {reason}")
        for path, reason in errors
    ]


def read_prepared(plan: CleanPlan, base: Path) -> tuple[dict[Path, str], str]:
    """Every planned file hashed, matched to its entry, and every summary the run will write
    built and measured after redaction, before anything is deleted; the reason the plan
    must be refused instead, already fitted to follow `BEFORE`, or an empty string."""
    digests: dict[Path, str] = {}
    budget = CAP - len(BEFORE)
    for number, entry in enumerate(plan.files, 1):
        rel = shown(entry.path, base)
        try:
            digests[entry.path] = clean_fs.read_digest(entry.path, entry)
        except clean_fs.Refused as refused:
            return {}, fit_summary(f"#{number} {refused}: ", rel, "", budget, _measure)
        except OSError as error:
            return {}, fit_summary(f"#{number} {error.strerror}: ", rel, "", budget, _measure)
        if (
            _measure(deleted_summary(number, entry.size, digests[entry.path], rel, CAP, _measure))
            > CAP
        ):
            head = f"#{number} no summary fits the ledger: "
            return {}, fit_summary(head, rel, "", budget, _measure)
    return digests, ""


def run_clean(
    target: str, delete: bool, base: Path, settings: dict, home: Path | None = None
) -> int:
    """The run, in the order the module docstring states. `home` is this repository's root."""
    targets = settings["clean"]["targets"]
    if target not in targets:
        print(
            f"kgme clean: unknown target {target!r}; targets: {', '.join(sorted(targets))}",
            file=sys.stderr,
        )
        return 2
    home = home or paths.root()
    if not (base / ".git").exists():
        print(f"kgme clean: {base} is not a git checkout", file=sys.stderr)
        return 2
    if base != home and (base.is_relative_to(home) or home.is_relative_to(base)):
        print(f"kgme clean: {base} is inside or above this repository, {home}", file=sys.stderr)
        return 2
    lock = clean_fs.write_lock(base)
    if lock is None:
        print("kgme clean: another kgme clean is running; nothing done", file=sys.stderr)
        return 1
    try:
        return run_locked(target, delete, base, settings)
    finally:
        os.close(lock)


def run_locked(target: str, delete: bool, base: Path, settings: dict) -> int:
    """The run once it holds the lock: reconcile, list, check, plan, then delete or note."""
    targets = settings["clean"]["targets"]
    dirs = ledger.read_base_dirs(settings, base)
    run_id = events.new_ulid()
    reconciled, untrusted = clean_reconcile.write_reconciled_outcomes(base, dirs, run_id)
    if reconciled:
        print(f"kgme clean: reconciled {reconciled} open plan(s)")
    if untrusted:
        print(
            f"kgme clean: stopped; {untrusted} open plan(s) left a payload that is not "
            "their recorded evidence, closed blocking; nothing planned",
            file=sys.stderr,
        )
        return 1
    manifest = policy.read_manifest(paths.root() / MANIFEST)
    blocklist, patterns, tier1 = clean_read.read_fences(settings, base)
    entries, allowed, errors = clean_read.read_candidates(base, list(targets[target]))
    manifest_refusals: dict[Path, str] = {}
    for entry in entries:
        verdict = policy.check(
            manifest, "delete", str(entry.path), base, blocklist, patterns, tier1
        )
        if not verdict.allowed:
            manifest_refusals[entry.resolved] = verdict.reason.replace(str(base) + "/", "")
    plan = plan_clean(
        target, entries, base, allowed, paths.ledger_dir(settings, base), manifest_refusals
    )
    if errors:
        refused = tuple(
            sorted((*plan.refused, *_refused_entries(errors)), key=lambda r: r.entry.path)
        )
        plan = CleanPlan(plan.target, plan.files, plan.dirs, refused, plan.kept)
    if target == "kept":
        plan = clean_kept.read_checked(plan, base, dirs)
    print("\n".join(plan_lines(plan, base)))
    key = f"clean:{target}:{events.now_iso()[:16]}"
    mode = "delete" if delete else "dry run"
    if plan.refused:
        intent_id = ledger.append(_event("intent", run_id, key, plan_summary(plan, mode)), dirs)
        write_refusals(plan, base, dirs, run_id, key, intent_id)
        print(
            f"kgme clean: refused; {len(plan.refused)} entries may not be deleted and nothing was",
            file=sys.stderr,
        )
        return 1
    if not delete:
        ledger.append(_event("note", run_id, f"{key}:dry-run", plan_summary(plan, mode)), dirs)
        print("kgme clean: dry run; pass --yes to delete")
        return 0
    if plan.empty():
        summary = f"clean {target}: nothing to delete"
        ledger.append(_event("note", run_id, f"clean:{target}:empty", summary), dirs)
        print("kgme clean: nothing to delete")
        return 0
    payloads = paths.payloads_dir(settings, base)
    name = f"clean-{target}-{run_id}.json"
    plan = keep_holding(plan, payloads / name)
    digests, problem = read_prepared(plan, base)
    if not problem:
        record = plan_record(plan, base, key, digests)
        text = json.dumps(record, indent=2) + "\n"
        try:
            clean_fs.write_payload(base, payloads / name, text)
        except clean_fs.Refused as refused:
            budget = CAP - len(BEFORE)
            head, tail = "payload directory ", f": {refused}"
            problem = fit_summary(head, shown(payloads, base), tail, budget, _measure)
    if problem:
        intent_id = ledger.append(_event("intent", run_id, key, plan_summary(plan, mode)), dirs)
        write_outcome(dirs, run_id, key, intent_id, BEFORE + problem, "refused", "blocking")
        summary = f"{CLOSE}refused, nothing deleted: the plan could not be prepared"
        write_outcome(dirs, run_id, key, intent_id, summary, "refused", "blocking")
        print(f"kgme clean: refused: {problem}", file=sys.stderr)
        return 1
    payload_ref = (payloads / name).relative_to(base).as_posix()
    intent_id = ledger.append(
        _event(
            "intent",
            run_id,
            key,
            plan_summary(plan, mode),
            payload_ref=payload_ref,
            payload_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        ),
        dirs,
    )
    result = run_deletions(plan, base, dirs, run_id, key, intent_id, digests)
    print(
        f"kgme clean {target}: deleted {result.deleted_files} files ({result.bytes} bytes), "
        f"removed {result.removed_dirs} directories, {result.errors} errors, "
        f"{result.refused} refused"
    )
    return 1 if result.errors or result.refused else 0
