"""`kgme clean kept`: the copies `kgme capture` keeps go only while they are what it kept.

Purpose: the one way a kept copy is removed (HANDOFF-0050; the rulings on review cycle 6 F13
and F15, option A, with Cowork's refinement: capture deletes nothing, ever). A copy beside a
file `kgme capture` added a line to is named `.<name>.capture-<intent id>`, and that
capture's `kept` note in the ledger records the sha256 prefixes of the file as read and as
intended. `read_checked` adds a refusal for every planned copy with no such note, or whose
bytes hash to neither: it holds a save the file lacks, and it is named so Michou can merge
it. A refusal stops the whole plan, as every `kgme clean` refusal does; the deletion itself
is `kgme.clean_io`'s, after its final check of each entry.
Inputs: the plan, the checkout, the ledger directories.
Outputs: the plan with those copies moved from its files to its refusals.
Side effects: reads the ledger and the planned copies; nothing is written.
"""

from pathlib import Path

from kgme import capture_fs, capture_record, capture_recover, clean_fs, ledger
from kgme.clean import CleanPlan, Refusal


def read_checked(plan: CleanPlan, base: Path, dirs: ledger.Dirs) -> CleanPlan:
    """`plan` with every copy that is not still what its capture kept refused."""
    files, refused = [], list(plan.refused)
    for entry in plan.files:
        reason = read_reason(entry, dirs)
        if reason:
            refused.append(Refusal(entry, reason))
        else:
            files.append(entry)
    return CleanPlan(
        plan.target,
        tuple(files),
        plan.dirs,
        tuple(sorted(refused, key=lambda r: r.entry.path)),
        plan.kept,
    )


def read_reason(entry, dirs: ledger.Dirs) -> str:
    """Why this copy may not go, or an empty string."""
    match = capture_fs.KEPT_NAME.match(entry.path.name)
    recorded = capture_record.read_kept_hashes(dirs, match["id"]) if match else None
    if recorded is None:
        return "no kgme capture recorded this copy; check it, then delete it by hand"
    try:
        digest = clean_fs.read_digest(entry.path, entry)
    except (clean_fs.Refused, OSError) as error:
        return f"could not be checked: {error}"
    if capture_recover.holds_save(digest, recorded):
        return "not what its capture kept; it holds a save: merge it by hand"
    return ""
