import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Tuple

import pandas
import polars
import pytest
from dotenv import load_dotenv

from git_author_stats._github import iter_organization_repository_clone_urls
from git_author_stats._stats import (
    Frequency,
    FrequencyUnit,
    Stats,
    check_output,
    iter_stats,
)

load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def test_iter_organization_stats() -> None:
    """
    Test obtaining stats for a Github organization
    """
    password: str = (
        os.environ.get("GH_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    assert password
    found: bool = False
    stats: Stats
    for stats in iter_stats(
        urls="https://github.com/enorganic",
        frequency=Frequency(2, FrequencyUnit.WEEK),
        since=date.today() - timedelta(days=365),
        password=password,
    ):
        found = True
        break
    assert found, 'No stats found for the "enorganic" organization.'


def test_iter_organization_repository_clone_urls() -> None:
    # Unauthenticated
    unauthenticated_urls: Tuple[str, ...] = tuple(
        iter_organization_repository_clone_urls("github.com/enorganic")
    )
    assert "https://github.com/enorganic/git-author-stats.git" in (
        unauthenticated_urls
    ), unauthenticated_urls
    # Authenticated
    password: str = (
        os.environ.get("GH_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    authenticated_urls: Tuple[str, ...] = tuple(
        iter_organization_repository_clone_urls(
            "github.com/enorganic",
            password=password,
        )
    )
    assert "https://github.com/enorganic/discussions.git" in (
        authenticated_urls
    ), authenticated_urls


def test_iter_repo_stats() -> None:
    """
    Test creating a pandas data frame from the stats of a single repository.
    """
    password: str = (
        os.environ.get("GH_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    assert password
    stats: Tuple[Stats, ...] = tuple(
        iter_stats(
            urls="https://github.com/enorganic/git-author-stats.git",
            frequency=Frequency(2, FrequencyUnit.WEEK),
            since=date.today() - timedelta(days=365),
            password=password,
        )
    )
    assert stats
    pandas_data_frame: pandas.DataFrame = pandas.DataFrame(stats)
    assert pandas_data_frame.columns.tolist() == [
        "url",
        "author",
        "since",
        "before",
        "insertions",
        "deletions",
        "file",
    ], stats
    polars_data_frame: polars.DataFrame = polars.DataFrame(stats)
    assert polars_data_frame.columns == [
        "url",
        "author",
        "since",
        "before",
        "insertions",
        "deletions",
        "file",
    ], stats


def test_cli_repo() -> None:
    password: str = (
        os.environ.get("GH_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    assert password
    # Markdown
    lines: List[str] = (
        check_output(
            (
                sys.executable,
                "-m",
                "git_author_stats",
                "https://github.com/enorganic/git-author-stats.git",
                "-f",
                "1w",
                "--since",
                (date.today() - timedelta(days=365)).isoformat(),
                "-p",
                password,
                "-md",
            ),
        )
        .strip()
        .split("\n")
    )
    assert len(lines) > 2
    # CSV
    lines = (
        check_output(
            (
                sys.executable,
                "-m",
                "git_author_stats",
                "https://github.com/enorganic/git-author-stats.git",
                "-f",
                "1w",
                "--since",
                (date.today() - timedelta(days=365)).isoformat(),
                "-p",
                password,
            ),
        )
        .strip()
        .split("\n")
    )
    assert len(lines) > 1


def test_cli_org() -> None:
    password: str = (
        os.environ.get("GH_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    assert password
    lines: List[str] = (
        check_output(
            (
                sys.executable,
                "-m",
                "git_author_stats",
                "https://github.com/enorganic",
                "-f",
                "1w",
                "--since",
                (date.today() - timedelta(days=365)).isoformat(),
                "-p",
                password,
            ),
            echo=True,
        )
        .strip()
        .split("\n")
    )
    assert len(lines) > 2


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
