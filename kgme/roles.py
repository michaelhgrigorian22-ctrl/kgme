"""The role registry, pure half: a role file and its rubric to classed findings (HANDOFF-0071).

Purpose: ADR-025 §2-4. A role is `roles/<department>/<role>.toml`; it names a session level
and optionally a profile, may narrow them and never widen them, never reaches Tier 1, and
escalates to `michou` in at most three hops. Its rubric, `roles/<department>/rubrics/<role>.md`,
has three to six dimensions under `## Dimensions`, one line each,
``- `name` (gate): what it measures.``, at least one a gate, with the standing `intent` and
`context` gates (§4). Every rule here is `blocking`; a field the registry does not know is
`advisory`. A field that should be a string and is not is a finding, and is then judged
absent, so one malformed role never stops the pass (AUDIT-0173 F5). `cheap` is not a role
level in v1 (AUDIT-0173 F3, ruled narrower): the cheap lane carries no role context yet.
What a level allows is derived as the rulings at adoption say: `loose` from its template's
`permissions.allow` (minus `deny`), `work` from the `claude-builder` profile or the role's
own, `tight` from `kgme.toml [hooks] read_only_tools`; that is the effects half's read
(`kgme.roles_io`), given here as `Level`s; the launch's half of the same contract
(AUDIT-0173 F2) is in `kgme.roles_run`.
Inputs: parsed roles, rubric texts, the skills and paths that exist, the levels, the profiles.
Outputs: `lint.Finding` records; tool names and why a tool is not one (`tool_problem`, which
the launch asks too, AUDIT-0174 F2); the chain of a role.
Side effects: none.
"""

import re
from dataclasses import dataclass

from kgme.lint import Finding

FIELDS = (
    "id",
    "department",
    "purpose",
    "kind",
    "skill",
    "model",
    "level",
    "slice",
    "tools",
    "tier_max",
    "escalates_to",
    "rubric",
)
OPTIONAL = ("profile",)
STRINGS = (
    "id",
    "department",
    "purpose",
    "kind",
    "skill",
    "model",
    "level",
    "profile",
    "escalates_to",
    "rubric",
)
KINDS = ("manager", "worker")
MODELS = ("cheap", "standard", "strong", "inherit")
# The tier each level can reach (rulings at adoption).
CEILINGS = {"tight": 2, "work": 2, "loose": 2}
# Levels a role may not name, and why (AUDIT-0173 F3, ruled narrower).
NOT_ROLE_LEVELS = {
    "cheap": "level `cheap` is not a role level in v1: the cheap lane carries no role "
    "context yet (AUDIT-0173 F3)",
}
# What a profile may declare that the launch cannot render at a level (AUDIT-0173 F2).
FENCES = ("read_paths", "write_paths", "network_destinations")
MICHOU = "michou"
MAX_HOPS = 3
RESERVED = ("templates",)  # `roles/templates/` holds the templates, never a department
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
TOOL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)")
BARE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")  # one whole tool name (AUDIT-0174 F2)
DIMENSION = re.compile(r"^- `([a-z][a-z0-9-]*)`( \(gate\))?: \S")
STANDING_GATES = ("intent", "context")


@dataclass(frozen=True)
class Level:
    """What a level allows: its tool names and the tier it reaches (its ceiling)."""

    tools: frozenset[str]
    ceiling: int


@dataclass(frozen=True)
class Profile:
    """A profile under `control/policy/profiles/`: its tool names, if it lists any, and its
    `max_tier`."""

    tools: frozenset[str] | None
    max_tier: int | None
    fences: tuple[str, ...] = ()  # the FENCES it declares


def tool_name(rule: str) -> str:
    """Pure: `Edit(/a/**)` and `Bash(make check)` → `Edit` and `Bash`."""
    match = TOOL.match(rule.strip())
    return match.group(1) if match else rule.strip()


def tool_problem(tool: object, grant: frozenset[str], level_name: str) -> str | None:
    """Pure: why `tool` is not one a role at `level_name` may list, or None. It must be one
    complete bare tool name, never a scoped rule, a list or padded, and one the level grants.
    Lint and the launch both ask this, so they never disagree (AUDIT-0174 F2)."""
    if not isinstance(tool, str) or not BARE.fullmatch(tool):
        return (f"{tool!r} is not one bare tool name (a scoped rule, a list or padding); "
                "the launch narrows by bare names (--tools), one per entry")  # fmt: skip
    if tool not in grant:
        return f"`{tool}` is not allowed at {level_name}; it allows {', '.join(sorted(grant))}"
    return None


def allowed_from_template(template: dict) -> frozenset[str]:
    """Pure: the tool names a session template's `permissions.allow` grants, minus `deny`."""
    permissions = template.get("permissions") or {}
    allow = {tool_name(r) for r in permissions.get("allow") or []}
    deny = {tool_name(r) for r in permissions.get("deny") or [] if "(" not in r}
    return frozenset(allow - deny)


def allowed(level: Level, profile: Profile | None, level_name: str) -> frozenset[str]:
    """Pure: what a role at `level` with `profile` may list. At `work` a profile's tools
    stand in for `claude-builder`'s; at any other level a profile only narrows."""
    if profile is None or profile.tools is None:
        return level.tools
    return profile.tools if level_name == "work" else level.tools & profile.tools


def ceiling(level: Level, profile: Profile | None) -> int:
    """Pure: the most sensitive tier the role can reach; a profile can only raise the number."""
    if profile is None or profile.max_tier is None:
        return level.ceiling
    return max(level.ceiling, profile.max_tier)


def chain(role_id: str, roles: dict[str, dict]) -> tuple[list[str], str | None]:
    """Pure: the escalation chain from `role_id`, ending at `michou` if it gets there, and
    why it fails if it does not (unresolved, a cycle, or too many hops)."""
    seen = [role_id]
    current = role_id
    while True:
        target = str(roles[current].get("escalates_to", ""))
        if target == MICHOU:
            seen.append(MICHOU)
            hops = len(seen) - 1
            if hops > MAX_HOPS:
                return seen, f"reaches michou in {hops} hops, more than {MAX_HOPS}"
            return seen, None
        if target not in roles:
            return seen, f"escalates_to `{target}` does not resolve to a role or michou"
        if target in seen:
            return seen + [target], "escalation is a cycle"
        seen.append(target)
        current = target


def rubric_findings(rel: str, text: str) -> list[str]:
    """Pure: what is wrong with a rubric's shape; empty when it is sound."""
    section = re.search(r"^## Dimensions[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    lines = section.group(1).splitlines() if section else []
    found = [DIMENSION.match(line) for line in lines]
    dimensions = {m.group(1): bool(m.group(2)) for m in found if m}
    problems = []
    if not 3 <= len(dimensions) <= 6:
        problems.append(f"{rel} has {len(dimensions)} dimensions; a rubric has three to six")
    if not any(dimensions.values()):
        problems.append(f"{rel} marks no dimension `(gate)`")
    for gate in STANDING_GATES:
        if not dimensions.get(gate):
            problems.append(f"{rel} lacks the standing `{gate}` gate")
    return problems


def check_role(
    rel: str,
    data: dict,
    roles: dict[str, dict],
    exists: frozenset[str],
    levels: dict[str, Level],
    profiles: dict[str, Profile],
    rubric_text: str | None,
) -> list[Finding]:
    """Pure: every finding for one role at `rel`, given every role by id, the paths that
    exist, the levels, the profiles, and its rubric's text (None if unreadable)."""
    out: list[Finding] = []

    def block(message: str) -> None:
        out.append(Finding(rel, "role", "blocking", message))

    for field in FIELDS:
        if field not in data:
            block(f"missing `{field}`")
    for field in STRINGS:
        if field in data and not isinstance(data[field], str):
            block(f"`{field}` is a string, got {type(data[field]).__name__}")
    data = {k: v for k, v in data.items() if k not in STRINGS or isinstance(v, str)}
    unknown = sorted(set(data) - set(FIELDS) - set(OPTIONAL))
    if unknown:
        message = "fields not in the registry: " + ", ".join(unknown)
        out.append(Finding(rel, "role", "advisory", message))
    parts = rel.split("/")
    department, stem = (parts[1], parts[-1].removesuffix(".toml")) if len(parts) == 3 else ("", "")
    if not department:
        block("a role is roles/<department>/<role>.toml")
    if "id" in data and data["id"] != f"{department}.{stem}":
        block(f"id `{data['id']}` is not `{department}.{stem}`, its path")
    if "department" in data and data["department"] != department:
        block(f"department `{data['department']}` is not its folder `{department}`")
    for field, values in (("kind", KINDS), ("model", MODELS)):
        if field in data and data[field] not in values:
            block(f"{field} `{data[field]}` is not one of {', '.join(values)}")
    if "skill" in data and f"skills/{data['skill']}/SKILL.md" not in exists:
        block(f"skill `{data['skill']}` has no skills/{data['skill']}/SKILL.md")
    if "rubric" in data:
        if str(data["rubric"]) not in exists or rubric_text is None:
            block(f"rubric `{data['rubric']}` does not exist")
        else:
            for problem in rubric_findings(str(data["rubric"]), rubric_text):
                block(problem)
    for field in ("slice", "tools"):
        if field in data and not (
            isinstance(data[field], list) and all(isinstance(v, str) for v in data[field])
        ):
            block(f"`{field}` is a list of strings")
    level_name = data.get("level")
    level = levels.get(level_name) if isinstance(level_name, str) else None
    if level_name in NOT_ROLE_LEVELS:
        block(NOT_ROLE_LEVELS[str(level_name)])
    elif "level" in data and level is None:
        block(f"level `{level_name}` is not one of {', '.join(sorted(levels))}")
    profile = None
    if "profile" in data:
        profile = profiles.get(str(data["profile"]))
        if profile is None:
            block(f"profile `{data['profile']}` is not under control/policy/profiles/")
    if level is not None:
        out.extend(_power(rel, data, level, profile, str(level_name)))
    if data.get("model") == "cheap":
        block("model `cheap` is the cheap lane's, not a role's in v1 (AUDIT-0173 F3)")
    if data.get("id") in roles and "escalates_to" in data:
        _, why = chain(str(data["id"]), roles)
        if why:
            block(why)
    return out


def _power(rel: str, data: dict, level: Level, profile: Profile | None, name: str) -> list[Finding]:
    """Pure: the role grants nothing its level does not: tools within it, the tier within
    its ceiling, and never Tier 1 (ADR-025 §3, ADR-021)."""
    out: list[Finding] = []
    grant = allowed(level, profile, name)
    tools = data.get("tools") if isinstance(data.get("tools"), list) else []
    for tool in tools:
        problem = tool_problem(tool, grant, name)
        if problem:
            out.append(Finding(rel, "role", "blocking", problem))
    tier = data.get("tier_max")
    if "tier_max" not in data:
        return out
    if type(tier) is not int or tier not in (1, 2, 3):
        out.append(Finding(rel, "role", "blocking", f"tier_max must be 2 or 3, got {tier!r}"))
    elif tier == 1:
        message = "tier_max = 1: Tier 1 is never a role's to claim (ADR-021, ADR-025 §3)"
        out.append(Finding(rel, "role", "blocking", message))
    elif tier < ceiling(level, profile):
        top = ceiling(level, profile)
        message = (
            f"tier_max = {tier} is more sensitive than {name} reaches: "
            f"the ceiling of {name} is {top}"
        )
        out.append(Finding(rel, "role", "blocking", message))
    return out


def check_departments(roles: dict[str, tuple[str, dict]]) -> list[Finding]:
    """Pure: one manager per department (ADR-025 §1); `roles` maps id to (path, data)."""
    managers: dict[str, list[str]] = {}
    for rel, data in roles.values():
        if data.get("kind") == "manager":
            managers.setdefault(str(data.get("department")), []).append(rel)
    return [
        Finding(
            rel,
            "role",
            "blocking",
            f"department `{dept}` has {len(rels)} managers; one manager each",
        )
        for dept, rels in sorted(managers.items())
        if len(rels) > 1
        for rel in rels
    ]
