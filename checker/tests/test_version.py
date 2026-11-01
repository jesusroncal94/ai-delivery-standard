import re
import tomllib
from pathlib import Path

from ads import __version__

from conftest import TEMPLATE


def test_checker_version_matches_the_latest_changelog_entry():
    latest = re.search(r"^## (\d+\.\d+\.\d+)", (Path(TEMPLATE) / "CHANGELOG.md").read_text(encoding="utf-8"), re.M).group(1)
    package = tomllib.loads((Path(TEMPLATE) / "checker" / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]

    assert __version__ == package == latest
