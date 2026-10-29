import os
import shutil
import subprocess
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE = os.environ.get("ADS_TEMPLATE", str(Path(__file__).resolve().parents[2]))
FIXTURES = Path(__file__).parent / "fixtures"


def git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)


@pytest.fixture(scope="session")
def template(tmp_path_factory) -> Path:
    """A committed snapshot of the working tree: renders include uncommitted changes, not the latest tag,
    and `copier update` can find the commit a project was rendered from."""
    source, snapshot = Path(TEMPLATE), tmp_path_factory.mktemp("template")
    listed = subprocess.run(
        ["git", "-C", str(source), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=True, capture_output=True, text=True,
    ).stdout
    for name in filter(None, listed.split("\0")):
        if (source / name).is_file():
            (snapshot / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, snapshot / name)
    git(snapshot, "init", "-q", "-b", "main")
    git(snapshot, "add", "-A")
    git(snapshot, "commit", "-q", "-m", "test: snapshot the working tree")
    return snapshot


@pytest.fixture
def render(tmp_path, template):
    def _render(name: str, **answers) -> Path:
        destination = tmp_path / name
        data = {"project_name": name, "check_command": "true", **answers}
        run_copy(str(template), destination, data=data, vcs_ref="HEAD", defaults=True, unsafe=True, quiet=True)
        git(destination, "init", "-q", "-b", "main")
        if not answers.get("local_only"):
            git(destination, "remote", "add", "origin", f"https://example.invalid/{name}.git")
        git(destination, "add", "-A")
        git(destination, "commit", "-q", "-m", "chore: adopt the standard")
        return destination
    return _render
