from dataclasses import dataclass, field

from .project import Project
from .rules import RULES, Rule

MAX_LEVEL = 3


@dataclass
class Outcome:
    rule: Rule
    problems: list[str]

    @property
    def passed(self) -> bool:
        return not self.problems


@dataclass
class Result:
    project: Project
    outcomes: list[Outcome] = field(default_factory=list)

    @property
    def achieved(self) -> int:
        achieved = 0
        for level in range(1, MAX_LEVEL + 1):
            if any(not o.passed for o in self.outcomes if o.rule.level == level):
                break
            achieved = level
        return achieved

    @property
    def conforms(self) -> bool:
        return self.achieved >= self.project.level

    def failures(self, up_to: int | None = None) -> list[Outcome]:
        limit = up_to or self.project.level
        return [o for o in self.outcomes if not o.passed and o.rule.level <= limit]

    def as_dict(self) -> dict:
        return {
            "project": self.project.root.name,
            "profile": self.project.profile,
            "target": self.project.level,
            "achieved": self.achieved,
            "conforms": self.conforms,
            "rules": [
                {"id": o.rule.id, "level": o.rule.level, "title": o.rule.title, "passed": o.passed, "problems": o.problems}
                for o in self.outcomes
            ],
        }


def evaluate(project: Project) -> Result:
    applicable = [r for r in RULES if r.level <= MAX_LEVEL and r.applies(project)]
    return Result(project, [Outcome(r, r.check(project)) for r in applicable])
