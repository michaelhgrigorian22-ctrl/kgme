"""Every path KGME touches, derived from one root and the parsed configuration.

Purpose: the single place paths come from (ADR-015). No other module joins path strings
from configuration; it asks this module. The repository root is the grandparent of this
file, never an environment variable: ADR-015 allows no environment-variable magic except
secret handles. The shell's `KGME_HOME` is used only outside Python, by the `kgme` shell
function, to tell `uv run --project` which checkout to run; inside Python the checkout
that is running is the root.
Inputs: this file's location; a `settings` dict from `kgme.config.read_config()`, passed
by the caller so this module stays pure.
Outputs: absolute `pathlib.Path` values.
Side effects: none. Nothing here opens, reads, or writes a file.
"""

from pathlib import Path


def root() -> Path:
    """The repository root: the directory that holds `kgme.toml` and this package."""
    return Path(__file__).resolve().parent.parent


def resolve(relative_or_absolute: str, base: Path | None = None) -> Path:
    """Turn a `kgme.toml` path value into an absolute path under `base` (default: the root)."""
    candidate = Path(relative_or_absolute).expanduser()
    if candidate.is_absolute():
        return candidate
    return (base or root()) / candidate


def _path_setting(settings: dict, key: str, base: Path | None) -> Path:
    return resolve(settings["paths"][key], base)


def vault(settings: dict, base: Path | None = None) -> Path:
    """`memory/`, the Obsidian vault."""
    return _path_setting(settings, "vault", base)


def ledger_dir(settings: dict, base: Path | None = None) -> Path:
    """`logs/ledger/`, git-tracked, never deleted (ADR-012)."""
    return _path_setting(settings, "ledger_dir", base)


def trace_dir(settings: dict, base: Path | None = None) -> Path:
    """`logs/trace/`, untracked read-only tool events (ADR-019 §2)."""
    return _path_setting(settings, "trace_dir", base)


def ledger_test_dir(settings: dict, base: Path | None = None) -> Path:
    """Where tests write ledger events so the real stream stays clean."""
    return _path_setting(settings, "ledger_test_dir", base)


def trace_test_dir(settings: dict, base: Path | None = None) -> Path:
    """Where tests write trace events."""
    return _path_setting(settings, "trace_test_dir", base)


def scratch_dir(settings: dict, base: Path | None = None) -> Path:
    """`logs/scratch/`, disposable, gitignored."""
    return _path_setting(settings, "scratch_dir", base)


def scratch_test_dir(settings: dict, base: Path | None = None) -> Path:
    """`logs/scratch-test/`, where hook tests put payloads and error lines."""
    return _path_setting(settings, "scratch_test_dir", base)


def payloads_dir(settings: dict, base: Path | None = None) -> Path:
    """`logs/scratch/payloads/`, raw tool inputs referenced by hash from ledger lines."""
    return _path_setting(settings, "payloads_dir", base)


def audit_dir(settings: dict, base: Path | None = None) -> Path:
    """`docs/audit/`, where reports and review audits live."""
    return _path_setting(settings, "audit_dir", base)


def handoff_dir(settings: dict, base: Path | None = None) -> Path:
    """`docs/handoff/`, the adopted handoffs."""
    return _path_setting(settings, "handoff_dir", base)


def review_prompt(settings: dict, base: Path | None = None) -> Path:
    """`tools/review/prompt.md`, the fixed reviewer prompt template."""
    return _path_setting(settings, "review_prompt", base)


def tier1_paths(settings: dict, base: Path | None = None) -> list[Path]:
    """Paths that no agent may read. Only the paths; never what is behind them."""
    return [resolve(p, base) for p in settings["paths"]["tier1_paths"]]
