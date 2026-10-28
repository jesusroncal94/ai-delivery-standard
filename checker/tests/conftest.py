import os
import subprocess
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE = os.environ.get("ADS_TEMPLATE", str(Path(__file__).resolve().parents[2]))
FIXTURES = Path(__file__).parent / "fixtures"


def git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)


@pytest.fixture
def render(tmp_path):
    def _render(name: str, **answers) -> Path:
        destination = tmp_path / name
        data = {"project_name": name, "check_command": "true", **answers}
        run_copy(TEMPLATE, destination, data=data, defaults=True, unsafe=True, quiet=True)
        git(destination, "init", "-q", "-b", "main")
        if not answers.get("local_only"):
            git(destination, "remote", "add", "origin", f"https://example.invalid/{name}.git")
        git(destination, "add", "-A")
        git(destination, "commit", "-q", "-m", "chore: adopt the standard")
        return destination
    return _render
