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


FAKE_DOCKER = """#!/usr/bin/env bash
# Stands in for docker in ads.sh: build does nothing; run executes the entrypoint in the folder mounted at /work.
[ "$1" = build ] && exit 0
shift
work= entrypoint=
while [ $# -gt 0 ]; do
  case $1 in
    --rm|-i) shift ;;
    -v) case $2 in *:/work) work=${2%:/work} ;; esac; shift 2 ;;
    -w|-e) shift 2 ;;
    --entrypoint) entrypoint=$2; shift 2 ;;
    *) break ;;
  esac
done
shift
cd "$work" && exec "$entrypoint" "$@"
"""
SCRIPTS = ["scripts/check.sh", "scripts/check-gates.sh", "scripts/sync-skills.sh", ".claude/hooks/guard-paths.sh", ".claude/hooks/session-start.sh"]


def index_modes(repo: Path) -> dict[str, str]:
    listed = subprocess.run(["git", "-C", str(repo), "ls-files", "-s"], check=True, capture_output=True, text=True).stdout
    return {line.split("\t", 1)[1]: line.split()[0] for line in listed.splitlines()}


@pytest.mark.parametrize("file_mode", ["false", "true"])
def test_ads_update_reuses_the_answers_and_keeps_the_committed_file_modes(template, tmp_path, file_mode):
    """A project that committed its scripts as executable, from a template that tracks them as plain files (as v1.1.7 does).
    copier update would ask the questions again without a terminal, and would copy the template's mode into the index
    (core.fileMode false, the Windows default) or onto disk (true)."""
    old = tmp_path / "old-template"
    shutil.copytree(template, old)
    subprocess.run("git ls-files -z | xargs -0 git update-index --chmod=-x", shell=True, cwd=old, check=True)
    git(old, "commit", "-q", "-m", "test: track every file as non-executable")
    git(old, "tag", "v0.0.1")
    changelog = old / "CHANGELOG.md"
    changelog.write_text(changelog.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    git(old, "commit", "-q", "-am", "test: a new version")
    git(old, "tag", "v0.0.2")

    project = tmp_path / "project"
    data = {"project_name": "project", "profile": "service", "level": 2, "check_command": "true"}
    run_copy(str(old), project, data=data, vcs_ref="v0.0.1", defaults=True, unsafe=True, quiet=True)
    git(project, "init", "-q", "-b", "main")
    git(project, "config", "core.fileMode", file_mode)
    git(project, "add", "-A")
    for script in SCRIPTS:
        (project / script).chmod(0o755)
        git(project, "update-index", "--chmod=+x", script)
    git(project, "commit", "-q", "-m", "chore: adopt the standard")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "docker").write_text(FAKE_DOCKER, encoding="utf-8")
    (bin_dir / "docker").chmod(0o755)
    result = subprocess.run(
        ["bash", str(template / "scripts/ads.sh"), "update", str(project), "--vcs-ref", "v0.0.2"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"},
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load((project / ".copier-answers.yml").read_text(encoding="utf-8"))["_commit"] == "v0.0.2"
    assert all(index_modes(project)[script] == "100755" for script in SCRIPTS), index_modes(project)
    # Staged or on disk, the only changes are the new version: its answers and the checker the CI installs.
    changes = subprocess.run(["git", "-C", str(project), "diff", "HEAD", "--raw", "--no-renames"], check=True, capture_output=True, text=True).stdout
    assert {line.split("\t", 1)[1] for line in changes.splitlines()} == {".copier-answers.yml", ".github/workflows/standard.yml"}
    assert [line for line in changes.splitlines() if line.split()[0][1:] != line.split()[1]] == []
