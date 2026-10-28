import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml

ANSWERS_FILE = ".copier-answers.yml"
CHARS_PER_TOKEN = 4


@dataclass
class Project:
    root: Path
    profile: str
    level: int
    adapters: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    local_only: bool = False
    has_answers: bool = False

    @classmethod
    def load(cls, root: Path, profile: str | None = None, level: int | None = None) -> "Project":
        answers = _read_answers(root / ANSWERS_FILE)
        return cls(
            root=root,
            profile=profile or answers.get("profile", "service"),
            level=int(level or answers.get("level", 1)),
            adapters=list(answers.get("adapters") or []),
            modules=list(answers.get("modules") or []),
            local_only=bool(answers.get("local_only", False)),
            has_answers=bool(answers),
        )

    @property
    def uses_claude(self) -> bool:
        return "claude-code" in self.adapters or self.exists("CLAUDE.md")

    def path(self, relative: str) -> Path:
        return self.root / relative

    def exists(self, relative: str) -> bool:
        return self.path(relative).exists()

    def read(self, relative: str) -> str:
        target = self.path(relative)
        return target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""

    def read_json(self, relative: str):
        try:
            return json.loads(self.read(relative))
        except json.JSONDecodeError:
            return None

    def lines(self, relative: str) -> int:
        return len(self.read(relative).splitlines())

    def tokens(self, relative: str) -> int:
        return estimate_tokens(self.read(relative))

    def files(self, pattern: str) -> list[Path]:
        return sorted(p for p in self.root.glob(pattern) if p.is_file() and ".git" not in p.parts)

    def is_git_repo(self) -> bool:
        return self.exists(".git")

    def remotes(self) -> list[str]:
        return os.environ.get("ADS_GIT_REMOTES", self._git("remote")).split()

    def first_commit_date(self) -> date | None:
        output = os.environ.get("ADS_GIT_FIRST_COMMIT") or self._git("log", "--reverse", "--format=%cs", "--max-parents=0")
        first = output.split()[:1]
        return datetime.strptime(first[0], "%Y-%m-%d").date() if first else None

    def _git(self, *args: str) -> str:
        if not self.is_git_repo():
            return ""
        result = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else ""


def estimate_tokens(text: str) -> int:
    return -(-len(text) // CHARS_PER_TOKEN)


def _read_answers(path: Path) -> dict:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
