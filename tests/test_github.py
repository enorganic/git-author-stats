import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from git_author_stats._github import iter_organization_repository_clone_urls

load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def test_iter_organization_repository_clone_urls() -> None:
    # Unauthenticated
    assert "https://github.com/enorganic/dependence.git" in (
        iter_organization_repository_clone_urls("github.com/enorganic")
    )
    # Authenticated
    assert "https://github.com/enorganic/dependence.git" in (
        iter_organization_repository_clone_urls(
            "github.com/enorganic",
            password=os.environ.get(
                "GH_TOKEN", os.environ.get("GITHUB_TOKEN", "")
            ),
        )
    )


if __name__ == "__main__":
    pytest.main(["-s", "-vv", __file__])
