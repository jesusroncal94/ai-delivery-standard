import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable

import yaml

from .project import Project

AGENTS_MAX_LINES = 200
INSTRUCTION_CHAIN_MAX_BYTES = 32 * 1024
CLAUDE_IMPORT_MAX_LINES = 20
STATE_FILE_MAX_TOKENS = 5_000
REFERENCE_DOC_MAX_TOKENS = 25_000
SKILL_MAX_LINES = 500
SKILL_DESCRIPTION_MAX_CHARS = 1_024
SKILL_SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MCP_MAX_SERVERS = 5
METRICS_GRACE_DAYS = 45

REQUIRED_SECTIONS = ("Commands", "Definition of done", "Prohibitions", "Portfolio conventions", "Where things live")
CORE_SKILLS = ("spec", "build-slice", "review", "handoff", "release")
INSTRUCTION_CHAIN = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md")
DENY_PATTERNS = ("git push", "gh pr merge", ".env")
MODULE_FILES = {
    "multi-user": "docs/security/authorization-matrix.md",
    "eu-personal-data": "docs/privacy/record-of-processing.md",
    "ai-extraction": "evals/schema.md",
}


@dataclass(frozen=True)
class Rule:
    id: str
    level: int
    title: str
    check: Callable[[Project], list[str]]
    applies: Callable[[Project], bool] = lambda project: True


RULES: list[Rule] = []


def rule(id: str, level: int, title: str, applies: Callable[[Project], bool] = lambda project: True):
    def register(check: Callable[[Project], list[str]]):
        RULES.append(Rule(id, level, title, check, applies))
        return check
    return register


def requires(project: Project, *paths: str) -> list[str]:
    return [f"missing {path}" for path in paths if not project.exists(path)]


def workflows(project: Project) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in project.files(".github/workflows/*.y*ml"))


def claude_settings(project: Project) -> dict:
    return project.read_json(".claude/settings.json") or {}


def normalized(path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def skill_frontmatter(text: str) -> dict | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None


def uses_claude(project: Project) -> bool:
    return project.uses_claude


def has_remote_ci(project: Project) -> bool:
    return not project.local_only


@rule("L1-GIT", 1, "The project is a Git repository")
def git_repository(project: Project) -> list[str]:
    return [] if project.is_git_repo() else ["not a Git repository"]


@rule("L1-REMOTE", 1, "The repository has a remote unless it is local-only", has_remote_ci)
def remote(project: Project) -> list[str]:
    return [] if project.remotes() else ["no remote configured (set local_only: true if that is deliberate)"]


@rule("L1-README", 1, "README.md states what the project is")
def readme(project: Project) -> list[str]:
    return [] if project.read("README.md").strip() else ["missing or empty README.md"]


@rule("L1-ANSWERS", 1, "The standard's answers file records profile and level")
def answers(project: Project) -> list[str]:
    return [] if project.has_answers else [".copier-answers.yml is missing; adopt the standard with Copier"]


@rule("C1-AGENTS", 1, f"AGENTS.md exists and has at most {AGENTS_MAX_LINES} lines")
def agents_file(project: Project) -> list[str]:
    if not project.exists("AGENTS.md"):
        return ["missing AGENTS.md"]
    lines = project.lines("AGENTS.md")
    return [] if lines <= AGENTS_MAX_LINES else [f"AGENTS.md has {lines} lines (limit {AGENTS_MAX_LINES})"]


@rule("C1-CHAIN", 1, f"The always-loaded instruction files total at most {INSTRUCTION_CHAIN_MAX_BYTES // 1024} KiB")
def instruction_chain(project: Project) -> list[str]:
    total = sum(len(project.read(path).encode("utf-8")) for path in INSTRUCTION_CHAIN)
    return [] if total <= INSTRUCTION_CHAIN_MAX_BYTES else [f"instruction files total {total} bytes (limit {INSTRUCTION_CHAIN_MAX_BYTES})"]


@rule("L1-SECTIONS", 1, "AGENTS.md has the five required sections")
def agents_sections(project: Project) -> list[str]:
    headings = {line[3:].strip().lower() for line in project.read("AGENTS.md").splitlines() if line.startswith("## ")}
    return [f"AGENTS.md lacks the section '## {name}'" for name in REQUIRED_SECTIONS if name.lower() not in headings]


@rule("L1-CLAUDE", 1, "CLAUDE.md imports AGENTS.md and does not duplicate it", uses_claude)
def claude_import(project: Project) -> list[str]:
    text = project.read("CLAUDE.md")
    problems = [] if "@AGENTS.md" in text else ["CLAUDE.md does not import @AGENTS.md"]
    if project.lines("CLAUDE.md") > CLAUDE_IMPORT_MAX_LINES:
        problems.append(f"CLAUDE.md has more than {CLAUDE_IMPORT_MAX_LINES} lines; move shared rules to AGENTS.md")
    return problems


@rule("L1-CHECK", 1, "One check command exists for agents and CI")
def check_script(project: Project) -> list[str]:
    return [] if project.exists("scripts/check.sh") or project.exists("scripts/check.ps1") else ["missing scripts/check.sh or scripts/check.ps1"]


@rule("L1-GITIGNORE", 1, ".gitignore keeps .env files out of Git")
def gitignore(project: Project) -> list[str]:
    return [] if ".env" in project.read(".gitignore") else [".gitignore does not ignore .env"]


@rule("L1-SECRETS", 1, "Secret scanning runs in CI or in the check command")
def secret_scanning(project: Project) -> list[str]:
    sources = workflows(project) + project.read("scripts/check.sh") + project.read("scripts/check.ps1")
    return [] if "gitleaks" in sources else ["no gitleaks step in CI or in the check scripts"]


@rule("L1-DENY", 1, "Agents are denied push, merge and .env reads", uses_claude)
def deny_rules(project: Project) -> list[str]:
    deny = " ".join(claude_settings(project).get("permissions", {}).get("deny", []))
    return [f"no deny rule for '{pattern}' in .claude/settings.json" for pattern in DENY_PATTERNS if pattern not in deny]


@rule("L2-CI", 2, "CI runs the check and the conformance checker on every pull request", has_remote_ci)
def ci(project: Project) -> list[str]:
    text = workflows(project)
    problems = [] if "pull_request" in text else ["no workflow runs on pull_request"]
    if "ads check" not in text:
        problems.append("no workflow runs 'ads check'")
    return problems


@rule("L2-UPDATE", 2, "CI checks on a schedule whether the standard has a newer version", has_remote_ci)
def update_check(project: Project) -> list[str]:
    text = workflows(project)
    return [] if "schedule" in text and "check-update" in text else ["no scheduled 'copier check-update' job"]


@rule("L2-GUARDED", 2, "Guarded paths protect the rules, CI and the gate script")
def guarded_paths(project: Project) -> list[str]:
    text = project.read(".standard/guarded-paths.txt")
    if not text:
        return ["missing .standard/guarded-paths.txt"]
    return [f"{path} is not guarded" for path in ("AGENTS.md", ".github/*", "scripts/check-gates.sh") if path not in text]


@rule("L2-ACCEPTANCE", 2, "acceptance/features.json lists criteria with steps and a passes flag")
def acceptance(project: Project) -> list[str]:
    data = project.read_json("acceptance/features.json")
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        return ["acceptance/features.json is missing or has no 'features' list"]
    return [
        f"feature {feature.get('id', index)} needs id, steps (list) and passes (boolean)"
        for index, feature in enumerate(data["features"])
        if not (feature.get("id") and isinstance(feature.get("steps"), list) and isinstance(feature.get("passes"), bool))
    ]


@rule("C6-STATE", 2, f"State files stay under {STATE_FILE_MAX_TOKENS} tokens so they survive compaction")
def state_files(project: Project) -> list[str]:
    problems = requires(project, "progress.md")
    problems += [
        f"{path} is about {project.tokens(path)} tokens (limit {STATE_FILE_MAX_TOKENS}); archive older entries"
        for path in ("progress.md", "acceptance/features.json")
        if project.tokens(path) > STATE_FILE_MAX_TOKENS
    ]
    return problems


@rule("C6-REFERENCE", 2, f"No Markdown document exceeds {REFERENCE_DOC_MAX_TOKENS} tokens")
def reference_docs(project: Project) -> list[str]:
    return [
        f"{path.relative_to(project.root).as_posix()} is about {project.tokens(str(path.relative_to(project.root)))} tokens; split it into sections"
        for path in project.files("**/*.md")
        if "node_modules" not in path.parts and project.tokens(str(path.relative_to(project.root))) > REFERENCE_DOC_MAX_TOKENS
    ]


@rule("L2-DOCS", 2, "Specs and ADRs have a home")
def specs_and_adrs(project: Project) -> list[str]:
    return requires(project, "docs/specs", "docs/adr")


@rule("L2-SKILLS", 2, "The core lifecycle skills are installed in .agents/skills")
def core_skills(project: Project) -> list[str]:
    return requires(project, *(f".agents/skills/{name}/SKILL.md" for name in CORE_SKILLS))


@rule("C4-SKILLS", 2, "Skills follow the Agent Skills specification and its size budget")
def skill_format(project: Project) -> list[str]:
    problems = []
    for path in project.files(".agents/skills/*/SKILL.md"):
        name = path.parent.name
        text = path.read_text(encoding="utf-8")
        meta = skill_frontmatter(text)
        if meta is None:
            problems.append(f"{name}: missing YAML frontmatter")
            continue
        if meta.get("name") != name:
            problems.append(f"{name}: frontmatter name must equal the folder name")
        if not meta.get("description") or len(str(meta["description"])) > SKILL_DESCRIPTION_MAX_CHARS:
            problems.append(f"{name}: description missing or over {SKILL_DESCRIPTION_MAX_CHARS} characters")
        if extra := set(meta) - SKILL_SPEC_FIELDS:
            problems.append(f"{name}: non-portable frontmatter fields {sorted(extra)}")
        if len(text.splitlines()) > SKILL_MAX_LINES:
            problems.append(f"{name}: over {SKILL_MAX_LINES} lines")
    return problems


@rule("L2-MIRROR", 2, "The Claude Code skills mirror matches .agents/skills", uses_claude)
def skills_mirror(project: Project) -> list[str]:
    problems = []
    for path in project.files(".agents/skills/*/SKILL.md"):
        mirror = project.path(f".claude/skills/{path.parent.name}/SKILL.md")
        if not mirror.is_file() or normalized(mirror) != normalized(path):
            problems.append(f".claude/skills/{path.parent.name}/SKILL.md differs from .agents/skills (run scripts/sync-skills.sh)")
    return problems


@rule("C7-MCP", 2, f"MCP servers are configured per project, at most {MCP_MAX_SERVERS}")
def mcp_servers(project: Project) -> list[str]:
    data = project.read_json(".mcp.json")
    if not isinstance(data, dict):
        return ["missing .mcp.json (an empty {\"mcpServers\": {}} is fine)"]
    count = len(data.get("mcpServers", {}))
    return [] if count <= MCP_MAX_SERVERS else [f".mcp.json lists {count} servers (limit {MCP_MAX_SERVERS})"]


@rule("L2-HOOKS", 2, "A PreToolUse hook blocks agent edits to guarded paths", uses_claude)
def hooks(project: Project) -> list[str]:
    pre_tool_use = json.dumps(claude_settings(project).get("hooks", {}).get("PreToolUse", []))
    return [] if "guard-paths" in pre_tool_use else ["no PreToolUse guard-paths hook in .claude/settings.json"]


@rule("L2-PRODUCT", 2, "Product projects keep a brief, assumptions and a runbook", lambda p: p.profile == "product")
def product_files(project: Project) -> list[str]:
    return requires(project, "docs/product/brief.md", "docs/product/assumptions.md", "docs/ops/runbook.md")


@rule("L2-SERVICE", 2, "Services and libraries keep a changelog", lambda p: p.profile == "service")
def service_files(project: Project) -> list[str]:
    return requires(project, "CHANGELOG.md")


@rule("L1-DEMO", 1, "Demos say in the README that they are not maintained", lambda p: p.profile == "demo")
def demo_status(project: Project) -> list[str]:
    return [] if "demo" in project.read("README.md").lower() else ["README.md does not say this is a demo"]


@rule("L2-MODULES", 2, "Each product module's files are present", lambda p: bool(p.modules))
def module_files(project: Project) -> list[str]:
    return requires(project, *(MODULE_FILES[module] for module in project.modules if module in MODULE_FILES))


@rule("L3-BUDGET", 3, "A token budget is declared")
def budget(project: Project) -> list[str]:
    text = project.read(".standard/budget.yml")
    if not text:
        return ["missing .standard/budget.yml"]
    data = yaml.safe_load(text) or {}
    return [f"budget.yml lacks '{key}'" for key in ("weekly", "session") if key not in data]


@rule("L3-METRICS", 3, "A monthly metrics record exists once the repository is older than 45 days")
def metrics(project: Project) -> list[str]:
    problems = requires(project, "metrics/README.md")
    started = project.first_commit_date()
    if started and date.today() - started > timedelta(days=METRICS_GRACE_DAYS) and not project.files("metrics/[0-9][0-9][0-9][0-9]-[0-9][0-9].md"):
        problems.append("no metrics/YYYY-MM.md record yet")
    return problems


@rule("L3-REVIEW", 3, "The harness is reviewed on a schedule")
def harness_review(project: Project) -> list[str]:
    return requires(project, "docs/harness-review.md")


@rule("L3-EVALS", 3, "AI features have an eval set and a report", lambda p: "ai-extraction" in p.modules)
def evals(project: Project) -> list[str]:
    return requires(project, "evals/schema.md", "evals/README.md")
