import os
import subprocess
from datetime import date
from pathlib import Path

import pytest

from conftest import TEMPLATE, git

SCRIPT = Path(TEMPLATE) / "scripts" / "check-release.sh"
TODAY = date.today().isoformat()


def repository(path: Path, heading: str, version: str = "1.2.3") -> Path:
    (path / "checker" / "ads").mkdir(parents=True)
    (path / "CHANGELOG.md").write_text(f"# Changelog\n\n{heading}\n\n- A change.\n\n## 1.2.2 — 2026-01-01\n", encoding="utf-8")
    (path / "checker" / "ads" / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    (path / "checker" / "pyproject.toml").write_text(f'[project]\nname = "ads"\nversion = "{version}"\n', encoding="utf-8")
    return path


def check_release(path: Path, tag: str = "v1.2.3") -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), tag, str(path)], capture_output=True, text=True)


def test_a_commit_whose_latest_entry_is_the_version_dated_today_is_ready(tmp_path):
    result = check_release(repository(tmp_path, f"## 1.2.3 — {TODAY}"))

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("heading", ["## 1.2.3 — unreleased", "## 1.2.3 — 2026-01-01", f"## 1.2.4 — {TODAY}"])
def test_a_commit_whose_latest_entry_is_undated_misdated_or_another_version_is_not_ready(tmp_path, heading):
    result = check_release(repository(tmp_path, heading))

    assert result.returncode == 1
    assert f"not '## 1.2.3 — {TODAY}'" in result.stderr


def test_a_checker_that_reports_another_version_is_not_ready(tmp_path):
    result = check_release(repository(tmp_path, f"## 1.2.3 — {TODAY}", version="1.2.2"))

    assert result.returncode == 1
    assert "__version__" in result.stderr and "pyproject.toml" in result.stderr


def test_a_pushed_tag_is_checked_against_its_own_date(tmp_path):
    project = repository(tmp_path, "## 1.2.3 — 2026-01-03")
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "docs(changelog): date the 1.2.3 release")
    subprocess.run(
        ["git", "-C", str(project), "tag", "-a", "v1.2.3", "-m", "1.2.3"],
        check=True, env={**os.environ, "GIT_COMMITTER_DATE": "2026-01-03T00:30:00+01:00"},
    )

    assert check_release(project).returncode == 0
    assert check_release(project, "v1.2.4").returncode == 1


def test_a_name_that_is_not_a_release_tag_is_refused(tmp_path):
    result = check_release(repository(tmp_path, f"## 1.2.3 — {TODAY}"), "1.2.3")

    assert result.returncode == 1
    assert "not a release tag" in result.stderr
