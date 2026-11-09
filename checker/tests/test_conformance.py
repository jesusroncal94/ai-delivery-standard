import os
import subprocess

import pytest
import yaml

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


def update_problems(project) -> list[str]:
    return next(o.problems for o in evaluate(Project.load(project)).outcomes if o.rule.id == "L2-UPDATE")


def test_the_update_check_needs_a_copier_that_has_check_update(render):
    project = render("sample-update-pin", profile="service", level=2)
    workflow = project / ".github/workflows/standard.yml"
    assert update_problems(project) == []

    workflow.write_text(workflow.read_text(encoding="utf-8").replace("copier==9.19.1", "copier==9.4.1"), encoding="utf-8")
    assert update_problems(project) == ["CI pins copier 9.4.1, which has no 'check-update' command; pin 9.8.0 or later"]

    workflow.write_text(workflow.read_text(encoding="utf-8").replace("copier==9.4.1", "copier==9.8"), encoding="utf-8")
    assert update_problems(project) == []


@pytest.mark.parametrize(
    ("copier_exit", "job_exit", "warns"),
    [(0, 0, False), (2, 1, True), (1, 1, False)],
    ids=["up-to-date", "update-available", "copier-error"],
)
def test_the_scheduled_job_warns_only_when_copier_reports_an_update(render, tmp_path, copier_exit, job_exit, warns):
    project = render(f"sample-update-exit-{copier_exit}", profile="service", level=2)
    job = yaml.safe_load((project / ".github/workflows/standard.yml").read_text(encoding="utf-8"))["jobs"]["standard-update"]
    script = tmp_path / "step.sh"
    script.write_text(job["steps"][-1]["run"], encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, code in (("pip", 0), ("copier", copier_exit)):
        (bin_dir / name).write_text(f"#!/bin/sh\nexit {code}\n", encoding="utf-8")
        (bin_dir / name).chmod(0o755)

    # GitHub runs `run:` steps with `bash --noprofile --norc -eo pipefail`.
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)],
        capture_output=True, text=True, env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"},
    )

    assert result.returncode == job_exit
    assert ("::warning::" in result.stdout) == warns
