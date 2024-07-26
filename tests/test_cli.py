import sys
from datetime import date, timedelta
from subprocess import check_output
from typing import List

import pytest


def test_cli() -> None:
    lines: List[str] = check_output(
        [
            sys.executable,
            "-m",
            "git_author_stats",
            "https://github.com/enorganic/git-author-stats.git",
            "-f",
            "1w",
            "--since",
            (date.today() - timedelta(days=365)).isoformat(),
        ],
        text=True,
    ).splitlines()
    assert len(lines) > 1


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
