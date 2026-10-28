from copier import run_update

from ads.conformance import evaluate
from ads.project import Project

from conftest import git


def test_raising_the_level_through_copier_update_adds_the_gated_files(render):
    project = render("raise-me", profile="service", level=1)
    assert Project.load(project).level == 1

    run_update(project, data={"level": 2}, defaults=True, overwrite=True, unsafe=True, quiet=True)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "chore: raise the standard level to L2")

    result = evaluate(Project.load(project))
    assert result.project.level == 2
    assert result.conforms, [(o.rule.id, o.problems) for o in result.failures()]
