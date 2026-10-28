import pytest

from ads.conformance import evaluate
from ads.project import Project


@pytest.mark.parametrize(
    "answers",
    [
        {"profile": "product", "level": 3, "modules": ["multi-user", "eu-personal-data", "ai-extraction"], "adapters": ["claude-code", "copilot"]},
        {"profile": "service", "level": 2},
        {"profile": "research", "level": 2},
        {"profile": "site", "level": 2},
        {"profile": "demo", "level": 1, "local_only": True},
    ],
    ids=lambda answers: f"{answers['profile']}-L{answers['level']}",
)
def test_rendered_projects_meet_their_level(render, answers):
    result = evaluate(Project.load(render(f"sample-{answers['profile']}", **answers)))

    assert result.conforms, [(o.rule.id, o.problems) for o in result.failures()]
    assert result.achieved >= answers["level"]


def test_an_unadopted_repository_does_not_conform(tmp_path):
    (tmp_path / "README.md").write_text("# legacy\n", encoding="utf-8")

    result = evaluate(Project.load(tmp_path, "service", 1))

    assert not result.conforms
    assert {"L1-GIT", "C1-AGENTS", "L1-ANSWERS"} <= {o.rule.id for o in result.failures()}
