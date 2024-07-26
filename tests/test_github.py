import os
from pathlib import Path
from typing import Tuple

import pytest
from dotenv import load_dotenv

from git_author_stats._github import iter_organization_repository_clone_urls

load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def test_iter_organization_repository_clone_urls() -> None:
    # Unauthenticated
    unauthenticated_urls: Tuple[str, ...] = tuple(
        iter_organization_repository_clone_urls("github.com/enorganic")
    )
    assert "https://github.com/enorganic/dependence.git" in (
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


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
