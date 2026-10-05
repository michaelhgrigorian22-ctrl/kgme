"""Worker manifests: what a worker may read, write, call, and reach (ADR-013 §1, HANDOFF-0032).

Purpose: one declaration per worker, `manifest.toml` beside the job or under
`tools/policy/profiles/`, and one pure check a Python job calls before every effect. A manifest
narrows and never widens: the guard's blocklist and the Tier 1 roots from `kgme.toml` are
refused whatever a manifest declares, and no manifest in this repository declares Tier 1.
Inputs: manifest text; an operation (`read`, `write`, `delete`, `network`, `tool`) and its
target; the repository root; the blocklist roots, name patterns, and Tier 1 roots.
Outputs: a `Manifest`, and a `Verdict` naming the layer (`manifest`) and the reason.
Side effects: `read_manifest` reads one file. Nothing else touches the disk or the network.

Paths in a manifest are repository-relative unless absolute or `~`-prefixed; an entry with a
`*` is a glob over the repository-relative path (`**/__pycache__/**`), anything else a root
that covers itself and everything under it. Targets are resolved with symlinks followed before
the roots apply, so a link under an allowed root that points elsewhere is refused.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from kgme.hooks import guard

KINDS = ("python-job", "agent-profile", "app")
OPERATIONS = ("read", "write", "delete", "network", "tool")
FIELDS = ("name", "kind", "max_tier", "read_paths", "write_paths", "tools", "network_destinations")
LISTS = ("read_paths", "write_paths", "tools", "network_destinations")
LAYER = "manifest"
DEFAULT_PORTS = {"http": 80, "https": 443}


@dataclass(frozen=True)
class Manifest:
    """One worker's declaration. `max_tier` is 2 or 3: Tier 1 is never declared here (ADR-002)."""

    name: str
    kind: str
    max_tier: int
    read_paths: tuple[str, ...]
    write_paths: tuple[str, ...]
    tools: tuple[str, ...]
    network_destinations: tuple[str, ...]


@dataclass(frozen=True)
class Verdict:
    """`allowed`, the layer that decided (`manifest`), and the reason when refused."""

    allowed: bool
    layer: str
    reason: str


def parse_manifest(text: str) -> Manifest:
    """A `Manifest` from TOML text. Every field required, none unknown; raises ValueError."""
    data = tomllib.loads(text)
    missing = [field for field in FIELDS if field not in data]
    unknown = sorted(set(data) - set(FIELDS))
    if missing or unknown:
        raise ValueError(f"manifest fields: missing {missing}, unknown {unknown}")
    if not isinstance(data["name"], str) or not data["name"]:
        raise ValueError("manifest name must be a non-empty string")
    if data["kind"] not in KINDS:
        raise ValueError(f"manifest kind must be one of {KINDS}, got {data['kind']!r}")
    if type(data["max_tier"]) is not int or data["max_tier"] not in (2, 3):
        raise ValueError("max_tier must be 2 or 3: Tier 1 is never declared in this repository")
    lists: dict[str, tuple[str, ...]] = {}
    for field in LISTS:
        value = data[field]
        if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
            raise ValueError(f"{field} must be a list of non-empty strings")
        lists[field] = tuple(value)
    return Manifest(data["name"], data["kind"], data["max_tier"], **lists)


def read_manifest(path: Path) -> Manifest:
    """The one effect: read a manifest file."""
    return parse_manifest(path.read_text(encoding="utf-8"))


def destination(url: str) -> str:
    """`host:port` of a URL or bare `host[:port]`, the form `network_destinations` declares."""
    parts = urlsplit(url if "//" in url else "//" + url)
    port = parts.port or DEFAULT_PORTS.get(parts.scheme or "")
    host = parts.hostname or ""
    return f"{host}:{port}" if port else host


def resolve_target(target: str, base: Path) -> Path:
    """The target as an absolute path, symlinks followed."""
    path = guard.expand_home(target)
    return (path if path.is_absolute() else base / path).resolve()


def path_allowed(resolved: Path, entries: tuple[str, ...], base: Path) -> bool:
    """True if `resolved` is under one of the declared roots or matches a declared glob."""
    for entry in entries:
        if "*" in entry:
            try:
                rel = PurePosixPath(resolved.relative_to(base).as_posix())
            except ValueError:
                continue
            # `a/**/b/**` names b and everything under it; full_match needs the two spelled out
            if rel.full_match(entry) or (entry.endswith("/**") and rel.full_match(entry[:-3])):
                return True
        elif guard.is_under_any(resolved, [resolve_target(entry, base)]):
            return True
    return False


def check(
    manifest: Manifest,
    operation: str,
    target: str,
    base: Path,
    blocklist: list[Path],
    name_patterns: list[str],
    tier1: list[Path],
) -> Verdict:
    """May `manifest`'s worker perform `operation` on `target`? Pure.

    `tool` and `network` are matched against the declared names and `host:port` strings.
    A path is refused first if the blocklist or a Tier 1 root covers it, then unless a
    declared root or glob of the operation's kind (`read_paths`, or `write_paths` for `write`
    and `delete`) covers its resolved form.
    """
    who = manifest.name
    if operation not in OPERATIONS:
        return Verdict(False, LAYER, f"refused: unknown operation {operation!r}")
    if operation == "tool":
        if target in manifest.tools:
            return Verdict(True, LAYER, "")
        return Verdict(False, LAYER, f"refused: tool {target} is not declared by {who}")
    if operation == "network":
        where = destination(target)
        if where in manifest.network_destinations:
            return Verdict(True, LAYER, "")
        return Verdict(False, LAYER, f"refused: destination {where} is not declared by {who}")
    resolved = resolve_target(target, base)
    if guard.is_blocklisted(resolved, [*blocklist, *tier1], name_patterns):
        return Verdict(
            False, LAYER, f"refused: {resolved} is blocklisted or Tier 1; no manifest grants it"
        )
    kind = "read" if operation == "read" else "write"
    entries = manifest.read_paths if operation == "read" else manifest.write_paths
    if not path_allowed(resolved, entries, base):
        return Verdict(
            False, LAYER, f"refused: {operation} of {resolved} is outside {who}'s {kind} paths"
        )
    return Verdict(True, LAYER, "")
