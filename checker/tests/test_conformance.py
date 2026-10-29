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


MANIFEST_ROW = "| 01 Overview | overview | [overview.svg](../diagrams/overview.svg) | [README](../../README.md) | 2026-10-29 |\n"


def publish_diagram(project, svg: str) -> None:
    (project / "docs/diagrams/overview.svg").write_text(svg, encoding="utf-8")
    manifest = project / "docs/design/README.md"
    manifest.write_text(manifest.read_text(encoding="utf-8").replace("|---|---|---|---|---|\n", "|---|---|---|---|---|\n" + MANIFEST_ROW), encoding="utf-8")


@pytest.mark.parametrize("level", [1, 2])
def test_a_project_with_diagrams_conforms_and_keeps_its_manifest_honest(render, level):
    project = render(f"sample-diagrams-l{level}", profile="site", level=level, diagrams=True)
    assert (project / "docs/design/tokens.json").is_file() and (project / "docs/design/postprocess-svg.sh").is_file()
    assert (project / ".agents/skills/update-diagram/SKILL.md").is_file() == (level >= 2)
    assert "`docs/diagrams/`" in (project / "AGENTS.md").read_text(encoding="utf-8")

    publish_diagram(project, '<svg xmlns="http://www.w3.org/2000/svg"><text style="font-family: Inter, sans-serif;">ok</text></svg>')
    result = evaluate(Project.load(project))
    assert result.conforms, [(o.rule.id, o.problems) for o in result.failures()]
    assert "L1-DIAGRAMS" in {o.rule.id for o in result.outcomes}

    (project / "docs/diagrams/stray.svg").write_text("<svg/>", encoding="utf-8")
    (project / "docs/diagrams/overview.svg").unlink()
    problems = next(o.problems for o in evaluate(Project.load(project)).outcomes if o.rule.id == "L1-DIAGRAMS")
    assert any("overview.svg, which does not exist" in p for p in problems)
    assert any("stray.svg is not in the manifest" in p for p in problems)


def test_an_svg_that_loads_a_web_font_fails_the_diagrams_rule(render):
    project = render("sample-diagrams-font", profile="research", level=2, diagrams=True)
    publish_diagram(project, "<svg><style>@font-face { font-family: Inter; src: url(https://example.invalid/inter.woff2); }</style></svg>")

    result = evaluate(Project.load(project))

    assert not result.conforms
    assert [o.rule.id for o in result.failures()] == ["L1-DIAGRAMS"]


def test_projects_without_diagrams_skip_the_rule(render):
    project = render("sample-no-diagrams", profile="service", level=2)

    assert not (project / "docs/design").exists()
    assert "L1-DIAGRAMS" not in {o.rule.id for o in evaluate(Project.load(project)).outcomes}
