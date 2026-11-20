"""The role registry, effects: read roles and levels, `kgme agent new|list|show` (HANDOFF-0071).

Purpose: the reads `kgme.roles` judges, and three of the four commands; `run` is in
`kgme.roles_run`. `read_findings` is the role
pass `kgme lint` calls: the index's roles and rubrics by default, read as the index's blobs,
so an unstaged repair or a working-tree deletion never changes the verdict on what is staged;
the working tree's under `--all` (AUDIT-0173 F6). Levels and profiles are read from the
working tree, as `kgme session` reads them at launch.
`run_new` writes a lint-clean role, rubric and stub skill from `roles/templates/` and says
what is still missing.
Inputs: the checkout, the parsed `kgme.toml`, a role id or a new role's names.
Outputs: findings; printed lines; exit codes (0 ok, 1 lint findings after `new`, 2 refused).
Side effects: `new` creates files under `roles/` and `skills/`, never over an existing one.
"""

import json
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

from kgme import roles
from kgme.lint import Finding

ROLES = "roles"
TEMPLATES = Path(ROLES) / "templates"
SESSIONS = Path("control") / "policy" / "sessions"
PROFILES = Path("control") / "policy" / "profiles"
WORK_PROFILE = "claude-builder"
# A role's model tier as the `kgme.toml [models]` key it resolves to. `[models]` names one
# Claude model today, so `strong`, `standard` and `inherit` resolve alike until it names more.
MODEL_KEYS = {"strong": "builder", "standard": "builder", "inherit": "builder"}


def read_blob(base: Path, rel: str) -> str | None:
    """Effect: the index's copy of `rel`, or None when the index holds no such file."""
    shown = subprocess.run(
        ["git", "cat-file", "blob", f":{rel}"], cwd=base, capture_output=True, check=False
    )
    return shown.stdout.decode("utf-8", "replace") if shown.returncode == 0 else None


def read_tree_file(base: Path, rel: str) -> str | None:
    """Effect: the working tree's copy of `rel`, or None when it is not a file."""
    path = base / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def make_reader(base: Path, index: bool) -> Callable[[str], str | None]:
    """Pure: the read the pass makes of one path: the index's blob, or the working tree's."""
    return (lambda rel: read_blob(base, rel)) if index else (lambda rel: read_tree_file(base, rel))


def read_role_texts(base: Path, index: bool) -> dict[str, str]:
    """Effect: `{rel: text}` of every `roles/<department>/<role>.toml` but the templates; the
    index's paths when `index`, else the working tree's."""
    if index:
        listed = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--", ROLES],
            cwd=base, capture_output=True, check=True,
        )  # fmt: skip
        names = [n for n in listed.stdout.decode("utf-8", "surrogateescape").split("\0") if n]
    else:
        root = base / ROLES
        names = (
            [p.relative_to(base).as_posix() for p in root.rglob("*.toml")] if root.is_dir() else []
        )
    read = make_reader(base, index)
    texts = {}
    for rel in sorted(names):
        parts = rel.split("/")
        if rel.endswith(".toml") and len(parts) == 3 and parts[1] not in roles.RESERVED:
            text = read(rel)
            if text is not None:
                texts[rel] = text
    return texts


def read_exists(base: Path, index: bool) -> frozenset[str]:
    """Effect: the paths a role may name that exist: the index's, or the working tree's
    `roles/` and `skills/`."""
    if index:
        from kgme import vault

        return vault.read_existing_paths(base)
    found = [
        p.relative_to(base).as_posix()
        for top in (ROLES, "skills")
        if (base / top).is_dir()
        for p in (base / top).rglob("*")
        if p.is_file()
    ]
    return frozenset(found)


def read_profiles(base: Path) -> dict[str, roles.Profile]:
    """Effect: every profile under `control/policy/profiles/` by file stem."""
    found = {}
    for path in sorted((base / PROFILES).glob("*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        tools = data.get("tools")
        tier = data.get("max_tier")
        found[path.stem] = roles.Profile(
            frozenset(tools) if isinstance(tools, list) else None,
            tier if type(tier) is int else None,
            tuple(field for field in roles.FENCES if data.get(field)),
        )
    return found


def read_levels(base: Path, settings: dict, profiles: dict) -> dict[str, roles.Level]:
    """Effect: each level whose template exists under `control/policy/sessions/`, with what it
    allows, derived as the rulings at adoption say."""
    found = {}
    for name, top in roles.CEILINGS.items():
        path = base / SESSIONS / f"{name}.json"
        if not path.is_file():
            continue
        if name == "tight":
            tools = frozenset(settings.get("hooks", {}).get("read_only_tools", []))
        elif name == "work":
            builder = profiles.get(WORK_PROFILE)
            tools = builder.tools if builder and builder.tools else frozenset()
        else:
            tools = roles.allowed_from_template(json.loads(path.read_text(encoding="utf-8")))
        found[name] = roles.Level(tools, top)
    return found


def parse_roles(texts: dict[str, str]) -> tuple[dict[str, tuple[str, dict]], list[Finding]]:
    """Pure over the texts: `{id: (rel, data)}` and a blocking finding per unparsable file."""
    parsed: dict[str, tuple[str, dict]] = {}
    bad: list[Finding] = []
    for rel, text in texts.items():
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            bad.append(Finding(rel, "role", "blocking", f"not TOML: {error}"))
            continue
        identifier = data["id"] if isinstance(data.get("id"), str) else rel
        if identifier in parsed:
            message = f"id `{identifier}` already used by {parsed[identifier][0]}"
            bad.append(Finding(rel, "role", "blocking", message))
            continue
        parsed[identifier] = (rel, data)
    return parsed, bad


def read_findings(base: Path, settings: dict, index: bool = False) -> list[Finding]:
    """Effect: the role pass of `kgme lint`, every role's findings."""
    parsed, found = parse_roles(read_role_texts(base, index))
    exists = read_exists(base, index)
    profiles = read_profiles(base)
    levels = read_levels(base, settings, profiles)
    by_id = {identifier: data for identifier, (_, data) in parsed.items()}
    read = make_reader(base, index)
    for rel, data in parsed.values():
        rubric = data.get("rubric")
        text = read(rubric) if isinstance(rubric, str) and rubric in exists else None
        found += roles.check_role(rel, data, by_id, exists, levels, profiles, text)
    return found + roles.check_departments(parsed)


def read_role_files(base: Path) -> dict[str, tuple[str, dict]]:
    """Effect: the working tree's roles by id, each with the path it was read from."""
    return parse_roles(read_role_texts(base, index=False))[0]


def read_roles(base: Path) -> dict[str, dict]:
    """Effect: the working tree's roles by id."""
    return {identifier: data for identifier, (_, data) in read_role_files(base).items()}


def run_list(base: Path) -> int:
    """`kgme agent list`: the roles by department, a count each, one line per role."""
    by_department: dict[str, list[dict]] = {}
    for data in read_roles(base).values():
        by_department.setdefault(str(data.get("department")), []).append(data)
    for department in sorted(by_department):
        members = sorted(
            by_department[department], key=lambda d: (d.get("kind") != "manager", d["id"])
        )
        print(f"{department.capitalize()} ({len(members)})")
        for d in members:
            print(f"  {d['id']:<24} {d.get('kind', '?'):<8} {d.get('level', '?'):<6} "
                  f"{d.get('model', '?'):<8} {d.get('purpose', '')}")  # fmt: skip
    return 0


def run_show(base: Path, settings: dict, role_id: str) -> int:
    """`kgme agent show <id>`: the file, what its level allows, its model and its chain."""
    files = read_role_files(base)
    if role_id not in files:
        print(f"kgme agent: no role `{role_id}`", file=sys.stderr)
        return 2
    rel, data = files[role_id]
    every = {identifier: d for identifier, (_, d) in files.items()}
    print((base / rel).read_text(encoding="utf-8"), end="")
    profiles = read_profiles(base)
    level = read_levels(base, settings, profiles).get(str(data.get("level")))
    if level:
        grant = roles.allowed(level, profiles.get(str(data.get("profile"))), str(data["level"]))
        print(f"# allowed at {data['level']}: {', '.join(sorted(grant))}")
    key = MODEL_KEYS.get(str(data.get("model")))
    print(f"# model: {settings.get('models', {}).get(key) if key else '?'}")
    print("# chain: " + " -> ".join(roles.chain(role_id, every)[0]))
    return 0


def run_new(base: Path, settings: dict, department: str, role: str) -> int:
    """`kgme agent new <department> <role>`: a role, its rubric and a stub skill from the
    templates, never over an existing file; then the role pass on them."""
    for word in (department, role):
        if not roles.NAME.match(word) or word in roles.RESERVED:
            print(f"kgme agent: `{word}` is not a kebab-case name or is reserved", file=sys.stderr)
            return 2
    identifier, skill = f"{department}.{role}", f"kgme-{department}-{role}"
    manager = next(
        (d["id"] for d in read_roles(base).values()
         if d.get("department") == department and d.get("kind") == "manager"),
        roles.MICHOU,
    )  # fmt: skip
    fill = {"{department}": department, "{role}": role, "{id}": identifier,
            "{skill}": skill, "{escalates_to}": manager}  # fmt: skip
    targets = {
        f"{ROLES}/{department}/{role}.toml": "role.toml",
        f"{ROLES}/{department}/rubrics/{role}.md": "rubric.md",
    }
    if not (base / "skills" / skill).exists():
        targets |= {f"skills/{skill}/SKILL.md": "skill.md", f"skills/{skill}/lessons.md": None}
    if (base / targets_role(department, role)).exists():
        print(f"kgme agent: {identifier} exists; nothing written", file=sys.stderr)
        return 2
    for rel, template in targets.items():
        text = "" if template is None else (base / TEMPLATES / template).read_text(encoding="utf-8")
        for key, value in fill.items():
            text = text.replace(key, value)
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        with open(base / rel, "x", encoding="utf-8") as handle:
            handle.write(text)
        print(f"wrote {rel}")
    role_file = targets_role(department, role)
    print(f"still missing: the skill body in skills/{skill}/SKILL.md, the purpose in "
          f"{role_file}, and the department's own rubric dimensions")  # fmt: skip
    mine = [f for f in read_findings(base, settings) if f.path in targets and f.cls == "blocking"]
    for finding in mine:
        print(finding.line())
    return 1 if mine else 0


def targets_role(department: str, role: str) -> str:
    """Pure: the path of role `role` of `department`."""
    return f"{ROLES}/{department}/{role}.toml"
