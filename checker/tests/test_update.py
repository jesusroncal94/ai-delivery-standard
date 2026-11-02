import os
import shutil
import signal
import subprocess
from pathlib import Path

import pytest
import yaml
from copier import run_copy, run_update

from ads.conformance import evaluate
from ads.project import Project

from conftest import git

SELF_CALLS = ["bash scripts/check.sh", "scripts/check.sh", "./scripts/check.sh", "pwsh -File scripts/check.ps1", r".\scripts\check.ps1"]
HAND_WRITTEN_CHECK = "docker compose run --rm tests\n"


def run_check(project: Path) -> subprocess.CompletedProcess:
    """Runs scripts/check.sh in its own process group, so a script that calls itself is killed whole instead of hanging the suite."""
    process = subprocess.Popen(["bash", "scripts/check.sh"], cwd=project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        pytest.fail("scripts/check.sh did not finish: it calls itself")
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)


def test_raising_the_level_through_copier_update_adds_the_gated_files(render):
    project = render("raise-me", profile="service", level=1)
    assert Project.load(project).level == 1

    run_update(project, data={"level": 2}, vcs_ref="HEAD", defaults=True, overwrite=True, unsafe=True, quiet=True)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "chore: raise the standard level to L2")

    result = evaluate(Project.load(project))
    assert result.project.level == 2
    assert result.conforms, [(o.rule.id, o.problems) for o in result.failures()]


@pytest.mark.parametrize("check_command", SELF_CALLS)
def test_a_check_command_that_runs_the_check_script_renders_a_placeholder_instead_of_a_loop(render, check_command):
    project = render("self-check", profile="service", level=1, check_command=check_command)

    result = run_check(project)

    assert result.returncode == 1
    assert "write the real check here" in result.stderr
    assert check_command in (project / "AGENTS.md").read_text(encoding="utf-8")


def test_other_check_commands_are_rendered_verbatim(render):
    project = render("plain-check", profile="service", level=1, check_command="bash scripts/check-gates.sh 2>/dev/null || echo checked")

    result = run_check(project)

    assert result.returncode == 0
    assert result.stdout.strip() == "checked"


def test_copier_update_keeps_an_answer_that_runs_the_check_script_and_marks_the_hand_written_check_as_a_conflict(template, tmp_path):
    """A project adopted before the fix answered `bash scripts/check.sh` and wrote the real check into the script by hand.
    The update keeps the answer and leaves one conflict in scripts/check.sh whose 'before updating' side is that check."""
    old = tmp_path / "old-template"
    shutil.copytree(template, old)
    (old / "template/scripts/check.sh.jinja").write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")/.."\n\n{{ check_command }}\n', encoding="utf-8"
    )
    git(old, "commit", "-q", "-am", "test: render the check command verbatim")
    git(old, "tag", "v0.0.1")
    shutil.copy2(template / "template/scripts/check.sh.jinja", old / "template/scripts/check.sh.jinja")
    git(old, "commit", "-q", "-am", "fix: do not let scripts/check.sh call itself")
    git(old, "tag", "v0.0.2")

    project = tmp_path / "adopted"
    data = {"project_name": "adopted", "profile": "service", "level": 1, "check_command": "bash scripts/check.sh"}
    run_copy(str(old), project, data=data, vcs_ref="v0.0.1", defaults=True, unsafe=True, quiet=True)
    check = project / "scripts/check.sh"
    check.write_text(check.read_text(encoding="utf-8").replace("bash scripts/check.sh\n", HAND_WRITTEN_CHECK), encoding="utf-8")
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "chore: adopt the standard")

    run_update(project, vcs_ref="v0.0.2", defaults=True, overwrite=True, unsafe=True, quiet=True)

    answers = yaml.safe_load((project / ".copier-answers.yml").read_text(encoding="utf-8"))
    assert answers["_commit"] == "v0.0.2"
    assert answers["check_command"] == "bash scripts/check.sh"
    assert "bash scripts/check.sh" in (project / "AGENTS.md").read_text(encoding="utf-8")
    before_updating = check.read_text(encoding="utf-8").split("<<<<<<< before updating\n")[1].split("=======\n")[0]
    assert before_updating == HAND_WRITTEN_CHECK
